import subprocess

from fire.engine.interfaces import AuthInterface
from fire.tools import first, merge, logger

class AuthKamailio(AuthInterface):
    def get_password(self, username):
        default_get_user_cmd = "kamctl show {username}"
        cmd = self.config.get(["kamailio", "get_user"], default_get_user_cmd).format(username=username)
        logger.debug("Run: {}".format(cmd))
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if result.returncode:
            logger.debug("Error, returncode {}: {}".format(result.returncode, result.stderr))
            return None
        else:
            return first(
                line.strip().split(":", 1)[1].strip()
                for line in result.stdout.decode("utf8").splitlines()
                if line.lstrip().startswith("password:")
            )
