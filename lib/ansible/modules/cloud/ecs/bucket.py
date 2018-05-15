#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: bucket

short_description: Creates new buckets in ECS

version_added: "2.4"

description:
    - "This module creates new buckets in Dell EMC ECS"

options:
    name:
        description:
            - The name of the bucket to create
        required: true
    namespace:
        description:
            - Name of namespace to contain the bucket. 
        required: true
    owner:
        description:
            - Name of object user to own the bucket.
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
id:
    description: The new bucket identifier (namespace.bucket)
    type: str
'''

from ansible.module_utils.basic import AnsibleModule
from util import ecs_argument_spec
from ecsclient.client import Client


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = ecs_argument_spec()
    module_args.update(dict(
        name=dict(type='str', required=True),
        namespace=dict(type='str', required=True),
        owner=dict(type='str', required=True)
    ))

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        secret_key='',
        key_timestamp=''
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

    print('username: %s password: %s' % (module.params['username'], module.params['password']))

    # Connect to ECS
    ecs_client = Client('3',
                        username=module.params['username'],
                        password=module.params['password'],
                        ecs_endpoint=module.params['endpoint'],
                        token_endpoint=module.params['endpoint']+'/login',
                        verify_ssl=module.params['validate_certs'])

    ecs_client.object_user.create(module.params['name'],
                                  module.params['namespace'])

    secret_key = ecs_client.secret_key.create(module.params['name'],
                                 module.params['namespace'])

    result = dict(
        secret_key=secret_key['secret_key'],
        key_timestamp=secret_key['key_timestamp']
    )

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
