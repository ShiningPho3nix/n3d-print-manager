#!/bin/bash

SOURCE_DIR="Source"
DESIGNS_DIR="Designs"
UNSORTED_DIR="_Unsorted"
UNSORTED_3MF="${UNSORTED_DIR}/3mf"
UNSORTED_OTHER="${UNSORTED_DIR}/other"
POKEBALLS_FOLDER="Pokeballs"
DEX_DATABASE="pokemon-dex.json"
MAX_ZIP_DEPTH=5

PROTECTED_ROOT_ENTRIES=(
    ".gitattributes"
    ".gitignore"
    "CLAUDE.md"
    "CONTEXT.md"
    "LICENSE"
    "README.md"
    "Start Pokemon Tracker.bat"
    "extract-and-organize.sh"
    "organize-pokemon.sh"
    "organizer-config.sh"
    "pokemon-dex.json"
    "pokemon-status-tracker.pyw"
    "pokemon-status.json"
)

is_protected_root_entry() {
    local candidate="$1"
    local entry
    for entry in "${PROTECTED_ROOT_ENTRIES[@]}"; do
        if [ "$candidate" = "$entry" ]; then
            return 0
        fi
    done
    return 1
}
