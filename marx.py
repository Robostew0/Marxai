import requests
import json
import time

# For personal use with marx ollama model
with open("settings.json", "r") as file:
    settings = json.load(file)

    url = settings["url"]
    streamMode = settings["stream"]
    model = settings["model"]
    endTokens = settings["endtokens"]
messages = []

def chatbotStream(body):
    with requests.post(url, json=body, stream=streamMode) as response:
        message = ""
        if streamMode == False:
            # If not streaming, simply print the response
            token = response.json()["message"]["content"]
            yield token
            return
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
                    token = content["message"]["content"]
                    section = ""
                    yield token
            except:
                # Ignore bad characters
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
        "stream": streamMode
    }


    textStream = chatbotStream(body)
    fullMessage = ""
    tokenBuffer = ""
    for token in textStream:
        tokenBuffer = tokenBuffer + token
        fullMessage = fullMessage + token
        print(token, end="", flush=True)
        if token in endTokens:
            # Do TTS on tokenBuffer here
            tokenBuffer = ""


    # Add the whole message to the history
    messages.append(
        {
            "role": "assistant",
            "content": fullMessage 
        }
    ) 

    print("\n")
