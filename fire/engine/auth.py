from fire.drivers.auth.kamailio import AuthKamailio
from fire.drivers.auth.test import AuthTest
from fire import config

AUTH_DRIVERS = {
    "kamailio": AuthKamailio,
    "test": AuthTest,
}

def get_instance():
    auth_driver_key = config.get(["drivers", "auth"], default="kamailio")
    class_ = AUTH_DRIVERS.get(auth_driver_key)
    if class_:
        return class_()
    else:
        raise RuntimeError("Unknown auth driver: {}".format(auth_driver_key))
