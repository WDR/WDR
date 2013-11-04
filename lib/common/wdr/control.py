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
import wdr

( AdminApp, AdminConfig, AdminControl, AdminTask, Help ) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger( 'wdrControl' )

def jmxmbean( objectName ):
    return JMXMBean( objectName )

def jmxmbeans( objectNames ):
    return map( lambda e:JMXMBean( e ), objectNames.splitlines() )

def mbean( objectName ):
    return MBean( objectName )

def mbeans( objectNames ):
    return map( lambda e:MBean( e ), objectNames.splitlines() )

class JMXMBeanAttribute:
    def __init__( self, mbean, info ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'creating JMXMBeanAtribute %s for JMXMBean %s', info.name, mbean._id )
        self.mbean = mbean
        self.info = info
    def getValue( self ):
        return AdminControl.getAttribute_jmx( self.mbean._objectName, self.info.name )
    def setValue( self, value ):
        AdminControl.setAttribute_jmx( self.mbean._objectName, self.info.name, value )
        return value

class JMXMBeanOperation:
    def __init__( self, mbean, info ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'creating JMXMBeanOperation %s for JMXMBean %s', info.name, mbean._id )
        self._mbean = mbean
        self._info = info
        self._signature = []
        for t in info.signature:
            self._signature.append( t.type )
    def __call__( self, *arguments ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'invoking JMXMBeanOperation %s for JMXMBean %s', self._info.name, self._mbean._id )
        return AdminControl.invoke_jmx( self._mbean._objectName, self._info.name, arguments, self._signature )

class JMXMBean:
    def __init__( self, _id ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'creating JMXMBean %s', _id )
        self._id = _id
        self._attributes = {}
        self._operations = {}
        self._objectName = AdminControl.makeObjectName( _id )
        mbeanInfo = AdminControl.getMBeanInfo_jmx( self._objectName )
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'retrieving list of attributes for JMXMBean %s', _id )
        for attr in mbeanInfo.attributes:
            self._attributes[attr.name] = JMXMBeanAttribute( self, attr )
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'retrieving list of operations for JMXMBean %s', _id )
        for opr in mbeanInfo.operations:
            if not self._operations.has_key( opr.name ):
                self._operations[opr.name] = OperationGroup( self, opr.name )
            group = self._operations[opr.name]
            group.addOperation( JMXMBeanOperation( self, opr ) )

    def __getattr__( self, name ):
        if self._attributes.has_key( name ):
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'retrieving attribute value %s for JMXMBean %s', name, self._id )
            return self._attributes[name].getValue()
        elif self._operations.has_key( name ):
            return self._operations[name]
        else:
            raise AttributeError, name

    def __setattr__( self, name, value ):
        if name in [ '_id', '_attributes', '_operations', '_objectName' ]:
            self.__dict__[name] = value
        elif self._attributes.has_key( name ):
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'changing attribute %s to value of %s for JMXMBean %s', name, value, self._id )
            return self._attributes[name].setValue( value )
        else:
            raise AttributeError, name

    def __str__( self ):
        return self._id

    def __unicode__( self ):
        return unicode( self._id )

    def __repr__( self ):
        return '%s("%s")' % ( self.__class__, self._id )

class MBeanAttribute:
    def __init__( self, mbean, info ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'creating MBeanAtribute %s for MBean %s', info.name, mbean._id )
        self.mbean = mbean
        self.info = info
    def getValue( self ):
        value = AdminControl.getAttribute( self.mbean._id, self.info.name )
        typeName = self.info.type
        if _typeRegistry.has_key( typeName ):
            converter = _typeRegistry[typeName]
            return converter.fromAdminControl( value )
        else:
            return value
    def setValue( self, value ):
        typeName = self.info.type
        if _typeRegistry.has_key( typeName ):
            converter = _typeRegistry[typeName]
            value = converter.toAdminControl( value )
        AdminControl.setAttribute( self.mbean._id, self.info.name, value )
        return value

class MBeanOperation:
    def __init__( self, mbean, info ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'creating MBeanOperation %s for MBean %s', info.name, mbean._id )
        self._mbean = mbean
        self._info = info
        self._signature = []
        for t in info.signature:
            self._signature.append( t.type )
    def __call__( self, *arguments ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'invoking MBeanOperation %s for MBean %s', self._info.name, self._mbean._id )
        return self._buildResult( AdminControl.invoke( self._mbean._id, self._info.name, self._buildStringArgument( arguments ) ) )
    def _buildResult( self, value ):
        returnTypeName = self._info.returnType
        if _typeRegistry.has_key( returnTypeName ):
            converter = _typeRegistry[returnTypeName]
            return converter.fromAdminControl( value )
        else:
            return value
    def _buildStringArgument( self, arguments ):
        if arguments:
            result = ''
            for a in arguments:
                result = '%s "%s"' % ( result, a )
            return result
        else:
            return ''

