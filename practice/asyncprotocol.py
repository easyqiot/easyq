import asyncio


class MyProto(asyncio.Protocol):
    identity = False

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        if not self.identity:
            self.transport.pause_reading()
            asyncio.ensure_future(self.login(data.strip()))
            return
        print(b'%s: %s' % (self.identity, data))
        self.transport.write(data)

    async def login(self, data):
        await asyncio.sleep(15)
        self.identity = data
        self.transport.resume_reading()

def main(loop):
    # Each client connection will create a new protocol instance
    coro = loop.create_server(MyProto, 'localhost', 8888)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    main(loop)

