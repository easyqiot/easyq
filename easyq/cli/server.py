import sys
from os import chdir
from os.path import relpath

from ..configuration import configure
from .base import Launcher, RequireSubCommand

DEFAULT_CONFIG_FILE = '%s.yml' % sys.argv[0]
DEFAULT_ADDRESS = '1085'


class RunServerLauncher(Launcher):

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('run', help='Starts a server on given host and port')
        parser.add_argument(
            '-b', '--bind',
            default=DEFAULT_ADDRESS, metavar='{HOST:}PORT',
            help='Bind Address. default: %s' % DEFAULT_ADDRESS
        )
        parser.add_argument(
            '-C', '--directory',
            default='.',
            help='Change to this path before starting the server'
        )
        parser.add_argument(
            '-V', '--version',
            default=False,
            action='store_true',
            help='Show the version.'
        )
        return parser

    def launch(self):
        if self.args.version:
            print(easyq.__version__)
            return 0

        try:
            host, port = \
                self.args.bind.split(':') if ':' in self.args.bind else ('', self.args.bind)

            # Change dir
            if relpath(self.args.directory, '.') != '.':
                chdir(self.args.directory)

            configure(files=self.args.config_file)

            print('Server starting!')
        except KeyboardInterrupt:
            print('CTRL+C detected.')
            return -1
        else:
            return 0


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


