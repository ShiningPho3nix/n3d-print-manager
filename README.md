# Pokemon 3D Print Organizer

Automatic organization and tracking of Pokemon 3D print files, with sorting by Pokedex number and variant.

## Features

### 🗂️ Automatic Organization
- **ZIP extraction**: Unpacks downloaded archives automatically
- **Nested ZIPs**: Archives inside archives are unpacked too (up to 5 levels)
- **Any folder depth**: Files are found regardless of the archive's structure
- **Structured sorting**: Files are organized by dex number and variant
- **Database backed**: Uses a Pokemon database for correct names
- **Typo correction**: Detects and corrects typos in file names
- **Format agnostic**: Handles any file type, not just `.3mf`
- **Pokeball support**: Separate category for Pokeball models
- **Catch-all folder**: Unassignable files land in `_Unsorted/` instead of being deleted

### ✅ Status Tracking
- **GUI application**: Clear overview of all Pokemon and variants
- **Checkbox system**: Mark finished prints with one click
- **Progress display**: Live statistics on print progress
- **Auto save**: Status is stored automatically
- **Explorer integration**: Open any folder straight from the GUI

### 🔧 Variant Support
- **Mega evolutions**: Mega Charizard X/Y, Mega Alakazam, etc.
- **Regional forms**: Alolan, Galarian, Hisuian, Paldean
- **Custom variants**: Christmas, Female/Male, NO SPOONS, etc.
- **Profile types**: AMS, SPLIT, MC - all in one folder

## Installation

### Requirements
- **Windows** (tested on Windows 10/11)
- **Git Bash** (for the shell scripts)
- **Python 3.x** (for the GUI)

### Setup
1. Extract all files into one folder
2. Install Git Bash (if not present yet)
3. Install Python 3 (if not present yet)
4. Done. No further dependencies needed.

## Project Layout

```
n3d designs/
├── Source/                     ← drop zone for new archives and files
├── Designs/                    ← sorted output
│   ├── 0025 - Pikachu/
│   └── Pokeballs/
├── organize-pokemon.sh
├── extract-and-organize.sh
├── organizer-config.sh
├── pokemon-status-tracker.pyw
├── Start Pokemon Tracker.bat
├── pokemon-dex.json
└── pokemon-status.json
```

`Source/` and `Designs/` are created automatically on the first run.

## Usage

### Where to put new files

Drop ZIP archives or loose files into **`Source/`**. Dropping them into the
project root works as well, but `Source/` keeps the project tidy.

- `Source/` is scanned recursively, including nested folders from archives
- The project root is scanned **top level only**, so the scan can never
  descend into already sorted files in `Designs/`
- Project files in the root are protected by `PROTECTED_ROOT_ENTRIES` in
  `organizer-config.sh` and are never treated as input

After a run, every successfully classified file is gone from both locations.

### Option 1: GUI (recommended)
1. Double click `Start Pokemon Tracker.bat`
2. The GUI opens
3. Click **"📂 Organize Files"** to:
   - Extract archives (if any are present)
   - Sort the files
   - Delete archives that were extracted successfully
4. Tick finished Pokemon with the checkboxes
5. Use the **"📁"** buttons to open a folder in Explorer

### Option 2: Command line
```bash
# Sort only, no archive extraction
./organize-pokemon.sh

# Extract archives, then sort
./extract-and-organize.sh
```

Both scripts can be started from any working directory. They switch to their
own location on startup.

## Folder Structure

### Pokemon
```
Designs/0025 - Pikachu/
├── 0025 - Pikachu - AMS Profile - V3.3mf          ← base form
├── 0025 - Pikachu - SPLIT Profile - V3.3mf        ← base form
└── Female/                                         ← variant
    ├── 0025 - Female Pikachu - AMS Profile.3mf
    └── 0025 - Female Pikachu - SPLIT Profile.3mf
```

### Mega Evolutions
```
Designs/0006 - Charizard/
├── 0006 - Charizard - AMS Profile.3mf             ← base form
├── Mega Charizard X/                              ← mega variant
│   └── 0006 - Mega Charizard X - AMS - V2.3mf
└── Mega Charizard Y/                              ← mega variant
    ├── 0006 Mega Charizard Y - AMS - V1.3mf
    ├── 0006 Mega Charizard Y - MC - V1.1.3mf
    └── 0006 Mega Charizard Y - SPLIT - V1.3mf
```

