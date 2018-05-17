import asyncio

from .configuration import settings
from .protocols import EasyQServerProtocol
from .authentication import initialize


__version__ = '0.1.0a1'


def create_server(loop=None, bind=None):
    loop = loop or asyncio.get_event_loop()

    # Host and Port to listen
    bind = bind or settings.server.bind
    host, port = bind.split(':') if ':' in bind else ('', bind)

    # Configuring the authenticator
    authentication.initialize()

    # Create the server coroutine
    return loop.create_server(EasyQServerProtocol, host, port)


