from src.notifications.interfaces.notification_channel import INotificationChannel
from src.notifications.properties.properties import TelegramNotificationProperties
import telegram
import asyncio


class TelegramNotificationchannel(INotificationChannel):

    def __init__(self, properties: TelegramNotificationProperties) -> None:

        self._chat_id = properties.chat_id
        self._token = properties.token
        self._bot = telegram.Bot(self._token)


    async def async_send_message(self, tittle: str, message: str):
        async with self._bot:
            await self._bot.send_message(text=f"{tittle}\n{message}", chat_id=self._chat_id, parse_mode="HTML")


    def send_message(self, tittle, message):
        asyncio.run(self.async_send_message(tittle, message))