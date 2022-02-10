from __future__ import annotations

import asyncio
import os
from abc import ABC, abstractmethod
from datetime import datetime
from logging import getLogger
from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Provider(ABC):
    def __init__(self, is_sandbox: bool, no_notifications: Optional[bool] = False):
        self.is_sandbox = is_sandbox
        self.logger = getLogger()
        self.no_notifications = no_notifications

        self.client_prop = None

    @property
    def client(self):
        if self.client_prop is None:
            raise RuntimeError

        return self.client_prop

    @abstractmethod
    def chart(self, stock: str, start: datetime, end: datetime | None) -> dict | list:
        raise NotImplemented

    @abstractmethod
    def economic(self, economic_type: str, timeframe: str, as_dataframe: bool = False):
        raise NotImplemented

    @abstractmethod
    def intraday(self, stock: str) -> dict:
        raise NotImplemented

    @abstractmethod
    def symbols(self) -> dict:
        raise NotImplemented

    @abstractmethod
    async def register_websockets(
            self,
            loop: asyncio.AbstractEventLoop,
            ticker: str,
            on_websocket_message: callable
    ) -> None:
        pass

    @staticmethod
    def chunks(lst, n) -> None:
        for item in range(0, len(lst), n):
            yield lst[item:item + n]

    async def shutdown(self, loop: asyncio.AbstractEventLoop, signal=None) -> None:
        if signal:
            self.logger.info(f"Received exit signal {signal.name}...")

        self.logger.info("Closing connections")

        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]

        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()

    def send_notification(self, message: str, slack_channel: Optional[str] = '#stock-scanner', **kwargs) -> None:
        slack_token = os.environ.get('SLACK_TOKEN')

        if self.no_notifications or slack_token is None:
            return

        client = WebClient(token=slack_token)

        if self.is_sandbox:
            slack_channel = '#stock-scanner-dev'

        try:
            client.chat_postMessage(channel=slack_channel, text=message, **kwargs)
        except SlackApiError as e:
            print(f"Got an error: {e.response['error']}")

    def send_slack_file(self, filename, title, channel: Optional[str] = '#stock-scanner', **kwargs) -> None:
        client = WebClient(token=os.environ.get('SLACK_TOKEN'))

        if self.is_sandbox:
            channel = '#stock-scanner-dev'

        try:
            client.files_upload(channels=channel, filename=filename, title=title, **kwargs)
        except SlackApiError as e:
            print(f"Got an error: {e.response['error']}")

    def handle_websocket_exception(self, loop: asyncio.AbstractEventLoop, context) -> None:
        print('woa')
        msg = context.get("exception", context["message"])
        self.logger.error(f"Caught exception: {msg}")
        self.logger.info("Shutting down...")

        asyncio.create_task(self.shutdown(loop))

    def connect_websocket(self, ticker: str, on_websocket_message: callable) -> None:
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(self.handle_websocket_exception)
        loop.run_until_complete(self.register_websockets(loop, ticker, on_websocket_message))
