import requests
import json
from time import sleep

# For personal use with marx ollama model
with open("settings.json", "r") as file:
    settings = json.load(file)

    url = settings["url"]
    streamMode = settings["stream"]
    model = settings["model"]

print("\nEnter \"quit\" to exit\nChatting with Karlie\n...")
while True:

    prompt = input("Prompt: ")
    if prompt == "quit":
        break

    # Construct body of request
    body = {
    "model": model,
    "prompt": prompt,
    "stream": streamMode
    }

    with requests.post(url, json=body, stream=streamMode) as response:

        if streamMode == False:
            # If not streaming, simply print the response
            print(response.json["response"])
        else:
            # If streaming, construct a series of dictionaries from the stream and print the response of each dictionary
            section = ""
            for chunk in response.iter_content():
                try:
                    # Try to decode the character in the stream and append it to the running section
                    character = chunk.decode('utf-8')
                    section = section + character
                    # If it's a newline, a new json object has begun and the token can be printed
                    if character == '\n':
                        content = json.loads(section)
                        print(content["response"], end='', flush=True)     
                        section = ""
                        sleep(0.01)
                except:
                    # Ignore bad characters
                    pass

    print("\n")
