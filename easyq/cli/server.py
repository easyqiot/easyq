import sys
import asyncio
from os import chdir
from os.path import relpath

from ..configuration import configure, DEFAULT_ADDRESS, settings
from ..protocol import EasyQProtocol
from .base import Launcher, RequireSubCommand


DEFAULT_CONFIG_FILE = '%s.yml' % sys.argv[0]


class RunServerLauncher(Launcher):

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('run', help='Starts a server on given host and port')
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
        bind = self.args.bind if self.args.bind else settings.server.bind
        host, port = bind.split(':') if ':' in bind else ('', bind)

        loop = asyncio.get_event_loop()
        # Each client connection will create a new protocol instance
        coro = loop.create_server(EasyQProtocol, host, port)
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
            serverclose()
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
        RunServerLauncher.register(server_subparsers)
        return parser


