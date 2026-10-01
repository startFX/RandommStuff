import json
import base64
from random import *
from simple_b64 import *
from pathlib import Path

LANGUAGE = "en_us"
with open("clicker_game.lang." + LANGUAGE + ".json", "r", encoding = "utf-8") as file:
    l = json.load(file)

### CONSTANTS
MENU = l["menu.intro"]
INSTRUCTIONS = l["menu.input_instructions"]
HELP = l["menu.help"]

DATA_SEPARATOR = "|"
FILE_NAME = "clicker_game"
SAVE_FILE_SUFFIX =".save.txt"
CONFIG_FILE_SUFFIX =".config.txt"

UPGRADE_PRICE_MULTIPLIER = 1.175

### Variables

## Save data values
# Statistics
clicks = 0
critical_hits = 0

# Gameplay
click_power = 1
critical_hit_chance = 0.05
critical_hit_base = 8           # Base value for critical hit.
critical_hit_range = 4          # Randomly added value for critical hits.
# A base value of 8 and a range of 4 will result in gains from 8 to 12.

### UPGRADES
upgrades_level = [
    0, # click power
    0, # critical hit
    ]
upgrades_base_price = [
    50,
    250,
]
upgrades_max_level = [
    -1,
    94,
]

### Functions
def load_game():
    with open((FILE_NAME + SAVE_FILE_SUFFIX), "r", encoding = "utf-8") as file:
        encoded_data = file.read()

    decoded_data = base64.b64decode(encoded_data).decode("utf-8")

    return decoded_data

def load_save_data(decoded_data):
    global clicks, critical_hits, upgrades_level

    save_data = json.loads(decoded_data)

    clicks = save_data["clicks"]
    critical_hits = save_data["critical_hits"]
    upgrades_level = save_data["upgrades_level"]

def save_game():
    save_data = {
        "misc.message": "Good job on decoding the save file! Don't use this knowledge to cheat, though. That wouldn't be very cool.",
        "clicks": clicks,
        "critical_hits": critical_hits,
        "upgrades_level": upgrades_level,
    }

    json_string = json.dumps(save_data, indent = 4)

    encoded = base64.b64encode(
        json_string.encode("utf-8")
    ).decode("ascii")

    with open((FILE_NAME+SAVE_FILE_SUFFIX), "w", encoding ="utf-8") as file:
        file.write(encoded)

def save_data_file_exists():
    """
    Checks if the save data text file exists. Returns True or False.
    """
    file_path=Path(__file__).parent/(FILE_NAME+SAVE_FILE_SUFFIX)
    if file_path.is_file():
        return True
    else:
        return False

def calc_increased_upgrade_price(base_price, level):
    """
    Calculates increased upgrade prices based on the upgrade's base price and level, as well as the global upgrade price multiplier.
    :param base_price: The base price of the upgrade to calculate from.
    :param level: The level of the upgrade of which the price is calculated.
    """
    return round(base_price * (UPGRADE_PRICE_MULTIPLIER ** level))

def upgrade_menu():
    """
    Upgrade menu code.
    """
    while True:
        print(l["menu.upgrade.title"])
        for i in range(2):
            print(l["menu.upgrade.upgrades." + str(i)].format(id = i+1) + " - " + l["menu.upgrade.upgrades_info." + str(i)])
            if upgrades_max_level[i] < 0:
                print(l["menu.upgrade.max_level_none.combined"].format(count = upgrades_level[i]))
            else:
                print(l["menu.upgrade.max_level.combined"].format(max = upgrades_max_level[i], count = upgrades_level[i]))
            price = calc_increased_upgrade_price(upgrades_base_price[i], upgrades_level[i])
            print(l["menu.upgrade.click_to_buy"].format(id = i+1, level =upgrades_level[i]+1, cost = price))
        print("") # Separate menu and input
        user_input = input(l["menu.upgrade.input_instructions"])

        if user_input == "":
            break

### Main
print(MENU)
while True:
    print("")
    if clicks == 1:
        print(l["interface.click_count.singular"].format(count = clicks))
    else:
        print(l["interface.click_count.plural"].format(count = clicks))
    if critical_hits == 1:
        print(l["interface.critical_hit_count.singular"].format(count = critical_hits))
    else:
        print(l["interface.critical_hit_count.plural"].format(count = critical_hits))

    user = input(INSTRUCTIONS)
    print("\n\n") # Leave space between turns

    if user == "":
        if random() < critical_hit_chance:
            critical_hits += 1
            temp = randint(critical_hit_base, critical_hit_base + critical_hit_range)
            clicks += temp
            if temp == 1:
                print(l["status.critical_hit.singular"].format(count = temp))
            else:
                print(l["status.critical_hit.plural"].format(count = temp))
        else:
            clicks += click_power
            if click_power == 1:
                print(l["status.click.singular"].format(count = click_power))
            else:
                print(l["status.click.plural"].format(count = click_power))

    elif user.lower() == "h":
        print(HELP)

    elif user.lower() == "s": # Saving game data to save file
        if save_data_file_exists():
            save_game()
            print(l["status.save.data_saved"].format(file = (FILE_NAME+SAVE_FILE_SUFFIX)))
        else:
            save_game()
            print(l["status.save.data_saved_new_file"].format(file = (FILE_NAME+SAVE_FILE_SUFFIX)))

    elif user.lower() == "l": # Loading save data
        if save_data_file_exists():
            print(l["status.load.save_data_found"].format(file = (FILE_NAME+SAVE_FILE_SUFFIX)))
            print(l["status.load.loading"])
            temp = load_game()
            load_save_data(temp)
            print(l["status.load.loaded"].format(file = (FILE_NAME+SAVE_FILE_SUFFIX)))

        # If it doesn't exist
        else:
            print(l["status.load.save_data_not_found"].format(file = (FILE_NAME+SAVE_FILE_SUFFIX)))

    elif user.lower() == "u": # Upgrade menu
        upgrade_menu()
