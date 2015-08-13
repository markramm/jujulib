from .configstore import ConfigStore
from .exceptions import EnvironmentNotBootstrapped


class Environment(object):
    """Represents an environment in a Juju System.

    The environment may be the initial environment of the system itself.
    """

    def __init__(self, name):
        self.name = name

    @property
    def running(self):
        # If there are cached values saved for the environment then it is, by
        # our definition, running.
        try:
            self.connection_info()
            return True
        except EnvironmentNotBootstrapped:
            return False

    def connection_info(self):
        store = ConfigStore()
        return store.connection_info(self.name)

    def status():
        # work in progress here...
        pass
