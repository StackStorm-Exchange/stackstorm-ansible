# Changelog

## v0.6.0

* Add a json parameter to `ansible.command` and `ansible.command_local` actions. When False (the default), stdout is not changed. When True, this replaces ansible's stdout with a valid JSON object. We do this by using ansible's `--tree` argument to save the output to a temporary directory, and then sending a json object where the node name is the key, and the ansible output is the value.

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


## v0.5.0

* Added ability to use yaml structures to pass arbitrarily complex values through extra_vars. key=value and @file syntax is still supported. Example usage:
```yaml
sample_task:
  action: ansible.playbook
  input:
    playbook: playbook.yml
    extra_vars:
      - key1=value1
      -
        key2: value2
        key3: [ value3a, value3b ]
        key4:
          - value4a
          - { value4bkey: value4bvalue }
        key5:
          key6: value6
          key7: value7
      - @path/to/file.yml
        ...
```

## v0.4

* Breaking Change: Added ability to pass in multiple extra_vars. The extra_vars parameter is now a list. Example usage:
```yaml
sample_task:
  action: ansible.playbook
  input:
    playbook: playbook.yml
    extra_vars: 
      - "@path/to/file.yml"
      - "@path/to/file.json"
      - key1=value1
      - key2={{ _.value2 }}
        ...
```

## v0.3

* Removed immutable flag for `sudo:` parameters for all actions. Default is `true`, which means that ansible commands are run with sudo (as root). Good thing is you can change it to `false` when required.

## v0.2

* Breaking Change: Replaced all dashes in parameter names with underscores (adhere to the spec of Jinja/Python variables)

## v0.1.1

* Prepend sandboxed path with ansible binaries to PATH env variable, allowing ansible binary discovery to follow PATH order

## v0.1.0

* Initial release with actions included:
 * `ansible.playbook`
 * `ansible.command`
 * `ansible.command_local`
 * `ansible.galaxy.install`
 * `ansible.galaxy.list`
 * `ansible.galaxy.remove`
 * `ansible.vault.encrypt`
 * `ansible.vault.decrypt`
