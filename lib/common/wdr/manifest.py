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

from types import ListType
import com.ibm.ws.scripting
import logging
import os
import re
import sys
import wdr.config
import wdr.task

logger = logging.getLogger( 'wdrManifest' )

_genericPattern = re.compile( r'^(?P<tabs>\t*).*$' )
_commentPattern = re.compile( r'^(?:#\.*)|(?:\n)' )
_directivePattern = re.compile( r'^(?P<tabs>\t*)@\s*(?P<name>[A-Za-z][a-zA-Z0-9_]*)(?P<values>(?:\s*(?P<value>.+?))*)?\s*$' )
_typePattern = re.compile( r'^(?P<tabs>\t*)(?P<type>[A-Za-z][a-zA-Z0-9_]*)\s*(?P<linkage>[&#][a-zA-Z0-9_]+)?\s*$' )
_keyPattern = re.compile( r'^(?P<tabs>\t*)\*(?P<name>[A-Za-z][a-zA-Z0-9_]*)\s*(?P<value>.+?)?\s*$' )
_attPattern = re.compile( r'^(?P<tabs>\t*)-(?P<name>[A-Za-z][a-zA-Z0-9_]*)\s*(?P<value>.+?)?\s*$' )
_variablePattern = re.compile( r'(?P<var>\$\[[a-zA-Z][a-zA-Z0-9]*\])' )
_appNamePattern = re.compile( r'^(?:(?:"(?P<qname>[^"]+)")|(?P<name>\S+))\s+(?:(?:"(?P<qpath>[^"]+)")|(?P<path>.+?))\s*$' )
_appOptionPattern = re.compile( r'^(?P<tabs>\t)(?P<name>\*?[a-zA-Z0-9_\.]+)\s*(?P<value>.+?)?\s*$' )
_appOptionValuePattern = re.compile( r'^(?P<tabs>\t\t)(?P<value>.+?)\s*$' )

class ManifestConfigObject:
    def __init__( self, type ):
        self.type = type
        self.children = []
        self.keys = {}
        self.attributes = {}
        self.anchor = None
        self.reference = None
        self._orderedAttributeNames = []
    def isEmpty( self ):
        return len( self.children ) == 0 and len( self.keys ) == 0 and len( self.attributes ) == 0
    def __str__( self ):
        return self._toString( 0 )
    def __unicode__( self ):
        return unicode( self._toString( 0 ) )
    def _toString( self, indent ):
        result = ''
        if self.anchor:
            result += "%s%s #%s\n" % ( "\t"*indent, self.type, self.anchor )
        elif self.reference:
            result += "%s%s &%s\n" % ( "\t"*indent, self.type, self.reference )
        else:
            result += "%s%s\n" % ( "\t"*indent, self.type )
        for ( k, v ) in self.keys.items():
            result += "%s*%s %s\n" % ( "\t"*( indent + 1 ), k, v )
        for k in self._orderedAttributeNames:
            v = self.attributes[k]
            if isinstance( v, ListType ):
                result += "%s-%s\n" % ( "\t"*( indent + 1 ), k )
                for c in v:
                    result += c._toString( indent + 2 )
            elif isinstance( v, ManifestConfigObject ):
                result += v._toString( indent + 1 )
            else:
                result += "%s-%s %s\n" % ( "\t"*( indent + 1 ), k, v )
        for c in self.children:
            result += c._toString( indent + 1 )
        return result

class LoadError:
    def __init__( self, message, filename = '', line = '', lineno = 0 ):
        self.message = message
        self.filename = filename
        self.line = line[0:-1]
        self.lineno = lineno
    def __str__( self ):
        return '(%s:%d) %s: %s' % ( self.filename, self.lineno, self.message, self.line )
    def __unicode__( self ):
        return unicode( self.__str__() )

class _ConfigEventConsumer:
    def __init__( self ):
        pass
    def consumeObject( self, filename, line, lineno, manifestPath ):
        logger.error( 'manifest parsing error - unexpected object definition at line %d', lineno )
        raise LoadError( 'Unexpected object definition', filename, line, lineno )
    def consumeKey( self, filename, line, lineno, variables, manifestPath ):
        logger.error( 'manifest parsing error - unexpected object key at line %d', lineno )
        raise LoadError( 'Unexpected key', filename, line, lineno )
    def consumeAttribute( self, filename, line, lineno, variables, manifestPath ):
        logger.error( 'manifest parsing error - unexpected object attribute at line %d', lineno )
        raise LoadError( 'Unexpected attribute', filename, line, lineno )
    def consumeDirective( self, filename, line, lineno, variables, manifestPath ):
        logger.error( 'manifest parsing error - unexpected directive at line %d', lineno )
        raise LoadError( 'Unexpected directive', filename, line, lineno )
    def consumeComment( self, filename, line, lineno, manifestPath ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'skipping comment [%d][%s]', lineno, line )

