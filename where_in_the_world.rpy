# The script of the game goes in this file.

define d = Character("Detective")
define s = Character("Seargant")
define w = Character("Witness")

init python:
    import random
    import json
    import re

    def generate(system_message, user_message, temp):
        llama_addy = f"http://localhost.lan:9090/v1/chat/completions"
        data = { "model": "llama-3_2-3b-it-q8_0", "messages": [ {"role": "system", "content": system_message}, {"role": "user", "content": user_message}], "temperature": temp, "max_tokens": -1, "stream": False }
        try:
            comment = renpy.fetch(llama_addy, json=data, method="POST", timeout=120, result='json')
            comment = comment['choices'][0]['message']['content'].strip()
            if "```json" in comment:
                comment = json.loads(comment.replace('```json', '').replace('```',''))
            else:
                comment = re.sub(r'^"|"$', '', comment)
            return comment
        except Exception as e:
            renpy.say(None, "Error: Could not connect to LLM.")
            renpy.say(None, str(e))
            return ""

    GAME_DESIGNER_SYSTEM_MESSAGE = f"You're a game designer for a `Where in the World is Carmen SanDiego` game."

    def call_llm(user_message, temp):
        return generate(GAME_DESIGNER_SYSTEM_MESSAGE, user_message, temp)

    def generate_witness_facts(city, nation):
        user_message = f"Create a cryptic clue about {city}, {nation} that a witness might say. The clue should hint at a famous landmark, cultural aspect, or historical event in the city. Only list one clue with no intro, outro, or explanation or notes."
        temp = 0.5
        clue = call_llm(user_message, temp)
        return clue


# The game starts here.
label start:

    while True:
        #Setup the localLLM call.
        $ user_message = "We need the item that was stolen for this round of the game. List a famous world artifact/monument/etc. that the criminal would have stolen. List only one, this is just for this round. Only list the item with no intro, outro, or explanation or notes. It can include modern or historical items."
        $ temp = 2.0
        $ stolen = call_llm(user_message, temp).replace('.', '')
        $ last_stolen = stolen

        $ user_message = f"The stolen item was {stolen}.  Where is that from?  Only list the nation and city in `City_name, Nation` format."
        $ temp = 0.0
        $ start_location = call_llm(user_message, temp)

        $ user_message = f"List 4 real cities on Earth that the user will need to travel through to find the target. Only list the cities in `City_name, Nation` format, one per line. Do not give any explanation or pre/post text, only the 4 cities. We are already starting from {start_location}, do NOT include that as a city or nation."
        $ temp = 1.0
        $ cities = call_llm(user_message, temp).split('\n')

        "[stolen] from [start_location] was stolen!"
        "You will need to travel through the following cities:"

        $ city_index = 0
        while city_index < len(cities):
            $ city = cities[city_index]
            $ city_name, nation = city.split(', ')
            "[city]"
            $ clue = generate_witness_facts(city_name, nation)
            "Witness: [clue]"
            $ city_index += 1


    # This ends the game.
    return
