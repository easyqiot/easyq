import argparse
import sys

import argcomplete

from .base import Launcher
from .server import ServerLauncher


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

