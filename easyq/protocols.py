import asyncio

from .authentication import authenticate


class Connection:
    session_id = None

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    def send(self, data):
        self.writer.write(b'%s\n' % data)

    async def receive(self):
        while True:
            try:
                line = await self.reader.readuntil()
                return line.rstrip()
            except asyncio.LimitOverrunError:
                # If the data cannot be read because of over limit, this error will be raised.
                # and the data will be left in the internal buffer, so it can be read again.
                continue

    def close(self):
        self.writer.write_eof()


class ClientConnection(Connection):
    pass


class ServerConnection(Connection):
    async def login(self):
        login = await self.receive()
        session_id = await authenticate(login)
        if session_id is None:
            self.send(str(ex).encode())
            return None

        self.session_id = session_id
        self.send(session_id)
        return session_id


async def server_handler(reader, writer):
    session = ServerConnection(reader, writer)

    try:
        # Authentication
        if await session.login() is None:
            return

        # Reading commands
        while True:
            chunk = await session.receive()
            session.send(chunk)

    except asyncio.IncompleteReadError:
        print('Connection closed by the peer')
    finally:
        session.close()

