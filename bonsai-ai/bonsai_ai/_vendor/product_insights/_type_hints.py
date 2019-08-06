# This is purely used to assist with type hinting in IDEs. Importing this file has no runtime
# effects whatsoever, but helps IDEs resolve things like List or Optional for type hinting.
# They can't be imported regularly due to the need to support Python 2.

try:
    from typing import *
except ImportError:
    pass
