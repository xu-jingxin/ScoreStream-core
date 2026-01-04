from music21 import converter, stream
import subprocess
from timeit import default_timer as timer
from datetime import timedelta

input_pdf_filepath = (
    r"C:\Users\jingx\git_wa\ScoreStream-core\scorestream_core\page_1_strip_2.png"
)
input_audio_filepath = (
    "C:/Users/jingx/git_wa/ScoreStream-core/Polonaise_audio_1st_pg.mp3"
)


def call_audiveris(sheet_path):
    start = timer()

    result = subprocess.run(
        [
            "C:/Program Files/Audiveris/bin/Audiveris.bat",
            "-export",
            "-batch",
            "-output",
            "C:/Users/jingx/git_wa/ScoreStream-core",
            sheet_path,
        ],
        # capture_output=True,
        # text=True,
    )

    end = timer()
    print(timedelta(seconds=end - start))  # this times how long Audiveris takes


call_audiveris(input_pdf_filepath)

# polonaise = converter.parse("../page_1_strip_2.mxl")
#
# stream_of_bars = (
#     polonaise.flatten(retainContainers=True)
#     .getElementsByClass(stream.base.Measure)
#     .stream()
# )
# polonaise.show("text")

# ^^^^ port over from past work in previous repos
