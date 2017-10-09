from fire.engine.interfaces import AuthInterface

class AuthTest(AuthInterface):
    def get_password(self, username):
        return "pass"

    def add_user(self, username, password):
        return True
