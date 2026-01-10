from typing import Tuple, List

import music21
from music21 import converter
from music21 import *
from collections import Counter

from music21.note import NotRest


def get_pitch_classes(element) -> list[int]:
    """Extract pitch classes (0-11) from a Note or Chord, handling enharmonic equivalence."""
    if hasattr(element, "pitches"):  # Chord
        return [p.pitchClass for p in element.pitches]
    elif hasattr(element, "pitch"):  # Note
        return [element.pitch.pitchClass]
    return []


def snip_to_pitch_counter(snip) -> Counter:
    """Convert a snip (list of Notes/Chords) to a Counter of pitch classes."""
    pitch_classes = []
    for element in snip:
        pitch_classes.extend(get_pitch_classes(element))
    return Counter(pitch_classes)


def checked_second_in_first(a: Counter, b: Counter) -> bool:
    """Check if b is a subset of a (all pitches in b exist in a with <= count)."""
    for key in b:
        if key not in a:
            return False
        if b[key] > a[key]:
            return False
    return True


def similarity_score(a: Counter, b: Counter) -> float:
    """Calculate Jaccard-like similarity between two pitch counters."""
    if not a and not b:
        return 1.0
    intersection = sum((a & b).values())
    union = sum((a | b).values())
    return intersection / union if union > 0 else 0.0


def checked_equal(midi_snip, mxl_snip) -> bool:
    """Check if two snips have the same pitches (ignoring octave and note/chord distinction)."""
    return snip_to_pitch_counter(midi_snip) == snip_to_pitch_counter(mxl_snip)


def checked_similar(midi_snip, mxl_snip, threshold=0.6) -> bool:
    """Check if two snips are similar enough (for fuzzy matching)."""
    return (
        similarity_score(
            snip_to_pitch_counter(midi_snip), snip_to_pitch_counter(mxl_snip)
        )
        >= threshold
    )


# Counter counts how many of each pitch there is in the snip


