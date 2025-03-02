# This is a Batman RPG RenPy script.rpy file.
# Please remember that RenPy syntax is slightly different than standard Python.
# For instance, for loops do not exist.
# Menu syntax is such as:
# menu:
#     "Menu Title"
#     "First option":
#         #first option function
#     "Second option":
#         #second option function
# The script of the game goes in this file.

# Define characters
define b = Character("Batman")
define a = Character("Alfred")
define com = Character("Commissioner Gordon")
# Add more character definitions as needed

# Define variables (player stats, inventory, etc.)
default player_health = 100
default player_attack = 10
default player_defense = 5
default player_inventory = []
default money = 0

# --- Helper Functions ---
# (These will be defined later, but declare them here for clarity)
init python:
    import random
    import json
    import re

    def show_inventory():
        # Function to display the player's inventory
        ui.interact() # Force immediate update
        return

    def add_item(item):
        # Function to add an item to the inventory
        global player_inventory
        player_inventory.append(item)
        ui.interact() # Force immediate update
        return

    def remove_item(item):
        # Function to remove an item from the inventory
        global player_inventory
        if item in player_inventory:
            player_inventory.remove(item)
        ui.interact() # Force immediate update
        return

    def use_item(item):
        # Function to use an item
        global player_health, player_attack, player_defense, player_inventory
        if item == "Health Pack":
            player_health += 20
            player_inventory.remove(item)
            "You used a Health Pack. Your health is now [player_health]."
        elif item == "Attack Boost":
            player_attack += 5
            player_inventory.remove(item)
            "You used an Attack Boost. Your attack is now [player_attack]."
        elif item == "Defense Boost":
            player_defense += 3
            player_inventory.remove(item)
            "You used a Defense Boost. Your defense is now [player_defense]."
        else:
            "You can't use that item here."
        ui.interact()
        return

    # generate function to make LLM API call within script.
    def generate(system_message, user_message, temp):
        llama_addy = f"http://localhost:9090/v1/chat/completions"
        data = { "model": "llama-3_2-3b-it-q8_0", "messages": [ {"role": "system", "content": system_message}, {"role": "user", "content": user_message}], "temperature": temp, "max_tokens": -1, "stream": False }
        try:
            comment = renpy.fetch(llama_addy, json=data, method="POST", timeout=120, result='json')
            if comment and 'choices' in comment and len(comment['choices']) > 0:
                comment = comment['choices'][0]['message']['content'].strip()
                if "```json" in comment:
                    comment = json.loads(comment.replace('```json', '').replace('```',''))
                else:
                    comment = re.sub(r'^"|"$', '', comment)
                return comment
            else:
                renpy.say(None, "Error: LLM returned an unexpected response.")
                return ""
        except Exception as e:
            renpy.say(None, "Error: Could not connect to LLM.")
            renpy.say(None, str(e))
            return ""

# --- Game Start ---

label start:

    scene bg black # Or a starting background

    "Gotham City. A city shrouded in darkness, both literal and metaphorical."

    b "I am vengeance. I am the night. I am Batman."

    $ health_percentage = int((player_health / 100.0) * 100)
    $ system_message_alfred = "You are Alfred Pennyworth, Bruce Wayne's butler and confidant. You are concerned for Bruce's well-being."
    $ user_message_alfred = f"Alfred, express your concern to Bruce about Bruce's readiness given your health percentage of {health_percentage}%. Respond in one short sentence."
    $ alfred_response = generate(system_message_alfred, user_message_alfred, 0.7)
    if alfred_response:
        a "[alfred_response]"
    else:
        a "Master Bruce, are you certain about this? Your health is at [player_health]."

    menu:
        "What do you say?"
        "I am ready":
            b "I'm ready, Alfred."
            jump gotham_streets

        "I need more time":
            b "I need more time."
            a "Very well, Master Bruce. Rest up."
            jump start

# --- Locations ---

