from typing import Tuple, List

import music21
from matplotlib.testing.compare import converter
from music21 import *
from collections import Counter

from music21.note import NotRest


def checked_second_in_first(a, b) -> bool:
    # checking if a subset of b
    for key in b:
        if key not in a:
            return False
        if b[key] > a[key]:
            return False
    return True


def checked_equal(midi_snip, mxl_snip) -> bool:
    return Counter(map(str, midi_snip)) == Counter(map(str, mxl_snip))


# Counter counts how many of each note there is in the snip


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
        midi_snip.append(
            self.midi_secondsMap[last_index + 1]["element"]
        )  # is this not .next() because the sorting spoiled the stream functionality.
        mxl_snip.append(mxl_snip[-1].next())
        print("expanded")
        return midi_snip, mxl_snip, last_index + 1

    def match(
        self, midi_snip, mxl_snip, annotated_dict, last_index
    ) -> tuple[list[note.NotRest], list[note.NotRest], dict, int]:
        def check(
            midi_snip, mxl_snip, expansions=0
        ) -> tuple[list[note.NotRest], list[note.NotRest], dict, int]:
            if expansions >= 6:  # arbitrary value of error tolerance.
                raise ValueError

            elif checked_equal(midi_snip, mxl_snip):
                annotated_dict[
                    self.midi_secondsMap[last_index]["element"].measureNumber
                ] = self.midi_secondsMap[last_index]["endTimeSeconds"]
                print("matched order")
                # print([self.midi_secondsMap[last_index + 1]['element']], [mxl_snip[-1].next()], annotated_dict, last_index + 1)

                return (
                    [self.midi_secondsMap[last_index + 1]["element"]],
                    [mxl_snip[-1].next()],
                    annotated_dict,
                    last_index + 1,
                )

            elif checked_second_in_first(
                midi_snip, mxl_snip
            ):  # assuming only the case of midi missing one note
                annotated_dict[
                    self.midi_secondsMap[last_index]["element"].measureNumber
                ] = self.midi_secondsMap[last_index]["endTimeSeconds"]
                print("matched subset")
                return (
                    [self.midi_secondsMap[last_index + 1]["element"]],
                    [mxl_snip[-1]],
                    annotated_dict,
                    last_index + 1,
                )  # step the midi but not the mxl

            else:
                check(self.expand(midi_snip, mxl_snip, last_index), expansions + 1)

        return check(midi_snip, mxl_snip)

    def stamp(
        self, midi_snip=None, mxl_snip=None, annotated_dict=None, last_index=0
    ):  # main driver function
        if annotated_dict is None:
            annotated_dict = {}
        if midi_snip is None:
            midi_snip = self.midi_snip
        if mxl_snip is None:
            mxl_snip = self.mxl_snip
        while (
            last_index < len(self.mxl) - 3
        ):  # mxl_snip[0].offset <= mxl.last().previous().offset:
            midi_snip, mxl_snip, annotated_dict, last_index = self.match(
                midi_snip, mxl_snip, annotated_dict, last_index
            )
            # print(midi_snip, mxl_snip, annotated_dict, last_index)
        return annotated_dict


stamp_Beethoven = Stamper(
    "Polonaise.mxl",
    "Polonaise.mxl",
)
is_this_a_dict = stamp_Beethoven.stamp()
