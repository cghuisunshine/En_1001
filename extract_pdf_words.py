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


def extract_pdf_text(input_path: Path) -> str:
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        raise RuntimeError("Missing `pdftotext`. Install poppler, then rerun.")

    with tempfile.TemporaryDirectory(prefix="pdf_words_") as tmpdir:
        output_txt = Path(tmpdir) / "document.txt"
        result = subprocess.run(
            [pdftotext, str(input_path), str(output_txt)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "PDF text extraction failed.\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )
        return output_txt.read_text(encoding="utf-8", errors="ignore")


def extract_words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_frequency_csv(path: Path, counter: Counter[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["word", "count"])
        for word, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
            writer.writerow([word, count])


def write_frequency_txt(path: Path, counter: Counter[str]) -> None:
    lines = [f"{word}\t{count}" for word, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))]
    write_lines(path, lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract all words from a PDF and sort them by frequency."
    )
    parser.add_argument("input", help="Path to the PDF file")
    parser.add_argument(
        "--out-dir",
        default="pdf_words_out",
        help="Directory to write output files into",
    )
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"Input file not found: {input_path}", file=sys.stderr)
        return 1
    if input_path.suffix.lower() != ".pdf":
        print(f"Input is not a PDF: {input_path}", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = input_path.stem
    all_words_path = out_dir / f"{stem}.all_words.txt"
    unique_words_path = out_dir / f"{stem}.unique_words.txt"
    freq_csv_path = out_dir / f"{stem}.word_frequencies.csv"
    freq_txt_path = out_dir / f"{stem}.words_by_frequency.txt"
    raw_text_path = out_dir / f"{stem}.raw_text.txt"

    try:
        text = extract_pdf_text(input_path)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    words = extract_words(text)
    normalized = [word.lower() for word in words]
    frequencies = Counter(normalized)

    raw_text_path.write_text(text, encoding="utf-8")
    write_lines(all_words_path, words)
    write_lines(unique_words_path, sorted(frequencies))
    write_frequency_csv(freq_csv_path, frequencies)
    write_frequency_txt(freq_txt_path, frequencies)

    print(f"Input: {input_path}")
    print(f"All words: {all_words_path} ({len(words)} words)")
    print(f"Unique words: {unique_words_path} ({len(frequencies)} words)")
    print(f"Words by frequency: {freq_txt_path}")
    print(f"Frequencies CSV: {freq_csv_path}")
    print(f"Raw text: {raw_text_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
