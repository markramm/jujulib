import logging
import websocket

# py 3 first and fall back to py 2
try:
    from http.client import HTTPSConnection
    from io import StringIO
except ImportError:
    from httplib import HTTPSConnection
    from StringIO import StringIO


# There are two pypi modules with the name websocket (python-websocket
# and websocket) We utilize python-websocket, sniff and error if we
# find the wrong one.
try:
    websocket.create_connection
except AttributeError:
    raise RuntimeError(
        "Expected 'python-websocket' "
        "found incompatible gevent 'websocket'")


websocket.logger = logging.getLogger("websocket")
logger = logging.getLogger("juju")

