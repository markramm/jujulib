import mock
import unittest

import juju.apiclient


class TestFacade(unittest.TestCase):

    def test_simple_call_no_version(self):
        connection = mock.Mock()
        connection._rpc = mock.Mock(return_value='called')

        facade = juju.apiclient.Facade(connection, "FacadeName")
        result = facade.SomeMethod('args')
        self.assertEqual(result, 'called')
        connection._rpc.assert_called_with('FacadeName', 'SomeMethod', 'args', version=None)

    def test_simple_call_explicit_version(self):
        connection = mock.Mock()
        connection._rpc = mock.Mock(return_value='called')

        facade = juju.apiclient.Facade(connection, "FacadeName", 3)
        result = facade.SomeMethod('args')
        self.assertEqual(result, 'called')
        connection._rpc.assert_called_with('FacadeName', 'SomeMethod', 'args', version=3)


class TestConnection(unittest.TestCase):

    def test_login_args(self):
        self.assertEqual(
            juju.apiclient.Connection._login_args(0, 'username', 'password', None),
            {"AuthTag": 'username', "Password": 'password'})
