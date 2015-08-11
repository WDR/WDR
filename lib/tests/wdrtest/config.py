import unittest
from wdr.config import _parseConfigId, _parseConfigIdList
from wdr.config import _isConfigId, _isConfigIdList
from wdr.config import parseAttributeType


class ConfigIdParsingTest(unittest.TestCase):
    def testSimple(self):
        strId = 'DefaultDatasource(cells/wdrCell/nodes/wdrNode/servers/wdrServer|resources.xml#DataSource_1234567890123)'
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, 'DefaultDatasource')
        self.assertEquals(cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuoted(self):
        strId = '"DefaultDatasource(cells/wdrCell/nodes/wdrNode/servers/wdrServer|resources.xml#DataSource_1234567890123)"'
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, 'DefaultDatasource')
        self.assertEquals(cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedWithSpace(self):
        strId = '"Default Datasource(cells/wdrCell/nodes/wdrNode/servers/wdrServer|resources.xml#DataSource_1234567890123)"'
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, 'Default Datasource')
        self.assertEquals(cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedWithLeadingSpace(self):
        strId = '" Default Datasource(cells/wdrCell/nodes/wdrNode/servers/wdrServer|resources.xml#DataSource_1234567890123)"'
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, ' Default Datasource')
        self.assertEquals(cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedWithTrailingSpace(self):
        strId = '"Default Datasource (cells/wdrCell/nodes/wdrNode/servers/wdrServer|resources.xml#DataSource_1234567890123)"'
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, 'Default Datasource ')
        self.assertEquals(cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testEmptyAdminName(self):
        strId = '(cells/wdrCell/nodes/wdrNode/servers/wdrServer|resources.xml#DataSource_1234567890123)'
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, '')
        self.assertEquals(cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedEmptyAdminName(self):
        strId = '"(cells/wdrCell/nodes/wdrNode/servers/wdrServer|resources.xml#DataSource_1234567890123)"'
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, '')
        self.assertEquals(cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedOnlySpacesInAdminName(self):
        strId = '" (cells/wdrCell/nodes/wdrNode/servers/wdrServer|resources.xml#DataSource_1234567890123)"'
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, ' ')
        self.assertEquals(cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'DataSource_1234567890123')

    def testQuotedParenthesisInAdminName(self):
        strId = '"Derby JDBC Provider (XA)(cells/wdrCell/nodes/wdrNode/servers/wdrServer|resources.xml#builtin_jdbcprovider)"'
        self.assert_(_isConfigId(strId))
        cfgId = _parseConfigId(strId)
        self.assertEquals(cfgId.name, 'Derby JDBC Provider (XA)')
        self.assertEquals(cfgId.xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgId.xmlDoc, 'resources.xml')
        self.assertEquals(cfgId.xmlId, 'builtin_jdbcprovider')

    def testEmptyElementList(self):
        strIds = '[]'
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 0)

    def testOneElementList(self):
        strIds = '[user.language(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_1)]'
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 1)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')

    def testTwoElementList(self):
        strIds = '[user.language(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_1) user.region(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_2)]'
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 2)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')
        self.assertEquals(cfgIds[1].name, 'user.region')
        self.assertEquals(cfgIds[1].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[1].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[1].xmlId, 'Property_2')

    def testThreeElementList(self):
        strIds = '[user.language(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_1) user.region(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_2) file.encoding(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_3)]'
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 3)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')
        self.assertEquals(cfgIds[1].name, 'user.region')
        self.assertEquals(cfgIds[1].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[1].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[1].xmlId, 'Property_2')
        self.assertEquals(cfgIds[2].name, 'file.encoding')
        self.assertEquals(cfgIds[2].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[2].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[2].xmlId, 'Property_3')

    def testOneElementListQuoted(self):
        strIds = '["user.language(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_1)"]'
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 1)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')

    def testTwoElementListQuoted(self):
        strIds = '["user.language(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_1)" "user.region(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_2)"]'
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 2)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')
        self.assertEquals(cfgIds[1].name, 'user.region')
        self.assertEquals(cfgIds[1].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[1].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[1].xmlId, 'Property_2')

    def testThreeElementListQuoted(self):
        strIds = '["user.language(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_1)" "user.region(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_2)" "file.encoding(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#Property_3)"]'
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 3)
        self.assertEquals(cfgIds[0].name, 'user.language')
        self.assertEquals(cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'Property_1')
        self.assertEquals(cfgIds[1].name, 'user.region')
        self.assertEquals(cfgIds[1].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[1].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[1].xmlId, 'Property_2')
        self.assertEquals(cfgIds[2].name, 'file.encoding')
        self.assertEquals(cfgIds[2].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[2].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[2].xmlId, 'Property_3')

    def testEntireListQuoted(self):
        # WAS 6.1 may return the entire list in quotes
        strIds = '"[(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#SomeObject_1) (cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#SomeObject_2)]"'
        self.assert_(_isConfigIdList(strIds))
        cfgIds = _parseConfigIdList(strIds)
        self.assertEquals(len(cfgIds), 2)
        self.assertEquals(cfgIds[0].name, '')
        self.assertEquals(cfgIds[0].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[0].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[0].xmlId, 'SomeObject_1')
        self.assertEquals(cfgIds[1].name, '')
        self.assertEquals(cfgIds[1].xmlPath, 'cells/wdrCell/nodes/wdrNode/servers/wdrServer')
        self.assertEquals(cfgIds[1].xmlDoc, 'server.xml')
        self.assertEquals(cfgIds[1].xmlId, 'SomeObject_2')


