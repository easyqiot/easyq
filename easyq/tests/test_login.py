import unittest
import asyncio

from easyq.tests.helpers import EasyQTestServer, TestCase


class LoginTestCase(TestCase):
    async def test_trust(self):
        await asyncio.sleep(1)

        #async with EasyQTestServer



if __name__ == '__main__':
    unittest.main()
