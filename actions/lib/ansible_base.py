import os
import sys
import subprocess
import shell
import ast

__all__ = [
    'AnsibleBaseRunner'
]


class AnsibleBaseRunner(object):
    """
    Base class for all Ansible Runners
    """
    BINARY_NAME = None
    REPLACEMENT_RULES = None

    def __init__(self, args):
        """
        :param args: Input command line arguments
        :type args: ``list``
        """
        self.args = args[1:]

        # handle multiple variables in extra_vars list
        for i, arg in enumerate(self.args):
            if '--extra_vars' in arg:
                # We are passed a literal string of "--extra_vars=[...]"
                # Pull the list of vars out as an actual list:
                var_list_str = arg.split("--extra_vars=")[1]
                var_list = ast.literal_eval(var_list_str)
                var_list = [n.strip() for n in var_list]
                # Multiple extra_vars are passed to ansible using multiple --extra-vars arguments.
                # Add one for each arg in our list:
                for v in var_list:
                    self.args.append("--extra-vars={0}".format(v))
                del self.args[i]  # Delete the original arg since we split it into separate ones
                break

        self._prepend_venv_path()

    @staticmethod
    def _prepend_venv_path():
        """
        Modify PATH env variable by prepending virtualenv path with ansible binaries.
        This way venv ansible has precedence over globally installed ansible.
        """
        venv_path = '/opt/stackstorm/virtualenvs/ansible/bin'
        old_path = os.environ.get('PATH', '').split(':')
        new_path = [venv_path] + old_path

        os.environ['PATH'] = ':'.join(new_path)

    def execute(self):
        """
        Execute the command and stream stdout and stderr output
        from child process as it appears without delay.
        Terminate with child's exit code.
        """
        exit_code = subprocess.call(self.cmd, env=os.environ.copy())
        if exit_code is not 0:
            sys.stderr.write('Executed command "%s"\n' % ' '.join(self.cmd))
        sys.exit(exit_code)

    @property
    @shell.replace_args('REPLACEMENT_RULES')
    def cmd(self):
        """
        Get full command line as list.

        :return: Command line.
        :rtype: ``list``
        """
        return [self.binary] + self.args

    @property
    def binary(self):
        """
        Get full path to executable binary.

        :return: Full path to executable binary.
        :rtype: ``str``
        """
        if not self.BINARY_NAME:
            sys.stderr.write('Ansible binary file name was not specified')
            sys.exit(1)

        for path in os.environ.get('PATH', '').split(':'):
            binary_path = os.path.join(path, self.BINARY_NAME)
            if os.path.isfile(binary_path):
                break
        else:
            sys.stderr.write('Ansible binary doesnt exist. Is it installed?')
            sys.exit(1)

        return binary_path
