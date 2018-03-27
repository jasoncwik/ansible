from ansible.module_utils.basic import env_fallback


def ecs_argument_spec():
    return dict(
        endpoint=dict(type='str',
                      required=False,
                      fallback=(env_fallback, ['ECS_ENDPOINT']),
                      ),
        username=dict(type='str',
                      aliases=['user', 'admin'],
                      required=False,
                      fallback=(env_fallback, ['ECS_USER'])),
        password=dict(type='str',
                      aliases=['pass', 'pwd'],
                      required=False,
                      no_log=True,
                      fallback=(env_fallback, ['ECS_PASSWORD'])),
        validate_certs=dict(type='bool',
                            required=False,
                            default=True,
                            fallback=(env_fallback, ['ECS_VALIDATE_CERTS'])),
    )
