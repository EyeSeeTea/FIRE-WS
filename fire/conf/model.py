from configobj import ConfigObj

class Config:
    def __init__(self, path):
        self.config = ConfigObj(path)

    def get_sip_host(self):
        return self.config["sip"]["host"]
