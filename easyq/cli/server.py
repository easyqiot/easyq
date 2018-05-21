import asyncio
import sys
from os import chdir
from os.path import relpath

import yaml
from easyq.server import Server
from ..configuration import DEFAULT_ADDRESS, configure
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

        parser.add_argument(
            '-c', '--config-file',
            metavar="FILE",
            default=DEFAULT_CONFIG_FILE,
        )

        parser.add_argument(
            '-o', '--option',
            action='append',
            metavar='key1.key2=value',
            dest='options',
            default=[],
            help='Configuration value to override. this option could be passed multiple times.'
        )

        return parser

    def launch(self):
        try:
            # Change dir
            if relpath(self.args.directory, '.') != '.':
                chdir(self.args.directory)

            settings = configure(files=self.args.config_file)
            for option in self.args.options:
                key, value = option.split('=')
                value = yaml.load(value)
                if isinstance(value, str):
                    value = f'"{value}"'

                exec(f'settings.{key} = {value}')

            self.start_server()
        except KeyboardInterrupt:
            print('CTRL+C detected.')
            return -1
        else:
            return 0

    def start_server(self):
        loop = asyncio.get_event_loop()
        server = Server(bind=self.args.bind, loop=loop)
        loop.run_until_complete(server.start())

        # Serve requests until Ctrl+C is pressed
        host, port = server.address
        print(f'Serving on {host}:{port}')
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print('CTRL+C pressed')
        finally:
            # Close the server
            loop.run_until_complete(server.close())
            loop.close()


class ServerLauncher(Launcher, RequireSubCommand):
    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('server')
        server_subparsers = parser.add_subparsers(dest='server_command')
        StartServerLauncher.register(server_subparsers)
        return parser

