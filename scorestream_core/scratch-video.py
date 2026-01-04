from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

timeline = [
    ("page_1_strip_2.png", 0.0, 6.5),
    ("page_1_strip_3.png", 6.5, 11.9),
    ("page_1_strip_4.png", 11.9, 19.5),
    # ("page_1_strip_5.png", 19.5, 26.9),
    # ("page_1_strip_6.png", 26.9, 34.0),
]

clips = []

for img, start, end in timeline:
    duration = end - start
    clip = ImageClip(img).with_duration(duration)
    clips.append(clip)

video = concatenate_videoclips(clips, method="compose")
audio = AudioFileClip(
    "C:/Users/jingx/git_wa/ScoreStream-core/Polonaise_3_lines.wav"
).with_start(0)

final = video.with_audio(audio)
final.write_videofile("final.mp4", fps=30, codec="libx264", audio_codec="aac")
