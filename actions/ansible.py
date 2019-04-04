#!/opt/stackstorm/st2/bin/python

import sys
from lib.ansible_base import AnsibleBaseRunner

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
        super(AnsibleRunner, self).__init__(*args, **kwargs)


if __name__ == '__main__':
    AnsibleRunner(sys.argv).execute()
