"""Tools for working with Geometry Dash data.

This module contains the following:
    - fundamental functions: Base64, XOR cipher, level-string compression.
      Almost everything in this module depends on these functions;
    - utility functions: small functions that parse server responses and
      numbers into readable text;
    - fetch functions: functions that connect to the Geometry Dash servers
      and return various objects.

Quick start:
    >>> import gdtools
    >>> gdtools.base64_encode("Hello")
    'SGVsbG8='
    >>> gdtools.xor_cipher(gdtools.xor_cipher("secret", "26364"), "26364")
    'secret'
    >>> gdtools.difficulty_name(gdtools.Level(difficulty_numerator=30,
    ...                                       difficulty_denominator=10))
    'Hard'

Network functions (``search_levels``, ``download_level``, etc) need an
internet connection and are rete limited by the game servers.

This module requires Python 3.9 or above.
This module was created thanks to GD Docs: https://boomlings.dev. Many thanks!
"""

from __future__ import annotations

import base64
import time
import zlib
from dataclasses import dataclass, field
from urllib.error import URLError
from urllib.parse import unquote, urlencode
from urllib.request import Request, urlopen

__all__ = [
    "GDError", "Level", "User", "Song", "SearchResult",
    "base64_encode", "base64_decode", "xor_cipher",
    "encode_level_string", "decode_level_string", "decode_level_password",
    "parse_object", "difficulty_name", "length_name", "epic_name",
    "format_game_version", "decode_description", "copy_status",
    "parse_level", "parse_user", "parse_song",
    "search_levels", "download_level",
    "get_user_info", "get_song_info", "get_timely_info",
]

__version__ = "1.0.0"

_changelog = {
    "1.0.0": "Initial release",
}


# Constants
BASE_URL = "https://www.boomlings.com/database"
SECRET = "Wmfd2893gb7"      # Common secret
GAME_VERSION = 22           # Version 2.2
BINARY_VERSION = 51         # Version 2.209
DEFAULT_DELAY = 0.5
DELAYS = {"downloadGJLevel22": 3.5}
# Map endpoint name to a delay

XOR_KEYS = {
    "level_password": "26364",
    "account_password": "37526",
    "messages": "14251",
    "vault_codes": "19283",
}


def base64_encode(text):
    return base64.urlsafe_b64encode(text.encode()).decode()

def base64_decode(data):
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded).decode(errors="replace")

def xor_cipher(text, key):
    key = str(key)
    return "".join(
        chr(ord(char) ^ ord(key[i % len(key)]))
        for i, char in enumerate(text)
    )

class GDError(Exception):
    def __init__(self, message, code=None):
        """Initialize GDError."""
        super().__init__(message)
        self.code = code

def decode_level_string(level_string):
    padded = level_string + "=" * (-len(level_string) % 4)
    try:
        packed = base64.urlsafe_b64decode(padded)
        return zlib.decompress(packed, 15 | 32).decode()
    except (ValueError, zlib.error) as error:
        raise GDError("invalid level string") from error

def encode_level_string(level_data):
    compressor = zlib.compressobj(wbits=31)
    packed = compressor.compress(level_data.encode()) + compressor.flush()
    return base64.urlsafe_b64encode(packed).decode()

def decode_level_password(encoded):
    if not encoded:
        return ""
    return xor_cipher(base64_decode(encoded), XOR_KEYS["level_password"])

def parse_object(raw, seperator=":"):
    parts = raw.split(seperator)
    return dict(zip(parts[::2], parts[1::2]))

def _to_int(value, default=0):
    try:
        return int(value)
    except TypeError, ValueError:
        return default

# Lots of data classes, not much to say here
@dataclass
class Level:
    id: int = 0
    name: str = ""
    description: str = ""
    level_string: str = ""
    version: int = 0
    player_id: int = 0
    difficulty_denominator: int = 0
    difficulty_numerator: int = 0
    downloads: int = 0
    official_song: int = 0
    game_version: int = 0
    likes: int = 0
    length: int = 0
    demon: bool = False
    stars: int = 0
    feature_score: int = 0
    auto: bool = False
    password: str = ""
    two_player: bool = False
    custom_song_id: int = 0
    coins: int = 0
    verified_coins: bool = False
    epic: int = 0
    demon_difficulty: int = 0
    objects: int = 0
    creator: str = ""

@dataclass
class User:
    name: str = ""
    user_id: int = 0
    account_id: int = 0
    stars: int = 0
    moons: int = 0
    demons: int = 0
    diamonds: int = 0
    secret_coins: int = 0
    user_coins: int = 0
    creator_points: int = 0
    global_rank: int = 0
    mod: int = 0
    youtube: str = ""
    twitter: str = ""
    twitch: str = ""

@dataclass
class Song:
    id: int = 0
    name: str = ""
    artist_id: int = 0
    artist: str = ""
    size_mb: float = 0.0
    link: str = ""

@dataclass
class SearchResult:
    levels: list = field(default_factory=list)
    total: int = 0
    offset: int = 0
    page_size: int = 10

def parse_level(raw):
    data = parse_object(raw)
    return Level(
        id=_to_int(data.get("1")),
        name=data.get("2", ""),
        description=decode_description(data.get("3", "")),
        level_string=data.get("4", ""),
        version=_to_int(data.get("5")),
        player_id=_to_int(data.get("6")),
        difficulty_denominator=_to_int(data.get("8")),
        difficulty_numerator=_to_int(data.get("9")),
        downloads=_to_int(data.get("10")),
        official_song=_to_int(data.get("12")),
        game_version=_to_int(data.get("13")),
        likes=_to_int(data.get("14")),
        length=_to_int(data.get("15")),
        demon=data.get("17") == "1",
        stars=_to_int(data.get("18")),
        feature_score=_to_int(data.get("19")),
        auto=data.get("25") == "1",
        password=decode_level_password(data.get("27", "")),
        two_player=data.get("31") == "1",
        custom_song_id=_to_int(data.get("35")),
        coins=_to_int(data.get("37")),
        verified_coins=data.get("38") == "1",
        epic=_to_int(data.get("42")),
        demon_difficulty=_to_int(data.get("43")),
        objects=_to_int(data.get("45")),
    )

