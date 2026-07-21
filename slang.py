import random
import re
from typing import Optional, Dict, List

# Simple slang mappings for demonstration. Expand as needed.
SLANG_MAP: Dict[str, Dict[str, List[str]]] = {
    "en": {
        "bro": ["twin", "vro", "dawg", "brocaca", "my boy"],
        "you": ["u", "ya"],
        "friend": ["bud", "pal", "homie"],
        "hello": ["yo", "sup", "heyyy"],
        "i am": ["I'm", "imma"],
    },
    "id": {
        "aku": ["gua", "guweh", "gw"],
        "kamu": ["lu", "km"],
        "teman": ["bro", "cuy", "sob"],
        "halo": ["yo", "hai"],
    }
}

# Basic language normalizer
def normalize_language(lang: Optional[str]) -> Optional[str]:
    if not lang:
        return "en"
    lang = lang.lower()
    if any(x in lang for x in ("ind", "id", "indo", "bahasa")):
        return "id"
    if any(x in lang for x in ("eng", "en", "english")):
        return "en"
    return "en"


def _match_case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[0].isupper():
        return replacement.capitalize()
    return replacement


def apply_slang(text: str, lang_key: Optional[str] = "en", probability: float = 0.12) -> str:
    """Randomly substitute words/phrases in `text` with slang variants based on `SLANG_MAP`.

    - `lang_key` selects which slang map to use (e.g., 'en' or 'id').
    - `probability` is the per-match replacement probability.
    """
    if not text or lang_key not in SLANG_MAP:
        return text

    mapping = SLANG_MAP[lang_key]

    # Avoid replacing inside URLs
    url_pattern = re.compile(r"https?://\S+|www\.\S+")

    # Create a list of (start, end) ranges for URLs to skip
    skip_ranges = []
    for m in url_pattern.finditer(text):
        skip_ranges.append((m.start(), m.end()))

    def in_skip(pos: int) -> bool:
        for a, b in skip_ranges:
            if a <= pos < b:
                return True
        return False

    # For each phrase in mapping, do a case-insensitive replacement with word boundaries
    # Sort by length desc so longer phrases match first
    phrases = sorted(mapping.keys(), key=lambda s: -len(s))
    new_text = text

    for phrase in phrases:
        pattern = re.compile(r"\b" + re.escape(phrase) + r"\b", flags=re.IGNORECASE)

        def repl(m: re.Match) -> str:
            # Skip replacements that occur inside URLs
            if in_skip(m.start()):
                return m.group(0)
            if random.random() > probability:
                return m.group(0)
            variants = mapping[phrase]
            choice = random.choice(variants)
            return _match_case(m.group(0), choice)

        new_text = pattern.sub(repl, new_text)

    return new_text
