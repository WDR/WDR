import unittest
import string
from wdr.manifest import substituteVariables


class VariableSubstitutionTest(unittest.TestCase):
    def testSimple(self):
        self.assertEquals('Hello world!', substituteVariables('Hello $[name]!', {'name': 'world'}))

    def testWithMixedCase(self):
        self.assertEquals('Hello world!', substituteVariables('Hello $[Name]!', {'Name': 'world'}))

    def testWithDigits(self):
        self.assertEquals('Hello world!', substituteVariables('Hello $[name0]!', {'name0': 'world'}))

    def testWithUnderscores(self):
        self.assertEquals('Hello world!', substituteVariables('Hello $[the_name]!', {'the_name': 'world'}))

    def testWithUnderscorePrefix(self):
        self.assertEquals('Hello world!', substituteVariables('Hello $[_name]!', {'_name': 'world'}))

    def testWithUnderscoreOnly(self):
        self.assertEquals('Hello world!', substituteVariables('Hello $[_]!', {'_': 'world'}))

    def testWithNestedDictionary(self):
        self.assertEquals('Hello world!', substituteVariables('Hello $[person.name]!', {'person': {'name': 'world'}}))

    def testWithDoubleNestedDictionary(self):
        self.assertEquals('Hello John Peter Smith!',
                          substituteVariables(
                              'Hello $[person.name.first] $[person.name.second] $[person.name.last]!',
                              {
                                  'person': {
                                      'name': {
                                          'first': 'John',
                                          'second': 'Peter',
                                          'last': 'Smith'
                                      }
                                  }
                              }
                          )
                          )

    def testNone(self):
        self.assertEquals('Hello !', substituteVariables('Hello $[name]!', {'name': None}))

    def testNumber(self):
        self.assertEquals('Hello 123!', substituteVariables('Hello $[name]!', {'name': 123}))

    def testList(self):
        self.assertEquals('Hello [123, 456]!', substituteVariables('Hello $[name]!', {'name': [123, 456]}))

    def testTuple(self):
        self.assertEquals('Hello (123, 456)!', substituteVariables('Hello $[name]!', {'name': (123, 456)}))

    def testCallable(self):
        self.assertEquals('Hello world!',
                          substituteVariables('Hello $[name]!', {'name': lambda expression, variables: 'world'}))

    def testCallableReturningNone(self):
        self.assertEquals('Hello !',
                          substituteVariables('Hello $[name]!', {'name': lambda expression, variables: None}))

    def testWithExtraSpaces(self):
        self.assertEquals('Hello world!',
                          substituteVariables('Hello $[ person.name ]!', {'person': {'name': 'world'}}))


class VariableSubstitutionWithFilteringTest(unittest.TestCase):
    def testUpper(self):
        self.assertEquals('Hello WORLD!',
                          substituteVariables('Hello $[name|upper]!', {'name': 'world', 'upper': string.upper}))

    def testListProcessing(self):
        self.assertEquals('Hello John Smith!',
                          substituteVariables('Hello $[name|join]!', {'name': ['John', 'Smith'], 'join': string.join}))

    def testListWithLambdaOnList(self):
        self.assertEquals(
            'deploymentTargets are [WebSphere:cell=wdrCell,cluster=wdrCluster+WebSphere:cell=wdrCell,node=httpNode01,server=httpServer01]',
            substituteVariables(
                'deploymentTargets are [$[deploymentTargets|joinDeploymentTargets]]',
                {
                    'deploymentTargets': [
                        [['cell', 'wdrCell'], ['cluster', 'wdrCluster']],
                        [['cell', 'wdrCell'], ['node', 'httpNode01'], ['server', 'httpServer01']]
                    ],
                    'joinDeploymentTargets':
                    lambda targetList: ('+'.join(
                        [
                            'WebSphere:' + ','.join(['='.join(attList) for attList in target])
                            for target in targetList
                        ]
                    )
                    )
                }
            )
        )

    def testListWithLambdaOnDict(self):
        self.assertEquals(
            'deploymentTargets are [WebSphere:cell=wdrCell,cluster=wdrCluster+WebSphere:cell=wdrCell,node=httpNode01,server=httpServer01]',
            substituteVariables(
                'deploymentTargets are [$[deploymentTargets|joinDeploymentTargets]]',
                {
                    'deploymentTargets': [
                        {'cell': 'wdrCell', 'cluster': 'wdrCluster'},
                        {'cell': 'wdrCell', 'node': 'httpNode01', 'server': 'httpServer01'}
                    ],
                    'joinDeploymentTargets':
                    lambda targetList: ('+'.join(
                        [
                            'WebSphere:cell=%(cell)s,cluster=%(cluster)s' % t
                            for t in filter(lambda e: e.get('cluster'), targetList)
                        ]
                        +
                        [
                            'WebSphere:cell=%(cell)s,node=%(node)s,server=%(server)s' % t
                            for t in filter(lambda e: e.get('node') and e.get('server'),
                                            targetList)
                        ]
                    )
                    )
                }
            )
        )

    def testWithExtraSpaces(self):
        self.assertEquals('Hello WORLD!',
                          substituteVariables(
                              'Hello $[ name | upper ]!',
                              {'name': 'world', 'upper': string.upper}
                          )
                          )
