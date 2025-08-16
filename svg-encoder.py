# -------------------------------------------
from __future__ import annotations

from urllib.parse import quote
from dataclasses import dataclass

from pathlib import Path
from typing import Iterator, List

import argparse
import base64
import shutil
import textwrap
# -------------------------------------------

DEFAULT_OUTPUT_DIR: str = "svg_encoded"


class Flags:
    INPUT = "input"
    OUTPUT = "output"
    RECURSIVE = "recursive"
    OVERRIDE = "override"


@dataclass
class ConversionRecord:
    input_path: Path
    relative_dir: Path
    stem: str
    written_files: List[Path]
    b64_length: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="svg_encoder", add_help=True)
    parser.add_argument(Flags.INPUT, help="Input folder")
    parser.add_argument(
        "-o",
        "--output",
        dest=Flags.OUTPUT,
        default=DEFAULT_OUTPUT_DIR,
        help="The specified output directory:: by default it is: ./" +
        DEFAULT_OUTPUT_DIR,
    )
    parser.add_argument(
        "-r",
        "--recursive",
        dest=Flags.RECURSIVE,
        action="store_true",
        help="Enable to recursively scan for .svg files",
    )
    parser.add_argument(
        "-f",
        "--override",
        dest=Flags.OVERRIDE,
        action="store_true",
        help="Enable to override existing encoded files",
    )
    return parser.parse_args()


def fetch_svgs(input_root: Path, recursive: bool = False) -> Iterator[Path]:
    glob_method = input_root.rglob if recursive else input_root.glob
    for svg_path in glob_method("*.svg"):
        if svg_path.is_file():
            yield svg_path


def convert_file(
        svg_path: Path,
        input_root: Path,
        output_root: Path,
        override: bool = False) -> ConversionRecord:
    try:
        relative_dir = svg_path.parent.relative_to(input_root)
    except Exception:
        relative_dir = Path(".")

    output_dir = output_root.joinpath(relative_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_bytes = svg_path.read_bytes()
    base64_text = base64.b64encode(raw_bytes).decode("ascii")
    data_uri = "data:image/svg+xml;base64," + base64_text
    percent_encoded_b64 = quote(base64_text, safe="")
    data_uri_percent = "data:image/svg+xml;base64," + percent_encoded_b64

    stem = svg_path.stem
    encodings_file = output_dir.joinpath(stem + ".encodings.txt")

    if encodings_file.exists() and not override:
        return ConversionRecord(
            input_path=svg_path,
            relative_dir=relative_dir,
            stem=stem,
            written_files=[encodings_file],
            b64_length=len(base64_text),
        )

    sections = [
        ("RAW BASE64", base64_text),
        ("DATA URI", data_uri),
        ("PERCENT-ENCODED BASE64", percent_encoded_b64),
        ("DATA URI (PERCENT-ENCODED)", data_uri_percent),
    ]

    lines: List[str] = []
    for title, content in sections:
        lines.append(f"===| {title} |===")
        lines.append(content)
        lines.append("")

    content_text = "\n".join(lines).rstrip() + "\n"
    encodings_file.write_text(content_text, encoding="utf-8")

    return ConversionRecord(
        input_path=svg_path,
        relative_dir=relative_dir,
        stem=stem,
        written_files=[encodings_file],
        b64_length=len(base64_text),
    )


def main() -> None:
    args = parse_args()

    input_root = Path(getattr(args, Flags.INPUT)).resolve()

    if not input_root.is_dir():
        raise SystemExit(
            f"Error: The path: '{input_root}' is not a valid directory")
    elif not input_root.exists():
        raise SystemExit(
            f"Error: The directory: '{input_root}' does not exist")

    output_root = Path(getattr(args, Flags.OUTPUT)).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    recursive = bool(getattr(args, Flags.RECURSIVE))
    override = bool(getattr(args, Flags.OVERRIDE))

    conversion_log: List[ConversionRecord] = []
    file_count: int = 0

    try:
        for svg in fetch_svgs(input_root, recursive=recursive):
            record = convert_file(
                svg, input_root, output_root, override=override)
            conversion_log.append(record)
            file_count += 1
            
            # Convoluted formatting is convoluted... but formatted
            label_text = "| ENCODED |: "
            indent_a = '\t' + label_text
            indent_b = '\t' + ' ' * (len(label_text)) 
            
            console_width = shutil.get_terminal_size((120,20)).columns
            wrap_width_guarantee = max(40,console_width-1)
            
            full_msg = f"{svg} -> {', '.join(str(path) for path in record.written_files)}"
            
            wrapped_text = textwrap.fill(full_msg,width=wrap_width_guarantee,initial_indent=indent_a,subsequent_indent=indent_b)
            print(wrapped_text + "\n")
            
    except KeyboardInterrupt:
        print(f"User aborted process...")

    print(f"\tEncoded {file_count} file{'s' if file_count > 1 else ''} \n")


if __name__ == "__main__":
    print(f"| SVG_ENCODER |\n\tStarting encoding process...\n")
    main()
    print(f"Process finished\n")
