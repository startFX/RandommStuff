from base64 import *
from random import *
from pathlib import Path
import json

LANGUAGE = "en_us"
with open("clicker_game.lang." + LANGUAGE + ".json", "r", encoding = "utf-8") as file:
    l = json.load(file)

### CONSTANTS
MENU = l["menu.intro"]
INSTRUCTIONS = l["menu.input_instructions"]
HELP = l["menu.help"]

DATA_SEPARATOR = "|"
FILE_NAME = "clicker_game"
SAVE_FILE_PREFIX = ".save.txt"
CONFIG_FILE_PREFIX = ".config.txt"

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

# Upgrades
u_click_power = 0

### Functions
def b64_encoded_str(s):
    tmp = b64encode(s.encode("utf-8"))
    return tmp.decode("utf-8")

def b64_decoded_str(s):
    tmp = b64decode(s.encode("utf-8"))
    return tmp.decode("utf-8")

def decode_save_data():
    with open((FILE_NAME + SAVE_FILE_PREFIX), "r", encoding = "utf-8") as save_data_file:
        s = save_data_file.read()
    splut = b64_decoded_str(s).split(DATA_SEPARATOR)
    return splut

def load_decoded_save_data(d):
    global clicks, critical_hits, click_power
    clicks = int(d[0])
    critical_hits = int(d[1])
    click_power = int(d[2])

def save_data():
    to_save = str(clicks) + DATA_SEPARATOR + str(critical_hits) + DATA_SEPARATOR + str(click_power)
    to_save = b64_encoded_str(to_save)
    with open((FILE_NAME + SAVE_FILE_PREFIX), "w", encoding = "utf-8") as save_data_file:
        save_data_file.write(to_save)

def save_data_file_exists():
    file_path=Path(__file__).parent/(FILE_NAME + SAVE_FILE_PREFIX)
    if file_path.is_file():
        return True
    else:
        return False

### Main
print(MENU)
print("")
while True:
    print("")
    if clicks == 1:
        print(l["interface.click_count.singular"].format(count = clicks))
    else:
        print(l["interface.click_count.plural"].format(count = clicks))
    if critical_hits == 1:
        print(l["interface.critical_hit_count.singular"].format(count = clicks))
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
            save_data()
            print(l["status.save.data_saved"].format(file = (FILE_NAME + SAVE_FILE_PREFIX)))
        else:
            save_data()
            print(l["status.save.data_saved_new_file"].format(file = (FILE_NAME + SAVE_FILE_PREFIX)))

    elif user.lower() == "l": # Loading save data
        if save_data_file_exists():
            print(l["status.load.save_data_found"].format(file = (FILE_NAME + SAVE_FILE_PREFIX)))
            print(l["status.load.loading"])
            temp = decode_save_data()
            load_decoded_save_data(temp)
            print(l["status.load.loaded"].format(file = (FILE_NAME + SAVE_FILE_PREFIX)))

        # If it doesn't exist
        else:
            print(l["status.load.save_data_not_found"].format(file = (FILE_NAME + SAVE_FILE_PREFIX)))

    elif user.lower() == "u": # Upgrade menu
        pass