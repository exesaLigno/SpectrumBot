from telebot.abstract import TextPreprocessor, KeyboardPreprocessor
from telebot.api import TelegramAPI
from telebot.logger import Logger
from telebot.user import User
from telebot.events import Message
from telebot.handler import Handler
from netifaces import interfaces, ifaddresses, AF_INET
import getpass
from typing import Any, Callable


class TelegramBot(TextPreprocessor, KeyboardPreprocessor, TelegramAPI):

    def __init__(self, token: str):
        TextPreprocessor.__init__(self, 'bot')
        KeyboardPreprocessor.__init__(self, 'bot')
        TelegramAPI.__init__(self, token)
        self.__botname: str | None = None
        self.__name: str | None = None
        self.__polling_offset: int = 0
        self.__event_queue: list[Any] = []
        self.__handlers: list[Handler] = []

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
                event_obj = None
                properties = {}
                if 'message' in event:
                    event_obj = Message(self.token, event['message'])
                    properties = {'type': Message, 'message_type': event_obj.type}
                    if event_obj.isCommand:
                        self.__chooseHandler(properties, event_obj, *event_obj.command)
                    else:
                        self.__chooseHandler(properties, event_obj)
                

                    

    def __chooseHandler(self, properties, *args, **kwargs):
        appropriate_handlers: list[tuple[int, Handler]] = []

        for handler in self.__handlers:
            #correct_types = handler.correspondesToTypes(*args, **kwargs)
            correct_rules, nrules = handler.correspondesToRules(properties)

            if correct_rules:
                appropriate_handlers.append((nrules, handler))

        if len(appropriate_handlers) == 0:
            print('No handler for this event!')
        appropriate_handlers.sort(key=lambda pair: pair[0], reverse=True)
        main_handler = appropriate_handlers[0][1]
        additional_handlers = list(map(lambda handler: handler[1], filter(lambda handler: handler[1].isAdditional, appropriate_handlers[1:])))
        main_handler(*args, **kwargs)
        for additional_handler in additional_handlers:
            additional_handler(*args, **kwargs)


        

    def registerHandler(self, additional: bool = False, **rules) -> Callable:
        def deco(function: Callable) -> Callable:
            self.__handlers.append(Handler(function, additional=additional, **rules))
            return function
        return deco

