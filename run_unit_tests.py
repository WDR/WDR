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

# Unit test launcher
#
# Does not require wsadmin, WAS nor WAS client to run. Regular Python or Jython
# should be absolutely enough to run all the tests. Some warnings may be
# logged during WDR imports though.

import sys

sys.path.extend( [ 'lib/common', 'lib/legacy', 'lib/tests' ] )

import logging
import logging.config

logging.config.fileConfig( 'lib/common/logconf.ini' )

import unittest
import wdrtest.config
import wdrtest.manifest
import wdrtest.task

suite = unittest.TestSuite()
suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(wdrtest.config))
suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(wdrtest.manifest))
suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(wdrtest.task))

unittest.TextTestRunner().run(suite)
