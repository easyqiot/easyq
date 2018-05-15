import sys
import argparse
from os.path import basename

import argcomplete

import easyq
from .base import Launcher
from .server import ServerLauncher
from .argcompletion import AutoCompletionLauncher


class MainLauncher(Launcher):

    def __init__(self):
        prog = basename(sys.argv[0])
        self.parser = parser = argparse.ArgumentParser(
            prog=prog,
            description='easyq command line interface.'
        )
        parser.add_argument(
            '-V', '--version',
            default=False,
            action='store_true',
            help='Show the version.'
        )
        subparsers = parser.add_subparsers(
            title="sub commands",
            prog=prog,
            dest="command"
        )

        ServerLauncher.register(subparsers)
        AutoCompletionLauncher.register(subparsers)
        argcomplete.autocomplete(parser)

    def launch(self, args=None):
        cli_args = self.parser.parse_args(args or sys.argv[1:])
        if cli_args.version:
            print(easyq.__version__)
            return 0

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

