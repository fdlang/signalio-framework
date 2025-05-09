from pydantic import BaseModel

class NotificationChannelBaseProperties(BaseModel):
    ...

class TelegramNotificationProperties(NotificationChannelBaseProperties):

    chat_id: str
    token: str