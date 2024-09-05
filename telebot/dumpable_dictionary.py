from typing import Any
import json

class DDict(object):

    def __init__(self, filename: str):
        self.filename = filename
        self.__internal_dict = dict()
        self.__tryload()

    def __getitem__(self, __name: str) -> Any:
        return self.__internal_dict[__name]

    def __setitem__(self, __name: str, value: Any) -> None:
        self.__internal_dict[__name] = value
        self.__dump()

    def __delitem__(self, __name: str) -> None:
        self.__internal_dict.pop(__name)
        self.__dump()

    def __getattr__(self, __name: str) -> Any:
        return self[__name]

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name not in ['filename', '_DDict__internal_dict']:
            self[__name] = __value
        else:
            self.__dict__[__name] = __value

    def __delattr__(self, __name: str) -> None:
        self.__delitem__(__name)

    def __str__(self) -> str:
        return self.__internal_dict.__str__()

    def __repr__(self) -> str:
        return f'{self.__internal_dict.__repr__()} at \'{self.filename}\''

    def __dump(self) -> None:
        with open(self.filename, 'w') as dump_file:
            dump_file.write(json.dumps(self.__internal_dict, indent = 4, ensure_ascii = False))

    def __load(self) -> None:
        with open(self.filename, 'r') as dump_file:
            self.__internal_dict = json.loads(dump_file.read())

    def __tryload(self) -> None:
        try: self.__load()
        except: pass

    def reload(self) -> None:
        self.__load()

    def clear(self) -> None:
        self.__internal_dict.clear()
        self.__load()

    def copy(self):
        raise RuntimeError('Can\'t create a copy of DDict. Create new object with another dump filename.')
    
    def keys(self):
        return self.__internal_dict.keys()

    def values(self):
        return self.__internal_dict.values()

    def items(self):
        return self.__internal_dict.items()

    def __len__(self) -> int:
        return self.__internal_dict.__len__()

    def __sizeof__(self) -> int:
        return self.__internal_dict.__sizeof__()

    def __iter__(self) -> int:
        return self.__internal_dict.__iter__()

    def __reversed__(self) -> int:
        return self.__internal_dict.__reversed__()

    def __contains__(self, __key: str) -> bool:
        return self.__internal_dict.__contains__(__key)