class OperationGroup:
    def __init__( self, mbean, name ):
        self._mbean = mbean
        self._operations = {}
        self._overloads = {}
        self._name = name
    def __call__( self, *arguments ):
        numberOfOperations = len( self._operations )
        numberOfOverloads = len( self._overloads.get( len( arguments ), 0 ) )
        # call may be ambiguous if the operation is not overloaded
        if numberOfOperations == 1:
            # if the operation isn't overloaded, then let's just proceed with the call
            # without even looking at arguments
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'matched non-overloaded operation %s for MBean %s', self._name, self._mbean._id )
            return apply( self._operations.values()[0], arguments )
        elif numberOfOverloads == 1:
            # if the operation is overloaded and number of parameters matches number of call arguments,
            # then we proceed with the call without checking argument types
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'based on argument number matched operation %s for MBean %s', self._name, self._mbean._id )
            return apply( self._overloads[len( arguments )][0], arguments )
        else:
            # otherwise the operation must be first looked up using it's signature: mbean.operationName[['int','int']]
            logger.error( 'could not match operation %s for MBean %s', self._name, self._mbean._id )
            raise Exception( 'Could not match operation %s for MBean %s' % ( self._name, self._mbean._id ) )
    def __getitem__( self, signature ):
        return self._operations[repr( tuple( signature ) )]
    def addOperation( self, operation ):
        signature = []
        for a in operation._info.signature:
            signature.append( a.type )
        self._operations[repr( tuple( signature ) )] = operation
        overloads = list( self._overloads.get( len( signature ), [] ) )
        overloads.append( operation )
        self._overloads[len( signature )] = tuple( overloads )

class MBean:
    def __init__( self, _id ):
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'creating MBean %s', _id )
        self._id = _id
        self._attributes = {}
        self._operations = {}
        mbeanInfo = AdminControl.getMBeanInfo_jmx( AdminControl.makeObjectName( _id ) )
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'retrieving list of attributes for MBean %s', _id )
        for attr in mbeanInfo.attributes:
            self._attributes[attr.name] = MBeanAttribute( self, attr )
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'retrieving list of operations for MBean %s', _id )
        for opr in mbeanInfo.operations:
            if not self._operations.has_key( opr.name ):
                self._operations[opr.name] = OperationGroup( self, opr.name )
            group = self._operations[opr.name]
            group.addOperation( MBeanOperation( self, opr ) )

    def __getattr__( self, name ):
        if self._attributes.has_key( name ):
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'retrieving attribute value %s for MBean %s', name, self._id )
            return self._attributes[name].getValue()
        elif self._operations.has_key( name ):
            return self._operations[name]
        else:
            raise AttributeError, name

    def __setattr__( self, name, value ):
        if name in [ '_id', '_attributes', '_operations' ]:
            self.__dict__[name] = value
        elif self._attributes.has_key( name ):
            if logger.isEnabledFor( logging.DEBUG ):
                logger.debug( 'changing attribute %s to value of %s for MBean %s', name, value, self._id )
            return self._attributes[name].setValue( value )
        else:
            raise AttributeError, name

    def __str__( self ):
        return self._id

    def __unicode__( self ):
        return unicode( self._id )

    def __repr__( self ):
        return '%s("%s")' % ( self.__class__, self._id )

def queryMBeans( **attributes ):
    """Queries given the query criteria, retrieves an array of matching MBeans.
    Example:
    print wdr.control.query( type = 'Server', node = 'wdrNode', name = 'wdrServer')"""
    queryString = 'WebSphere:*'
    for ( k, v ) in attributes.items():
        queryString += ',%s=%s' % ( k, v )
    result = []
    for name in AdminControl.queryNames( queryString ).splitlines():
        if name.strip() != '':
            result.append( MBean( name ) )
    return result

def getMBean( **attributes ):
    """Queries given the query criteria, retrieves single instance of MBean
    Example:
    print wdr.control.query( type = 'Server', node = 'wdrNode', name = 'wdrServer')"""
    queryString = 'WebSphere:*'
    for ( k, v ) in attributes.items():
        queryString += ',%s=%s' % ( k, v )
    result = AdminControl.queryNames( queryString ).splitlines()
    if len( result ) == 1:
        return MBean( result[0] )
    elif len( result ) == 0:
        return None
    else:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'More than one MBean found matching query %s', queryString )
        raise Exception( 'More than one MBean found matching query %s' % queryString )

