[![Build Status](https://circleci.com/gh/StackStorm-Exchange/stackstorm-ansible.svg?style=shield)](https://circleci.com/gh/StackStorm-Exchange/stackstorm-ansible)

# <img src="http://www.ansible.com/favicon.ico" width="32px" valign="-3px"/> Ansible Integration Pack
This pack provides [Ansible](http://www.ansible.com/) integration to perform remote operations on both local and remote machines.
After [pack installation](http://docs.stackstorm.com/packs.html#getting-a-pack) all ansible executable files are available in pack virtualenv and ready to use.

## Requirements
This pack installs Ansible from `pip` and therefore may require some OS-level packages to be in place.
Ubuntu:
```
sudo apt-get install gcc libkrb5-dev
```
RHEL/CentOS:
```
sudo yum install gcc krb5-devel
```

## Actions
* `command` - Run single [Ad-Hoc command](http://docs.ansible.com/intro_adhoc.html). It has all the regular parameters of `ansible` executable.
* `command_local` - Perform single ansible Ad-Hoc command (module) locally.
* `playbook` - Action to run [Ansible Playbook](http://docs.ansible.com/playbooks.html) (`ansible-playbook` executable).
* `vault.encrypt` - Encrypt ansible data files (playbooks, vars, roles, etc) with password (`ansible-vault` executable).
* `vault.decrypt` - Decrypt ansible data files (playbooks, vars, roles, etc) with password (`ansible-vault` executable).
* `galaxy.install` - Install role from [Ansible Galaxy](http://docs.ansible.com/galaxy.html) - hub of [community developed roles](https://galaxy.ansible.com/) (`ansible-galaxy`).
* `galaxy.list` - List installed from Ansible Galaxy roles (`ansible-galaxy` executable).
* `galaxy.remove` - Remove the role installed from Ansible Galaxy (`ansible-galaxy` executable).

## Examples
See [StackStorm with Ansible on Vagrant demo](https://github.com/StackStorm/st2-ansible-vagrant) for more examples

#### `ansible.command` examples
```sh
# run ansible command with optional verbose parameter
st2 run ansible.command hosts=all args='hostname -i' verbose=vv
```

Action `ansible.command_local` is helper for the `ansible.command` with predefined parameters to run the command locally. So this is the same:
```sh
st2 run ansible.command_local args='echo $TERM'
st2 run ansible.command connection=local inventory_file='127.0.0.1,' hosts=all args='echo $TERM'
```
which is equivalent of ansible commands:
```sh
ansible all -c local -i '127.0.0.1,' -a 'echo $TERM'
ansible all --connection=local --inventory-file='127.0.0.1,' --args='echo $TERM'
```

#### `ansible.playbook` examples
```sh
# run some simple playbook
st2 run ansible.playbook playbook=/etc/ansible/playbooks/nginx.yml

# run playbook on last machine listed in inventory file
st2 run ansible.playbook playbook=/etc/ansible/playbooks/nginx.yml limit='all[-1]'
```

#### `ansible.vault` examples
```sh
# encrypt /tmp/nginx.yml playbook with password containing in vault.txt
st2 run ansible.vault.encrypt vault_password_file=vault.txt files=/tmp/nginx.yml

# decrypt /etc/ansible/nginx.yml and /etc/ansible/db.yml files
st2 run ansible.vault.decrypt cwd=/etc/ansible vault_password_file=vault.txt files='nginx.yml db.yml'

# decrypt all files in /etc/ansible/playbooks directory
st2 run ansible.vault.decrypt cwd=/etc/ansible vault_password_file=vault.txt files='playbooks/*'
```

#### `ansible.galaxy` examples
```sh
# download many roles
st2 run ansible.galaxy.install roles='bennojoy.mysql kosssi.composer'

# list rolex
st2 run ansible.galaxy.list roles_path=/etc/ansible/roles
```

## Tips & Tricks
#### Using Ansible `extra_vars` in StackStorm Workflow
This is an example from a workflow that passes several different
variables to the playbook as extra-vars:

```yaml
sample_task:
  action: ansible.playbook
  input:
    playbook: /path/to/playbook.yml
    extra_vars:
      #
      # as key=value pairs
      - key1=value1
      - key2=value2
      #
      # variables from a yaml (or json) file
      - '@/path/to/file.yml'
      #
      # an arbitrarily complex dict of variables (passed as JSON to ansible)
      -
        key3: "{{ value3 }}"
        key4: [ value4a, value4b ]
        key5:
          - value5a
          - { value5bkey: value5bvalue }
        key6:
          key7: value7
          key8: value8
```

#### Structured output
```sh
# get structured JSON output from a playbook
st2 run ansible.playbook playbook=/etc/ansible/playbooks/nginx.yml env='{"ANSIBLE_STDOUT_CALLBACK":"json"}'
```
Using the JSON stdout_callback leads to JSON output which enables access to details of the result of the playbook in actions following the playbook execution, e.g. posting the results to Slack in an action-alias.
```yaml
format: | 
    *Execution Overview*
    {% for host, result in execution.result.stdout.stats.iteritems() %}
        {{ host }}: ```{{ result }}```
    {% endfor %}
```
There is, however, a bug that breaks the JSON when the playbook execution fails (example output below). See [this issue](https://github.com/ansible/ansible/issues/17122) for more information. Manual handling of this case is necessary until the bug is fixed.
```
	to retry, use: --limit @/etc/ansible/playbooks/top.retry
{
    "plays": [
        {
            "play": {
                "id": "b5fe7b50-9d7d-4927-ac17-6886218bcabc", 
                "name": "some-host.com"
            }, 
            ...
}
```

#### Relative path to playbooks within StackStorm workflows
Current working directory (`CWD`) defaults to pack dir you're invoking Ansible pack actions from.
That means if you're calling `ansible.playbook` from the `custom.workflow`, then you can use relative path to playbooks you'd ship with the `custom` pack (infra-as-code, yeah).
```
version: '2.0'
custom.workflow:
  description: A sample workflow that demonstrates how to use relative paths to playbooks shipped with pack.
  type: direct
  tasks:
    a:
      action: ansible.playbook
      input:
        # 'ansible_play.yml' is part of the 'custom' pack
        playbook: "ansible_play.yml"
        inventory_file: "localhost,"
```
This eliminates the need to specify absolute path to Ansible playbook file, located somewhere in `/opt/stackstorm/packs/...`.

#### Windows Hosts
Connecting to windows is possibe as of version `v0.5.2` of this pack.
This is accomplished using ansible's [builtin windows support](http://docs.ansible.com/ansible/latest/intro_windows.html).

Prior to executing a playbook on a Windows host, the host must be configured to
accept WinRM connections. To accomplish this, execute the ansible [setup PowerShell script](https://github.com/ansible/ansible/blob/devel/examples/scripts/ConfigureRemotingForAnsible.ps1)
on every Windows host you connect to. We recommend performing this on your
Windows VM templates.

The following `extra_vars` must be passed in when executing a playbook on a Windows host:

* `ansible_user` : User to connect as (prefer user@domain.tld over domain\user)
* `ansible_password` : Password to use when connecting
* `ansible_connection` : Connection method to use (`winrm` for windows)
* `ansible_port` : Port to use for the connection (`5986` for WinRM)
* `ansible_winrm_transport` : WinRM transport to use for the connection (suggested: `ntlm` or `credssp`, for more information consult the [pywinrm documentation](https://github.com/diyan/pywinrm/).
* `ansible_winrm_server_cert_validation` : Should the SSL cert be validated. (suggested: `ignore`)


Connecting via NTLM using a `user@domain.tld` style login:

``` sh
st2 run ansible.playbook playbook=/etc/ansible/playbooks/windows_playbook.yaml inventory_file="winvm01.domain.tld," extra_vars='["ansible_user=user@domain.tld","ansible_password=xxx","ansible_port=5986","ansible_connection=winrm","ansible_winrm_server_cert_validation=ignore","ansible_winrm_transport=ntlm"]'
```

Connecting via CredSSP using a `DOMAIN\user` style login (note the extra `\`):

``` sh
st2 run ansible.playbook playbook=/etc/ansible/playbooks/windows_playbook.yaml inventory_file="winvm01.domain.tld," extra_vars='["ansible_user=DOMAIN\\\\user","ansible_password=xxx","ansible_port=5986","ansible_connection=winrm","ansible_winrm_server_cert_validation=ignore","ansible_winrm_transport=credssp"]'
```
