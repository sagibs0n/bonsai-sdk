from __future__ import absolute_import

import glob
import os
import sys


# This module does some magic to make any .eggs or modules within _lib accessible from the global PYTHONPATH (sys.path).
# This module must be imported, and set_paths() must be called before trying to import modules from this location.


def set_paths():
    """
    Ensures that all libraries within this module are importable
    """
    path = os.path.split(__file__)[0]

    sys.path.append(path)

    if os.path.exists(path):
        # This check is done to see if we're running from a .egg or .zip file. If we're fully installed,
        # this block executes. If running from a bundle, it won't.
        for egg in glob.glob(os.path.join(path, '*.egg')):
            sys.path.append(egg)


def get_eggs():
    # type: () -> List[str]
    """
    Returns a list of paths for each .egg file in this module
    :return: a list of strings naming each .egg file in this module
    """
    return glob.glob(os.path.join(os.path.split(__file__)[0], '*.egg'))


set_paths()
