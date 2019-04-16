"""
Copyright (C) 2019 Microsoft
"""
import sys

from bonsai_ai.version import __version__

def get_user_info():
    """ Get Information about user that will be passed into
        The 'User-Agent' header with requests """
    platform = sys.platform
    python_version = "{}.{}.{}".format(
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro)
    user_info = "bonsai-ai/{} (python {}; {})".format(
        __version__, python_version, platform)
    return user_info
