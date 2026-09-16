# Pokemon 3D Print Organizer

Sorts Pokemon 3D print files into `Designs/{dex#} - {name}/[variant]/` and
tracks which ones you have printed. Drop archives into `Source/`, click one
button, done.

## Requirements

- Python 3.10 or newer with tkinter (ships with the standard installer)

No further dependencies, standard library only. Tested on Windows 10/11.
Opening folders from the GUI currently requires Windows Explorer.

## Usage

1. Drop ZIP archives or loose files into `Source/`
2. Double click `Start Pokemon Tracker.bat` or run `python pokemon-status-tracker.pyw`
3. Click **Organize Files**: archives are extracted, files sorted, extracted
   archives deleted
4. Tick finished Pokemon, the status is saved automatically
5. Use the folder buttons to open any entry in Explorer

Command line alternative:

```bash
python -m pokemon_organizer                  # extract archives, then sort
python -m pokemon_organizer --organize-only  # sort only
python -m pokemon_organizer --keep-zips      # keep archives after extraction
python -m pokemon_organizer --base-dir PATH  # use another folder's Source/ and Designs/
```

Run it from the project folder so the package can be imported. Sorting targets
the project folder's `Designs/` unless `--base-dir` says otherwise. The command
exits with `1` when a file could not be moved or an archive could not be
unpacked.

```bash
python -m unittest discover -s tests -t .    # run the tests
```

## Result

```
Designs/
├── 0006 - Charizard/
│   ├── 0006 - Charizard - AMS Profile.3mf              ← base form
│   └── Mega Charizard X/                               ← variant
│       └── 0006 - Mega Charizard X - AMS - V2.3mf
├── 0025 - Pikachu/
│   ├── 0025+-+Pikachu+-+AMS+Profile+-+V3.3mf           ← base form
│   ├── 0025+-+Pikachu+-+SPLIT+Profile+-+V3.3mf
│   └── Female/                                         ← variant
│       ├── #0025+-+Female+Pikachu+-+AMS+Profile.3mf
│       └── #0025+-+Female+Pikachu+-+SPLIT+Profile.3mf
└── Pokeballs/
    └── Great Ball/
        ├── Great+Ball+-+AMS+Profile.3mf
        └── Great+Ball+-+SPLIT+Profile.3mf

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

Supported variants: Mega, Gmax, Gigantamax, Alolan, Galarian, Hisuian, Paldean
and custom keywords such as Christmas, Female, Male. URL encoded names
(`0025+-+Pikachu.3mf`) and nested archives (up to 5 levels) are handled.

## Customizing

- **New Pokemon**: add `"1026": "Name"` to `pokemon-dex.json`
- **New variant keyword**: extend `CUSTOM_VARIANT_PATTERN` in `pokemon_organizer/classifier.py`
- **Exclude a file from sorting**: add it to `PROTECTED_ROOT_ENTRIES` in `pokemon_organizer/config.py`

## Troubleshooting

- **`ModuleNotFoundError: pokemon_organizer`**: run the command from the project
  folder, the package sits next to `pokemon-status-tracker.pyw`.
- **GUI is empty**: sorted files must live in `Designs/`, not next to the code.
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
