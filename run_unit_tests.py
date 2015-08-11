# Unit test launcher
#
# Does not require wsadmin, WAS nor WAS client to run. Regular Python or Jython
# should be absolutely enough to run all the tests. Some warnings may be
# logged during WDR imports though.

import sys

sys.path.extend(['lib/common', 'lib/legacy', 'lib/tests', 'lib/wsadmin'])

import logging
import logging.config

logging.config.fileConfig('lib/common/logconf.ini')

import unittest
import wdrtest.config
import wdrtest.manifest
import wdrtest.task

suite = unittest.TestSuite()
suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(wdrtest.config))
suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(wdrtest.manifest))
suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(wdrtest.task))

unittest.TextTestRunner().run(suite)
