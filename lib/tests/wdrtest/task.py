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
from wdr.task import *

class AdminTaskDictTest( unittest.TestCase ):
    def testEmpty( self ):
        output = ''
        self.assertEquals( adminTaskAsDict( output ),
            {} )

    def testSiple( self ):
        output = '[a 1][b 2][c 3]'
        self.assertEquals( adminTaskAsDict( output ), {'a':'1', 'b':'2', 'c':'3'} )

    def testSpecialCharsInNames( self ):
        output = '[a 1][b.0 2][c 3]'
        self.assertEquals( adminTaskAsDict( output ), {'a':'1', 'b.0':'2', 'c':'3'} )

    def testSpecialCharsInValues( self ):
        output = '[a 1][b {http://www.a123.com/unicorn/V1}WebService_V1.0][c 3]'
        self.assertEquals( adminTaskAsDict( output ),
            {'a':'1', 'b':'{http://www.a123.com/unicorn/V1}WebService_V1.0', 'c':'3'} )

    def testQuotedValues( self ):
        output = '[a 1][binding [Provider sample]][c 3]'
        self.assertEquals( adminTaskAsDict( output ),
            {'a':'1', 'binding':'Provider sample', 'c':'3'} )

class AdminTaskDictListTest( unittest.TestCase ):
    def testEmpty( self ):
        output = ''
        self.assertEquals( adminTaskAsDictList( output ),
            [
            ] )

    def testSiple( self ):
        output = ( '[[a 1][b 2][c 3]]\n'
            '[[d 4][e 5][f 6]]\n'
            '[[g 7][h 8][i 9]]' )
        self.assertEquals( adminTaskAsDictList( output ),
            [
                {'a':'1', 'b':'2', 'c':'3'},
                {'d':'4', 'e':'5', 'f':'6'},
                {'g':'7', 'h':'8', 'i':'9'}
            ] )

    def testSpecialCharsInNames( self ):
        output = ( '[[a 1][b.0 2][c 3]]\n'
            '[[d 4][e 5][f 6]]\n'
            '[[g 7][h 8][i 9]]' )
        self.assertEquals( adminTaskAsDictList( output ),
            [
                {'a':'1', 'b.0':'2', 'c':'3'},
                {'d':'4', 'e':'5', 'f':'6'},
                {'g':'7', 'h':'8', 'i':'9'}
            ] )

    def testSpecialCharsInValues( self ):
        output = ( '[[a 1][b {http://www.a123.com/unicorn/V1}WebService_V1.0][c 3]]\n'
            '[[d 4][e 5][f 6]]\n'
            '[[g 7][h 8][i 9]]' )
        self.assertEquals( adminTaskAsDictList( output ),
            [
                {'a':'1', 'b':'{http://www.a123.com/unicorn/V1}WebService_V1.0', 'c':'3'},
                {'d':'4', 'e':'5', 'f':'6'},
                {'g':'7', 'h':'8', 'i':'9'}
            ] )

    def testQuotedValues( self ):
        output = ( '[[a 1][binding [Provider sample]][c 3]]\n'
            '[[d 4][e 5][f 6]]\n'
            '[[g 7][h 8][i 9]]' )
        self.assertEquals( adminTaskAsDictList( output ),
            [
                {'a':'1', 'binding':'Provider sample', 'c':'3'},
                {'d':'4', 'e':'5', 'f':'6'},
                {'g':'7', 'h':'8', 'i':'9'}
            ] )

class AdminTaskListOfListsTest( unittest.TestCase ):
    def testEmpty( self ):
        output = ''
        self.assertEquals( adminTaskAsListOfLists( output ),
            [] )

    def testSiple( self ):
        output = '[a 1][b 2][c 3]'
        self.assertEquals( adminTaskAsListOfLists( output ),
            [['a','1'], ['b','2'], ['c','3']] )

    def testSpecialCharsInNames( self ):
        output = '[a 1][b.0 2][c 3]'
        self.assertEquals( adminTaskAsListOfLists( output ),
            [['a','1'], ['b.0','2'], ['c','3']] )

    def testSpecialCharsInValues( self ):
        output = '[a 1][b {http://www.a123.com/unicorn/V1}WebService_V1.0][c 3]'
        self.assertEquals( adminTaskAsListOfLists( output ),
            [['a','1'], ['b','{http://www.a123.com/unicorn/V1}WebService_V1.0'], ['c','3']] )

    def testQuotedValues( self ):
        output = '[a 1][binding [Provider sample]][c 3]'
        self.assertEquals( adminTaskAsListOfLists( output ),
            [['a','1'], ['binding','Provider sample'], ['c','3']] )

class AdminTaskListOfListsListTest( unittest.TestCase ):
    def testEmpty( self ):
        output = ''
        self.assertEquals( adminTaskAsListOfListsList( output ),
            [
            ] )

    def testSiple( self ):
        output = ( '[[a 1][b 2][c 3]]\n'
            '[[d 4][e 5][f 6]]\n'
            '[[g 7][h 8][i 9]]' )
        self.assertEquals( adminTaskAsListOfListsList( output ),
            [
                [['a','1'], ['b','2'], ['c','3']],
                [['d','4'], ['e','5'], ['f','6']],
                [['g','7'], ['h','8'], ['i','9']]
            ] )

    def testSpecialCharsInNames( self ):
        output = ( '[[a 1][b.0 2][c 3]]\n'
            '[[d 4][e 5][f 6]]\n'
            '[[g 7][h 8][i 9]]' )
        self.assertEquals( adminTaskAsListOfListsList( output ),
            [
                [['a','1'], ['b.0','2'], ['c','3']],
                [['d','4'], ['e','5'], ['f','6']],
                [['g','7'], ['h','8'], ['i','9']]
            ] )

    def testSpecialCharsInValues( self ):
        output = ( '[[a 1][b {http://www.a123.com/unicorn/V1}WebService_V1.0][c 3]]\n'
            '[[d 4][e 5][f 6]]\n'
            '[[g 7][h 8][i 9]]' )
        self.assertEquals( adminTaskAsListOfListsList( output ),
            [
                [['a','1'], ['b','{http://www.a123.com/unicorn/V1}WebService_V1.0'], ['c','3']],
                [['d','4'], ['e','5'], ['f','6']],
                [['g','7'], ['h','8'], ['i','9']]
            ] )

    def testQuotedValues( self ):
        output = ( '[[a 1][binding [Provider sample]][c 3]]\n'
            '[[d 4][e 5][f 6]]\n'
            '[[g 7][h 8][i 9]]' )
        self.assertEquals( adminTaskAsListOfListsList( output ),
            [
                [['a','1'], ['binding','Provider sample'], ['c','3']],
                [['d','4'], ['e','5'], ['f','6']],
                [['g','7'], ['h','8'], ['i','9']]
            ] )

