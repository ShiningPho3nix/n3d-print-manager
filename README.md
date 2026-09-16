# Pokemon 3D Print Organizer

Sorts Pokemon 3D print files into `Designs/{dex#} - {name}/[variant]/` and
tracks which ones you have printed. Drop archives into `Source/`, click one
button, done.

## Requirements

- Windows 10/11
- Git Bash (runs the shell scripts, ships with `unzip`)
- Python 3 with tkinter (standard library, for the GUI)

No further dependencies.

## Usage

1. Drop ZIP archives or loose files into `Source/`
2. Double click `Start Pokemon Tracker.bat`
3. Click **Organize Files**: archives are extracted, files sorted, extracted
   archives deleted
4. Tick finished Pokemon, the status is saved automatically
5. Use the folder buttons to open any entry in Explorer

Command line alternative:

```bash
./extract-and-organize.sh              # extract archives, then sort
./organize-pokemon.sh                  # sort only
KEEP_ZIPS=1 ./extract-and-organize.sh  # keep archives after extraction
```

Both scripts can be started from any working directory.

## Result

```
Designs/
├── 0006 - Charizard/
│   ├── 0006 - Charizard - AMS Profile.3mf      ← base form
│   └── Mega Charizard X/                       ← variant
├── 0025 - Pikachu/
│   └── Female/
└── Pokeballs/
    └── Great Ball/

_Unsorted/
├── 3mf/                    ← .3mf without a valid dex number
└── other/{zip-name}/       ← any other format, archive path preserved
```

Nothing is ever deleted except successfully extracted archives. Files that
cannot be classified land in `_Unsorted/`, which the GUI does not show.

## How Files Are Classified

Every file goes through four stages, first match wins:

1. **File name**: dex number → database lookup → base name and variant
2. **Parent folder**: first folder name towards `Source/` that resolves
3. Unresolved `.3mf` → `_Unsorted/3mf/`
4. Unresolved other format → `_Unsorted/other/{archive}/{original path}/`

| Input | Output |
|-------|--------|
| `0282 - Gardivoir - AMS.3mf` (typo) | `Designs/0282 - Gardevoir/` |
| `0006 - Mega Charizard X - AMS.3mf` | `Designs/0006 - Charizard/Mega Charizard X/` |
| `0001 - Bulbasaur - Christmas - AMS.3mf` | `Designs/0001 - Bulbasaur/Christmas/` |
| `Great Ball - AMS.3mf` | `Designs/Pokeballs/Great Ball/` |
| `preview.png` inside `0001 - Bulbasaur/` | `Designs/0001 - Bulbasaur/` |
| `mystery.3mf` | `_Unsorted/3mf/` |

Supported variants: Mega, Alolan, Galarian, Hisuian, Paldean and custom
keywords such as Christmas, Female, Male. URL encoded names
(`0025+-+Pikachu.3mf`) and nested archives (up to 5 levels) are handled.

## Customizing

- **New Pokemon**: add `"1026": "Name"` to `pokemon-dex.json`
- **New variant keyword**: extend `custom_variant_keywords` in `organize-pokemon.sh`
- **Exclude a file from sorting**: add it to `PROTECTED_ROOT_ENTRIES` in `organizer-config.sh`

## Troubleshooting

- **`$'\r': command not found`**: the script has CRLF line endings. Re-checkout,
  `.gitattributes` pins LF.
- **GUI is empty**: sorted files must live in `Designs/`, not next to the scripts.
- **A file is missing**: check `_Unsorted/`. With identical names the last file
  processed wins, the live output warns about it.
- **Archive not extracted**: it is kept on failure, see the organize window for
  the error.

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for the
full text. In short: use it, modify it and redistribute it, commercially or
not, as long as the copyright notice stays with the copies.

## Disclaimer

The MIT License covers the code in this repository only. It does not cover:

- **Pokemon names, characters and imagery.** Pokemon is a registered trademark
  of Nintendo, Creatures Inc. and GAME FREAK Inc. This project is not
  affiliated with, endorsed by or sponsored by any of them. Pokemon names are
  used solely to identify and sort files.
- **The 3D model files themselves.** They belong to their respective creators
  and are covered by whatever terms those creators set. No model files are
  included in this repository.
