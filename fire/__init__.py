from fire.conf.config import Config, UninitializedConfig

def init(path):
    global config
    config = Config(path)

config = UninitializedConfig()
