from .configuration import settings


class BaseAuthenticator:
    def __init__(self, options):
        self.options = options

    async def authenticate(self, credentials) -> bytes:
        raise NotImplementedError()


class TrustAuthenticator(BaseAuthenticator):

    async def authenticate(self, name):
        return name


authenticator = None


def initialize():
    global authenticator
    configuration = settings.authentication
    method = configuration.method
    try:
        authenticator = {'trust': TrustAuthenticator}[method](configuration)
    except KeyError:
        raise ValueError(f'Invalid value for authentication method: {method}')

async def authenticate(credentials):
    parts = credentials.split(b' ')
    if parts[0].lower() != b'login':
        return None
    return await authenticator.authenticate(b' '.join(parts[1:]))

