from .configuration import settings


class BaseAuthenticator:
    def __init__(self, options):
        pass


class TrustAuthenticator(BaseAuthenticator):
    pass


authenticator = None


def initialize():
    global authenticator
    configuration = settings.server.authentication
    method = configuration.method
    try:
        authenticator = {'trust': TrustAuthenticator}[method](configuration)
    except KeyError:
        raise ValueError(f'Invalid value for authentication method: {method}')

def authenticate(credentials):
    authenticator.authenticate(credentials)

