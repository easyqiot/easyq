
import asyncio
import re

from .constants import LINE_ENDING


class ClientProtocol(asyncio.Protocol):
    identity = None
    chunk = None

    class Patterns:
        session_id = re.compile('^HI\s(?P<sessionid>.+)$')

    def __init__(self, login):
        self.login = login
        self.logged_in = asyncio.Future()

    def connection_made(self, transport):
        self.transport = transport
        transport.write(b'LOGIN ' + self.login.encode() + b'\n')

    def data_received(self, data):
        if self.chunk:
            data = self.chunk + data

         # Splitting the received data with \n and adding buffered chunk if available
        lines = data.split(LINE_ENDING)

        # Adding unterminated line into buffer (if available) to be completed with the next call
        if not lines[-1].endswith(LINE_ENDING):
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
        print('The server closed the connection')

    async def process_response(self, data):
        print(b'Data from server: ' + data)


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



