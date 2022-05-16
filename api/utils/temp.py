import logging



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

    f_handler.setLevel(logging.DEBUG)
    logger.addHandler(f_handler)

    logger.warning('This is a warning')
    logger.error('This is an error')

    return logger


# logger = get_file_logger('my_logger')
# logger.error('aaa')

import sys
print(sys.stdout)