class _ObjectConsumer( _ConfigEventConsumer ):
    def __init__( self, parentList ):
        _ConfigEventConsumer.__init__( self )
        self.parentList = parentList
    def consumeObject( self, filename, line, lineno, manifestPath ):
        mat = _typePattern.match( line )
        name = mat.group( 'type' )
        linkage = mat.group( 'linkage' )
        obj = ManifestConfigObject( name )
        if linkage:
            if linkage[0] == '#':
                obj.anchor = linkage[1:]
            else:
                obj.reference = linkage[1:]
        self.parentList.append( obj )
        return [self, _ObjectDataConsumer( obj )]
    def consumeDirective( self, filename, line, lineno, variables, manifestPath ):
        mat = _directivePattern.match( line )
        name = mat.group( 'name' )
        values = mat.group( 'values' ).split()
        if 'include' == name:
            self.parentList.extend( _loadConfigurationManifest( _locateManifestFile( values[0], [os.path.dirname( filename )] ), variables, manifestPath ) )
            return [self]
        elif 'import' == name:
            self.parentList.extend( _loadConfigurationManifest( _locateManifestFile( values[0], manifestPath ), variables, manifestPath ) )
            return [self]
        logger.error( 'manifest parsing error - unexpected directive at line %d', lineno )
        raise LoadError( 'Unexpected directive', filename, line, lineno )

class _ObjectDataConsumer( _ConfigEventConsumer ):
    def __init__( self, parentObject ):
        _ConfigEventConsumer.__init__( self )
        self.parentObject = parentObject
    def consumeKey( self, filename, line, lineno, variables, manifestPath ):
        mat = _keyPattern.match( line )
        name = mat.group( 'name' )
        value = re.sub( _variablePattern, lambda k, v = variables:v[k.group( 'var' )[2:-1]], mat.group( 'value' ) )
        self.parentObject.keys[name] = value
        return [self]
    def consumeAttribute( self, filename, line, lineno, variables, manifestPath ):
        mat = _attPattern.match( line )
        name = mat.group( 'name' )
        value = mat.group( 'value' )
        if value is None:
            values = []
            self.parentObject.attributes[name] = values
            self.parentObject._orderedAttributeNames.append( name )
            return [self, _ObjectConsumer( values )]
        else:
            self.parentObject.attributes[name] = re.sub( _variablePattern, lambda k, v = variables:v[k.group( 'var' )[2:-1]], value )
            self.parentObject._orderedAttributeNames.append( name )
            return [self, _ConfigEventConsumer()]
    def consumeObject( self, filename, line, lineno, manifestPath ):
        mat = _typePattern.match( line )
        name = mat.group( 'type' )
        linkage = mat.group( 'linkage' )
        obj = ManifestConfigObject( name )
        if linkage:
            if linkage[0] == '#':
                obj.anchor = linkage[1:]
            else:
                obj.reference = linkage[1:]
        self.parentObject.children.append( obj )
        return [self, _ObjectDataConsumer( obj )]
    def consumeDirective( self, filename, line, lineno, variables, manifestPath ):
        mat = _directivePattern.match( line )
        name = mat.group( 'name' )
        values = mat.group( 'values' ).split()
        if 'include' == name:
            self.parentObject.children.extend( _loadConfigurationManifest( _locateManifestFile( values[0], [os.path.dirname( filename )] ), variables, manifestPath ) )
            return [self]
        elif 'import' == name:
            self.parentObject.children.extend( _loadConfigurationManifest( _locateManifestFile( values[0], manifestPath ), variables, manifestPath ) )
            return [self]
        logger.error( 'manifest parsing error - unexpected directive at line %d', lineno )
        raise LoadError( 'Unexpected directive', filename, line, lineno )

class ApplicationDeploymentListener:
    def beforeInstall( self, appName, archivePath ):
        pass
    def beforeUpdate( self, appName, archivePath ):
        pass
    def afterInstall( self, appName, archivePath ):
        pass
    def afterUpdate( self, appName, archivePath ):
        pass
    def skippedUpdate( self, appName, archivePath ):
        pass

class ApplicationObject:
    def __init__( self, name, archive ):
        self.name = name
        self.archive = archive
        self.options = {}
        self.extras = {}
    def __str__( self ):
        result = ''
        if self.name.find( ' ' ) == -1:
            result += '%s ' % self.name
        else:
            result += '"%s" ' % self.name
        if self.archive.find( ' ' ) == -1:
            result += '%s\n' % self.archive
        else:
            result += '"%s"\n' % self.archive
        extraOptionNames = self.extras.keys()
        extraOptionNames.sort()
        for k in extraOptionNames:
            v = self.extras[k]
            if isinstance( v, ListType ):
                result += '\t*%s\n' % k
                for c in v:
                    if isinstance( c, ListType ):
                        result += '\t\t%s\n' % ';'.join( c )
                    else:
                        result += '\t\t%s\n' % c
            else:
                result += '\t*%s %s\n' % ( k, v )
        optionNames = self.options.keys()
        optionNames.sort()
        for k in optionNames:
            v = self.options[k]
            if isinstance( v, ListType ):
                result += '\t%s\n' % k
                for c in v:
                    if isinstance( c, ListType ):
                        result += '\t\t%s\n' % ';'.join( c )
                    else:
                        result += '\t\t%s\n' % c
            else:
                result += '\t%s %s\n' % ( k, v )
        return result
    def __unicode__( self ):
        return unicode( self.__str__() )

