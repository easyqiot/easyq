import asyncio
import functools
import re

from .authentication import authenticate, initialize as initialize_authentication
from .configuration import settings
from .logging import getlogger
from .queuemanager import getqueue


"""
-> PUSH 'message' INTO queue1 [ID 122]
-> PULL FROM queue1
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

    def connection_made(self, transport):
        self.peername = transport.get_extra_info('peername')
        logger.info(f'Connection from {self.peername}')
        self.transport = transport

    def connection_lost(self, exc):
        logger.info(f'Connection lost: {self.peername}')

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

    async def push(self, message=None, queue=None):
        await getqueue(queue).push(message)

    async def process_command(self, command):
        logger.debug(f'Processing command: {command.decode()} by {self.identity}')
        m = self.Patterns.push.match(command)
        if m:
            await self.push(*m.groupdict())
        else:
            logger.debug(f'Invalid command: {command}')
            self.transport.write(b'Invalid command: %s;\n' % command)

    class Patterns:
        regex = functools.partial(re.compile, flags=re.DOTALL + re.IGNORECASE)
        login = regex(b'^LOGIN (?P<credentials>.+)$')
        push = regex(b'^PUSH (?P<message>.+) INTO (?P<queue>[0-9a-zA-Z\._:-]+)$')


async def create_server(bind=None, loop=None):
    loop = loop or asyncio.get_event_loop()

    # Host and Port to listen
    bind = bind or settings.bind
    host, port = bind.split(':') if ':' in bind else ('', bind)

    # Configuring the authenticator
    initialize_authentication()

    # Create the server coroutine
    return await loop.create_server(ServerProtocol, host, port)

