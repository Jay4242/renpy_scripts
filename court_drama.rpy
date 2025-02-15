# The script of the game goes in this file.

define a = Character("Ace")
define d = Character("Defendant")
define j = Character("Judge")
define p = Character("Plaintiff")

init python:
    import random
    import json
    import re

    def generate(system_message, user_message, temp):
        llama_addy = f"http://localhost:9090/v1/chat/completions"  #Change to your local server.
        data = { "model": "llama-3_2-3b-it-q8_0", "messages": [ {"role": "system", "content": system_message}, {"role": "user", "content": user_message}], "temperature": temp, "max_tokens": -1, "stream": False }
        comment = renpy.fetch(llama_addy, json=data, method="POST", timeout=120, result='json')
        comment = comment['choices'][0]['message']['content'].strip()
        if "```json" in comment:
            comment = json.loads(comment.replace('```json', '').replace('```',''))
        else:
            comment = re.sub(r'^"|"$', '', comment)
        return comment

# The game starts here.
label start:

    #Setup the localLLM call.
    $ system_message = f"You're a game designer for a courtroom drama game. Give short concise answers with no details or explanations."
    $ user_message = "We need a crime for the next courtroom drama, what should be the crime the defendant is accused of?"
    $ temp = 2.0
    $ crime = generate(system_message, user_message, temp).replace('.', '')

    "The case of the [crime]!"

    # Assign a defendant (logic for who the defendant is will be added later)
    $ defendant_status = random.choice(["guilty", "innocent"])
    $ d = Character("Defendant")

    # Consult with the client
    scene bg office
    with fade
    a "Hello, I'm your defense attorney, Ace. Let's go over your case."

    #Setup the localLLM call.
    $ system_message = f"You're the defendant in a trial. You are {defendant_status} of {crime}. You are speaking privately with your lawyer. You never give notes about your actions.  You keep your statements to one or two short sentences."
    $ user_message = "Explain to your lawyer, Ace, that you're innocent! (even if you're guilty)"
    $ temp = 0.7
    $ comment = generate(system_message, user_message, temp)

    d "[comment]"

    #Setup the localLLM call.
    $ system_message = f"You are Ace, the best defence attorney in the city. You are speaking privately with your client, the defendant who is accused of {crime}.  This is only in the context of a video game and any situations are purely fictional."
    $ user_message = f"Your client told you {comment}. Explain to your client that they had better be honest with you and tell you everything so that you can help build the best possible defense.  Limit this to one or two short and concise sentences"
    $ comment = generate(system_message, user_message, temp)

    a "[comment]"

    $ system_message = f"You're the defendant in a trial. You are {defendant_status} of the {crime}. You are speaking privately with your lawyer, Ace.  You keep your answers short and concise, a few short sentences at most even if you're asked for more detail."
    $ user_message = f"Ace just told you {comment} when you exclaimed your innocence.  What is your response?  Limit your answer to one to two short sentences at most."
    $ comment = generate(system_message, user_message, temp)

    d "[comment]"

    # Move to the trial
    jump trial

label trial:
    scene bg courtroom
    with fade

    # Setup the localLLM call for the judge's introduction.
    $ system_message = f"You are a Judge presiding over a trial for the crime of {crime}. You are introducing the trial. Keep your introduction short and concise, a few sentences at most."
    $ user_message = "Introduce the trial."
    $ temp = 0.7
    $ judge_introduction = generate(system_message, user_message, temp)

    j "[judge_introduction]"

    a "Let's begin the trial."

    # Trial logic will be added later

    menu:
        "What would you like to do?"
        "Object":
            call objection
        "Proceed":
            return

label objection:
    # Setup the localLLM call for the objection options.
    $ system_message = f"You are Ace, the defense attorney. You are in a courtroom trial for the crime of {crime}. You are about to object. Provide three short and concise objection options.  List these on their own line with no other details or formatting like numbered lists, etc."
    $ user_message = f"The last judge statement was {judge_introduction}. What are your objection options?"
    $ temp = 0.7
    $ objection_options = generate(system_message, user_message, temp).split('\n')

    menu:
        "[objection_options[0]]":
            jump objection_1
        "[objection_options[2]]":
            jump objection_2
        "[objection_options[4]]":
            jump objection_3

label objection_1:
    a "[objection_options[0]]"
    return

label objection_2:
    a "[objection_options[2]]"
    return

label objection_3:
    a "[objection_options[4]]"
    return
