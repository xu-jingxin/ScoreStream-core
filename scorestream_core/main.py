from music21 import converter, stream
import subprocess
from timeit import default_timer as timer
from datetime import timedelta

input_pdf_filepath = "C:/Users/jingx/Downloads/Polonaise.pdf"

start = timer()

result = subprocess.run(
    [
        "C:/Program Files/Audiveris/bin/Audiveris.bat",
        "-export",
        "-batch",
        "-output",
        "C:/Users/jingx/git_wa/ScoreStream-core",
        input_pdf_filepath,
    ],
    # capture_output=True,
    # text=True,
)

end = timer()
print(timedelta(seconds=end - start))

polonaise = converter.parse("../Polonaise.mxl")
# polonaise.show("lily")

stream_of_bars = (
    polonaise.flatten(retainContainers=True)
    .getElementsByClass(stream.base.Measure)
    .stream()
)
stream_of_bars.show("text")
print(stream_of_bars[-1].number)
