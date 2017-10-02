import logging
import os
import subprocess

def first(it):
    return next(it, None)

def merge(d1, d2):
    d3 = d1.copy()
    d3.update(d2)
    return d3

def create_logger(name, level=logging.DEBUG, format='[%(levelname)s:%(module)s] %(message)s'):
    formatter = logging.Formatter(fmt=format)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def run(cmd, env=None):
    logger.debug("Run: {}".format(cmd))
    my_env = os.environ.copy()
    for key, value in (env or {}).items():
        my_env[key] = value
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, env=my_env)
    if result.returncode:
        logger.debug("Error, returncode {}:\nstdout={}\nstderr={}".\
            format(result.returncode, result.stdout, result.stderr))
    return result

logger = create_logger("fire")
