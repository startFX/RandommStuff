"""Convert between romaji, hiragana and katakana.

A module for Japanese text typed on a Latin keyboard.
It can convert from romaji to hiragana/katakana and back and
has functionality for "live" conversion and includes utilities for working with kana text.

Quick start:
    >>> import romaji_kana
    >>> romaji_kana.romaji_to_kana("konnichiwa")
    'こんにちわ'
    >>> romaji_kana.convert("サクラ")
    'さくら'
    >>> romaji_kana.kana_to_romaji("がっこう")
    'gakkou'

Typing rules for romaji input:
    - "-" gives ー (the long vowel mark).
    - A doubled consonant gives っ ("kk" becomes っ by "k...").
    - "nn" or "n'" both give ん; "nn" before a vowel gives ん followed by an n-syllable.
    - Hepburn (shi, chi, tsu) and Nihon-shiki (si, ti, tu) spellings both work.
    - Anything that isn't romaji (kana, digits or punctuation) is left unchanged.

Command line support:
    python romaji_kana.py                       interactive converter
    python romaji_kana.py sakura --katakana     one-off conversion
"""

from __future__ import annotations

import sys

__version__ = "1.0.0"

__all__ = ["romaji_to_kana", "kana_to_romaji", "romaji_to_kana_partial", "convert",
           "is_kana", "split_kana", "is_hiragana", "is_katakana", "to_hiragana",
           "to_katakana", "has_ascii_letters", "same_reading", "morae",
           "LONG_MARK", "SOKUON"]

LONG_MARK = "ー"     # Character given when typing '-'
SOKUON = "っ"        # Doubles the next consonant

# Main table
_R = """
a あ|i い|u う|e え|o お
ka か|ki き|ku く|ke け|ko こ
sa さ|shi し|si し|su す|se せ|so そ
ta た|chi ち|ti ち|tsu つ|tu つ|te て|to と
na な|ni に|nu ぬ|ne ね|no の
ha は|hi ひ|fu ふ|hu ふ|he へ|ho ほ
ma ま|mi み|mu む|me め|mo も
ya や|yu ゆ|yo よ
ra ら|ri り|ru る|re れ|ro ろ
wa わ|wo を|wi うぃ|we うぇ
ga が|gi ぎ|gu ぐ|ge げ|go ご
za ざ|ji じ|zi じ|zu ず|ze ぜ|zo ぞ
da だ|di ぢ|du づ|de で|do ど
ba ば|bi び|bu ぶ|be べ|bo ぼ
pa ぱ|pi ぴ|pu ぷ|pe ぺ|po ぽ
kya きゃ|kyu きゅ|kyo きょ
sha しゃ|shu しゅ|sho しょ|she しぇ|sya しゃ|syu しゅ|syo しょ
cha ちゃ|chu ちゅ|cho ちょ|che ちぇ|cya ちゃ|cyu ちゅ|cyo ちょ|tya ちゃ|tyu ちゅ|tyo ちょ
nya にゃ|nyu にゅ|nyo にょ
hya ひゃ|hyu ひゅ|hyo ひょ
mya みゃ|myu みゅ|myo みょ
rya りゃ|ryu りゅ|ryo りょ
gya ぎゃ|gyu ぎゅ|gyo ぎょ
ja じゃ|ju じゅ|jo じょ|je じぇ|jya じゃ|jyu じゅ|jyo じょ|zya じゃ|zyu じゅ|zyo じょ
dya ぢゃ|dyu ぢゅ|dyo ぢょ
bya びゃ|byu びゅ|byo びょ
pya ぴゃ|pyu ぴゅ|pyo ぴょ
fa ふぁ|fi ふぃ|fe ふぇ|fo ふぉ
tsa つぁ|tsi つぃ|tse つぇ|tso つぉ
thi てぃ|thu てゅ|dhi でぃ|dhu でゅ
va ゔぁ|vi ゔぃ|vu ゔ|ve ゔぇ|vo ゔぉ
ye いぇ
xa ぁ|xi ぃ|xu ぅ|xe ぇ|xo ぉ|la ぁ|li ぃ|lu ぅ|le ぇ|lo ぉ
xya ゃ|xyu ゅ|xyo ょ|lya ゃ|lyu ゅ|lyo ょ
xtu っ|xtsu っ|ltu っ|ltsu っ
nn ん|n' ん|xn ん
"""

