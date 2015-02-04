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

import unittest
import string
from wdr.manifest import _substituteVariables

class VariableSubstitutionTest( unittest.TestCase ):
    def testSimple( self ):
        self.assertEquals( 'Hello world!', _substituteVariables( 'Hello $[name]!', {'name': 'world'} ) )
    def testWithMixedCase( self ):
        self.assertEquals( 'Hello world!', _substituteVariables( 'Hello $[Name]!', {'Name': 'world'} ) )
    def testWithDigits( self ):
        self.assertEquals( 'Hello world!', _substituteVariables( 'Hello $[name0]!', {'name0': 'world'} ) )
    def testWithUnderscores( self ):
        self.assertEquals( 'Hello world!', _substituteVariables( 'Hello $[the_name]!', {'the_name': 'world'} ) )
    def testWithUnderscorePrefix( self ):
        self.assertEquals( 'Hello world!', _substituteVariables( 'Hello $[_name]!', {'_name': 'world'} ) )
    def testWithUnderscoreOnly( self ):
        self.assertEquals( 'Hello world!', _substituteVariables( 'Hello $[_]!', {'_': 'world'} ) )
    def testWithNestedDictionary( self ):
        self.assertEquals( 'Hello world!', _substituteVariables( 'Hello $[person.name]!', {'person': {'name': 'world'}} ) )
    def testWithNestedDictionary( self ):
        self.assertEquals( 'Hello John Peter Smith!', _substituteVariables( 'Hello $[person.name.first] $[person.name.second] $[person.name.last]!', { 'person': { 'name': { 'first':'John', 'second':'Peter', 'last':'Smith' } } } ) )
    def testNone( self ):
        self.assertEquals( 'Hello !', _substituteVariables( 'Hello $[name]!', {'name': None }) )
    def testNumber( self ):
        self.assertEquals( 'Hello 123!', _substituteVariables( 'Hello $[name]!', {'name': 123 }) )
    def testList( self ):
        self.assertEquals( 'Hello [123, 456]!', _substituteVariables( 'Hello $[name]!', {'name': [123, 456] }) )
    def testTuple( self ):
        self.assertEquals( 'Hello (123, 456)!', _substituteVariables( 'Hello $[name]!', {'name': (123, 456) }) )
    def testCallable( self ):
        self.assertEquals( 'Hello world!', _substituteVariables( 'Hello $[name]!', {'name': lambda expression, variables: 'world'} ) )
    def testCallableReturningNone( self ):
        self.assertEquals( 'Hello !', _substituteVariables( 'Hello $[name]!', {'name': lambda expression, variables: None} ) )
    def testWithExtraSpaces( self ):
        self.assertEquals( 'Hello world!', _substituteVariables( 'Hello $[ person.name ]!', {'person': {'name': 'world'}} ) )

class VariableSubstitutionWithFilteringTest( unittest.TestCase ):
    def testUpper( self ):
        self.assertEquals( 'Hello WORLD!', _substituteVariables( 'Hello $[name|upper]!', {'name': 'world', 'upper': string.upper } ) )
    def testListProcessing( self ):
        self.assertEquals( 'Hello John Smith!', _substituteVariables( 'Hello $[name|join]!', {'name': ['John', 'Smith'], 'join': string.join } ) )
    def testListWithLambdaOnList( self ):
        self.assertEquals( 'deploymentTargets are [WebSphere:cell=wdrCell,cluster=wdrCluster+WebSphere:cell=wdrCell,node=httpNode01,server=httpServer01]', 
            _substituteVariables( 'deploymentTargets are [$[deploymentTargets|joinDeploymentTargets]]', 
                {
                    'deploymentTargets': [
                        [['cell', 'wdrCell'], ['cluster', 'wdrCluster']],
                        [['cell', 'wdrCell'], ['node', 'httpNode01'], ['server', 'httpServer01']]
                        ],
                    'joinDeploymentTargets': lambda targetList: ('+'.join(['WebSphere:' + ','.join(['='.join(attList) for attList in target]) for target in targetList])) } ) )
    def testListWithLambdaOnDict( self ):
        self.assertEquals( 'deploymentTargets are [WebSphere:cell=wdrCell,cluster=wdrCluster+WebSphere:cell=wdrCell,node=httpNode01,server=httpServer01]', 
            _substituteVariables( 'deploymentTargets are [$[deploymentTargets|joinDeploymentTargets]]', 
                {
                    'deploymentTargets': [
                        {'cell': 'wdrCell', 'cluster': 'wdrCluster'},
                        {'cell': 'wdrCell', 'node': 'httpNode01', 'server': 'httpServer01'}
                    ],
                    'joinDeploymentTargets': lambda targetList: ('+'.join(['WebSphere:cell=%(cell)s,cluster=%(cluster)s' % t for t in filter(lambda e: e.get('cluster'), targetList)] + ['WebSphere:cell=%(cell)s,node=%(node)s,server=%(server)s' % t for t in filter(lambda e: e.get('node') and e.get('server'), targetList)])) } ) )
    def testWithExtraSpaces( self ):
        self.assertEquals( 'Hello WORLD!', _substituteVariables( 'Hello $[ name | upper ]!', {'name': 'world', 'upper': string.upper } ) )
