import asyncio

from easyq.client import connect


async def message_received(queue, message):
    print(f'Messsage received from {queue.decode()}: {message.decode()}')


async def main():
    client = await connect('Username', 'localhost', 1085)
    await client.pull(b'q', message_received)
    await client.push(b'q', b'Hello')
    await asyncio.sleep(2)
    await client.ignore(b'q', message_received)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())

