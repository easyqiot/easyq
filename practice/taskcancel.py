import asyncio

running = 0

async def worker(name):
    global running
    c = 0
    running = True
    try:
        raise Exception('di dada doo da')
        while True:
            print(f'worker: {name} working cycle: {c}')
            await asyncio.sleep(1)
            c += 1
    except asyncio.CancelledError:
        print('Canceling the task')
        pass


async def monitor():
    for i in range(5):
        print('Running' if running else 'Not Running')
        await asyncio.sleep(1)


async def main(loop):
    worker_task = loop.create_task(worker('a'))
    await monitor()
    worker_task.cancel()
    await worker_task


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
