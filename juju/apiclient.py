import functools
import json
import logging
import ssl
import tempfile
import time

import websocket

from .configstore import ConfigStore


# There are two pypi modules with the name websocket (python-websocket
# and websocket) We utilize python-websocket, sniff and error if we
# find the wrong one.
try:
    websocket.create_connection
except AttributeError:
    raise RuntimeError(
        "Expected 'python-websocket' package or 'websocket-client' from pypi, "
        "found incompatible gevent 'websocket'")


websocket.logger = logging.getLogger("websocket")
logger = logging.getLogger("juju")


class UnknownFacade(Exception):
    """UnknownFacade is raised if the server doesn't have the requested facade.

    This can occur if asking for a non-existent facade, or a newer facade that
    is not supported on the API server, or even a known facade that isn't
    supported at the endpoint that has been connected to.

    """


class FacadeVersionNotSupported(Exception):
    """Raised if the requested facade version isn't supported."""


class ServerError(Exception):
    """Base exception class for particular server side errors.

    If there is no specific error type for the error code returned from the
    server, then this is the type of the returned error.

    """
    def __init__(self, error_code, message):
        super(ServerError, self).__init__(message)
        self.error_code = error_code
        self.message = message

    def __str__(self):
        return "<ServerError - '{}'>".format(self.message)


class NotImplementedError(ServerError):
    """NotImplementedError is raised when a method does not exist.

    The error could be caused due to either the method name being incorrect,
    or the facade version not being supported on the API server, or the facade
    name itself not existing on the server.

    If the Facade instances are being constructed through the Connection
    instance, then the more specialized UnknownFacade and
    FacadeVersionNotSupported errors will be raised, however if a Facade
    instance is created through another method, the NotImplementedError will
    be raised in the cases of bad facade names or versions.

    """
    def __init__(self, *args):
        super(NotImplementedError, self).__init__(*args)


def new_error(response):
    """Constructs a specific exception type based on the ErrorCode."""
    err_code = response.get("ErrorCode")
    message = response.get("Error")
    if err_code == "not implemented":
        return NotImplementedError(err_code, message)
    return ServerError(err_code, message)


class Facade(object):
    """The Facade instances provide convenient syntactic sugar for API calls.

    Facade instances are constructed with a Connection, and facade name and
    version. Any resulting method calls to a facade are translated into RPC
    calls on the connection instance.

    For example, calling the 'FullStatus' method on the client facade:

        >>> client = Facade(connection, "Client")
        >>> result = client.FullStatus()

    This ends up being the same as:

        >>> connection.rpc("Client", "FullStatus")

    """

    def __init__(self, connection, name, version=None):
        self.connection = connection
        self.name = name
        self.version = version

    def __getattr__(self, attr):
        return functools.partial(
            self.connection.rpc, self.name, attr, version=self.version)


