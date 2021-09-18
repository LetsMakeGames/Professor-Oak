import json
import openai
import os
import requests
from flask import Flask, request, Response
from re import search

# Load an assign environment variables
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.environ["OPENAI_API_TOKEN"]
api_token = os.environ["SLACK_API_TOKEN"]
openAI_url = "https://api.openai.com/v1/engines/davinci/completions"
defineBot = ("This is a chatbot that imitates Professor Oak the Pokémon professor from the popular TV show and video game franchise. " 
             "Professor Oak is a friendly and intelligent professor that knows everything about Pokémon. "
             "He is never rude and always child-friendly.")

# Initialize Flask app
app = Flask(__name__)

@app.route('/events', methods=['POST'])
def events_handler():

    request_body_json = request.get_json()
        
    if "challenge" in request_body_json:
        # Respond to the challenge
        return Response(request_body_json["challenge"]), 200
    else:
        # Store details about the user
        evt = request_body_json["event"]
        user_id = evt["user"]
        channel_id = evt["channel"]
        text = evt["blocks"][0]["elements"][0]["elements"][1]["text"]

        # Send message to OpenAI
        botResponse = request_completion(text)

        # Build the message payload
        build_message(channel_id, botResponse)
    
    # Return a 200 to the event request
    return Response(status=200)

# Send message to Open AI for completion
def request_completion(text):
    completion = openai.Completion.create(
        engine="davinci",
        prompt=defineBot + "\nUser:" + text + "\nProf. Oak:",
        max_tokens=64,
        temperature=0.5,
        top_p=1,
        n=1,
        stream=False,
        echo=False,
        stop=["User:","\n"]
    )
    response = completion['choices'][0]['text']
    return str(response)

# Build the message payload
def build_message(channel_id, botResponse):
    
    message = [{
        "pretext": botResponse
    }]

    print(message)

    post_update(message, channel_id)

    return

# Post the actual message to a channel
def post_update(attachments, channel_id):
    if len(attachments[0].keys()) > 0:
        data = {
            "token": api_token,
            "channel": channel_id,
            "icon_emoji": ":slack:",
            "text": attachments[0]["pretext"],
            "pretty": True
        }
    else:
        data = {
            "token": api_token,
            "channel": channel_id,
            "icon_emoji": ":slack:",
            "text": "Something went wrong!",
            "pretty": True
        }
        
    try:
        r = requests.post("https://slack.com/api/chat.postMessage", data=data)
        r.raise_for_status()

        # log Slack API responses
        print(r.json())

    except requests.exceptions.HTTPError as err:
        # If there's an HTTP error, log the error message
        print(err)

    return