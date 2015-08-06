__metaclass__ = type

import os
import yaml

from .exceptions import EnvironmentNotBootstrapped


class ConfigStore():
    """The config store contains the cached information about a juju environment.

    The location of this cache is $JUJU_HOME/environments/cache.yaml. If the
    cache.yaml file does not exist, then the config store falls back to
    looking for .jenv files in the $JUJU_HOME/environments directory.
    """

    def __init__(self, directory=None):
        if directory is None:
            directory = self._get_directory()
        self.directory = directory

    def _get_directory(self):
        juju_home = os.path.expanduser(
            os.environ.get('JUJU_HOME', '~/.juju'))
        return os.path.expanduser(os.path.join(juju_home, 'environments'))

    def connection_info(self, name):
        # Look in the cache file first.
        cache_file = os.path.join(self.directory, 'cache.yaml')
        if os.path.exists(cache_file):
            try:
                return self._environment_from_cache(name, cache_file)
            except EnvironmentNotBootstrapped:
                pass
                # Fall through to getting the info from the jenv

        jenv = os.path.join(self.directory, '{}.jenv'.format(name))
        if not os.path.exists(jenv):
            raise EnvironmentNotBootstrapped(name)
        return self._environment_from_jenv(jenv)

    def _environment_from_cache(self, env_name, cache_filename):
        with open(cache_filename) as fh:
            data = yaml.safe_load(fh.read())
            try:
                # environment holds:
                #   user, env-uuid, server-uuid
                environment = data['environment'][env_name]
                server = data['server-data'][environment['server-uuid']]
                return {
                    'user': environment['user'],
                    'password': server['identities'][environment['user']],
                    'environ-uuid': environment['env-uuid'],
                    'server-uuid': environment['server-uuid'],
                    'state-servers': server['api-endpoints'],
                    'ca-cert': server['ca-cert'],
                }
            except KeyError:
                raise EnvironmentNotBootstrapped(env_name)

    def _environment_from_jenv(self, jenv):
        with open(jenv) as fh:
            data = yaml.safe_load(fh.read())
            return data
