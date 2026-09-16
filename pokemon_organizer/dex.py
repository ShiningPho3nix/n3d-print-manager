import json
from functools import lru_cache
from pathlib import Path

from .config import DEX_DATABASE, PROJECT_ROOT


class DexDatabaseError(RuntimeError):
    pass


@lru_cache(maxsize=None)
def load_dex(base_dir: Path | None = None) -> dict[str, str]:
    database_path = (base_dir or PROJECT_ROOT) / DEX_DATABASE

    if not database_path.is_file():
        raise DexDatabaseError(f"{DEX_DATABASE} not found in {database_path.parent}")

    try:
        raw = json.loads(database_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise DexDatabaseError(f"Failed to read {database_path}: {error}") from error

    if not isinstance(raw, dict) or not raw:
        raise DexDatabaseError(f"{database_path} does not contain a non-empty object")

    for dex_number, name in raw.items():
        if not isinstance(name, str) or not name.strip():
            raise DexDatabaseError(f"Entry '{dex_number}' has no usable name")
        if not (len(dex_number) == 4 and dex_number.isdigit()):
            raise DexDatabaseError(f"Entry '{dex_number}' is not a 4 digit dex number")

    return raw
