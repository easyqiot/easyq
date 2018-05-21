import unittest
import asyncio

from easyq.server import ServerProtocol
from easyq.tests.helpers import EasyQTestServer, TestCase
from easyq.client import AuthenticationError


class PushTestCase(TestCase):
    async def test_parser(self):
        whitelist = [
            (b'PUSH Hello INTO q1', b'Hello', b'q1'),
            (b'PUSH \'Hello\' INTO myq', b'\'Hello\'', b'myq'),
            (b'PUSH Hello dear INTO myq', b'Hello dear', b'myq'),
            (b'PUSH Hello\ndear INTO myq', b'Hello\ndear', b'myq'),
            (b'PUSH Hello dear INTO bad INTO myq', b'Hello dear INTO bad', b'myq'),
            (b'PUSH Hello INTO myq:a.b_c', b'Hello', b'myq:a.b_c'),
            (b'push hello into myq:a.b_c', b'hello', b'myq:a.b_c'),
        ]

        for command, expected_message, expected_queue in whitelist:
            m = ServerProtocol.Patterns.push.match(command)
            if m is None:
                print(command)
            self.assertIsNotNone(m)
            message, queue = m.groups()
            self.assertEqual(expected_queue, queue)
            self.assertEqual(expected_message, message)

        blacklist = [
            b'PUSH Hello INTO my\nq',
        ]

        for t in blacklist:
            self.assertIsNone(ServerProtocol.Patterns.push.match(t))

    async def test_push(self):
       async with self.server() as connect:
            client = await connect('testuser')
            await client.push(b'q1', b'Hello')
            await asyncio.sleep(1)


if __name__ == '__main__':
    unittest.main()

