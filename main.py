from __future__ import annotations

import argparse
from pathlib import Path

from app.analyzer import TextAnalyzer
from app.report import print_report


def main() -> None:

    parser = argparse.ArgumentParser(
        description="Analyze the linguistic characteristics of a text."
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to a UTF-8 text file.",
    )

    args = parser.parse_args()

    if not args.file.exists():
        raise FileNotFoundError(
            f"File not found: {args.file}"
        )

    text = args.file.read_text(
        encoding="utf-8"
    )

    if not text.strip():
        raise ValueError(
            "The input file is empty."
        )

    analyzer = TextAnalyzer()

    try:
        result = analyzer.analyze(text)
        print_report(result)
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()