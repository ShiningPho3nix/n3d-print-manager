# CLAUDE.md - Pokemon 3D Print Organizer

## Project Overview
This project organizes Pokemon 3D print files into a structured folder hierarchy based on Pokemon Dex numbers and variants. It includes a Python package for extraction and organization, and a GUI for tracking completion status.

## Language Policy

**Everything in this project is written in English and stays English.**

This covers code, comments, identifiers, documentation, script output, commit
messages, branch names, issue and pull request text, repository metadata and
**GUI labels**. Anything that lands in the repository or on its GitHub page is
English.

Talking about the project is not covered. Conversation with the maintainer is
held in German. The policy applies to artifacts, not to the discussion around
them.

This rule intentionally overrides the global instruction to write user
interface text in German. It applies to this project only.

## Git Workflow

**Squash merge is the default. Branches are updated by rebasing, never by
merging.**

- Land every pull request as a single commit:
  `gh pr merge <number> --squash --delete-branch`
- `main` keeps one commit per change. The commit message of that squash is what
  documents the change, so it carries the reasoning, not just the file list.
- Bring a branch up to date with `git rebase main` or `git pull --rebase`.
  A merge commit from `main` into a branch does not belong in the history.
- Delete the branch right after the squash merge. Its commits no longer exist
  in `main`, so rebasing a stale branch later would replay work that is already
  merged.
- Never rebase a branch someone else is working on, and never force push to
  `main`.

### No Exceptions

Every change goes through a pull request, including documentation, typo fixes
and configuration touch ups. A repository rule on GitHub rejects direct pushes
to `main`, so a commit made on `main` by mistake has to be moved to a branch:
`git branch <name> && git reset --hard origin/main && git checkout <name>`.

### Repository Setup

`.git/config` is not versioned, so a fresh clone does not carry these settings.
Run them once after cloning:

```bash
git config --local pull.rebase true   # pull rebases instead of merging
git config --local fetch.prune true   # drop refs of branches deleted on GitHub
git config --local merge.ff only      # refuse an accidental merge commit
```

The first one matters most: the Git for Windows installer writes
`pull.rebase = false` into the system config, so without the local override a
plain `git pull` does the opposite of what this section requires.

## Project Structure

