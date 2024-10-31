import requests
from io import BytesIO
from typing import Any
from json import dumps

class TelegramAPI(object):

    def __init__(self, token: str):
        self.token = token
        self.max_retries = 5

    def __makeRequest(self, method: str, post_arguments: dict[str, Any] = {}, **kwargs):
        arguments = "&".join(map(lambda pair: f"{pair[0]}={pair[1]}", filter(lambda pair: pair[1] != None, kwargs.items())))
        request_string = f'https://api.telegram.org/bot{self.token}/{method}?{arguments}'

        responce = {"connection_established": False, "ok": False}

        for retry in range(self.max_retries):
            try:
                if (len(post_arguments) == 0):
                    responce = requests.get(request_string).json()
                else:
                    responce = requests.post(request_string, files=post_arguments).json()

                responce["connection_established"] = True
                break

            except Exception as error: # [FIX] add normal error handling and logging
                continue

        return responce
    
    def __downloadFile(self, file_path: str):
        request_string = f'https://api.telegram.org/file/bot{self.token}/{file_path}'
        print(request_string)

        responce = {"connection_established": False, "ok": False}

        for retry in range(self.max_retries):
            try:
                result = requests.get(request_string)
                
                responce['ok'] = result.status_code == 200
                responce['connection_established'] = True
                responce['file'] = BytesIO(result.content)
                break

            except Exception as error: # [FIX] add normal error handling and logging
                continue

        return responce
    
    def getFile(self, file_id: str):
        responce = self.__makeRequest('getFile', file_id=file_id)
        if responce['connection_established'] and responce['ok']:
            responce = self.__downloadFile(responce['result']['file_path'])
        if responce['connection_established'] and responce['ok']:
            return responce['file']
        return None
    
    def sendMessage(self, chat_id, text: str | None, photo: BytesIO | bytes | None = None, reply_to: int | None = None):
        reply_params = None
        if reply_to is not None:
            reply_params = dumps({'message_id': reply_to})

        if photo is not None:
            if isinstance(photo, BytesIO):
                photo = photo.read()
            
            return self.__makeRequest('sendPhoto', post_arguments={'photo': photo}, chat_id=chat_id, caption=text, reply_parameters=reply_params)
        
        else:
            return self.__makeRequest('sendMessage', chat_id=chat_id, text=text, reply_parameters=reply_params)
        
    def deleteMessage(self, chat_id, message_id):
        return self.__makeRequest('deleteMessage', chat_id=chat_id, message_id=message_id)
    
    
