import logging
import threading
import types
import wdr

import java.util
import javax.management

(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger('wdr.control')


def jmxmbean(objectName):
    return JMXMBean(objectName)


def jmxmbeans(objectNames):
    return map(lambda e: JMXMBean(e), objectNames.splitlines())


def mbean(objectName):
    return MBean(objectName)


def mbeans(objectNames):
    return map(lambda e: MBean(e), objectNames.splitlines())


class JMXMBeanAttribute:
    def __init__(self, mbean, info):
        self.mbean = mbean
        self.info = info

    def getValue(self):
        return AdminControl.getAttribute_jmx(
            self.mbean._objectName, self.info.name
        )

    def setValue(self, value):
        AdminControl.setAttribute_jmx(
            self.mbean._objectName, self.info.name, value
        )
        return value


class JMXMBeanOperation:
    def __init__(self, mbean, info):
        self._mbean = mbean
        self._info = info
        self._signature = []
        for t in info.signature:
            self._signature.append(t.type)

    def __call__(self, *arguments):
        logger.debug(
            'invoking JMXMBeanOperation %s for JMXMBean %s',
            self._info.name, self._mbean._id
        )
        return AdminControl.invoke_jmx(
            self._mbean._objectName, self._info.name, arguments,
            self._signature
        )


class JMXMBean:
    def __init__(self, _id):
        self._id = _id
        self._attributes = {}
        self._operations = {}
        self._objectName = AdminControl.makeObjectName(_id)
        mbeanInfo = AdminControl.getMBeanInfo_jmx(self._objectName)
        for attr in mbeanInfo.attributes:
            self._attributes[attr.name] = JMXMBeanAttribute(self, attr)
        for opr in mbeanInfo.operations:
            if not self._operations.has_key(opr.name):
                self._operations[opr.name] = OperationGroup(self, opr.name)
            group = self._operations[opr.name]
            group.addOperation(JMXMBeanOperation(self, opr))

    def __getattr__(self, name):
        if self._attributes.has_key(name):
            logger.debug(
                'retrieving attribute value %s for JMXMBean %s', name, self._id
            )
            return self._attributes[name].getValue()
        elif self._operations.has_key(name):
            return self._operations[name]
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ['_id', '_attributes', '_operations', '_objectName']:
            self.__dict__[name] = value
        elif self._attributes.has_key(name):
            logger.debug(
                'changing attribute %s value for JMXMBean %s', name, self._id
            )
            return self._attributes[name].setValue(value)
        else:
            raise AttributeError(name)

    def __str__(self):
        return self._id

    def __unicode__(self):
        return unicode(self._id)

    def __repr__(self):
        return '%s("%s")' % (self.__class__, self._id)

    def waitForNotification(
        self, typeOrTypes=None, propertiesOrPropertiesList=None, timeout=300.0
    ):
        return waitForNotification(
            self._id, typeOrTypes, propertiesOrPropertiesList, timeout
        )


class MBeanAttribute:
    def __init__(self, mbean, info):
        self.mbean = mbean
        self.info = info

    def getValue(self):
        value = AdminControl.getAttribute(self.mbean._id, self.info.name)
        typeName = self.info.type
        if _typeRegistry.has_key(typeName):
            converter = _typeRegistry[typeName]
            return converter.fromAdminControl(value)
        else:
            return value

    def setValue(self, value):
        typeName = self.info.type
        if _typeRegistry.has_key(typeName):
            converter = _typeRegistry[typeName]
            value = converter.toAdminControl(value)
        AdminControl.setAttribute(self.mbean._id, self.info.name, value)
        return value


class MBeanOperation:
    def __init__(self, mbean, info):
        self._mbean = mbean
        self._info = info
        self._signature = []
        for t in info.signature:
            self._signature.append(t.type)

    def __call__(self, *arguments):
        logger.debug('invoking MBeanOperation %s for MBean %s',
                     self._info.name, self._mbean._id)
        return self._buildResult(
            AdminControl.invoke(
                self._mbean._id, self._info.name,
                self._buildStringArgument(arguments)
            )
        )

    def _buildResult(self, value):
        returnTypeName = self._info.returnType
        if _typeRegistry.has_key(returnTypeName):
            converter = _typeRegistry[returnTypeName]
            return converter.fromAdminControl(value)
        else:
            return value

    def _buildStringArgument(self, arguments):
        if arguments:
            result = ''
            for a in arguments:
                result = '%s "%s"' % (result, a)
            return result
        else:
            return ''


class OperationGroup:
    def __init__(self, mbean, name):
        self._mbean = mbean
        self._operations = {}
        self._overloads = {}
        self._name = name

    def __call__(self, *arguments):
        numberOfOperations = len(self._operations)
        numberOfOverloads = len(self._overloads.get(len(arguments), 0))
        # call may be ambiguous if the operation is not overloaded
        if numberOfOperations == 1:
            # if the operation isn't overloaded, then let's just proceed with
            # the call without even looking at arguments
            return apply(self._operations.values()[0], arguments)
        elif numberOfOverloads == 1:
            # if the operation is overloaded and number of parameters matches
            # number of call arguments, then we proceed with the call without
            # checking argument types
            return apply(self._overloads[len(arguments)][0], arguments)
        else:
            # otherwise the operation must be first looked up using it's
            # signature:
            # mbean.operationName[['int','int']]
            logger.error(
                'could not match operation %s for MBean %s',
                self._name, self._mbean._id
            )
            raise Exception(
                'Could not match operation %s for MBean %s'
                % (self._name, self._mbean._id)
            )

    def __getitem__(self, signature):
        return self._operations[repr(tuple(signature))]

    def addOperation(self, operation):
        signature = []
        for a in operation._info.signature:
            signature.append(a.type)
        self._operations[repr(tuple(signature))] = operation
        overloads = list(self._overloads.get(len(signature), []))
        overloads.append(operation)
        self._overloads[len(signature)] = tuple(overloads)


class MBean:
    def __init__(self, _id):
        self._id = _id
        self._attributes = {}
        self._operations = {}
        mbeanInfo = AdminControl.getMBeanInfo_jmx(
            AdminControl.makeObjectName(_id)
        )
        for attr in mbeanInfo.attributes:
            self._attributes[attr.name] = MBeanAttribute(self, attr)
        for opr in mbeanInfo.operations:
            if not self._operations.has_key(opr.name):
                self._operations[opr.name] = OperationGroup(self, opr.name)
            group = self._operations[opr.name]
            group.addOperation(MBeanOperation(self, opr))

    def __getattr__(self, name):
        if self._attributes.has_key(name):
            logger.debug(
                'retrieving attribute value %s for MBean %s', name, self._id
            )
            return self._attributes[name].getValue()
        elif self._operations.has_key(name):
            return self._operations[name]
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ['_id', '_attributes', '_operations']:
            self.__dict__[name] = value
        elif self._attributes.has_key(name):
            logger.debug(
                'changing attribute %s value for MBean %s', name, self._id
            )
            return self._attributes[name].setValue(value)
        else:
            raise AttributeError(name)

    def __str__(self):
        return self._id

    def __unicode__(self):
        return unicode(self._id)

    def __repr__(self):
        return '%s("%s")' % (self.__class__, self._id)

    def waitForNotification(
        self, typeOrTypes=None, propertiesOrPropertiesList=None, timeout=300.0
    ):
        return waitForNotification(
            self._id, typeOrTypes, propertiesOrPropertiesList, timeout
        )

def getFirstMatchingMBean( domain='WebSphere', **attributes ):
    """Find an MBean using the provided template. Returns the first matching
    MBean, or 'None' if no matches are found.
    Example:
    print wdr.control.getFirstMatchingMBean(
        type='Application',
        name='applicationName'
        )"""
    template = '%s:*' % domain
    for ( k, v ) in attributes.items():
        template += ',%s=%s' % ( k, v )
    result = AdminControl.completeObjectName(template)
    if result:
        return MBean(result)
    else:
        return None

def queryMBeans(domain='WebSphere', **attributes):
    """Queries given the query criteria, retrieves an array of matching MBeans.
    Example:
    print wdr.control.query(type='Server', node='wdrNode', name='wdrServer')"""
    queryString = '%s:*' % domain
    for (k, v) in attributes.items():
        queryString += ',%s=%s' % (k, v)
    result = []
    for name in AdminControl.queryNames(queryString).splitlines():
        if name.strip() != '':
            result.append(MBean(name))
    return result


def getMBean(domain='WebSphere', **attributes):
    """Queries given the query criteria, retrieves single instance of MBean
    Example:
    print wdr.control.query(type='Server', node='wdrNode', name='wdrServer')"""
    queryString = '%s:*' % domain
    for (k, v) in attributes.items():
        queryString += ',%s=%s' % (k, v)
    result = AdminControl.queryNames(queryString).splitlines()
    if len(result) == 1:
        return MBean(result[0])
    elif len(result) == 0:
        return None
    else:
        raise Exception(
            'More than one MBean found matching query %s' % queryString
        )


def getMBean1(domain='WebSphere', **attributes):
    """Queries given the query criteria, retrieves single instance of MBean
    Example:
    print wdr.control.query(type='Server', node='wdrNode', name='wdrServer')"""
    queryString = '%s:*' % domain
    for (k, v) in attributes.items():
        queryString += ',%s=%s' % (k, v)
    result = AdminControl.queryNames(queryString).splitlines()
    if len(result) == 1:
        return MBean(result[0])
    elif len(result) == 0:
        raise Exception('No MBean found matching query %s' % queryString)
    else:
        raise Exception(
            'More than one MBean found matching query %s' % queryString
        )


def queryJMXMBeans(domain='WebSphere', **attributes):
    """Queries given the query criteria, retrieves an array of matching
    JMXMBeans.
    Example:
    print wdr.control.query(type='Server', node='wdrNode', name='wdrServer')"""
    queryString = '%s:*' % domain
    for (k, v) in attributes.items():
        queryString += ',%s=%s' % (k, v)
    result = []
    for name in AdminControl.queryNames(queryString).splitlines():
        if name.strip() != '':
            result.append(JMXMBean(name))
    return result


def getJMXMBean(domain='WebSphere', **attributes):
    """Queries given the query criteria, retrieves single instance of JMXMBean
    Example:
    print wdr.control.query(type='Server', node='wdrNode', name='wdrServer')"""
    queryString = '%s:*' % domain
    for (k, v) in attributes.items():
        queryString += ',%s=%s' % (k, v)
    result = AdminControl.queryNames(queryString).splitlines()
    if len(result) == 1:
        return JMXMBean(result[0])
    elif len(result) == 0:
        return None
    else:
        raise Exception(
            'More than one JMXMBean found matching query %s' % queryString
        )


def getJMXMBean1(domain='WebSphere', **attributes):
    """Queries given the query criteria, retrieves single instance of JMXMBean
    Example:
    print wdr.control.query(type='Server', node='wdrNode', name='wdrServer')"""
    queryString = '%s:*' % domain
    for (k, v) in attributes.items():
        queryString += ',%s=%s' % (k, v)
    result = AdminControl.queryNames(queryString).splitlines()
    if len(result) == 1:
        return JMXMBean(result[0])
    elif len(result) == 0:
        raise Exception('No JMXMBean found matching query %s' % queryString)
    else:
        raise Exception(
            'More than one JMXMBean found matching query %s' % queryString
        )


class AttributeConverter:
    def __init__(self):
        pass

    def fromAdminControl(self, value):
        raise NotImplementedError

    def toAdminControl(self, value):
        raise NotImplementedError


class BooleanAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminControl(self, value):
        if value:
            if value == 'true':
                return 1
            else:
                return 0
        return 0

    def toAdminControl(self, value):
        if value:
            return 'true'
        else:
            return 'false'


class IntegerAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminControl(self, value):
        return int(value, 10)

    def toAdminControl(self, value):
        return str(value)


class LongAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminControl(self, value):
        return long(value, 10)

    def toAdminControl(self, value):
        return str(value)


class FloatAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminControl(self, value):
        return float(value)

    def toAdminControl(self, value):
        return str(value)


class StringAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminControl(self, value):
        return value

    def toAdminControl(self, value):
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


class BaseLocalNotificationFilter(javax.management.NotificationFilter):
    def __init__(self):
        pass

    def getNotificationFilterSupport(self):
        return javax.management.NotificationFilterSupport()


class LocalNotificationFilter(BaseLocalNotificationFilter):
    def __init__(self, typeOrTypes, propertiesOrPropertiesList):
        BaseLocalNotificationFilter.__init__(self)
        if typeOrTypes is None:
            self.types = None
        elif isinstance(typeOrTypes, types.ListType):
            if len(typeOrTypes):
                self.types = tuple(typeOrTypes)
            else:
                self.types = None
        elif isinstance(typeOrTypes, types.TupleType):
            if len(typeOrTypes):
                self.types = typeOrTypes
            else:
                self.types = None
        else:
            self.types = (typeOrTypes,)
        if propertiesOrPropertiesList is None:
            self.properties = None
        elif isinstance(propertiesOrPropertiesList, types.ListType):
            self.properties = tuple(propertiesOrPropertiesList)
        elif isinstance(propertiesOrPropertiesList, types.TupleType):
            self.properties = propertiesOrPropertiesList
        else:
            self.properties = (propertiesOrPropertiesList,)

    def isNotificationEnabled(self, notification):
        matched = 1
        matched &= (
            (self.types is None)
            or
            (str(notification.type) in self.types)
        )
        matched &= (
            (self.properties is None)
            or
            (notification.userData is None)
            or
            (self.userDataMatchesProperties(notification.userData))
        )
        return matched

    def userDataMatchesProperties(self, userData):
        if java.util.Map.isAssignableFrom(userData.__class__):
            transformedUserData = {}
            for e in userData.entrySet():
                transformedUserData[str(e.key)] = str(e.value)
            return transformedUserData in self.properties
        else:
            return 0

    def getNotificationFilterSupport(self):
        if self.types is not None:
            result = (
                BaseLocalNotificationFilter.getNotificationFilterSupport(self)
            )
            for t in self.types:
                result.enableType(t)
        else:
            result = None
        return result


class NotificationHandler(javax.management.NotificationListener):
    def __init__(self, notificationFilter):
        self.condition = threading.Condition()
        self.notificationFilter = notificationFilter
        self._notifications = []

    def register(self, mbean, handback=None):
        if isinstance(mbean, MBean):
            objectName = mbean._id
        elif isinstance(mbean, MBean):
            objectName = mbean._id
        else:
            objectName = mbean
        if not isinstance(objectName, javax.management.ObjectName):
            objectName = AdminControl.makeObjectName(objectName)
        AdminControl.adminClient.addNotificationListener(
            objectName, self,
            self.notificationFilter.getNotificationFilterSupport(), handback
        )

    def remove(self, mbean):
        if isinstance(mbean, MBean):
            objectName = mbean._id
        elif isinstance(mbean, MBean):
            objectName = mbean._id
        else:
            objectName = mbean
        if not isinstance(objectName, javax.management.ObjectName):
            objectName = AdminControl.makeObjectName(objectName)
        AdminControl.adminClient.removeNotificationListener(objectName, self)

    def waitForNotification(self, timeout=0):
        result = None
        self.condition.acquire()
        try:
            if self._notifications:
                result = self._notifications.pop(0)
            else:
                self.condition.wait(timeout)
                if self._notifications:
                    result = self._notifications.pop(0)
        finally:
            self.condition.release()
        return result

    def handleNotification(self, notification, handback):
        logger.debug(
            'received %s with userData %s', notification, notification.userData
        )
        self.condition.acquire()
        try:
            if (
                self.notificationFilter is None
                or
                self.notificationFilter.isNotificationEnabled(notification)
            ):
                self._notifications.append(notification)
                self.condition.notify()
                self.onNotification(notification, handback)
                logger.debug(
                    'returning notification %s with userData %s',
                    notification, notification.userData
                )
            else:
                logger.debug(
                    'ignoring notification %s with userData %s',
                    notification, notification.userData
                )
        finally:
            self.condition.release()

    def onNotification(self, notification, handback):
        pass


def waitForNotification(
    mbean, typeOrTypes=None, propertiesOrPropertiesList=None, timeout=300.0
):
    handler = NotificationHandler(
        LocalNotificationFilter(typeOrTypes, propertiesOrPropertiesList)
    )
    handler.register(mbean)
    try:
        result = handler.waitForNotification(timeout)
    finally:
        handler.remove(mbean)
    return result
