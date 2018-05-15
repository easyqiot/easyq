import asyncio


class EasyQProtocol(asyncio.Protocol):
    """
    State machine:

        start -> connection_made() [-> data_received() *] [-> eof_received() ?] -> \
            connection_lost() -> end

    """
    transport = None

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def connection_lost(self, exc):
        print(f'Connection closed: {self.transport.get_extra_info("peername")}')

    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}'.format(message))

        print('Send: {!r}'.format(message))
        self.transport.write(data)

    def eof_received(self):
        print(f'EOF received on {self.transport.get_extra_info("peername")}')
        print('Close the client socket')
        self.transport.close()

