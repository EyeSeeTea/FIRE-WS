import subprocess

from fire.engine.interfaces import AuthInterface
from fire.tools import first, merge, logger, run

class AuthKamailio(AuthInterface):
    def _get_kamailio_password(self):
        return self.config.get(["kamailio", "password"])

    def get_password(self, username):
        default_get_user_cmd = "kamctl show {username}"
        cmd = self.config.get(["kamailio", "get_user"], default_get_user_cmd).format(username=username)
        result = run(cmd)
        if result.returncode == 0:
            return first(
                line.strip().split(":", 1)[1].strip()
                for line in result.stdout.decode("utf8").splitlines()
                if line.lstrip().startswith("password:")
            )

    def add_user(self, username, password):
        default_add_user_cmd = "DBRWPW={kamailio_password} kamctl add {username} {password}"
        kamailio_password = self._get_kamailio_password()
        cmd = self.config.get(["kamailio", "add_user"], default_add_user_cmd).\
            format(kamailio_password=kamailio_password, username=username, password=password)
        result = run(cmd)
        return result.returncode == 0
