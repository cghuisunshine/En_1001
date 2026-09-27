#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def convert_to_text(input_path: Path, output_txt: Path) -> None:
    ebook_convert = shutil.which("ebook-convert")
    if not ebook_convert:
        raise RuntimeError(
            "Missing `ebook-convert` (Calibre CLI). Install Calibre, then rerun.\n"
            "macOS example: brew install --cask calibre"
        )

    result = subprocess.run(
        [ebook_convert, str(input_path), str(output_txt)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Conversion failed.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def extract_words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_frequencies(path: Path, counter: Counter[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "count"])
        for word, count in sorted(counter.items()):
            writer.writerow([word, count])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract all words from an ebook file and write ordered, unique, and frequency outputs."
    )
    parser.add_argument("input", help="Path to the ebook file, e.g. .azw3")
    parser.add_argument(
        "--out-dir",
        default="ebook_words_out",
        help="Directory to write output files into",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = input_path.stem
    ordered_path = out_dir / f"{stem}.all_words.txt"
    unique_path = out_dir / f"{stem}.unique_words.txt"
    freq_path = out_dir / f"{stem}.word_frequencies.csv"
    text_dump_path = out_dir / f"{stem}.raw_text.txt"

    try:
        with tempfile.TemporaryDirectory(prefix="ebook_words_") as tmpdir:
            tmp_txt = Path(tmpdir) / "converted.txt"
            convert_to_text(input_path, tmp_txt)
            text = tmp_txt.read_text(encoding="utf-8", errors="ignore")
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    text_dump_path.write_text(text, encoding="utf-8")

    ordered_words = extract_words(text)
    unique_words = sorted({word.lower() for word in ordered_words})
    frequencies = Counter(word.lower() for word in ordered_words)

    write_lines(ordered_path, ordered_words)
    write_lines(unique_path, unique_words)
    write_frequencies(freq_path, frequencies)

    print(f"Input: {input_path}")
    print(f"Ordered words: {ordered_path} ({len(ordered_words)} words)")
    print(f"Unique words: {unique_path} ({len(unique_words)} words)")
    print(f"Frequencies: {freq_path}")
    print(f"Raw text: {text_dump_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
