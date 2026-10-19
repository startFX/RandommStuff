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
