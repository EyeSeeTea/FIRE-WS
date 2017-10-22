import logging
import os
import subprocess

import inflection
from marshmallow_sqlalchemy.convert import ModelConverter


def first(it):
    "Return the first element given by an iterator, or None"
    return next(it, None)


def merge(d1, d2):
    "Return a dictionary with the contents of d1 updated by d2"
    d = d1.copy()
    d.update(d2)
    return d


def create_logger(name, level=logging.DEBUG,
                  format='[%(levelname)s:%(module)s] %(message)s'):
    "Return a logger with the given name, level and format"
    formatter = logging.Formatter(fmt=format)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


def run(cmd, env=None):
    "Run a command in a shell, log it and return its result"
    logger.debug("Run: {}".format(cmd))
    my_env = merge(os.environ, env or {})
    result = subprocess.run(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True, env=my_env)
    if result.returncode:
        logger.debug("Error, returncode {}:\nstdout={}\nstderr={}".\
                     format(result.returncode, result.stdout, result.stderr))
    return result


class CamelModelResourceConverter(ModelConverter):
    def _add_column_kwargs(self, kwargs, prop):
        super(CamelModelResourceConverter, self)._add_column_kwargs(kwargs, prop)
        kwargs["load_from"] = inflection.camelize(prop.key, uppercase_first_letter=False)
        kwargs["dump_to"] = inflection.camelize(prop.key, uppercase_first_letter=False)

    def _add_relationship_kwargs(self, kwargs, prop):
        super(CamelModelResourceConverter, self)._add_relationship_kwargs(kwargs, prop)
        kwargs["load_from"] = inflection.camelize(prop.key, uppercase_first_letter=False)
        kwargs["dump_to"] = inflection.camelize(prop.key, uppercase_first_letter=False)
        return


logger = create_logger("fire")
