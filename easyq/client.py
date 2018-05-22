import functools
import asyncio
import re


class ClientProtocol(asyncio.Protocol):
    identity = None
    chunk = None
    onerror = None

    class Patterns:
        regex = functools.partial(re.compile, flags=re.DOTALL)
        session_id = regex('^HI\s(?P<sessionid>.+)$')
        incomming = regex(b'^MESSAGE (?P<message>.+) FROM (?P<queue>[0-9a-zA-Z\._:-]+)$')

    def __init__(self, login):
        self.login = login
        self.logged_in = asyncio.Future()
        self.handlers = {}

    def connection_made(self, transport):
        self.transport = transport
        transport.write(b'LOGIN ' + self.login.encode() + b';\n')

    def data_received(self, data):
        if self.chunk:
            data = self.chunk + data

         # Splitting the received data with \n and adding buffered chunk if available
        lines = data.split(b';')

        # Adding unterminated line into buffer (if available) to be completed with the next call
        if not lines[-1].endswith(b';'):
            self.chunk = lines.pop()

        # Exiting if there is no line to process
        if not lines:
            return

        if self.identity is None:
            login_response = lines.pop(0).decode()
            match = self.Patterns.session_id.match(login_response)
            if not match:
                self.transport.write_eof()
                self.transport.close()
                self.logged_in.set_result(False)
                return

            self.identity, = session_id, = match.groups()
            self.logged_in.set_result(True)

        for response in lines:
            response = response.strip()
            asyncio.ensure_future(self.process_response(response))

    def connection_lost(self, exc):
        self.logged_in.set_result(False)

    async def process_response(self, data):
        m = self.Patterns.incomming.match(data)
        if m is not None:
            return await self.dispatch(**m.groupdict())

        return await self.error(data)

    async def push(self, queue, message):
        self.transport.write(b'PUSH %s INTO %s;\n' % (message, queue))

    async def pull(self, queue, callback):
        self.transport.write(b'PULL FROM %s;\n' % queue)
        handlers = self.handlers.setdefault(queue, set())
        handlers.add(callback)

    async def ignore(self, queue, callback):
        handlers = self.handlers.setdefault(queue, set())
        if callback not in handlers:
            raise ValueError(f'Invalid callback: {callback}')

        handlers.remove(callback)
        self.transport.write(b'IGNORE %s;\n' % queue)

    async def dispatch(self, message, queue):
        handlers = self.handlers.get(queue)
        if handlers:
            await asyncio.gather(
                *(handler(queue, message) for handler in handlers),
                return_exceptions=True
            )

    async def error(self, err):
        if self.onerror:
            await self.onerror(self, err)


class EasyQClientError(Exception):
    pass


class AuthenticationError(EasyQClientError):
    pass


async def connect(login, host, port, loop=None) -> ClientProtocol:
    loop = loop or asyncio.get_event_loop()
    transport, protocol = await loop.create_connection(lambda: ClientProtocol(login), host, port)

    if not await protocol.logged_in:
        raise AuthenticationError('Cannot connect, the server refuses the credentials')

    return protocol



