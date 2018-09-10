import pymlconf


settings = pymlconf.DeferredRoot()


DEFAULT_ADDRESS = 'localhost:1085'

BUILTIN_CONFIGURATION = f'''
bind: {DEFAULT_ADDRESS}

authentication:
  method: trust

logging:
  level: debug

queues:
  default:
    maxsize: 100

dispatchers: 1
dispatcher:
  messages_per_queue: 5
  intervals: .3

'''


def configure(init_value=None, filename=None, force=None):
    """ Load configurations

    .. seealso:: `pymlconf Documentations <https://github.com/pylover/pymlconf#documentation>`_

    :param args: positional arguments pass into ``pymlconf.DeferredConfigManager.load``
    :param kwargs: keyword arguments pass into ``pymlconf.DeferredConfigManager.load``
    """
    settings.initialize(
        BUILTIN_CONFIGURATION,
        force=force
    )

    if init_value is not None:
        settings.merge(init_value)

    if filename is not None:
        settings.load_file(filename)

    return settings

