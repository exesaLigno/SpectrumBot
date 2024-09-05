from telebot.abstract import TextPreprocessor, KeyboardPreprocessor
from telebot.api import TelegramAPI
from telebot.logger import Logger
from telebot.user import User
from telebot.events import Message
from netifaces import interfaces, ifaddresses, AF_INET
import getpass
from typing import Any


class TelegramBot(TextPreprocessor, KeyboardPreprocessor, TelegramAPI):

    def __init__(self, token: str):
        TextPreprocessor.__init__(self, 'bot')
        KeyboardPreprocessor.__init__(self, 'bot')
        TelegramAPI.__init__(self, token)
        self.__botname: str | None = None
        self.__name: str | None = None
        self.__polling_offset: int = 0
        self.__event_queue: list[Any] = []

    @property
    def botname(self):
        if self.__botname == None:
            self.__setMe()
        return self.__botname

    @property
    def name(self):
        if self.__name == None:
            self.__setMe()
        return self.__name

    def __setMe(self):
        bot_info = self.__makeRequest("getMe")

    @property
    def host_ip(self):
        for ifaceName in interfaces():
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
            for addr in addresses:
                if addr != 'No IP addr' and addr != '127.0.0.1':
                    return addr
        return "Unknown IP"

    @property
    def host_username(self):
        return getpass.getuser()
    
    def __getUpdates(self):
        updates = self._TelegramAPI__makeRequest("getUpdates", offset = self.__polling_offset, timeout = 1)

        if updates["ok"] and len(updates["result"]) > 0:
            self.__event_queue += updates["result"]
            self.__polling_offset = updates["result"][-1]["update_id"] + 1

    def polling(self):
        while True:
            self.__getUpdates()
            while len(self.__event_queue) != 0:
                event = self.__event_queue.pop(-1)
                if 'message' in event:
                    self.handleMessage(Message(self.token, event['message']))

    def handleMessage(self, message: Message):
        user = User(message.from_id)
        print(message.type)
        # if message['text'] == '/settings':
        #     pass


