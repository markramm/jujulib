

class EnvironmentNotBootstrapped(Exception):

    def __init__(self, environment):
        self.environment = environment

    def __str__(self):
        return "environment %s is not bootstrapped" % self.environment
