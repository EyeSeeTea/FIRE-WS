from fire.conf.config import Config, UninitializedConfig
from fire.engine import auth as authmod

def load_config(path):
    global config, auth
    config = Config(path)
    auth = authmod.get_instance(config)

config = UninitializedConfig()
auth = None
