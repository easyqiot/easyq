import unittest
import asyncio

from easyq.tests.helpers import EasyQTestServer, TestCase


class LoginTestCase(TestCase):
    async def test_trust(self):
        options = '''
        server:
          authentication:
            method: trust
        '''
        async with self.server(options) as connect:
            connection = await connect()
            connection.send(b'LOGIN test')
            session_id = await connection.receive()
            self.assertEqual(b'test', session_id)


if __name__ == '__main__':
    unittest.main()

