from typing import Protocol

class INotificationChannel:

    def send_message(self, tittle: str, message: str):
        ...