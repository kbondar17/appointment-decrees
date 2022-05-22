import logging
from threading import local
from typing import Any
from functools import wraps

# from api.config import loggin_level
loggin_level = 'INFO'

def create_logger(name):
    logging.basicConfig(format='LOGGER::%(asctime)s::%(name)s.%(funcName)s::%(levelname)s::%(message)s|')
    logger = logging.getLogger(name)
    logger.setLevel(loggin_level) 
    return logger

    


def get_file_logger(name):
    # Create a custom logger
    logger = logging.getLogger(name)

    # Create handlers
    # c_handler = logging.StreamHandler()
    # c_handler.setLevel(logging.WARNING)

    f_handler = logging.FileHandler('my_logs.log')

    my_format = 'LOGGER::%(name)s.%(funcName)s(line %(lineno)d)::%(levelname)s::%(message)s |'
    f_format = logging.Formatter(my_format)
    f_handler.setFormatter(f_format)

    f_handler.setLevel(logging.INFO)
    logger.addHandler(f_handler)

    return logger


class Log:

    def __init__(self, name) -> None:
        self.name = name
        self.logger = create_logger(name) 
 

    def __call__(self, fun, *args: Any, **kwds: Any) -> Any:        

        @wraps(fun)
        def wrapper(*args: Any, **kwds: Any):
            self.logger.warning('\n\nOK. -- Функция={} -- args={}'.format(fun.__name__,(args, kwds)))
            res = fun(*args, **kwds)
            self.logger.warning('\n\tРезультат функции {}::{}'.format(fun.__name__, res))
            return res

        wrapper.__name__ = fun.__name__
        return wrapper



@Log(__name__)
def my_fun(x, *args, **kwargs):
    print('locals -- ', locals())
    print('args in my fun::',x)
    return 'my_fun result'


# my_fun('my arg')