import logging

def first(it):
    return next(it, None)

def merge(d1, d2):
    d3 = d1.copy()
    d3.update(d2)
    return d3

def create_logger(name):
    formatter = logging.Formatter(fmt='[%(levelname)s:%(module)s] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger

logger = create_logger("fire")
