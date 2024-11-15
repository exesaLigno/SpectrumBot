from enum import Enum
from typing import Any

class Language(Enum):
    RU = 'русский'
    EN = 'english'

class MultilanguageTextStorage:

    def __init__(self, json = None):
        self.default_language = Language.EN
        self.data = {
            'help': {
                Language.RU: 'Это сообщение помощи',
                Language.EN: 'This is help message'
            },
            'settings': {
                Language.RU: 'Настройки',
                Language.EN: 'Settings'
            },
            'test': {
                Language.RU: 'Пиво пиво'
            }
        }

    def __split_name_lang(self, name: str) -> tuple[str, Language]:

        if len(name) >= 3 and name[-3] == '_' and name[-2:].upper() in Language._member_names_:
            ret_lang = Language[name[-2:].upper()]
            ret_name = name[:-3]
        else:
            ret_lang = self.default_language
            ret_name = name
        
        return ret_name, ret_lang
    
    def __get_text(self, name: str, lang: Language) -> str:
        if name not in self.data:
            raise AttributeError(f'There is no entry for name "{name}"', name=name)
        if lang not in self.data[name]:
            raise AttributeError(f'There is no language "{lang}" in "{name}"', name=lang)
        
        return self.data[name][lang]

    def __getattribute__(self, name: str) -> Any:
        print(name)
        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass
        s_name, s_lang = self.__split_name_lang(name)
        return self.__get_text(s_name, s_lang)


if __name__ == "__main__":
    m = MultilanguageTextStorage()
    print(m.help_ru)
    print(m.help_en)
    print(m.help)
    print(m.settings_ru)
    print(m.test_ru)
    print(m.test_en)
