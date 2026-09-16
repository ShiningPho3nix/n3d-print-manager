import argparse
import os
import sys
from pathlib import Path

from .dex import DexDatabaseError
from .events import console_sink
from .extractor import parse_keep_zips
from .organizer import organize
from .paths import runtime_base_dir
from .runner import run_all


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m pokemon_organizer",
        description="Extract archives from Source/ and organize the files into Designs/",
    )
    parser.add_argument(
        "--keep-zips",
        action="store_true",
        help="keep archives after a successful extraction",
    )
    parser.add_argument(
        "--organize-only",
        action="store_true",
        help="skip extraction and only organize the files that are already present",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=runtime_base_dir(),
        help="project directory that holds Source/ and Designs/ (default: %(default)s)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if sys.stdout is not None:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    args = build_parser().parse_args(argv)

    keep_zips = args.keep_zips
    if not keep_zips and "KEEP_ZIPS" in os.environ:
        try:
            keep_zips = parse_keep_zips(os.environ["KEEP_ZIPS"])
        except ValueError as error:
            print(f"❌ {error}", file=sys.stderr)
            return 1

    try:
        if args.organize_only:
            organize_summary = organize(args.base_dir, console_sink)
            extract_failures = 0
        else:
            extract_summary, organize_summary = run_all(args.base_dir, keep_zips, console_sink)
            extract_failures = extract_summary.failed
    except DexDatabaseError as error:
        print(f"❌ {error}", file=sys.stderr)
        return 1

    return 1 if organize_summary.errors or extract_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
