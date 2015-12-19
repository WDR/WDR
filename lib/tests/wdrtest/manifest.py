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


class VariableSubstitutionTest(unittest.TestCase):
    def testSimple(self):
        self.assertEquals(
            'Hello world!',
            substituteVariables('Hello $[name]!', {'name': 'world'})
        )

    def testWithMixedCase(self):
        self.assertEquals(
            'Hello world!',
            substituteVariables('Hello $[Name]!', {'Name': 'world'})
        )

    def testWithDigits(self):
        self.assertEquals(
            'Hello world!',
            substituteVariables('Hello $[name0]!', {'name0': 'world'})
        )

    def testWithUnderscores(self):
        self.assertEquals(
            'Hello world!',
            substituteVariables('Hello $[the_name]!', {'the_name': 'world'})
        )

    def testWithUnderscorePrefix(self):
        self.assertEquals(
            'Hello world!',
            substituteVariables('Hello $[_name]!', {'_name': 'world'})
        )

    def testWithUnderscoreOnly(self):
        self.assertEquals(
            'Hello world!',
            substituteVariables('Hello $[_]!', {'_': 'world'})
        )

    def testWithNestedDictionary(self):
        self.assertEquals(
            'Hello world!',
            substituteVariables(
                'Hello $[person.name]!', {'person': {'name': 'world'}}
            )
        )

    def testWithDoubleNestedDictionary(self):
        self.assertEquals(
            'Hello John Peter Smith!',
            substituteVariables(
                'Hello '
                '$[person.name.first] '
                '$[person.name.second] '
                '$[person.name.last]!',
                {
                    'person': {
                        'name': {
                            'first': 'John',
                            'second': 'Peter',
                            'last': 'Smith',
                        }
                    }
                }
            )
        )

    def testNone(self):
        self.assertEquals(
            'Hello !',
            substituteVariables('Hello $[name]!', {'name': None})
        )

    def testNumber(self):
        self.assertEquals(
            'Hello 123!',
            substituteVariables('Hello $[name]!', {'name': 123})
        )

    def testList(self):
        self.assertEquals(
            'Hello [123, 456]!',
            substituteVariables('Hello $[name]!', {'name': [123, 456]})
        )

    def testTuple(self):
        self.assertEquals(
            'Hello (123, 456)!',
            substituteVariables('Hello $[name]!', {'name': (123, 456)})
        )

    def testCallable(self):
        self.assertEquals(
            'Hello world!',
            substituteVariables(
                'Hello $[name]!',
                {'name': lambda expression, variables: 'world'}
            )
        )

    def testCallableReturningNone(self):
        self.assertEquals(
            'Hello !',
            substituteVariables(
                'Hello $[name]!',
                {'name': lambda expression, variables: None}
            )
        )

    def testWithExtraSpaces(self):
        self.assertEquals(
            'Hello world!',
            substituteVariables(
                'Hello $[ person.name ]!',
                {'person': {'name': 'world'}}
            )
        )


