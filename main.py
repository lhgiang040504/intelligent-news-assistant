import argparse
import sys
from pathlib import Path

from config.settings import Settings
from src.pipeline.pipeline import NewsPipeline
from src.utils.date_utils import parse_date_arg


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Intelligent News Assistant: collect, filter, and summarize Vietnamese news."
    )
    parser.add_argument(
        "--topic",
        default="technology",
        help="Category name (e.g. technology, sports) or a custom keyword for filtering (default: technology).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Rolling window: last N days from now (default: 7). Ignored if --from/--to are set.",
    )
    parser.add_argument(
        "--from",
        dest="date_from",
        metavar="YYYY-MM-DD",
        help="Fixed range start (UTC, inclusive). Must be used with --to.",
    )
    parser.add_argument(
        "--to",
        dest="date_to",
        metavar="YYYY-MM-DD",
        help="Fixed range end (UTC, inclusive). Must be used with --from.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if (args.date_from is None) != (args.date_to is None):
        parser.error("Fixed range requires both --from and --to (YYYY-MM-DD each).")

    date_from = parse_date_arg(args.date_from) if args.date_from else None
    date_to = parse_date_arg(args.date_to) if args.date_to else None

    try:
        settings = Settings.from_inputs(
            topic=args.topic,
            days=args.days,
            date_from=date_from,
            date_to=date_to,
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        sys.exit(2)

    pipeline = NewsPipeline(settings=settings)
    report_markdown = pipeline.run()

    output_path = Path(settings.report_output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_markdown, encoding="utf-8")

    print(f"Weekly report generated: {output_path}")


if __name__ == "__main__":
    main()
