# ScoreStream-core
A tool to combine score images and audio streams into videos.

# Features


# How to get started

You need music21. pip install music21.
(or is one supposed to use poetry?)

You need to install Audiveris (which needs Java >21)
https://github.com/Audiveris/audiveris?tab=readme-ov-file

You might need to install lilypond to run _stream_.show("lily")
https://lilypond.org/doc/v2.23/Documentation/web/download

Or musescore, to run _stream_.show("musicxml")
https://musescore.org/en/download

After installing lilypond or musescore, you need to update their paths for music21. see m21 paths.py. 

Install Python 3.12 via Scoop
```commandline
scoop bucket add versions
scoop install python312
```

Install pipx
```commandline
scoop install pipx
```

Install Poetry
```commandline
pipx install poetry
pipx ensurepath
```
Install packages with Poetry
```commandline
poetry install
```

Install MiniConda
```commandline
scoop install miniconda3
```

Install packages with Conda
```commandline
conda env create -f environment.yaml
```




# Future Product Roadmap

