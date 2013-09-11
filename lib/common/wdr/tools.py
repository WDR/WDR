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

import java.util.List

class ManifestGenerationAdminApp:
    def __init__( self, adminApp ):
        shellField = adminApp.__class__.getSuperclass().getDeclaredField( '_shell' )
        shellField.setAccessible( 1 )
        self.langUtils = shellField.get( adminApp ).getLangUtils()
    def install( self, earfile, options ):
        parsedOptions = self.langUtils.optionsToHashtable( options )
        self._dump( parsedOptions['appname'], earfile, parsedOptions )
    def update( self, appname, type, options ):
        parsedOptions = self.langUtils.optionsToHashtable( options )
        self._dump( appname, parsedOptions['contents'], parsedOptions )
    def _dump( self, appname, earfile, options ):
        print '%s %s' % ( appname, earfile )
        for e in options.entrySet():
            if e.key in ( 'operation', 'contents', 'installed.ear.destination', 'appname' ):
                continue
            if java.util.List.isAssignableFrom( e.value.__class__ ):
                print '\t%s' % e.key
                if e.key == 'MapWebModToVH':
                    for v in e.value:
                        values = [el for el in v]
                        values[2] = '$[virtualHost]'
                        print '\t\t%s' % ';'.join( values )
                elif e.key == 'MapModulesToServers':
                    for v in e.value:
                        values = [el for el in v]
                        if values[0].endswith(',WEB-INF/web.xml'):
                            values[2] = '$[deploymentTargets]+$[webServers]'
                        else:
                            values[2] = '$[deploymentTargets]'
                        print '\t\t%s' % ';'.join( values )
                else:
                    for v in e.value:
                        print '\t\t%s' % ';'.join( v )
            else:
                print '\t%s %s' % ( e.key, e.value )
