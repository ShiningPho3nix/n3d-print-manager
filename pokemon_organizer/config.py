from .paths import PROJECT_ROOT, executable_name

SOURCE_DIR = "Source"
DESIGNS_DIR = "Designs"
UNSORTED_DIR = "_Unsorted"
UNSORTED_3MF = f"{UNSORTED_DIR}/3mf"
UNSORTED_OTHER = f"{UNSORTED_DIR}/other"
POKEBALLS_FOLDER = "Pokeballs"
DEX_DATABASE = "pokemon-dex.json"
MAX_ZIP_DEPTH = 5

PROTECTED_ROOT_ENTRIES = frozenset(
    {
        ".gitattributes",
        ".gitignore",
        "CLAUDE.md",
        "CONTEXT.md",
        "LICENSE",
        "README.md",
        "Start Pokemon Tracker.bat",
        "pokemon-dex.json",
        "pokemon-status-tracker.pyw",
        "pokemon-status.json",
    }
)


def is_protected_root_entry(name: str) -> bool:
    return name in PROTECTED_ROOT_ENTRIES or name == executable_name()
