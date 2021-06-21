class NoDefaultConfigFile(FileNotFoundError):
    """Raise if there is no 'default_config.yaml file in ./source dir"""