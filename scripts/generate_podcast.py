from __future__ import annotations

import html
import json
import os
import re
import subprocess
import tempfile
import textwrap
from datetime import datetime
from email.utils import format_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "input" / "narration.txt"
OUTPUT_DIR = ROOT / "output"
DOCS_DIR = ROOT / "docs"
HISTORY_FILE = DOCS_DIR / "podcast-history.json"

REPOSITORY = "fatpotato333/news"
SITE_URL = "https://fatpotato333.github.io/news"
RELEASE_TAG = "daily-podcast"

MODEL = "gpt-4o-mini-tts"
VOICE = os.getenv("OPENAI_TTS_VOICE", "cedar")

MAX_CHARS_PER_CHUNK = 5_500
MAX_NARRATION_WORDS = 1_200
MAX_DURATION_SECONDS = 600
TARGET_DURATION_SECONDS = 590
MAX_SPEEDUP = 1.10
EPISODES_TO_KEEP = 7


def split_text(text: str) -> list[str]:
    units = [
        unit.strip()
        for unit in re.split(r"(?<=[.!?])\s+|\n+", text)
        if unit.strip()
    ]

    chunks: list[str] = []
    current = ""

    for unit in units:
        parts = textwrap.wrap(
            unit,
            width=MAX_CHARS_PER_CHUNK,
            break_long_words=False,
            break_on_hyphens=False,
        ) or [unit]

        for part in parts:
            candidate = f"{current} {part}".strip()

            if current and len(candidate) > MAX_CHARS_PER_CHUNK:
                chunks.append(current)
                current = part
            else:
                current = candidate

    if current:
        chunks.append(current)

    return chunks


def probe_duration(path: Path) -> float:
    return float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
    )


def format_duration(total_seconds: int) -> str:
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def enforce_duration_limit(episode_path: Path) -> int:
    duration = probe_duration(episode_path)

    if duration <= MAX_DURATION_SECONDS:
        return int(round(duration))

    speedup = duration / TARGET_DURATION_SECONDS

    if speedup > MAX_SPEEDUP:
        raise ValueError(
            f"Generated episode is {duration:.1f} seconds long. "
            "Shorten input/narration.txt; the allowed maximum is 600 seconds."
        )

    shortened_path = episode_path.with_name(f"{episode_path.stem}-shortened.mp3")

    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(episode_path),
            "-filter:a",
            f"atempo={speedup:.6f}",
            "-ac",
            "1",
            "-ar",
            "24000",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "96k",
            str(shortened_path),
        ],
        check=True,
    )

    shortened_path.replace(episode_path)
    final_duration = probe_duration(episode_path)

    if final_duration > MAX_DURATION_SECONDS:
        raise ValueError(
            f"Episode remains {final_duration:.1f} seconds after adjustment."
        )

    return int(round(final_duration))


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []

    try:
        payload = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    episodes = payload.get("episodes", [])
    return episodes if isinstance(episodes, list) else []


def build_feed(episodes: list[dict]) -> str:
    description = "Martin's concise daily intelligence briefing."

    items: list[str] = []

    for episode in episodes:
        title = html.escape(str(episode["title"]))
        item_description = html.escape(str(episode["description"]))
        pub_date = html.escape(str(episode["pub_date"]))
        guid = html.escape(str(episode["guid"]))
        asset_url = html.escape(str(episode["url"]), quote=True)
        length = int(episode["length"])
        duration = html.escape(str(episode["duration"]))

        items.append(
            f"""    <item>
      <title>{title}</title>
      <description>{item_description}</description>
      <pubDate>{pub_date}</pubDate>
      <guid isPermaLink="false">{guid}</guid>
      <enclosure url="{asset_url}" length="{length}" type="audio/mpeg" />
      <itunes:duration>{duration}</itunes:duration>
    </item>"""
        )

    joined_items = "\n\n".join(items)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>Martin's Daily News</title>
    <link>{SITE_URL}/</link>
    <description>{description}</description>
    <language>en-us</language>
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml" />
    <itunes:author>Martin</itunes:author>
    <itunes:explicit>false</itunes:explicit>

{joined_items}
  </channel>
</rss>
"""


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

    narration = INPUT_FILE.read_text(encoding="utf-8").strip()

    if len(narration) < 100:
        raise ValueError("Narration is unexpectedly short.")

    word_count = len(re.findall(r"\b[\w'-]+\b", narration))

    if word_count > MAX_NARRATION_WORDS:
        raise ValueError(
            f"Narration has {word_count} words; maximum is "
            f"{MAX_NARRATION_WORDS}."
        )

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not available.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(ZoneInfo("Europe/Prague"))
    date_slug = now.strftime("%Y-%m-%d")
    episode_filename = f"daily-news-{date_slug}.mp3"
    episode_path = OUTPUT_DIR / episode_filename

    client = OpenAI(api_key=api_key)
    chunks = split_text(narration)

    with tempfile.TemporaryDirectory() as temp_directory:
        temp_path = Path(temp_directory)
        segment_paths: list[Path] = []

        for index, chunk in enumerate(chunks, start=1):
            segment_path = temp_path / f"segment-{index:03d}.wav"

            with client.audio.speech.with_streaming_response.create(
                model=MODEL,
                voice=VOICE,
                input=chunk,
                instructions=(
                    "Read only the supplied text. Use one calm, natural "
                    "American-English newsreader voice at a brisk but comfortable "
                    "pace of roughly 155 to 165 words per minute. Use clear "
                    "pronunciation, minimal dramatic emphasis, and only brief "
                    "pauses between stories. Do not add greetings, commentary, "
                    "transitions, conclusions, or any words not present in the text."
                ),
                response_format="wav",
            ) as response:
                response.stream_to_file(segment_path)

            segment_paths.append(segment_path)

        concat_file = temp_path / "segments.txt"
        concat_file.write_text(
            "\n".join(f"file '{segment.as_posix()}'" for segment in segment_paths),
            encoding="utf-8",
        )

        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-ac",
                "1",
                "-ar",
                "24000",
                "-codec:a",
                "libmp3lame",
                "-b:a",
                "96k",
                str(episode_path),
            ],
            check=True,
        )

    duration_seconds = enforce_duration_limit(episode_path)
    file_size = episode_path.stat().st_size

    title = f"Daily News — {date_slug}"
    description = f"Concise daily news briefing for {date_slug}."
    asset_url = (
        f"https://github.com/{REPOSITORY}/releases/download/"
        f"{RELEASE_TAG}/{episode_filename}"
    )

    current_episode = {
        "date": date_slug,
        "title": title,
        "description": description,
        "pub_date": format_datetime(now),
        "guid": f"daily-news-{date_slug}",
        "url": asset_url,
        "length": file_size,
        "duration": format_duration(duration_seconds),
        "filename": episode_filename,
    }

    history = [
        episode
        for episode in load_history()
        if isinstance(episode, dict) and episode.get("date") != date_slug
    ]
    history.append(current_episode)
    history.sort(key=lambda episode: str(episode.get("date", "")), reverse=True)
    history = history[:EPISODES_TO_KEEP]

    HISTORY_FILE.write_text(
        json.dumps(
            {
                "version": 1,
                "episodes": history,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (DOCS_DIR / "feed.xml").write_text(
        build_feed(history),
        encoding="utf-8",
    )

    print(f"Narration words: {word_count}")
    print(f"Episode duration: {duration_seconds} seconds")
    print(f"Generated: {episode_path.relative_to(ROOT)}")
    print(f"Updated: {HISTORY_FILE.relative_to(ROOT)}")
    print(f"Updated: {(DOCS_DIR / 'feed.xml').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
