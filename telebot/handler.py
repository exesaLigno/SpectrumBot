from typing import Callable, Any, Type

class Handler:
    def __init__(self, handler: Callable, additional: bool = False, **rules):
        self.__handler: Callable = handler
        if len(self.__annotations__) == 0:
            raise ValueError(f'Function {self.__name__}() must have type annotation')
        
        self.__rules = rules
        self.__additional = additional


    def __call__(self, *args, **kwargs):
        correct, reason = self.__checkTypesCorrespondence(*args, **kwargs)
        if not correct:
            #raise ValueError(reason)
            pass
        self.__handler(*args, **kwargs)


    def __checkTypesCorrespondence(self, *args: list[Any], **kwargs: dict[str, Any]) -> tuple[bool, str | None]:

        handler_args = list(self.__annotations__.keys())
        if 'return' in handler_args:
            handler_args.remove('return')
        handler_args_len = len(handler_args)
        given_args_len = len(args) + len(kwargs.keys())

        # Checking args count
        if given_args_len > handler_args_len:
            return False, f'Function {self.__name__}() takes {handler_args_len} arguments but {given_args_len} were given'

        # Checking positional arguments
        for narg, arg in enumerate(args):
            arg_name = handler_args.pop(0)
            if not isinstance(arg, self.__annotations__[arg_name]):
                return False, f'Function {self.__name__}() takes {self.__className(self.__annotations__[arg_name])} as argument {arg_name} (position {narg + 1}) but {self.__className(type(arg))} was given'
        
        # Checking named arguments (also checking if this argument was already 
        # passed throw positional arguments)
        for arg_name, arg in list(kwargs.items()):
            if arg_name not in self.__annotations__.keys():
                return False, f'Function {self.__name__}() has no argument {arg_name}'

            elif arg_name not in handler_args:
                return False, f'Function {self.__name__}() was already gotten {arg_name} as positional argument'

            elif not isinstance(arg, self.__annotations__[arg_name]):
                return False, f'Function {self.__name__}() takes {self.__className(self.__annotations__[arg_name])} as argument {arg_name} but {self.__className(type(arg))} was given'

        return True, None
    

    def correspondesToTypes(self, *args: list[Any], **kwars: dict[str, Any]) -> bool:
        correct, _ = self.__checkTypesCorrespondence(*args, **kwars)
        return correct
    

    @property
    def __annotations__(self) -> dict[str, Any]:
        return self.__handler.__annotations__
    

    @property
    def __name__(self) -> str:
        return self.__handler.__name__
    

    def __str__(self) -> str:

        args: list[str] = []
        ret: str | None = None

        for arg, type in self.__annotations__.items():
            if arg != 'return':
                args.append(f'{arg}: {self.__className(type)}')
            else:
                ret = self.__className(type)

        args_str = ', '.join(args)
        ret_str = '' if ret is None else f' -> {ret}'
        
        return f'<function {self.__name__}({args_str}){ret_str}>'
    
    
    @staticmethod
    def __className(cls: Type | None):
        if cls is None:
            return 'None'
        else:
            return cls.__name__


    def correspondesToRules(self, properties: dict[str, Any]) -> tuple[bool, int]:
        used_rules = 0
        correspondes = True
        for rule_name in self.__rules:
            if rule_name in properties:
                if self.__rules[rule_name] != properties[rule_name]:
                    correspondes = False
                    break
                used_rules += 1
        
        return correspondes, used_rules
    
    @property
    def isAdditional(self) -> bool:
        return self.__additional

