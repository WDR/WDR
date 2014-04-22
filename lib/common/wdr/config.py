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

from string import split, join, upper
from types import StringType
import logging
import re
import time
import wdr

( AdminApp, AdminConfig, AdminControl, AdminTask, Help ) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger( 'wdrConfig' )

_configNamePattern = re.compile( r'((?:"(?P<qname>[^"^\[^\]]*)\((?P<qxmlPath>.+?)\|(?P<qxmlDoc>.+?\.xml)#(?P<qxmlId>[a-zA-Z_0-9]+?)\)")|(?:(?P<name>[^ ^"^\[^\]]*)\((?P<xmlPath>.+?)\|(?P<xmlDoc>.+?\.xml)#(?P<xmlId>[a-zA-Z_0-9]+?)\)))' )
_configNameListPattern = re.compile( r'^"?\[(?:(%s) *)*\]"?$' % _configNamePattern.pattern )
_attributeTypePattern = re.compile( '[, \(\)]+' )

_typeRegistryInitialized = 0

class AttributeConverter:
    def __init__( self ):
        pass
    def fromAdminConfig( self, value ):
        raise NotImplementedError
    def toAdminConfig( self, value ):
        raise NotImplementedError

class BooleanAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminConfig( self, value ):
        if value:
            if value == 'true':
                return 1
            else:
                return 0
        return 0
    def toAdminConfig( self, value ):
        if value:
            if isinstance( value, StringType ):
                upperValue = upper( value )
                if upperValue == 'TRUE' or upperValue == 'T' or upperValue == 'YES' or upperValue == 'Y':
                    return 'true'
            elif value == 1:
                return 'true'
        return 'false'

class IntegerAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminConfig( self, value ):
        return int( value, 10 )
    def toAdminConfig( self, value ):
        return str( value )

class LongAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminConfig( self, value ):
        return long( value, 10 )
    def toAdminConfig( self, value ):
        return str( value )

class FloatAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminConfig( self, value ):
        return float( value )
    def toAdminConfig( self, value ):
        return str( value )

class StringAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminConfig( self, value ):
        return value
    def toAdminConfig( self, value ):
        return value

class EnumAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminConfig( self, value ):
        return value
    def toAdminConfig( self, value ):
        return value

def parseAttributeType( attName, attType ):
    attList = 0
    if attType[-1] == '*':
        attList = 1
        attType = attType[:-1]
    attReference = 0
    if attType[-1] == '@':
        attReference = 1
        attType = attType[:-1]
    attTypeAndOptions = _attributeTypePattern.split( attType )
    attTypeName = attTypeAndOptions[0]
    if attTypeName[-1] == '*':
        attList = 1
        attTypeName = attTypeName[:-1]
    attEnumValues = None
    attSubTypes = None
    if attTypeName == 'ENUM':
        if len( attTypeAndOptions ) > 2:
            attEnumValues = attTypeAndOptions[1:-1]
        else:
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'Enum values expected for attribute %s', attName )
            raise Exception( 'Enum values expected for attribute %s' % attName )
    elif len( attTypeAndOptions ) > 2:
        attSubTypes = attTypeAndOptions[1:-1]
    return AttributeInfo( attName, attTypeName, attList, attReference, attEnumValues, attSubTypes )

def _pre7objectTypeRetriever( configId, configNameCache = [None] ):
    if not configNameCache[0]:
        # a dirty hack for accessing non-public AdminConfig.nameCache member
        # hack is targeted for WAS pre-7
        # WAS 7 comes with AdminConfig.getObjectType which eliminates the need for such hack
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'accessing AdminConfig.nameCache field using reflection' )
        configNameCache[0] = AdminConfig.__class__.getDeclaredField( 'nameCache' )
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'setting AdminConfig.nameCache field to accessible via reflection' )
        configNameCache[0].setAccessible( 1 )
    return configNameCache[0].get( AdminConfig ).getType( str( configId ) )

def _post7objectTypeRetriever( configId ):
    return AdminConfig.getObjectType( str( configId ) )

def getObjectType( configId, objectTypeRetriever = [_post7objectTypeRetriever, _pre7objectTypeRetriever] ):
    typeName = None
    try:
        typeName = objectTypeRetriever[0]( str( configId ) )
    except AttributeError, ae:
        if 'getObjectType' not in ae.args:
            raise
        logger.warning( 'default method of retrieving object types has failed, falling back to reflection-based mechanism' )
        # from now on, the default type retriever will be the one using reflection
        objectTypeRetriever[0] = objectTypeRetriever[1]
        typeName = getObjectType( configId )
    getTypeInfo( typeName )
    return typeName

