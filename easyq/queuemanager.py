import asyncio

from .configuration import settings
from .logging import getlogger


logger = getlogger('QM')
queues = {}


class AlreadySubscribedError(Exception):
    pass


class NotSubscribedError(Exception):
    pass


class Queue:

    def __init__(self, name):
        self.name = name
        options = settings.queues.default if name not in settings.queues else settings.queues[name]
        self._queue = asyncio.Queue(maxsize=options.maxsize)
        self.subscriptors = []

    def push(self, message):
        self._queue.put_nowait(message)

    def get(self):
        return self._queue.get_nowait()

    def subscribe(self, protocol):
        if protocol in self.subscriptors:
            raise AlreadySubscribedError()
        logger.info(f'Queue {self.name.decode()} was subscribed by {protocol.identity}')
        self.subscriptors.append(protocol)

    def unsubscribe(self, protocol):
        if protocol not in self.subscriptors:
            raise NotSubscribedError()

        logger.info(f'Queue {self.name.decode()} was ignored by {protocol.identity}')
        self.subscriptors.remove(protocol)

    async def dispatch(self, message):
        for protocol in self.subscriptors:
            logger.debug(
                f'Dispatching message {message} from queue {self.name.decode()} to {protocol.identity}'
            )
            await protocol.dispatch(self.name, message)


async def dispatcher(name, intervals=.5, messages_per_queue=5):
    logger = getlogger(name)
    cycle = 0
    try:
        while True:
            if cycle % 100 == 0:
                logger.debug(f'Cycle: {cycle}')
            for queue in queues.values():
                try:
                    for i in range(messages_per_queue):
                        message = queue.get()
                        logger.debug(f'Dispatching {message}')
                        await queue.dispatch(message)

                except asyncio.QueueEmpty:
                    pass

            cycle += 1
            await asyncio.sleep(intervals)
    except asyncio.CancelledError:
        logger.info(f'Terminating on cycle: {cycle}')


def getqueue(name) -> Queue:
    if name not in queues:
        queues[name] = Queue(name)
        logger.info(f'Queue {name.decode()} just created.')
    return queues[name]


def subscribe(name, protocol):
    getqueue(name).subscribe(protocol)


def unsubscribe(name, protocol):
    getqueue(name).unsubscribe(protocol)


def unsubscribe_all(protocol):
    for queue in queues.values():
        try:
            queue.unsubscribe(protocol)
        except NotSubscribedError:
            pass

