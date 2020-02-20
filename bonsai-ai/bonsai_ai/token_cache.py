# pyright: strict
import os
from bonsai_ai.logger import Logger
from msal import SerializableTokenCache
import keyring

log = Logger()


class BonsaiTokenCache(SerializableTokenCache):
    """
    Custom extension of MSAL's SerializableTokenCache class. Writes token cache
    to the current OS's secret store (keychain, Protected Storage System, etc.) so that authentication can persist between CLI
    calls. If a secure storage isn't available by default, it will store the token in plain text in the user's home directory.

    Cache is deserialized from file (if it exists) upon instantiation. The
    AADClient class should use atexit.register() to write any changes to cache
    on exit.

    TODO: write cache to platform keyring rather than a text file (#11932).
    """

    def __init__(self):
        super().__init__()
        self.secure_backend_available = False
        self.supported_backends = ["WinVaultKeyring",
                                    "OS_X.Keyring",
                                    "EncryptedKeyring"]
        try:
            self.available_backend = str(keyring.get_keyring())
            for backend in self.supported_backends:
                if self.available_backend.find(backend) > 0:
                    self.secure_backend_available = True
                    break
            if self.secure_backend_available == True:
                log.debug('Using secure storage to save access token.')
                # ATTENTION: We are intentionally calling keyring.get_password('bonsai-ai', 'bonsai-user') twice.
                # otherwise it doesn't work on windows.
                keyring.get_password('bonsai-ai', 'bonsai-user')
                auth_state = keyring.get_password('bonsai-ai', 'bonsai-user')
                self.deserialize(auth_state)
            else:
                log.debug('Secure storage not found, using palin text to store user access token.')
                home = os.path.expanduser('~')
                if len(home) > 0:
                    self._cache_file = os.path.join(home, '.aadcache')
                else:
                    raise Exception('Unable to find home directory.')
                with open(self._cache_file, 'r') as f:
                    self.deserialize(f.read())

            log.debug('Existing token cache found, '
                      'populating cache from file.')
        except FileNotFoundError:
            log.debug('No exisiting token cache found, will create a new one.')
        except keyring.errors.InitError as e:
            log.debug('Error while initializing keyring.')
            log.debug(e)
        except keyring.errors.KeyringError as e:
            log.debug('Error while getting password from keyring')
            log.debug(e)


    def write_cache_to_file(self):
        if self.has_state_changed:
            log.debug('Token cache changed, updating...')
            if self.secure_backend_available:
                try:
                    keyring.set_password('bonsai-ai', 'bonsai-user', self.serialize())
                except keyring.errors.PasswordSetError as e:
                    log.debug('Error writing token to the system secure storage')
                    log.debug(e)
            else:
                with open(self._cache_file, 'w') as f:
                    f.write(self.serialize())
