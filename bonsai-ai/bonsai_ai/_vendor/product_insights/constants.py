import platform
import sys

import product_insights


_uname = platform.uname()

tenant = 'AST'
os_platform = _uname[0]
language_platform = 'Python_' + str(sys.version_info.major)
projection = 'no'
pi_version = product_insights.__version__

version_string = '{version}-{os}-{language}-{projection}-{sdk_version}'.format(
    version=tenant, os=os_platform, language=language_platform, projection=projection, sdk_version=pi_version
)
