from pathlib import Path
import yaml

from .exceptions import NoDefaultConfigFile


__all__ = ('load_config')


DEFAULT_CONFIG_FILE_PATH = Path(__file__).resolve().parent / 'default_config.yaml'


def load_config(config_file=None)-> dict:
    """Loads and converts yaml config files and returns it as dicts"""
    
    # load default configuration file first
    try:
        config = yaml.safe_load(DEFAULT_CONFIG_FILE_PATH.open())
    except FileNotFoundError:
        raise NoDefaultConfigFile('Cannot find default_config.yaml:' +
                                  'it should be placed in ./source dir.')

    # overwrite default configs with the values from config_file arg.
    if config_file is not None:
        custom_config = yaml.safe_load(config_file)
        config.update(**custom_config)

    return config
