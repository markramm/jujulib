import mock
import os
import unittest

import juju.apiclient


class TestFacade(unittest.TestCase):

    def test_simple_call_no_version(self):
        connection = mock.Mock()
        connection.rpc = mock.Mock(return_value='called')

        facade = juju.apiclient.Facade(connection, 'FacadeName')
        result = facade.SomeMethod('args')
        self.assertEqual(result, 'called')
        connection.rpc.assert_called_with('FacadeName', 'SomeMethod', 'args', version=None)

    def test_simple_call_explicit_version(self):
        connection = mock.Mock()
        connection.rpc = mock.Mock(return_value='called')

        facade = juju.apiclient.Facade(connection, 'FacadeName', 3)
        result = facade.SomeMethod('args')
        self.assertEqual(result, 'called')
        connection.rpc.assert_called_with('FacadeName', 'SomeMethod', 'args', version=3)


class TestConnection(unittest.TestCase):

    def test_write_cert(self):
        cert_text = 'some fake cert text'
        f = juju.apiclient.Connection._write_cert(cert_text)
        filename = f.name
        self.assertTrue(filename.endswith('.pem'))
        with open(filename) as cert_file:
            content = cert_file.read()
            self.assertEqual(content, cert_text)

    def test_write_cert_removed_when_closed(self):
        cert_text = 'some fake cert text'
        f = juju.apiclient.Connection._write_cert(cert_text)
        filename = f.name
        f.close()
        self.assertRaises(
            OSError,
            os.stat,
            filename)

    def test_login_args(self):
        self.assertEqual(
            juju.apiclient.Connection._login_args(0, 'username', 'password', None),
            {'AuthTag': 'username', 'Password': 'password'})
        self.assertEqual(
            juju.apiclient.Connection._login_args(0, 'username', 'password', 'a nonce'),
            {'AuthTag': 'username', 'Password': 'password', 'Nonce': 'a nonce'})
        for version in (1, 2):
            self.assertEqual(
                juju.apiclient.Connection._login_args(version, 'username', 'password', None),
                {'auth-tag': 'username', 'credentials': 'password'})
            self.assertEqual(
                juju.apiclient.Connection._login_args(version, 'username', 'password', 'a nonce'),
                {'auth-tag': 'username', 'credentials': 'password', 'nonce': 'a nonce'})

    def test_endpoint(self):
        address = 'localhost:12345'
        self.assertEqual(
            juju.apiclient.Connection._endpoint(address, ''),
            'wss://localhost:12345')
        self.assertEqual(
            juju.apiclient.Connection._endpoint(address, 'env-uuid'),
            'wss://localhost:12345/environment/env-uuid/api')
