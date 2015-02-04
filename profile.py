#
# Copyright 2012-2015 Marcin Plonka <mplonka@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys, os

def _findLogConfFile( logconfFile = 'logconf.ini' ):
    logconfPath = sys.path
    logconfPath.reverse()
    for dirname in logconfPath:
        candidate = os.path.join( dirname, logconfFile )
        if os.path.isfile( candidate ):
            return candidate
    raise Exception( 'Cannot find logconf.ini' )

import logging
import logging.config
logging.config.fileConfig( _findLogConfFile() )

import wdr
from wdr.app import *
from wdr.config import *
from wdr.control import *
from wdr.task import *
from wdr.manifest import *
from wdr.util import *

wdr.versionInfo()

