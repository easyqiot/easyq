import unittest
import asyncio

from easyq.tests.helpers import EasyQTestServer, TestCase
from easyq.client import AuthenticationError


class LoginTestCase(TestCase):
    async def test_trust(self):
        options = '''
            authentication:
              method: trust
        '''
        async with self.server(options) as connect:
            client = await connect('testuser')
            self.assertEqual('testuser', client.identity)

            with self.assertRaises(AuthenticationError):
                await connect('colon:not:allowed')


if __name__ == '__main__':
    unittest.main()

