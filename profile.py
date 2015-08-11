import os
import sys


def _findLogConfFile(logconfFile='logconf.ini'):
    logconfPath = sys.path
    logconfPath.reverse()
    for dirname in logconfPath:
        candidate = os.path.join(dirname, logconfFile)
        if os.path.isfile(candidate):
            return candidate
    raise Exception('Cannot find logconf.ini')


import logging
import logging.config

logging.config.fileConfig(_findLogConfFile())

import wdr
from wdr.app import * # noqa
from wdr.config import * # noqa
from wdr.control import * # noqa
from wdr.task import * # noqa
from wdr.manifest import * # noqa
from wdr.util import * # noqa

wdr.versionInfo()