class VariableSubstitutionWithFilteringTest(unittest.TestCase):
    def testUpper(self):
        self.assertEquals(
            'Hello WORLD!',
            substituteVariables(
                'Hello $[name|upper]!',
                {'name': 'world', 'upper': string.upper}
            )
        )

    def testListProcessing(self):
        self.assertEquals(
            'Hello John Smith!',
            substituteVariables(
                'Hello $[name|join]!',
                {'name': ['John', 'Smith'], 'join': string.join}
            )
        )

    def testListWithLambdaOnList(self):
        self.assertEquals(
            'deploymentTargets are '
            '['
            'WebSphere'
            ':cell=wdrCell,cluster=wdrCluster+WebSphere'
            ':cell=wdrCell,node=httpNode01,server=httpServer01'
            ']',
            substituteVariables(
                'deploymentTargets are '
                '[$[deploymentTargets|joinDeploymentTargets]]',
                {
                    'deploymentTargets': [
                        [
                            ['cell', 'wdrCell'],
                            ['cluster', 'wdrCluster'],
                        ],
                        [
                            ['cell', 'wdrCell'],
                            ['node', 'httpNode01'],
                            ['server', 'httpServer01'],
                        ]
                    ],
                    'joinDeploymentTargets':
                    lambda targetList: ('+'.join(
                        [
                            'WebSphere:'
                            + ','.join(
                                ['='.join(attList) for attList in target]
                            )
                            for target in targetList
                        ]
                    )
                    )
                }
            )
        )

    def testListWithLambdaOnDict(self):
        self.assertEquals(
            'deploymentTargets are '
            '['
            'WebSphere'
            ':cell=wdrCell,cluster=wdrCluster+WebSphere'
            ':cell=wdrCell,node=httpNode01,server=httpServer01'
            ']',
            substituteVariables(
                'deploymentTargets are '
                '[$[deploymentTargets|joinDeploymentTargets]]',
                {
                    'deploymentTargets': [
                        {
                            'cell': 'wdrCell',
                            'cluster': 'wdrCluster',
                        },
                        {
                            'cell': 'wdrCell',
                            'node': 'httpNode01',
                            'server': 'httpServer01',
                        }
                    ],
                    'joinDeploymentTargets':
                    lambda targetList: (
                        '+'.join(
                            [
                                'WebSphere:cell=%(cell)s,cluster=%(cluster)s'
                                % t
                                for t in filter(
                                    lambda e: e.get('cluster'), targetList
                                )
                            ]
                            +
                            [
                                'WebSphere'
                                ':cell=%(cell)s,node=%(node)s,server=%(server)s'
                                % t
                                for t in filter(
                                    lambda e: e.get('node') and e.get('server'),
                                    targetList
                                )
                            ]
                        )
                    )
                }
            )
        )

    def testWithExtraSpaces(self):
        self.assertEquals(
            'Hello WORLD!',
            substituteVariables(
                'Hello $[ name | upper ]!',
                {'name': 'world', 'upper': string.upper}
            )
        )


class BasicManifestImportTest(AbstractConfigTest):
    def testUpdateStrings(self):
        """Modifying single string attribute"""
        srv = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s/'
            % topology
        )
        importConfigurationManifest(
            'wdrtest/manifests/basic/string_attribute_change.wdrc', topology
        )
        self.assertEquals(srv.changeUserAfterStartup, 'vagrant')
        self.assertEquals(srv.changeGroupAfterStartup, 'vagrant')

    def testUpdateBooleans(self):
        """Modifying boolean attributes"""
        srv = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s/'
            % topology
        )
        self.assertFalse(srv.developmentMode)
        self.assertTrue(srv.parallelStartEnabled)
        importConfigurationManifest(
            'wdrtest/manifests/basic/boolean_attribute_change.wdrc', topology
        )
        self.assertTrue(srv.developmentMode)
        self.assertFalse(srv.parallelStartEnabled)

    def testUpdateBooleanWithInvalidValue(self):
        """Attempting to assign invalid value to a boolean attribute"""
        srv = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s/'
            % topology
        )
        self.assertTrue(srv.parallelStartEnabled)
        importConfigurationManifest(
            'wdrtest/manifests/basic/boolean_attribute_invalid.wdrc', topology
        )
        self.assertFalse(srv.developmentMode)

    def testUpdateInteger(self):
        """Updating integer attribute"""
        jvm = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:/'
            % topology
        )
        self.assertEquals(jvm.initialHeapSize, 0)
        self.assertEquals(jvm.maximumHeapSize, 0)
        importConfigurationManifest(
            'wdrtest/manifests/basic/integer_attribute_change.wdrc', topology
        )
        self.assertEquals(jvm.initialHeapSize, 12345)
        self.assertEquals(jvm.maximumHeapSize, 67890)

    def testUpdateEnum(self):
        """Updating enum attribute"""
        cell = getid1(
            '/Cell:%(cellName)s/'
            % topology
        )
        self.assertEquals(cell.cellDiscoveryProtocol, 'TCP')
        importConfigurationManifest(
            'wdrtest/manifests/basic/enum_attribute_change.wdrc', topology
        )
        self.assertEquals(cell.cellDiscoveryProtocol, 'UDP')

    def testUpdateEnumWithInvalidValue(self):
        """Attempting to assign invalid enum value to an attribute"""
        cell = getid1(
            '/Cell:%(cellName)s/'
            % topology
        )
        self.assertEquals(cell.cellDiscoveryProtocol, 'TCP')
        failure = 0
        try:
            importConfigurationManifest(
                'wdrtest/manifests/basic/enum_attribute_invalid.wdrc', topology
            )
            failure = 1
        except:
            pass
        self.assertFalse(failure, 'should fail on invalid enum value')
        self.assertEquals(cell.cellDiscoveryProtocol, 'TCP')

    def testFailOnInvalidType(self):
        """Attempting use invalid object type"""
        failure = 0
        try:
            importConfigurationManifest(
                'wdrtest/manifests/basic/fail_on_invalid_type.wdrc', topology
            )
            failure = 1
        except:
            pass
        self.assertFalse(failure, 'should fail on invalid type')

    def testFailOnInvalidKey(self):
        """Attempting use invalid object attribute in key"""
        failure = 0
        try:
            importConfigurationManifest(
                'wdrtest/manifests/basic/fail_on_invalid_key.wdrc', topology
            )
            failure = 1
        except:
            pass
        self.assertFalse(failure, 'should fail on invalid key')

    def testFailOnInvalidAttribute(self):
        """Attempting use invalid object attribute"""
        failure = 0
        try:
            importConfigurationManifest(
                'wdrtest/manifests/basic/fail_on_invalid_attribute.wdrc',
                topology
            )
            failure = 1
        except:
            pass
        self.assertFalse(failure, 'should fail on invalid attribute')

    def testCommentsValid(self):
        """Comments in manifests"""
        importConfigurationManifest(
            'wdrtest/manifests/basic/comments_valid.wdrc', topology
        )

    def testCommentIndented(self):
        importConfigurationManifest(
            'wdrtest/manifests/basic/comment_indented.wdrc', topology
        )
        self.assertFalse(hasChanges())

    def testNoChanges(self):
        importConfigurationManifest(
            'wdrtest/manifests/basic/no_changes.wdrc', topology
        )
        self.assertFalse(hasChanges())