class AttributeInfoParsingTest(unittest.TestCase):
    def testAttributeWithEnum(self):
        ai = parseAttributeType('authMechanismPreference', 'ENUM(BASIC_PASSWORD, KERBEROS)')
        self.assertEquals(ai.name, 'authMechanismPreference')
        self.assertEquals(ai.type, 'ENUM')
        self.assertEquals(ai.list, 0)
        self.assertEquals(ai.enumValues, ['BASIC_PASSWORD', 'KERBEROS'])
        self.assertEquals(ai.reference, 0)
        self.assertEquals(ai.subTypes, None)

    def testAttributeWithTypeAndSubTypes(self):
        ai = parseAttributeType('properties', 'Property(TypedProperty, DescriptiveProperty)')
        self.assertEquals(ai.name, 'properties')
        self.assertEquals(ai.type, 'Property')
        self.assertEquals(ai.list, 0)
        self.assertEquals(ai.enumValues, None)
        self.assertEquals(ai.reference, 0)
        self.assertEquals(ai.subTypes, ['TypedProperty', 'DescriptiveProperty'])

    def testAttributeListWithTypeAndSubTypes(self):
        ai = parseAttributeType('files',
                                'File(Archive, EJBJarFile, WARFile, EARFile, ApplicationClientFile, ModuleFile, Container, ReadOnlyDirectory, RARFile)*')
        self.assertEquals(ai.name, 'files')
        self.assertEquals(ai.type, 'File')
        self.assertEquals(ai.list, 1)
        self.assertEquals(ai.enumValues, None)
        self.assertEquals(ai.reference, 0)
        self.assertEquals(ai.subTypes,
                          ['Archive', 'EJBJarFile', 'WARFile', 'EARFile', 'ApplicationClientFile', 'ModuleFile',
                           'Container', 'ReadOnlyDirectory', 'RARFile'])

    def testAttributeReference(self):
        ai = parseAttributeType('provider', 'J2EEResourceProvider@')
        self.assertEquals(ai.name, 'provider')
        self.assertEquals(ai.type, 'J2EEResourceProvider')
        self.assertEquals(ai.list, 0)
        self.assertEquals(ai.enumValues, None)
        self.assertEquals(ai.reference, 1)
        self.assertEquals(ai.subTypes, None)

    def testAttributeListOfReferences(self):
        ai = parseAttributeType('preferredCoordinatorServers', 'CoreGroupServer@*')
        self.assertEquals(ai.name, 'preferredCoordinatorServers')
        self.assertEquals(ai.type, 'CoreGroupServer')
        self.assertEquals(ai.list, 1)
        self.assertEquals(ai.enumValues, None)
        self.assertEquals(ai.reference, 1)
        self.assertEquals(ai.subTypes, None)
