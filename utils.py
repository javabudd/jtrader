import os

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def chunks(lst, n):
    for item in range(0, len(lst), n):
        yield lst[item:item + n]


def send_slack_message(message: str):
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

    try:
        client.chat_postMessage(channel='#stonks', text=message)
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")


def send_slack_file(filename, title, **kwargs):
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

    try:
        client.files_upload(channels='#stonks', filename=filename, title=title, **kwargs)
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")