class HierarchiesManifestImportTest(AbstractConfigTest):
    def testOneChild(self):
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/JDBCProvider:/'
            % topology
        )
        self.assertEquals(providers, [])
        importConfigurationManifest(
            'wdrtest/manifests/hierarchies/one_child.wdrc', topology
        )
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/JDBCProvider:/'
            % topology
        )
        self.assertEquals(len(providers), 1)
        db2provider = providers[0]
        self.assertEquals(db2provider.name, 'DB2 Provider')
        self.assertEquals(db2provider.classpath, ['a', 'b', 'c'])
        self.assertTrue(db2provider.xa)

    def testMultipleChildren(self):
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/JDBCProvider:/'
            % topology
        )
        self.assertEquals(providers, [])
        importConfigurationManifest(
            'wdrtest/manifests/hierarchies/multiple_children.wdrc', topology
        )
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/JDBCProvider:/'
            % topology
        )
        self.assertEquals(len(providers), 2)
        db2provider = providers[0]
        self.assertEquals(db2provider.name, 'DB2 Provider')
        self.assertEquals(db2provider.classpath, ['a', 'b', 'c'])
        self.assertFalse(db2provider.xa)
        db2provider = providers[1]
        self.assertEquals(db2provider.name, 'MS SQL Provider')
        self.assertEquals(db2provider.classpath, ['d', 'e', 'f'])
        self.assertTrue(db2provider.xa)

    def testMultipleChildrenInList(self):
        cellVariables = getid1(
            '/Cell:%(cellName)s/VariableMap:/'
            % topology
        )
        variableCount = len(cellVariables.entries)
        importConfigurationManifest(
            'wdrtest/manifests/hierarchies/multiple_children_in_list.wdrc',
            topology
        )
        self.assertEquals(len(cellVariables.entries), variableCount+2)

    def testMultipleChildrenInAttribute(self):
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/JDBCProvider:/'
            % topology
        )
        self.assertEquals(providers, [])
        importConfigurationManifest(
            'wdrtest/manifests/hierarchies/multiple_children_in_attribute.wdrc',
            topology
        )
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/JDBCProvider:/'
            % topology
        )
        self.assertEquals(len(providers), 1)
        db2provider = providers[0]
        self.assertEquals(db2provider.name, 'DB2 Provider')
        self.assertEquals(len(db2provider.propertySet.resourceProperties), 2)

    def testRepeatedObjects(self):
        importConfigurationManifest(
            'wdrtest/manifests/hierarchies/repeated_objects.wdrc', topology
        )
        server = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s/'
            % topology
        )
        referenceList = server.lookup1(
            'CustomService',
            {
                'displayName': 'first',
            },
            'customServices'
        )


