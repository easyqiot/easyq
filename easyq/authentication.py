from .logging import getlogger
from .configuration import settings


class BaseAuthenticator:
    def __init__(self, options):
        self.options = options

    async def authenticate(self, credentials) -> bytes:
        raise NotImplementedError()


class TrustAuthenticator(BaseAuthenticator):

    async def authenticate(self, name):
        if b':' in name:
            return None
        return name.decode()


authenticator = None
logger = getlogger('AUTH')


def initialize():
    global authenticator
    configuration = settings.authentication
    method = configuration.method
    logger.info(f'Method: {method}')
    try:
        authenticator = {'trust': TrustAuthenticator}[method](configuration)
    except KeyError:
        raise ValueError(f'Invalid value for authentication method: {method}')


async def authenticate(credentials):
    return await authenticator.authenticate(credentials)

