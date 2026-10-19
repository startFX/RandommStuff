"""Convert between romaji, hiragana and katakana.

(placeholder)
"""

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
    """Return True if c is a hiragana (between U+3041 and U+3096)."""
    return "\u3041" <= c <= "\u3096"

def is_katakana(c: str) -> bool:
    """Return True if c is a katakana (between U+30a1 and U+30fa)."""
    return "\u30a1" <= c <= "\u30fa"

def to_hiragana(s: str) -> str:
    """Return 's' with every katakana character replaced by hiragana.

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
        can still become a syllable. It is "" is everything was
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
        # The first turns hyphens (ASCII, full-width or 'ー') into 'ー"  #
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
        if rest[0] == "n" and len(rest) >= 2 and rest[2] not in _VOWELS + "y":  # n before non-vowel
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
