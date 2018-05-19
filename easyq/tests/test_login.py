import unittest
import asyncio

from easyq.tests.helpers import EasyQTestServer, TestCase


class LoginTestCase(TestCase):
    async def test_trust(self):
        options = '''
            authentication:
              method: trust

            logging:
              level: debug
        '''
        async with self.server(options) as connect:
            client = await connect('testuser')
            self.assertEqual('testuser', client.identity)


if __name__ == '__main__':
    unittest.main()