class IncludesAndImportsTest(AbstractConfigTest):
    def testImportValid(self):
        cellVariables = getid1(
            '/Cell:%(cellName)s/VariableMap:/'
            % topology
        )
        variableCount = len(cellVariables.entries)
        importConfigurationManifest(
            'wdrtest/manifests/imports/import_valid.wdrc', topology
        )
        self.assertEquals(len(cellVariables.entries), variableCount + 2)

    def testIncludeWithPath(self):
        cellVariables = getid1(
            '/Cell:%(cellName)s/VariableMap:/'
            % topology
        )
        variableCount = len(cellVariables.entries)
        importConfigurationManifest(
            'wdrtest/manifests/imports/include_with_path.wdrc', topology
        )
        self.assertEquals(len(cellVariables.entries), variableCount + 3)

    def testIncludeWithoutPath(self):
        cellVariables = getid1(
            '/Cell:%(cellName)s/VariableMap:/'
            % topology
        )
        variableCount = len(cellVariables.entries)
        importConfigurationManifest(
            'wdrtest/manifests/imports/include_without_path.wdrc', topology
        )
        self.assertEquals(len(cellVariables.entries), variableCount + 2)


class VariablesAndFiltersTest(AbstractConfigTest):
    def testCallables(self):
        d = {}
        d.update(topology)
        d['list'] = ['a', 'b', 'c', 'd']
        d['first'] = lambda x: x[0] # noqa
        d['last'] = lambda x: x[-1] # noqa
        cellVariables = getid1(
            '/Cell:%(cellName)s/VariableMap:/'
            % topology
        )
        variableCount = len(cellVariables.entries)
        importConfigurationManifest(
            'wdrtest/manifests/vars/callables.wdrc',
            d
        )
        self.assertEquals(len(cellVariables.entries), variableCount + 2)
        self.assertEquals(cellVariables.entries[-2].symbolicName, 'a')
        self.assertEquals(cellVariables.entries[-2].value, 'val1')
        self.assertEquals(cellVariables.entries[-1].symbolicName, 'd')
        self.assertEquals(cellVariables.entries[-1].value, 'val2')


class ReferencesTest(AbstractConfigTest):
    def testMailProtocolProvider(self):
        """Assigning reference to attribute"""
        smtpProtocol = getid1(
            '/Cell:%(cellName)s/MailProvider:Built-in Mail Provider/'
            % topology
        ).lookup1(
            'ProtocolProvider',
            {
                'protocol': 'smtp',
            },
            'protocolProviders'
        )
        importConfigurationManifest(
            'wdrtest/manifests/references/mail_protocol_provider.wdrc', topology
        )
        mailSession = getid1(
            '/Cell:%(cellName)s'
            '/MailProvider:Built-in Mail Provider'
            '/MailSession:test mail session'
            % topology
        )
        self.assertEquals(
            str(mailSession.mailTransportProtocol), str(smtpProtocol)
        )
        self.assertEquals(mailSession.name, 'test mail session')
        self.assertEquals(mailSession.jndiName, 'mail/test')
        self.assertEquals(mailSession.mailTransportHost, 'smtp.example.com')

    def testDependentService(self):
        """Assigning multiple references to attribute"""
        importConfigurationManifest(
            'wdrtest/manifests/references/dependent_service.wdrc', topology
        )
        server = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s/'
            % topology
        )
        referenceList = server.lookup1(
            'CustomService',
            {
                'displayName': 'with dependencies',
            },
            'customServices'
        ).prerequisiteServices
        self.assertEquals(len(referenceList), 3)
        self.assertEquals(referenceList[0].displayName, 'first')
        self.assertEquals(referenceList[1].displayName, 'second')
        self.assertEquals(referenceList[2].displayName, 'fifth')

    def testDependentServiceExtension(self):
        """Assigning more references to an attribute"""
        importConfigurationManifest(
            'wdrtest/manifests/references/dependent_service.wdrc', topology
        )
        importConfigurationManifest(
            'wdrtest/manifests/references/dependent_service2.wdrc', topology
        )
        server = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s/'
            % topology
        )
        referenceList = server.lookup1(
            'CustomService',
            {
                'displayName': 'with dependencies',
            },
            'customServices'
        ).prerequisiteServices
        self.assertEquals(len(referenceList), 5)
        self.assertEquals(referenceList[0].displayName, 'first')
        self.assertEquals(referenceList[1].displayName, 'second')
        self.assertEquals(referenceList[2].displayName, 'fifth')
        self.assertEquals(referenceList[3].displayName, 'third')
        self.assertEquals(referenceList[4].displayName, 'fourth')


