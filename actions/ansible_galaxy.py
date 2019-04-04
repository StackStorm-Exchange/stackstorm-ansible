#!/opt/stackstorm/st2/bin/python

import sys
from lib.ansible_base import AnsibleBaseRunner

__all__ = [
    'AnsibleGalaxyRunner'
]


class AnsibleGalaxyRunner(AnsibleBaseRunner):
    """
    Runs Ansible galaxy commands: install/remove/list.
    See: http://docs.ansible.com/galaxy.html
    """
    BINARY_NAME = 'ansible-galaxy'
    REPLACEMENT_RULES = {
        '--roles_path': '--roles-path',
        '--ignore_errors': '--ignore-errors',
        '--no_deps': '--no-deps',
        '--role_file': '--role-file',
    }

    def __init__(self, *args, **kwargs):
        super(AnsibleGalaxyRunner, self).__init__(*args, **kwargs)


if __name__ == '__main__':
    AnsibleGalaxyRunner(sys.argv).execute()
