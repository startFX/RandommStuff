import json
import base64
from random import *
from pathlib import Path

LANGUAGE = "en_us"
with open("clicker_game.lang." + LANGUAGE + ".json", "r", encoding = "utf-8") as file:
    l = json.load(file)

### CONSTANTS
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
base_click_power = 1

critical_hit_chance = 50
base_critical_hit_chance = 50

critical_hit_base = 8           # Base value for critical hit click bonus.
critical_hit_range = 4          # Randomly added value for critical hit click bonus.

base_critical_hit_base = 8
base_critical_hit_range = 4
# A base value of 8 and a range of 4 will result in gains from 8 to 12.

### UPGRADES
upgrades_level = [
    0, # click power
    0, # critical hit
    0, # critical hit bonus
    ]
upgrades_base_price = [
    50,
    250,
    350,
]
upgrades_max_level = [
    -1,
    20,
    38,
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

def save_data_file_exists():
    """
    Checks if the save data text file exists. Returns True or False.
    """
    file_path=Path(__file__).parent/(FILE_NAME+SAVE_FILE_SUFFIX)
    if file_path.is_file():
        return True
    else:
        return False

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

def save_game_with_status():
    if save_data_file_exists():
        save_game()
        print(l["status.save.data_saved"].format(file = (FILE_NAME + SAVE_FILE_SUFFIX)))
    else:
        save_game()
        print(l["status.save.data_saved_new_file"].format(file = (FILE_NAME + SAVE_FILE_SUFFIX)))

def calc_increased_upgrade_price(base_price, level, multiplier):
    """
    Calculates increased upgrade prices based on the upgrade's base price and level, as well as the global upgrade price multiplier.
    :param base_price: The base price of the upgrade to calculate from.
    :param level: The level of the upgrade of which the price is calculated.
    :param multiplier: The multiplier to use when calculating increased upgrade prices.
    """
    return round(base_price * (multiplier ** (level ** 0.925)))

def upgrade_menu():
    """
    Upgrade menu code.
    """
    global upgrades_level # We need to be able to change this list's contents within this function
    global clicks
    status = l["menu.upgrade.status.none"]
    while True:
        print(l["menu.upgrade.title"]) # "UPGRADE MENU"

        for i in range(len(upgrades_base_price)): # Code uses upgrades base price list to determine how many upgrades are currently in the game
            print(l["menu.upgrade.info"][str(i)]["name_id"].format(id = i+1) + " - " + l["menu.upgrade.info"][str(i)]["flavor"]) # Upgrade ID, name and info
            if upgrades_max_level[i] < 0: # Upgrades max level display. Anything under 0 is marked as not having a limit (e.g. -1)
                print(l["menu.upgrade.max_level_none.combined"].format(count = upgrades_level[i]) + l["menu.upgrade.info"][str(i)]["effect"].format(n = upgrades_level[i]))
            else:
                print(l["menu.upgrade.max_level.combined"].format(max = upgrades_max_level[i], count = upgrades_level[i]) + l["menu.upgrade.info"][str(i)]["effect"].format(n = upgrades_level[i]))
            price = calc_increased_upgrade_price(upgrades_base_price[i], upgrades_level[i], UPGRADE_PRICE_MULTIPLIER) # Calculate price based on formula
            if upgrades_level[i] >= upgrades_max_level[i] >= 0:
                print(l["menu.upgrade.max_level_reached"])
            else:
                print(l["menu.upgrade.click_to_buy"].format(id = i+1, level = upgrades_level[i]+1, cost = price)) # Enter [n] to buy level [x] for [count] clicks

        print(""); print(status); print(l["menu.upgrade.status.click_count"].format(click = clicks)); print("")
        user_input = input(l["menu.upgrade.input_instructions"])

        if user_input == "":
            break # Exit upgrade menu on lack of user input. It is mentioned in the input instruction that leaving the input empty leaves the menu
        else:
            if user_input in [str(i+1) for i in range(len(upgrades_base_price))]: # If user input is in accepted range of "upgrade-buying"
                # If upgrades_base_price has a length of 2, it will check if str(input) is in [1, 2]
                user_b = int(user_input) - 1 # If input is valid, make it into an integer for easier work
                # Check if upgrade limit has been reached:
                if upgrades_level[user_b] >= upgrades_max_level[user_b] >= 0: # If the level of the upgrade is equal to or higher than its max level
                    status = l["menu.upgrade.status.max_level_reached"].format(upgrade = l["menu.upgrade.info"][str(user_b)]["name"])
                else:
                    price = calc_increased_upgrade_price(upgrades_base_price[user_b], upgrades_level[user_b], UPGRADE_PRICE_MULTIPLIER)
                    if clicks >= price:
                        status = l["menu.upgrade.status.level_bought"].format(level = upgrades_level[user_b] + 1, upgrade = l["menu.upgrade.info"][str(user_b)]["name"], cost = price)
                        clicks -= price
                        upgrades_level[user_b] += 1
                    else:
                        status = l["menu.upgrade.status.not_enough_clicks"].format(difference = price - clicks)

def apply_upgrades():
    """
    Dynamically applies upgrades' effects on respective variables.
    """
    global click_power, critical_hit_chance, critical_hit_base
    click_power = base_click_power + upgrades_level[0]
    critical_hit_chance = base_critical_hit_chance + (upgrades_level[1] * 10)
    critical_hit_base = base_critical_hit_base + upgrades_level[2]

### Main
print(l["menu.intro"])
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

    user = input(l["menu.input_instructions"])
    print("\n\n") # Leave space between turns

    if user == "":
        if random() * 1000 < critical_hit_chance:
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

    elif user.lower() == "s": # Saving game data to save file
        save_game_with_status()

    elif user.lower() == "l": # Loading save data
        if save_data_file_exists():
            print(l["status.load.save_data_found"].format(file = (FILE_NAME+SAVE_FILE_SUFFIX)))
            print(l["status.load.loading"])
            temp = load_game()
            load_save_data(temp)
            print(l["status.load.loaded"].format(file = (FILE_NAME+SAVE_FILE_SUFFIX)))
            apply_upgrades()

        # If it doesn't exist
        else:
            print(l["status.load.save_data_not_found"].format(file = (FILE_NAME+SAVE_FILE_SUFFIX)))

    elif user.lower() == "u": # Upgrade menu
        upgrade_menu()
        apply_upgrades()

    elif user.lower() == "h": # Show help
        print(l["menu.help"])

    elif user.lower() == "i": # Show extra info
        print(l["menu.extra_info"])

    elif user.lower() == "-": # Quit game without saving
        print(l["menu.quit_message.no_save"])
        break

    elif user.lower() == "q": # Save and quit game
        save_game_with_status()
        print(l["menu.quit_message"])
        break
