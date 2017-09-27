from abc import ABCMeta, abstractmethod

class AuthInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_password(self, username):
        raise NotImplementedError
