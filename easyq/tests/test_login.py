import unittest
import asyncio

from easyq.tests.helpers import EasyQTestServer, TestCase


class LoginTestCase(TestCase):
    async def test_trust(self):
        async with self.server() as connect:
            connection = connect()
            connection.send(b'LOGIN test')
            self.assertEqual(b'LOGIN test', connection.receive())

        #async with EasyQTestServer



if __name__ == '__main__':
    unittest.main()
