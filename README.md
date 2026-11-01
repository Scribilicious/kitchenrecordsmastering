# matchering mastering CLI

`master.py` masters one target audio file against every reference track in a
genre folder and writes one mastered file per reference.

## Requirements

Dependencies (matchering 2.0.6, soundfile/libsndfile 1.2.2, numpy, ...) live
in the project virtualenv. On a fresh clone or another machine, create it
once with:

```
./setup.sh
```

(The `venv/` in this repo is not portable across machines.) Then always run
the script with the venv interpreter — the system `python3` does not have
matchering:

```
./venv/bin/python master.py ...
```

or activate the venv first (`source venv/bin/activate`), then plain
`python master.py ...` works.

## Usage

```
./venv/bin/python master.py <file> <genre> [-f {24bit,16bit,mp3}] [--preview] [-o FOLDER]
```

- `file` — path to the audio file to master (`~` is expanded, e.g.
  `~/Desktop/song.wav`)
- `genre` — subfolder of `reference/` containing the reference tracks
  (currently: `techno`)
- `-f` / `--format` — output format, one of `24bit` (default), `16bit`, `mp3`
- `--preview` — additionally save the loudest section of each master as a
  separate file (matchering picks the loudest 30 s window by RMS, analyzed in
  5 s steps; saved in the same format as the master)
- `-o` / `--output` — output folder (default: the same folder as the source
  file). Created if it does not exist.

Example:

```
./venv/bin/python master.py ~/Desktop/LLMv2Final.wav techno -f mp3
```

## References

Reference tracks live in `reference/<genre>/`. To add a new genre, create a
folder (e.g. `reference/house/`) and drop audio files into it. Every file in
the folder is used as a reference, in sorted order.

## Output

For each reference, one file is written to the **output folder** (default:
the source file's folder; override with `-o`):

```
<target_stem>_mastered_<format>_(<reference_slug>).<ext>
```

where `<reference_slug>` is the reference filename lowercased with spaces
replaced by underscores, e.g.:

```
LLMv2Final_mastered_24bit_(garden_of_god_-_fiddler).wav
LLMv2Final_mastered_mp3_(mau_p_-_drugs_from_amsterdam).mp3
LLMv2Final_mastered_24bit_loudest_(garden_of_god_-_fiddler).wav   # only with --preview
```

Formats: `24bit` = WAV PCM_24, `16bit` = WAV PCM_16, `mp3` = MPEG Layer III.
(There is no 12-bit WAV subtype in libsndfile; 16bit is the lowest PCM depth.)

## Building a standalone executable

PyInstaller can bundle the script into a single file (no venv needed on the
target machine):

```
venv/bin/pip install pyinstaller
venv/bin/pyinstaller --onefile --clean --name master master.py
```

The binary lands in `dist/master` (~80 MB). When frozen, the script looks for
`reference/` **next to the executable**, not next to the source — so copy
`reference/` into `dist/` (already done here). Outputs are still written to
the current working directory:

```
dist/master ~/Desktop/song.wav techno -f mp3 --preview -o ~/Desktop/masters
```

## Notes

- The script prints an ASCII banner on startup and matchering's progress log.
- Errors (missing target file, unknown genre, empty reference folder) exit
  with code 2 and a usage message.
- There is no test suite; to smoke-test, generate a short wav and run it
  against `techno`, then check the outputs with `soundfile.info`.
