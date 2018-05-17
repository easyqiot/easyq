import asyncio

from aiounittest import AsyncTestCase

from easyq.protocols import EasyQProtocol


class TestCase(AsyncTestCase):
    @classmethod
    def server(cls):
        return EasyQTestServer()


class EasyQTestServer:
    server = None

    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()

    async def __aenter__(self):
        self.server = await self.loop.create_server(EasyQProtocol, port=0)
        host, port = self.server.sockets[0].getsockname()
        async def connector():
            reader, writer = yield from asyncio.open_connection(host, port, loop=loop)

            writer.close()
        return connector

    async def __aexit__(self, exc_type, exc, tb):
        self.server.close()
        await self.server.wait_closed()

