# pyright: strict
import os
from bonsai_ai.logger import Logger
from msal import SerializableTokenCache

from typing import Optional

log = Logger()

_WORKSPACE_CACHE_KEY = 'BONSAI_WORKSPACE'

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
        if 'HOME' in os.environ:
            self._cache_file = os.path.join(os.environ['HOME'], '.aadcache')
        else:
            self._cache_file = os.path.join(os.getcwd(), '.aadcache')
        try:
            with open(self._cache_file, 'r') as f:
                self.deserialize(f.read())
            log.debug('Existing token cache found, '
                      'populating cache from file.')
        except FileNotFoundError:
            log.debug('No exisiting token cache found, will create a new one.')

    def set_workspace(self, workspace: str):
        self._cache[_WORKSPACE_CACHE_KEY] = workspace
        self.has_state_changed = True
    
    def get_workspace(self) -> Optional[str]:
        return self._cache.get(_WORKSPACE_CACHE_KEY)

    def write_cache_to_file(self):
        if self.has_state_changed:
            log.debug('Token cache changed, '
                      'updating {}'.format(self._cache_file))
            with open(self._cache_file, 'w') as f:
                f.write(self.serialize())
