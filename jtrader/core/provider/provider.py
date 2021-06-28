from abc import ABC
from typing import Optional

import discord_notify as dn
from cement.core.log import LogInterface
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from jtrader.core.secrets import SLACK_TOKEN


class Provider(ABC):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            no_notifications: Optional[bool] = False
    ):
        self.is_sandbox = is_sandbox
        self.logger = logger
        self.no_notifications = no_notifications

    @staticmethod
    def chunks(lst, n):
        for item in range(0, len(lst), n):
            yield lst[item:item + n]

    def send_notification(self, message: str, slack_channel: Optional[str] = '#stock-scanner', **kwargs):
        if self.no_notifications:
            return

        client = WebClient(token=SLACK_TOKEN)
        discord_url = None

        if self.is_sandbox:
            slack_channel = '#stock-scanner-dev'
            discord_url = None

        try:
            client.chat_postMessage(channel=slack_channel, text=message, **kwargs)
        except SlackApiError as e:
            print(f"Got an error: {e.response['error']}")

        if discord_url is not None:
            try:
                notifier = dn.Notifier(discord_url)
                notifier.send(message, print_message=False)
            except Exception as e:
                print(f"Got an error: {e.args[0]}")

    def send_slack_file(self, filename, title, channel: Optional[str] = '#stock-scanner', **kwargs):
        client = WebClient(token=SLACK_TOKEN)

        if self.is_sandbox:
            channel = '#stock-scanner-dev'

        try:
            client.files_upload(channels=channel, filename=filename, title=title, **kwargs)
        except SlackApiError as e:
            print(f"Got an error: {e.response['error']}")
