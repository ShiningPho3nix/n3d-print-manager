#!/bin/bash

SOURCE_DIR="Source"
DESIGNS_DIR="Designs"
POKEBALLS_FOLDER="Pokeballs"
DEX_DATABASE="pokemon-dex.json"

PROTECTED_ROOT_ENTRIES=(
    ".gitattributes"
    ".gitignore"
    "CLAUDE.md"
    "CONTEXT.md"
    "README.md"
    "Start Pokemon Tracker.bat"
    "extract-and-organize.sh"
    "organize-pokemon.sh"
    "organizer-config.sh"
    "pokemon-dex.json"
    "pokemon-status-tracker.pyw"
    "pokemon-status.json"
    "n3d-designs-2026-09-13.zip"
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