class _AppEventConsumer:
    def __init__( self ):
        pass
    def consumeApp( self, filename, line, lineno, variables ):
        logger.error( 'manifest parsing error - unexpected application definition at line %d', lineno )
        raise LoadError( 'Unexpected application definition', filename, line, lineno )
    def consumeOption( self, filename, line, lineno, variables ):
        logger.error( 'manifest parsing error - unexpected option at line %d', lineno )
        raise LoadError( 'Unexpected option', filename, line, lineno )
    def consumeOptionValue( self, filename, line, lineno, variables ):
        logger.error( 'manifest parsing error - unexpected option value at line %d', lineno )
        raise LoadError( 'Unexpected option value', filename, line, lineno )
    def consumeComment( self, filename, line, lineno ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'skipping comment [%d][%s]', lineno, line )

class _AppConsumer( _AppEventConsumer ):
    def __init__( self, parentList ):
        _AppEventConsumer.__init__( self )
        self.parentList = parentList
    def consumeApp( self, filename, line, lineno, variables ):
        mat = _appNamePattern.match( line )
        name = mat.group( 'name' )
        if name is None:
            name = mat.group( 'qname' )
        name = re.sub( _variablePattern, lambda k, v = variables:v[k.group( 'var' )[2:-1]], name )
        archive = mat.group( 'path' )
        if archive is None:
            archive = mat.group( 'qpath' )
        archive = re.sub( _variablePattern, lambda k, v = variables:v[k.group( 'var' )[2:-1]], archive )
        dirname = os.path.dirname( os.path.normpath( os.path.abspath( filename ) ) )
        archive = os.path.normpath( os.path.join( dirname, archive ) )
        obj = ApplicationObject( name, archive )
        self.parentList.append( obj )
        return [self, _AppOptionConsumer( obj )]

class _AppOptionConsumer( _AppEventConsumer ):
    def __init__( self, parentObject ):
        _AppEventConsumer.__init__( self )
        self.parentObject = parentObject
    def consumeOption( self, filename, line, lineno, variables ):
        mat = _appOptionPattern.match( line )
        name = mat.group( 'name' )
        value = mat.group( 'value' )
        if name == 'appname':
            logger.error( 'The \'appname\' option is not allowed in application manifest' )
            raise LoadError( 'The \'appname\' option is not allowed in application manifest', filename, line, lineno )
        if name.startswith( '*' ):
            name = name[1:]
            if value is None:
                values = []
                self.parentObject.extras[name] = values
                return [self, _AppOptionValueConsumer( values )]
            else:
                self.parentObject.extras[name] = re.sub( _variablePattern, lambda k, v = variables:v[k.group( 'var' )[2:-1]], value )
                return [self, _AppEventConsumer()]
            pass
        else:
            if value is None:
                values = []
                self.parentObject.options[name] = values
                return [self, _AppOptionValueConsumer( values )]
            else:
                self.parentObject.options[name] = re.sub( _variablePattern, lambda k, v = variables:v[k.group( 'var' )[2:-1]], value )
                return [self, _AppEventConsumer()]

class _AppOptionValueConsumer( _AppEventConsumer ):
    def __init__( self, parentList ):
        _AppEventConsumer.__init__( self )
        self.parentList = parentList
    def consumeOptionValue( self, filename, line, lineno, variables ):
        mat = _appOptionValuePattern.match( line )
        value = mat.group( 'value' )
        self.parentList.append( re.sub( _variablePattern, lambda k, v = variables:v[k.group( 'var' )[2:-1]], value ).split( ';' ) )
        return [self, _AppEventConsumer()]

def _extraOptionProcessor_startingWeight( mo, name, value ):
    wdr.config.getid1( '/Deployment:%s' % mo.name ).deployedObject.startingWeight = value

def _extraOptionProcessor_classLoadingMode( mo, name, value ):
    wdr.config.getid1( '/Deployment:%s' % mo.name ).deployedObject.classloader.mode = value

def _extraOptionProcessor_webModuleClassLoadingMode( mo, name, value ):
    for ( uri, mode ) in value:
        applied = 0
        for module in wdr.config.getid1( '/Deployment:%s' % mo.name ).deployedObject.modules:
            if module._type == 'WebModuleDeployment' and module.uri == uri:
                module.classloaderMode = mode
                applied = 1
        if not applied:
            logger.error( 'webModuleClassLoadingMode option could not match module %s', uri )
            raise Exception( 'webModuleClassLoadingMode option could not match module %s', uri )

