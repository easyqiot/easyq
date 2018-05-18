import asyncio

from .authentication import authenticate
from .logging import get_logger

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


logger = get_logger('Protocol')


class ServerProtocol(asyncio.Protocol):
    identity = None

    def __init__(self):
        self.chunk = b''

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        logger.info(f'Connection from {peername}')
        self.transport = transport

    def data_received(self, data):
        logger.info(f'Data received: {data.decode().strip()}')
        lines = data.split(b'\n')
        lines[0] = self.chunk + lines[0]

        if self.identity is None:
            self.login(lines[0])

        commands += [l for l in lines if l.strip()]
        for command in commands:
            asyncio.ensure_future(self.process_command(command))

        # self.transport.close()

