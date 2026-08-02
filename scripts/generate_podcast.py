from __future__ import annotations

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

REPOSITORY = "fatpotato333/news"
SITE_URL = "https://fatpotato333.github.io/news"
RELEASE_TAG = "daily-podcast"

MODEL = "gpt-4o-mini-tts"
VOICE = os.getenv("OPENAI_TTS_VOICE", "cedar")

# gpt-4o-mini-tts supports at most 2,000 input tokens per request.
# Keeping chunks below 5,500 characters provides a practical safety margin.
MAX_CHARS_PER_CHUNK = 5500


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


def format_duration(total_seconds: int) -> str:
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_FILE}")

    narration = INPUT_FILE.read_text(encoding="utf-8").strip()

    if len(narration) < 50:
        raise ValueError("Narration is unexpectedly short.")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not available.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now(ZoneInfo("Europe/Prague"))
    date_slug = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y%m%dT%H%M%S%z")

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
                    "Read as one calm, natural American-English news presenter. "
                    "Use realistic pacing, clear pronunciation and subtle emphasis. "
                    "Pause naturally between stories. Do not sound robotic, theatrical, "
                    "promotional or excessively enthusiastic. "
                    "Read only the supplied text."
                ),
                response_format="wav",
            ) as response:
                response.stream_to_file(segment_path)

            segment_paths.append(segment_path)

        concat_file = temp_path / "segments.txt"
        concat_file.write_text(
            "\n".join(
                f"file '{segment.as_posix()}'"
                for segment in segment_paths
            ),
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

    duration_seconds = int(
        round(
            float(
                subprocess.check_output(
                    [
                        "ffprobe",
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=noprint_wrappers=1:nokey=1",
                        str(episode_path),
                    ],
                    text=True,
                ).strip()
            )
        )
    )

    title = f"Daily News — {date_slug}"

    description = (
        "Martin's daily intelligence briefing, narrated using "
        "an AI-generated voice."
    )

    asset_url = (
        f"https://github.com/{REPOSITORY}/releases/download/"
        f"{RELEASE_TAG}/{episode_filename}"
    )

    file_size = episode_path.stat().st_size

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>Martin's Daily News</title>
    <link>{SITE_URL}/</link>
    <description>{description}</description>
    <language>en-us</language>
    <atom:link
      href="{SITE_URL}/feed.xml"
      rel="self"
      type="application/rss+xml" />
    <itunes:author>Martin</itunes:author>
    <itunes:explicit>false</itunes:explicit>

    <item>
      <title>{title}</title>
      <description>{description}</description>
      <pubDate>{format_datetime(now)}</pubDate>
      <guid isPermaLink="false">daily-news-{timestamp}</guid>
      <enclosure
        url="{asset_url}"
        length="{file_size}"
        type="audio/mpeg" />
      <itunes:duration>{format_duration(duration_seconds)}</itunes:duration>
    </item>
  </channel>
</rss>
"""

    feed_path = DOCS_DIR / "feed.xml"
    feed_path.write_text(feed, encoding="utf-8")

    print(f"Generated: {episode_path.relative_to(ROOT)}")
    print(f"Generated: {feed_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()