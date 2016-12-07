import os
import sys
import json
import random
import requests
from flask import Flask, request

app = Flask(__name__)

# Fuck prithaj

#mssg_array=["Fuck StackOverflow","I hate Java, do you?","JavaScript is awesome","Who uses IRC anymore tbh","Windows should be illegal"]
msg_array={"projects":"We worked on an online whiteboard last semester","hey":"Hello!","thnx":"No problem","when":"We meet at wednesdays at 5 PM at Au Sable","count":"We have around 20 members","prez":"Prithaj","vprez":"Alex"}


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = str(messaging_event["message"]["text"])  # the message's text

                    if ("when" in message_text) or ("When" in message_text):
                        send_message(sender_id, msg_array["when"])
                    
                    elif "vice" in message_text:
                        send_message(sender_id, msg_array["vprez"])
                    
                    elif "president"in message_text:
                        send_message(sender_id, msg_array["prez"])
                    
                    elif "many" in message_text:
                        send_message(sender_id, msg_array["count"])
                    elif "hey" in message_text:
                        send_message(sender_id,msg_array["hey"])

                    elif ("thanks" in message_text) or ("Thanks" in message_text) or ("Thank you" in message_text):
                        send_message(sender_id,msg_array["thnx"])
                    elif "project" in message_text:
                        send_message(sender_id,msg_array["projects"])

                    else:
                        send_message(sender_id,"I didn't get that. Could you repeat that please?")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):
    

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)
