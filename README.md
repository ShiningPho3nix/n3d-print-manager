# Pokemon 3D Print Organizer

Automatische Organisation und Tracking von Pokemon 3D-Druckdateien (.3mf) mit intelligenter Sortierung nach Pokedex-Nummern und Varianten.

## Features

### 🗂️ Automatische Organisation
- **ZIP-Extraktion**: Automatisches Entpacken von heruntergeladenen ZIP-Archiven
- **Intelligente Sortierung**: Dateien werden nach Dex-Nummer und Varianten organisiert
- **Datenbank-gestützt**: Verwendet offizielle Pokemon-Datenbank für korrekte Namen
- **Tippfehler-Korrektur**: Erkennt und korrigiert Tippfehler in Dateinamen
- **Pokeball-Support**: Separate Kategorie für Pokeball-Modelle
- **Beliebige Ordnertiefe**: Dateien werden unabhängig von der Ordnerstruktur im Archiv gefunden
- **Verschachtelte ZIPs**: ZIPs innerhalb von ZIPs werden automatisch mit entpackt (bis 5 Ebenen)
- **Sammelordner**: Nicht zuordenbare Dateien landen in `_Unsorted/` statt gelöscht zu werden

### ✅ Status-Tracking
- **GUI-Anwendung**: Übersichtliche Darstellung aller Pokemon und Varianten
- **Checkbox-System**: Markiere erledigte Drucke mit einem Klick
- **Fortschritts-Anzeige**: Echtzeit-Statistik über Druckfortschritt
- **Auto-Save**: Status wird automatisch gespeichert
- **Explorer-Integration**: Direkter Zugriff auf Ordner aus der GUI

### 🔧 Varianten-Unterstützung
- **Mega-Evolutionen**: Mega Charizard X/Y, Mega Alakazam, etc.
- **Regionale Formen**: Alolan, Galarian, Hisuian, Paldean
- **Custom-Varianten**: Christmas, Female/Male, NO SPOONS, etc.
- **Profile-Typen**: AMS, SPLIT, MC - alle in einem Ordner

## Installation

### Voraussetzungen
- **Windows** (getestet auf Windows 10/11)
- **Git Bash** (für Bash-Skripte)
- **Python 3.x** (für GUI)

### Setup
1. Alle Dateien in einen Ordner entpacken
2. Git Bash installieren (falls noch nicht vorhanden)
3. Python 3 installieren (falls noch nicht vorhanden)
4. Fertig! Keine weiteren Dependencies nötig.

## Verwendung

### Option 1: GUI (Empfohlen)
1. Doppelklick auf `Start Pokemon Tracker.bat`
2. GUI öffnet sich
3. Klicke auf **"📂 Organize Files"** um:
   - ZIPs zu extrahieren (falls vorhanden)
   - Dateien zu organisieren
   - ZIPs zu löschen
4. Markiere erledigte Pokemon mit Checkboxen
5. Nutze **"📁"** Buttons um Ordner im Explorer zu öffnen

### Option 2: Manuell (Kommandozeile)
```bash
# Nur organisieren (ohne ZIP-Extraktion)
./organize-pokemon.sh

# ZIP-Extraktion + Organisation
./extract-and-organize.sh
```

## Ordnerstruktur

### Pokemon
```
0025 - Pikachu/
├── 0025 - Pikachu - AMS Profile - V3.3mf          ← Base-Form
├── 0025 - Pikachu - SPLIT Profile - V3.3mf        ← Base-Form
└── Female/                                         ← Variante
    ├── 0025 - Female Pikachu - AMS Profile.3mf
    └── 0025 - Female Pikachu - SPLIT Profile.3mf
```

### Mega-Evolutionen
```
0006 - Charizard/
├── 0006 - Charizard - AMS Profile.3mf             ← Base-Form
├── Mega Charizard X/                              ← Mega-Variante
│   └── 0006 - Mega Charizard X - AMS - V2.3mf
└── Mega Charizard Y/                              ← Mega-Variante
    ├── 0006 Mega Charizard Y - AMS - V1.3mf
    ├── 0006 Mega Charizard Y - MC - V1.1.3mf
    └── 0006 Mega Charizard Y - SPLIT - V1.3mf
```

### Pokeballs
```
Pokeballs/
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

### Sammelordner (`_Unsorted`)
```
_Unsorted/
├── 3mf/                          ← .3mf ohne gültige Dex-Nummer und kein Pokeball
│   └── mystery-model.3mf
└── other/                        ← Alle Dateien, die kein .3mf sind
    └── {zip-name}/               ← Pro Bulk-Download getrennt
        └── a/b/c/                ← Originalpfad aus dem Archiv bleibt erhalten
            ├── handbuch.pdf
            └── teil.stl