class RemovalTest(AbstractConfigTest):
    def testJdbcProvider(self):
        """Removing JDBCProvider - a child of another object (Server)"""
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JDBCProvider:Derby JDBC Provider/'
            % topology
        )
        self.assertEquals(len(providers), 1)
        importConfigurationManifest(
            'wdrtest/manifests/removal/jdbc_provider.wdrc', topology
        )
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JDBCProvider:Derby JDBC Provider/'
            % topology
        )
        self.assertEquals(len(providers), 0)

    def testJvmProperty(self):
        """Removing Property from JavaVirtualMachine.systemProperties"""
        prop = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:'
            '/Property:com.ibm.security.jgss.debug/'
            % topology
        )
        self.assertEquals(len(prop), 1)
        importConfigurationManifest(
            'wdrtest/manifests/removal/jvm_property.wdrc', topology
        )
        prop = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:'
            '/Property:com.ibm.security.jgss.debug/'
            % topology
        )
        self.assertEquals(len(prop), 0)

    def testMailTransportProtocol(self):
        """Removing reference from MailSession.mailTransportProtocol"""
        smtpProtocol = getid1(
            '/Cell:%(cellName)s/MailProvider:Built-in Mail Provider/'
            % topology
        ).lookup1(
            'ProtocolProvider',
            {
                'protocol': 'smtp',
            },
            'protocolProviders'
        )
        importConfigurationManifest(
            'wdrtest/manifests/removal/mail_protocol_provider.wdrc', topology
        )
        mailSession = getid1(
            '/Cell:%(cellName)s'
            '/MailProvider:Built-in Mail Provider'
            '/MailSession:test mail session/'
            % topology
        )
        self.assertEquals(
            str(mailSession.mailTransportProtocol), str(smtpProtocol)
        )
        importConfigurationManifest(
            'wdrtest/manifests/removal/mail_protocol_provider2.wdrc', topology
        )
        self.assertNone(mailSession.mailTransportProtocol)

    def testDependentService(self):
        """Removing one of CustomService.prerequisiteServices references"""
        importConfigurationManifest(
            'wdrtest/manifests/removal/dependent_service.wdrc', topology
        )
        importConfigurationManifest(
            'wdrtest/manifests/removal/dependent_service2.wdrc', topology
        )
        server = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s/'
            % topology
        )
        referenceList = server.lookup1(
            'CustomService',
            {
                'displayName': 'with dependencies',
            },
            'customServices'
        ).prerequisiteServices
        self.assertEquals(len(referenceList), 2)
        self.assertEquals(referenceList[0].displayName, 'first')
        self.assertEquals(referenceList[1].displayName, 'fifth')


