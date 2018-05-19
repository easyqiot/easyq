import asyncio
import functools

from aiounittest import AsyncTestCase

from easyq.server import create_server, configure
from easyq.client import connect


class TestCase(AsyncTestCase):

    def get_event_loop(self):
        return asyncio.get_event_loop()

    def server(self, options=None):
        return EasyQTestServer(self.get_event_loop(), options)


class ClientConnection:
    session_id = None

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def send(self, data):
        self.writer.write(data)
        self.writer.write(b'\n')
        await self.writer.drain()

    async def readline(self):
        while True:
            try:
                line = await self.reader.readuntil()
                return line.rstrip()
            except asyncio.LimitOverrunError:
                # If the data cannot be read because of over limit, this error will be raised.
                # and the data will be left in the internal buffer, so it can be read again.
                continue

    def close(self):
        self.writer.write_eof()
        self.writer.close()


class EasyQTestServer:
    server = None

    def __init__(self, loop=None, options=None):
        self.loop = loop or asyncio.get_event_loop()
        self.connections = []
        configure(init_value=options)

    async def __aenter__(self):
        self.server = await create_server(bind='localhost:0')
        host, port = self.server.sockets[0].getsockname()
        return functools.partial(connect, host=host, port=port, loop=self.loop)

    async def __aexit__(self, exc_type, exc, tb):
        for c in self.connections:
            c.close()
        self.server.close()
        await self.server.wait_closed()

