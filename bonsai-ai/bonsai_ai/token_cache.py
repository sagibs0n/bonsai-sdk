# pyright: strict
import os
from bonsai_ai.logger import Logger
from msal import SerializableTokenCache

log = Logger()


class BonsaiTokenCache(SerializableTokenCache):
    """
    Custom extension of MSAL's SerializableTokenCache class. Writes token cache
    to user's HOME directory so that authentication can persist between CLI
    calls.

    Cache is deserialized from file (if it exists) upon instantiation. The
    AADClient class should use atexit.register() to write any changes to cache
    on exit.

    TODO: write cache to platform keyring rather than a text file (#11932).
    """

    def __init__(self):
        super().__init__()
        home = os.path.expanduser('~')
        if len(home) > 0:
            self._cache_file = os.path.join(home, '.aadcache')
        else:
            raise Exception('Unable to find home directory.')
        try:
            with open(self._cache_file, 'r') as f:
                self.deserialize(f.read())
            log.debug('Existing token cache found, '
                      'populating cache from file.')
        except FileNotFoundError:
            log.debug('No exisiting token cache found, will create a new one.')

    def write_cache_to_file(self):
        if self.has_state_changed:
            log.debug('Token cache changed, '
                      'updating {}'.format(self._cache_file))
            with open(self._cache_file, 'w') as f:
                f.write(self.serialize())
