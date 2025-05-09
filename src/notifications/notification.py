from .interfaces.notification_channel import INotificationChannel
from .properties.properties import TelegramNotificationProperties, NotificationChannelBaseProperties
from .channles.telegram_notification_channel import TelegramNotificationchannel

class NotificationService():

    def __init__(self, properties: NotificationChannelBaseProperties) -> None:
        self._channel = self._get_channel(properties)


    def _get_channel(self, properties: NotificationChannelBaseProperties):

        if isinstance(properties, TelegramNotificationProperties):
             return TelegramNotificationchannel(properties)
        else:
            raise Exception(f"ERROR NotificationService: No existe comunicación con el canal.")
            

    def send_notification(self, tittle: str, message: str):
        self._channel.send_message(tittle, message)