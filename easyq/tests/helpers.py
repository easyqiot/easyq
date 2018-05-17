import asyncio

from aiounittest import AsyncTestCase

import easyq


class TestCase(AsyncTestCase):

    @classmethod
    def server(cls):
        return EasyQTestServer()


class Connection:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    def send(self, data):
        self.writer.write(b'%s\n' % data)

    async def receive(self):
        line = await self.reader.readuntil()
        return line.rstrip()

    def close(self):
        self.writer.write_eof()


class EasyQTestServer:
    server = None

    def __init__(self, loop=None, options=None):
        self.loop = loop or asyncio.get_event_loop()
        self.connections = []
        easyq.configure(init_value=options)

    async def __aenter__(self):
        self.server = await easyq.create_server(bind='localhost:0')
        host, port = self.server.sockets[0].getsockname()
        async def connector():
            reader, writer = await asyncio.open_connection(host, port, loop=self.loop)
            connection = Connection(reader, writer)
            self.connections.append(connection)
            return connection
        return connector

    async def __aexit__(self, exc_type, exc, tb):
        for c in self.connections:
            c.close()
        self.server.close()
        await self.server.wait_closed()