def getMBean1( **attributes ):
    """Queries given the query criteria, retrieves single instance of MBean
    Example:
    print wdr.control.query( type = 'Server', node = 'wdrNode', name = 'wdrServer')"""
    queryString = 'WebSphere:*'
    for ( k, v ) in attributes.items():
        queryString += ',%s=%s' % ( k, v )
    result = AdminControl.queryNames( queryString ).splitlines()
    if len( result ) == 1:
        return MBean( result[0] )
    elif len( result ) == 0:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'No MBean found matching query %s', queryString )
        raise Exception( 'No MBean found matching query %s' % queryString )
    else:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'More than one MBean found matching query %s', queryString )
        raise Exception( 'More than one MBean found matching query %s' % queryString )

def queryJMXMBeans( **attributes ):
    """Queries given the query criteria, retrieves an array of matching JMXMBeans.
    Example:
    print wdr.control.query( type = 'Server', node = 'wdrNode', name = 'wdrServer')"""
    queryString = 'WebSphere:*'
    for ( k, v ) in attributes.items():
        queryString += ',%s=%s' % ( k, v )
    result = []
    for name in AdminControl.queryNames( queryString ).splitlines():
        if name.strip() != '':
            result.append( JMXMBean( name ) )
    return result

def getJMXMBean( **attributes ):
    """Queries given the query criteria, retrieves single instance of JMXMBean
    Example:
    print wdr.control.query( type = 'Server', node = 'wdrNode', name = 'wdrServer')"""
    queryString = 'WebSphere:*'
    for ( k, v ) in attributes.items():
        queryString += ',%s=%s' % ( k, v )
    result = AdminControl.queryNames( queryString ).splitlines()
    if len( result ) == 1:
        return JMXMBean( result[0] )
    elif len( result ) == 0:
        return None
    else:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'More than one JMXMBean found matching query %s', queryString )
        raise Exception( 'More than one JMXMBean found matching query %s' % queryString )

def getJMXMBean1( **attributes ):
    """Queries given the query criteria, retrieves single instance of JMXMBean
    Example:
    print wdr.control.query( type = 'Server', node = 'wdrNode', name = 'wdrServer')"""
    queryString = 'WebSphere:*'
    for ( k, v ) in attributes.items():
        queryString += ',%s=%s' % ( k, v )
    result = AdminControl.queryNames( queryString ).splitlines()
    if len( result ) == 1:
        return JMXMBean( result[0] )
    elif len( result ) == 0:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'No JMXMBean found matching query %s', queryString )
        raise Exception( 'No JMXMBean found matching query %s' % queryString )
    else:
        if logger.isEnabledFor( logging.DEBUG ):
            logger.debug( 'More than one JMXMBean found matching query %s', queryString )
        raise Exception( 'More than one JMXMBean found matching query %s' % queryString )

class AttributeConverter:
    def __init__( self ):
        pass
    def fromAdminControl( self, value ):
        raise NotImplementedError
    def toAdminControl( self, value ):
        raise NotImplementedError

class BooleanAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminControl( self, value ):
        if value:
            if value == 'true':
                return 1
            else:
                return 0
        return 0
    def toAdminControl( self, value ):
        if value:
            return 'true'
        else:
            return 'false'

class IntegerAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminControl( self, value ):
        return int( value, 10 )
    def toAdminControl( self, value ):
        return str( value )

class LongAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminControl( self, value ):
        return long( value, 10 )
    def toAdminControl( self, value ):
        return str( value )

class FloatAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminControl( self, value ):
        return float( value )
    def toAdminControl( self, value ):
        return str( value )

class StringAttributeConverter( AttributeConverter ):
    def __init__( self ):
        AttributeConverter.__init__( self )
    def fromAdminControl( self, value ):
        return value
    def toAdminControl( self, value ):
        return value

_typeRegistry = {
                 'int': IntegerAttributeConverter(),
                 'java.lang.Integer': IntegerAttributeConverter(),
                 'long': LongAttributeConverter(),
                 'java.lang.Long': LongAttributeConverter(),
                 'float': FloatAttributeConverter(),
                 'java.lang.Float': FloatAttributeConverter(),
                 'boolean': BooleanAttributeConverter(),
                 'java.lang.Boolean': BooleanAttributeConverter(),
                 'java.lang.String': StringAttributeConverter()
                 }

