import asyncio

from aiounittest import AsyncTestCase

import easyq


class TestCase(AsyncTestCase):

    def get_event_loop(self):
        return asyncio.get_event_loop()

    def server(self, options=None):
        return EasyQTestServer(self.get_event_loop(), options)


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
            connection = easyq.ClientConnection(reader, writer)
            self.connections.append(connection)
            return connection
        return connector

    async def __aexit__(self, exc_type, exc, tb):
        for c in self.connections:
            c.close()
        self.server.close()
        await self.server.wait_closed()

