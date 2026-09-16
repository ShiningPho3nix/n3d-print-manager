from pathlib import Path

from .events import Event, EventSink, null_sink
from .extractor import SEPARATOR, ExtractSummary, extract_all
from .organizer import OrganizeSummary, organize
from .paths import runtime_base_dir


def run_all(
    base_dir: Path | None = None,
    keep_zips: bool = False,
    emit: EventSink = null_sink,
) -> tuple[ExtractSummary, OrganizeSummary]:
    base_dir = base_dir or runtime_base_dir()

    emit(Event("header", "=== Pokemon ZIP Extractor & Organizer ==="))
    extract_summary = extract_all(base_dir, keep_zips, emit)

    emit(Event("separator", SEPARATOR))
    emit(Event("header", "🗂️  Organizing files..."))
    organize_summary = organize(base_dir, emit)

    return extract_summary, organize_summary