def _extraOptionProcessor_clientWSPolicySetAttachments( mo, name, value ):
    appName = mo.name
    for att in wdr.task.adminTaskAsDictList(AdminTask.getPolicySetAttachments(['-applicationName', appName, '-attachmentType', 'client'])):
        AdminTask.deletePolicySetAttachment(['-attachmentId', att['id'], '-applicationName', appName, '-attachmentType', 'client'])
    for ( policySet, resource, binding ) in value:
        AdminTask.createPolicySetAttachment(['-policySet', policySet, '-resources', [resource], '-applicationName', appName, '-attachmentType', 'client'])
        AdminTask.setBinding(['-bindingScope', 'domain', '-bindingName', binding, '-attachmentType', 'application', '-bindingLocation', [ ['application', appName], ['attachmentId', attId] ], '-attachmentType', 'client'])

def _extraOptionProcessor_applicationWSPolicySetAttachments( mo, name, value ):
    appName = mo.name
    for att in wdr.task.adminTaskAsDictList(AdminTask.getPolicySetAttachments(['-applicationName', appName, '-attachmentType', 'application'])):
        AdminTask.deletePolicySetAttachment(['-attachmentId', att['id'], '-applicationName', appName, '-attachmentType', 'application'])
    for ( policySet, resource, binding ) in value:
        attId = AdminTask.createPolicySetAttachment(['-policySet', policySet, '-resources', [resource], '-applicationName', appName, '-attachmentType', 'application'])
        AdminTask.setBinding(['-bindingScope', 'domain', '-bindingName', binding, '-attachmentType', 'application', '-bindingLocation', [ ['application', appName], ['attachmentId', attId] ], '-attachmentType', 'application'])

def _extraOptionProcessor_systemTrustWSPolicySetAttachments( mo, name, value ):
    appName = mo.name
    for att in wdr.task.adminTaskAsDictList(AdminTask.getPolicySetAttachments(['-applicationName', appName, '-attachmentType', 'system/trust'])):
        AdminTask.deletePolicySetAttachment(['-attachmentId', att['id'], '-applicationName', appName, '-attachmentType', 'system/trust'])
    for ( policySet, resource, binding ) in value:
        AdminTask.createPolicySetAttachment(['-policySet', policySet, '-resources', [resource], '-applicationName', appName, '-attachmentType', 'system/trust'])
        AdminTask.setBinding(['-bindingScope', 'domain', '-bindingName', binding, '-attachmentType', 'application', '-bindingLocation', [ ['application', appName], ['attachmentId', attId] ], '-attachmentType', 'system/trust'])

def _extraOptionProcessor_providerPolicySharingInfo( mo, name, value ):
    appName = mo.name
    for si in wdr.task.adminTaskAsDictList(AdminTask.getProviderPolicySharingInfo(['-applicationName', appName])):
        AdminTask.setProviderPolicySharingInfo(['-applicationName', appName, '-resource', si['resource'], '-remove', 'true'])
    for row in value:
        ( resource, methods ) = row[0:2]
        wsMexPolicySetName = None
        wsMexPolicySetBinding = None
        if len( row ) > 2:
            wsMexPolicySetName = row[2]
        if len( row ) > 3:
            wsMexPolicySetBinding = row[3]
        args = ['-applicationName', appName, '-resource', resource, '-sharePolicyMethods', methods]
        wsMexProperties = []
        if wsMexPolicySetName:
            wsMexProperties.append(['wsMexPolicySetName', wsMexPolicySetName])
        if wsMexPolicySetBinding:
            wsMexProperties.append(['wsMexPolicySetBinding', wsMexPolicySetBinding])
        if wsMexProperties:
            args.append(['-wsMexProperties', wsMexProperties])
        AdminTask.setProviderPolicySharingInfo(args)

def _extraOptionProcessor_scaImportWSBindings( mo, name, value ):
    appName = mo.name
    for ( moduleName, importName, endpoint ) in value:
        AdminTask.modifySCAImportWSBinding(['-applicationName', appName, '-moduleName', moduleName, '-import', importName, '-endpoint', endpoint])

def _extraOptionProcessor_scaModuleProperties( mo, name, value ):
    appName = mo.name
    for ( moduleName, propertyName, propertyValue ) in value:
        AdminTask.modifySCAModuleProperty(['-applicationName', appName, '-moduleName', moduleName, '-propertyName', propertyName, '-newPropertyValue', propertyValue])

_extraOptionNamesOrdered = (
    'startingWeight',
    'classLoadingMode',
    'webModuleClassLoadingMode',
    'scaImportWSBindings',
    'scaModuleProperties',
    'applicationWSPolicySetAttachments',
    'clientWSPolicySetAttachments',
    'systemTrustWSPolicySetAttachments',
    'providerPolicySharingInfo',
    )

