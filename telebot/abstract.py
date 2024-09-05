from types import BuiltinFunctionType, BuiltinMethodType,  FunctionType, MethodType, LambdaType
from typing import Any
from telebot.logger import Logger
from telebot.database import DataBase
import json

class Serializable(object):

    def getField(self, field_name: str) -> any:

        field_value = self.__getattribute__(field_name)

        if isinstance(field_value, (BuiltinFunctionType, BuiltinMethodType,  FunctionType, MethodType, LambdaType)):
            raise AttributeError(f'Attribute \'{field_name}\' is a method')
        
        return field_value


class TextPreprocessor(Serializable):

    def __init__(self, entity_name):
        self.__entity_name = entity_name

    def preprocessText(self, text, **destinations):
        
        for key in list(destinations.keys()):
            if key == self.__entity_name:
                Logger.log(f'WARNING: Destination \'bot\' can not be passed through the parameters')
                destinations.pop(key)
            elif not isinstance(destinations[key], Serializable):
                Logger.log(f'WARNING: Destination \'{key}\' is not Serializable, skipping')
                destinations.pop(key)
        
        preprocessed_text = ''

        destinations[self.__entity_name] = self

        while True:
            oi, ci = text.find('{'), text.find('}')

            if oi == -1 or ci == -1:
                preprocessed_text += text
                break

            clear_text, varspec, text = text[:oi], text[oi+1:ci].split('.'), text[ci+1:]

            if len(varspec) == 1: 
                destination = self.__entity_name
                variable = varspec[0]
            elif len(varspec) == 2:
                destination = varspec[0]
                variable = varspec[1]
            else:
                Logger.log(f'WARNING: Incorrect varspec: \'{varspec}\'')
                destination, variable = None, None

            try:
                preprocessed_text += f'{clear_text}{destinations[destination].getField(variable)}'
            except AttributeError as attribute_exception:
                Logger.log(f'WARNING: Can\'t preprocess text: variable \'{variable}\' is not found in destination object')
                preprocessed_text += f'{clear_text}{{{".".join(varspec)}}}'
            except KeyError as key_error:
                Logger.log(f'WARNING: Can\'t preprocess text: destination object \'{destination}\' does not exist')
                preprocessed_text += f'{clear_text}{{{".".join(varspec)}}}'
        
        return preprocessed_text


class KeyboardPreprocessor(Serializable):

    def __init__(self, entity_name):
        self.__entity_name = entity_name

    def preprocessKeyboard(self, keyboard, **destinations):
        
        for key in list(destinations.keys()):
            if key == self.__entity_name:
                Logger.log(f'WARNING: Destination \'bot\' can not be passed through the parameters')
                destinations.pop(key)
            elif not isinstance(destinations[key], Serializable):
                Logger.log(f'WARNING: Destination \'{key}\' is not Serializable, skipping')
                destinations.pop(key)
        
        preprocessed_text = ''

        destinations[self.__entity_name] = self

        while True:
            oi, ci = text.find('{'), text.find('}')

            if oi == -1 or ci == -1:
                preprocessed_text += text
                break

            clear_text, varspec, text = text[:oi], text[oi+1:ci].split('.'), text[ci+1:]

            if len(varspec) == 1: 
                destination = self.__entity_name
                variable = varspec[0]
            elif len(varspec) == 2:
                destination = varspec[0]
                variable = varspec[1]
            else:
                Logger.log(f'WARNING: Incorrect varspec: \'{varspec}\'')
                destination, variable = None, None

            try:
                preprocessed_text += f'{clear_text}{destinations[destination].getField(variable)}'
            except AttributeError as attribute_exception:
                Logger.log(f'WARNING: Can\'t preprocess text: variable \'{variable}\' is not found in destination object')
                preprocessed_text += f'{clear_text}{{{".".join(varspec)}}}'
            except KeyError as key_error:
                Logger.log(f'WARNING: Can\'t preprocess text: destination object \'{destination}\' does not exist')
                preprocessed_text += f'{clear_text}{{{".".join(varspec)}}}'
        
        return preprocessed_text


class DBSerializable:

    __database__: DataBase = None
    __dict_keys__: list[str] = None

    __buffer__: dict[int, dict[str, Any]] = {}
    __buffer_size__: int = 25

    def __init__(self, **columns):
        if self.__class__.__database__ == None:
            self.__class__.__database__ = DataBase()
            self.__class__.__database__.createTable(self.__class__.__name__, **columns)
            self.__class__.__dict_keys__ = list(columns.keys())

        self.__serialization__ = False

    @staticmethod
    def __queueString(**queue):
        return ', '.join(map(lambda pair: f"{pair[0]}='{pair[1]}'", queue.items()))

    def __tryLoadFromBuffer(self, **queue):
        queue_string = self.__queueString(**queue)
        if queue_string not in self.__buffer__:
            return False

        data = self.__buffer__.pop(queue_string)
        self.__buffer__[queue_string] = data

        for field, value in zip(self.__class__.__dict_keys__, data.values()):
            self.__dict__[field] = value
        
        return True

    def __saveToBuffer(self, **queue):
        queue_string = self.__queueString(**queue)

        if queue_string in self.__buffer__:
            self.__buffer__.pop(queue_string)
        
        self.__buffer__[queue_string] = {field : self.__dict__[field] for field in self.__class__.__dict_keys__}

        self.__deleteExtraBufferEntries()

    def __updateInBuffer(self, **queue):
        self.__saveToBuffer(**queue)

    def __deleteExtraBufferEntries(self):
        if len(self.__buffer__) <= self.__buffer_size__:
            return

        while len(self.__buffer__) > self.__buffer_size__:
            self.__buffer__.pop(list(self.__buffer__.keys())[0])

    def tryLoad(self, **queue):
        if not self.__tryLoadFromBuffer(**queue):
            queue_string = self.__queueString(**queue)
            self.__class__.__database__.cursor.execute(f'SELECT * FROM {self.__class__.__name__}_table WHERE {queue_string};')
            found = self.__class__.__database__.cursor.fetchall()

            if len(found) == 0:
                return False

            found = list(map(lambda elem: json.loads(elem), found[0]))
            for field, value in zip(self.__class__.__dict_keys__, found):
                self.__dict__[field] = value

            self.__saveToBuffer(**queue)
        return True

    def save(self, **queue):
        data = [json.dumps(self.__dict__[field], ensure_ascii=False) for field in self.__class__.__dict_keys__]
        self.__database__.cursor.execute(f'''INSERT INTO {self.__class__.__name__}_table
            ({', '.join(self.__class__.__dict_keys__)})
            VALUES({', '.join(['?'] * len(self.__class__.__dict_keys__))})
        ''', data)
        self.__database__.connector.commit()
        self.__saveToBuffer(**queue)

    def update(self, **queue):
        data = [json.dumps(self.__dict__[field], ensure_ascii=False) for field in self.__class__.__dict_keys__]
        set_list = ',\n'.join(map(lambda key: f'{key} = ?', self.__class__.__dict_keys__))
        self.__database__.cursor.execute(f'''UPDATE {self.__class__.__name__}_table
            SET
                {set_list}
            WHERE
                {self.__queueString(**queue)};
        ''', data)
        self.__database__.connector.commit()
        self.__updateInBuffer(**queue)

    def beginSerialization(self):
        self.__serialization__ = True

    def stopSerialization(self):
        self.__serialization__ = False
    
    @property
    def serialization(self):
        return self.__serialization__
