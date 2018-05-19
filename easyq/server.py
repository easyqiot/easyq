import asyncio

from .configuration import settings, configure
from .logging import get_logger
from .constants import LINE_ENDING
from .authentication import authenticate, initialize as initialize_authentication

"""
-> LOGIN token
<- HI user1

-> PUSH 'message' INTO queue1 [ID 122]
-> PULL FROM queue1
-> IGNORE queue1
-> EXIT

<- MESSAGE FROM queue1 [ID 122]
<- MESSAGE 122 IS DELIVERED TO user1

"""


logger = get_logger('PROTO')


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
        logger.debug('EOF Received: {self.peername}')
        self.transport.close()

    def data_received(self, data):
        logger.debug(f'Data received: {data.decode().strip()}')
        if self.chunk:
            data = self.chunk + data

        if self.identity is None:
            if LINE_ENDING not in data:
                self.chunk = data
                return

            credentials, self.chunk = data.split(LINE_ENDING, 1)
            # Suspending all other commands before authentication
            self.transport.pause_reading()

            # Scheduling a login task, if everything went ok, then the resume_reading will be
            # called in the future.
            asyncio.ensure_future(self.login(credentials))
            return

        # Splitting the received data with \n and adding buffered chunk if available
        lines = data.split(LINE_ENDING)

        # Adding unterminated command into buffer (if available) to be completed with the next call
        if not lines[-1].endswith(LINE_ENDING):
            self.chunk = lines.pop()

        # Exiting if there is no command to process
        if not lines:
            return

        for command in lines:
            command = command.strip()
            asyncio.ensure_future(self.process_command(command))

    async def login(self, credentials):
        logger.info(f'Authenticating: {self.peername}')
        if not credentials.lower().startswith(b'login '):
            await self.login_failed(credentials)
            return

        credentials = credentials[6:]
        self.identity = await authenticate(credentials)
        if self.identity is None:
            await self.login_failed(credentials)
            return

        logger.info(f'Login success: {self.identity} from {self.peername}')
        self.transport.write(b'SESSION ID: ' + self.identity.encode() + b'\n')
        self.transport.resume_reading()

    async def login_failed(self, credentials):
        logger.info(
            'Login failed for {self.peername} with credentials: {credentials}, Closing socket.'
        )
        self.transport.write(b'LOGIN FAILED\n')
        self.transport.close()

    async def process_command(self, command):
        logger.debug(f'Processing Command: {command.decode()} by {self.identity}')
        self.transport.write(command)
        self.transport.write(LINE_ENDING)


async def create_server(bind=None, loop=None):
    loop = loop or asyncio.get_event_loop()

    # Host and Port to listen
    bind = bind or settings.bind
    host, port = bind.split(':') if ':' in bind else ('', bind)

    # Configuring the authenticator
    initialize_authentication()

    # Create the server coroutine
    return await loop.create_server(ServerProtocol, host, port)

