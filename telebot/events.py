from telebot.api import TelegramAPI
from enum import Enum
from typing import Any, Self


class Message(TelegramAPI):

    class Type(Enum):
        UNKNOWN = 0
        PLAIN_MESSAGE = 1   # Contains only text
        COMMAND = 11        # Contains only text (starting from /)
        VOICE_MESSAGE = 2   # Contains only voice
        VIDEO_MESSAGE = 3   # Contains only video_note
        LOCATION = 4        # Contains only location
        DOCUMENT = 5        # Contains a document and (optional) text
        PHOTO = 6           # Contains a photo and (optional) text
        VIDEO = 7           # Contains a video and (optional) text
        AUDIO = 8           # Contains an audio and (optional) text


    def __init__(self: Self, token: str, message_dict: dict):
        TelegramAPI.__init__(self, token=token)
        self.message_id: int = message_dict['message_id']
        self.from_id: int = message_dict['from']['id']
        self.chat_id: int = message_dict['chat']['id']
        self.timestamp: int = message_dict['date']
        self.type: self.Type = self.Type.UNKNOWN

        self.text: str | None = None
        self.media: Any = None

        if 'text' in message_dict:
            self.type = self.Type.PLAIN_MESSAGE
            self.text = message_dict['text']
            if self.isCommand:
                self.type = self.Type.COMMAND

        elif 'document' in message_dict:
            self.type = self.Type.DOCUMENT
            self.media = message_dict['document']
            if 'caption' in message_dict:
                self.text = message_dict['caption']
        elif 'photo' in message_dict:
            self.type = self.Type.PHOTO
            self.media = message_dict['photo']
            if 'caption' in message_dict:
                self.text = message_dict['caption']
        elif 'video' in message_dict:
            self.type = self.Type.VIDEO
            self.media = message_dict['video']
            if 'caption' in message_dict:
                self.text = message_dict['caption']
        elif 'audio' in message_dict:
            self.type = self.Type.AUDIO
            self.media = message_dict['audio']
            if 'caption' in message_dict:
                self.text = message_dict['caption']

        elif 'voice' in message_dict: 
            self.type = self.Type.VOICE_MESSAGE
            self.media = message_dict['voice']
        elif 'video_note' in message_dict: 
            self.type = self.Type.VIDEO_MESSAGE
            self.media = message_dict['video_note']
        elif 'location' in message_dict:
            self.type = self.Type.LOCATION
            self.media = message_dict['location']

    @property
    def isCommand(self: Self) -> bool:
        return (self.type == self.Type.PLAIN_MESSAGE and 
                self.text is not None and
                self.text[0] == '/')
    
    @property
    def command(self: Self) -> tuple[str, list[str]] | None:
        if self.isCommand:
            parts = self.text.split(' ')
            while ' ' in parts: parts.remove(' ')
            return parts[0], parts[1:]
        else:
            raise AttributeError('This message has no attribute\'command\'', name='command')

