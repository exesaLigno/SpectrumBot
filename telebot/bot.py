from telebot.abstract import TextPreprocessor, KeyboardPreprocessor
from telebot.api import TelegramAPI
from telebot.logger import Logger
from telebot.user import User
from telebot.events import Message, Callback, Event
from telebot.handler import Handler
from netifaces import interfaces, ifaddresses, AF_INET
import getpass
from typing import Any, Callable, NoReturn, Self
from threading import Thread
from queue import Queue
import traceback

class TelegramBot(TextPreprocessor, KeyboardPreprocessor, TelegramAPI):

    def __init__(self: Self, token: str):
        TextPreprocessor.__init__(self, 'bot')
        KeyboardPreprocessor.__init__(self, 'bot')
        TelegramAPI.__init__(self, token)
        self.__botname: str | None = None
        self.__name: str | None = None
        self.__polling_offset: int = 0
        self.__queue: Queue[Event] = Queue()
        self.__handlers: list[Handler] = []


    @property
    def botname(self: Self) -> str:
        if self.__botname == None:
            self.getMe()
        return self.__botname


    @property
    def name(self: Self) -> str:
        if self.__name == None:
            self.getMe()
        return self.__name


    def getMe(self: Self) -> None:
        bot_info = super().getMe()
        self.__botname = bot_info['username']
        self.__name = bot_info['first_name']


    @property
    def host_ip(self: Self) -> str:
        for ifaceName in interfaces():
            addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
            for addr in addresses:
                if addr != 'No IP addr' and addr != '127.0.0.1':
                    return addr
        return "Unknown IP"


    @property
    def host_username(self: Self) -> str:
        return getpass.getuser()
    

    def __getUpdates(self: Self) -> None:
        updates = self._TelegramAPI__makeRequest("getUpdates", offset = self.__polling_offset, timeout = 1)

        if updates["ok"] and len(updates["result"]) > 0:
            for event in updates["result"]:
                if 'message' in event:
                    self.__queue.put(Message(self.token, event['message']))
                elif 'callback_query' in event:
                    self.__queue.put(Callback(self.token, event['callback_query']))
                else:
                    print(f'Unsupported event {event}')

            self.__polling_offset = updates["result"][-1]["update_id"] + 1


    def __polling_sync(self: Self) -> NoReturn:
        while True:

            self.__getUpdates()

            if not self.__queue.empty():
                event = self.__queue.get()
                handlers = self.__chooseHandlers(event)

                for handler in handlers:
                    handler(event)


    def __polling_async(self: Self) -> NoReturn:
        pass


    def polling(self, async_run: bool = False, supress_exceptions: bool = False) -> None:
        while True:
            try:
                if async_run:
                    self.__polling_async()
                else:
                    self.__polling_sync()                    
            
            except Exception as error:
                if supress_exceptions:
                    print(f'Error {error} occurred')
                    continue
                else:
                    traceback.print_exc()
                    break
                    

    def __chooseHandlers(self: Self, event: Event) -> list[Handler]:
        appropriate_handlers: list[tuple[int, Handler]] = []

        for handler in self.__handlers:
            correct_rules, nrules = handler.correspondesToRules(event.properties)

            if correct_rules:
                appropriate_handlers.append((nrules, handler))

        if len(appropriate_handlers) == 0:
            return []
        
        appropriate_handlers.sort(key=lambda pair: pair[0], reverse=True)
        main_handler = appropriate_handlers[0][1]
        additional_handlers = list(map(lambda handler: handler[1], filter(lambda handler: handler[1].isAdditional, appropriate_handlers[1:])))

        return [main_handler] + additional_handlers


    def registerHandler(self: Self, additional: bool = False, **rules) -> Callable:
        def deco(function: Callable) -> Callable:
            self.__handlers.append(Handler(function, additional=additional, **rules))
            return function
        return deco

