# The script of the game goes in this file.

define d = Character("Detective")
define s = Character("Seargant")
define w = Character("Witness")

init python:
    import random
    import json
    import re

    def generate(system_message, user_message, temp):
        llama_addy = f"http://localhost:9090/v1/chat/completions"  #Set local server here.
        data = { "model": "llama-3_2-3b-it-q8_0", "messages": [ {"role": "system", "content": system_message}, {"role": "user", "content": user_message}], "temperature": temp, "max_tokens": -1, "stream": False }
        comment = renpy.fetch(llama_addy, json=data, method="POST", timeout=120, result='json')
        comment = comment['choices'][0]['message']['content'].strip()
        if "```json" in comment:
            comment = json.loads(comment.replace('```json', '').replace('```',''))
        else:
            comment = re.sub(r'^"|"$', '', comment)
        return comment

    def generate_witness_facts(city, nation):
        system_message = f"You're a game designer for a `Where in the World is Carmen SanDiego` game."  #May actually be limiting the bot by mentioning the game...
        user_message = f"Create a fact about {city}, {nation} that a witness might say. Only list one fact with no intro, outro, or explanation or notes."
        temp = 0.5
        fact = generate(system_message, user_message, temp)
        return fact


# The game starts here.
label start:

    while True:
        #Setup the localLLM call.
        $ system_message = f"You're a game designer for a `Where in the World is Carmen SanDiego` game."  #May actually be limiting the bot by mentioning the game...
        $ user_message = "We need the item that was stolen for this round of the game. List a famous world artifact/monument/etc. that the criminal would have stolen. List only one, this is just for this round. Only list the item with no intro, outro, or explanation or notes. It can include modern or historical items."
        $ temp = 2.0
        $ stolen = generate(system_message, user_message, temp).replace('.', '')
        $ last_stolen = stolen

        $ system_message = f"You're a game designer for a `Where in the World is Carmen SanDiego` game."
        $ user_message = f"The stolen item was {stolen}.  Where is that from?  Only list the nation and city in `City_name, Nation` format."
        $ temp = 0.0
        $ start_location = generate(system_message, user_message, temp)

        $ system_message = f"You're a game designer for a `Where in the World is Carmen SanDiego` game."
        $ user_message = f"List 4 real cities on Earth that the user will need to travel through to find the target. Only list the cities in `City_name, Nation` format, one per line. Do not give any explanation or pre/post text, only the 4 cities. We are already starting from {start_location}, do NOT include that as a city or nation."
        $ temp = 1.0
        $ cities = generate(system_message, user_message, temp).split('\n')

        "[stolen] from [start_location] was stolen!"
        "You will need to travel through the following cities:"
        for city in cities:  #This is actually not how you loop through an array in RenPy and needs to be fixed.
            $ city_name, $ nation = city.split(', ')
            "[city]"
            $ fact = generate_witness_facts(city_name, nation)
            "Witness: [fact]"


    # This ends the game.
    return
