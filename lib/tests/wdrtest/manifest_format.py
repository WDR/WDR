import unittest
import string
import wdr
from wdr.app import * #noqa
from wdr.config import * #noqa
from wdr.control import * #noqa
from wdr.manifest import * #noqa
from wdr.util import * #noqa
from wdrtest.topology import topology

(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()


class AbstractConfigTest(unittest.TestCase):
    def tearDown(self):
        reset()

    def assertTrue(self, value, msg=None):
        self.assertNotEqual(0, value, msg)

    def assertFalse(self, value, msg=None):
        self.assertEqual(0, value, msg)

    def assertNone(self, value, msg=None):
        if value is not None:
            raise AssertionError(msg or '%s not None' % value)

    def assertNotNone(self, value, msg=None):
        if value is None:
            raise AssertionError(msg or '%s not None' % value)

manifestPaths = [
    ['wdrtest/manifests/format/tabs'], ['wdrtest/manifests/format/spaces']
]

class FormatTest(AbstractConfigTest):
    def testObjectWithSimpleAttributes(self):
        for mp in manifestPaths:
            mos = loadConfigurationManifest(
                'object_with_simple_attributes.wdrc', {}, mp
            )
            self.assertEqual(len(mos), 1)
            mo = mos[0]
            self.assertEqual(mo.type, "Root")
            self.assertEqual(mo.keys, {'name': 'root'})
            self.assertEqual(mo.items, [
                {'name':'a1', 'value': 'v1', 'attribute': 1},
                {'name':'a2', 'value': 'v2', 'attribute': 1}
            ])

    def testObjectWithChild(self):
        for mp in manifestPaths:
            mos = loadConfigurationManifest(
                'object_with_child.wdrc', {}, mp
            )
            self.assertEqual(len(mos), 1)
            mo = mos[0]
            self.assertEqual(mo.type, "Root")
            self.assertEqual(mo.keys, {'name': 'root'})
            self.assertEqual(mo.items[:2], [
                {'name':'a1', 'value': 'v1', 'attribute': 1},
                {'name':'a2', 'value': 'v2', 'attribute': 1}
            ])
            self.assertTrue(mo.items[2]['child'])
            child = mo.items[2]['value']
            self.assertEqual(child.type, "Child")
            self.assertEqual(child.keys, {'name': 'child'})
            self.assertEqual(child.items, [
                {'name':'a1', 'value': 'V1', 'attribute': 1},
                {'name':'a2', 'value': 'V2', 'attribute': 1}
            ])

    def testObjectWithChildren(self):
        for mp in manifestPaths:
            mos = loadConfigurationManifest(
                'object_with_children.wdrc', {}, mp
            )
            self.assertEqual(len(mos), 1)
            mo = mos[0]
            self.assertEqual(mo.type, "Root")
            self.assertEqual(mo.keys, {'name': 'root'})
            self.assertEqual(mo.items[:2], [
                {'name':'a1', 'value': 'v1', 'attribute': 1},
                {'name':'a2', 'value': 'v2', 'attribute': 1}
            ])
            self.assertTrue(mo.items[2]['child'])
            child = mo.items[2]['value']
            self.assertEqual(child.type, "Child")
            self.assertEqual(child.keys, {'name': 'child1'})
            self.assertEqual(child.items, [
                {'name':'a1', 'value': 'V11', 'attribute': 1},
                {'name':'a2', 'value': 'V12', 'attribute': 1}
            ])
            child = mo.items[3]['value']
            self.assertEqual(child.type, "Child")
            self.assertEqual(child.keys, {'name': 'child2'})
            self.assertEqual(child.items, [
                {'name':'a1', 'value': 'V21', 'attribute': 1},
                {'name':'a2', 'value': 'V22', 'attribute': 1}
            ])

    def testObjectWithAttributeChildren(self):
        for mp in manifestPaths:
            mos = loadConfigurationManifest(
                'object_with_attribute_children.wdrc', {}, mp
            )
            self.assertEqual(len(mos), 1)
            mo = mos[0]
            self.assertEqual(mo.type, "Root")
            self.assertEqual(mo.keys, {'name': 'root'})
            self.assertEqual(mo.items[:2], [
                {'name':'a1', 'value': 'v1', 'attribute': 1},
                {'name':'a2', 'value': 'v2', 'attribute': 1}
            ])
            self.assertTrue(mo.items[2]['attribute'])
            children = mo.items[2]['value']
            self.assertEqual(children[0].type, "Child")
            self.assertEqual(children[0].keys, {'name': 'child1'})
            self.assertEqual(children[0].items, [
                {'name':'a1', 'value': 'V11', 'attribute': 1},
                {'name':'a2', 'value': 'V12', 'attribute': 1}
            ])
            self.assertEqual(children[1].type, "Child")
            self.assertEqual(children[1].keys, {'name': 'child2'})
            self.assertEqual(children[1].items, [
                {'name':'a1', 'value': 'V21', 'attribute': 1},
                {'name':'a2', 'value': 'V22', 'attribute': 1}
            ])