_extraOptionProcessors = {
    'startingWeight': _extraOptionProcessor_startingWeight,
    'classLoadingMode': _extraOptionProcessor_classLoadingMode,
    'webModuleClassLoadingMode': _extraOptionProcessor_webModuleClassLoadingMode,
    'scaImportWSBindings': _extraOptionProcessor_scaImportWSBindings,
    'scaModuleProperties': _extraOptionProcessor_scaModuleProperties,
    'applicationWSPolicySetAttachments': _extraOptionProcessor_applicationWSPolicySetAttachments,
    'clientWSPolicySetAttachments': _extraOptionProcessor_clientWSPolicySetAttachments,
    'systemTrustWSPolicySetAttachments': _extraOptionProcessor_systemTrustWSPolicySetAttachments,
    'providerPolicySharingInfo': _extraOptionProcessor_providerPolicySharingInfo,
}

def processExtraAppOption( mo, name, value ):
    extraOptionProcessor = _extraOptionProcessors.get( name )
    if extraOptionProcessor:
        extraOptionProcessor( mo, name, value )
    else:
        logger.error( 'Extra option "%s" specified for %s is not supported', name, mo.name )
        raise Exception( 'Extra option "%s" specified for %s is not supported' % ( name, mo.name ) )

def _importApplicationManifest( filename, variables ):
    if logger.isEnabledFor( logging.DEBUG ):
        logger.debug( 'loading file %s with variables %s', filename, variables )
    fi = open( filename, 'r' )
    if logger.isEnabledFor( logging.DEBUG ):
        logger.debug( 'file %s successfully opened', filename )
    try:
        manifestObjects = []
        stack = [_AppConsumer( manifestObjects )]
        lineno = 0
        for line in fi.readlines():
            lineno += 1
            imat = _genericPattern.match( line )
            if not imat:
                logger.error( 'wrong indentation in line %d', lineno )
                raise LoadError( 'Wrong indentation', filename, line, lineno )
            indent = len( imat.group( 'tabs' ) )
            if len( stack ) < indent + 1:
                return manifestObjects
            if _appNamePattern.match( line ):
                stack = stack[0:indent] + stack[indent].consumeApp( filename, line, lineno, variables )
            elif _appOptionPattern.match( line ):
                stack = stack[0:indent] + stack[indent].consumeOption( filename, line, lineno, variables )
            elif _appOptionValuePattern.match( line ):
                stack = stack[0:indent] + stack[indent].consumeOptionValue( filename, line, lineno, variables )
            elif _commentPattern.match( line ):
                stack[indent].consumeComment( filename, line, lineno )
            else:
                logger.error( 'invalid manifest statement in line %s', lineno )
                raise LoadError( 'Not recognized', filename, line, lineno )
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'file %s successfuly parsed', filename )
        return manifestObjects
    finally:
        fi.close()

def loadApplications( filename, variables = {}, listener = None ):
    logger.warning( 'wdr.manifest.loadApplications is deprecated and will be removed in v0.5. Use importApplicationManifest instead' )
    return importApplicationManifest( filename, variables, listener )

def importApplicationManifest( filename, variables = {}, listener = None, manifestPath = None ):
    if listener is None:
        listener = ApplicationDeploymentListener()
    if manifestPath is None:
        manifestPath = ['.']
        sysPathReversed = sys.path[:]
        sysPathReversed.reverse()
        manifestPath.extend( sysPathReversed )
    affectedApplications = []
    for mo in _importApplicationManifest( _locateManifestFile( filename, manifestPath ), variables ):
        if mo.name in wdr.app.listApplications():
            deployment = wdr.config.getid1( '/Deployment:%s/' % mo.name )
            deployedChecksumProperties = deployment.deployedObject.lookup( 'Property', {'name':'wdr.checksum'} )
            if deployedChecksumProperties:
                deployedChecksum = deployedChecksumProperties[0].value
            else:
                deployedChecksum = ''
            fileChecksum = wdr.util.generateSHA512( mo.archive )
            manifestChecksum = wdr.util.sha512( str( mo ) )
            calculatedChecksum = fileChecksum + ';' + manifestChecksum
            if deployedChecksum == calculatedChecksum:
                if logger.isEnabledFor( logging.DEBUG ):
                    logger.debug( 'skipping update of %s, due to matching checksum (%s)', mo.name, calculatedChecksum )
                listener.skippedUpdate( mo.name, mo.archive )
            else:
                listener.beforeUpdate( mo.name, mo.archive )
                logger.debug( 'application %s will be updated. deployedChecksum(%s), calculatedChecksum(%s)', mo.name, deployedChecksum, calculatedChecksum )
                action = wdr.app.UpdateApp()
                for ( k, v ) in mo.options.items():
                    if v:
                        action[k] = v
                    else:
                        action[k] = None
                action.contents = mo.archive
                action( mo.name )
                wdr.config.getid1( '/Deployment:%s/' % mo.name ).deployedObject.assure( 'Property', {'name':'wdr.checksum'}, 'properties', value = calculatedChecksum, description = 'Checksum of deployed EAR file and application manifest' )
                affectedApplications.append( mo.name )
                listener.afterUpdate( mo.name, mo.archive )
        else:
            listener.beforeInstall( mo.name, mo.archive )
            action = wdr.app.Install()
            for ( k, v ) in mo.options.items():
                if v:
                    action[k] = v
                else:
                    action[k] = None
            action['appname'] = mo.name
            action( mo.archive )
            fileChecksum = wdr.util.generateSHA512( mo.archive )
            manifestChecksum = wdr.util.sha512( str( mo ) )
            calculatedChecksum = fileChecksum + ';' + manifestChecksum
            wdr.config.getid1( '/Deployment:%s/' % mo.name ).deployedObject.assure( 'Property', {'name':'wdr.checksum'}, 'properties', value = calculatedChecksum, description = 'Checksum of deployed EAR file and application manifest' )
            affectedApplications.append( mo.name )
            listener.afterInstall( mo.name, mo.archive )
        for extraOptionName in _extraOptionNamesOrdered:
            if mo.extras.has_key( extraOptionName ):
                processExtraAppOption( mo, extraOptionName, mo.extras[ extraOptionName ] )
    return affectedApplications

