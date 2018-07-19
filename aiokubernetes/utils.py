import os
import warnings

import aiokubernetes as k8s


def load_config(config_file=None, context=None, warn=True):
    """Return configuration object to setup your Http library.

    Inputs:
        config_file: str
            Location of kubeconfig to use.
        context: str
            The K8s context in case you have multiple in your kubeconfig file.

    Returns:
        k8s.configuration.Configuration: config object with SSL certs and API token.
    """

    # Search for kubeconfig file in default locations unless the user has
    # specified one.
    if config_file is None:
        config_file = os.path.expanduser(os.environ.get('KUBECONFIG', '~/.kube/config'))

    # Create dummy configuration.
    config = k8s.configuration.Configuration()

    loader = k8s.config.kube_config._get_kube_config_loader_for_yaml_file(
        config_file,
        active_context=context,
        config_persister=None
    )

    # Load the token and refresh it, if necessary. Suppress all warnings if
    # asked. This option will suppress an annoying Google Auth library message
    # that warns about using your kubeconfig file instead of service accounts.
    if warn:
        loader.load_and_set(config)
    else:
        with warnings.catch_warnings(record=True):
            loader.load_and_set(config)
    return config
