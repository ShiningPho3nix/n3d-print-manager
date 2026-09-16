# CLAUDE.md - Pokemon 3D Print Organizer

## Project Overview
This project organizes Pokemon 3D print files (.3mf) into a structured folder hierarchy based on Pokemon Dex numbers and variants. It includes scripts for extraction, organization, and a GUI for tracking completion status.

## Project Structure

### Main Scripts
1. **extract-and-organize.sh**
   - Extracts ZIP files, including nested ZIPs (max depth 5)
   - Finds .3mf files at any folder depth and moves them to root
   - Collects all non-.3mf files in `_Unsorted/other/{zip-name}/{original path}/`
   - Calls organize-pokemon.sh
   - Deletes ZIPs after successful extraction, unless `KEEP_ZIPS` is set (`1/true/yes`)
   - Invalid `KEEP_ZIPS` values abort the script before anything is extracted (fail-fast on a destructive step)

2. **organize-pokemon.sh**
   - Core organization logic
   - Uses pokemon-dex.json database for Pokemon names
   - Creates folder structure: `{dex#} - {name}/[variant]/`
   - Handles special cases: Pokeballs, Mega forms, regional variants, typos
   - Moves unassignable .3mf files to `_Unsorted/3mf/`

3. **pokemon-status-tracker.pyw**
   - GUI application for tracking completion status
   - Shows Pokemon and variants with checkboxes
   - Includes "Organize Files" button to run extract-and-organize.sh
   - Saves status to pokemon-status.json

### Data Files
- **pokemon-dex.json** - Complete Pokemon database (Gen 1-9, 1025 Pokemon)
- **pokemon-status.json** - Tracks completion status (auto-generated)

## Key Concepts

### Folder Structure
```
{dex#} - {pokemon_name}/
├── base_files.3mf          ← Base form files directly in main folder
├── Mega {pokemon_name}/    ← Mega variants in subfolders
├── Alolan/                 ← Regional variants
├── Custom Variant/         ← Custom variants (Christmas, Female, etc.)
└── ...

Pokeballs/
├── Great Ball/
├── Master Ball/
└── ...

_Unsorted/
├── 3mf/                    ← .3mf without valid dex number and not a Pokeball
└── other/{zip-name}/       ← All non-.3mf files, original archive path preserved
```
The GUI ignores `_Unsorted` automatically: `scan_and_populate()` only accepts folders whose first 4 characters are digits, plus `Pokeballs`.

### Variant Detection Logic
1. **Known Form Variants**: Mega, Alolan, Galarian, Hisuian, Paldean → Full name in subfolder
2. **Custom Variants**: Christmas, Female, Male, NO SPOONS, etc. → Subfolder
3. **Typos**: Names similar to database name but not exact → Treated as base form (no subfolder)

### File Naming Patterns
- Format 1: `{dex#} - {name} - {profile} - {version}.3mf`
- Format 2: `{dex#}+-+{name}+-+{profile}.3mf` (URL encoded)
- Pokeballs: `{ball_name} - {profile}.3mf` (no dex number)

## Important Implementation Details

### Bash String Matching
- Uses `[[ "$string" == *"$pattern"* ]]` instead of `grep -F` to avoid core dumps
- Case-insensitive matching where needed

### ZIP Extraction (two phases)
- Phase 1 `expand_nested_zips()`: iterative loop over `find -iname "*.zip"`, limited by `MAX_ZIP_DEPTH=5`
- Iterative instead of recursive, because `find` would otherwise traverse directories the recursion is creating itself
- Archives that fail to unpack are stored in `failed_zips` and skipped on the next pass to prevent endless retries
- Phase 2 `collect_files()`: sweeps every remaining file, extension compared lowercase (`${ext,,}`) so `.3MF` and `.STL` are handled correctly
- Folder names inside an archive are never evaluated: bulk downloads allow arbitrary keyword structures, only the filename carries information

### GUI Live Output
- Uses `subprocess.Popen()` instead of `subprocess.run()` for live output
- Filters verbose lines for cleaner display
- Hides bash console window with `CREATE_NO_WINDOW` flag (Windows)

### Error Handling
- Typos in filenames: Create correct folder based on dex number from database
- Missing dex numbers: Check if it's a Pokeball, otherwise move to `_Unsorted/3mf/`
- Foreign formats: Moved to `_Unsorted/other/`, never deleted
- Duplicate files: Overwrite existing files, logged with a warning

## Code Conventions

### Bash Scripts
- Use double brackets `[[ ]]` for string comparisons
- Use `xargs` for trimming whitespace
- Normalize filenames: Replace `+` with spaces, remove `#` prefix
- Filter out profile keywords: AMS, SPLIT, MC, Profile, V[0-9]

### Python GUI
- UTF-8 encoding for all text
- Filter patterns for compact output
- Auto-save status on every checkbox change
- Thread-based script execution to keep GUI responsive

## Common Issues

### Core Dumps
- Caused by `grep -F` with certain strings
- Solution: Use bash pattern matching `[[ == *..* ]]`

### Encoding Errors
- Windows console vs UTF-8 output
- Solution: Explicit UTF-8 encoding + error='replace'

### Bash Window Popup
- Subprocess opens visible console
- Solution: CREATE_NO_WINDOW + STARTUPINFO flags

## Testing Scenarios

1. **Normal Pokemon**: `0025 - Pikachu - AMS Profile.3mf` → `0025 - Pikachu/`
2. **Mega Variant**: `0006 - Mega Charizard X - AMS.3mf` → `0006 - Charizard/Mega Charizard X/`
3. **Custom Variant**: `0001 - Bulbasaur - Christmas - AMS.3mf` → `0001 - Bulbasaur/Christmas/`
4. **Typo**: `0282 - Gardivoir - AMS.3mf` → `0282 - Gardevoir/` (no subfolder)
5. **Pokeball**: `Great Ball - AMS.3mf` → `Pokeballs/Great Ball/`
6. **Deep nesting**: `a/b/c/d/e/0025 - Pikachu - AMS.3mf` → `0025 - Pikachu/`
7. **Nested ZIP**: `x/inner.zip` → unpacked, contents processed like any other file
8. **Foreign format**: `a/b/handbuch.pdf` → `_Unsorted/other/{zip-name}/a/b/handbuch.pdf`
9. **No dex number**: `mystery-model.3mf` → `_Unsorted/3mf/`

## Maintenance

### Adding New Pokemon (Future Generations)
1. Update `pokemon-dex.json` with new entries
2. No code changes needed - scripts use database automatically

### Adding New Variant Types
1. Add keyword to variant detection regex in organize-pokemon.sh
2. Consider if it needs special folder naming (like Mega forms)

## File Modifications

When modifying scripts, ensure:
- Bash scripts remain executable: `chmod +x *.sh`
- GUI maintains live output functionality
- Filter patterns stay in sync between scripts and GUI
- Database integrity (valid JSON, no duplicates)
