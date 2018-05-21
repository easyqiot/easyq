import unittest
import asyncio

from easyq.server import ServerProtocol
from easyq.tests.helpers import EasyQTestServer, TestCase
from easyq.client import AuthenticationError


class LoginTestCase(TestCase):
    async def test_parser(self):
        whitelist = [
            (b'LOGIN user', b'user'),
            (b'LOGIN user name', b'user name'),
            (b'login user name', b'user name'),
        ]

        for command, expected_credentials in whitelist:
            m = ServerProtocol.Patterns.login.match(command)
            if m is None:
                print(command)
            self.assertIsNotNone(m)
            credentials, = m.groups()
            self.assertEqual(expected_credentials, credentials)

        blacklist = [
            b'LOGINuser',
        ]

        for t in blacklist:
            self.assertIsNone(ServerProtocol.Patterns.push.match(t))


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