def loadConfiguration( filename, variables = {} ):
    logger.warning( 'wdr.manifest.loadConfiguration is deprecated and will be removed in v0.5. Use importConfigurationManifest instead' )
    return importConfigurationManifest( filename, variables )

def _locateManifestFile( filename, manifestPath ):
    if logger.isEnabledFor( logging.DEBUG ):
        logger.debug( 'Locating manifest file %s in %s', filename, manifestPath )
    for dirname in manifestPath:
        dirname = os.path.abspath( dirname )
        candidate = os.path.normpath( os.path.join( dirname, filename ) )
        if os.path.isfile( candidate ):
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'Manifest file %s found in %s as %s', filename, dirname, candidate )
            return candidate
        else:
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'Manifest file %s not found in %s', filename, dirname )
    if logger.isEnabledFor( logging.DEBUG ):
        logger.debug( 'Manifest file %s not found in %s', filename, manifestPath )
    raise Exception( 'Manifest file %s not found' % filename )

def _loadConfigurationManifest( filename, variables, manifestPath ):
    filename = os.path.normpath( os.path.abspath( filename ) )
    logger.debug( 'loading file %s with variables %s', filename, variables )
    fi = open( filename, 'r' )
    logger.debug( 'file %s successfully opened', filename )
    try:
        manifestObjects = []
        stack = [_ObjectConsumer( manifestObjects )]
        lineno = 0
        for line in fi.readlines():
            lineno += 1
            imat = _genericPattern.match( line )
            if not imat:
                logger.error( 'wrong indentation in line %d', lineno )
                raise LoadError( 'Wrong indentation', filename, line, lineno )
            indent = len( imat.group( 'tabs' ) )
            if len( stack ) < indent + 1:
                return manifestObjects
            if _typePattern.match( line ):
                stack = stack[0:indent] + stack[indent].consumeObject( filename, line, lineno, manifestPath )
            elif _keyPattern.match( line ):
                stack = stack[0:indent] + stack[indent].consumeKey( filename, line, lineno, variables, manifestPath )
            elif _attPattern.match( line ):
                stack = stack[0:indent] + stack[indent].consumeAttribute( filename, line, lineno, variables , manifestPath)
            elif _directivePattern.match( line ):
                stack = stack[0:indent] + stack[indent].consumeDirective( filename, line, lineno, variables, manifestPath )
            elif _commentPattern.match( line ):
                stack[indent].consumeComment( filename, line, lineno, manifestPath )
            else:
                logger.error( 'invalid manifest statement in line %s', lineno )
                raise LoadError( 'Not recognized', filename, line, lineno )
        logger.debug( 'file %s successfuly parsed', filename )
    finally:
        fi.close()
    return manifestObjects

def importConfigurationManifest( filename, variables = {}, manifestPath = None ):
    if manifestPath is None:
        manifestPath = ['.']
        sysPathReversed = sys.path[:]
        sysPathReversed.reverse()
        manifestPath.extend( sysPathReversed )
    anchors = {}
    for mo in _loadConfigurationManifest( _locateManifestFile( filename, manifestPath ), variables, manifestPath ):
        _importManifestConfigObject( mo, anchors )

def _findMatchingObjects( manifestObject, candidateList ):
    matchingList = []
    for o in candidateList:
        if o._type == manifestObject.type:
            for ( k, v ) in manifestObject.keys.items():
                if o[k] != v:
                    break
            else:
                matchingList.append( o )
    return matchingList

