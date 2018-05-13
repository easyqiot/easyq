import os
import sys
from os.path import join, basename

from .base import Launcher, RequireSubCommand


class AutoCompletionLauncher(Launcher, RequireSubCommand):

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('autocompletion')
        sub_subparsers = parser.add_subparsers(dest='autocompletion_command')
        AutoCompletionInstaller.register(sub_subparsers)
        return parser



class ArgCompleteInstaller(Launcher):

    @classmethod
    def create_parser(cls, subparsers):
        parser = subparsers.add_parser('install-autocompletion')
        parser.add_argument(
            '-s', '--system-wide',
            action='store_true',
            help='Installs the scripts in /etc/bash_completion.d'
        )
        return parser

    def launch(self):
        if 'VIRTUAL_ENV' in os.environ:
            self.install_virtualenv()
        elif self.args.system_wide:
            self.install_systemwide()
        else:
            self.install_user()

    def install_virtualenv(self):
        sourcefile = join(os.environ['VIRTUAL_ENV'], 'bin/postactivate')
        self.install_file(sourcefile)

    def install_user(self):
        sourcefile = join(os.environ['HOME'], '.bashrc')
        self.install_file(sourcefile)

    def install_file(self, filename):
        with open(filename) as f:
            content = f.readlines()

        line = 'eval "$(register-python-argcomplete %s)"\n' % basename(sys.argv[0])
        if line not in content:
            with open(filename, mode='a') as f:
                f.write(line)

    def install_systemwide(self):
        exp = 'PYTHON_ARGCOMPLETE_OK'
        filename = sys.argv[0]
        with open(filename) as f:

            content = f.read(1024)
            if exp in content:
                print('The global bash completion is already activated', file=sys.stderr)
                return 1

            content += f.read()

        lines = content.splitlines()
        lines.insert(1, exp + '\n')
        with open(filename, mode='w') as f:
            f.writelines(lines)