label gotham_streets:
    scene bg gotham_street # Define this background

    "The streets of Gotham are riddled with crime."

    $ random_event = random.randint(1, 3)

    if random_event == 1:
        com "Batman! We need your help! The Joker is causing chaos downtown!"

        menu:
            "What do you do?"
            "Investigate downtown":
                jump downtown

            "Check the rooftops":
                jump rooftops

            "Go to Batcave":
                jump batcave
    else:
        "You encounter a suspicious character lurking in the shadows."

        $ system_message_crime = "You are a game developer designing a Batman RPG."
        $ user_message_crime = "Generate a random crime that a suspicious person might be involved in, in Gotham City. Keep it short."
        $ crime = generate(system_message_crime, user_message_crime, 0.7)

        menu:
            "What do you do?"
            "Question the character":
                $ system_message = "You are Batman, interrogating a criminal in Gotham City. Be terse and to the point."
                $ user_message = f"Ask them what they know about the {crime}."
                $ batman_response = generate(system_message, user_message, 0.7)
                if batman_response:
                    b "[batman_response]"
                    $ system_message = "You are a criminal being interrogated by Batman in Gotham City. You are scared and want to get away. Be terse and to the point."
                    $ user_message = f"Respond to Batman's question, {batman_response}"
                    $ criminal_response = generate(system_message, user_message, 0.7)
                    if criminal_response:
                        "Suspicious Person: [criminal_response]"
                    menu:
                        "What do you do next?"
                        "Continue questioning":
                            $ system_message = "You are Batman, interrogating a criminal in Gotham City. Be terse and to the point."
                            $ user_message = f"The criminals answer was {criminal_response}. Press them for more details."
                            $ batman_response = generate(system_message, user_message, 0.7)
                            if batman_response:
                                b "[batman_response]"
                                $ system_message = "You are a criminal being interrogated by Batman in Gotham City. You are scared and want to get away. Be terse and to the point."
                                $ user_message = f"Respond to Batman's question, {batman_response}"
                                $ criminal_response = generate(system_message, user_message, 0.7)
                                if criminal_response:
                                    "Suspicious Person: [criminal_response]"
                            jump gotham_streets
                        "Let them go":
                            "You decide they are not worth your time and let them go."
                            jump gotham_streets
                else:
                    "Batman remains silent."
                jump gotham_streets

            "Leave the character":
                "You decide to leave the character alone."
                jump gotham_streets

        $ system_message_menu = "You are a game developer designing a Batman RPG. Provide 3-4 menu options for Batman when encountering a suspicious character in Gotham City. The options should be short, and relevant to the situation. Respond in JSON format."
        $ user_message_menu = f"Batman has encountered a suspicious character who may be involved in {crime}."
        $ menu_options = generate(system_message_menu, user_message_menu, 0.7)

        if menu_options:
            python:
                try:
                    if isinstance(menu_options, str):
                        menu_options = json.loads(menu_options)
                    # Create a list to store the menu options and their corresponding jump labels
                    menu_items = []
                    for i, option in enumerate(menu_options):
                        if isinstance(option, str):
                            # Generate a unique label for each option
                            label_name = f"gotham_streets_option_{i}"
                            # Add the option and label to the list
                            menu_items.append((option, label_name))

                    # Create a list to store the menu options and their corresponding jump labels
                    menu_items = []
                    for i, option in enumerate(menu_options):
                        if isinstance(option, str):
                            # Generate a unique label for each option
                            label_name = f"gotham_streets_option_{i}"
                            menu_items.append((option, label_name))
                        else:
                            menu_items.append(("Invalid Option", "gotham_streets"))

                    # Create the menu dynamically
                except json.JSONDecodeError as e:
                    "Error decoding JSON from LLM: [e]"
                    pass
        else:
            pass
    menu:
        "What do you do?"
        "Leave the character":
            "You decide to leave the character alone."
            jump gotham_streets

    # Define the labels and the actions to take when the options are chosen
    python:
        if 'menu_options' in locals() and menu_options:
            try:
                if isinstance(menu_options, str):
                    menu_options = json.loads(menu_options)
                for i, option in enumerate(menu_options):
                    if isinstance(option, str):
                        label_name = f"gotham_streets_option_{i}"
                        renpy.jump_label(label_name)
                        system_message_option = "You are a game developer designing a Batman RPG."
                        user_message_option = f"The player chose the option {option}.  Write the text that should be displayed when the player chooses that option."
                        option_result = generate(system_message_option, user_message_option, 0.7)
                        if option_result:
                            renpy.say(b, option_result)
                        renpy.jump("gotham_streets")  # Return to the main Gotham Streets menu
            except json.JSONDecodeError:
                pass # Handle the error gracefully, maybe log it

