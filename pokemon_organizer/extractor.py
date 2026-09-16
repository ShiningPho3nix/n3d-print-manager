import os
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .config import MAX_ZIP_DEPTH, PROJECT_ROOT, SOURCE_DIR, is_protected_root_entry
from .events import Event, EventSink, null_sink

SEPARATOR = "━" * 52

KEEP_ZIPS_TRUE_VALUES = {"1", "true", "yes"}
KEEP_ZIPS_FALSE_VALUES = {"0", "false", "no"}


@dataclass
class ExtractSummary:
    extracted: int = 0
    failed: int = 0
    deleted: int = 0
    kept: int = 0


def parse_keep_zips(value: str) -> bool:
    normalized = value.strip().lower()

    if normalized in KEEP_ZIPS_TRUE_VALUES:
        return True
    if normalized in KEEP_ZIPS_FALSE_VALUES:
        return False

    raise ValueError(
        f"Invalid KEEP_ZIPS value: '{value}' (expected 0/1, false/true, no/yes)"
    )


def is_zip_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".zip"


def reserve_directory(candidate: Path, separator: str) -> Path:
    target = candidate
    counter = 0

    while target.exists():
        counter += 1
        target = candidate.with_name(f"{candidate.name}{separator}{counter}")

    return target


def extract_zip(archive: Path, destination: Path) -> str | None:
    try:
        destination.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(destination)
    except (zipfile.BadZipFile, OSError, RuntimeError) as error:
        shutil.rmtree(destination, ignore_errors=True)
        return str(error) or error.__class__.__name__

    return None


def expand_nested_zips(root: Path, emit: EventSink) -> None:
    failed: set[Path] = set()
    depth = 0

    while depth < MAX_ZIP_DEPTH:
        pending = [
            path
            for path in sorted(root.rglob("*"))
            if is_zip_file(path) and path not in failed
        ]

        if not pending:
            break

        for archive in pending:
            target = reserve_directory(archive.with_suffix(""), "__")
            error = extract_zip(archive, target)

            if error is None:
                archive.unlink(missing_ok=True)
                emit(Event("extracted", f"  ✅ Unpacked nested ZIP: {archive.name}"))
            else:
                failed.add(archive)
                emit(
                    Event("warning", f"  ⚠️  Could not unpack nested ZIP: {archive.name} ({error})")
                )

        depth += 1

    if depth >= MAX_ZIP_DEPTH and any(is_zip_file(path) for path in root.rglob("*")):
        emit(
            Event(
                "warning",
                f"  ⚠️  Maximum ZIP depth ({MAX_ZIP_DEPTH}) reached, remaining ZIPs stay packed",
            )
        )


def collect_zip_files(base_dir: Path, emit: EventSink) -> list[Path]:
    archives: list[Path] = []
    source_root = base_dir / SOURCE_DIR

    if source_root.is_dir():
        archives.extend(sorted(path for path in source_root.rglob("*") if is_zip_file(path)))

    for path in sorted(base_dir.iterdir()):
        if not is_zip_file(path) or path.name.startswith("."):
            continue

        if is_protected_root_entry(path.name):
            emit(Event("skipped", f"Skipping protected archive: {path.name}"))
            continue

        archives.append(path)

    return archives


def extract_all(
    base_dir: Path | None = None,
    keep_zips: bool = False,
    emit: EventSink = null_sink,
) -> ExtractSummary:
    base_dir = base_dir or PROJECT_ROOT
    source_root = base_dir / SOURCE_DIR
    source_root.mkdir(parents=True, exist_ok=True)

    summary = ExtractSummary()
    archives = collect_zip_files(base_dir, emit)

    if not archives:
        emit(Event("info", "No ZIP files found, skipping extraction."))
        return summary

    emit(Event("info", f"Found {len(archives)} ZIP file(s) to extract:"))
    temporary_dir = source_root / f".extract_tmp_{os.getpid()}"

    for archive in archives:
        display_path = archive.relative_to(base_dir).as_posix()
        emit(Event("separator", SEPARATOR))
        emit(Event("info", f"Extracting: {display_path}"))

        shutil.rmtree(temporary_dir, ignore_errors=True)
        error = extract_zip(archive, temporary_dir)

        if error is not None:
            emit(Event("error", f"  ❌ Failed to extract, archive kept: {display_path} ({error})"))
            summary.failed += 1
            continue

        target_dir = reserve_directory(source_root / archive.stem, "_")
        shutil.move(str(temporary_dir), str(target_dir))

        emit(
            Event(
                "extracted",
                f"  ✅ Extracted to: {target_dir.relative_to(base_dir).as_posix()}/",
            )
        )
        expand_nested_zips(target_dir, emit)
        summary.extracted += 1

        if keep_zips:
            emit(Event("info", f"  📌 KEEP_ZIPS is active, archive kept: {display_path}"))
            summary.kept += 1
            continue

        try:
            archive.unlink()
        except OSError as unlink_error:
            emit(Event("error", f"  ❌ Failed to delete archive: {display_path} ({unlink_error})"))
            continue

        emit(Event("info", f"  🗑️  Deleted archive: {display_path}"))
        summary.deleted += 1

    emit(Event("separator", SEPARATOR))

    if keep_zips:
        emit(
            Event(
                "summary",
                f"Extraction complete: {summary.extracted} successful, "
                f"{summary.failed} failed, {summary.kept} archive(s) kept",
            )
        )
    else:
        emit(
            Event(
                "summary",
                f"Extraction complete: {summary.extracted} successful, "
                f"{summary.failed} failed, {summary.deleted} archive(s) deleted",
            )
        )

    return summary
