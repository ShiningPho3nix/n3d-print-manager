# CONTEXT.md - Glossary

## Pokemon-Specific Terms

### Dex Number
- **Definition**: Unique number of a Pokemon in the National Pokedex
- **Format**: 4-digit number with leading zeros (e.g. `0001`, `0025`, `0384`)
- **Examples**:
  - 0001 = Bulbasaur
  - 0025 = Pikachu
  - 0006 = Charizard
- **Usage**: Primary identifier for sorting and organization

### Pokemon Forms and Variants

#### Base Form
- **Definition**: Standard appearance of a Pokemon without any special variant
- **Example**: Regular Pikachu, regular Charizard
- **Location**: Directly inside the main folder `Designs/{dex#} - {name}/`

#### Mega Evolution
- **Definition**: Temporary battle transformation in the Pokemon games
- **Examples**:
  - Mega Charizard X (Fire/Dragon)
  - Mega Charizard Y (Fire/Flying)
  - Mega Alakazam
  - Mega Lucario
- **Folder structure**: `Designs/{dex#} - {base_name}/Mega {pokemon_name}/`
- **Note**: Keeps the dex number of the base form

#### Regional Forms
- **Definition**: Local variants from different regions
- **Types**:
  - **Alolan**: From the Alola region (Gen 7)
  - **Galarian**: From the Galar region (Gen 8)
  - **Hisuian**: From the Hisui region (Legends: Arceus)
  - **Paldean**: From the Paldea region (Gen 9)
- **Example**: Alolan Ninetales (Ice/Fairy instead of Fire)
- **Folder structure**: `Designs/{dex#} - {base_name}/Alolan/`

#### Custom Variants
- **Definition**: Unofficial modifications or designs
- **Examples**:
  - Christmas Bulbasaur (Christmas theme)
  - Female Pikachu (gender specific)
  - NO SPOONS Alakazam (without spoons)
  - Open Pokeball (opened state)
- **Folder structure**: `Designs/{dex#} - {name}/{variant_name}/`

## 3D Printing Terms

### .3mf File
- **Definition**: 3D Manufacturing Format - file format for 3D print models
- **Standard**: Developed by the 3MF Consortium
- **Advantages**:
  - Compact (ZIP based)
  - Contains metadata, colors, textures
  - Better than STL for modern 3D printers
- **Usage**: Main format for Pokemon 3D print files

### Profiles

#### AMS Profile
- **Definition**: Automated Material System - multi-filament printing
- **Manufacturer**: Bambu Lab
- **Usage**: Automatic color changes during the print
- **Example**: `0025 - Pikachu - AMS Profile - V3.3mf`

#### SPLIT Profile
- **Definition**: Model split into multiple parts
- **Purpose**:
  - Printing without support material
  - Separate coloring
  - Larger models on small print beds
- **Example**: `0025 - Pikachu - SPLIT Profile - V3.3mf`

#### MC Profile (Multi-Color)
- **Definition**: Multi-color printing with manual color changes
- **Usage**: For printers without AMS
- **Example**: `0146 - Moltres - MC Profile - V1.1.3mf`

### Versions
- **Format**: `V{major}.{minor}` or `V{major}`
- **Examples**: `V1`, `V2.1`, `V3.3mf`
- **Meaning**: Version number of the 3D model

## Pokeballs

### Definition
- **In the Pokemon universe**: Devices for catching and storing Pokemon
- **As 3D models**: Separate category of print files

### Types
- **Poke Ball**: Standard ball (red/white)
- **Great Ball**: Improved version (blue)
- **Ultra Ball**: Even stronger (yellow/black)
- **Master Ball**: Catches any Pokemon guaranteed (purple)
- **Special balls**: Timer Ball, Dusk Ball, Quick Ball, etc.

### Folder Structure
```
Designs/Pokeballs/
├── Great Ball/
│   ├── Great Ball - AMS Profile.3mf
│   └── Great Ball - SPLIT Profile.3mf
├── Master Ball/
└── Ultra Ball/
```

## Directory Roles

### Source Directory
- **Definition**: Drop zone for everything that has not been sorted yet
- **Accepts**: ZIP archives and loose files of any format
- **Scanning**: Recursive, including nested folders from extracted archives
- **After sorting**: Successfully classified files are gone, empty folders are removed
- **Configured in**: `organizer-config.sh` as `SOURCE_DIR`

### Designs Directory
- **Definition**: Target root for all sorted design files
- **Contains**: Pokemon folders and the `Pokeballs/` folder
- **Never scanned as input**: The root scan is top level only, so it can never
  descend into already sorted files
