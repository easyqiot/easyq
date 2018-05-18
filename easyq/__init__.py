import asyncio

from .configuration import settings, configure
from .protocols import ServerProtocol
from .authentication import initialize


__version__ = '0.1.0a1'
__all__ = [
    'configure',
    'create_server',
]


def create_server(bind=None, loop=None):
    loop = loop or asyncio.get_event_loop()

    # Host and Port to listen
    bind = bind or settings.bind
    host, port = bind.split(':') if ':' in bind else ('', bind)

    # Configuring the authenticator
    authentication.initialize()

    # Create the server coroutine
    return loop.create_server(ServerProtocol, host, port)

