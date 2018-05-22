import unittest
import asyncio

from easyq.server import ServerProtocol
from easyq.tests.helpers import EasyQTestServer, TestCase
from easyq.client import AuthenticationError, ClientProtocol
from easyq.queuemanager import AlreadySubscribedError


class PullTestCase(TestCase):
    async def test_subscription_parser(self):
        whitelist = [
            (b'PULL FROM q1', b'q1'),
            (b'pull from q1', b'q1'),
        ]

        for command, expected_queue in whitelist:
            m = ServerProtocol.Patterns.pull.match(command)
            self.assertIsNotNone(m)
            queue, = m.groups()
            self.assertEqual(expected_queue, queue)

        blacklist = [
            b'PULL FROM my!q',
        ]

        for t in blacklist:
            self.assertIsNone(ServerProtocol.Patterns.push.match(t))

    async def test_incomming_message_parser(self):
        whitelist = [
            (b'MESSAGE Hello FROM q1', b'Hello', b'q1'),
            (b'MESSAGE Hello\nDear FROM q1', b'Hello\nDear', b'q1'),
        ]

        for command, expected_message, expected_queue in whitelist:
            m = ClientProtocol.Patterns.incomming.match(command)
            self.assertIsNotNone(m)
            message, queue = m.groups()
            self.assertEqual(expected_queue, queue)
            self.assertEqual(expected_message, message)

        blacklist = [
            b'MESSAGE FROM my!q',
        ]

        for t in blacklist:
            self.assertIsNone(ServerProtocol.Patterns.push.match(t))


    async def test_pull(self):
       async with self.server() as connect:
            client = await connect('testuser')
            messages = []
            errors = []

            async def message_received(queue, message):
                messages.append(message)

            async def error(client_, error):
                errors.append(error)

            client.onerror = error

            await client.pull(b'q1', message_received)
            await client.push(b'q1', b'Hello')
            await asyncio.sleep(1.1)
            self.assertEqual([b'Hello'], messages)
            self.assertEqual([], errors)

            # pulling twice!
            await client.pull(b'q1', message_received)
            await asyncio.sleep(1.1)
            self.assertEqual([b'ERROR: QUEUE q1 IS ALREADY SUBSCRIBED'], errors)

            # Unsunscribing
            await client.ignore(b'q1', message_received)
            messages = []
            errors = []
            await client.push(b'q1', b'Hello')
            await asyncio.sleep(1.1)
            self.assertEqual([], messages)
            self.assertEqual([], errors)

            # Ignoring twice!
            client.handlers[b'q1'] = [message_received]
            await client.ignore(b'q1', message_received)
            await asyncio.sleep(1.1)
            self.assertEqual([b'ERROR: QUEUE q1 IS NOT SUBSCRIBED'], errors)




if __name__ == '__main__':
    unittest.main()

