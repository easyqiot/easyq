import unittest
import asyncio

from easyq.tests.helpers import EasyQTestServer, TestCase


class LoginTestCase(TestCase):
    async def test_trust(self):
        options = '''
        authentication:
          method: trust

        logging:
          level: warning
        '''
        async with self.server(options) as connect:
            connection = await connect()
            await connection.send(b'LOGIN testuser')
            session_id = await connection.readline()
            self.assertEqual(b'testuser', session_id)


if __name__ == '__main__':
    unittest.main()