### Pokeballs
```
Designs/Pokeballs/
├── Great Ball/
│   ├── Great Ball - AMS Profile.3mf
│   └── Great Ball - SPLIT Profile.3mf
├── Master Ball/
│   ├── Master Ball - AMS Profile - V1.3mf
│   └── Master Ball - SPLIT Profile.3mf
└── Ultra Ball/
    ├── Ultra Ball - AMS Profile - V1.1.3mf
    └── Ultra Ball - SPLIT Profile - V1.1.3mf
```

### Catch-all Folder (`_Unsorted`)
```
_Unsorted/
├── 3mf/                          ← .3mf without a valid dex number, not a Pokeball
│   └── mystery-model.3mf
└── other/                        ← every file that is not a .3mf
    └── {zip-name}/               ← kept separate per bulk download
        └── a/b/c/                ← original path from the archive is preserved
            ├── manual.pdf
            └── part.stl
```
> The catch-all folder deliberately never appears in the GUI list. The GUI scans
> `Designs/` only, and it accepts just folders starting with 4 digits, plus `Pokeballs`.

## File Handling

### Supported Name Formats
- **Standard**: `0025 - Pikachu - AMS Profile - V3.3mf`
- **URL encoded**: `0025+-+Pikachu+-+AMS+Profile.3mf`
- **Variants**: `0006 - Mega Charizard X - AMS - V2.3mf`
- **Pokeballs**: `Great Ball - AMS Profile.3mf`
- **Folder structure inside an archive**: arbitrarily deep and freely named

### Classification
Every file runs through four stages, in this order:

1. **By file name**: dex number → database lookup → base name and variant
2. **By parent folder**: if the file name carries no dex number, the script
   walks up towards `Source/` and uses the first folder name that resolves
3. **Unresolved `.3mf`** → `_Unsorted/3mf/`
4. **Unresolved other format** → `_Unsorted/other/{archive}/{original path}/`

Stages 2 to 4 are what make mixed-format archives work. A `preview.png` or
`supports.stl` has no dex number of its own, but inherits the classification of
the folder it came in. Anything that stage 2 cannot resolve either is caught by
the `_Unsorted` net rather than being deleted or left lying around.

Stage 2 only fires when a folder name genuinely resolves against the dex
database. Archives with freely named folders simply fall through, so the stage
can add matches but never misfile anything.

### Special Cases
| Input | Handling | Output |
|-------|----------|--------|
| `0282 - Gardivoir` (typo) | as base form | `Designs/0282 - Gardevoir/` |
| `0006 - Mega Charizard X` | as mega variant | `Designs/0006 - Charizard/Mega Charizard X/` |
| `Great Ball - AMS` | as Pokeball | `Designs/Pokeballs/Great Ball/` |
| `0001 - Bulbasaur - Christmas` | as custom variant | `Designs/0001 - Bulbasaur/Christmas/` |
| `preview.png` in `0001 - Bulbasaur/` | via parent folder | `Designs/0001 - Bulbasaur/` |
| `notes.txt` (no context) | left in place | reported as unresolved |

## GUI Features in Detail

### Main Window
- **Pokemon list**: Sorted by dex number
- **Checkboxes**: ☑ = done, ☐ = open
- **Variants**: Indented below their main Pokemon
- **Pokeballs**: At the end of the list with a 🎱 icon
- **Progress**: `Progress: 45/120 (37.5%)`

### Buttons
| Button | Function |
|--------|----------|
| **Refresh** | Reload the list |
| **📂 Organize Files** | Extract archives, then sort |
| **📁** (on every entry) | Open the folder in Explorer |

### Organize Window
- **Live output**: Shows progress in real time
- **Compact view**: Filters unimportant details
- **No console window**: Runs in the background
- **Close button**: Enabled once the run has finished

## Profile Types

### AMS (Automated Material System)
- **Used with**: Bambu Lab AMS
- **Benefit**: Automatic color changes
- **Best for**: Multi-color prints

### SPLIT
- **Used with**: Models split into parts
- **Benefit**: No support material needed
- **Best for**: Separate coloring

### MC (Multi-Color)
- **Used with**: Manual color changes
- **Benefit**: Printable without AMS
- **Best for**: Printers without a multi-material system

## Troubleshooting

### The GUI does not start
- Is Python installed? `python --version`
- Start it via `Start Pokemon Tracker.bat`

### A shell script does not run
- Is Git Bash installed?
- Is the script executable? `chmod +x *.sh`
- Run it with Git Bash, not CMD
- If bash reports `$'\r': command not found`, the script was checked out with
  CRLF line endings. `.gitattributes` pins them to LF, so re-checkout the file.

