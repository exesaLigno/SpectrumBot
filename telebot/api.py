import requests

class TelegramAPI(object):

    def __init__(self, token: str):
        self.token = token
        self.max_retries = 5

    def __makeRequest(self, method, **kwargs):
        arguments = "&".join(map(lambda pair: f"{pair[0]}={pair[1]}", filter(lambda pair: pair[1] != None, kwargs.items())))
        request_string = f'https://api.telegram.org/bot{self.token}/{method}?{arguments}'

        responce = {"connection_established": False, "ok": False}

        for retry in range(self.max_retries):
            try:
                responce = requests.get(request_string).json()
                responce["connection_established"] = True
                break

            except Exception as error: # [FIX] add normal error handling and logging
                continue

        return responce
