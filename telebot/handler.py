from typing import Callable, Any

class Handler:
    def __init__(self, handler: Callable):
        self.__handler: Callable = handler
        self.__name: str = handler.__name__
        self.__annotations: dict[str, Any] = handler.__annotations__


    def __call__(self, *args, **kwargs):
        correct, reason = self.__checkTypesCorrespondence(*args, **kwargs)
        if not correct:
            raise ValueError(reason)
        self.__handler(*args, **kwargs)


    def __checkTypesCorrespondence(self, *args: list[Any], **kwargs: dict[str, Any]) -> tuple[bool, str | None]:

        handler_args = list(self.__annotations.keys())
        if 'return' in handler_args:
            handler_args.remove('return')
        handler_args_len = len(handler_args)
        given_args_len = len(args) + len(kwargs.keys())

        # Checking args count
        if given_args_len > handler_args_len:
            return False, f'Function {self.__name}() takes {handler_args_len} arguments but {given_args_len} were given'

        # Checking positional arguments
        for narg, arg in enumerate(args):
            arg_name = handler_args.pop(0)
            if not isinstance(arg, self.__annotations[arg_name]):
                return False, f'Function {self.__name}() takes {self.__annotations[arg_name].__name__} as argument {arg_name} (position {narg + 1}) but {type(arg).__name__} was given'
        
        # Checking named arguments (also checking if this argument was already 
        # passed throw positional arguments)
        for arg_name, arg in list(kwargs.items()):
            if arg_name not in self.__annotations.keys():
                return False, f'Function {self.__name}() has no argument {arg_name}'

            elif arg_name not in handler_args:
                return False, f'Function {self.__name}() was already gotten {arg_name} as positional argument'

            elif not isinstance(arg, self.__annotations[arg_name]):
                return False, f'Function {self.__name}() takes {self.__annotations[arg_name].__name__} as argument {arg_name} but {type(arg).__name__} was given'

        return True, None
    

    def correspondes(self, *args: list[Any], **kwars: dict[str, Any]) -> bool:
        correct, _ = self.__checkTypesCorrespondence(args, kwars)
        return correct
