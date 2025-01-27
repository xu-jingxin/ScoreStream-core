from music21 import converter, stream

mxl = converter.parse("/tests/Sonate_No._14_Moonlight_1st_Movement.mxl")
stream_of_bars = (
    mxl.flatten(retainContainers=True).getElementsByClass(stream.base.Measure).stream()
)
stream_of_bars.show("text")
print(stream_of_bars[-1].number)
