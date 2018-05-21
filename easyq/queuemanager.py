import asyncio

from .configuration import settings
from .logging import getlogger


logger = getlogger('QM')
queues = {}


class Queue:

    def __init__(self, name):
        self.name = name
        options = settings.queues.default if name not in settings.queues else settings.queues[name]
        self._queue = asyncio.Queue(maxsize=options.maxsize)
        self.subscriptors = []

    def push(self, message):
        self._queue.put_nowait(message)

    def subscribe(self, protocol):
        self.subscriptors.append(protocol)

    def unsubscribe(self, protocol):
        self.subscriptors.remove(protocol)

    async def dispatch(self, message):
        for protocol in self.subscriptors:
            await protocol.dispatch(queue, message)


def getqueue(name) -> Queue:
    if name not in queues:
        queues[name] = Queue(name)
        logger.info(f'Queue {name} just created.')
    return queues[name]


async def dispatcher(name, intervals=.5, messages_per_queue=5):
    logger = getlogger(name)
    cycle = 0
    try:
        while True:
            logger.debug(f'Cycle: {cycle}')
            for queue in queues:
                try:
                    for i in range(message_per_queue):
                        message = queue.get_nowait()
                        await queue.dispatch(message)

                except EmptyQueue:
                    logger.info(f'Queue {queue.decode()} is empty')

            cycle += 1
            await asyncio.sleep(intervals)
    except asyncio.CancelledError:
        logger.info(f'Terminating on cycle: {cycle}')

