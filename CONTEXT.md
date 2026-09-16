# CONTEXT.md - Begriffserklärungen

## Pokemon-spezifische Begriffe

### Dex-Nummer (Dex Number)
- **Definition**: Eindeutige Nummer eines Pokemon im National Pokedex
- **Format**: 4-stellige Zahl mit führenden Nullen (z.B. `0001`, `0025`, `0384`)
- **Beispiele**:
  - 0001 = Bulbasaur
  - 0025 = Pikachu
  - 0006 = Charizard
- **Verwendung**: Primärer Identifikator für Sortierung und Organisation

### Pokemon-Formen und Varianten

#### Base Form (Grundform)
- **Definition**: Standard-Erscheinung eines Pokemon ohne besondere Varianten
- **Beispiel**: Normales Pikachu, normales Charizard
- **Speicherort**: Direkt im Hauptordner `{dex#} - {name}/`

#### Mega-Evolution
- **Definition**: Temporäre Kampf-Transformation in Pokemon-Spielen
- **Beispiele**:
  - Mega Charizard X (Feuer/Drache)
  - Mega Charizard Y (Feuer/Flug)
  - Mega Alakazam
  - Mega Lucario
- **Ordnerstruktur**: `{dex#} - {base_name}/Mega {pokemon_name}/`
- **Besonderheit**: Behalten die Dex-Nummer der Grundform

#### Regionale Formen (Regional Forms)
- **Definition**: Lokale Varianten aus verschiedenen Regionen
- **Typen**:
  - **Alolan**: Aus der Alola-Region (Gen 7)
  - **Galarian**: Aus der Galar-Region (Gen 8)
  - **Hisuian**: Aus der Hisui-Region (Legends: Arceus)
  - **Paldean**: Aus der Paldea-Region (Gen 9)
- **Beispiel**: Alolan Ninetales (Eis/Fee statt Feuer)
- **Ordnerstruktur**: `{dex#} - {base_name}/Alolan/`

#### Custom Varianten
- **Definition**: Nicht-offizielle Modifikationen oder Designs
- **Beispiele**:
  - Christmas Bulbasaur (Weihnachts-Theme)
  - Female Pikachu (Geschlechtsspezifisch)
  - NO SPOONS Alakazam (ohne Löffel)
  - Open Pokeball (geöffneter Zustand)
- **Ordnerstruktur**: `{dex#} - {name}/{variant_name}/`

## 3D-Druck-spezifische Begriffe

### .3mf Datei
- **Definition**: 3D Manufacturing Format - Dateiformat für 3D-Druckmodelle
- **Standard**: Von 3MF Consortium entwickelt
- **Vorteile**:
  - Kompakt (ZIP-basiert)
  - Enthält Metadaten, Farben, Texturen
  - Besser als STL für moderne 3D-Drucker
- **Verwendung**: Hauptformat für Pokemon 3D-Druckdateien

### Profile

#### AMS Profile
- **Definition**: Automated Material System - Multi-Filament-Druck
- **Hersteller**: Bambu Lab
- **Verwendung**: Automatischer Farbwechsel während des Drucks
- **Beispiel**: `0025 - Pikachu - AMS Profile - V3.3mf`

#### SPLIT Profile
- **Definition**: Modell in mehrere Teile aufgeteilt
- **Zweck**:
  - Druck ohne Support-Material
  - Separate Farbgebung
  - Größere Modelle auf kleinen Druckbetten
- **Beispiel**: `0025 - Pikachu - SPLIT Profile - V3.3mf`

#### MC Profile (Multi-Color)
- **Definition**: Multi-Color-Druck mit manuellen Farbwechseln
- **Verwendung**: Für Drucker ohne AMS
- **Beispiel**: `0146 - Moltres - MC Profile - V1.1.3mf`

### Versionen
- **Format**: `V{major}.{minor}` oder `V{major}`
- **Beispiele**: `V1`, `V2.1`, `V3.3mf`
- **Bedeutung**: Versionsnummer des 3D-Modells

## Pokeballs

