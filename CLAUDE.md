# CLAUDE.md - Pokemon 3D Print Organizer

## Project Overview
This project organizes Pokemon 3D print files into a structured folder hierarchy based on Pokemon Dex numbers and variants. It includes scripts for extraction, organization, and a GUI for tracking completion status.

## Language Policy

**Everything in this project is written in English and stays English.**

This covers code, comments, identifiers, documentation, script output, commit
messages and **GUI labels**.

This rule intentionally overrides the global instruction to write user
interface text in German. It applies to this project only.

## Project Structure

### Directories
- **Source/** - drop zone for unsorted archives and files, scanned recursively
- **Designs/** - target root for all sorted output, never scanned as input

Both are created automatically and are excluded from version control.

### Main Scripts
1. **organizer-config.sh**
   - Shared configuration sourced by both shell scripts
   - Defines SOURCE_DIR, DESIGNS_DIR and PROTECTED_ROOT_ENTRIES
   - PROTECTED_ROOT_ENTRIES is what stops the tooling from sorting its own
     files, which matters because the file filter is format agnostic

2. **extract-and-organize.sh**
   - Extracts archives found in Source/ and in the project root
   - Extracts into Source/{archive name}/ preserving the archive structure
   - Deletes an archive only after it extracted successfully
   - Always calls organize-pokemon.sh, even when no archive was found

3. **organize-pokemon.sh**
   - Core organization logic
   - Uses pokemon-dex.json database for Pokemon names
   - Creates folder structure: `Designs/{dex#} - {name}/[variant]/`
   - Handles special cases: Pokeballs, Mega forms, regional variants, typos
   - Classifies by file name first, then falls back to the parent folder name
   - Leaves unresolvable files in place and reports them

4. **pokemon-status-tracker.pyw**
   - GUI application for tracking completion status
   - Scans Designs/ and shows Pokemon and variants with checkboxes
   - Includes "Organize Files" button to run extract-and-organize.sh
   - Saves status to pokemon-status.json, keyed relative to Designs/

### Data Files
- **pokemon-dex.json** - Complete Pokemon database (Gen 1-9, 1025 Pokemon)
- **pokemon-status.json** - Tracks completion status (auto-generated)

## Key Concepts

### Folder Structure
```
Designs/{dex#} - {pokemon_name}/
├── base_files.3mf          ← Base form files directly in main folder
├── Mega {pokemon_name}/    ← Mega variants in subfolders
├── Alolan/                 ← Regional variants
├── Custom Variant/         ← Custom variants (Christmas, Female, etc.)
└── ...

Designs/Pokeballs/
├── Great Ball/
├── Master Ball/
└── ...
```

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
- Never use `xargs` to trim whitespace. It treats quotes as special and fails
  on names like `Farfetch'd`, which silently yields an empty result. Use
  `trim_whitespace()` instead.

### Path Sanitization
- `sanitize_path_component()` is applied when building a folder name, never
  before comparing names. Comparing sanitized names would break variant
  detection, because the database name and the file name would no longer match.
- Replaces `< > : " / \ | ? *` with a space, collapses repeated spaces and
  strips trailing dots and spaces.
- Affected database names: `Type: Null` (0772) becomes `Type Null`,
  `Mime Jr.` (0439) becomes `Mime Jr`, which is what Windows would store anyway.

### GUI Live Output
- Uses `subprocess.Popen()` instead of `subprocess.run()` for live output
- Filters verbose lines for cleaner display
- Hides bash console window with `CREATE_NO_WINDOW` flag (Windows)

### Error Handling
- Typos in filenames: Create correct folder based on dex number from database
- Missing dex numbers: Check if it's a Pokeball, then try the parent folder name
- Still unresolvable: Leave the file untouched and list it in the final report
- Duplicate files: Overwrite existing files
- Failed extraction: Keep the archive, remove the partial temporary folder

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

1. **Normal Pokemon**: `0025 - Pikachu - AMS Profile.3mf` → `Designs/0025 - Pikachu/`
2. **Mega Variant**: `0006 - Mega Charizard X - AMS.3mf` → `Designs/0006 - Charizard/Mega Charizard X/`
3. **Custom Variant**: `0001 - Bulbasaur - Christmas - AMS.3mf` → `Designs/0001 - Bulbasaur/Christmas/`
4. **Typo**: `0282 - Gardivoir - AMS.3mf` → `Designs/0282 - Gardevoir/` (no subfolder)
5. **Pokeball**: `Great Ball - AMS.3mf` → `Designs/Pokeballs/Great Ball/`
6. **Parent folder fallback**: `Source/batch/0001 - Bulbasaur/preview.png` → `Designs/0001 - Bulbasaur/`
7. **Unresolvable**: `Source/batch/notes.txt` → stays in place, reported at the end
8. **Protected file**: `CLAUDE.md` in the project root → never treated as input

## Maintenance

### Adding New Pokemon (Future Generations)
1. Update `pokemon-dex.json` with new entries
2. No code changes needed - scripts use database automatically

### Adding New Variant Types
1. Add the keyword to `form_variant_keywords` or `custom_variant_keywords` in
   organize-pokemon.sh
2. Consider if it needs special folder naming (like Mega forms)

### Excluding a File From Sorting
Add its name to `PROTECTED_ROOT_ENTRIES` in organizer-config.sh.

## Known Limitations

- Nested archives (a ZIP inside a ZIP) are not extracted recursively within a
  single run.
- Windows reserved device names (CON, NUL, AUX, PRN, COM1-9, LPT1-9) are not
  special cased. No Pokemon name collides with them, and every main folder is
  prefixed with its dex number, so this is theoretical.

## File Modifications

When modifying scripts, ensure:
- Bash scripts remain executable: `chmod +x *.sh`
- Shell scripts keep LF line endings (pinned in `.gitattributes`; CRLF breaks bash)
- GUI maintains live output functionality
- Filter patterns stay in sync between scripts and GUI
- Folder names stay in sync between organizer-config.sh and the DESIGNS_DIR
  constant in pokemon-status-tracker.pyw
- Database integrity (valid JSON, no duplicates)
