from fire.conf.model import Config

class UninitializedConfig:
    def __getattr__(self, name):
        def method(*args, **kwargs):
            raise RuntimeError("Module not initialized: call fire.init() must be called")
        return method

config = UninitializedConfig()

def init(path):
    global config
    config = Config(path)
