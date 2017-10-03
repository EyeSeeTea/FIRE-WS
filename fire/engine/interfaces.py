from abc import ABCMeta, abstractmethod

class AuthInterface:
    __metaclass__ = ABCMeta

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_password(self, username):
        """Return plain password for some user."""
        raise NotImplementedError

    @abstractmethod
    def add_user(self, username, password):
        """Create a new user given a username/password pair.

        Return True on success, False on failure."""
        raise NotImplementedError
