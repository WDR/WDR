import types
import unittest

import wdr
from wdr.app import * #noqa
from wdr.config import * #noqa
from wdr.control import * #noqa
from wdr.manifest import * #noqa
from wdr.util import * #noqa
from wdr.config import _parseConfigId, _parseConfigIdList
from wdr.config import _isConfigId, _isConfigIdList
from wdrtest.topology import topology

(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger('wdr.test.config')


class AbstractConfigTest(unittest.TestCase):
    def tearDown(self):
        reset()

    def assertTrue(self, value, msg=None):
        self.assertNotEqual(0, value, msg)

    def assertFalse(self, value, msg=None):
        self.assertEqual(0, value, msg)


class ConfigIdParsingTest(unittest.TestCase):
    def testSimple(self):
        strId = (
            ''
            + 'DefaultDatasource'
            + '('
            + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
            + '|'
            + 'resources.xml'
            + '#'
            + 'DataSource_1234567890123'
            + ')'
        )
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, 'DefaultDatasource')
        self.assertEquals(
            cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuoted(self):
        strId = (
            ''
            + '"'
            + 'DefaultDatasource'
            + '('
            + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
            + '|'
            + 'resources.xml'
            + '#'
            + 'DataSource_1234567890123'
            + ')'
            + '"'
        )
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, 'DefaultDatasource')
        self.assertEquals(
            cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedWithSpace(self):
        strId = (
            ''
            + '"'
            + 'Default Datasource'
            + '('
            + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
            + '|'
            + 'resources.xml'
            + '#'
            + 'DataSource_1234567890123'
            + ')'
            + '"'
        )
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, 'Default Datasource')
        self.assertEquals(
            cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedWithLeadingSpace(self):
        strId = (
            ''
            + '"'
            + ' Default Datasource'
            + '('
            + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
            + '|'
            + 'resources.xml'
            + '#'
            + 'DataSource_1234567890123'
            + ')'
            + '"'
        )
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, ' Default Datasource')
        self.assertEquals(
            cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedWithTrailingSpace(self):
        strId = (
            ''
            + '"'
            + 'Default Datasource '
            + '('
            + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
            + '|'
            + 'resources.xml'
            + '#'
            + 'DataSource_1234567890123'
            + ')'
            + '"'
        )
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, 'Default Datasource ')
        self.assertEquals(
            cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testEmptyAdminName(self):
        strId = (
            ''
            + '('
            + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
            + '|'
            + 'resources.xml'
            + '#'
            + 'DataSource_1234567890123'
            + ')'
        )
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, '')
        self.assertEquals(
            cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedEmptyAdminName(self):
        strId = (
            ''
            + '"'
            + '('
            + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
            + '|'
            + 'resources.xml'
            + '#'
            + 'DataSource_1234567890123'
            + ')'
            + '"'
        )
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, '')
        self.assertEquals(
            cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedOnlySpacesInAdminName(self):
        strId = (
            ''
            + '"'
            + ' (cells/wdrCell/nodes/wdrNode/servers/wdrServer'
            + '|'
            + 'resources.xml'
            + '#'
            + 'DataSource_1234567890123'
            + ')'
            + '"'
        )
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, ' ')
        self.assertEquals(
            cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedParenthesisInAdminName(self):
        strId = (
            ''
            + '"'
            + 'Derby JDBC Provider (XA)'
            + '('
            + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
            + '|'
            + 'resources.xml'
            + '#'
            + 'builtin_jdbcprovider'
            + ')'
            + '"'
        )
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, 'Derby JDBC Provider (XA)')
        self.assertEquals(
            cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'builtin_jdbcprovider')

    def testEmptyElementList(self):
        strIds = '[]'
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 0)

    def testOneElementList(self):
        strIds = (
            ''
            + '['
            + 'user.language'
            + '('
            + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
            + '|'
            + 'server.xml'
            + '#'
            + 'Property_1'
            + ')'
            + ']'
        )
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 1)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(
            cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')

    def testMaskedList(self):
        strIds = '*****'
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 0)

    def testReallyLongList(self):
        strIds = (
            '['
            + ' '.join(
                [
                    '(cells/wdrCell|virtualhosts.xml#MimeEntry_%s)' % i
                    for i in range(500)
                ]
            )
            + ']'
        )
        ids = _parseConfigIdList(strIds)
        self.assertEquals(len(ids), 500)
        for i in range(500):
            self.assertEquals(
                '(cells/wdrCell|virtualhosts.xml#MimeEntry_%s)' % i,
                str(ids[i])
            )

    def testTwoElementList(self):
        strIds = (
            ''
            + '['
            + (
                'user.language'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml#Property_1'
                + ')'
            )
            + ' '
            + (
                'user.region'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'Property_2'
                + ')'
            )
            + ']'
        )
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 2)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(
            cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')
        self.assertEquals(cfgIds[1].name, 'user.region')
        self.assertEquals(
            cfgIds[1].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[1].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[1].xmlId, 'Property_2')

    def testThreeElementList(self):
        strIds = (
            ''
            + '['
            + (
                'user.language'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'Property_1'
                + ')'
            )
            + ' '
            + (
                'user.region'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'Property_2'
                + ')'
            )
            + ' '
            + (
                'file.encoding'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'Property_3'
                + ')'
            )
            + ']'
        )
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 3)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(
            cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')
        self.assertEquals(cfgIds[1].name, 'user.region')
        self.assertEquals(
            cfgIds[1].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[1].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[1].xmlId, 'Property_2')
        self.assertEquals(cfgIds[2].name, 'file.encoding')
        self.assertEquals(
            cfgIds[2].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[2].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[2].xmlId, 'Property_3')

    def testOneElementListQuoted(self):
        strIds = (
            ''
            + '['
            + (
                '"'
                + 'user.language'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'Property_1'
                + ')'
                + '"'
            )
            + ']'
        )
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 1)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(
            cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')

    def testTwoElementListQuoted(self):
        strIds = (
            ''
            + '['
            + (
                '"'
                + 'user.language'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'Property_1'
                + ')'
                + '"'
            )
            + ' '
            + (
                '"'
                + 'user.region'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'Property_2'
                + ')'
                + '"'
            )
            + ']'
        )
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 2)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(
            cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')
        self.assertEquals(cfgIds[1].name, 'user.region')
        self.assertEquals(
            cfgIds[1].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[1].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[1].xmlId, 'Property_2')

    def testThreeElementListQuoted(self):
        strIds = (
            ''
            + '['
            + (
                '"'
                + 'user.language'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'Property_1'
                + ')'
                + '"'
            )
            + ' '
            + (
                '"'
                + 'user.region'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'Property_2'
                + ')'
                + '"'
            )
            + ' '
            + (
                '"'
                + 'file.encoding'
                + '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'Property_3'
                + ')'
                + '"'
            )
            + ']'
        )
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 3)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(
            cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')
        self.assertEquals(cfgIds[1].name, 'user.region')
        self.assertEquals(
            cfgIds[1].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[1].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[1].xmlId, 'Property_2')
        self.assertEquals(cfgIds[2].name, 'file.encoding')
        self.assertEquals(
            cfgIds[2].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[2].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[2].xmlId, 'Property_3')

    def testEntireListQuoted(self):
        # WAS 6.1 may return the entire list in quotes
        strIds = (
            ''
            + '"'
            + '['
            + (
                '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'SomeObject_1'
                + ')'
            )
            + ' '
            + (
                '('
                + 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
                + '|'
                + 'server.xml'
                + '#'
                + 'SomeObject_2'
                + ')'
            )
            + ']'
            + '"'
        )
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 2)
        self.assertEquals(cfgIds[0].name, '')
        self.assertEquals(
            cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'SomeObject_1')
        self.assertEquals(cfgIds[1].name, '')
        self.assertEquals(
            cfgIds[1].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer'
        )
        self.assertEquals(cfgIds[1].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[1].xmlId, 'SomeObject_2')


