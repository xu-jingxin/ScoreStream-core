import subprocess
import tempfile
import os
from pathlib import Path

timeline = [
    ("page_1_strip_2.png", 0.0, 6.5),
    ("page_1_strip_3.png", 6.5, 11.9),
    ("page_1_strip_4.png", 11.9, 19.5),
]

audio_path = "C:/Users/jingx/git_wa/ScoreStream-core/Polonaise_3_lines.wav"
output_path = "final.mp4"


def run(cmd):
    subprocess.run(cmd, check=True)


def create_image_clip(image_path, duration, output_path, fps=30):
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        image_path,
        "-t",
        str(duration),
        "-r",
        str(fps),
        "-pix_fmt",
        "yuv420p",
        "-c:v",
        "libx264",
        output_path,
    ]
    run(cmd)


def build_video_from_images(timeline, audio_path, output_path, fps=30):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        video_files = []

        # 1. Create image clips
        for i, (img, start, end) in enumerate(timeline):
            duration = end - start
            clip_path = tmp / f"clip_{i:03d}.mp4"

            create_image_clip(
                image_path=img,
                duration=duration,
                output_path=str(clip_path),
                fps=fps,
            )

            video_files.append(clip_path)

        # 2. Create concat list
        concat_file = tmp / "list.txt"
        with open(concat_file, "w") as f:
            for vf in video_files:
                f.write(f"file '{vf.as_posix()}'\n")

        # 3. Concatenate clips
        concat_video = tmp / "video.mp4"
        run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                str(concat_video),
            ]
        )

        # 4. Add audio
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(concat_video),
                "-i",
                audio_path,
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                output_path,
            ]
        )

    print(f"Video written to {output_path}")


build_video_from_images(timeline, audio_path, output_path)
