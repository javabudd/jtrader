from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from jtrader.core.secrets import SLACK_TOKEN, IS_SANDBOX


def chunks(lst, n):
    for item in range(0, len(lst), n):
        yield lst[item:item + n]


def send_slack_message(message: str, channel: Optional[str] = '#stock-scanner', **kwargs):
    client = WebClient(token=SLACK_TOKEN)

    if IS_SANDBOX:
        channel = '#stock-scanner-dev'

    try:
        client.chat_postMessage(channel=channel, text=message, **kwargs)
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")


def send_slack_file(filename, title, channel: Optional[str] = '#stock-scanner', **kwargs):
    client = WebClient(token=SLACK_TOKEN)

    if IS_SANDBOX:
        channel = '#stock-scanner-dev'

    try:
        client.files_upload(channels=channel, filename=filename, title=title, **kwargs)
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")