class Stamper:
    def check_MM(self) -> bool | ValueError:  # check metronome marks
        if (
            len(
                self.midi.recurse()
                .getElementsByClass(tempo.MetronomeMark)
                .getElementsByOffset(0)
            )
            == 0
        ):
            raise ValueError("invalid midi: no MetronomeMark at the beginning")
        else:
            return True

    def __init__(self, midi_path: str, mxl_path: str):
        self.midi = converter.parse(midi_path)
        self.check_MM()
        self.midi_secondsMap = sorted(
            self.midi.flatten().getElementsByClass(note.NotRest).stream().secondsMap,
            key=lambda x: x["offsetSeconds"],
        )
        self.mxl = (
            converter.parse(mxl_path)
            .flatten()
            .getElementsByClass(note.NotRest)
            .stream()
        )
        self.midi_snip = [self.midi_secondsMap[0]["element"]]
        self.mxl_snip = [self.mxl[0]]

    def expand(
        self,
        midi_snip: list[note.NotRest],
        mxl_snip: list[note.NotRest],
        last_index: int,
        expansions: int = 0,
    ) -> tuple[list[NotRest], list[NotRest], int]:
        # range expansion to deal with wrong order of (almost) concurrent notes.
        # Check bounds before expanding
        if last_index + 1 >= len(self.midi_secondsMap):
            return midi_snip, mxl_snip, last_index  # Can't expand further
        next_mxl = mxl_snip[-1].next()
        if next_mxl is None:
            return midi_snip, mxl_snip, last_index  # Can't expand further
        midi_snip.append(
            self.midi_secondsMap[last_index + 1]["element"]
        )  # is this not .next() because the sorting spoiled the stream functionality.
        mxl_snip.append(next_mxl)
        print("expanded")
        return midi_snip, mxl_snip, last_index + 1

    def match(
        self, midi_snip, mxl_snip, annotated_dict, last_index
    ) -> tuple[list[note.NotRest], list[note.NotRest], dict, int]:
        def check(
            midi_snip, mxl_snip, last_index, expansions=0
        ) -> tuple[list[note.NotRest], list[note.NotRest], dict, int]:
            if expansions >= 10:  # arbitrary value of error tolerance.
                # Skip ahead and try to re-sync
                print(f"skipping at last_index={last_index} (could not match)")
                if last_index + 1 >= len(self.midi_secondsMap):
                    raise StopIteration("Reached end of MIDI")
                next_mxl = mxl_snip[-1].next()
                if next_mxl is None:
                    raise StopIteration("Reached end of MXL")
                return (
                    [self.midi_secondsMap[last_index + 1]["element"]],
                    [next_mxl],
                    annotated_dict,
                    last_index + 1,
                )

            elif checked_equal(midi_snip, mxl_snip):
                annotated_dict[
                    mxl_snip[
                        -1
                    ].measureNumber  # measure number from MXL (score structure)
                ] = self.midi_secondsMap[last_index][
                    "endTimeSeconds"
                ]  # timing from MIDI (audio)
                print("matched order")
                # print([self.midi_secondsMap[last_index + 1]['element']], [mxl_snip[-1].next()], annotated_dict, last_index + 1)

                return (
                    [self.midi_secondsMap[last_index + 1]["element"]],
                    [mxl_snip[-1].next()],
                    annotated_dict,
                    last_index + 1,
                )

            elif checked_second_in_first(
                snip_to_pitch_counter(midi_snip), snip_to_pitch_counter(mxl_snip)
            ):  # MIDI has all MXL pitches (MIDI may have extra from harmonics)
                annotated_dict[
                    mxl_snip[
                        -1
                    ].measureNumber  # measure number from MXL (score structure)
                ] = self.midi_secondsMap[last_index][
                    "endTimeSeconds"
                ]  # timing from MIDI (audio)
                print("matched subset (midi >= mxl)")
                return (
                    [self.midi_secondsMap[last_index + 1]["element"]],
                    [mxl_snip[-1].next()],
                    annotated_dict,
                    last_index + 1,
                )  # advance both since we matched

            elif checked_second_in_first(
                snip_to_pitch_counter(mxl_snip), snip_to_pitch_counter(midi_snip)
            ):  # MXL has all MIDI pitches (MIDI missing some notes)
                annotated_dict[
                    mxl_snip[
                        -1
                    ].measureNumber  # measure number from MXL (score structure)
                ] = self.midi_secondsMap[last_index][
                    "endTimeSeconds"
                ]  # timing from MIDI (audio)
                print("matched subset (mxl >= midi)")
                return (
                    [self.midi_secondsMap[last_index + 1]["element"]],
                    [mxl_snip[-1]],
                    annotated_dict,
                    last_index + 1,
                )  # step the midi but not the mxl (mxl has more notes to match)

            elif checked_similar(midi_snip, mxl_snip, threshold=0.35):
                # Fuzzy match - accept if at least 50% similar
                annotated_dict[mxl_snip[-1].measureNumber] = self.midi_secondsMap[
                    last_index
                ]["endTimeSeconds"]
                score = similarity_score(
                    snip_to_pitch_counter(midi_snip), snip_to_pitch_counter(mxl_snip)
                )
                print(f"matched fuzzy (similarity={score:.2f})")
                return (
                    [self.midi_secondsMap[last_index + 1]["element"]],
                    [mxl_snip[-1].next()],
                    annotated_dict,
                    last_index + 1,
                )

            else:
                midi_snip, mxl_snip, last_index = self.expand(
                    midi_snip, mxl_snip, last_index
                )
                return check(midi_snip, mxl_snip, last_index, expansions + 1)

        return check(midi_snip, mxl_snip, last_index)

    def stamp(
        self, midi_snip=None, mxl_snip=None, annotated_dict=None, last_index=0
    ):  # main driver function
        if annotated_dict is None:
            annotated_dict = {}
        if midi_snip is None:
            midi_snip = self.midi_snip
        if mxl_snip is None:
            mxl_snip = self.mxl_snip
        try:
            while (
                last_index < len(self.mxl) - 3
                and last_index < len(self.midi_secondsMap) - 1
            ):
                midi_snip, mxl_snip, annotated_dict, last_index = self.match(
                    midi_snip, mxl_snip, annotated_dict, last_index
                )
        except StopIteration as e:
            print(f"Stopped: {e}")
        return annotated_dict


if __name__ == "__main__":
    stamp_Polonaise = Stamper(
        "basic_pitch_transcription.mid",
        "Polonaise.mxl",
    )
    try:
        timestamps = stamp_Polonaise.stamp()
        print("\n=== SUCCESS ===")
        print(f"Matched {len(timestamps)} measures:")
        for measure, time in sorted(timestamps.items()):
            print(f"  Measure {measure}: {time:.2f}s")
    except ValueError as e:
        print("\n=== FAILED TO MATCH ===")
        print(
            f"Matched {len(stamp_Polonaise.stamp.__code__.co_freevars)} measures before failure"
        )