def _isConfigId( str ):
    if( str ):
        return _configNamePattern.match( str ) is not None
    else:
        return 0

def _isConfigIdList( str ):
    if( str ):
        return _configNameListPattern.match( str ) is not None
    else:
        return 0

def _firstNonNone( *args ):
    for v in args:
        if v is not None:
            return v
    return None

def getTypeInfo( typeName ):
    if not _typeRegistry.has_key( typeName ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'introspecting type %s', typeName )
        attributes = {}
        for att in AdminConfig.attributes( typeName ).splitlines():
            ( attName, attType ) = att.split( ' ', 1 )
            attributes[attName] = parseAttributeType( attName, attType )
        _typeRegistry[typeName] = TypeInfo( typeName, attributes, parents( typeName ), [] )
        for parent in parents( typeName ):
            parentTypeInfo = getTypeInfo( parent )
            if not typeName in parentTypeInfo.children:
                parentTypeInfo.children.append( typeName )
    return _typeRegistry[typeName]

def configObject( configId ):
    return ConfigObject( _parseConfigId( configId ) )

def configObjects( configIds ):
    return map( lambda e:configObject( e ), _parseConfigIdList( configIds ) )

def _parseConfigId( configId ):
    mat = _configNamePattern.match( configId )
    if mat:
        name = _firstNonNone( mat.group( 'qname' ), mat.group( 'name' ) )
        xmlPath = _firstNonNone( mat.group( 'qxmlPath' ), mat.group( 'xmlPath' ) )
        xmlDoc = _firstNonNone( mat.group( 'qxmlDoc' ), mat.group( 'xmlDoc' ) )
        xmlId = _firstNonNone( mat.group( 'qxmlId' ), mat.group( 'xmlId' ) )
        return ConfigId( name, xmlPath, xmlDoc, xmlId )
    else:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'ConfigID regular expression matching failed for the string: "%s"', configId )
        raise Exception( 'Invalid configuration id: %s' % configId )

def _parseConfigIdList( configIdList ):
    listMatcher = _configNameListPattern.match( configIdList )
    if listMatcher:
        result = []
        if listMatcher.group( 1 ):
            for el in _configNamePattern.findall( listMatcher.group( 0 ) ):
                result.append( _parseConfigId( el[0] ) )
        return result
    else:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'ConfigID list regular expression matching failed for the string: "%s"', configIdList )
        raise Exception( 'Invalid configuration id list: %s' % configIdList )

def getid( criteriaString ):
    objectList = AdminConfig.getid( criteriaString )
    result = []
    for l in objectList.splitlines():
        result.append( ConfigObject( _parseConfigId( l ) ) )
    return result

def getid1( criteriaString ):
    objectList = AdminConfig.getid( criteriaString ).splitlines()
    if len( objectList ) == 0:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'No configuration object matched criteria %s', criteriaString )
        raise Exception( 'No configuration object matched criteria %s' % criteriaString )
    elif len( objectList ) > 1:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'More than one configuration object matched criteria %s', criteriaString )
        raise Exception( 'More than one configuration object matched criteria %s' % criteriaString )
    else:
        return ConfigObject( _parseConfigId( objectList[0] ) )

def listConfigObjects( type, scopeOrPattern = None ):
    v = None
    if scopeOrPattern:
        v = AdminConfig.list( type, str( scopeOrPattern ) )
    else:
        v = AdminConfig.list( type )
    result = []
    for l in v.splitlines():
        result.append( ConfigObject( _parseConfigId( l ) ) )
    return result

def attributes( obj ):
    if isinstance( obj, ConfigObject ):
        type = obj._type
    elif isinstance( obj, StringType ):
        type = obj
    else:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'unexpected argument type: %s', type( obj ) )
        raise ValueError( 'unexpected argument type: %s' % type( obj ) )
    typeInfo = getTypeInfo( type )
    result = [a for a in typeInfo.attributes.keys()]
    result.sort()
    return result

def hasChanges():
    return AdminConfig.hasChanges()

def parents( type ):
    parentsString = AdminConfig.parents( type )
    if not parentsString.startswith( 'WASX7351I' ):
        return parentsString.splitlines()
    else:
        return []

def reset():
    AdminConfig.reset()

def discard():
    reset()

def save():
    AdminConfig.save()

