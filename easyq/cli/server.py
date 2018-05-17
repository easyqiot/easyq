import asyncio
import sys
from os import chdir
from os.path import relpath

import easyq
from ..configuration import configure, DEFAULT_ADDRESS
from .base import Launcher, RequireSubCommand


DEFAULT_CONFIG_FILE = '%s.yml' % sys.argv[0]


class StartServerLauncher(Launcher):

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('start', help='Starts a server on given host and port')
        parser.add_argument(
            '-b', '--bind',
            metavar='{HOST:}PORT',
            help='Bind Address. if ommited the value from the config file will be used'
                 'The default config value is: %s' % DEFAULT_ADDRESS
        )
        parser.add_argument(
            '-C', '--directory',
            default='.',
            help='Change to this path before starting the server'
        )
        return parser

    def launch(self):
        try:
            # Change dir
            if relpath(self.args.directory, '.') != '.':
                chdir(self.args.directory)

            configure(files=self.args.config_file)
            self.start_server()
        except KeyboardInterrupt:
            print('CTRL+C detected.')
            return -1
        else:
            return 0

    def start_server(self):
        loop = asyncio.get_event_loop()
        coro = easyq.create_server(bind=self.args.bind, loop=loop)
        server = loop.run_until_complete(coro)

        # Serve requests until Ctrl+C is pressed
        host, port = server.sockets[0].getsockname()
        print(f'Serving on {host}:{port}')
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print('CTRL+C pressed')
        finally:
            # Close the server
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()


class ServerLauncher(Launcher, RequireSubCommand):
    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('server')
        parser.add_argument(
            '-c', '--config-file',
            metavar="FILE",
            default=DEFAULT_CONFIG_FILE,
        )

        server_subparsers = parser.add_subparsers(dest='server_command')
        StartServerLauncher.register(server_subparsers)
        return parser