# Split table into a list of tuples.
# Each tuple has two strings, the second being the hiragana character(s)
# and the first being its romaji equivalent.
ROMAJI_TABLE = []

for _line in _R.strip().splitlines():       # Split by line first
    for _item in _line.split("|"):          # Then by '|'
        _r, _k = _item.split()              # Then by ' '
        ROMAJI_TABLE.append((_r, _k))       # Finally, append tuple to list


_R2K = dict(ROMAJI_TABLE)                           # Build dictionary from table ("Romaji To Kana")
_MAXLEN = max(len(r) for r, _ in ROMAJI_TABLE)      # Store the max length of romaji the code will have to process

_PREFIXES = set()
for _r, _ in ROMAJI_TABLE:                          # For each item,
    for _i in range(1, len(_r)):                    # store its correct incomplete spellings.
        _PREFIXES.add(_r[:_i])                      # shi: s, sh ; tsu: t, ts
_PREFIXES.add("n")                                  # Add 'n' by hand, as it can become ん or na.

_K2R = {}                                           # Build reverse dictionary ("Kana To Romaji")
for _r, _k in ROMAJI_TABLE:                         # For each item
    if _r in ("nn", "n", "xn"):                     # Skip these three
        continue
    _K2R.setdefault(_k, _r)                         # Add to the dictionary in reverse order (kana -> romaji and not romaji -> kana)
_K2R["ん"] = "n"                                    # Add these two manually
_K2R["を"] = "wo"

_VOWELS = "aiueo"                                   # Vowels str
_CONS = set("bcdfghjklmpqrstvwxyz")                 # Consonants set


# Functions: characters and Unicode
def is_hiragana(c: str) -> bool:
    """Return True if `c` is a hiragana (between U+3041 and U+3096)."""
    return "\u3041" <= c <= "\u3096"

def is_katakana(c: str) -> bool:
    """Return True if `c` is a katakana (between U+30a1 and U+30fa)."""
    return "\u30a1" <= c <= "\u30fa"

def to_hiragana(s: str) -> str:
    """Return `s` with every katakana character replaced by hiragana.

    Other characters like romaji are left unchanged.

    >>> to_hiragana("サクラ")
    'さくら'
    """
    return "".join(chr(ord(c) - 0x60) if is_katakana(c) else c for c in s)

def to_katakana(s: str) -> str:
    """Return 's' with every hiragana character replaced by katakana.

    Other characters like romaji are left unchanged.

    >>> to_katakana("さくら")
    'サクラ'
    """
    return "".join(chr(ord(c) + 0x60) if is_hiragana(c) else c for c in s)

# Romaji to Kana algorithm

