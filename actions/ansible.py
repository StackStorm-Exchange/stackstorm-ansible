#!/usr/bin/env python

from __future__ import print_function

import json
import os
import shutil
import sys
import tempfile
from lib.ansible_base import AnsibleBaseRunner, ParamaterConflict

__all__ = [
    'AnsibleRunner'
]


class AnsibleRunner(AnsibleBaseRunner):
    """
    Runs ansible ad-hoc command (single module).
    See: http://docs.ansible.com/intro_adhoc.html
    Modules: http://docs.ansible.com/list_of_all_modules.html
    """
    BINARY_NAME = 'ansible'
    REPLACEMENT_RULES = {
        '--verbose=vvvv': '-vvvv',
        '--verbose=vvv': '-vvv',
        '--verbose=vv': '-vv',
        '--verbose=v': '-v',
        '--become_method': '--become-method',
        '--become_user': '--become-user',
        '--inventory_file': '--inventory-file',
        '--list_hosts': '--list-hosts',
        '--module_path': '--module-path',
        '--module_name': '--module-name',
        '--one_line': '--one-line',
        '--private_key': '--private-key',
        '--vault_password_file': '--vault-password-file',
    }

    def __init__(self, *args, **kwargs):
        self.tree_dir = None
        self.one_line = False
        if '--one_line' in args:
            self.one_line = True
        super(AnsibleRunner, self).__init__(*args, **kwargs)

    def handle_json_arg(self):
        if next((True for arg in self.args if arg.startswith('--tree')), False):
            msg = "--json uses --tree internally. Setting both --tree and --json is not supported."
            raise ParamaterConflict(msg)
        execution_id = os.environ.get('ST2_ACTION_EXECUTION_ID', 'EXECUTION_ID_NA')
        self.tree_dir = tempfile.mkdtemp(prefix='{}.'.format(execution_id))

        tree_arg = '--tree={}'.format(self.tree_dir)
        self.args.append(tree_arg)

        # This sends all ansible stdout to /dev/null - if there's anything in there that's not in
        # the --tree output, then it will be lost. Hopefully ansible doesn't print anything truly
        # important... If something breaks, I guess we'll just have to run it without --json
        # to see what is going on.
        self.stdout = open(os.devnull, 'w')

    def output_json(self):
        output = {}
        for host in os.listdir(self.tree_dir):
            # one file per host in tree dir; name of host is name of file
            with open(os.path.join(self.tree_dir, host), 'r') as host_output:
                try:
                    output[host] = json.load(host_output)
                except ValueError:
                    # something is messed up in the json, so include it as a string.
                    host_output.seek(0)
                    output[host] = host_output.read()
        if self.one_line:
            print(json.dumps(output))
        else:
            print(json.dumps(output, indent=2))

    def cleanup(self):
        shutil.rmtree(self.tree_dir)
        self.stdout.close()

    def post_execute(self):
        if self.json_output:
            self.output_json()
            self.cleanup()


if __name__ == '__main__':
    AnsibleRunner(sys.argv).execute()