def _createConfigObject( manifestObject, parentObject, parentAttribute = None ):
    typeName = manifestObject.type
    typeInfo = wdr.config.getTypeInfo( typeName )
    simpleAttributes = []
    for ( propName, propValue ) in manifestObject.keys.items():
        if typeInfo.attributes.has_key( propName ):
            if wdr.config.getTypeInfo( typeInfo.attributes[propName].type ).converter:
                simpleAttributes.append( [propName, propValue] )
    for propName in manifestObject._orderedAttributeNames:
        propValue = manifestObject.attributes[propName]
        if typeInfo.attributes.has_key( propName ):
            if wdr.config.getTypeInfo( typeInfo.attributes[propName].type ).converter:
                simpleAttributes.append( [propName, propValue] )
        else:
            raise Exception( 'Invalid attribute %s specified for object %s(%s)' % ( propName, typeName, manifestObject.keys ) )
    result = parentObject._create( typeName, parentAttribute, simpleAttributes )
    return result

def _setAnchor( manifestObject, anchors, configObject ):
    if manifestObject.anchor:
        if anchors.has_key( manifestObject.anchor ):
            raise Exception( 'Duplicate anchor: %s' % manifestObject.anchor )
        else:
            logger.debug( 'setting anchor %s to %s', manifestObject.anchor, configObject )
            anchors[manifestObject.anchor] = configObject

def _updateConfigObjectSimpleAttributes( configObject, manifestObject ):
    typeName = manifestObject.type
    typeInfo = wdr.config.getTypeInfo( typeName )
    for propName in manifestObject._orderedAttributeNames:
        propValue = manifestObject.attributes[propName]
        if typeInfo.attributes.has_key( propName ):
            attributeInfo = typeInfo.attributes[propName]
            attributeTypeInfo = wdr.config.getTypeInfo( attributeInfo.type )
            if attributeTypeInfo.converter:
                if attributeInfo.list:
                    if propValue == []:
                        newPropValue = propValue
                    else:
                        newPropValue = propValue.split( ';' )
                else:
                    newPropValue = propValue
                try:
                    configObject._modify( [[propName, newPropValue]] )
                except com.ibm.ws.scripting.ScriptingException, ex:
                    msg = '' + ex.message
                    if msg.find( 'ADMG0014E' ) != -1:
                        if configObject._getConfigAttribute( propName ) != newPropValue:
                            logger.warning( 'read-only attribute %s.%s could not be modified', typeName, propName )
                    else:
                        raise

def _updateConfigObjectKeys( configObject, manifestObject ):
    typeName = manifestObject.type
    typeInfo = wdr.config.getTypeInfo( typeName )
    for ( propName, propValue ) in manifestObject.keys.items():
        if typeInfo.attributes.has_key( propName ):
            attributeInfo = typeInfo.attributes[propName]
            attributeTypeInfo = wdr.config.getTypeInfo( attributeInfo.type )
            if attributeTypeInfo.converter:
                try:
                    if attributeInfo.list:
                        configObject._modify( [[propName, propValue.split( ';' )]] )
                    else:
                        configObject._modify( [[propName, propValue]] )
                except com.ibm.ws.scripting.ScriptingException, ex:
                    msg = '' + ex.message
                    if msg.find( 'ADMG0014E' ) != -1:
                        logger.warning( 'read-only attribute %s.%s could not be modified', typeName, propName )
                    else:
                        raise

def _updateConfigObjectComplexAttributes( configObject, manifestObject, anchors ):
    typeName = manifestObject.type
    typeInfo = wdr.config.getTypeInfo( typeName )
    for propName in manifestObject._orderedAttributeNames:
        propValue = manifestObject.attributes[propName]
        if typeInfo.attributes.has_key( propName ):
            attributeInfo = typeInfo.attributes[propName]
            attributeTypeInfo = wdr.config.getTypeInfo( attributeInfo.type )
            if not attributeTypeInfo.converter:
                for obj in propValue:
                    _importManifestConfigObject( obj, anchors, configObject, propName )

def _updateConfigObjectChildren( configObject, manifestObject, anchors ):
    for obj in manifestObject.children:
        _importManifestConfigObject( obj, anchors, configObject )

