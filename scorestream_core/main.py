from music21 import converter, stream
import subprocess
from timeit import default_timer as timer
from datetime import timedelta
import librosa

input_pdf_filepath = "C:/Users/jingx/git_wa/ScoreStream-core/Polonaise.pdf"
input_audio_filepath = (
    "C:/Users/jingx/git_wa/ScoreStream-core/Polonaise_audio_1st_pg.mp3"
)

duration = librosa.get_duration(path=input_audio_filepath)
print("duration: ", duration)


start = timer()

# result = subprocess.run(
#     [
#         "C:/Program Files/Audiveris/bin/Audiveris.bat",
#         "-export",
#         "-batch",
#         "-output",
#         "C:/Users/jingx/git_wa/ScoreStream-core",
#         input_pdf_filepath,
#     ],
#     # capture_output=True,
#     # text=True,
# )

end = timer()
print(timedelta(seconds=end - start))

polonaise = converter.parse("../Polonaise.mxl")

stream_of_bars = (
    polonaise.flatten(retainContainers=True)
    .getElementsByClass(stream.base.Measure)
    .stream()
)
polonaise.show("musicxml.png")
# or, polonaise.show("lily")

last_bar = stream_of_bars[-1].number

seconds_per_bar: int = duration / last_bar


def end_time(bar_number: int):
    return bar_number * seconds_per_bar


# for i in range(1, last_bar):
#     print(i, end_time(i))