class AttributeInfoParsingTest(unittest.TestCase):
    def testAttributeWithEnum(self):
        ai = parseAttributeType(
            'authMechanismPreference', 'ENUM(BASIC_PASSWORD, KERBEROS)'
        )
        self.assertEquals(ai.name, 'authMechanismPreference')
        self.assertEquals(ai.type, 'ENUM')
        self.assertEquals(ai.list, 0)
        self.assertEquals(ai.enumValues, ['BASIC_PASSWORD', 'KERBEROS'])
        self.assertEquals(ai.reference, 0)
        self.assertEquals(ai.subTypes, None)

    def testAttributeWithTypeAndSubTypes(self):
        ai = parseAttributeType(
            'properties', 'Property(TypedProperty, DescriptiveProperty)'
        )
        self.assertEquals(ai.name, 'properties')
        self.assertEquals(ai.type, 'Property')
        self.assertEquals(ai.list, 0)
        self.assertEquals(ai.enumValues, None)
        self.assertEquals(ai.reference, 0)
        self.assertEquals(
            ai.subTypes, ['TypedProperty', 'DescriptiveProperty']
        )

    def testAttributeListWithTypeAndSubTypes(self):
        ai = parseAttributeType(
            'files',
            'File('
            + 'Archive, EJBJarFile, WARFile, EARFile, ApplicationClientFile, '
            + 'ModuleFile, Container, ReadOnlyDirectory, RARFile'
            + ')*'
        )
        self.assertEquals(ai.name, 'files')
        self.assertEquals(ai.type, 'File')
        self.assertEquals(ai.list, 1)
        self.assertEquals(ai.enumValues, None)
        self.assertEquals(ai.reference, 0)
        self.assertEquals(
            ai.subTypes,
            [
                'Archive', 'EJBJarFile', 'WARFile', 'EARFile',
                'ApplicationClientFile', 'ModuleFile', 'Container',
                'ReadOnlyDirectory', 'RARFile'
            ]
        )

    def testAttributeReference(self):
        ai = parseAttributeType('provider', 'J2EEResourceProvider@')
        self.assertEquals(ai.name, 'provider')
        self.assertEquals(ai.type, 'J2EEResourceProvider')
        self.assertEquals(ai.list, 0)
        self.assertEquals(ai.enumValues, None)
        self.assertEquals(ai.reference, 1)
        self.assertEquals(ai.subTypes, None)

    def testAttributeListOfReferences(self):
        ai = parseAttributeType(
            'preferredCoordinatorServers', 'CoreGroupServer@*'
        )
        self.assertEquals(ai.name, 'preferredCoordinatorServers')
        self.assertEquals(ai.type, 'CoreGroupServer')
        self.assertEquals(ai.list, 1)
        self.assertEquals(ai.enumValues, None)
        self.assertEquals(ai.reference, 1)
        self.assertEquals(ai.subTypes, None)


