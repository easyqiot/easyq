import asyncio
from datetime import datetime

from easyq.client import connect


async def message_received(queue, message):
    print(f'Messsage received from {queue.decode()}: {message.decode()}')


async def main():
    client = await connect('ROBOT', '192.168.8.44', 1085)
    await client.pull(b'q', message_received)
    try:
        while True:
            now = datetime.now()
            msg = 'Hello %s:%s' % (now.strftime('%H:%m:%s'), '#' * now.second)
            await client.push(b'q', msg.encode())
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await client.ignore(b'q', message_received)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

