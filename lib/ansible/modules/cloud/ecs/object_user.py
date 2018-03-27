#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: object_user

short_description: Creates new object users in ECS

version_added: "2.4"

description:
    - "This module creates new object users in Dell EMC ECS and returns their secret key"

options:
    name:
        description:
            - The name of the user to create
        required: true
    namespace:
        description:
            - Name of namespace to contain the user. 
        required: true

requirements:
  - ecsclient >= 1.1.8
  - python >= 2.6

extends_documentation_fragment:
    - azure

author:
    - Jason Cwik (@jasoncwik)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_new_test_module:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_new_test_module:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_new_test_module:
    name: fail me
'''

RETURN = '''
secret_key:
    description: The secret key for the new user
    type: str
key_timestamp:
    description: The creation timestamp of the new secret key
new:
    description: Returns true if a user was created.
    type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.modules.cloud.ecs.util import ecs_argument_spec
from ecsclient.client import Client
from ecsclient.common.exceptions import ECSClientException


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = ecs_argument_spec()
    module_args.update(dict(
        name=dict(type='str', required=True),
        namespace=dict(type='str', required=True)
    ))

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        secret_key='',
        key_timestamp='',
        new=False
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if module.params['name'] == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    # Connect to ECS
    ecs_client = Client('3',
                        username=module.params['username'],
                        password=module.params['password'],
                        ecs_endpoint=module.params['endpoint'],
                        token_endpoint=module.params['endpoint']+'/login',
                        verify_ssl=module.params['validate_certs'])

    name=module.params['name']
    namespace=module.params['namespace']

    # See if the object user already exists.
    try:
        ecs_client.object_user.get(name, namespace)

        # Yes, it does.
        secret_key = ecs_client.secret_key.get(name, namespace)
        result = dict(
            secret_key=secret_key['secret_key_1'],
            key_timestamp=secret_key['key_timestamp_1'],
            new=False
        )
        module.exit_json(**result)
        return
    except ECSClientException:
        pass

    ecs_client.object_user.create(name,
                                  namespace)

    secret_key = ecs_client.secret_key.create(name,
                                 namespace)

    result = dict(
        secret_key=secret_key['secret_key'],
        key_timestamp=secret_key['key_timestamp'],
        new=True
    )

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