class Connection(object):
    """A connection represents an open, authenticated API connection."""
    _request_id = 0
    _upgrade_retry_count = 60
    _upgrade_retry_delay_secs = 1

    def __init__(self, address, cacert, auth_tag, credentials,
                 nonce="", env_uuid=""):
        """The constructor expects the following parameters:

        address: an string representing <host>:<port> where the host is either
        an IP address or a hostname.

        cacert: the standard textual PEM representation of the certificate
        used by the API server to authenticate requests.

        auth_tag: a string representation of the user, machine, or unit tag
        that we are connecting to the API as.

        credentials: a string representing the password or in the future, a
        macaroon that is used to authenticate the entity represented by the
        auth_tag.

        nonce: a string representing the nonce used when provisioning the
        machine. This is only used by machine connections to the API server.

        env_uuid: a string representation of the environment UUID. If the
        env_uuid is not specified the connection path is the root ('/'), and
        for modern Juju systems will be a connection to the System, but not an
        Environment.

        """
        self._cert_file = self._write_cert(cacert)
        endpoint = self._endpoint(address, env_uuid)
        cert_path = self._cert_file.name
        self._connection = self._connect(endpoint, cert_path)
        self._info = self._authenticate(auth_tag, credentials, nonce)
        self._generate_facades()

    def _authenticate(self, auth_tag, credentials, nonce):
        # Start with version 2 of admin facade and work our way back.
        for version in (2, 1, 0):
            try:
                self._auth_creds = self._login_args(
                    version, auth_tag, credentials, nonce)
                return self.rpc(
                    "Admin", "Login", self._auth_creds, version=version)
            except NotImplementedError:
                # do nothing and try the previous version
                pass
        raise RuntimeError("unexpected missing login command")

    @staticmethod
    def _login_args(version, auth_tag, credentials, nonce):
        if version == 0:
            args = {"AuthTag": auth_tag, "Password": credentials}
            if nonce is not None:
                args['Nonce'] = nonce
            return args
        # Otherwise, use the newer login structure.
        args = {"auth-tag": auth_tag, "credentials": credentials}
        if nonce is not None:
            args['nonce'] = nonce
        return args

    @staticmethod
    def _connect(endpoint, cert_path):
        sslopt = {
            'ssl_version': ssl.PROTOCOL_TLSv1,
            'ca_certs': cert_path,
            'check_hostname': False,
        }
        return websocket.create_connection(
            endpoint, origin=endpoint, sslopt=sslopt)

    @staticmethod
    def _endpoint(address, env_uuid):
        endpoint = "wss://%s" % address
        if env_uuid:
            endpoint += "/environment/%s/api" % env_uuid
        return endpoint

    @staticmethod
    def _write_cert(cert):
        """Write ssl CA cert into a temp file, and return the filename."""
        # Note: we purposefully don't close the file as the temp file will be
        # deleted as soon as it is closed. Since we leave it open, the file
        # will be closed as the process finishes, and it removes the temporary
        # file. Also we have a reference to the temporary file that exists for
        # the lifetime of the connection instance. This way we are sure that
        # the temporary file is around for the duration of its use.
        f = tempfile.NamedTemporaryFile(suffix='.pem')
        f.write(cert)
        f.flush()
        return f

    def rpc(self, facade, func, params=None, version=None):
        if params is None:
            params = {}
        op = {
            'Type': facade,
            'Request': func,
            'Params': params,
            'RequestId': self._request_id
        }
        if version is not None:
            op['Version'] = version
        self._request_id += 1
        result = self._rpc_retry_if_upgrading(op)
        if 'Error' in result:
            raise new_error(result)
        return result['Response']

    def _rpc_retry_if_upgrading(self, op):
        """If Juju is upgrading when the specified rpc call is made,
        retry the call."""
        retry_count = 0
        while retry_count <= self._upgrade_retry_count:
            result = self._send_request(op)
            if 'Error' in result and 'upgrade in progress' in result['Error']:
                logger.info("Juju upgrade in progress...")
                retry_count += 1
                time.sleep(self._upgrade_retry_delay_secs)
                continue
            break
        return result

    def _send_request(self, op):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("rpc request:\n%s" % (json.dumps(op, indent=2)))
        self._connection.send(json.dumps(op))
        raw = self._connection.recv()
        result = json.loads(raw)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("rpc response:\n%s" % (json.dumps(result, indent=2)))
        return result

    def _generate_facades(self):
        self._facade_versions = dict([
            (facade['Name'], facade['Versions'])
            for facade in self._info['facades']
        ])

    def get_facade(self, name, version=None):
        try:
            versions = self._facade_versions[name]
            if version is None:
                version = max(versions)
            if version in versions:
                return Facade(self, name, version)
            raise FacadeVersionNotSupported(
                "{} version {}".format(name, version))
        except KeyError:
            raise UnknownFacade(name)


def open_environment(env_name):
    """Return an API connection to a named environment.

    The specified environment name is looked up in the user's config store.
    The resulting connection is to the environment endpoint.

    """
    store = ConfigStore()
    info = store.connection_info(env_name)
    auth_tag = "user-{}".format(info['user'])
    credentials = info['password']
    return Connection(
        info['state-servers'][0],
        info['ca-cert'],
        auth_tag, credentials,
        env_uuid=info['environ-uuid'])
