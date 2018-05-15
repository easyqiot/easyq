import pymlconf


settings = pymlconf.DeferredConfigManager()


DEFAULT_ADDRESS = 'localhost:1085'

BUILTIN_CONFIGURATION = f'''
server:
  bind: {DEFAULT_ADDRESS}

'''


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

