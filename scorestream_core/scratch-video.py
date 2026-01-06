from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from scorestream_core.match_timestamp import is_this_a_dict
from music21 import *


print(is_this_a_dict)

strip_paths = ["page_1_strip_2.mxl", "page_1_strip_3.mxl", "page_1_strip_4.mxl"]

timeline = []

strip_start = 0
strip_end = 0
measure_count = 0

for i in range(2, 5):
    strip = converter.parse(f"page_1_strip_{i}.mxl").flatten(retainContainers=True)
    measures = strip.getElementsByClass("Measure")
    last_measure = measures[-1]
    measure_count += last_measure.measureNumber
    strip_end = is_this_a_dict[measure_count]
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