```
> Der Sammelordner erscheint bewusst **nicht** in der GUI-Liste — dort werden nur Ordner angezeigt, die mit 4 Ziffern beginnen, plus `Pokeballs`.

## Datei-Behandlung

### Unterstützte Formate
- **Standard**: `0025 - Pikachu - AMS Profile - V3.3mf`
- **URL-Encoded**: `0025+-+Pikachu+-+AMS+Profile.3mf`
- **Varianten**: `0006 - Mega Charizard X - AMS - V2.3mf`
- **Pokeballs**: `Great Ball - AMS Profile.3mf`
- **Ordnerstruktur im ZIP**: beliebig tief und frei benannt — ausgewertet wird ausschließlich der Dateiname

### Automatische Erkennung
- **Dex-Nummer**: Erste 4 Ziffern → Datenbank-Lookup
- **Pokemon-Name**: Aus Datenbank (korrekte Schreibweise)
- **Varianten**: Pattern-Matching gegen bekannte Keywords
- **Tippfehler**: Werden erkannt und korrekt zugeordnet

### Spezialfälle
| Eingabe | Behandlung | Ausgabe |
|---------|------------|---------|
| `0282 - Gardivoir` (Tippfehler) | Als Base-Form | `0282 - Gardevoir/` |
| `0006 - Mega Charizard X` | Als Mega-Variante | `0006 - Charizard/Mega Charizard X/` |
| `Great Ball - AMS` | Als Pokeball | `Pokeballs/Great Ball/` |
| `0001 - Bulbasaur - Christmas` | Als Custom-Variante | `0001 - Bulbasaur/Christmas/` |
| `mystery-model.3mf` (keine Dex-Nr.) | Nicht zuordenbar | `_Unsorted/3mf/` |
| `handbuch.pdf`, `teil.stl` | Kein .3mf-Format | `_Unsorted/other/{zip-name}/{pfad}/` |
| `x/inner.zip` (ZIP in ZIP) | Wird entpackt, Inhalt normal verarbeitet | je nach Inhalt |
| Zwei gleichnamige `.3mf` | Letzte gewinnt, Warnung im Live-Output | Zielordner |

## GUI-Features im Detail

### Hauptfenster
- **Pokemon-Liste**: Sortiert nach Dex-Nummer
- **Checkboxen**: ☑ = Erledigt, ☐ = Offen
- **Varianten**: Eingerückt unter Haupt-Pokemon
- **Pokeballs**: Am Ende der Liste mit 🎱 Icon
- **Fortschritt**: `Progress: 45/120 (37.5%)`

### Buttons
| Button | Funktion |
|--------|----------|
| **Refresh** | Liste neu laden |
| **📂 Organize Files** | ZIP-Extraktion + Organisation |
| **📁** (bei jedem Eintrag) | Ordner im Explorer öffnen |

### Organize-Fenster
- **Live-Output**: Zeigt Fortschritt in Echtzeit
- **Kompakte Ansicht**: Filtert unwichtige Details
- **Kein Bash-Fenster**: Läuft im Hintergrund
- **Close-Button**: Aktiviert nach Abschluss

## Profile-Typen

### AMS (Automated Material System)
- **Verwendung**: Bambu Lab AMS
- **Vorteil**: Automatischer Farbwechsel
- **Ideal für**: Multi-Color-Drucke

### SPLIT
- **Verwendung**: In Teile gesplittet
- **Vorteil**: Kein Support nötig
- **Ideal für**: Separate Farbgebung

### MC (Multi-Color)
- **Verwendung**: Manueller Farbwechsel
- **Vorteil**: Ohne AMS druckbar
- **Ideal für**: Drucker ohne Multi-Material-System

## Troubleshooting

### Problem: GUI startet nicht
**Lösung**:
- Python installiert? `python --version`
- Doppelklick auf `Start Pokemon Tracker.bat`

### Problem: Bash-Skript funktioniert nicht
**Lösung**:
- Git Bash installiert?
- Skript ausführbar? `chmod +x *.sh`
- Mit Git Bash ausführen, nicht CMD

### Problem: Encoding-Fehler (kaputte Zeichen)
**Lösung**:
- Wird automatisch gehandhabt (UTF-8 + error='replace')
- Sollte nicht mehr auftreten

### Problem: Core Dumps / Crashes
**Lösung**:
- Wurde gefixt (bash string matching statt grep)
- Bei Problemen: Skript neu downloaden

### Problem: Dateien landen im falschen Ordner
**Lösung**:
- Dex-Nummer prüfen: Erste 4 Ziffern müssen gültig sein
- pokemon-dex.json aktuell?
- Bei Tippfehlern: Wird automatisch korrigiert

### Problem: Datei fehlt nach dem Organisieren
**Lösung**:
- `_Unsorted/3mf/` prüfen: `.3mf` ohne gültige Dex-Nummer landen dort
- `_Unsorted/other/{zip-name}/` prüfen: alle Nicht-3MF-Dateien, Originalpfad erhalten
- Bei gleichnamigen Dateien überschreibt die zuletzt verarbeitete (Warnung im Live-Output)
- Gelöscht wird nichts — nur die ZIP-Archive selbst nach erfolgreicher Extraktion

## Erweiterte Nutzung

### Neue Pokemon hinzufügen (Zukunft)
1. `pokemon-dex.json` öffnen
2. Neuen Eintrag hinzufügen:
   ```json
   "1026": "NewPokemonName"
   ```
3. Speichern - fertig!

### Custom-Varianten definieren
Keywords in `organize-pokemon.sh` Zeile 217 anpassen:
```bash
elif echo "$pokemon_name" | grep -qiE "(Christmas|Halloween|YourKeyword)"; then
```

### Batch-Verarbeitung
Alle ZIPs in Ordner legen und:
```bash
./extract-and-organize.sh
```
→ Alle ZIPs werden verarbeitet

**ZIPs behalten (für Testläufe):**
```bash
KEEP_ZIPS=1 ./extract-and-organize.sh
```
→ Die Archive bleiben nach der Verarbeitung erhalten. Erlaubt sind `0/1`, `false/true`, `no/yes` — bei einem unbekannten Wert bricht das Skript ab, **bevor** entpackt wird.

## Technische Details

### Dateien
| Datei | Zweck |
|-------|-------|
| `extract-and-organize.sh` | ZIP-Extraktion + Organisation |
| `organize-pokemon.sh` | Kern-Organisations-Logik |
| `pokemon-status-tracker.pyw` | GUI-Anwendung |
| `Start Pokemon Tracker.bat` | GUI-Starter |
| `pokemon-dex.json` | Pokemon-Datenbank (1025 Einträge) |
| `pokemon-status.json` | Status-Speicherung (auto-generiert) |

### Anforderungen
- **Bash**: Git Bash (unter Windows)
- **Python**: 3.x mit tkinter (Standard-Library)
- **Tools**: unzip (in Git Bash enthalten)

### Performance
- **Organisation**: ~1 Sekunde pro 10 Dateien
- **ZIP-Extraktion**: Abhängig von Archiv-Größe
- **GUI**: Sofortiges Laden bei <200 Pokemon

## Changelog

### Version 1.1
- ✅ Bulk-ZIPs mit beliebiger Ordnertiefe und freier Keyword-Struktur
- ✅ Verschachtelte ZIPs werden rekursiv entpackt (max. 5 Ebenen)
- ✅ Sammelordner `_Unsorted/` statt Löschen nicht zuordenbarer Dateien
- ✅ Case-insensitive Endungs-Erkennung (`.3MF`, `.STL`)
- ✅ Warnung bei gleichnamigen Dateien aus verschiedenen Unterordnern
- ✅ GUI-Filter zeigt wieder an, welche ZIP gerade entpackt wird
- ✅ `KEEP_ZIPS=1` behält die ZIP-Archive nach der Verarbeitung (Testläufe)

### Version 1.0 (Initial Release)
- ✅ Automatische Organisation nach Dex-Nummer
- ✅ Varianten-Unterstützung (Mega, Alolan, Custom)
- ✅ Pokeball-Kategorie
- ✅ ZIP-Extraktion
- ✅ GUI mit Status-Tracking
- ✅ Live-Output ohne Bash-Fenster
- ✅ Tippfehler-Korrektur
- ✅ UTF-8 Encoding
- ✅ Core Dump Fixes

## Credits

- **Pokemon-Datenbank**: Gen 1-9 (1025 Pokemon)
- **3D-Modelle**: Von verschiedenen Creators (siehe Original-Dateien)
- **Organisation**: Automatisch via Scripts

## Support

Bei Problemen oder Fragen:
1. Siehe **Troubleshooting** Sektion
2. `CONTEXT.md` für Begriffserklärungen
3. `CLAUDE.md` für technische Details

## Lizenz

Dieses Tool ist für den persönlichen Gebrauch. Pokemon ist ein eingetragenes Warenzeichen von Nintendo/Game Freak/Creatures Inc.
