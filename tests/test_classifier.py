import unittest

from pokemon_organizer.classifier import classify_name, sanitize_path_component
from pokemon_organizer.dex import load_dex

DEX = load_dex()

CASES = [
    ("0025 - Pikachu - AMS Profile.3mf", "0025 - Pikachu", "base"),
    ("0025+-+Pikachu+-+SPLIT+Profile+-+V3.3mf", "0025 - Pikachu", "base"),
    ("#0039+Jigglypuff+-+AMS+Profile+-+V1.1.3mf", "0039 - Jigglypuff", "base"),
    ("0006 - Mega Charizard X - AMS.3mf", "0006 - Charizard/Mega Charizard X", "variant"),
    ("0065 - Mega Alakazam - AMS - V1.3mf", "0065 - Alakazam/Mega Alakazam", "variant"),
    ("0025 - Female Pikachu - AMS Profile.3mf", "0025 - Pikachu/Female Pikachu", "variant"),
    ("0065 - Alakazam - NO SPOONS - AMS Profile - V1.3mf", "0065 - Alakazam/NO SPOONS", "variant"),
    ("0001 - Bulbasaur - Christmas - AMS.3mf", "0001 - Bulbasaur/Christmas", "variant"),
    ("0025 - Pikachu Libre - AMS.3mf", "0025 - Pikachu/Libre", "variant"),
    # a variant glued to the name with a hyphen keeps the whole name as folder
    ("0658 Ash-Greninja - SPLIT - V1.1.3mf", "0658 - Greninja/Ash-Greninja", "variant"),
    ("0474 - Porygon-Z-Shiny - AMS.3mf", "0474 - Porygon-Z/Porygon-Z-Shiny", "variant"),
    # accents and gender symbols are ignored when comparing names
    ("0669 - Flabebe - AMS.3mf", "0669 - Flabébé", "base"),
    ("0029 - Nidoran - AMS.3mf", "0029 - Nidoran♀", "base"),
    ("0083 - Farfetchd - AMS.3mf", "0083 - Farfetch'd", "base"),
    # a name that does not resemble the dex entry becomes its own variant folder
    ("0025 - Raichu - AMS.3mf", "0025 - Pikachu/Raichu", "unmatched"),
    ("Great Ball - AMS.3mf", "Pokeballs/Great Ball", "pokeball"),
    # a ball name written as one word must not create a second folder
    ("PokeBall+-+AMS+Profile.3mf", "Pokeballs/Poke Ball", "pokeball"),
    ("Pokeball+-+Open+-+SPLIT+v1.2.3mf", "Pokeballs/Poke Ball", "pokeball"),
    # the ball name is the segment that says "ball", not the first segment
    (
        "Cham3l30n's P2S Profile - Nathans Livestream - Abomination Ball.3mf",
        "Pokeballs/Abomination Ball",
        "pokeball",
    ),
    ("0250 - Ho-Oh - AMS Profile.3mf", "0250 - Ho-Oh", "base"),
    ("0474 - Mega Porygon-Z - AMS.3mf", "0474 - Porygon-Z/Mega Porygon-Z", "variant"),
    ("0782 - Jangmo-o - SPLIT Profile.3mf", "0782 - Jangmo-o", "base"),
    ("0122 - Mr. Mime - AMS.3mf", "0122 - Mr. Mime", "base"),
    ("0122 - Shiny Mr. Mime - AMS.3mf", "0122 - Mr. Mime/Shiny Mr. Mime", "variant"),
    ("0772 - Type: Null - AMS.3mf", "0772 - Type Null", "base"),
    ("0439 - Mime Jr. - AMS.3mf", "0439 - Mime Jr", "base"),
    # Chimchar contains "mc", which must not be read as a profile keyword
    ("0390 - Christmas Chimchar - AMS.3mf", "0390 - Chimchar/Christmas Chimchar", "variant"),
    # Mew ends in "w", which must not be read as the "w " profile keyword
    ("0151 - Shiny Mew - AMS.3mf", "0151 - Mew/Shiny Mew", "variant"),
    # a wrong dex number must not turn the name into a variant
    ("0150 - Mewtwo - AMS.3mf", "0150 - Mewtwo", "base"),
]

MISSPELLED = [
    ("0282 - Gardivoir - AMS.3mf", "0282 - Gardevoir", "base", "Gardivoir"),
    ("0122 - Mr Mine - AMS.3mf", "0122 - Mr. Mime", "base", "Mr Mine"),
    # phonetic misspellings score lower than single letter swaps
    ("0155 - Cinderquil - AMS Profile - V1.1.3mf", "0155 - Cyndaquil", "base", "Cinderquil"),
    # a typo inside a variant is corrected in the folder name
    ("0658 - Ash-Grenimja - AMS.3mf", "0658 - Greninja/Ash-Greninja", "variant", "Grenimja"),
    ("0006 - Mega Charizrd X - AMS.3mf", "0006 - Charizard/Mega Charizard X", "variant", "Charizrd"),
]

UNRESOLVED = [
    "mystery-model.3mf",
    "Cham3l30n's P2S Profile.3mf",
    "9999 - Nonexistent - AMS.3mf",
]


class ClassifyNameTest(unittest.TestCase):
    def test_classification(self):
        for raw_name, expected_path, expected_kind in CASES:
            with self.subTest(raw_name=raw_name):
                result = classify_name(raw_name, DEX)
                self.assertIsNotNone(result)
                self.assertEqual(expected_path, result.relative_path)
                self.assertEqual(expected_kind, result.kind)
                self.assertIsNone(result.misspelling)

    def test_misspelled_names(self):
        for raw_name, expected_path, expected_kind, expected_misspelling in MISSPELLED:
            with self.subTest(raw_name=raw_name):
                result = classify_name(raw_name, DEX)
                self.assertIsNotNone(result)
                self.assertEqual(expected_path, result.relative_path)
                self.assertEqual(expected_kind, result.kind)
                self.assertEqual(expected_misspelling, result.misspelling)

    def test_unresolved_names(self):
        for raw_name in UNRESOLVED:
            with self.subTest(raw_name=raw_name):
                self.assertIsNone(classify_name(raw_name, DEX))

    def test_parent_folder_names_resolve_without_extension(self):
        result = classify_name("0001 - Bulbasaur", DEX)
        self.assertIsNotNone(result)
        self.assertEqual("0001 - Bulbasaur", result.relative_path)


class SanitizePathComponentTest(unittest.TestCase):
    def test_removes_invalid_characters(self):
        self.assertEqual("Type Null", sanitize_path_component("Type: Null"))
        self.assertEqual("Mime Jr", sanitize_path_component("Mime Jr."))
        self.assertEqual("a b", sanitize_path_component('  a <>:"/\|?* b . '))
