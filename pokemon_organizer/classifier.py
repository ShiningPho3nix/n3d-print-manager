import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Literal

from .config import POKEBALLS_FOLDER

BALL_KEYWORD = "ball"

ClassificationKind = Literal["base", "variant", "unmatched", "pokeball"]

TYPO_SIMILARITY_THRESHOLD = 0.7

SEGMENT_SEPARATOR_PATTERN = re.compile(r"\s+-\s+")
EXTENSION_PATTERN = re.compile(r"\.([A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*)$")
DEX_NUMBER_PATTERN = re.compile(r"^[0-9]{4}")
INVALID_PATH_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*]')
PROFILE_WORD_PATTERN = re.compile(r"^(AMS|SPLIT|MC|Profile|V[0-9]|w/)", re.IGNORECASE)
NAME_TOKEN_PATTERN = re.compile(r"[^\s-]+")


@dataclass(frozen=True)
class Classification:
    parts: tuple[str, ...]
    note: str
    kind: ClassificationKind
    misspelling: str | None = None
    resolved_by_name: bool = False

    @property
    def relative_path(self) -> str:
        return "/".join(self.parts)


@dataclass(frozen=True)
class BaseNameMatch:
    start: int
    end: int
    similarity: float


@dataclass(frozen=True)
class VariantDecision:
    folder: str
    note: str
    kind: ClassificationKind
    misspelling: str | None = None


def strip_extension(name: str) -> str:
    return EXTENSION_PATTERN.sub("", name)


def sanitize_path_component(component: str) -> str:
    component = INVALID_PATH_CHARS_PATTERN.sub(" ", component)
    component = re.sub(r" +", " ", component)
    component = re.sub(r"[\s.]+$", "", component)
    return component.lstrip()


def normalize_name(raw_name: str) -> str:
    normalized = raw_name.replace("+", " ")
    normalized = normalized.removeprefix("#")
    return strip_extension(normalized)


def split_name_words(text: str) -> list[str]:
    words: list[str] = []
    for segment in SEGMENT_SEPARATOR_PATTERN.split(text):
        for word in segment.split():
            if PROFILE_WORD_PATTERN.match(word):
                return words
            words.append(word)
    return words


