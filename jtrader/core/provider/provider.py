import os
from abc import ABC, abstractmethod
from typing import Optional

from cement.core.log import LogInterface
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


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

        self.client_prop = None

    @property
    def client(self):
        if self.client_prop is None:
            raise RuntimeError

        return self.client_prop

    @abstractmethod
    def chart(self, stock: str, timeframe: str) -> dict:
        pass

    @abstractmethod
    def symbols(self) -> dict:
        pass

    @staticmethod
    def chunks(lst, n) -> None:
        for item in range(0, len(lst), n):
            yield lst[item:item + n]

    def send_notification(self, message: str, slack_channel: Optional[str] = '#stock-scanner', **kwargs):
        if self.no_notifications:
            return

        client = WebClient(token=os.environ.get('SLACK_TOKEN'))

        if self.is_sandbox:
            slack_channel = '#stock-scanner-dev'

        try:
            client.chat_postMessage(channel=slack_channel, text=message, **kwargs)
        except SlackApiError as e:
            print(f"Got an error: {e.response['error']}")

    def send_slack_file(self, filename, title, channel: Optional[str] = '#stock-scanner', **kwargs):
        client = WebClient(token=os.environ.get('SLACK_TOKEN'))

        if self.is_sandbox:
            channel = '#stock-scanner-dev'

        try:
            client.files_upload(channels=channel, filename=filename, title=title, **kwargs)
        except SlackApiError as e:
            print(f"Got an error: {e.response['error']}")
