import fire

def application(environ, *args, **kwargs):
    config_file = environ.get("CONFIG_FILE")
    if not config_file:
        raise RuntimeError("CONFIG_FILE environ variable not set")
    fire.load_config(config_file)
    from fire.api.server import app as fire_application
    return fire_application(environ, *args, **kwargs)