- **Configured in**: `organizer-config.sh` as `DESIGNS_DIR`

### Project Root as Input
- **Definition**: Loose files dropped next to the scripts are picked up as well
- **Scanning**: Top level only, never recursive
- **Protection**: Project files are excluded via `PROTECTED_ROOT_ENTRIES`

### Protected Root Entries
- **Definition**: Explicit list of files in the project root that are never
  treated as input
- **Why it is needed**: Since the file filter is format agnostic, without this
  list the tooling would try to sort its own scripts and documentation
- **Contents**: Scripts, documentation, `pokemon-dex.json`, `pokemon-status.json`
  and archives that are intentionally excluded
- **Configured in**: `organizer-config.sh`

## Technical Terms

### Normalization
- **Definition**: Converting file names into a uniform format
- **Steps**:
  - `+` → space
  - Remove leading `#`
  - Resolve URL encoding
  - Strip the file extension
- **Example**: `#0025+-+Pikachu` → `0025 - Pikachu`

### Variant Detection
- **Method**: Pattern matching against known keywords
- **Keywords**: Mega, Alolan, Female, Christmas, etc.
- **Fallback**: Used when the name does not contain the base name

### Base Name Extraction
- **Source**: `pokemon-dex.json` database
- **Usage**: Correct folder naming despite typos
- **Example**:
  - File: `0282 - Gardivoir - AMS.3mf` (typo)
  - Database: 0282 = "Gardevoir"
  - Folder: `Designs/0282 - Gardevoir/`

### Parent Folder Fallback
- **Definition**: Second classification stage for files whose own name carries
  no dex number
- **Why it exists**: Bulk archives may contain arbitrary file formats, for
  example `preview.png` or `supports.stl`, that only make sense in the context
  of their folder
- **Method**: Walk up from the file towards `Source/` and classify the first
  parent folder name that resolves
- **Example**:
  - File: `Source/batch/0448 - Mega Lucario Z/preview.png`
  - Folder resolves to: `0448 - Lucario` with variant `Mega Lucario Z`
  - Target: `Designs/0448 - Lucario/Mega Lucario Z/`

### Unresolved Files
- **Definition**: Files that neither their own name nor any parent folder can
  classify
- **Behavior**: They stay exactly where they are, nothing is guessed
- **Reporting**: Listed individually at the end of the organize run

### Filter Patterns
- **Skip patterns**: Lines that are NOT shown in the GUI
  - `✓ Base form`
- **Keep patterns**: Lines that ARE shown
  - `Processing:`, `Extracting`, `Extraction`, `Organizing`, `Found`
  - `✅ Moved to:`, `❌`, `⚠️`, `🗑️`
  - `🎱` Pokeball, `🎨` variant
  - `↳` parent folder fallback, `•` unresolved file

## File Name Conventions

### Standard Format
```
{dex#} - {pokemon_name} - {profile} - {version}.3mf
```
**Example**: `0025 - Pikachu - AMS Profile - V3.3mf`

### URL Encoded Format
```
{dex#}+-+{pokemon_name}+-+{profile}.3mf
```
**Example**: `0025+-+Pikachu+-+AMS+Profile.3mf`

### Variant Format
```
{dex#} - {variant} {pokemon_name} - {profile}.3mf
```
**Example**: `0006 - Mega Charizard X - AMS - V2.3mf`

### Pokeball Format
```
{ball_name} - {profile}.3mf
```
**Example**: `Great Ball - AMS Profile.3mf`

### Arbitrary Formats
```
any file name inside a classifiable folder
```
**Example**: `preview.png` inside `0001 - Bulbasaur/`

## Status Tracking

### pokemon-status.json
- **Structure**: Key-value pairs
- **Key**: Path relative to `Designs/` (e.g. `"0025 - Pikachu"`,
  `"0025 - Pikachu/Female"`, `"Pokeballs/Great Ball"`)
- **Value**: Boolean (`true` = done, `false` = open)
- **Auto save**: On every checkbox change

### Progress Calculation
```
Progress = (Done items / Total items) × 100%
```

## Folder Hierarchy

### Level 1: Pokemon Main Folder
```
Designs/{dex#} - {pokemon_name}/
```

### Level 2: Variant Subfolder (optional)
```
Designs/{dex#} - {pokemon_name}/
└── {variant_name}/
```

### Special Case: Pokeballs
```
Designs/Pokeballs/
└── {ball_type}/
```

### GUI Representation
- Pokemon: Flat list (level 1)
- Variants: Indented with `↳` (level 2)
- Pokeballs: At the end behind a separator, flat with a 🎱 icon
