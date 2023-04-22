class ConfigError(Exception):
    """Base class for config exceptions"""


class FieldsMissing(ConfigError):
    """Not all fields specified in config or file not exists"""