### Directories
- **Source/** - drop zone for unsorted archives and files, scanned recursively
- **Designs/** - target root for all sorted output, never scanned as input
- **_Unsorted/** - catch-all for anything that cannot be classified

All three are created automatically and are excluded from version control.

### Running
```bash
python -m pokemon_organizer                  # extract archives, then sort
python -m pokemon_organizer --organize-only  # sort only, no extraction
python -m pokemon_organizer --keep-zips      # keep archives after extraction
python -m unittest discover -s tests -t .    # run the tests
```

The CLI exits with `1` when files could not be moved or archives could not be
unpacked, so a run is scriptable. Everything is standard library only, there are
no third party dependencies and no installation step.

### Main Modules
0. **pokemon_organizer/paths.py**
   - Lowest module, imports nothing from the package
   - `PROJECT_ROOT` is the resource root: the folder that holds the code and
     `pokemon-dex.json`. From source it is the repository, compiled it is the
     folder Nuitka unpacks to
   - `runtime_base_dir()` is the user data root: the folder that holds
     `Source/`, `Designs/` and `pokemon-status.json`. From source it equals
     `PROJECT_ROOT`, compiled it is `__compiled__.containing_dir`, the folder
     next to the executable (or next to the `.app` on macOS)
   - `is_compiled()` tests for Nuitka's `__compiled__` attribute. Nuitka does
     not set `sys.frozen`, do not test for it
   - `executable_name()` names the running executable so it is never sorted

1. **pokemon_organizer/config.py**
   - Shared configuration: `SOURCE_DIR`, `DESIGNS_DIR`, `MAX_ZIP_DEPTH` and
     `PROTECTED_ROOT_ENTRIES`
   - Re-exports `PROJECT_ROOT` from `paths.py`, every other module imports it
     from here
   - `PROTECTED_ROOT_ENTRIES` is what stops the tooling from sorting its own
     files, which matters because the file filter is format agnostic.
     `is_protected_root_entry()` additionally protects the running executable

2. **pokemon_organizer/dex.py**
   - Loads and validates `pokemon-dex.json` once per run, cached
   - Always reads from `PROJECT_ROOT`, never from `base_dir`. The compiled
     executable embeds the database, `--base-dir` only moves `Source/` and
     `Designs/`
   - Fails fast on a missing file, invalid JSON, a non-4-digit key or an empty
     name

3. **pokemon_organizer/classifier.py**
   - Pure functions, no file system access, covered by the tests
   - `classify_name()` returns a `Classification` with path components, a note
     and a `kind` (`base`, `variant`, `custom_variant`, `typo`, `pokeball`), or
     `None` when the name cannot be resolved

4. **pokemon_organizer/extractor.py**
   - Extracts archives found in Source/ and in the project root
   - Extracts into Source/{archive name}/ preserving the archive structure
   - Expands nested ZIPs in place, up to MAX_ZIP_DEPTH (5)
   - Deletes an archive only after it extracted successfully, unless
     `--keep-zips` or `KEEP_ZIPS` (`1/true/yes`) is set
   - Invalid `KEEP_ZIPS` values abort the run before anything is extracted
     (fail-fast on a destructive step)

5. **pokemon_organizer/organizer.py**
   - Core organization logic
   - Creates folder structure: `Designs/{dex#} - {name}/[variant]/`
   - Classifies by file name first, then falls back to the parent folder name
   - Moves unassignable .3mf files to `_Unsorted/3mf/`
   - Moves unassignable other formats to `_Unsorted/other/{archive}/{path}/`
   - Skips .zip files entirely, they belong to the extractor
   - Counts failed moves and reports them instead of aborting the whole run

6. **pokemon_organizer/events.py**
   - `Event(kind, message, verbose)`, the single output channel
   - Console and GUI are two sinks for the same events, neither parses text
   - `verbose=True` marks lines the GUI hides (currently base form notes)

7. **pokemon_organizer/runner.py**
   - `run_all()` runs extraction and organization, used by CLI and GUI alike

8. **pokemon-status-tracker.pyw**
   - GUI application for tracking completion status, entry point of the
     released executables
   - Uses `runtime_base_dir()` for `Designs/` and the status file, never
     `Path(__file__)`
   - Scans Designs/ and shows Pokemon and variants with checkboxes
   - Includes "Organize Files" button that calls `run_all()` in a thread
   - Saves status to pokemon-status.json, keyed relative to Designs/
   - Opens folders with `os.startfile`, `open` or `xdg-open` depending on
     `sys.platform`
   - Shows `pokemon_organizer.__version__` in the window title

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

_Unsorted/
├── 3mf/                    ← .3mf without valid dex number and not a Pokeball
└── other/{zip-name}/       ← All non-.3mf files, original archive path preserved
```
The GUI never shows `_Unsorted`: it scans `Designs/` only, and `_Unsorted/` sits
outside that root. On top of that, `scan_and_populate()` only accepts folders
whose first 4 characters are digits, and appends `Pokeballs` separately.

### Variant Detection Logic
1. **Known Form Variants**: Mega, Alolan, Galarian, Hisuian, Paldean → Full name in subfolder
2. **Custom Variants**: Christmas, Female, Male, NO SPOONS, etc. → Subfolder
3. **Typos**: Names similar to database name but not exact → Treated as base form (no subfolder)

### File Naming Patterns
- Format 1: `{dex#} - {name} - {profile} - {version}.3mf`
- Format 2: `{dex#}+-+{name}+-+{profile}.3mf` (URL encoded)
- Pokeballs: `{ball_name} - {profile}.3mf` (no dex number)

## Important Implementation Details

### Name Splitting
- Names are split at the real separator `" - "` first, then each segment is
  split into words. That drops separator dashes but keeps dashes inside names,
  which is what `Ho-Oh`, `Porygon-Z`, `Jangmo-o` and `Chien-Pao` depend on.
- Profile keywords (`AMS`, `SPLIT`, `MC`, `Profile`, `V[0-9]`, `w/`) are matched
  **anchored at the start of a word**, never as a substring. `Chimchar`
  contains `mc` and would otherwise be read as a profile marker.
- The base name is located with word boundaries, not a plain substring test.
  Otherwise `Mewtwo` would be read as variant `two` of `Mew`.

### Pokeball Names
- The ball name is taken from the segment that actually contains `ball`, not
  from the first segment. Otherwise a file like
  `{profile} - {stream} - Abomination Ball.3mf` would name its folder after the
  profile.
- A ball name written as one word is split before the final `Ball`, so
  `PokeBall` and `Pokeball` both end up in `Poke Ball` instead of creating
  competing folders that differ only in spelling.

### Path Sanitization
- `sanitize_path_component()` in classifier.py is applied when building a folder
  name, never before comparing names. Comparing sanitized names would break
  variant detection, because the database name and the file name would no longer
  match.
- Replaces `< > : " / \ | ? *` with a space, collapses repeated spaces and
  strips trailing dots and spaces.
- Affected database names: `Type: Null` (0772) becomes `Type Null`,
  `Mime Jr.` (0439) becomes `Mime Jr`, which is what Windows would store anyway.

### ZIP Extraction
- Uses `zipfile` from the standard library, which sanitizes member paths, so an
  archive cannot escape its target folder
- `expand_nested_zips()`: iterative loop over `rglob`, limited by `MAX_ZIP_DEPTH=5`
- Iterative instead of recursive, because the traversal would otherwise walk
  into directories it is creating itself
- Archives that fail to unpack are remembered and skipped on the next pass to
  prevent endless retries
- Archives are extracted **structure preserving** into `Source/{archive name}/`.
  Never flatten them: the folder context is what the parent folder fallback and
  the `_Unsorted/other/` path reconstruction both depend on.
- Extensions are compared lowercase so `.3MF` and `.STL` are handled correctly

### Classification Chain
Four stages, in this order:
1. File name resolves → `Designs/...`
2. Parent folder name resolves → `Designs/...`
3. Unresolved `.3mf` → `_Unsorted/3mf/`
4. Unresolved other format → `_Unsorted/other/{archive}/{original path}/`

Stage 2 only fires when a folder name actually resolves against the dex
database. Archives with freely named folders simply fall through to stage 3
or 4, so the stage can add matches but never misfile anything.

### GUI Live Output
- `run_all()` runs in a `threading.Thread` and only puts `Event` objects into a
  `queue.Queue`
- The queue is drained by `root.after(50, ...)` on the main thread, so **only
  the main thread ever touches Tk widgets**
- Events with `verbose=True` are skipped, `kind` selects the text tag. There is
  no text filtering and nothing to keep in sync between modules and GUI.

### Error Handling
- Typos in filenames: Create correct folder based on dex number from database
- Missing dex numbers: Check if it's a Pokeball, then try the parent folder name
- Still unresolvable `.3mf`: Moved to `_Unsorted/3mf/`
- Still unresolvable other formats: Moved to `_Unsorted/other/`, never deleted
- Duplicate files: Overwrite existing files
- Failed extraction: Keep the archive, remove the partial temporary folder
- Failed move: Counted, reported as an `error` event, run continues, exit code 1

## Code Conventions

### Python
- Standard library only, no third party packages
- Type hints on module level functions
- Dataclasses for results (`Classification`, `Event`, `OrganizeSummary`,
  `ExtractSummary`), never global result variables
- File system code takes `base_dir` as a parameter, so it can be tested against
  a fixture instead of the real project
- Normalize filenames: Replace `+` with spaces, remove `#` prefix
- Filter out profile keywords: AMS, SPLIT, MC, Profile, V[0-9]

## Common Issues

### Console Encoding
- The Windows console is not UTF-8 by default, the output uses emoji
- Solution: `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` in
  `__main__.py`

### Tk And Threads
- Tk is not thread safe. Never touch a widget from a worker thread.
- Solution: the worker puts events into a queue, `root.after()` drains it

## Testing Scenarios

1. **Normal Pokemon**: `0025 - Pikachu - AMS Profile.3mf` → `Designs/0025 - Pikachu/`
2. **Mega Variant**: `0006 - Mega Charizard X - AMS.3mf` → `Designs/0006 - Charizard/Mega Charizard X/`
3. **Custom Variant**: `0001 - Bulbasaur - Christmas - AMS.3mf` → `Designs/0001 - Bulbasaur/Christmas/`
4. **Typo**: `0282 - Gardivoir - AMS.3mf` → `Designs/0282 - Gardevoir/` (no subfolder)
5. **Pokeball**: `Great Ball - AMS.3mf` → `Designs/Pokeballs/Great Ball/`
6. **Deep nesting**: `Source/batch/a/b/c/d/e/0025 - Pikachu - AMS.3mf` → `Designs/0025 - Pikachu/`
7. **Nested ZIP**: `Source/batch/x/inner.zip` → unpacked, contents processed like any other file
8. **Parent folder fallback**: `Source/batch/0001 - Bulbasaur/preview.png` → `Designs/0001 - Bulbasaur/`
9. **Foreign format**: `Source/batch/a/b/handbuch.pdf` → `_Unsorted/other/batch/a/b/handbuch.pdf`
10. **No dex number**: `mystery-model.3mf` → `_Unsorted/3mf/`
11. **Protected file**: `CLAUDE.md` in the project root → never treated as input
12. **Archive at organize time**: `Source/kept.zip` → skipped, reported, left in place
13. **Dash in name**: `0474 - Mega Porygon-Z - AMS.3mf` → `Designs/0474 - Porygon-Z/Mega Porygon-Z/`

Scenarios 1-5, 10 and 13 are covered by `tests/test_classifier.py`.

## Maintenance

### Adding New Pokemon (Future Generations)
1. Update `pokemon-dex.json` with new entries
2. No code changes needed - the modules use the database automatically

### Adding New Variant Types
1. Add the keyword to `FORM_VARIANT_PATTERN` or `CUSTOM_VARIANT_PATTERN` in
   classifier.py
2. Consider if it needs special folder naming (like Mega forms)
3. Add a case to `tests/test_classifier.py`

### Excluding a File From Sorting
Add its name to `PROTECTED_ROOT_ENTRIES` in `pokemon_organizer/config.py`.

### Releasing
Releases are built by `.github/workflows/release.yml` with
[Nuitka](https://nuitka.net/) on GitHub's runners, one job per platform:
Windows x64 onefile, macOS arm64 app bundle, Linux x64 onefile. The dex
database is embedded with `--include-data-files`.

1. Bump `__version__` in `pokemon_organizer/__init__.py` through a pull request
2. After the squash merge: `git tag vX.Y.Z && git push origin vX.Y.Z`
3. The workflow refuses a tag that does not match `__version__`, runs the
   tests, builds, and creates the release with the three files attached

Pinned versions (`PYTHON_VERSION`, `NUITKA_VERSION`) live in the workflow's
`env` block. Bump them deliberately, never to `latest`. The static part of the
release notes is `.github/RELEASE_NOTES.md`, the change list is generated.

The executables are not code signed: macOS shows a Gatekeeper dialog, Windows
Defender may ask. Signing costs money and is out of scope.

## Known Limitations

- Nested archives are expanded only up to `MAX_ZIP_DEPTH` (5) levels per run.
  Anything deeper stays packed and is reported.
- A profile segment ends the name, so a variant that appears **after** the
  profile marker is dropped: `0004 - Charmander - SPLIT Profile - No Feet - V3.1`
  sorts as the base form, `No Feet` is lost.
- Windows reserved device names (CON, NUL, AUX, PRN, COM1-9, LPT1-9) are not
  special cased. No Pokemon name collides with them, and every main folder is
  prefixed with its dex number, so this is theoretical.
- Released executables cannot be customized: `pokemon-dex.json` and the
  patterns are compiled in. Customizing means running from source or building
  your own executable. Intel Macs are not built, GitHub retires its Intel
  runners in 2027.

## File Modifications

When modifying the code, ensure:
- Python files keep LF line endings (pinned in `.gitattributes`)
- `python -m unittest discover -s tests -t .` passes
- GUI maintains live output functionality
- The GUI imports folder names from `pokemon_organizer.config`, never redefines
  them
- Database integrity (valid JSON, no duplicates)
