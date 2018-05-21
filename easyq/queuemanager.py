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

    async def push(self, message):
        await self._queue.put(message)


def getqueue(name) -> Queue:
    if name not in queues:
        queues[name] = Queue(name)
        logger.info(f'Queue {name} just created.')
    return queues[name]

