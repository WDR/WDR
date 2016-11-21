# Unit test launcher
#
# Needs to be executed agains clean standalone profile.
#
# The topology of this profile is:
# Cell
#   *name vagrant
#   Node
#     *name vagrant
#     Server
#       *name server1

import unittest

import wdrtest.config
import wdrtest.control
import wdrtest.manifest
import wdrtest.task

try:
    suite = unittest.TestSuite()
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromModule(wdrtest.config)
    )
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromModule(wdrtest.control)
    )
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromModule(wdrtest.manifest)
    )
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromModule(wdrtest.task)
    )
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromModule(wdrtest.manifest_format)
    )
    unittest.TextTestRunner().run(suite)
finally:
    reset()
