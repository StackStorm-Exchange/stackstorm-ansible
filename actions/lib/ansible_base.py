import os
import sys
import subprocess
import ast
import json
import six

from . import shell

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
        self._parse_extra_vars()  # handle multiple entries in --extra_vars arg
        self._prepend_venv_path()

    def _parse_extra_vars(self):
        """
        This method turns the string list ("--extra_vars=[...]") passed in from the args
        into an actual list and adds new --extra-vars kwargs for file and k\v entries.

        Example (line breaks added for readability):
          Input from args:
            "--extra_vars=[u'"@path/to/vars_file.yml"',
                           u'"key1=value1", u'"key2=value2"',
                           {u'"key3"': u'"value3"'}]"
          Passed to Ansible after transformation:
            ... --extra-vars=@path/to/vars_file.yml
                --extra-vars=key1=value1 key2=value2
                --extra-vars='{"key3": "value3"}'...
        """
        for i, arg in enumerate(self.args):
            if '--extra_vars' in arg:
                var_list_str = arg.split("--extra_vars=")[1]
                var_list = []
                for n in ast.literal_eval(var_list_str):
                    if isinstance(n, six.string_types):
                        if n.strip().startswith("@"):
                            var_list.append(('file', n.strip()))
                        else:
                            var_list.append(('kwarg', n.strip()))
                    elif isinstance(n, dict):
                        var_list.append(('json', n))

                last = ''
                kv_param = ''
                for t, v in var_list:
                    # Add --extra-vars for each file
                    if t == 'file':
                        self.args.append("--extra-vars={0}".format(v))

                    # Add --extra-vars for each json object
                    elif t == 'json':
                        self.args.append("--extra-vars={0}".format(json.dumps(v)))

                    # Combine contiguous kwarg vars into a single space-separated --extra-vars kwarg
                    elif t == 'kwarg' and last != t:
                        kv_param = "--extra-vars={0}".format(v)
                    elif t == 'kwarg':  # last == t
                        kv_param += " {0}".format(v)

                    if last == 'kwarg' and t != last:
                        self.args.append(kv_param)
                        kv_param = ""

                    last = t

                if kv_param:
                    self.args.append(kv_param)

                del self.args[i]  # Delete the original arg since we split it into separate ones
                break

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
        if exit_code != 0:
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
