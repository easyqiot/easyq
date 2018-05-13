import argparse
import sys
from os.path import basename

import argcomplete

from .base import Launcher
from .server import ServerLauncher
from .argcompletion import ArgCompleteInstaller


class MainLauncher(Launcher):

    def __init__(self):
        prog = basename(sys.argv[0])
        self.parser = parser = argparse.ArgumentParser(
            prog=prog,
            description='easyq command line interface.'
        )
        subparsers = parser.add_subparsers(
            title="sub commands",
            prog=prog,
            dest="command"
        )

        ServerLauncher.register(subparsers)
        ArgCompleteInstaller.register(subparsers)
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

