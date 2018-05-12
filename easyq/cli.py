import argparse
import sys
from os import chdir
from os.path import relpath

import argcomplete

from .configuration import configure


DEFAULT_CONFIG_FILE = 'easyq.yml'
DEFAULT_ADDRESS = '1085'


class Launcher:
    no_launch = False
    parser = None

    @classmethod
    def create_parser(cls, subparsers):
        raise NotImplementedError

    @classmethod
    def register(cls, subparsers):
        parser = cls.create_parser(subparsers)
        instance = cls()
        instance.parser = parser
        if not cls.no_launch:
            parser.set_defaults(func=instance)
        return instance

    def __call__(self, *args):
        self.args = args[0] if len(args) else None
        sys.exit(self.launch())

    def launch(self):
        if self.parser:
            self.parser.print_help()
        return 1


class RequireSubCommand:
    no_launch = True


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


class MainLauncher(Launcher):

    def __init__(self):
        self.parser = parser = argparse.ArgumentParser(
            prog=sys.argv[0],
            description='easyq command line interface.'
        )
        subparsers = parser.add_subparsers(
            title="sub commands",
            prog=sys.argv[0],
            dest="command"
        )

        ServerLauncher.register(subparsers)
        argcomplete.autocomplete(parser)

    def launch(self, args=None):
        cli_args = self.parser.parse_args(args)
        if hasattr(cli_args, 'func'):
            cli_args.func(cli_args)
        else:
            self.parser.print_help()
        sys.exit(0)

    @classmethod
    def create_parser(cls, subparsers):
        """
        Do nothing here
        """
        pass

