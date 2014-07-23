#
# Copyright 2012,2014 Marcin Plonka <mplonka@gmail.com>
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

import logging
import re
import wdr

( AdminApp, AdminConfig, AdminControl, AdminTask, Help ) = wdr.WsadminObjects().getObjects()
logger = logging.getLogger( 'wdrTask' )

_listPattern = re.compile( r'\[(.*)\]' )
_itemPattern = re.compile( r'(?<=\[)(?P<key>\S+)\s+(?:\[(?P<valueQuoted>[^\]]+)\]|(?P<valueNotQuoted>[^ \[\]]+))' )

def adminTaskAsDict( adminTaskList ):
    result = {}
    for ( key, valueQuoted, valueNotQuoted ) in _itemPattern.findall( adminTaskList ):
        result[key] = valueQuoted or valueNotQuoted
    return result

def adminTaskAsDictList( adminTaskListOfLists ):
    result = []
    for l in adminTaskListOfLists.splitlines():
        listMatcher = _listPattern.match( l )
        if listMatcher:
            result.append( adminTaskAsDict( listMatcher.group( 1 ) ) )
    return result
