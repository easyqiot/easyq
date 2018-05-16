
from aiounittest import AsyncTestCase


class TestCase(AsyncTestCase):
    pass


class EasyQTestServer:
    async def __aenter__(self):
        print('Entering context')

    async def __aexit__(self, exc_type, exc, tb):
        print('Exiting context')

