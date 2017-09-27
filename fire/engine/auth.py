from fire.drivers.auth.kamailio import AuthKamailio
from fire.drivers.auth.test import AuthTest

AUTH_DRIVERS = {
    "kamailio": AuthKamailio,
    "test": AuthTest,
}

def get_instance(config):
    auth_driver_key = config.get(["drivers", "auth"], default="kamailio")
    class_ = AUTH_DRIVERS.get(auth_driver_key)
    if class_:
        return class_(config)
    else:
        raise RuntimeError("Unknown auth driver: {}".format(auth_driver_key))