# --- Batcave Location ---
label batcave:
    scene bg batcave_bg

    "You are in the Batcave. What do you want to do?"

    menu:
        "What do you do?"
        "Analyze crime data":
            "You analyze the data and find a clue about the Joker's plan."
            $ add_item("Joker's Clue")
            jump gotham_streets

        "Upgrade bat suit":
            "You upgrade your Bat-Suit, increasing defense."
            $ player_defense += 2
            jump gotham_streets

        "Check inventory":
            $ show_inventory()
            jump batcave

        "Use item":
            $ show_inventory()
            $ item_to_use = renpy.input("Enter the name of the item to use:")
            if item_to_use:
                $ use_item(item_to_use)
            jump batcave

# --- Downtown Location ---
label downtown:
    scene bg downtown_bg

    "Downtown Gotham is in chaos. People are running and screaming."

    "You see the Joker causing mayhem."

    menu:
        "What do you do?"
        "Attack the Joker":
            jump joker_fight

        "Rescue civilians":
            "You rescue some civilians, but the Joker escapes!"
            jump gotham_streets

# --- Rooftops Location ---
label rooftops:
    scene bg rooftops_bg

    "You are on the rooftops of Gotham."

    "You find a thug."

    menu:
        "What do you do?"
        "Question the thug":
            "The thug reveals some information about the Joker's hideout."
            $ add_item("Hideout Location")
            jump gotham_streets

        "Leave the thug":
            "You leave the thug."
            jump gotham_streets

# --- Combat Example ---

label joker_fight:
    scene bg joker_lair

    "You confront the Joker!"

    "The Joker laughs maniacally."

    # Example combat (very basic)
    $ joker_health = 50
    $ joker_attack = 8

    while joker_health > 0 and player_health > 0:
        menu:
            "What do you do?"
            "Attack":
                "You attack the Joker!"
                $ joker_health -= player_attack
                "Joker's health: [joker_health]"
                if joker_health <= 0:
                    jump ending 
                "The Joker attacks you!"
                $ player_health -= joker_attack
                "Your health: [player_health]"
                if player_health <= 0:
                    jump game_over
            "Use batarang":
                if "Batarang" in player_inventory:
                    $ joker_health -= (player_attack + 5)
                    $ remove_item("Batarang")
                    "You throw a Batarang at the Joker!"
                    "Joker's health: [joker_health]"
                else:
                    "You don't have a Batarang!"
                    return

            "Use item":
                $ show_inventory()
                $ item_to_use = renpy.input("Enter the name of the item to use:")
                if item_to_use:
                    $ use_item(item_to_use)
                return

            "Defend":
                "You defend yourself."
                "The Joker attacks you, but you block most of the damage."
                $ player_health -= (joker_attack / 2)
                "Your health: [player_health]"
                if player_health <= 0:
                    jump game_over

    if player_health <= 0:
        "You have been defeated!"
        jump game_over
    else:
        "You have defeated the Joker!"
        jump ending

# --- Ending ---

label ending:
    scene bg gotham_night

    "Gotham is safe... for now."

    b "This city is under my protection."

    return

# --- Game Over ---
label game_over:
    scene bg black
    "Game Over. Batman has fallen."
    return
