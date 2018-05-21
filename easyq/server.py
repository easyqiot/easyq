import asyncio
import functools
import re

from .authentication import authenticate, initialize as initialize_authentication
from .configuration import settings
from .logging import getlogger
from .queuemanager import getqueue, dispatcher


"""
> PULL FROM queue1
-> IGNORE queue1

<- MESSAGE FROM queue1 [ID 122]
<- MESSAGE 122 IS DELIVERED TO user1

"""


logger = getlogger('PROTO')


class ServerProtocol(asyncio.Protocol):
    identity = None
    transport = None
    chunk = None
    peername = None

    class Patterns:
        regex = functools.partial(re.compile, flags=re.DOTALL + re.IGNORECASE)
        login = regex(b'^LOGIN (?P<credentials>.+)$')
        push = regex(b'^PUSH (?P<message>.+) INTO (?P<queue>[0-9a-zA-Z\._:-]+)$')
        pull = regex(b'^PULL FROM (?P<queue>[0-9a-zA-Z\._:-]+)$')

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        logger.info(f'Connection from {self.peername}')
        self.transport = transport

    def connection_lost(self, exc):
        logger.info(f'Connection lost: {self.peername}')
        # FIXME: remove from all queues subscriptions

    def eof_received(self):
        logger.debug(f'EOF Received: {self.peername}')
        self.transport.close()

    def data_received(self, data):
        logger.debug(f'Data received: {data.decode().strip()}')
        if self.chunk:
            data = self.chunk + data

        if self.identity is None:
            if b';' not in data:
                self.chunk = data
                return

            credentials, self.chunk = data.split(b';', 1)
            # Suspending all other commands before authentication
            self.transport.pause_reading()

            # Scheduling a login task, if everything went ok, then the resume_reading will be
            # called in the future.
            asyncio.ensure_future(self.login(credentials))
            return

        # Splitting the received data with \n and adding buffered chunk if available
        lines = data.split(b';')

        # Adding unterminated command into buffer (if available) to be completed with the next call
        if not lines[-1].endswith(b';'):
            self.chunk = lines.pop()

        # Exiting if there is no command to process
        if not lines:
            return

        for command in lines:
            command = command.strip()
            asyncio.ensure_future(self.process_command(command))

    async def login(self, credentials):
        logger.info(f'Authenticating: {self.peername}')
        m = self.Patterns.login.match(credentials)
        if m is None:
            await self.login_failed(credentials)
            return

        credentials = m.groupdict()['credentials']
        self.identity = await authenticate(credentials)
        if self.identity is None:
            await self.login_failed(credentials)
            return

        logger.info(f'Login success: {self.identity} from {self.peername}')
        self.transport.write(b'HI %s;\n' %  self.identity.encode())
        self.transport.resume_reading()

    async def login_failed(self, credentials):
        logger.info(
            f'Login failed for {self.peername} with credentials: {credentials}, Closing socket.'
        )
        self.transport.write(b'LOGIN FAILED\n')
        self.transport.close()

    async def push(self, message, queue):
        try:
            getqueue(queue).push(message)
        except asyncio.QueueFull:
            self.logger.warning(f'Queue is full: {self.name}')
            self.transport.write(b'ERROR: QUEUE %s IS FULL;\n' % queue)

    async def process_command(self, command):
        logger.debug(f'Processing command: {command.decode()} by {self.identity}')
        m = self.Patterns.push.match(command)
        if m is not None:
            return await self.push(**m.groupdict())

        logger.debug(f'Invalid command: {command}')
        self.transport.write(b'ERROR: Invalid command: %s;\n' % command)

    async def dispatch(self, queue, message):
        self.transport.write(b'MESSAGE %s FROM %s;\n' % (message, queue))


def create_dispatchers(workers=1, **kwargs):
    logger.info(f'Creating {workers} dispatchers')
    return asyncio.gather(*())


class Server:
    _server = None
    def __init__(self, bind=None, loop=None):
        self.loop = loop or asyncio.get_event_loop()

        # Host and Port to listen
        bind = bind or settings.bind
        self.host, self.port = bind.split(':') if ':' in bind else ('', bind)

        # Configuring the authenticator
        initialize_authentication()

        self.server_coro = self.loop.create_server(ServerProtocol, self.host, self.port)
        self._dispatchers = []

    async def start(self):
        self._server = await self.server_coro

        for i in range(settings.dispatchers):
            self._dispatchers.append(
                self.loop.create_task(dispatcher('WORKER %d' % i, **settings.dispatcher))
            )

    async def close(self):
        for dispatcher in self._dispatchers:
            dispatcher.cancel()
        self._server.close()
        await self._server.wait_closed()
        await asyncio.wait(self._dispatchers)

    @property
    def address(self):
        return self._server.sockets[0].getsockname()