def comparison_key(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(char for char in decomposed if char.isalnum()).casefold()


def name_similarity(candidate: str, base_name: str) -> float:
    return SequenceMatcher(None, comparison_key(candidate), comparison_key(base_name)).ratio()


def find_base_name(pokemon_name: str, base_name: str) -> BaseNameMatch | None:
    tokens = list(NAME_TOKEN_PATTERN.finditer(pokemon_name))
    best: BaseNameMatch | None = None

    for first_index, first_token in enumerate(tokens):
        for last_token in tokens[first_index:]:
            candidate = pokemon_name[first_token.start() : last_token.end()]
            similarity = name_similarity(candidate, base_name)
            if best is None or similarity > best.similarity:
                best = BaseNameMatch(first_token.start(), last_token.end(), similarity)

    if best is None or best.similarity < TYPO_SIMILARITY_THRESHOLD:
        return None

    return best


def build_name_index(dex: dict[str, str]) -> dict[str, set[str]]:
    name_index: dict[str, set[str]] = {}
    for dex_number, name in dex.items():
        name_index.setdefault(comparison_key(name), set()).add(dex_number)
    return name_index


def find_dex_number_by_name(pokemon_name: str, dex: dict[str, str]) -> str | None:
    name_index = build_name_index(dex)
    tokens = list(NAME_TOKEN_PATTERN.finditer(pokemon_name))
    matches: list[tuple[int, int, set[str]]] = []

    for first_index, first_token in enumerate(tokens):
        for last_token in tokens[first_index:]:
            candidate = pokemon_name[first_token.start() : last_token.end()]
            dex_numbers = name_index.get(comparison_key(candidate))
            if dex_numbers:
                matches.append((first_token.start(), last_token.end(), dex_numbers))

    outermost_matches = [
        (start, end, dex_numbers)
        for start, end, dex_numbers in matches
        if not any(
            other_start <= start and end <= other_end and (other_start, other_end) != (start, end)
            for other_start, other_end, _ in matches
        )
    ]
    found_dex_numbers = set().union(*(dex_numbers for _, _, dex_numbers in outermost_matches))

    if len(found_dex_numbers) != 1:
        return None

    return found_dex_numbers.pop()


def normalize_ball_name(ball_name: str) -> str:
    if " " in ball_name or not ball_name.lower().endswith(BALL_KEYWORD):
        return ball_name

    prefix = ball_name[: -len(BALL_KEYWORD)].strip()
    return f"{prefix} Ball" if prefix else ball_name


def classify_pokeball(normalized: str) -> Classification | None:
    ball_segments = [
        segment.strip()
        for segment in SEGMENT_SEPARATOR_PATTERN.split(normalized)
        if BALL_KEYWORD in segment.lower()
    ]

    if not ball_segments:
        return None

    ball_name = normalize_ball_name(sanitize_path_component(ball_segments[0]))

    if not ball_name:
        return None

    return Classification(
        parts=(POKEBALLS_FOLDER, ball_name),
        note=f"🎱 Pokeball: {ball_name}",
        kind="pokeball",
    )


def classify_variant(pokemon_name: str, base_name: str) -> VariantDecision:
    match = find_base_name(pokemon_name, base_name)

    if match is None:
        return VariantDecision(
            folder=pokemon_name,
            note=f"⚠️  '{pokemon_name}' does not contain '{base_name}', using it as variant folder",
            kind="unmatched",
        )

    prefix = pokemon_name[: match.start]
    suffix = pokemon_name[match.end :]
    matched_name = pokemon_name[match.start : match.end]
    misspelling = matched_name if match.similarity < 1.0 else None
    typo_note = f" (typo '{misspelling}' corrected)" if misspelling else ""

    if not prefix.strip() and not suffix.strip():
        if misspelling:
            return VariantDecision(
                folder="",
                note=f"⚠️  '{misspelling}' looks like a typo of '{base_name}', using base form",
                kind="base",
                misspelling=misspelling,
            )
        return VariantDecision(folder="", note=f"✓ Base form of {base_name}", kind="base")

    if prefix.strip() or not suffix.startswith(" "):
        variant_folder = f"{prefix}{base_name}{suffix}"
    else:
        variant_folder = suffix.strip()

    return VariantDecision(
        folder=variant_folder,
        note=f"🎨 Variant: {variant_folder}{typo_note}",
        kind="variant",
        misspelling=misspelling,
    )


def classify_pokemon(
    dex_number: str, base_name: str, pokemon_name: str, resolved_by_name: bool
) -> Classification:
    variant = classify_variant(pokemon_name, base_name)

    main_folder = f"{dex_number} - {sanitize_path_component(base_name)}"
    parts = (main_folder,)

    if variant.folder:
        sanitized_variant = sanitize_path_component(variant.folder)
        if sanitized_variant:
            parts = (main_folder, sanitized_variant)

    note = variant.note
    if resolved_by_name:
        note = f"⚠️  No dex number, identified by name as {main_folder} ({variant.note})"

    return Classification(
        parts=parts,
        note=note,
        kind=variant.kind,
        misspelling=variant.misspelling,
        resolved_by_name=resolved_by_name,
    )


def classify_name(raw_name: str, dex: dict[str, str]) -> Classification | None:
    normalized = normalize_name(raw_name)

    dex_match = DEX_NUMBER_PATTERN.match(normalized)

    if dex_match:
        dex_number = dex_match.group()
        base_name = dex.get(dex_number)
        if base_name is None:
            return classify_pokeball(normalized)
        after_dex = re.sub(rf"^{dex_number}\s*-?\s*", "", normalized)
        pokemon_name = " ".join(split_name_words(after_dex))
        return classify_pokemon(dex_number, base_name, pokemon_name, resolved_by_name=False)

    pokeball = classify_pokeball(normalized)
    if pokeball is not None:
        return pokeball

    pokemon_name = " ".join(split_name_words(normalized))
    dex_number = find_dex_number_by_name(pokemon_name, dex)
    if dex_number is None:
        return None

    return classify_pokemon(dex_number, dex[dex_number], pokemon_name, resolved_by_name=True)
