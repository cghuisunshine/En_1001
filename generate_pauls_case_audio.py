#!/usr/bin/env python3
"""Generate per-page Edge TTS audio and word timings for pauls_case.html."""

import argparse
import asyncio
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "pauls_case.html"
OUTPUT = ROOT / "pauls_case_audio"
VOICE = "en-US-AriaNeural"
TICKS_PER_SECOND = 10_000_000


class StoryParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.page = None
        self.paragraph = None
        self.pages = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "section" and "reader-page" in attributes.get("class", "").split():
            self.page = attributes["id"].removeprefix("page-")
            self.pages[self.page] = []
        if tag == "p" and self.page and self.stack[-1:] == ["section"]:
            if "note" not in attributes.get("class", "").split():
                self.paragraph = []
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "p" and self.paragraph is not None:
            self.pages[self.page].append("".join(self.paragraph))
            self.paragraph = None
        if tag == "section":
            self.page = None
        if self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self.paragraph is not None:
            self.paragraph.append(data)


def source_pages():
    parser = StoryParser()
    parser.feed(SOURCE.read_text(encoding="utf-8"))
    if len(parser.pages) != 18 or not all(parser.pages.values()):
        raise ValueError("Expected story paragraphs on all 18 pages")
    return parser.pages


def find_span(text, spoken, cursor):
    """Locate a spoken word in the exact source text, allowing OCR punctuation."""
    wanted = re.sub(r"\W+", "", spoken, flags=re.UNICODE).casefold()
    if not wanted:
        return None
    for match in re.finditer(r"\w+(?:[’'\-]\w+)*", text[cursor:]):
        start = cursor + match.start()
        end = cursor + match.end()
        candidate = re.sub(r"\W+", "", text[start:end], flags=re.UNICODE).casefold()
        if candidate == wanted:
            return start, end
        if start > cursor + 100:
            break
    return None


async def synthesize(page, paragraphs, voice):
    text = "\n\n".join(paragraphs)
    audio_path = OUTPUT / f"page-{page}.mp3"
    metadata_path = OUTPUT / f"page-{page}.words.json"
    if audio_path.exists() and metadata_path.exists():
        previous = json.loads(metadata_path.read_text(encoding="utf-8"))
        if previous.get("text") == text and previous.get("voice") == voice and previous.get("words"):
            return previous

    words = []
    cursor = 0
    missed = 0
    communicate = edge_tts.Communicate(text, voice=voice, boundary="WordBoundary")
    partial_path = audio_path.with_suffix(".partial")
    try:
        with partial_path.open("wb") as audio_file:
            async for message in communicate.stream():
                if message["type"] == "audio":
                    audio_file.write(message["data"])
                elif message["type"] == "WordBoundary":
                    span = find_span(text, message.get("text", ""), cursor)
                    if span is None:
                        missed += 1
                        continue
                    start_char, end_char = span
                    cursor = end_char
                    start = round(message["offset"] / TICKS_PER_SECOND, 4)
                    end = round((message["offset"] + message["duration"]) / TICKS_PER_SECOND, 4)
                    words.append([start, end, start_char, end_char])
        if not words or missed > max(5, len(words) * 0.02):
            raise ValueError(f"Page {page}: {len(words)} matched words, {missed} unmatched")
        partial_path.replace(audio_path)
        data = {"text": text, "voice": voice, "words": words}
        metadata_path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"Page {page}: {len(words)} words, {missed} unmatched", flush=True)
        return data
    finally:
        partial_path.unlink(missing_ok=True)


def page_metadata(paragraphs, words):
    page = []
    cursor = 0
    for paragraph in paragraphs:
        end = cursor + len(paragraph)
        local_words = [[start, stop, a - cursor, b - cursor]
                       for start, stop, a, b in words if cursor <= a < b <= end]
        page.append({"text": paragraph, "words": local_words})
        cursor = end + 2
    if sum(len(item["words"]) for item in page) != len(words):
        raise ValueError("A word boundary crossed a paragraph")
    return page


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", default=VOICE)
    args = parser.parse_args()
    pages = source_pages()
    OUTPUT.mkdir(exist_ok=True)
    all_data = {}
    for page, paragraphs in pages.items():
        data = await synthesize(page, paragraphs, args.voice)
        all_data[page] = page_metadata(paragraphs, data["words"])
    (OUTPUT / "timings.js").write_text(
        "// Generated by generate_pauls_case_audio.py.\n"
        + "window.PAULS_CASE_AUDIO = "
        + json.dumps(all_data, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT / 'timings.js'}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