def romaji_to_kana_partial(text: str, katakana: bool = False) -> tuple[str, str]:
    """Convert romaji to kana partially - convert only what's certain and leave the rest as is.
    Made for real-time typing/partial conversion.

    Args:
        text (str): The text to convert.
        katakana (bool, optional): Whether to convert to katakana
            instead of hiragana or not.

    Returns:
        A tuple (kana, pending). pending is the trailing romaji that
        can still become a syllable. It is "" if everything was
        converted and nothing is undecided.

    >>> romaji_to_kana_partial("kak")
    ('か', 'k')
    >>> romaji_to_kana_partial("hon")
    ('ほ', 'n')
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        lc = c.lower()

        #------------------------- Two blocks: -------------------------#
        # The first turns hyphens (ASCII, full-width or 'ー') into 'ー' #
        # The second leaves any non-English letter unchanged.           #
        #---------------------------------------------------------------#
        if c == "-" or c == "\uff0d" or c == "\u30fc":
            out.append(LONG_MARK)
            i+= 1
            continue
        if not (lc.isascii() or lc.isalpha()):
            out.append(c)
            i += 1
            continue

        #--------------------------------- Look at the lowercased rest of the text with this rule order: ---------------------------------#
        # 1. two equal consonants that aren't 'n' (e.g. 'kk', 'tt')  -> output 'っ', advance one letter                                   #
        # 2. text starting with 'tch'                                -> output 'っ', advance one letter                                   #
        # 3. 'nn' followed by a vowel or 'y'                         -> output 'ん', advance one (the second 'n' starts another syllable) #
        # 4. the rest is exactly nn                                  -> stop (pending)                                                    #
        #---------------------------------------------------------------------------------------------------------------------------------#
        rest = text[i:].lower()
        if len(rest) >= 2 and rest[0] == rest[1] and rest[0] in _CONS and rest[0] != "n":
            out.append(SOKUON)
            i += 1
            continue
        if rest.startswith("tch"):
            out.append(SOKUON)
            i += 1
            continue
        if rest.startswith("nn") and len(rest) >= 3 and rest[2] in _VOWELS + "y":
            out.append("ん")
            i += 1
            continue
        if rest == "nn":
            kana = "".join(out)
            return(to_katakana(kana) if katakana else kana), text[i:]

        matched = False     # This is a flag
        for L in range(min(_MAXLEN, len(rest)), 0, -1):     # Count down from the longest chunk length to 1
            chunk = rest[:L]
            if chunk in _R2K:               # Matched!
                out.append(_R2K[chunk])     # Output
                i += L                      # Advance by L
                matched = True              # Set flag to True
                break
        if matched:                         # If yes match, continue
            continue
        # If no match, treat these three cases in order
        if rest[0] == "n" and len(rest) >= 2:
            if rest[1] not in _VOWELS + "y":
                out.append("ん")
                i += 1
                continue
        if rest in _PREFIXES or (len(rest) == 1 and rest in _CONS):             # prefix/consonant that can still grow
            kana = "".join(out)
            return to_katakana(kana) if katakana else kana, text[i:]
        out.append(c)
        i += 1
    kana = "".join(out)
    return to_katakana(kana) if katakana else kana, ""                          # anything else

def romaji_to_kana(text: str, katakana: bool = False) -> str:
    """Convert romaji to hiragana (or katakana).

    A trailing "n" becomes 'ん'.
    Text that isn't romaji is left unchanged.

    Args:
        text (str): The text to convert.
        katakana (bool, optional): If True, convert into katakana instead of hiragana.

    Returns:
        The converted string.

    >>> romaji_to_kana("konnichiwa")
    'こんにちわ'
    >>> romaji_to_kana("sa-ku-ra", katakana=True)
    'サークーラ'
    >>> romaji_to_kana("sushi 42")
    'すし 42'
    """
    kana, pending = romaji_to_kana_partial(text, katakana)
    if pending:                                         # Simplified writing to check if pending isn't empty
        low = pending.lower()
        if low in ("n", "nn"):                          # A trailing 'n' or 'nn' becomes 'ん'.
            kana += "ん" if not katakana else "ン"
        else:
            kana += pending
    return kana

def has_ascii_letters(s: str) -> bool:
    """Return True if `s` contains at least one plain letter (a-z or A-Z).

    >>> has_ascii_letters("sakura"), has_ascii_letters("さくら")
    (True, False)
    """
    return any(c.isascii() and c.isalpha() for c in s)

def kana_to_romaji(text: str) -> str:
    """Convert hiragana or katakana to romaji with Hepburn-style spelling.

    Args:
        text (str): The text to convert. Can be hiragana or katakana.
                    Other characters are left unchanged.

    Returns:
        The converted string.

    >>> kana_to_romaji("がっこう")
    'gakkou'
    >>> kana_to_romaji("サークーラ")
    'sa-ku-ra'
    """
    text = to_hiragana(text)        # Convert to hiragana first
    out = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == LONG_MARK:          # No need for extra processing
            out.append("-")         # This is a set case
            i += 1
        elif c == "っ":              # Sokuon
            nxt = None
            if i + 1 < n:
                two = text[i + 1:i + 3]
                nxt = _K2R.get(two) or _K2R.get(text[i + 1])
            if nxt and nxt[0] in _CONS:        # Double next consonant
                out.append("t" if nxt.startswith("ch") else nxt[0])
            else:
                out.append("xtu")               # Nothing is after: we append "xtu"
            i += 1
        elif c == "ん":                          # n, n' if before a vowel
            nxt = _K2R.get(text[i + 1:i + 3]) or _K2R.get(text[i + 1:i + 2]) if i + 1 < n else None
            if nxt and (nxt[0] in _VOWELS or nxt[0] == "y" or nxt[0] == "n"):
                out.append("n'")
            else:
                out.append("n")
            i += 1
        else:
            two = text[i:i + 2]
            if len(two) == 2 and two in _K2R:   # Known combination
                out.append(_K2R[two])
                i += 2
            elif c in _K2R:                     # One kana
                out.append(_K2R[c])
                i += 1
            else:                               # Unknown character
                out.append(c)
                i += 1
    return "".join(out)

def is_kana(text: str, allow: str="") -> bool:
    """Return True if `text` is made only of kana and isn't empty.
    Hiragana, katakana and the long mark ('ー') all count as kana.

    Args:
        text: The text to check.
        allow: Extra characters to accept.

    >>> is_kana("さーくー"), is_kana("sa"), is_kana("")
    (True, False, False)
    >>> is_kana("さ く", allow=" ")
    True
    """
    if not text:        # If text is empty
        return False
    return all(is_hiragana(c) or is_katakana(c) or c == LONG_MARK or c in allow for c in text)

def convert(text: str, to: str="hiragana") -> str:
    """Convert text, whether it's in romaji, hiragana or katakana, to a single script.

    Args:
        text: Romaji, hiragana, katakana, or any mix of them.
        to: The target script. "hiragana", "katakana" or "romaji".

    Returns:
        The converted string.

    Raises:
        ValueError: if `to` is not one of the three targets.

    >>> convert("sakura"), convert("sakura", "katakana")
    ('さくら', 'サクラ')
    >>> convert("さくら", "romaji")
    'sakura'
    """
    if to == "romaji":
        return kana_to_romaji(text)
    if to == "katakana":
        return to_katakana(romaji_to_kana(text, katakana=True))
    if to == "hiragana":
        return to_hiragana(romaji_to_kana(text))
    raise ValueError('to must be "hiragana", "katakana" or "romaji"')

_SMALL = set("ゃゅょぁぃぅぇぉゎャュョァィゥェォヮ")

def split_kana(text: str) -> list[str]:
    """Split kana text into morae, with each taking up one list entry.

    Small kana (ゃ, ゅ, ょ, ぁ...) join the previous kana.
    ー, っ and ん each take up an entry of their own.

    >>> split_kana("きゃくせん")
    ['きゃ', 'く', 'せ', 'ん']
    >>> split_kana("がっこう")
    ['が', 'っ', 'こ', 'う']
    """
    out = []
    for c in text:
        if c in _SMALL and out and out[-1] not in (LONG_MARK, SOKUON, "ッ"):      # Small kana join the previous entry
            out[-1] += c
        else:
            out.append(c)
    return out

def same_reading(a: str, b: str) -> bool:
    """Returns True if `a` and `b` are read the same, regardless of the script they're in.

    Args:
        a: String to compare b to.
        b: String to compare to a.

    Returns:
        True if `a` and `b` are read the same.

    >>> same_reading("kyakusen", "きゃくせん"), same_reading("sakura", "がっこう")
    (True, False)
    """
    return convert(a) == convert(b)

def morae(text: str) -> int:
    """Count how many morae are in a text composed of any script.

    Args:
        text: The text to count the amount of morae of. Can be hiragana, katakana or romaji.

    Returns:
        How many morae are in the given text.

    >>> morae("haiku"), morae("mizu no oto"), morae("wagahai ha neko de aru")
    (3, 5, 10)
    >>> morae("さくららら")
    5
    """
    return len(split_kana(convert(text.replace(" ", ""))))      # Remove spaces just in case



def _roundtrip_ok(text: str) -> bool:
    """Test if some romaji text stays the same after being converted to kana and back."""
    return kana_to_romaji(romaji_to_kana(text)) == text

def _main(argv):
    """Command line tool."""
    katakana = "--katakana" in argv
    args = [a for a in argv if a != "--katakana"]
    if args:
        print(romaji_to_kana(" ".join(args), katakana))
        return
    print("romaji_kana - type romaji to get kana, or kana to get romaji. Ctrl+C to quit.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if has_ascii_letters(line) or "-" in line:
            print("  kana  :", romaji_to_kana(line, katakana))
        else:
            print("  romaji:", kana_to_romaji(line))


if __name__ == "__main__":      # Only True when ran. False when imported
    _main(sys.argv[1:])
