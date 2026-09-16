import re
from dataclasses import dataclass
from typing import Literal

from .config import POKEBALLS_FOLDER

BALL_KEYWORD = "ball"

ClassificationKind = Literal["base", "variant", "custom_variant", "typo", "pokeball"]

SEGMENT_SEPARATOR_PATTERN = re.compile(r"\s+-\s+")
EXTENSION_PATTERN = re.compile(r"\.([A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*)$")
DEX_NUMBER_PATTERN = re.compile(r"^[0-9]{4}")
INVALID_PATH_CHARS_PATTERN = re.compile(r'[<>:"/\\|?*]')
PROFILE_WORD_PATTERN = re.compile(r"^(AMS|SPLIT|MC|Profile|V[0-9]|w/)", re.IGNORECASE)
FORM_VARIANT_PATTERN = re.compile(
    r"^(Mega|Alolan|Galarian|Hisuian|Paldean|Gmax|Gigantamax)", re.IGNORECASE
)
CUSTOM_VARIANT_PATTERN = re.compile(
    r"(Christmas|Halloween|Female|Male|Shiny|Shadow|NO |Open)", re.IGNORECASE
)


@dataclass(frozen=True)
class Classification:
    parts: tuple[str, ...]
    note: str
    kind: ClassificationKind

    @property
    def relative_path(self) -> str:
        return "/".join(self.parts)


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


def find_base_name(pokemon_name: str, base_name: str) -> re.Match[str] | None:
    return re.search(rf"(?:^|\s){re.escape(base_name)}(?=\s|$)", pokemon_name)


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


def classify_variant(pokemon_name: str, base_name: str) -> tuple[str, str, ClassificationKind]:
    if pokemon_name == base_name:
        return "", f"✓ Base form of {base_name}", "base"

    match = find_base_name(pokemon_name, base_name)

    if match:
        prefix = pokemon_name[: match.start()].strip()
        suffix = pokemon_name[match.end() :].strip()

        if prefix and suffix:
            variant_folder = f"{prefix} {base_name} {suffix}"
        elif prefix:
            variant_folder = f"{prefix} {base_name}" if FORM_VARIANT_PATTERN.match(prefix) else prefix
        else:
            variant_folder = suffix

        return variant_folder, f"🎨 Variant: {variant_folder}", "variant"

    if FORM_VARIANT_PATTERN.match(pokemon_name):
        return pokemon_name, f"🎨 Variant: {pokemon_name}", "variant"

    if CUSTOM_VARIANT_PATTERN.search(pokemon_name):
        return pokemon_name, f"🎨 Custom variant: {pokemon_name}", "custom_variant"

    return (
        "",
        f"⚠️  Name '{pokemon_name}' looks like a typo of '{base_name}', using base form",
        "typo",
    )


def classify_name(raw_name: str, dex: dict[str, str]) -> Classification | None:
    normalized = normalize_name(raw_name)

    dex_match = DEX_NUMBER_PATTERN.match(normalized)
    dex_number = dex_match.group() if dex_match else ""
    base_name = dex.get(dex_number) if dex_number else None

    if base_name is None:
        return classify_pokeball(normalized)

    after_dex = re.sub(rf"^{dex_number}\s*-?\s*", "", normalized)
    pokemon_name = " ".join(split_name_words(after_dex))

    variant_folder, note, kind = classify_variant(pokemon_name, base_name)

    main_folder = f"{dex_number} - {sanitize_path_component(base_name)}"
    parts = (main_folder,)

    if variant_folder:
        sanitized_variant = sanitize_path_component(variant_folder)
        if sanitized_variant:
            parts = (main_folder, sanitized_variant)

    return Classification(parts=parts, note=note, kind=kind)
