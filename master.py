import argparse
import sys
from pathlib import Path

import matchering as mg

mg.log(print)

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

REFERENCE_DIR = BASE_DIR / "reference"

FORMATS = {
    "24bit": ("wav", mg.pcm24),
    "16bit": ("wav", mg.pcm16),
    "mp3": ("mp3", lambda file: mg.Result(file, "MPEG_LAYER_III")),
}

def intro():
    print(r'''               ,,                ,,
`7MMF' `YMM'   db   mm         `7MM
  MM   .M'          MM           MM
  MM .d"     `7MM mmMMmm ,p6"bo  MMpMMMb.  .gP"Ya `7MMpMMMb.
  MMMMM.       MM   MM  6M'  OO  MM    MM ,M'   Yb  MM    MM
  MM  VMA      MM   MM  8M       MM    MM 8M""""""  MM    MM
  MM   `MM.    MM   MM  YM.    , MM    MM YM.    ,  MM    MM
.JMML.   MMb..JMML. `MbmoYMbmd'.JMML  JMML.`Mbmmd'.JMML  JMML.
                                                    ,,
`7MM"""Mq.      -=[ MASTERING AGENT 2.0 ]=-       `7MM
  MM   `MM.                                         MM
  MM   ,M9  .gP"Ya   ,p6"bo   ,pW"Wq.`7Mb,od8  ,M""bMM  ,pP"Ybd
  MMmmdM9  ,M'   Yb 6M'  OO  6W'   `Wb MM' "',AP    MM  8I   `"
  MM  YM.  8M"""""" 8M       8M     M8 MM    8MI    MM  `YMMMa.
  MM   `Mb.YM.    , YM.    , YA.   ,A9 MM    `Mb    MM  L.   I8
.JMML. .JMM.`Mbmmd'  YMbmd'   `Ybmd9'.JMML.   `Wbmd"MML.M9mmmP'
''')


def main():
    intro()
    parser = argparse.ArgumentParser(
        description="Master a target file against every reference in reference/<genre>/ (default output: pcm24)."
    )
    parser.add_argument("file", help="Path to the target audio file to master")
    parser.add_argument("genre", help="Genre folder inside reference/ (e.g. techno)")
    parser.add_argument(
        "-f",
        "--format",
        choices=FORMATS.keys(),
        default="24bit",
        help="Output format (default: 24bit)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Also save the loudest section of each master as a separate file",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output folder (default: same folder as the source file)",
    )
    args = parser.parse_args()

    target = Path(args.file).expanduser()
    if not target.is_file():
        parser.error(f"Target file not found: {target}")

    output_dir = Path(args.output).expanduser() if args.output else target.parent
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        parser.error(f"Cannot use output folder {output_dir}: {e}")

    reference_dir = REFERENCE_DIR / args.genre
    if not reference_dir.is_dir():
        parser.error(f"Reference folder not found: {reference_dir}")

    references = sorted(p for p in reference_dir.iterdir() if p.is_file())
    if not references:
        parser.error(f"No reference files in {reference_dir}")

    ext, make_result = FORMATS[args.format]
    for reference in references:
        ref_name = reference.stem.lower().replace(" ", "_")
        result = output_dir / f"{target.stem}_mastered_{args.format}_({ref_name}).{ext}"
        print(f"Mastering {target.name} against {reference.name} -> {result}")
        process_kwargs = {}
        if args.preview:
            preview = (
                output_dir
                / f"{target.stem}_mastered_{args.format}_loudest_({ref_name}).{ext}"
            )
            print(f"  loudest-part preview -> {preview}")
            process_kwargs["preview_result"] = make_result(str(preview))
        mg.process(
            target=str(target),
            reference=str(reference),
            results=[make_result(str(result))],
            **process_kwargs,
        )


if __name__ == "__main__":
    main()