class ConfigId:
    def __init__( self, name, xmlPath, xmlDoc, xmlId ):
        self.name = name
        self.xmlPath = xmlPath
        self.xmlDoc = xmlDoc
        self.xmlId = xmlId
    def __eq__( self, other ):
        if type( other ) == type( self ):
            if str( self ) == str( other ):
                return 1
        return 0
    def __str__( self ):
        return "%s(%s|%s#%s)" % ( self.name, self.xmlPath, self.xmlDoc, self.xmlId )
    def __unicode__( self ):
        return unicode( self.__str__() )
    def __repr__( self ):
        return "%s(%s|%s#%s)" % ( self.name, self.xmlPath, self.xmlDoc, self.xmlId )

class TypeInfo:
    def __init__( self, name, attributes, parents, children, converter = None ):
        self.name = name
        self.attributes = attributes
        self.parents = parents
        self.children = children
        self.converter = converter

class AttributeInfo:
    def __init__( self, name, type, list, reference, enumValues, subTypes ):
        self.name = name
        self.type = type
        self.list = list
        self.reference = reference
        self.enumValues = enumValues
        self.subTypes = subTypes

    def __str__( self ):
        return '%s %s' % ( self.name, self.type )

    def __unicode__( self ):
        return unicode( self.__str__() )

    def __repr__( self ):
        return '%s %s' % ( self.name, self.type )

