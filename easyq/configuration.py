import pymlconf


settings = pymlconf.DeferredConfigManager()


BUILTIN_CONFIGURATION = """
server:
  host: localhost
  port: 1085

"""


def configure(*args, **kwargs):
    """ Load configurations

    .. seealso:: `pymlconf Documentations <https://github.com/pylover/pymlconf#documentation>`_

    :param args: positional arguments pass into ``pymlconf.DeferredConfigManager.load``
    :param kwargs: keyword arguments pass into ``pymlconf.DeferredConfigManager.load``
    """
    settings.load(
        *args,
        builtin=BUILTIN_CONFIGURATION,
        missing_file_behavior=pymlconf.IGNORE,
        **kwargs
    )
