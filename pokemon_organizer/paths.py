import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def is_compiled() -> bool:
    return "__compiled__" in globals()


def runtime_base_dir() -> Path:
    if is_compiled():
        return Path(globals()["__compiled__"].containing_dir).resolve()
    return PROJECT_ROOT


def executable_name() -> str | None:
    if is_compiled():
        return Path(sys.argv[0]).name
    return None