class ConfigObject:
    def __init__( self, _id ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'creating ConfigObject with id: %s', _id )
        self._id = _id
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'retrieving type information for ConfigObject %s', _id )
        self._type = getObjectType( _id )

    def __str__( self ):
        return str( self._id )

    def __unicode__( self ):
        return unicode( self.__str__() )

    def __repr__( self ):
        return repr( self._id )

    def __getitem__( self, item ):
        return self._getConfigAttribute( item )

    def __nonzero__( self ):
        return 1

    def __eq__( self, other ):
        if type( other ) == type( self ):
            if str( self ) == str( other ):
                return 1
        return 0

    def __getattr__( self, name ):
        if name == '__methods__':
            return {
                    'listConfigObjects':self.listConfigObjects,
                    'create':self.create,
                    'modify':self.modify,
                    'remove':self.remove
                    }
        elif name == '__members__':
            return _typeRegistry[self._type].attributes
        else:
            return self._getConfigAttribute( name )

    def _getConfigAttribute( self, name ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'retrieving attribute %s from ConfigObject %s', name, self )
        v = AdminConfig.showAttribute( str( self ), name )
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'retrieved attribute %s from ConfigObject %s as value of %s', name, self, v )
        return self._processAttributeValue( name, v )

    def _processAttributeValue( self, name, v ):
        ai = getTypeInfo( self._type ).attributes[name]
        ti = getTypeInfo( ai.type )
        cnv = ti.converter
        if v is None:
            return None
        if cnv:
            if ai.list:
                if v == '[]':
                    return []
                else:
                    return map( cnv.fromAdminConfig, split( v, ';' ) )
            else:
                return cnv.fromAdminConfig( v )
        else:
            if ai.list:
                return map( lambda e:ConfigObject( e ), _parseConfigIdList( v ) )
            else:
                return ConfigObject( _parseConfigId( v ) )

    def _processAttributeValueFromList( self, name, v ):
        ai = getTypeInfo( self._type ).attributes[name]
        ti = getTypeInfo( ai.type )
        cnv = ti.converter
        if v is None:
            return None
        if cnv:
            if ai.list:
                if v == '[]':
                    return []
                else:
                    return map( cnv.fromAdminConfig, split( v, ';' ) )
            else:
                # wsadmin prints empty strings as [] in AdminConfig.show()
                if v == '[]':
                    v = ''
                # wsadmin encloses strings containing spaces with double-quotes in AdminConfig.show()
                if len( v ) >= 2 and v[0] == '"' and v[-1] == '"':
                    v = v[1:-1]
                return cnv.fromAdminConfig( v )
        else:
            if ai.list:
                return map( lambda e:ConfigObject( e ), _parseConfigIdList( v ) )
            else:
                return ConfigObject( _parseConfigId( v ) )

    def getAllAttributes( self ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'retrieving all attributes ConfigObject %s', self )
        showResult = AdminConfig.show( str( self ) )
        attributes = {}
        for l in showResult.splitlines():
            ( name, value ) = l[1:-1].split( ' ', 1 )
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'about to process attribute %s with value "%s"', name, value )
            attributes[name] = self._processAttributeValueFromList( name, value )
        return attributes

    def __setattr__( self, name, value ):
        if name in [ '_id', '_type' ]:
            self.__dict__[name] = value
            return value
        else:
            return self._setConfigAttribute( name, value )

    def __setitem__( self, item, value ):
        return self._setConfigAttribute( item, value )

    def _setConfigAttribute( self, name, value ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'assigning value of %s to attribute %s of ConfigObject %s', value, name, self )
        self._modify( [(name, value)] )
        v = self._getConfigAttribute( name )
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'value of %s has been written to attribute %s of ConfigObject %s', v, name, self )
        return v

    def __delitem__( self, name ):
        AdminConfig.unsetAttributes( str( self ), [name] )
        return None

    def __delattr__( self, name ):
        AdminConfig.unsetAttributes( str( self ), [name] )
        return None

    def listConfigObjects( self, _type ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'listing objects of type %s in scope of %s', _type, self )
        result = []
        for l in AdminConfig.list( _type, str( self ) ).splitlines():
            result.append( ConfigObject( _parseConfigId( l ) ) )
        return result

    def create( self, _type, _propertyName = None, **_attributes ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'creating object of type %s in scope %s with attributes %s', _type, self, _attributes )
        createAttributes = []
        for ( k, v ) in _attributes.items():
            createAttributes.append( [k, v] )
        return self._create( _type, _propertyName, createAttributes )

    def _create( self, type, propertyName, attributes ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'creating object %s with attributes %s for property %s.%s', type, attributes, str( self ), propertyName )
        if propertyName:
            newConfigId = AdminConfig.create( type, str( self ), attributes, propertyName )
        else:
            newConfigId = AdminConfig.create( type, str( self ), attributes )
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'created %s', newConfigId )
        return ConfigObject( _parseConfigId( newConfigId ) )

    def modify( self, **_attributes ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'modifying object %s with attributes %s', self, _attributes )
        modifyAttributes = []
        for ( k, v ) in _attributes.items():
            modifyAttributes.append( [k, v] )
        return self._modify( modifyAttributes )

    def _modify( self, attributes ):
        if len( attributes ) > 0:
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'modifying object %s with attributes %s', self, attributes )
            emptyAttributes = []
            atomicAttributes = []
            listAttributes = []
            for ( name, value ) in attributes:
                if value is None:
                    emptyAttributes.append( name )
                else:
                    ai = getTypeInfo( self._type ).attributes[name]
                    ti = getTypeInfo( ai.type )
                    cnv = ti.converter
                    v = None
                    if ai.list:
                        if cnv:
                            v = join( map( cnv.toAdminConfig, value ), ';' )
                        else:
                            v = map( lambda e:str( e ), value )
                        listAttributes.append( [name, v] )
                    else:
                        if cnv:
                            v = cnv.toAdminConfig( value )
                        else:
                            v = str( value )
                        atomicAttributes.append( [name, v] )
            if len( emptyAttributes ) > 0:
                AdminConfig.unsetAttributes( str( self ), emptyAttributes )
            if len( atomicAttributes ) > 0:
                AdminConfig.modify( str( self ), atomicAttributes )
            for ( n, v ) in listAttributes:
                currentValue = self._getConfigAttribute( n )
                ai = getTypeInfo( self._type ).attributes[n]
                ti = getTypeInfo( ai.type )
                cnv = ti.converter
                if cnv:
                    currentValue = join( map( cnv.toAdminConfig, currentValue ), ';' )
                else:
                    currentValue = map( lambda e:str( e ), currentValue )
                if currentValue != v:
                    AdminConfig.modify( str( self ), [[n, []]] )
                    AdminConfig.modify( str( self ), [[n, v]] )
        return self

    def remove( self ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'removing object %s', self )
        AdminConfig.remove( str( self ) )
        return self

    def unset( self, _attributes ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'unsetting attributes %s of ConfigObject %s', _attributes, self )
        AdminConfig.unsetAttributes( str( self ), _attributes )
        return self

    def lookup1( self, _type, _criteria, _propertyName = None ):
        result = self.lookup( _type, _criteria, _propertyName )
        if len( result ) == 0:
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'No configuration object matched criteria %s', _criteria )
            raise Exception( 'No configuration object matched criteria %s' % _criteria )
        elif len( result ) > 1:
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'More than one configuration object matched criteria %s', _criteria )
            raise Exception( 'More than one configuration object matched criteria %s' % _criteria )
        return result[0]

    def lookup( self, _type, _criteria, _propertyName = None ):
        name = _criteria.get( 'name', None )
        if _propertyName:
            if name:
                candidates = [c for c in self._getConfigAttribute( _propertyName ) if c._id.name == name]
            else:
                candidates = self._getConfigAttribute( _propertyName )
        else:
            myName = None
            if getTypeInfo( self._type ).attributes.has_key( 'name' ):
                myName = self._getConfigAttribute( 'name' )
            allAncestors = self.listConfigObjects( _type )
            if self._type in parents( _type ):
                if myName and name:
                    indexedCandidates = getid( '/%s:%s/%s:%s/' % ( self._type, myName, _type, name ) )
                elif name:
                    indexedCandidates = getid( '/%s:%s/%s:%s/' % ( self._type, '', _type, name ) )
                elif myName:
                    indexedCandidates = getid( '/%s:%s/%s:%s/' % ( self._type, myName, _type, '' ) )
                else:
                    indexedCandidates = getid( '/%s:%s/%s:%s/' % ( self._type, '', _type, '' ) )
                candidates = [c for c in allAncestors if c in indexedCandidates]
            else:
                candidates = allAncestors
            # exclude grandchildren
            for parentType in parents( _type ):
                if parentType != self._type:
                    for child in self.listConfigObjects( parentType ):
                        for grandchild in child.listConfigObjects( _type ):
                            if logger.isEnabledFor( logging.DEBUG ):
                                logger.debug( 'grandchild %s of %s found', grandchild, self )
                            if grandchild in candidates:
                                candidates.remove( grandchild )
                                if logger.isEnabledFor( logging.DEBUG ):
                                    logger.debug( 'grandchild %s of %s removed from list of lookup candidates', grandchild, self )
        result = []
        for obj in candidates:
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'matching %s with %s', obj, _criteria )
            for ( k, v ) in _criteria.items():
                if obj[k] != v:
                    if logger.isEnabledFor( logging.DEBUG ):
                        logger.debug( 'object %s did not match the criteria, attribute %s != "%s"', obj, k, v )
                    break
            else:
                if logger.isEnabledFor( logging.DEBUG ):
                    logger.debug( 'object %s matched criteria %s', obj, _criteria )
                result.append( obj )
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'lookup for type %s, criteria %s, property %s returns %s', _type, _criteria, _propertyName, result )
        return result

    def assure( self, _type, _criteria, _propertyName = None, **_attributes ):
        result = self.lookup( _type, _criteria, _propertyName )
        if len( result ) == 0:
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'no object match criteria %s', _criteria )
            allAttributes = {}
            allAttributes.update( _attributes )
            allAttributes.update( _criteria )
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'new object with attributes %s will be created', allAttributes )
            return self._create( _type, _propertyName, [[x, y] for ( x, y ) in allAttributes.items() ] )
        elif len( result ) > 1:
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'More than one configuration object matched criteria %s', _criteria )
            raise Exception( 'More than one configuration object matched criteria %s' % _criteria )
        else:
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'object %s match criteria %s', result[0], _criteria )
            return result[0]._modify( [[x, y] for ( x, y ) in _attributes.items() ] )

