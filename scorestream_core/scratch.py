from music21 import converter, stream

polonaise = converter.parse("../Polonaise.mxl")
polonaise.show("musicxml")

stream_of_bars = (
    polonaise.flatten(retainContainers=True)
    .getElementsByClass(stream.base.Measure)
    .stream()
)