def _importManifestConfigObject( manifestObject, anchors, parentObject = None, parentAttribute = None ):
    typeName = manifestObject.type
    logger.debug( 'importing object type %s as child of object %s and property %s', typeName, parentObject, parentAttribute )
    configObject = None
    if parentObject:
        # knowing the parent, we can either create or modify the object
        parentTypeName = parentObject._type
        parentTypeInfo = wdr.config.getTypeInfo( parentTypeName )
        if parentAttribute:
            parentAttributeInfo = parentTypeInfo.attributes[parentAttribute]
            if parentAttributeInfo.list:
                if parentAttributeInfo.reference:
                    # adding object reference to parent's attribute (parent attribute is a list)
                    if not manifestObject.isEmpty():
                        raise Exception( 'Objects being assigned to reference-attributes must not contain keys/attributes/children' )
                    if not manifestObject.reference:
                        raise Exception( 'Objects being assigned to reference-attributes must be references to other objects' )
                    if not anchors.has_key( manifestObject.reference ):
                        raise Exception( 'Unresolved reference: %s' % manifestObject.reference )
                    parentObject[parentAttribute] = parentObject[parentAttribute].append( anchors[manifestObject.reference] )
                else:
                    # adding object to a list
                    matchingObjects = _findMatchingObjects( manifestObject, parentObject[parentAttribute] )
                    if len( matchingObjects ) == 0:
                        configObject = _createConfigObject( manifestObject, parentObject, parentAttribute )
                        _setAnchor( manifestObject, anchors, configObject )
                        _updateConfigObjectComplexAttributes( configObject, manifestObject, anchors )
                        _updateConfigObjectChildren( configObject, manifestObject, anchors )
                    elif len( matchingObjects ) == 1:
                        configObject = matchingObjects[0]
                        _setAnchor( manifestObject, anchors, configObject )
                        _updateConfigObjectSimpleAttributes( configObject, manifestObject )
                        _updateConfigObjectComplexAttributes( configObject, manifestObject, anchors )
                        _updateConfigObjectChildren( configObject, manifestObject, anchors )
                    else:
                        raise Exception( 'Multiple %s objects matched criteria' % typeName )
            else:
                if parentAttributeInfo.reference:
                    # assigning object reference to parent object's attribute
                    if not manifestObject.isEmpty():
                        raise Exception( 'Objects being assigned to reference-attributes must not contain keys/attributes/children' )
                    if not manifestObject.reference:
                        raise Exception( 'Objects being assigned to reference-attributes must be references to other objects' )
                    if not anchors.has_key( manifestObject.reference ):
                        raise Exception( 'Unresolved reference: %s' % manifestObject.reference )
                    parentObject[parentAttribute] = anchors[manifestObject.reference]
                else:
                    # creating/modifying single object attribute
                    if len( manifestObject.keys ) != 0:
                        raise Exception( '%s.%s is not a list, therefore no keys are allowed for its objects' )
                    matchingObjects = [parentObject[parentAttribute]]
                    if len( matchingObjects ) == 0 or ( len( matchingObjects ) == 1 and matchingObjects[0] is None ):
                        configObject = _createConfigObject( manifestObject, parentObject, parentAttribute )
                        _setAnchor( manifestObject, anchors, configObject )
                        _updateConfigObjectComplexAttributes( configObject, manifestObject, anchors )
                        _updateConfigObjectChildren( configObject, manifestObject, anchors )
                    elif len( matchingObjects ) == 1:
                        configObject = matchingObjects[0]
                        _setAnchor( manifestObject, anchors, configObject )
                        _updateConfigObjectKeys( configObject, manifestObject )
                        _updateConfigObjectSimpleAttributes( configObject, manifestObject )
                        _updateConfigObjectComplexAttributes( configObject, manifestObject, anchors )
                        _updateConfigObjectChildren( configObject, manifestObject, anchors )
                    else:
                        raise Exception( 'Multiple %s objects matched criteria' % typeName )
        else:
            # parent attribute name not provided
            if manifestObject.reference:
                raise Exception( 'Reference "%s" was not expected here' % manifestObject.reference )
            matchingObjects = _findMatchingObjects( manifestObject, parentObject.lookup( typeName, {} ) )
            if len( matchingObjects ) == 0:
                configObject = _createConfigObject( manifestObject, parentObject )
                _setAnchor( manifestObject, anchors, configObject )
                _updateConfigObjectComplexAttributes( configObject, manifestObject, anchors )
                _updateConfigObjectChildren( configObject, manifestObject, anchors )
            elif len( matchingObjects ) == 1:
                configObject = matchingObjects[0]
                _setAnchor( manifestObject, anchors, configObject )
                _updateConfigObjectSimpleAttributes( configObject, manifestObject )
                _updateConfigObjectComplexAttributes( configObject, manifestObject, anchors )
                _updateConfigObjectChildren( configObject, manifestObject, anchors )
            else:
                raise Exception( 'Multiple %s objects matched criteria' % typeName )
    else:
        # without knowing the parent, object can be only modified, no new object can be created
        matchingObjects = _findMatchingObjects( manifestObject, wdr.config.listConfigObjects( typeName ) )
        if len( matchingObjects ) == 1:
            configObject = matchingObjects[0]
            _updateConfigObjectSimpleAttributes( configObject, manifestObject )
            _setAnchor( manifestObject, anchors, configObject )
            _updateConfigObjectComplexAttributes( configObject, manifestObject, anchors )
            _updateConfigObjectChildren( configObject, manifestObject, anchors )
        elif len( matchingObjects ) == 0:
            raise Exception( 'No %s object matched criteria' % typeName )
        else:
            raise Exception( 'Multiple %s objects matched criteria' % typeName )