def initializeTypeRegistry():
    if wdr.config._typeRegistryInitialized == 0:
        startTime = time.time()
        logger.info( 'full initialization of type registry' )
        for typeName in AdminConfig.types().splitlines():
            getTypeInfo( typeName )
        wdr.config._typeRegistryInitialized = 1
        logger.info( 'full initialization of type registry completed in %.2f seconds', ( time.time() - startTime ) )

_typeRegistry = {
                 'int': TypeInfo( 'int', {}, [], [], IntegerAttributeConverter() ),
                 'Integer': TypeInfo( 'Integer', {}, [], [], IntegerAttributeConverter() ),
                 'long': TypeInfo( 'long', {}, [], [], LongAttributeConverter() ),
                 'Long': TypeInfo( 'Long', {}, [], [], LongAttributeConverter() ),
                 'float': TypeInfo( 'float', {}, [], [], FloatAttributeConverter() ),
                 'Float': TypeInfo( 'Float', {}, [], [], FloatAttributeConverter() ),
                 'boolean':TypeInfo( 'boolean', {}, [], [], BooleanAttributeConverter() ),
                 'Boolean': TypeInfo( 'Boolean', {}, [], [], BooleanAttributeConverter() ),
                 'String': TypeInfo( 'String', {}, [], [], StringAttributeConverter() ),
                 'ENUM': TypeInfo( 'ENUM', {}, [], [], EnumAttributeConverter() )
                 }

