from string import split, join, upper
from types import StringType
import logging
import re
import time
import wdr

(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger('wdr.config')

_typeRegistryInitialized = 0


def _compileRegularExpressions():
    # expression matching websphere configuration object id
    # make sure you run unit tests after modifying it
    configNamePattern = re.compile(
        r'('
        # config object ids may contain whitespaces and are being quoted then
        r'(?:'
        r'"'
        r'(?P<qname>[^"\[\]]*)'
        r'\((?P<qxmlPath>.+?)\|(?P<qxmlDoc>.+?\.xml)'
        r'#(?P<qxmlId>[a-zA-Z_0-9]+?)\)'
        r'"'
        r')'
        #
        r'|'
        # config object ids without whitespaces are not being quoted
        r'(?:'
        r'(?P<name>[^ "\[\]]*)'
        r'\((?P<xmlPath>.+?)\|(?P<xmlDoc>.+?\.xml)'
        r'#(?P<xmlId>[a-zA-Z_0-9]+?)\)'
        r')'
        #
        r'|'
        r'(?:\*+)'
        #
        r')'
    )
    maskedAttributePattern = re.compile('\*+')
    # expression matching list of object ids
    # lists of config objects are being returned as whitespace-separated strings
    # surrounded by square brackets, for compatility with Jacl
    configNameListPattern = re.compile(r'^(?:"?\[.*\]"?)|(\*+)$')
    attributeTypePattern = re.compile('[, \(\)]+')
    return (
        configNamePattern, configNameListPattern, attributeTypePattern,
        maskedAttributePattern
    )

(
    _configNamePattern, _configNameListPattern, _attributeTypePattern,
    _maskedAttributePattern
) = _compileRegularExpressions()


class AttributeConverter:
    def __init__(self):
        pass

    def fromAdminConfig(self, value):
        raise NotImplementedError

    def toAdminConfig(self, value):
        raise NotImplementedError


class BooleanAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminConfig(self, value):
        if value:
            if value == 'true':
                return 1
            else:
                return 0
        return 0

    def toAdminConfig(self, value):
        if value:
            if isinstance(value, StringType):
                upperValue = upper(value)
                if upperValue in ('TRUE', 'T', 'YES', 'Y'):
                    return 'true'
            elif value == 1:
                return 'true'
        return 'false'


class IntegerAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminConfig(self, value):
        return int(value, 10)

    def toAdminConfig(self, value):
        return str(value)


class LongAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminConfig(self, value):
        return long(value, 10)

    def toAdminConfig(self, value):
        return str(value)


class FloatAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminConfig(self, value):
        return float(value)

    def toAdminConfig(self, value):
        return str(value)


class StringAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminConfig(self, value):
        return value

    def toAdminConfig(self, value):
        return value


class EnumAttributeConverter(AttributeConverter):
    def __init__(self):
        AttributeConverter.__init__(self)

    def fromAdminConfig(self, value):
        return value

    def toAdminConfig(self, value):
        return value


def parseAttributeType(attName, attType):
    attList = 0
    if attType[-1] == '*':
        attList = 1
        attType = attType[:-1]
    attReference = 0
    if attType[-1] == '@':
        attReference = 1
        attType = attType[:-1]
    attTypeAndOptions = _attributeTypePattern.split(attType)
    attTypeName = attTypeAndOptions[0]
    if attTypeName[-1] == '*':
        attList = 1
        attTypeName = attTypeName[:-1]
    attEnumValues = None
    attSubTypes = None
    if attTypeName == 'ENUM':
        if len(attTypeAndOptions) > 2:
            attEnumValues = attTypeAndOptions[1:-1]
        else:
            raise Exception('Enum values expected for attribute %s' % attName)
    elif len(attTypeAndOptions) > 2:
        attSubTypes = attTypeAndOptions[1:-1]
    return AttributeInfo(
        attName, attTypeName, attList, attReference, attEnumValues, attSubTypes
    )


def _pre7objectTypeRetriever(configId, configNameCache=[None]):
    if not configNameCache[0]:
        # a dirty hack for accessing non-public AdminConfig.nameCache member
        # hack is targeted for WAS pre-7
        # WAS 7 comes with AdminConfig.getObjectType which eliminates the need
        # for such hack
        logger.debug('accessing AdminConfig.nameCache field using reflection')
        configNameCache[0] = AdminConfig.__class__.getDeclaredField('nameCache')
        logger.debug(
            'setting AdminConfig.nameCache field to accessible via reflection'
        )
        configNameCache[0].setAccessible(1)
    return configNameCache[0].get(AdminConfig).getType(str(configId))


def _post7objectTypeRetriever(configId):
    return AdminConfig.getObjectType(str(configId))


def getObjectType(
    configId,
    objectTypeRetriever=[
        _post7objectTypeRetriever, _pre7objectTypeRetriever
    ]
):
    try:
        typeName = objectTypeRetriever[0](str(configId))
    except AttributeError, ae:
        if 'getObjectType' not in ae.args:
            raise
        logger.warning(
            'default method of retrieving object types has failed, '
            'falling back to reflection-based mechanism'
        )
        # from now on, the default type retriever will be the one using
        # reflection
        objectTypeRetriever[0] = objectTypeRetriever[1]
        typeName = getObjectType(configId)
    getTypeInfo(typeName)
    return typeName


def _isConfigId(cfgid):
    if cfgid:
        return _configNamePattern.match(cfgid) is not None
    else:
        return 0


def _isConfigIdList(cfgids):
    if cfgids:
        return _configNameListPattern.match(cfgids) is not None
    else:
        return 0


def _firstNonNone(*args):
    for v in args:
        if v is not None:
            return v
    return None


def getTypeInfo(typeName):
    if not _typeRegistry.has_key(typeName):
        logger.debug('introspecting type %s', typeName)
        attributes = {}
        for att in AdminConfig.attributes(typeName).splitlines():
            (attName, attType) = att.split(' ', 1)
            attributes[attName] = parseAttributeType(attName, attType)
        _typeRegistry[typeName] = TypeInfo(
            typeName, attributes, parents(typeName), []
        )
        for parent in parents(typeName):
            parentTypeInfo = getTypeInfo(parent)
            if typeName not in parentTypeInfo.children:
                parentTypeInfo.children.append(typeName)
    return _typeRegistry[typeName]


def configObject(configId):
    return ConfigObject(_parseConfigId(configId))


def configObjects(configIds):
    return map(lambda e: configObject(e), _parseConfigIdList(configIds))


def _parseConfigId(configId):
    mat = _configNamePattern.match(configId)
    if mat:
        name = _firstNonNone(mat.group('qname'), mat.group('name'))
        xmlPath = _firstNonNone(mat.group('qxmlPath'), mat.group('xmlPath'))
        xmlDoc = _firstNonNone(mat.group('qxmlDoc'), mat.group('xmlDoc'))
        xmlId = _firstNonNone(mat.group('qxmlId'), mat.group('xmlId'))
        return ConfigId(name, xmlPath, xmlDoc, xmlId)
    else:
        raise Exception('Invalid configuration id: %s' % configId)


def _parseConfigIdList(configIdList):
    listMatcher = _configNameListPattern.match(configIdList)
    if listMatcher:
        result = []
        if not _maskedAttributePattern.match(configIdList):
            for el in _configNamePattern.findall(listMatcher.group(0)):
                result.append(_parseConfigId(el[0]))
        return result
    else:
        raise Exception('Invalid configuration id list: %s' % configIdList)


def getid(criteriaString):
    objectList = AdminConfig.getid(criteriaString)
    result = []
    for l in objectList.splitlines():
        result.append(ConfigObject(_parseConfigId(l)))
    return result


def getid1(criteriaString):
    objectList = AdminConfig.getid(criteriaString).splitlines()
    if len(objectList) == 0:
        raise Exception(
            'No configuration object matched criteria %s' % criteriaString
        )
    elif len(objectList) > 1:
        raise Exception(
            'More than one configuration object matched criteria %s'
            % criteriaString
        )
    else:
        return ConfigObject(_parseConfigId(objectList[0]))


def listConfigObjects(type, scopeOrPattern=None):
    if scopeOrPattern:
        v = AdminConfig.list(type, str(scopeOrPattern))
    else:
        v = AdminConfig.list(type)
    result = []
    for l in v.splitlines():
        result.append(ConfigObject(_parseConfigId(l)))
    return result


def attributes(obj):
    if isinstance(obj, ConfigObject):
        typeName = obj._type
    elif isinstance(obj, StringType):
        typeName = obj
    else:
        raise ValueError('unexpected argument type: %s' % type(obj))
    typeInfo = getTypeInfo(typeName)
    result = [a for a in typeInfo.attributes.keys()]
    result.sort()
    return result


def hasChanges():
    return AdminConfig.hasChanges()


def parents(type):
    parentsString = AdminConfig.parents(type)
    if not parentsString.startswith('WASX7351I'):
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
    def __init__(self, name, xmlPath, xmlDoc, xmlId):
        self.name = name
        self.xmlPath = xmlPath
        self.xmlDoc = xmlDoc
        self.xmlId = xmlId

    def __eq__(self, other):
        if type(other) == type(self):
            if str(self) == str(other):
                return 1
        return 0

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return "%s(%s|%s#%s)" % (
            self.name, self.xmlPath, self.xmlDoc, self.xmlId
        )

    def __unicode__(self):
        return unicode(self.__str__())

    def __repr__(self):
        return "%s(%s|%s#%s)" % (
            self.name, self.xmlPath, self.xmlDoc, self.xmlId
        )


class TypeInfo:
    def __init__(self, name, attributes, parents, children, converter=None):
        self.name = name
        self.attributes = attributes
        self.parents = parents
        self.children = children
        self.converter = converter


class AttributeInfo:
    def __init__(self, name, type, list, reference, enumValues, subTypes):
        self.name = name
        self.type = type
        self.list = list
        self.reference = reference
        self.enumValues = enumValues
        self.subTypes = subTypes

    def __str__(self):
        return '%s %s' % (self.name, self.type)

    def __unicode__(self):
        return unicode(self.__str__())

    def __repr__(self):
        return '%s %s' % (self.name, self.type)


class AttributeValueCache:
    def __init__(self):
        self.cache = {}

    def getAttribute(self, configObject, attributeName):
        oid = str(configObject)
        objectCache = self.cache[oid] = self.cache.get(oid, {})
        if objectCache.has_key(attributeName):
            return objectCache[attributeName]
        result = configObject._getConfigAttribute(attributeName)
        objectCache[attributeName] = result
        return result

    def invalidate(self, configObject=None, attributeName=None):
        if configObject is None:
            self.cache.clear()
            return
        oid = str(configObject)
        if self.cache.has_key(oid):
            if attributeName is not None:
                if self.cache[oid].has_key(attributeName):
                    del self.cache[oid][attributeName]
            else:
                self.cache[oid].clear()


def getTemplates(typeName, templateId):
    typeTemplates = _templateRegistry.get(templateId)
    if typeTemplates is None:
        typeTemplates = {}
        for t in [
            configObject(t)
            for t in AdminConfig.listTemplates(typeName).splitlines()
        ]:
            for id in (
                t._id.name,
                '%s|%s#%s' % (t._id.xmlPath, t._id.xmlDoc, t._id.xmlId),
                str(t),
            ):
                templateList = typeTemplates.get(id, [])
                templateList.append(t)
                typeTemplates[id] = templateList
        _templateRegistry[typeName] = typeTemplates
    return typeTemplates.get(templateId)


def getTemplate(typeName, templateId):
    templateList = getTemplates(typeName, templateId)
    if templateList and len(templateList) == 1:
        return templateList[0]
    else:
        raise Exception(
            'Template <%s> not found or is not unique' % templateId
        )


class ConfigObject:
    def __init__(self, _id):
        self._id = _id
        self._type = getObjectType(_id)

    def __str__(self):
        return str(self._id)

    def __unicode__(self):
        return unicode(self.__str__())

    def __repr__(self):
        return repr(self._id)

    def __getitem__(self, item):
        return self._getConfigAttribute(item)

    def __nonzero__(self):
        return 1

    def __eq__(self, other):
        if type(other) == type(self):
            if str(self) == str(other):
                return 1
        return 0

    def __hash__(self):
        return hash(self._id)

    def __getattr__(self, name):
        if name == '__methods__':
            return {
                'listConfigObjects': self.listConfigObjects,
                'create': self.create,
                'modify': self.modify,
                'remove': self.remove
            }
        elif name == '__members__':
            return _typeRegistry[self._type].attributes
        else:
            return self._getConfigAttribute(name)

    def _getConfigAttribute(self, name):
        logger.debug('retrieving attribute %s from ConfigObject %s', name, self)
        v = AdminConfig.showAttribute(str(self), name)
        logger.debug(
            'retrieved attribute %s from ConfigObject %s as value of %s',
            name, self, v
        )
        return self._processAttributeValue(name, v)

    def _processAttributeValue(self, name, v):
        ai = getTypeInfo(self._type).attributes[name]
        ti = getTypeInfo(ai.type)
        cnv = ti.converter
        if v is None:
            return None
        if cnv:
            if ai.list:
                if v == '[]':
                    return []
                else:
                    return map(cnv.fromAdminConfig, split(v, ';'))
            else:
                return cnv.fromAdminConfig(v)
        else:
            if ai.list:
                return map(lambda e: ConfigObject(e), _parseConfigIdList(v))
            else:
                return ConfigObject(_parseConfigId(v))

    def _processAttributeValueFromList(self, name, v):
        ai = getTypeInfo(self._type).attributes[name]
        ti = getTypeInfo(ai.type)
        cnv = ti.converter
        if v is None:
            return None
        if cnv:
            if ai.list:
                if v == '[]':
                    return []
                else:
                    return map(cnv.fromAdminConfig, split(v, ';'))
            else:
                # wsadmin prints empty strings as [] in AdminConfig.show()
                if v == '[]':
                    v = ''
                # wsadmin encloses strings containing spaces with double-quotes
                # in AdminConfig.show()
                if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
                    v = v[1:-1]
                return cnv.fromAdminConfig(v)
        else:
            if ai.list:
                return map(lambda e: ConfigObject(e), _parseConfigIdList(v))
            else:
                return ConfigObject(_parseConfigId(v))

    def getAllAttributes(self):
        logger.debug('retrieving all attributes ConfigObject %s', self)
        showResult = AdminConfig.show(str(self))
        attributes = {}
        for l in showResult.splitlines():
            (name, value) = l[1:-1].split(' ', 1)
            logger.debug(
                'about to process attribute %s with value "%s"', name, value
            )
            attributes[name] = self._processAttributeValueFromList(name, value)
        return attributes

    def __setattr__(self, name, value):
        if name in ['_id', '_type']:
            self.__dict__[name] = value
            return value
        else:
            return self._setConfigAttribute(name, value)

    def __setitem__(self, item, value):
        return self._setConfigAttribute(item, value)

    def _setConfigAttribute(self, name, value):
        logger.debug(
            'assigning value of %s to attribute %s of ConfigObject %s',
            value, name, self
        )
        self._modify([(name, value)])
        v = self._getConfigAttribute(name)
        logger.debug(
            'value of %s has been written to attribute %s of ConfigObject %s',
            v, name, self
        )
        return v

    def __delitem__(self, name):
        AdminConfig.unsetAttributes(str(self), [name])
        return None

    def __delattr__(self, name):
        AdminConfig.unsetAttributes(str(self), [name])
        return None

    def listConfigObjects(self, _type):
        result = []
        for l in AdminConfig.list(_type, str(self)).splitlines():
            result.append(ConfigObject(_parseConfigId(l)))
        return result

    def create(self, _type, _propertyName=None, **_attributes):
        createAttributes = []
        for (k, v) in _attributes.items():
            createAttributes.append([k, v])
        return self._create(_type, _propertyName, createAttributes)

    def _create(self, type, propertyName, attributes, templateName=None):
        logger.debug(
            'creating object %s with attributes %s for property %s.%s',
            type, attributes, str(self), propertyName
        )
        if templateName:
            template = getTemplate(type, templateName)
        else:
            template = None
        if propertyName:
            if template:
                newConfigId = AdminConfig.createUsingTemplate(
                    type, str(self), attributes, propertyName, str(template)
                )
            else:
                newConfigId = AdminConfig.create(
                    type, str(self), attributes, propertyName
                )
        else:
            if template:
                newConfigId = AdminConfig.createUsingTemplate(
                    type, str(self), attributes, str(template)
                )
            else:
                newConfigId = AdminConfig.create(type, str(self), attributes)
        logger.debug('created %s', newConfigId)
        return ConfigObject(_parseConfigId(newConfigId))

    def modify(self, **_attributes):
        modifyAttributes = []
        for (k, v) in _attributes.items():
            modifyAttributes.append([k, v])
        return self._modify(modifyAttributes)

    def _modify(self, attributes):
        if len(attributes) > 0:
            logger.debug(
                'modifying object %s with attributes %s', self, attributes
            )
            emptyAttributes = []
            atomicAttributes = []
            listAttributes = []
            for (name, value) in attributes:
                if value is None:
                    emptyAttributes.append(name)
                else:
                    ai = getTypeInfo(self._type).attributes[name]
                    ti = getTypeInfo(ai.type)
                    cnv = ti.converter
                    if ai.list:
                        if cnv:
                            v = join(map(cnv.toAdminConfig, value), ';')
                        else:
                            v = map(lambda e: str(e), value)
                        listAttributes.append([name, v])
                    else:
                        if cnv:
                            v = cnv.toAdminConfig(value)
                        else:
                            v = str(value)
                        atomicAttributes.append([name, v])
            self.unset(emptyAttributes)
            self._modifyAtomic(atomicAttributes)
            self._modifyList(listAttributes)
        return self

    def _modifyAtomic(self, atomicAttributes):
        if len(atomicAttributes) > 0:
            AdminConfig.modify(str(self), atomicAttributes)

    def _modifyList(self, listAttributes):
        for (n, v) in listAttributes:
            currentValue = self._getConfigAttribute(n)
            ai = getTypeInfo(self._type).attributes[n]
            ti = getTypeInfo(ai.type)
            cnv = ti.converter
            if cnv:
                currentValue = join(
                    map(cnv.toAdminConfig, currentValue), ';'
                )
            else:
                currentValue = map(lambda e: str(e), currentValue)
            if currentValue != v:
                AdminConfig.modify(str(self), [[n, []]])
                AdminConfig.modify(str(self), [[n, v]])

    def remove(self):
        logger.debug('removing object %s', self)
        AdminConfig.remove(str(self))
        return self

    def unset(self, _attributes):
        if len(_attributes) > 0:
            logger.debug(
                'unsetting attributes %s of ConfigObject %s', _attributes, self
            )
            AdminConfig.unsetAttributes(str(self), _attributes)
        return self

    def lookup1(self, _type, _criteria, _propertyName=None):
        result = self.lookup(_type, _criteria, _propertyName)
        if len(result) == 0:
            raise Exception(
                'No configuration object matched criteria %s' % _criteria
            )
        elif len(result) > 1:
            raise Exception(
                'More than one configuration object matched criteria %s'
                % _criteria
            )
        return result[0]

    def lookup(self, _type, _criteria, _propertyName=None, attributeCache=None):
        attributeCache = attributeCache or AttributeValueCache()
        candidates = []
        candidates.extend(
            self._lookupCandidatesInProperty(
                _type, _criteria, _propertyName, attributeCache
            )
        )
        candidates.extend(
            self._lookupIndexedChildren(
                _type, _criteria, _propertyName, attributeCache
            )
        )
        candidates.extend(
            self._lookupNonIndexedChildren(
                _type, _criteria, _propertyName, attributeCache
            )
        )
        return self._filterCandidates(candidates, _criteria, attributeCache)

    def _lookupCandidatesInProperty(
        self, _type, _criteria, _propertyName=None, attributeCache=None
    ):
        name = _criteria.get('name', None)
        if _propertyName:
            if name:
                return [
                    c for c in attributeCache.getAttribute(self, _propertyName)
                    if c._type == _type and c._id.name == name
                ]
            else:
                return [
                    c for c in attributeCache.getAttribute(self, _propertyName)
                    if c._type == _type
                ]
        else:
            return []

    def _lookupIndexedChildren(
        self, _type, _criteria, _propertyName, attributeCache
    ):
        if _propertyName is None:
            name = _criteria.get('name', '')
            myName = ''
            if getTypeInfo(self._type).attributes.has_key('name'):
                myName = attributeCache.getAttribute(self, 'name')
            if self._type in parents(_type):
                indexedParents = getid('/%s:%s/' % (self._type, myName))
                indexedCandidates = getid(
                    '/%s:%s/%s:%s/'
                    % (self._type, myName, _type, name)
                )
                if len(indexedParents) == 1:
                    return indexedCandidates
                else:
                    return [
                        c for c in self.listConfigObjects(_type)
                        if c in indexedCandidates
                    ]
        return []

    def _lookupNonIndexedChildren(
        self, _type, _criteria, _propertyName, attributeCache
    ):
        if _propertyName is None:
            if self._type not in parents(_type):
                logger.warning(
                    'using suboptimal lookup of %s objects within %s',
                    _type, self._type
                )
                candidates = self.listConfigObjects(_type)
                # exclude grandchildren
                for parentType in parents(_type):
                    if parentType != self._type:
                        for child in self.listConfigObjects(parentType):
                            for grandchild in child.listConfigObjects(_type):
                                if grandchild in candidates:
                                    candidates.remove(grandchild)
                return candidates
        return []

    def _filterCandidates(self, candidates, criteria, attributeCache):
        result = []
        for obj in candidates:
            for (k, v) in criteria.items():
                if attributeCache.getAttribute(obj, k) != v:
                    break
            else:
                result.append(obj)
        return result

    def assure(self, _type, _criteria, _propertyName=None, **_attributes):
        result = self.lookup(_type, _criteria, _propertyName)
        if len(result) == 0:
            allAttributes = {}
            allAttributes.update(_attributes)
            allAttributes.update(_criteria)
            return self._create(
                _type, _propertyName,
                [[x, y] for (x, y) in allAttributes.items()]
            )
        elif len(result) > 1:
            raise Exception(
                'More than one configuration object matched criteria %s'
                % _criteria
            )
        else:
            return result[0]._modify([[x, y] for (x, y) in _attributes.items()])


def initializeTypeRegistry():
    if wdr.config._typeRegistryInitialized == 0:
        startTime = time.time()
        logger.info('full initialization of type registry')
        for typeName in AdminConfig.types().splitlines():
            getTypeInfo(typeName)
        wdr.config._typeRegistryInitialized = 1
        logger.info(
            'full initialization of type registry completed in %.2f seconds',
            (time.time() - startTime)
        )


_typeRegistry = {
    'int': TypeInfo('int', {}, [], [], IntegerAttributeConverter()),
    'Integer': TypeInfo('Integer', {}, [], [], IntegerAttributeConverter()),
    'long': TypeInfo('long', {}, [], [], LongAttributeConverter()),
    'Long': TypeInfo('Long', {}, [], [], LongAttributeConverter()),
    'float': TypeInfo('float', {}, [], [], FloatAttributeConverter()),
    'Float': TypeInfo('Float', {}, [], [], FloatAttributeConverter()),
    'boolean': TypeInfo('boolean', {}, [], [], BooleanAttributeConverter()),
    'Boolean': TypeInfo('Boolean', {}, [], [], BooleanAttributeConverter()),
    'String': TypeInfo('String', {}, [], [], StringAttributeConverter()),
    'ENUM': TypeInfo('ENUM', {}, [], [], EnumAttributeConverter())
}

_templateRegistry = {
}
