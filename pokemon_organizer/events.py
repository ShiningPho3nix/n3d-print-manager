from dataclasses import dataclass
from typing import Callable, Literal

EventKind = Literal[
    "header",
    "separator",
    "info",
    "file",
    "detail",
    "moved",
    "unsorted",
    "skipped",
    "extracted",
    "warning",
    "error",
    "summary",
]


@dataclass(frozen=True)
class Event:
    kind: EventKind
    message: str
    verbose: bool = False


EventSink = Callable[[Event], None]


def null_sink(event: Event) -> None:
    return None


def console_sink(event: Event) -> None:
    print(event.message, flush=True)
