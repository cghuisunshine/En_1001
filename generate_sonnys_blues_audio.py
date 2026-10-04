#!/usr/bin/env python3
"""Generate per-page Edge TTS audio and word timings for sonnys_blues.html."""

import argparse
import asyncio
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import edge_tts


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sonnys_blues.html"
OUTPUT = ROOT / "sonnys_blues_audio"
VOICE = "en-US-AriaNeural"
TICKS_PER_SECOND = 10_000_000


class StoryParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.page = None
        self.paragraph = None
        self.pages = {}
        self.skip_sup = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "section" and "reader-page" in attributes.get("class", "").split():
            self.page = attributes["id"].removeprefix("page-")
            self.pages[self.page] = []
        if tag == "p" and self.page and "story-paragraph" in attributes.get("class", "").split():
            self.paragraph = []
        if tag == "sup" and self.paragraph is not None:
            self.skip_sup = True
        if tag in {"img", "input", "meta", "link", "br", "hr", "source"}:
            return
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "sup":
            self.skip_sup = False
        if tag == "p" and self.paragraph is not None:
            self.pages[self.page].append("".join(self.paragraph))
            self.paragraph = None
        if tag == "section":
            self.page = None
        if self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self.paragraph is not None and not self.skip_sup:
            self.paragraph.append(data)


def source_pages():
    parser = StoryParser()
    parser.feed(SOURCE.read_text(encoding="utf-8"))
    if list(parser.pages) != [str(page) for page in range(57, 80)] or not all(parser.pages.values()):
        raise ValueError("Expected story paragraphs on printed pages 57–79")
    transcription = json.loads((ROOT / "sonny_blues_img_transcription.json").read_text(encoding="utf-8"))
    for page in transcription["pages"]:
        expected = [re.sub(r"\[\d+\]", "", text) for text in page["paragraphs"]]
        if parser.pages[str(page["page"])] != expected:
            raise ValueError(f"Narration text differs from the transcription on page {page['page']}")
    return parser.pages


def find_span(text, spoken, cursor):
    """Map boundaries across OCR punctuation, compound words, and initials."""
    wanted = re.sub(r"\W+", "", spoken, flags=re.UNICODE).casefold()
    if not wanted:
        return None
    window = text[cursor:cursor + 200]
    letters = r"[\W_]*".join(re.escape(char) for char in wanted)
    match = re.search(r"(?<!\w)" + letters + r"(?!\w)", window, re.IGNORECASE)
    if match is not None and match.start() <= 100:
        return cursor + match.start(), cursor + match.end()
    # Edge can emit multiple boundaries for one source token, such as initials.
    match = re.match(r"[\W_]*(" + letters + r")", window, re.IGNORECASE)
    if match is not None:
        return cursor + match.start(1), cursor + match.end(1)
    return None


async def synthesize(page, paragraphs, voice, refresh=False):
    text = "\n\n".join(paragraphs)
    audio_path = OUTPUT / f"page-{page}.mp3"
    metadata_path = OUTPUT / f"page-{page}.words.json"
    if not refresh and audio_path.exists() and metadata_path.exists():
        previous = json.loads(metadata_path.read_text(encoding="utf-8"))
        if previous.get("text") == text and previous.get("voice") == voice and previous.get("words"):
            return previous

    words = []
    cursor = 0
    missed = 0
    unmatched = []
    communicate = edge_tts.Communicate(text, voice=voice, boundary="WordBoundary")
    partial_path = audio_path.with_suffix(".partial")
    try:
        with partial_path.open("wb") as audio_file:
            async for message in communicate.stream():
                if message["type"] == "audio":
                    audio_file.write(message["data"])
                elif message["type"] == "WordBoundary":
                    if not any(char.isalnum() for char in message.get("text", "")):
                        continue
                    span = find_span(text, message.get("text", ""), cursor)
                    if span is None:
                        missed += 1
                        unmatched.append(message.get("text", ""))
                        continue
                    start_char, end_char = span
                    cursor = end_char
                    start = round(message["offset"] / TICKS_PER_SECOND, 4)
                    end = round((message["offset"] + message["duration"]) / TICKS_PER_SECOND, 4)
                    words.append([start, end, start_char, end_char])
        if not words or missed > max(5, len(words) * 0.02):
            raise ValueError(f"Page {page}: {len(words)} matched words, {missed} unmatched: {unmatched}")
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
    parser.add_argument("--refresh-pages", nargs="*", type=int, default=[], choices=range(57, 80),
                        help="Regenerate selected pages even when their audio is cached")
    parser.add_argument("--jobs", type=int, default=3, choices=range(1, 7),
                        help="Maximum number of simultaneous page requests")
    args = parser.parse_args()
    pages = source_pages()
    OUTPUT.mkdir(exist_ok=True)
    semaphore = asyncio.Semaphore(args.jobs)
    async def generate(page, paragraphs):
        async with semaphore:
            for attempt in range(3):
                try:
                    data = await synthesize(page, paragraphs, args.voice, refresh=int(page) in args.refresh_pages)
                    return page, page_metadata(paragraphs, data["words"])
                except Exception as error:
                    if attempt == 2:
                        raise
                    print(f"Page {page}: retry after {type(error).__name__}: {error}", flush=True)
                    await asyncio.sleep(2 ** attempt)
    all_data = dict(await asyncio.gather(*(generate(page, paragraphs) for page, paragraphs in pages.items())))
    temporary = OUTPUT / "timings.js.partial"
    temporary.write_text(
        "// Generated by generate_sonnys_blues_audio.py.\n"
        + "window.SONNYS_BLUES_AUDIO = "
        + json.dumps(all_data, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    temporary.replace(OUTPUT / "timings.js")
    print(f"Wrote {OUTPUT / 'timings.js'}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
