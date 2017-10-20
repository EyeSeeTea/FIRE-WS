from configobj import ConfigObj

class UninitializedConfig:
    def __getattr__(self, name):
        def method(*args, **kwargs):
            raise RuntimeError("Module not initialized: call fire.load_config() must be called")
        return method

class Config:
    def __init__(self, path):
        self.config = ConfigObj(path)

    def get(self, keys, default=None):
        result = self.config
        for key in keys:
            if key not in result:
                if default is not None:
                    return default
                else:
                    raise ValueError("Cannot get config path: {}".format(keys))
            result = result[key]
        return result
