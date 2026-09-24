import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .classifier import Classification, classify_name
from .config import (
    DESIGNS_DIR,
    SOURCE_DIR,
    UNSORTED_3MF,
    UNSORTED_OTHER,
    is_protected_root_entry,
)
from .dex import load_dex
from .events import Event, EventSink, null_sink
from .paths import runtime_base_dir

SEPARATOR = "━" * 52


@dataclass
class OrganizeSummary:
    organized: int = 0
    unsorted_3mf: int = 0
    unsorted_other: int = 0
    errors: int = 0
    skipped_archives: list[str] = field(default_factory=list)


def collect_input_files(base_dir: Path) -> list[Path]:
    files: list[Path] = []
    source_root = base_dir / SOURCE_DIR

    if source_root.is_dir():
        files.extend(sorted(path for path in source_root.rglob("*") if path.is_file()))

    files.extend(
        sorted(
            path
            for path in base_dir.iterdir()
            if path.is_file()
            and not path.name.startswith(".")
            and not is_protected_root_entry(path.name)
        )
    )

    return files


def classify_by_parent_folders(
    base_dir: Path, file_path: Path, dex: dict[str, str]
) -> Classification | None:
    source_root = base_dir / SOURCE_DIR
    parent = file_path.parent

    while parent not in (base_dir, source_root) and parent != parent.parent:
        result = classify_name(parent.name, dex)
        if result is not None:
            return result
        parent = parent.parent

    return None


def move_file(source: Path, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    overwritten = destination.exists()

    if overwritten:
        destination.unlink()

    shutil.move(str(source), str(destination))
    return overwritten


def route_to_unsorted(base_dir: Path, file_path: Path) -> Path:
    if file_path.suffix.lower() == ".3mf":
        destination_dir = base_dir / UNSORTED_3MF
    else:
        destination_dir = base_dir / UNSORTED_OTHER
        source_root = base_dir / SOURCE_DIR

        if file_path.is_relative_to(source_root):
            relative_dir = file_path.parent.relative_to(source_root)
            if relative_dir != Path("."):
                destination_dir = destination_dir / relative_dir

    move_file(file_path, destination_dir / file_path.name)
    return destination_dir


def remove_empty_directories(root: Path) -> None:
    if not root.is_dir():
        return

    for current, _, _ in os.walk(root, topdown=False):
        current_path = Path(current)
        if current_path == root:
            continue
        if not any(current_path.iterdir()):
            current_path.rmdir()


def organize(base_dir: Path | None = None, emit: EventSink = null_sink) -> OrganizeSummary:
    base_dir = base_dir or runtime_base_dir()
    dex = load_dex()
    summary = OrganizeSummary()

    emit(Event("header", "=== Pokemon 3D Files Organizer (Database-driven) ==="))

    input_files = collect_input_files(base_dir)

    if not input_files:
        emit(Event("info", "✓ No files found to organize."))
        return summary

    emit(Event("info", f"Found {len(input_files)} file(s) to organize:"))
    (base_dir / DESIGNS_DIR).mkdir(parents=True, exist_ok=True)

    for file_path in input_files:
        display_path = file_path.relative_to(base_dir).as_posix()
        emit(Event("separator", SEPARATOR))
        emit(Event("file", f"Processing: {display_path}"))

        if file_path.suffix.lower() == ".zip":
            emit(Event("skipped", "  ⏭️  Archive, left for the extraction step"))
            summary.skipped_archives.append(display_path)
            continue

        classification = classify_name(file_path.name, dex)

        if classification is None:
            classification = classify_by_parent_folders(base_dir, file_path, dex)
            if classification is not None:
                emit(Event("detail", "  ↳ Classified by parent folder"))

        try:
            if classification is None:
                destination_dir = route_to_unsorted(base_dir, file_path)
                relative_destination = destination_dir.relative_to(base_dir).as_posix()
                emit(
                    Event(
                        "unsorted",
                        f"  ⚠️  Could not classify, moved to: {relative_destination}/",
                    )
                )

                if file_path.suffix.lower() == ".3mf":
                    summary.unsorted_3mf += 1
                else:
                    summary.unsorted_other += 1
                continue

            needs_review = (
                classification.kind == "unmatched"
                or classification.misspelling is not None
                or classification.resolved_by_name
            )
            emit(
                Event(
                    "warning" if needs_review else "detail",
                    f"  {classification.note}",
                    verbose=classification.kind == "base" and not needs_review,
                )
            )

            target_folder = (base_dir / DESIGNS_DIR).joinpath(*classification.parts)
            overwritten = move_file(file_path, target_folder / file_path.name)
            relative_target = target_folder.relative_to(base_dir).as_posix()

            if overwritten:
                emit(
                    Event("moved", f"  ✅ Moved to: {relative_target}/ (overwrote existing file)")
                )
            else:
                emit(Event("moved", f"  ✅ Moved to: {relative_target}/"))

            summary.organized += 1

        except OSError as error:
            summary.errors += 1
            emit(Event("error", f"  ❌ Failed to move '{display_path}': {error}"))

    remove_empty_directories(base_dir / SOURCE_DIR)
    emit_summary(summary, emit)
    return summary


def emit_summary(summary: OrganizeSummary, emit: EventSink) -> None:
    emit(Event("separator", SEPARATOR))
    emit(Event("summary", f"✅ Organization complete! Organized {summary.organized} file(s)."))

    if summary.unsorted_3mf:
        emit(
            Event(
                "warning",
                f"⚠️  {summary.unsorted_3mf} unassignable .3mf file(s) moved to {UNSORTED_3MF}/",
            )
        )

    if summary.unsorted_other:
        emit(
            Event(
                "warning",
                f"⚠️  {summary.unsorted_other} other file(s) moved to {UNSORTED_OTHER}/",
            )
        )

    if summary.errors:
        emit(Event("error", f"❌ {summary.errors} file(s) could not be moved."))

    if summary.skipped_archives:
        emit(
            Event(
                "skipped",
                f"⏭️  {len(summary.skipped_archives)} archive(s) skipped, "
                "run 'python -m pokemon_organizer' to unpack them:",
            )
        )
        for skipped in summary.skipped_archives:
            emit(Event("skipped", f"  • {skipped}"))
