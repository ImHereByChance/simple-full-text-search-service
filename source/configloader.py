from pathlib import Path
from pyaml_env import parse_config

from .exceptions import NoDefaultConfigFile


__all__ = ('load_config')


DEFAULT_CONFIG_FILE_PATH = Path(__file__).resolve().parent / 'default_config.yaml'


def load_config(config_file=None)-> dict:
    """Loads and converts yaml config files and returns it as dicts"""
    
    # load default configuration file first
    try:
        config = parse_config(DEFAULT_CONFIG_FILE_PATH.as_posix())
    except FileNotFoundError:
        raise NoDefaultConfigFile('Cannot find default_config.yaml:' +
                                  'it should be placed in ./source dir.')

    # overwrite default configs with the values from config_file arg.
    if config_file is not None:
        custom_config = parse_config(config_file)
        config.update(**custom_config)

    return config
