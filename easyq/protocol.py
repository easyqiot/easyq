import asyncio


class EasyQProtocol(asyncio.Protocol):
    """
    State machine:

        start -> connection_made() [-> data_received() *] [-> eof_received() ?] -> \
            connection_lost() -> end

    """

    def connection_made(self, transport):
        """
        Called when a connection is made.

        The transport argument is the transport representing the connection. You are responsible
        for storing it somewhere (e.g. as an attribute) if you need to.
        """
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def connection_lost(self, exc):
        """
        Called when the connection is lost or closed.

        The argument is either an exception object or None. The latter means a regular EOF is
        received, or the connection was aborted or closed by this side of the connection.
        """
        print(f'Connection closed: {self.transport.get_extra_info("peername")}')

    def data_received(self, data):
        """
        Called when some data is received. data is a non-empty bytes object containing the incoming data.

        """
        message = data.decode()
        print('Data received: {!r}'.format(message))

        print('Send: {!r}'.format(message))
        self.transport.write(data)

#         print('Close the client socket')
#         self.transport.close()

    def eof_received(self):
        """
        Called when the other end signals it won’t send any more data (for example by calling
        write_eof(), if the other end also uses asyncio).

        This method may return a false value (including None), in which case the transport
        will close itself. Conversely, if this method returns a true value, closing the
        transport is up to the protocol. Since the default implementation returns None, it
        implicitly closes the connection.

        Note Some transports such as SSL don’t support half-closed connections, in which case
        returning true from this method will not prevent closing the connection.

        data_received() can be called an arbitrary number of times during a connection. However,
        eof_received() is called at most once and, if called, data_received() won’t be called
        after it.
        """
        print(f'EOF received on {self.transport.get_extra_info("peername")}')
        print('Close the client socket')
        self.transport.close()



