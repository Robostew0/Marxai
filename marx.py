import requests
import json
import time
import os
from pyt2s.services import stream_elements
from pygame import mixer
import threading

# For personal use with marx ollama model
with open("settings.json", "r") as file:
    settings = json.load(file)

    url = settings["url"]
    streamMode = settings["stream"]
    model = settings["model"]
    endTokens = settings["endtokens"]
    temperature = settings["creativity"]
    if settings["voice"] == 1:
        voice = "Hans"
    else:
        voice = "de-DE-Wavenet-B"

messages = []

def playSounds(soundsList):
    mixer.init()
    soundsPlayed = 0
    play = True
    while play:
        while soundsPlayed == len(soundsList):
            time.sleep(0.1)
        if soundsList[soundsPlayed] == "done":
            break
        soundsList[soundsPlayed].play()
        while mixer.get_busy():
            time.sleep(0.1)
        soundsPlayed+=1

def chatbotStream(body):
    with requests.post(url, json=body, stream=streamMode) as response:
        if streamMode == False:
            # If not streaming, simply print the response
            token = response.json()["message"]["content"]
            yield token
            return
        # If streaming, construct a series of dictionaries from the stream and print the response of each dictionary
        section = ""
        chunkBytes = b""
        for chunk in response.iter_content():
            # Try to decode the character in the stream and append it to the running section
            chunkBytes = chunkBytes + chunk
            try:
                character = chunkBytes.decode('utf-8')
                chunkBytes = b""
                section = section + character
                # If it's a newline, a new json object has begun and the token can be printed
                if character == '\n':
                    content = json.loads(section)
                    token = content["message"]["content"]
                    section = ""
                    yield token
            except:
                pass

print("\nEnter \"quit\" to exit\nChatting with Karlie\n...")
while True:

    prompt = input("Prompt: ")
    if prompt == "quit":
        break
    
    messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Construct body of request
    body = {
        "model": model,
        "messages": messages,
        "stream": streamMode,
        "options": {
            "seed": round(time.time()),
            "temperature": temperature
        }
    }

    mixer.init()

    textStream = chatbotStream(body)
    fullMessage = ""
    tokenBuffer = ""

    sound = 0
    sounds = []

    thread = threading.Thread(target=playSounds, args=(sounds,))
    thread.start()

    for token in textStream:
        tokenBuffer = tokenBuffer + token
        fullMessage = fullMessage + token
        print(token, end="", flush=True)
        if token in endTokens or streamMode == False:
            sound+=1
            data = stream_elements.requestTTS(text=tokenBuffer, voice=voice)  #de-DE-Standard-B
            try:
                os.remove(f"ttsSound{sound}.mp3")
            except:
                pass

            with open(f"ttsSound{sound}.mp3", 'wb') as file:
                file.write(data)
                try:
                    sounds.append(mixer.Sound(f"ttsSound{sound}.mp3"))
                except:
                    pass
            os.remove(f"ttsSound{sound}.mp3")

            tokenBuffer = ""

    sounds.append("done")

    # Add the whole message to the history
    messages.append(
        {
            "role": "assistant",
            "content": fullMessage 
        }
    ) 

    print("\n")
