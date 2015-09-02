import types
import unittest

import wdr
from wdr.app import * #noqa
from wdr.config import * #noqa
from wdr.control import * #noqa
from wdr.manifest import * #noqa
from wdr.util import * #noqa
from wdrtest.topology import Topology

(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()


logger = logging.getLogger('wdr.test.control')


class AbstractControlTest(unittest.TestCase):
    def assertTrue(self, value, msg=None):
        self.assertNotEqual(0, value, msg)

    def assertFalse(self, value, msg=None):
        self.assertEqual(0, value, msg)


class MBeanAttributeTest(AbstractControlTest):
    def testReadingSimpleAttribute(self):
        srv = getMBean1(
            type='Server',
            node=Topology.nodeName, process=Topology.serverName
        )
        self.assertEquals(srv.name, Topology.serverName)

    def testWritingSimpleAttribute(self):
        jvm = getMBean1(
            type='JVM',
            node=Topology.nodeName, process=Topology.serverName
        )
        jvm.maxHeapDumpsOnDisk = 1234
        self.assertEquals(jvm.maxHeapDumpsOnDisk, 1234)
        jvm.maxHeapDumpsOnDisk = 1
        self.assertEquals(jvm.maxHeapDumpsOnDisk, 1)


class MBeanOperationTest(AbstractControlTest):
    def testInvokeSimpleOperation(self):
        jvm = getMBean1(
            type='JVM',
            node=Topology.nodeName, process=Topology.serverName
        )
        t1 = jvm.getCurrentTimeInMillis()
        t2 = jvm.getCurrentTimeInMillis()
        self.assertTrue(0 < t1)
        self.assertTrue(t1 <= t2)

    def testInvokeOperationReturningList(self):
        ts = getMBean1(
            type='TraceService',
            node=Topology.nodeName, process=Topology.serverName
        )
        groups = ts.listAllRegisteredComponents()
        self.assertTrue('ConnLeakLogic' in groups)
        self.assertTrue(isinstance(groups, types.ListType))