class CustomizeTest(AbstractConfigTest):
    def testJvmProperty(self):
        """Customize existing Property in JavaVirtualMachine.systemProperties"""
        prop = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:'
            '/Property:com.ibm.security.jgss.debug/'
            % topology
        )
        self.assertEquals(len(prop), 1)
        self.assertEquals(prop[0].value, 'off')
        importConfigurationManifest(
            'wdrtest/manifests/customize/jvm_property.wdrc', topology
        )
        prop = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:'
            '/Property:com.ibm.security.jgss.debug/'
            % topology
        )
        self.assertEquals(len(prop), 1)
        self.assertEquals(prop[0].value, 'on')

    def testMissingJvmProperty(self):
        """Customize missing Property in JavaVirtualMachine.systemProperties"""
        prop = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:'
            '/Property:com.ibm.security.jgss.debug/'
            % topology
        )
        self.assertEquals(len(prop), 1)
        prop[0].remove()
        importConfigurationManifest(
            'wdrtest/manifests/customize/jvm_property.wdrc', topology
        )
        prop = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JavaProcessDef:/JavaVirtualMachine:'
            '/Property:com.ibm.security.jgss.debug/'
            % topology
        )
        self.assertEquals(len(prop), 0)

    def testExistingDataSource(self):
        """Customize existing DataSource's attributes"""
        dataSource = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JDBCProvider:Derby JDBC Provider'
            '/DataSource:Default Datasource/'
            % topology
        )
        self.assertEquals(dataSource.jndiName, 'DefaultDatasource')
        importConfigurationManifest(
            'wdrtest/manifests/customize/data_source.wdrc', topology
        )
        self.assertEquals(dataSource.jndiName, 'DefaultDatasource_WDR')

    def testNonexistentDataSource(self):
        """Customize missing DataSource"""
        provider = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JDBCProvider:Derby JDBC Provider/'
            % topology
        )
        dataSource = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JDBCProvider:Derby JDBC Provider'
            '/DataSource:Default Datasource/'
            % topology
        )
        self.assertEquals(dataSource.jndiName, 'DefaultDatasource')
        self.assertEquals(
            provider.description, 'Derby embedded non-XA  JDBC Provider'
        )
        dataSource.remove()
        importConfigurationManifest(
            'wdrtest/manifests/customize/data_source.wdrc', topology
        )
        dataSources = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JDBCProvider:Derby JDBC Provider'
            '/DataSource:Default Datasource/'
            % topology
        )
        self.assertEquals(len(dataSources), 1)
        self.assertEquals(dataSources[0].jndiName, 'DefaultDatasource_WDR')
        self.assertEquals(
            provider.description, 'customized'
        )

    def testNonexistentProvider(self):
        """Customize missing DataSource"""
        provider = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JDBCProvider:Derby JDBC Provider/'
            % topology
        )
        dataSource = getid1(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JDBCProvider:Derby JDBC Provider'
            '/DataSource:Default Datasource/'
            % topology
        )
        self.assertEquals(dataSource.jndiName, 'DefaultDatasource')
        provider.remove()
        importConfigurationManifest(
            'wdrtest/manifests/customize/data_source.wdrc', topology
        )
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JDBCProvider:Derby JDBC Provider/'
            % topology
        )
        self.assertEquals(providers, [])
        dataSources = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/Server:%(serverName)s'
            '/JDBCProvider:Derby JDBC Provider'
            '/DataSource:Default Datasource/'
            % topology
        )
        self.assertEquals(dataSources, [])


class TemplatesTest(AbstractConfigTest):

    def test_db2_ibm_jcc_xa(self):
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/JDBCProvider:/'
            % topology
        )
        self.assertEquals(providers, [])
        importConfigurationManifest(
            'wdrtest/manifests/templates/db2_ibm_jcc_xa.wdrc', topology
        )
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/JDBCProvider:/'
            % topology
        )
        self.assertEquals(len(providers), 1)
        db2provider = providers[0]
        self.assertEquals(
            db2provider.name,
            'Template based provider'
        )
        self.assertEquals(
            db2provider.description,
            'Created from "DB2 Using IBM JCC Driver (XA)" template'
        )
        self.assertEquals(
            db2provider.providerType, 'DB2 Using IBM JCC Driver (XA)'
        )
        self.assertTrue(db2provider.xa)

    def test_db2_ibm_jcc_xa_using_full_id(self):
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/JDBCProvider:/'
            % topology
        )
        self.assertEquals(providers, [])
        importConfigurationManifest(
            'wdrtest/manifests/templates/db2_ibm_jcc_xa_using_full_id.wdrc',
            topology
        )
        providers = getid(
            '/Cell:%(cellName)s/Node:%(nodeName)s/JDBCProvider:/'
            % topology
        )
        self.assertEquals(len(providers), 1)
        db2provider = providers[0]
        self.assertEquals(
            db2provider.name,
            'Template based provider'
        )
        self.assertEquals(
            db2provider.description,
            'Created from "DB2 Using IBM JCC Driver (XA)" template'
        )
        self.assertEquals(
            db2provider.providerType, 'DB2 Using IBM JCC Driver (XA)'
        )
        self.assertTrue(db2provider.xa)

    def test_non_unique_template(self):
        try:
            importConfigurationManifest(
                'wdrtest/manifests/templates/non_unique_template.wdrc',
                topology
            )
        except:
            return
        self.fail('non-unique template name should raise exception')

    def test_web_server(self):
        self.assertEqual(0, len(getid('/Server:DefaultServerFromTemplate/')))
        importConfigurationManifest(
            'wdrtest/manifests/templates/default_server.wdrc',
            topology
        )
        self.assertEqual(1, len(getid('/Server:DefaultServerFromTemplate/')))

    def test_non_existent_template(self):
        try:
            importConfigurationManifest(
                'wdrtest/manifests/templates/non_existent_template.wdrc',
                topology
            )
        except:
            return
        self.fail('non-unique template name should raise exception')