### Definition
- **Im Pokemon-Universum**: Geräte zum Fangen und Lagern von Pokemon
- **Als 3D-Modelle**: Separate Kategorie von Druckdateien

### Typen
- **Poke Ball**: Standard-Ball (rot/weiß)
- **Great Ball**: Verbesserte Version (blau)
- **Ultra Ball**: Noch stärker (gelb/schwarz)
- **Master Ball**: Fängt jedes Pokemon garantiert (lila)
- **Spezial-Bälle**: Timer Ball, Dusk Ball, Quick Ball, etc.

### Ordnerstruktur
```
Pokeballs/
├── Great Ball/
│   ├── Great Ball - AMS Profile.3mf
│   └── Great Ball - SPLIT Profile.3mf
├── Master Ball/
└── Ultra Ball/
```

## Technische Begriffe

### Normalisierung (Normalization)
- **Definition**: Umwandlung von Dateinamen in einheitliches Format
- **Schritte**:
  - `+` → Leerzeichen
  - `#` Prefix entfernen
  - URL-Encoding auflösen
- **Beispiel**: `#0025+-+Pikachu` → `0025 - Pikachu`

### Varianten-Erkennung (Variant Detection)
- **Methode**: Pattern-Matching gegen bekannte Keywords
- **Keywords**: Mega, Alolan, Female, Christmas, etc.
- **Fallback**: Wenn Name nicht Base-Name enthält

### Base-Name-Extraktion
- **Quelle**: pokemon-dex.json Datenbank
- **Verwendung**: Korrekte Ordnerbenennung trotz Tippfehlern
- **Beispiel**:
  - Datei: `0282 - Gardivoir - AMS.3mf` (Tippfehler)
  - Datenbank: 0282 = "Gardevoir"
  - Ordner: `0282 - Gardevoir/`

### Filter Patterns
- **Skip Patterns**: Zeilen die NICHT angezeigt werden
  - `📋 Dex Number`
  - `🎯 Base Pokemon`
  - `📝 Extracted Name`
  - `📦 Ball Type`
- **Keep Patterns**: Zeilen die ANGEZEIGT werden
  - `Processing:`
  - `✅ Moved to:`
  - `⚠️ Warning:`
  - `🎱 Pokeball detected`

## Dateiformat-Konventionen

### Standard-Format
```
{dex#} - {pokemon_name} - {profile} - {version}.3mf
```
**Beispiel**: `0025 - Pikachu - AMS Profile - V3.3mf`

### URL-Encoded Format
```
{dex#}+-+{pokemon_name}+-+{profile}.3mf
```
**Beispiel**: `0025+-+Pikachu+-+AMS+Profile.3mf`

### Varianten-Format
```
{dex#} - {variant} {pokemon_name} - {profile}.3mf
```
**Beispiel**: `0006 - Mega Charizard X - AMS - V2.3mf`

### Pokeball-Format
```
{ball_name} - {profile}.3mf
```
**Beispiel**: `Great Ball - AMS Profile.3mf`

## Status-Tracking

### pokemon-status.json
- **Struktur**: Key-Value Pairs
- **Key**: Relativer Pfad (z.B. `"0025 - Pikachu"`, `"0025 - Pikachu/Female"`)
- **Value**: Boolean (`true` = erledigt, `false` = offen)
- **Auto-Save**: Bei jeder Checkbox-Änderung

### Fortschritts-Berechnung
```
Fortschritt = (Erledigte Items / Gesamt Items) × 100%
```

## Ordner-Hierarchie

### Level 1: Pokemon Hauptordner
```
{dex#} - {pokemon_name}/
```

### Level 2: Varianten-Unterordner (optional)
```
{dex#} - {pokemon_name}/
└── {variant_name}/
```

### Sonderfall: Pokeballs
```
Pokeballs/
└── {ball_type}/
```

### GUI-Darstellung
- Pokemon: Flache Liste (Level 1)
- Varianten: Eingerückt mit `↳` (Level 2)
- Pokeballs: Am Ende mit Separator, flach mit 🎱 Icon
