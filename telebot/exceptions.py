class APIConnectionError(Exception):
    def __init__(self, *args):
        if len(args) != 0: self.message = args[0]
        else: self.message = 'Can\'t establish internet connection'

    def __str__(self):
        return f'APIConnectionError: {self.message}'
