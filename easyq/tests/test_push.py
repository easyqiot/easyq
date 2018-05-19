import unittest
import asyncio

from easyq.tests.helpers import EasyQTestServer, TestCase
from easyq.client import AuthenticationError


class PushTestCase(TestCase):
    async def test_push(self):
       async with self.server() as connect:
            client = await connect('testuser')
#            queue = client.get_queue('q1')
#            queue.push('Hello')


if __name__ == '__main__':
    unittest.main()

