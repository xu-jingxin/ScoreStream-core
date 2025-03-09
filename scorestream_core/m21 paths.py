from music21 import environment

us = environment.UserSettings()
print(us.keys())
print(us["lilypondPath"])
us["lilypondPath"] = (
    "C:/Program Files (x86)/LilyPond/usr/bin/lilypond.exe"  # for example.
)

print(us["musicxmlPath"])