### The GUI is empty after an update
- Sorted files live in `Designs/` now. If your Pokemon folders still sit next
  to the scripts, move them into `Designs/`.

### Files end up in the wrong folder
- Check the dex number: the first 4 digits must be valid
- Is `pokemon-dex.json` up to date?
- Typos are corrected automatically against the database

### An archive was not extracted
- The archive is kept on failure, nothing is deleted
- Check the error message in the organize window
- Archives listed in `PROTECTED_ROOT_ENTRIES` are skipped on purpose

### A file is missing after organizing
- Check `_Unsorted/3mf/`: `.3mf` files without a valid dex number end up there
- Check `_Unsorted/other/{zip-name}/`: every non-3mf file, original path preserved
- With identical file names, the last one processed wins (warning in the live output)
- Nothing is ever deleted, except the archives themselves after a successful extraction

## Advanced Usage

### Adding new Pokemon
1. Open `pokemon-dex.json`
2. Add a new entry:
   ```json
   "1026": "NewPokemonName"
   ```
3. Save - done.

### Defining custom variants
Adjust `custom_variant_keywords` in `organize-pokemon.sh`:
```bash
custom_variant_keywords="(Christmas|Halloween|Female|Male|Shiny|Shadow|NO |Open)"
```

### Excluding a file from sorting
Add its name to `PROTECTED_ROOT_ENTRIES` in `organizer-config.sh`.

### Batch processing
Put all archives into `Source/` and run:
```bash
./extract-and-organize.sh
```
→ Every archive is extracted and sorted.

**Keeping archives (for repeated test runs):**
```bash
KEEP_ZIPS=1 ./extract-and-organize.sh
```
→ Archives are kept after processing. Accepted values are `0/1`, `false/true`,
`no/yes`. An unknown value aborts the script **before** anything is extracted.

## Technical Details

### Files
| File | Purpose |
|------|---------|
| `extract-and-organize.sh` | Archive extraction, then organization |
| `organize-pokemon.sh` | Core organization logic |
| `organizer-config.sh` | Shared folder names and protected file list |
| `pokemon-status-tracker.pyw` | GUI application |
| `Start Pokemon Tracker.bat` | GUI launcher |
| `pokemon-dex.json` | Pokemon database (1025 entries) |
| `pokemon-status.json` | Status storage (auto generated) |

### Requirements
- **Bash**: Git Bash (on Windows)
- **Python**: 3.x with tkinter (standard library)
- **Tools**: unzip (included in Git Bash)

### Performance
- **Organization**: roughly 1 second per 10 files
- **Archive extraction**: depends on archive size
- **GUI**: loads instantly below ~200 Pokemon

## Changelog

### Version 1.1
- ✅ Folder names sanitized for Windows (`Type: Null`, `Mime Jr.`)
- ✅ Whitespace trimming no longer breaks on `Farfetch'd` / `Sirfetch'd`
- ✅ Sorted output moved into `Designs/`
- ✅ `Source/` drop zone, with the project root still accepted as input
- ✅ Format-agnostic handling instead of a hard `.3mf` filter
- ✅ Parent folder fallback for files without a dex number
- ✅ Archives extracted structure preserving instead of flattened
- ✅ Bulk archives with arbitrary folder depth and free keyword structures
- ✅ Nested archives are unpacked recursively (max 5 levels)
- ✅ `_Unsorted/` catch-all instead of dropping unassignable files
- ✅ Case-insensitive extension detection (`.3MF`, `.STL`)
- ✅ Sorting now also runs when no archive is present
- ✅ Protected file list so the tooling never sorts itself
- ✅ `KEEP_ZIPS=1` keeps archives after processing (for repeated test runs)
- ✅ Line endings pinned via `.gitattributes`

### Version 1.0 (Initial Release)
- ✅ Automatic organization by dex number
- ✅ Variant support (Mega, Alolan, custom)
- ✅ Pokeball category
- ✅ Archive extraction
- ✅ GUI with status tracking
- ✅ Live output without a console window
- ✅ Typo correction
- ✅ UTF-8 encoding
- ✅ Core dump fixes

## Credits

- **Pokemon database**: Gen 1-9 (1025 Pokemon)
- **3D models**: By various creators (see the original files)
- **Organization**: Automatic via the scripts

## Support

If something does not work:
1. See the **Troubleshooting** section
2. `CONTEXT.md` for terminology
3. `CLAUDE.md` for technical details

## License

This tool is for personal use. Pokemon is a registered trademark of Nintendo / Game Freak / Creatures Inc.