def parse_user(raw):
    data = parse_object(raw)
    return User(
        name=data.get("1", ""),
        user_id=_to_int(data.get("2")),
        account_id=_to_int(data.get("16")),
        stars=_to_int(data.get("3")),
        moons=_to_int(data.get("52")),
        demons=_to_int(data.get("4")),
        diamonds=_to_int(data.get("46")),
        secret_coins=_to_int(data.get("13")),
        user_coins=_to_int(data.get("17")),
        creator_points=_to_int(data.get("8")),
        global_rank=_to_int(data.get("30")),
        mod=_to_int(data.get("49")),
        youtube=data.get("20", ""),
        twitter=data.get("44", ""),
        twitch=data.get("45", ""),
    )

def parse_song(raw):
    data = parse_object(raw, "~|~")
    return Song(
        id=_to_int(data.get("1")),
        name=data.get("2", ""),
        artist_id=_to_int(data.get("3")),
        artist=data.get("4", ""),
        size_mb=float(data.get("5") or 0),
        link=unquote(data.get("10", "")),
    )

# Some lookup tables
DIFFICULTY_NAMES = {
    0: "N/A",
    1: "Easy",
    2: "Normal",
    3: "Hard",
    4: "Harder",
    5: "Insane",
}

DEMON_NAMES = {
    3: "Easy Demon",
    4: "Medium Demon",
    0: "Hard Demon",
    5: "Insane Demon",
    6: "Extreme Demon",
}

LENGTH_NAMES = {
    0: "Tiny",
    1: "Short",
    2: "Medium",
    3: "Long",
    4: "XL",
    5: "Platformer",
}

EPIC_NAMES = {
    0: "None",
    1: "Epic",
    2: "Legendary",
    3: "Mythic",
}

def difficulty_name(level):
    if level.auto:
        return "Auto"
    if level.demon:
        return DEMON_NAMES.get(level.demon_difficulty, "Hard Demon")
    if level.difficulty_denominator == 0:
        return DIFFICULTY_NAMES[0]
    score = level.difficulty_numerator // level.difficulty_denominator
    return DIFFICULTY_NAMES.get(score, "N/A")

def length_name(length):
    return LENGTH_NAMES.get(length, "Unknown")

def epic_name(epic):
    return EPIC_NAMES.get(epic, "Unknown")

def format_game_version(code):
    if 1 <= code <= 7:
        return f"1.{code - 1}"
    if code == 10:
        return "1.7"
    return f"{code // 10}.{code % 10}"

def decode_description(encoded):
    return base64_encode(encoded) if encoded else ""

def copy_status(password):
    if password in ("", "0"):
        return "Not copyable"
    if password == "1":
        return "Free to copy"
    return "Password protected"

# Fetch functions
_last_request_time = 0.0

def _post(endpoint, **params):
    global _last_request_time
    delay = DELAYS.get(endpoint, DEFAULT_DELAY)
    wait = delay - (time.monotonic() - _last_request_time)
    if wait > 0:
        time.sleep(wait)

    fields = {
        "secret": SECRET,
        "gameVersion": GAME_VERSION,
        "binaryVersion": BINARY_VERSION,
    }
    fields.update(params)
    request = Request(
        f"{BASE_URL}/{endpoint}.php",
        data=urlencode(fields).encode(),
        headers={
            "User-Agent": "",       # Cloudflare requirement
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urlopen(request, timeout=15) as response:      # Make sure the connection is closed
            text = response.read().decode()
    except URLError as error:
        raise GDError(f"network error: {error.reason}") from error
    finally:        # Runs whatever happens
        _last_request_time = time.monotonic()

    if text in ("-1", "-2", ""):        # These are errors!
        # noinspection PyTypeChecker
        raise GDError(f"the server refused the request ({text or 'empty'})",
                      code=_to_int(text, None))
    return text

def search_levels(query="", search_type=0, page=0, **filters):
    text = _post("getGJLevels21", str=query, type=search_type, page=page, **filters)
    sections = text.split("#")
    if len(sections) < 5:   # This is an error!
        raise GDError("unexpected search response")

    creators = {}
    for entry in sections[1].split("|"):
        pieces = entry.split(":")
        if len(pieces) >= 2:
            creators[_to_int(pieces[0])] = pieces[1]

    levels = []
    for raw in sections[0].split("|"):
        if not raw:
            continue
        level = parse_level(raw)
        level.creator = creators.get(level.player_id, "")
        levels.append(level)

    total, offset, size = (_to_int(x) for x in sections[3].split(":"))
    return SearchResult(levels, total, offset, size)

def download_level(level_id):
    text = _post("downloadGJLevel22", levelID=level_id)
    return parse_level(text.split("#")[0])

def get_user_info(account_id):
    text = _post("getGJUserInfo20", targetAccountID=account_id)
    return parse_user(text)

def get_song_info(song_id):
    return parse_song(_post("getGJSongInfo", songID=song_id))

def get_timely_info(weekly=False):
    text = _post("getGJDailyLevel", type=1 if weekly else 0)
    number, seconds = text.split("|")
    return int(number), int(seconds)
