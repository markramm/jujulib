import copy
import mock
import os
import shutil
import tempfile
import unittest
import yaml

from juju import configstore
from juju.exceptions import EnvironmentNotBootstrapped


SAMPLE_CONFIG = {
    'user': 'tester',
    'password': 'sekrit',
    'environ-uuid': 'some-uuid',
    'server-uuid': 'server-uuid',
    'state-servers': ['localhost:12345'],
    'ca-cert': 'test-cert',
}


class TestConfigStore(unittest.TestCase):

    @mock.patch.dict(os.environ, JUJU_HOME='/test/juju/home')
    def test_configstore_default_uses_juju_home(self):
        store = configstore.ConfigStore()
        expected = os.path.join(os.environ['JUJU_HOME'], 'environments')
        self.assertEqual(store.directory, expected)

    @mock.patch.dict(os.environ, HOME='/test/home', clear=True)
    def test_get_juju_home_through_home(self):
        store = configstore.ConfigStore()
        expected = os.path.join(os.environ['HOME'], '.juju', 'environments')
        self.assertEqual(store.directory, expected)

    def test_configstore_directory_set(self):
        store = configstore.ConfigStore('/use/this/dir')
        self.assertEqual(store.directory, '/use/this/dir')

    def test_parse_env_missing(self):
        temp_juju_home = self.mkdir()
        with mock.patch.dict('os.environ', {'JUJU_HOME': temp_juju_home}):
            store = configstore.ConfigStore()
            self.assertRaises(
                EnvironmentNotBootstrapped,
                store.connection_info,
                'missing')

    def test_parse_env_jenv(self):
        temp_juju_home = self.mkdir()
        self.write_jenv(temp_juju_home, 'test-env', SAMPLE_CONFIG)
        with mock.patch.dict('os.environ', {'JUJU_HOME': temp_juju_home}):
            store = configstore.ConfigStore()
            env = store.connection_info('test-env')
            self.assertEqual(env, SAMPLE_CONFIG)

    def test_parse_cache_file(self):
        temp_juju_home = self.mkdir()
        self.write_cache_file(temp_juju_home, 'test-env', SAMPLE_CONFIG)
        with mock.patch.dict('os.environ', {'JUJU_HOME': temp_juju_home}):
            store = configstore.ConfigStore()
            env = store.connection_info('test-env')
            self.assertEqual(env, SAMPLE_CONFIG)

    def test_parse_cache_file_missing_env(self):
        """Create a valid cache file, but look for an environment that isn't there.
        """
        temp_juju_home = self.mkdir()
        self.write_cache_file(temp_juju_home, 'test-env', SAMPLE_CONFIG)
        with mock.patch.dict('os.environ', {'JUJU_HOME': temp_juju_home}):
            store = configstore.ConfigStore()
            self.assertRaises(
                EnvironmentNotBootstrapped,
                store.connection_info,
                'missing')

    def test_parse_env_cache_file_first(self):
        """The cache file has priority over a jenv file."""
        temp_juju_home = self.mkdir()
        content = copy.deepcopy(SAMPLE_CONFIG)
        self.write_jenv(temp_juju_home, 'test-env', content)
        # Now change the password.
        content['password'] = 'new password'
        self.write_cache_file(temp_juju_home, 'test-env', content)
        with mock.patch.dict('os.environ', {'JUJU_HOME': temp_juju_home}):
            store = configstore.ConfigStore()
            env = store.connection_info('test-env')
            self.assertEqual(env, content)

    def mkdir(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d)
        return d

    def write_jenv(self, juju_home, env_name, content):
        env_dir = os.path.join(juju_home, 'environments')
        if not os.path.exists(env_dir):
            os.mkdir(env_dir)
        jenv = os.path.join(env_dir, '{}.jenv'.format(env_name))
        with open(jenv, 'w') as f:
            yaml.dump(content, f, default_flow_style=False)

    def write_cache_file(self, juju_home, env_name, content):
        env_dir = os.path.join(juju_home, 'environments')
        if not os.path.exists(env_dir):
            os.mkdir(env_dir)
        filename = os.path.join(env_dir, 'cache.yaml')
        cache_content = {
            'environment': {
                env_name: {'env-uuid': content['environ-uuid'],
                           'server-uuid': content['server-uuid'],
                           'user': content['user']}},
            'server-data': {
                content['server-uuid']: {
                    'api-endpoints': content['state-servers'],
                    'ca-cert': content['ca-cert'],
                    'identities': {content['user']: content['password']}}},
            # Explicitly don't care about 'server-user' here.
            }
        with open(filename, 'w') as f:
            yaml.dump(cache_content, f, default_flow_style=False)
