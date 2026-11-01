# AGENTS.md — working in this repo

## Running the code

- Always use the project venv interpreter: `./venv/bin/python master.py ...`
  The system `python3` has no `matchering` installed and fails with
  `ModuleNotFoundError`. Alternatively `source venv/bin/activate` first.
- First-time setup on a fresh machine/clone: run `./setup.sh` (creates
  `venv/` if missing and installs `matchering==2.0.6`; idempotent). The
  committed `venv/` is machine-specific and not portable.
- Entry point is `master.py` (no package, no tests, no build step).

## What master.py does

- CLI: `master.py <file> <genre> [-f {24bit,16bit,mp3}] [--preview] [-o FOLDER]`
  (argparse).
- Masters `<file>` against every file in `reference/<genre>/` via
  `matchering.process`, writing one output per reference into the **output
  folder**: `-o/--output` if given (created with mkdir -p), else the source
  file's folder (`target.parent`). Never the cwd unless it is also the
  source folder.
- Output naming: `<target_stem>_mastered_<format>_(<ref_slug>).<ext>` where
  `<ref_slug>` = reference stem lowercased, spaces → underscores.
- `--preview` passes `preview_result=make_result(preview_path)` to
  `mg.process`, which saves the loudest section of the master (default:
  loudest 30 s window, 5 s analysis step — see `Config` in matchering's
  `defaults.py`) as `<target>_mastered_<format>_loudest_(<ref_slug>).<ext>`
  in the same format. Reuses the `FORMATS` maker so the preview subtype
  always matches the selected format.
- Format selection is the `FORMATS` dict at the top of `master.py`
  (`24bit` default → `mg.pcm24`, `16bit` → `mg.pcm16`, `mp3` →
  `mg.Result(file, "MPEG_LAYER_III")`). The file extension picks the
  container, the `Result` subtype picks bit depth/codec. libsndfile has no
  PCM_12 subtype — do not add a "12bit" format.
- `reference/` subfolders are genres; add new ones by creating a folder with
  audio files. `REFERENCE_DIR` is resolved relative to `master.py` (or the
  executable when frozen), so cwd affects neither reference lookup nor output
  location.

## Editing constraints

- `intro()` holds the ASCII banner as a **raw triple-single-quoted string**
  (`r'''...'''`) because the art contains `"""` and quotes. Keep that quoting
  if you touch the art; do not reformat it.
- `~` in the target path is expanded via `Path.expanduser()`; beware Unicode
  look-alike tildes (U+02DC) pasted into commands — they are not expanded by
  the shell.
- `REFERENCE_DIR` resolves next to `master.py` normally, but next to the
  executable (`sys.executable`) when frozen (PyInstaller). Build with
  `venv/bin/pyinstaller --onefile --clean --name master master.py`; copy
  `reference/` into `dist/` so the binary finds its references. `setup.sh`
  installs runtime deps only — `pip install pyinstaller` is a build-time
  extra. Rebuilds leave `build/` and `master.spec` in the repo root.
- Keep README.md in sync with CLI behavior (arguments, formats, naming).

## Verifying changes

No test suite. Smoke-test with a small generated wav, e.g.:

```
./venv/bin/python master.py /tmp/t.wav techno -f mp3
```

then confirm outputs with `soundfile.info(...)` and clean up the generated
files afterwards.
