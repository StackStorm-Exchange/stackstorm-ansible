[![Build Status](https://circleci.com/gh/StackStorm-Exchange/stackstorm-ansible.svg?style=shield)](https://circleci.com/gh/StackStorm-Exchange/stackstorm-ansible)

# <img src="http://www.ansible.com/favicon.ico" width="32px" valign="-3px"/> Ansible Integration Pack
This pack provides [Ansible](http://www.ansible.com/) integration to perform remote operations on both local and remote machines.
After [pack installation](http://docs.stackstorm.com/packs.html#getting-a-pack) all ansible executable files are available in pack virtualenv and ready to use.

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

##### structured output from `ansible.command` and `ansible.command_local`:

To get a JSON object back from `ansible.command*`, set the json parameter to True. This uses ansible's `--tree` output to generate a JSON object with one element per node: `{"node-name": node-ouput}`


```
$ st2 run ansible.command_local become=true module_name=setup json=True
.
id: 594d6657c4da5f08e9ec7c51
status: succeeded
parameters:
  become: true
  json: true
  module_name: setup
result:
  failed: false
  return_code: 0
  stderr: ''
  stdout:
    127.0.0.1:
      ansible_facts:
        ansible_all_ipv4_addresses:
      ...
      changed: false
  succeeded: true
```

With this structured output, you could use the setup module as the first step of a workflow, and then base additional workflow steps on variables from ansible's setup. It should work similarly for other modules.

For instance, if you needed the default ipv4 address of a node, you could publish the appropriate ansible_fact like this (in an action-chain workflow):

```yaml
chain:
  -
    name: ansible_setup
    ref:  ansible.command_local
    parameters:
      become: True
      json: True
      module_name: setup
    publish:
      default_ip: "{{ ansible_setup.stdout['127.0.0.1'].ansible_facts.ansible_default_ipv4.address }}"
```



#### `ansible.playbook` examples
```sh
# run some simple playbook
st2 run ansible.playbook playbook=/etc/ansible/playbooks/nginx.yml

# run playbook on last machine listed in inventory file
st2 run ansible.playbook playbook=/etc/ansible/playbooks/nginx.yml limit='all[-1]'
```

This is an example from a workflow that passes several several different
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

##### Structured output
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
