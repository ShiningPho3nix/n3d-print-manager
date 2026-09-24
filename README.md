# Pokemon 3D Print Organizer

Sorts the Pokemon character ball designs from
[N3D Melbourne](https://www.n3dmelbourne.com/) into
`Designs/{dex#} - {name}/[variant]/` and tracks which ones you have printed.
Drop the downloaded archives into `Source/`, click one button, done.

The classifier is built around N3D's file naming
(`0025 - Pikachu - AMS Profile - V3.3mf`). Files from other creators are sorted
only if they follow the same pattern, everything else lands in `_Unsorted/`.

## Download

Grab the file for your system from the
[latest release](https://github.com/ShiningPho3nix/n3d-print-manager/releases/latest),
put it into an empty folder and start it. No Python installation is needed.
`Source/`, `Designs/` and `pokemon-status.json` are created next to it.

| Platform | File | First start |
|----------|------|-------------|
| Windows 10/11 (x64) | `PokemonStatusTracker-windows-x64.exe` | Windows Defender may ask for confirmation, the executable is not code signed |
| macOS (Apple Silicon) | `PokemonStatusTracker-macos-arm64.zip` | Unzip, right click the app, choose **Open**. The app is not notarized |
| Linux (x64) | `PokemonStatusTracker-linux-x64.tar.gz` | Needs a glibc at least as new as Ubuntu 24.04 and a desktop session |

Intel Macs are not supported. The executables are built by the
[release workflow](.github/workflows/release.yml) on GitHub's runners, nothing
is built on a private machine.

## Running From Source

- Python 3.10 or newer with tkinter (ships with the standard installer)

No further dependencies, standard library only. Works on Windows, macOS and
Linux, the folder buttons use the file manager of the platform.

## Usage

1. Drop ZIP archives or loose files into `Source/`
2. Start the downloaded executable, or from source double click
   `Start Pokemon Tracker.bat` or run `python pokemon-status-tracker.pyw`
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
the project folder's `Designs/` unless `--base-dir` says otherwise, the
database `pokemon-dex.json` is always read from the project folder. The command
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
│   └── Female Pikachu/                                 ← variant
│       ├── #0025+-+Female+Pikachu+-+AMS+Profile.3mf
│       └── #0025+-+Female+Pikachu+-+SPLIT+Profile.3mf
└── Pokeballs/
    └── Great Ball/
        ├── Great+Ball+-+AMS+Profile.3mf
        └── Great+Ball+-+SPLIT+Profile.3mf

_Unsorted/
├── 3mf/                    ← .3mf that resolves neither by dex number nor by name
└── other/{zip-name}/       ← any other format, archive path preserved
```

Nothing is ever deleted except successfully extracted archives. Files that
cannot be classified land in `_Unsorted/`, which the GUI does not show.

## How Files Are Classified

Every file goes through four stages, first match wins:

1. **File name**: dex number → database lookup → base name and variant.
   Without a dex number: Pokeball, then an exact, unambiguous Pokemon name
2. **Parent folder**: first folder name towards `Source/` that resolves
3. Unresolved `.3mf` → `_Unsorted/3mf/`
4. Unresolved other format → `_Unsorted/other/{archive}/{original path}/`

| Input | Output |
|-------|--------|
| `0282 - Gardivoir - AMS.3mf` (typo) | `Designs/0282 - Gardevoir/` |
| `0006 - Mega Charizard X - AMS.3mf` | `Designs/0006 - Charizard/Mega Charizard X/` |
| `0658 Ash-Greninja - SPLIT - V1.1.3mf` | `Designs/0658 - Greninja/Ash-Greninja/` |
| `0658 - Ash-Grenimja - AMS.3mf` (typo) | `Designs/0658 - Greninja/Ash-Greninja/` |
| `0001 - Bulbasaur - Christmas - AMS.3mf` | `Designs/0001 - Bulbasaur/Christmas/` |
| `0025 - Raichu - AMS.3mf` (name does not match) | `Designs/0025 - Pikachu/Raichu/` |
| `Great Ball - AMS.3mf` | `Designs/Pokeballs/Great Ball/` |
| `Rose Bulbasaur - AMS Profile.3mf` (no dex number) | `Designs/0001 - Bulbasaur/Rose Bulbasaur/` |
| `Pikachu and Eevee - AMS.3mf` (no dex number, two names) | `_Unsorted/3mf/` |
| `preview.png` inside `0001 - Bulbasaur/` | `Designs/0001 - Bulbasaur/` |
| `mystery.3mf` | `_Unsorted/3mf/` |

There is no list of variant keywords. The dex number picks the Pokemon, its
name is searched inside the file name (typos and missing accents included),
and whatever surrounds it is the variant. Text in front of the name or glued
on with a hyphen keeps the full name (`Mega Charizard X`, `Ash-Greninja`), a
separate suffix stands alone (`Christmas`). Typos are corrected in the folder
name and reported as warnings. URL encoded names (`0025+-+Pikachu.3mf`) and
nested archives (up to 5 levels) are handled.

## Customizing

All of this requires running from source. The released executables embed
`pokemon-dex.json` and the code, so they cannot be customized in place. Make
the change in a clone of the repository, then run from source or build your
own executable as described below.

- **New Pokemon**: add `"1026": "Name"` to `pokemon-dex.json`
- **Stricter or looser typo detection**: change `TYPO_SIMILARITY_THRESHOLD` in `pokemon_organizer/classifier.py`
- **Exclude a file from sorting**: add it to `PROTECTED_ROOT_ENTRIES` in `pokemon_organizer/config.py`

## Building The Executable Yourself

The build uses [Nuitka](https://nuitka.net/), which compiles the Python code
to a native executable. It needs a C compiler: MSVC on Windows, Xcode command
line tools on macOS, gcc on Linux. Without one, `pip install ziglang` provides
a compiler Nuitka picks up automatically.

```bash
pip install nuitka zstandard
python -m nuitka --mode=onefile --enable-plugin=tk-inter \
  --windows-console-mode=disable \
  --include-data-files=pokemon-dex.json=pokemon-dex.json \
  --output-dir=build --output-filename=PokemonStatusTracker.exe \
  pokemon-status-tracker.pyw
```

On macOS use `--mode=app` instead of `--mode=onefile` to get an app bundle,
on Linux drop `--windows-console-mode` and the `.exe` suffix. Linux
additionally needs `pip install patchelf`. The exact commands the releases are
built with are in `.github/workflows/release.yml`.

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
- **The 3D model files themselves.** The designs are created and sold by
  [N3D Melbourne](https://www.n3dmelbourne.com/) and remain their property.
  Downloading, printing and selling prints is governed by N3D's own licence
  terms. This project is not affiliated with N3D, and no model files are
  included in this repository.