class EnvironmentTest(AbstractConfigTest):
    def testCellName(self):
        cellName = getid1(
            '/Cell:%(cellName)s/' % topology
        ).name
        self.assertEquals(cellName, 'vagrant')

    def testNodeName(self):
        nodeName = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/' % topology
        ).name
        self.assertEquals(nodeName, 'vagrant')

    def testServer1Exists(self):
        getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s'
            '/Server:%(serverName)s/'
            % topology
        )


class AttributeReadTest(AbstractConfigTest):
    def testGetString(self):
        srv = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s'
            '/Server:%(serverName)s/'
            % topology
        )
        self.assertEquals(srv.name, 'server1')

    def testGetStringList(self):
        jvm = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s'
            '/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:/'
            % topology
        )
        self.assertEquals(jvm.classpath, [])

    def testGetInteger(self):
        jvm = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s'
            '/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:/'
            % topology
        )
        self.assertEquals(jvm.maximumHeapSize, 0)
        self.assertEquals(type(jvm.maximumHeapSize), types.IntType)

    def testGetBoolean(self):
        srv = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s'
            '/Server:%(serverName)s/'
            % topology
        )
        self.assertFalse(srv.developmentMode)
        self.assertTrue(srv.parallelStartEnabled)

    def testGetMasked(self):
        sec = getid1(
            '/Cell:%(cellName)s/Security:/' % topology
        )
        self.assertEquals(sec.wsPasswords, [])

    def testGetAllAttributesFromServerObject(self):
        srv = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s'
            '/Server:%(serverName)s/'
            % topology
        )
        allAttributes = srv.getAllAttributes()
        self.assertFalse(allAttributes['developmentMode'])
        self.assertTrue(allAttributes['parallelStartEnabled'])

    def testGetAllAttributesFromSecurityObject(self):
        sec = getid1(
            '/Cell:%(cellName)s/Security:/' % topology
        )
        allAttributes = sec.getAllAttributes()
        self.assertEquals(allAttributes['wsPasswords'], [])


class AttributeWriteTest(AbstractConfigTest):
    def testSetString(self):
        jvm = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s'
            '/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:/'
            % topology
        )
        jvm.genericJvmArguments = ' a b c '
        genericJvmArguments = AdminConfig.showAttribute(
            str(jvm),
            'genericJvmArguments'
        )
        self.assertEquals(genericJvmArguments, ' a b c ')

    def testSetStringList(self):
        jvm = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s'
            '/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:/'
            % topology
        )
        self.assertEquals(jvm.classpath, [])
        jvm.classpath = ['a', 'b', 'c']
        self.assertEquals(jvm.classpath, ['a', 'b', 'c'])
        classpath = AdminConfig.showAttribute(
            str(jvm),
            'classpath'
        )
        self.assertEquals(classpath, 'a;b;c')

    def testSetInteger(self):
        jvm = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s'
            '/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:/'
            % topology
        )
        jvm.maximumHeapSize = 12345
        maximumHeapSize = AdminConfig.showAttribute(
            str(jvm),
            'maximumHeapSize'
        )
        self.assertEquals(maximumHeapSize, '12345')

    def testSetBoolean(self):
        srv = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s'
            '/Server:%(serverName)s/'
            % topology
        )
        self.assertFalse(srv.developmentMode)
        self.assertTrue(srv.parallelStartEnabled)
        srv.developmentMode = 1
        srv.parallelStartEnabled = 0
        developmentMode = AdminConfig.showAttribute(
            str(srv),
            'developmentMode'
        )
        parallelStartEnabled = AdminConfig.showAttribute(
            str(srv),
            'parallelStartEnabled'
        )
        self.assertEquals(developmentMode, 'true')
        self.assertEquals(parallelStartEnabled, 'false')
