#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: metering_facts

short_description: Extracts metering information from ECS.

version_added: "2.4"

description:
    - "This module connects to the ECS metering (billing) API and extracts the requested metrics."

options:
    include_bucket_detail:
        description:
            - If true, include details for each bucket.
        required: false
        type: bool
    csv_file:
        description:
            - If specified, write the metering data in CSV format to the specified file
        required: false
        type: str

extends_documentation_fragment:
    - azure
    
requirements:
  - ecsclient >= 1.1.8
  - python >= 2.6

author:
    - Jason Cwik (@yourhandle)
'''

EXAMPLES = '''
# Pass in a message
- include_bucket_detail: true

'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.modules.cloud.ecs.util import ecs_argument_spec
from ecsclient.client import Client
from ecsclient.common.exceptions import ECSClientException
import csv


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = ecs_argument_spec()
    module_args.update(dict(
        include_bucket_detail=dict(type='bool', required=False, default=False),
        csv_file=dict(type='str', required=False)
    ))

    csv_headers=['namespace', 'sample_time', 'uptodate_till', 'total_objects', 'total_size',
                 'total_mpu_size', 'total_mpu_parts']

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        samples=[]
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

    # Connect to ECS
    ecs_client = Client('3',
                        username=module.params['username'],
                        password=module.params['password'],
                        ecs_endpoint=module.params['endpoint'],
                        token_endpoint=module.params['endpoint']+'/login',
                        verify_ssl=module.params['validate_certs'])

    include_bucket_detail=module.params['include_bucket_detail']

    # Get the list of namespaces.
    namespace_list=ecs_client.namespace.list()
    print("Namespace list: %s" % namespace_list)

    # open output file if needed
    if module.params['csv_file']:
        csv_file = open(module.params['csv_file'], 'w')
        csvwriter = csv.writer(csv_file)
        #csvwriter.writerow(csv_headers)
    else:
        csvwriter=None

    first=True
    for namespace in namespace_list['namespace']:
        print("Namespace: " + namespace['name'])
        namespace_info = ecs_client.billing.get_namespace_billing_info(namespace['name']);
        result['samples'].append(namespace_info)
        if csvwriter:
            if first:
                csvwriter.writerow(namespace_info.keys())
                first=False
            csvwriter.writerow(namespace_info.values())

    if csvwriter:
        csv_file.close()

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()