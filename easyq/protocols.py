import asyncio

from .authentication import authenticate

"""
-> LOGIN token
<- HI user1

-> PUSH 'message' INTO queue1 [ID 122]
-> PULL FROM queue1
-> IGNORE queue1
<- MESSAGE FROM queue1 [ID 122]
<- MESSAGE 122 IS DELIVERED TO user1
"""

class Connection:
    session_id = None

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def send(self, data):
        self.writer.write(data)
        self.writer.write(b'\n')
        await self.writer.drain()

    async def readline(self):
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
        self.writer.close()


class ClientConnection(Connection):
    pass


class ServerConnection(Connection):

    async def login(self):
        login = await self.readline()
        session_id = await authenticate(login)
        if session_id is None:
            await self.send(b'Authentication failed')
            return None

        self.session_id = session_id
        await self.send(session_id)
        return session_id


    @classmethod
    async def handler(cls, reader, writer):
        session = cls(reader, writer)

        try:
            # Authentication
            if await session.login() is None:
                return

            # Reading commands
            while True:
                chunk = await session.readline()
                await session.send(chunk)

        except asyncio.IncompleteReadError:
            print('Connection closed by the peer')
        finally:
            session.close()

