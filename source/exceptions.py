class NoDefaultConfigFile(FileNotFoundError):
    """ Raise if there is no 'default_config.yaml
    file in ./source dir.
    """


class FailToDeleteFromIndex(Exception):
    """ Document was not deleted from Elasticsearch
    index after appropriate request.
    """


class PartialDeletionError(Exception):
    """ Document deleted in Elasticsearch index
    but did not in database."""


class IdNotDigitError(ValueError):
    """Document id is not convertable to Int."""
