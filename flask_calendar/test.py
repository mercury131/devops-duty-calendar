import os
from slack import WebClient
from slack.errors import SlackApiError

duty = ""
message = "TEST There!"
slackchannel=''
apitoken=''

def send_to_slack(duty,message,slackchannel,apitoken):

    client = WebClient(token=apitoken)

    user = ("<@" + duty + '>')
    allmessage = (user + ' ' +  message)

    try:
        response = client.chat_postMessage(
            channel=('#' + slackchannel),
            text=allmessage)
        response["message"]["text"] == allmessage
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

send_to_slack(duty,message,slackchannel,apitoken)

