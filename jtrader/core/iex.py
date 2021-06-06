from abc import ABC, abstractmethod
from typing import Optional

import discord_notify as dn
import pyEX as IEXClient
from cement.core.log import LogInterface
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from jtrader.core.secrets import IEX_CLOUD_API_TOKEN, IEX_CLOUD_SANDBOX_API_TOKEN, SLACK_TOKEN


class IEX(ABC):
    def __init__(
            self,
            is_sandbox: bool,
            logger: LogInterface,
            version: Optional[str] = 'stable'
    ):
        self.is_sandbox = is_sandbox
        self.logger = logger

        token = IEX_CLOUD_API_TOKEN
        if self.is_sandbox:
            version = 'sandbox'
            token = IEX_CLOUD_SANDBOX_API_TOKEN

        self.iex_client = IEXClient.Client(token, version)

    @abstractmethod
    def run(self):
        pass

    @staticmethod
    def chunks(lst, n):
        for item in range(0, len(lst), n):
            yield lst[item:item + n]

    def send_notification(self, message: str, slack_channel: Optional[str] = '#stock-scanner', **kwargs):
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
