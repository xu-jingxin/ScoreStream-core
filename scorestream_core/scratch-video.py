from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from match_timestamp import Stamper
from music21 import *

stamp_Polonaise: dict = Stamper(
    "basic_pitch_transcription.mid",
    "Polonaise.mxl",
).stamp()

print(f"Matched timestamps: {stamp_Polonaise}")

strip_paths = ["page_1_strip_2.mxl", "page_1_strip_3.mxl", "page_1_strip_4.mxl"]

timeline = []

strip_start = 0
strip_end = 0
measure_count = 0

# Get max timestamp for interpolation fallback
max_measure = max(stamp_Polonaise.keys()) if stamp_Polonaise else 1
max_time = stamp_Polonaise.get(max_measure, 30.0)

def get_timestamp(measure_num):
    """Get timestamp for a measure, interpolating if not found."""
    if measure_num in stamp_Polonaise:
        return stamp_Polonaise[measure_num]
    # Interpolate based on known timestamps
    known = sorted(stamp_Polonaise.keys())
    if not known:
        return measure_num * 2.0  # Fallback: 2 seconds per measure
    if measure_num < known[0]:
        return stamp_Polonaise[known[0]] * measure_num / known[0]
    if measure_num > known[-1]:
        # Extrapolate using average time per measure
        avg_time_per_measure = stamp_Polonaise[known[-1]] / known[-1]
        return measure_num * avg_time_per_measure
    # Find surrounding known measures and interpolate
    for i, k in enumerate(known[:-1]):
        if k < measure_num < known[i+1]:
            ratio = (measure_num - k) / (known[i+1] - k)
            return stamp_Polonaise[k] + ratio * (stamp_Polonaise[known[i+1]] - stamp_Polonaise[k])
    return measure_num * 2.0

for i in range(2, 5):
    strip = converter.parse(f"page_1_strip_{i}.mxl").flatten(retainContainers=True)
    measures = strip.getElementsByClass("Measure")
    last_measure = measures[-1]
    measure_count += last_measure.measureNumber
    strip_end = get_timestamp(measure_count)
    timeline.append((f"page_1_strip_{i}.png", strip_start, strip_end))
    strip_start = strip_end

print(timeline)

clips = []

for img, start, end in timeline:
    duration = end - start
    clip = ImageClip(img).with_duration(duration)
    clips.append(clip)

video = concatenate_videoclips(clips, method="compose")
audio = AudioFileClip("Polonaise_3_lines.m4a").with_start(0)

final = video.with_audio(audio)
final.write_videofile("final.mp4", fps=30, codec="libx264", audio_codec="aac")
