from abc import ABCMeta, abstractmethod

class AuthInterface:
    __metaclass__ = ABCMeta

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_password(self, username):
        raise NotImplementedError
