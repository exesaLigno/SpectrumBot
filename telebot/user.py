from typing import Any
from telebot.abstract import Serializable, DBSerializable

class User(DBSerializable, Serializable):

    def tryLoad(self):
        return super().tryLoad(uid=self.uid)

    def save(self):
        super().save(uid=self.uid)

    def update(self):
        super().update(uid=self.uid)

    def __setattr__(self, __name: str, __value: Any) -> None:
        self.__dict__[__name] = __value
        if self.serialization: self.update()

    def __repr__(self):
        return self.__dict__.__repr__()
    
    def __init__(self, uid: int):

        super().__init__(uid='TEXT PRIMARY KEY', last_message_id='TEXT',
                         _User__window='TEXT', _User__scaling='TEXT', _User__limits='TEXT')

        self.uid = uid
        
        self.last_message_id = None

        self.__window = 'hann'
        self.__scaling = 'auto'
        self.__limits = 'auto'

        if not self.tryLoad():
            self.save()

        self.beginSerialization()

    @property
    def window(self) -> str:
        if self.__window == 'hann': return 'Окно Ханна'
        else: return 'Неизвестный тип окна'

    @property
    def scaling(self) -> str:
        if self.__scaling == 'auto': return 'Автоматически'
        elif self.__scaling == 'linear': return 'Линейная шкала'
        elif self.__scaling == 'logarithmic': return 'Логарифмическая шкала'
        else: return 'Неизвестный тип шкалы'

    @property
    def limits(self) -> str:
        if self.__limits == 'auto': return 'Автоматически'
        elif self.__limits == 'fit_to_data': return 'Обрезка по данным'
        elif self.__limits == 'full': return 'Обрезка отключена'
        else: return 'Неизвестный тип обрезки'


