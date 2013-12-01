#
# Copyright 2012,2013 Marcin Plonka <mplonka@gmail.com>
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
import sys

__all__ = ['config', 'control', 'manifest', 'util']

logger = logging.getLogger( 'wdr' )

MAJOR_VERSION = 0
MINOR_VERSION = 3

class WsadminObjects:
    __wsadminObjects = None
    def __init__( self ):
        if self.__wsadminObjects is None:
            rootFrame = sys._getframe()
            while rootFrame.f_back:
                rootFrame = rootFrame.f_back
            values = []
            for v in ( 'AdminApp', 'AdminConfig', 'AdminControl', 'AdminTask', 'Help' ):
                try:
                    values.append( rootFrame.f_globals[v] )
                except:
                    logger.warning( 'unable to retrieve wsadmin object: %s', v )
                    values.append( None )
            self.__wsadminObjects = values
    def getObjects( self ):
        return tuple( self.__wsadminObjects )

( AdminApp, AdminConfig, AdminControl, AdminTask, Help ) = WsadminObjects().getObjects()

def versionInfo():
    logger.info( 'using WDR (http://wdr.github.io/WDR/) version %d.%d', MAJOR_VERSION, MINOR_VERSION )
    if AdminControl.adminClient:
        logger.info( 'the client is connected to host %s:%s using %s connector', AdminControl.host, AdminControl.port, AdminControl.type )
        logger.info( 'the target process is %s/%s/%s', AdminControl.cell, AdminControl.node, AdminControl.processName )
    else:
        logger.warning( 'the client is not connected to live server instance' )

