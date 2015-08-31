from types import DictType
from types import ListType
import com.ibm.ws.scripting
import logging
import os
import re
import sys
import wdr.app
import wdr.config
import wdr.task

(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger('wdr.manifest')

_genericPattern = re.compile(r'^(?P<tabs>\t*).*$')
_commentPattern = re.compile(r'^(?:\s*#\.*)|(?:\s*)$')
_directivePattern = re.compile(
    r'^(?P<tabs>\t*)'
    r'@'
    r'\s*'
    r'(?P<name>[A-Za-z][a-zA-Z0-9_]*)'
    r'(?P<values>(?:\s*(?P<value>.+?))*)?'
    r'\s*$')
_typePattern = re.compile(
    r'^(?P<tabs>\t*)'
    r'(?:(?P<operation>[!?+])\s*)?'
    r'\s*'
    r'(?P<type>[A-Za-z][a-zA-Z0-9_]*)'
    r'\s*'
    r'(?P<linkage>[&#][a-zA-Z0-9_]+)?'
    r'\s*$')
_keyPattern = re.compile(
    r'^(?P<tabs>\t*)'
    r'\*'
    r'(?P<name>[A-Za-z][a-zA-Z0-9_]*)'
    r'\s*'
    r'(?P<value>.+?)?'
    r'\s*$')
_attPattern = re.compile(
    r'^(?P<tabs>\t*)'
    r'-'
    r'(?P<name>[A-Za-z][a-zA-Z0-9_]*)'
    r'\s*'
    r'(?P<value>.+?)?'
    r'\s*$')
_variablePattern = re.compile(
    r'\$\['
    r'\s*'
    r'(?P<var>[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
    r'(?:'
    + (
        r'\s*'
        r'\|'
        r'\s*'
        r'(?P<filter>[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)'
    ) +
    r')?'
    r'\s*'
    r'\]')
_appNamePattern = re.compile(
    r'^'
    r'(?:(?:"(?P<qname>[^"]+)")|(?P<name>\S+))'
    r'\s+'
    r'(?:(?:"(?P<qpath>[^"]+)")|(?P<path>.+?))'
    r'\s*$')
_appOptionPattern = re.compile(
    r'^(?P<tabs>\t)'
    r'(?P<name>\*?[a-zA-Z0-9_\.]+)'
    r'\s*'
    r'(?P<value>.+?)?'
    r'\s*$')
_appOptionValuePattern = re.compile(r'^(?P<tabs>\t\t)(?P<value>.+?)\s*$')
WDR_CHECKSUM_DESCRIPTION = (
    'Checksum of deployed EAR file and application manifest'
)


def _defaultFilter(value):
    if value is None:
        return ''
    else:
        return str(value)


def _lookupVariable(expression, filterExpression, variables):
    value = None
    context = variables
    try:
        for seg in expression.split('.'):
            value = context[seg]
            if isinstance(value, DictType):
                context = value
    except KeyError:
        raise KeyError(expression)
    if callable(value):
        value = value(expression, variables)
    filter = _defaultFilter
    if filterExpression is not None:
        context = variables
        try:
            for seg in filterExpression.split('.'):
                filter = context[seg]
                if isinstance(filter, DictType):
                    context = filter
        except KeyError:
            raise KeyError(filterExpression)
    return filter(value)


def substituteVariables(value, variables):
    return re.sub(
        _variablePattern,
        (
            lambda k, v=variables:
            _lookupVariable(k.group('var'), k.group('filter'), v)
        ),
        value
    )


class Operations:
    names = {
        '+': 'assure',
        '?': 'customize',
        '!': 'remove',
    }
    assure, customize, remove = names.keys()


class ManifestConfigObject:
    def __init__(self, type, filename=None, linenumber=0):
        self.type = type
        self.operation = Operations.assure
        self.filename = filename
        self.linenumber = linenumber
        self.children = []
        self.keys = {}
        self.attributes = {}
        self.anchor = None
        self.reference = None
        self._orderedAttributeNames = []

    def isEmpty(self):
        return (
            len(self.children) == 0
            and
            len(self.keys) == 0
            and
            len(self.attributes) == 0
        )

    def __str__(self):
        return self._toString(0)

    def __unicode__(self):
        return unicode(self._toString(0))

    def getSourceLocation(self):
        if self.filename and self.linenumber:
            return '%s(%d)' % (self.filename, self.linenumber)
        else:
            return '(unknown source)'

    def _toString(self, indent):
        result = ''
        opcode = ''
        if self.operation != Operations.assure:
            opcode = self.operation
        if self.anchor:
            result += (
                "%s%s%s #%s\n"
                %
                ("\t" * indent, opcode, self.type, self.anchor)
            )
        elif self.reference:
            result += (
                "%s%s%s &%s\n"
                %
                ("\t" * indent, opcode, self.type, self.reference)
            )
        else:
            result += (
                "%s%s%s\n"
                %
                ("\t" * indent, opcode, self.type)
            )
        for (k, v) in self.keys.items():
            result += "%s*%s %s\n" % ("\t" * (indent + 1), k, v)
        for k in self._orderedAttributeNames:
            v = self.attributes[k]
            if isinstance(v, ListType):
                result += "%s-%s\n" % ("\t" * (indent + 1), k)
                for c in v:
                    result += c._toString(indent + 2)
            elif isinstance(v, ManifestConfigObject):
                result += v._toString(indent + 1)
            else:
                result += "%s-%s %s\n" % ("\t" * (indent + 1), k, v)
        for c in self.children:
            result += c._toString(indent + 1)
        return result

    def mapOperation(self, opcode):
        if opcode is None:
            return Operations.assure
        if not Operations.names.has_key(opcode):
            raise Exception(
                '[%s] Invalid operation code: "%s"'
                % (self.getSourceLocation(), opcode)
            )
        return opcode

    def apply(self, anchors, parentObject, parentAttribute, attributeCache):
        typeName = self.type
        logger.debug(
            'importing object type %s as child of object %s and property %s',
            typeName, parentObject, parentAttribute
        )
        if parentObject:
            self._applyWithParentContext(
                anchors, parentObject, parentAttribute, attributeCache
            )
        else:
            self._applyWithoutParentContext(
                anchors, parentObject, parentAttribute, attributeCache
            )

    def _filterMatching(self, candidateList, attributeCache):
        matchingList = []
        for o in candidateList:
            if o._type == self.type:
                for (k, v) in self.keys.items():
                    if attributeCache.getAttribute(o, k) != v:
                        break
                else:
                    matchingList.append(o)
        return matchingList

    def _create(self, parentObject, parentAttribute, attributeCache):
        typeName = self.type
        typeInfo = wdr.config.getTypeInfo(typeName)
        simpleAttributes = []
        for (propName, propValue) in self.keys.items():
            if typeInfo.attributes.has_key(propName):
                if wdr.config.getTypeInfo(
                    typeInfo.attributes[propName].type
                ).converter:
                    simpleAttributes.append([propName, propValue])
        for propName in self._orderedAttributeNames:
            propValue = self.attributes[propName]
            if typeInfo.attributes.has_key(propName):
                if wdr.config.getTypeInfo(
                    typeInfo.attributes[propName].type
                ).converter:
                    simpleAttributes.append([propName, propValue])
            else:
                raise Exception(
                    '[%s] Invalid attribute %s specified for object %s(%s)'
                    % (
                        self.getSourceLocation(), propName, typeName, self.keys
                    )
                )
        result = parentObject._create(
            typeName, parentAttribute, simpleAttributes
        )
        if parentAttribute is not None:
            attributeCache.invalidate(parentObject, parentAttribute)
        return result

    def _remove(self, configObject, anchors, attributeCache):
        if self.children or self.attributes:
            raise Exception(
                '[%s] Objects being removed '
                'must not have attributes nor children'
                % self.getSourceLocation()
            )
        if self.reference:
            raise Exception(
                '[%s] Remove not implemented yet' % self.getSourceLocation()
            )
        else:
            configObject.remove()

    def _setAnchor(self, anchors, configObject):
        if self.anchor:
            if anchors.has_key(self.anchor):
                raise Exception(
                    '[%s] Duplicate anchor: %s'
                    % (self.getSourceLocation(), self.anchor)
                )
            else:
                logger.debug(
                    'setting anchor %s to %s', self.anchor, configObject
                )
                anchors[self.anchor] = configObject

    def _updateSimpleAttributes(self, configObject, attributeCache):
        typeName = self.type
        typeInfo = wdr.config.getTypeInfo(typeName)
        for propName in self._orderedAttributeNames:
            propValue = self.attributes[propName]
            if typeInfo.attributes.has_key(propName):
                attributeInfo = typeInfo.attributes[propName]
                attributeTypeInfo = wdr.config.getTypeInfo(attributeInfo.type)
                if attributeTypeInfo.converter:
                    if attributeInfo.list:
                        if propValue:
                            newPropValue = propValue.split(';')
                        else:
                            newPropValue = propValue
                    else:
                        newPropValue = propValue
                    try:
                        configObject._modify([[propName, newPropValue]])
                        attributeCache.invalidate(configObject, propName)
                    except com.ibm.ws.scripting.ScriptingException, ex:
                        msg = '' + ex.message
                        if msg.find('ADMG0014E') != -1:
                            if (
                                configObject._getConfigAttribute(propName)
                                !=
                                newPropValue
                            ):
                                logger.warning(
                                    '[%s] read-only attribute %s.%s'
                                    ' could not be modified',
                                    self.getSourceLocation(), typeName,
                                    propName
                                )
                        else:
                            raise
            else:
                raise Exception(
                    '[%s] Invalid attribute %s specified for object %s(%s)'
                    % (
                        self.getSourceLocation(), propName, typeName, self.keys
                    )
                )

    def _updateKeys(self, configObject, attributeCache):
        typeName = self.type
        typeInfo = wdr.config.getTypeInfo(typeName)
        for (propName, propValue) in self.keys.items():
            if typeInfo.attributes.has_key(propName):
                attributeInfo = typeInfo.attributes[propName]
                attributeTypeInfo = wdr.config.getTypeInfo(attributeInfo.type)
                if attributeTypeInfo.converter:
                    try:
                        if attributeInfo.list:
                            configObject._modify(
                                [[propName, propValue.split(';')]]
                            )
                        else:
                            configObject._modify([[propName, propValue]])
                        attributeCache.invalidate(configObject, propName)
                    except com.ibm.ws.scripting.ScriptingException, ex:
                        msg = '' + ex.message
                        if msg.find('ADMG0014E') != -1:
                            logger.warning(
                                '[%s] read-only attribute %s.%s'
                                ' could not be modified',
                                self.getSourceLocation(), typeName, propName
                            )
                        else:
                            raise

    def _updateComplexAttributes(self, configObject, anchors, attributeCache):
        typeName = self.type
        typeInfo = wdr.config.getTypeInfo(typeName)
        for propName in self._orderedAttributeNames:
            propValue = self.attributes[propName]
            if typeInfo.attributes.has_key(propName):
                attributeInfo = typeInfo.attributes[propName]
                attributeTypeInfo = wdr.config.getTypeInfo(attributeInfo.type)
                if not attributeTypeInfo.converter:
                    for mo in propValue:
                        mo.apply(
                            anchors, configObject, propName, attributeCache
                        )
            else:
                raise Exception(
                    '[%s] Invalid attribute %s specified for object %s(%s)'
                    % (self.getSourceLocation(), propName, typeName, self.keys)
                )

    def _updateChildren(self, configObject, anchors, attributeCache):
        for mo in self.children:
            mo.apply(anchors, configObject, None, attributeCache)

    def _updateRefOrRefList(
        self, anchors, parentObject, parentAttribute, attributeCache
    ):
        if not self.isEmpty():
            raise Exception(
                '[%s] Objects being assigned to'
                ' reference-attributes must not contain'
                ' keys/attributes/children'
                % self.getSourceLocation()
            )
        if not self.reference:
            raise Exception(
                '[%s] Objects being assigned to'
                ' reference-attributes must be references to'
                ' other objects'
                % self.getSourceLocation()
            )
        if not anchors.has_key(self.reference):
            raise Exception(
                '[%s] Unresolved reference: %s'
                % (self.getSourceLocation(), self.reference)
            )
        parentTypeName = parentObject._type
        parentTypeInfo = wdr.config.getTypeInfo(parentTypeName)
        parentAttributeInfo = parentTypeInfo.attributes[parentAttribute]
        if parentAttributeInfo.list:
            anchor = anchors[self.reference]
            referenceList = parentObject[parentAttribute]
            if self.operation in (Operations.assure, Operations.customize):
                referenceList.append(anchor)
            elif self.operation == Operations.remove:
                if anchor in referenceList:
                    referenceList.remove(anchor)
            parentObject[parentAttribute] = referenceList
            attributeCache.invalidate(parentObject, parentAttribute)
        else:
            if self.operation in (Operations.assure, Operations.customize):
                anchor = anchors[self.reference]
                parentObject[parentAttribute] = anchor
            elif self.operation == Operations.remove:
                parentObject[parentAttribute] = None
            attributeCache.invalidate(parentObject, parentAttribute)

    def _applyToChild(
        self, anchors, parentObject, parentAttribute, attributeCache
    ):
        typeName = self.type
        if parentAttribute is None:
            matchingObjects = self._filterMatching(
                parentObject.lookup(typeName, {}), attributeCache
            )
        else:
            matchingObjects = self._filterMatching(
                attributeCache.getAttribute(parentObject, parentAttribute),
                attributeCache
            )
        if (
            len(matchingObjects) == 0
            or
            (
                len(matchingObjects) == 1 and matchingObjects[0] is None
            )
        ):
            if self.operation == Operations.assure:
                configObject = self._create(
                    parentObject, parentAttribute, attributeCache
                )
                self._setAnchor(anchors, configObject)
                self._updateComplexAttributes(
                    configObject, anchors, attributeCache
                )
                self._updateChildren(configObject, anchors, attributeCache)
            elif self.operation == Operations.remove:
                pass
            elif self.operation == Operations.customize:
                pass
        elif len(matchingObjects) == 1:
            configObject = matchingObjects[0]
            if self.operation in (Operations.assure, Operations.customize):
                self._setAnchor(anchors, configObject)
                self._updateKeys(configObject, attributeCache)
                self._updateSimpleAttributes(configObject, attributeCache)
                self._updateComplexAttributes(
                    configObject, anchors, attributeCache
                )
                self._updateChildren(configObject, anchors, attributeCache)
            elif self.operation == Operations.remove:
                self._remove(configObject, anchors, attributeCache)
        else:
            raise Exception(
                '[%s] Multiple %s objects matched criteria'
                % (self.getSourceLocation(), typeName)
            )

    def _applyWithParentContext(
        self, anchors, parentObject, parentAttribute, attributeCache
    ):
        # knowing the parent, we can either create or modify the object
        parentTypeName = parentObject._type
        parentTypeInfo = wdr.config.getTypeInfo(parentTypeName)
        if parentAttribute:
            parentAttributeInfo = parentTypeInfo.attributes[parentAttribute]
            if parentAttributeInfo.reference:
                self._updateRefOrRefList(
                    anchors, parentObject, parentAttribute, attributeCache
                )
            else:
                self._applyToChild(
                    anchors, parentObject, parentAttribute, attributeCache
                )
        else:
            # parent attribute name not provided
            if self.reference:
                raise Exception(
                    '[%s] Reference "%s" was not expected here'
                    % (self.getSourceLocation(), self.reference)
                )
            else:
                self._applyToChild(
                    anchors, parentObject, parentAttribute, attributeCache
                )

    def _applyWithoutParentContext(
        self, anchors, parentObject, parentAttribute, attributeCache
    ):
        # without knowing the parent, object can be only modified,
        # no new object can be created
        typeName = self.type
        matchingObjects = self._filterMatching(
            wdr.config.listConfigObjects(typeName), attributeCache
        )
        if len(matchingObjects) == 1:
            configObject = matchingObjects[0]
            if self.operation in (Operations.assure, Operations.customize):
                self._updateSimpleAttributes(configObject, attributeCache)
                self._setAnchor(anchors, configObject)
                self._updateComplexAttributes(
                    configObject, anchors, attributeCache
                )
                self._updateChildren(configObject, anchors, attributeCache)
            elif self.operation == Operations.remove:
                self._remove(configObject, anchors, attributeCache)
        elif len(matchingObjects) == 0:
            if self.operation == Operations.assure:
                raise Exception(
                    '[%s] No %s object matched criteria'
                    % (self.getSourceLocation(), typeName)
                )
            elif self.operation in (Operations.customize, Operations.remove):
                pass
        else:
            raise Exception(
                '[%s] Multiple %s objects matched criteria'
                % (self.getSourceLocation(), typeName)
            )


class LoadError:
    def __init__(self, message, filename='', line='', lineno=0):
        self.message = message
        self.filename = filename
        self.line = line[0:-1]
        self.lineno = lineno

    def __str__(self):
        return (
            '[%s(%d)] %s: %s'
            % (self.filename, self.lineno, self.message, self.line)
        )

    def __unicode__(self):
        return unicode(self.__str__())


class _ConfigEventConsumer:
    def __init__(self):
        pass

    def consumeObject(self, filename, line, lineno, manifestPath):
        logger.error(
            '[%s(%d)] manifest parsing error - unexpected object definition',
            filename, lineno
        )
        raise LoadError('Unexpected object definition', filename, line, lineno)

    def consumeKey(self, filename, line, lineno, variables, manifestPath):
        logger.error(
            '[%s(%d)] manifest parsing error - unexpected object key', filename,
            lineno
        )
        raise LoadError('Unexpected key', filename, line, lineno)

    def consumeAttribute(self, filename, line, lineno, variables, manifestPath):
        logger.error(
            '[%s(%d)] manifest parsing error - unexpected object attribute',
            filename, lineno
        )
        raise LoadError('Unexpected attribute', filename, line, lineno)

    def consumeDirective(self, filename, line, lineno, variables, manifestPath):
        logger.error(
            '[%s(%d)] manifest parsing error - unexpected directive', filename,
            lineno
        )
        raise LoadError('Unexpected directive', filename, line, lineno)

    def consumeComment(self, filename, line, lineno, manifestPath):
        pass


class _ObjectConsumer(_ConfigEventConsumer):
    def __init__(self, parentList):
        _ConfigEventConsumer.__init__(self)
        self.parentList = parentList

    def consumeObject(self, filename, line, lineno, manifestPath):
        mat = _typePattern.match(line)
        name = mat.group('type')
        opcode = mat.group('operation')
        linkage = mat.group('linkage')
        obj = ManifestConfigObject(name, filename, lineno)
        obj.operation = obj.mapOperation(opcode)
        if linkage:
            if linkage[0] == '#':
                obj.anchor = linkage[1:]
            else:
                obj.reference = linkage[1:]
        self.parentList.append(obj)
        return [self, _ObjectDataConsumer(obj)]

    def consumeDirective(self, filename, line, lineno, variables, manifestPath):
        mat = _directivePattern.match(line)
        name = mat.group('name')
        values = mat.group('values').split()
        if 'include' == name:
            try:
                self.parentList.extend(
                    _loadConfigurationManifest(
                        _locateManifestFile(
                            values[0],
                            [os.path.dirname(filename)]
                        ),
                        variables,
                        manifestPath
                    )
                )
            except:
                logger.error(
                    '[%s(%d)] error while processing include directive',
                    filename, lineno
                )
                raise
            return [self]
        elif 'import' == name:
            try:
                self.parentList.extend(
                    _loadConfigurationManifest(
                        _locateManifestFile(values[0], manifestPath),
                        variables,
                        manifestPath
                    )
                )
            except:
                logger.error(
                    '[%s(%d)] error while processing import directive',
                    filename, lineno
                )
                raise
            return [self]
        logger.error(
            '[%s(%d)] manifest parsing error - unexpected directive',
            filename, lineno
        )
        raise LoadError('Unexpected directive', filename, line, lineno)


class _ObjectDataConsumer(_ConfigEventConsumer):
    def __init__(self, parentObject):
        _ConfigEventConsumer.__init__(self)
        self.parentObject = parentObject

    def consumeKey(self, filename, line, lineno, variables, manifestPath):
        mat = _keyPattern.match(line)
        name = mat.group('name')
        try:
            value = substituteVariables(mat.group('value'), variables)
        except:
            logger.error(
                '[%s(%d)] error while substituting variables', filename, lineno
            )
            raise
        self.parentObject.keys[name] = value
        return [self]

    def consumeAttribute(self, filename, line, lineno, variables, manifestPath):
        mat = _attPattern.match(line)
        name = mat.group('name')
        value = mat.group('value')
        if value is None:
            values = []
            self.parentObject.attributes[name] = values
            self.parentObject._orderedAttributeNames.append(name)
            return [self, _ObjectConsumer(values)]
        else:
            try:
                self.parentObject.attributes[name] = (
                    substituteVariables(value, variables)
                )
            except:
                logger.error(
                    '[%s(%d)] error while substituting variables', filename,
                    lineno
                )
                raise
            self.parentObject._orderedAttributeNames.append(name)
            return [self, _ConfigEventConsumer()]

    def consumeObject(self, filename, line, lineno, manifestPath):
        mat = _typePattern.match(line)
        name = mat.group('type')
        opcode = mat.group('operation')
        linkage = mat.group('linkage')
        obj = ManifestConfigObject(name, filename, lineno)
        obj.operation = obj.mapOperation(opcode)
        if linkage:
            if linkage[0] == '#':
                obj.anchor = linkage[1:]
            else:
                obj.reference = linkage[1:]
        self.parentObject.children.append(obj)
        return [self, _ObjectDataConsumer(obj)]

    def consumeDirective(self, filename, line, lineno, variables, manifestPath):
        mat = _directivePattern.match(line)
        name = mat.group('name')
        values = mat.group('values').split()
        if 'include' == name:
            self.parentObject.children.extend(
                _loadConfigurationManifest(
                    _locateManifestFile(
                        values[0],
                        [os.path.dirname(filename)]
                    ),
                    variables,
                    manifestPath
                )
            )
            return [self]
        elif 'import' == name:
            self.parentObject.children.extend(
                _loadConfigurationManifest(
                    _locateManifestFile(values[0], manifestPath),
                    variables,
                    manifestPath
                )
            )
            return [self]
        logger.error(
            'manifest parsing error - unexpected directive at line %d', lineno
        )
        raise LoadError('Unexpected directive', filename, line, lineno)


class ApplicationDeploymentListener:
    def __init__(self):
        pass

    def beforeInstall(self, appName, archivePath):
        pass

    def beforeUpdate(self, appName, archivePath):
        pass

    def afterInstall(self, appName, archivePath):
        pass

    def afterUpdate(self, appName, archivePath):
        pass

    def skippedUpdate(self, appName, archivePath):
        pass


class ApplicationObject:
    def __init__(self, name, archive):
        self.name = name
        self.archive = archive
        self.options = {}
        self.extras = {}

    def _str_app_name(self):
        result = ''
        if self.name.find(' ') == -1:
            result += '%s ' % self.name
        else:
            result += '"%s" ' % self.name
        if self.archive.find(' ') == -1:
            result += '%s\n' % self.archive
        else:
            result += '"%s"\n' % self.archive
        return result

    def _str_extra_options(self):
        result = ''
        extraOptionNames = self.extras.keys()
        extraOptionNames.sort()
        for k in extraOptionNames:
            v = self.extras[k]
            if isinstance(v, ListType):
                result += '\t*%s\n' % k
                for c in v:
                    if isinstance(c, ListType):
                        result += '\t\t%s\n' % ';'.join(c)
                    else:
                        result += '\t\t%s\n' % c
            else:
                result += '\t*%s %s\n' % (k, v)
        return result

    def _str_options(self):
        result = ''
        optionNames = self.options.keys()
        optionNames.sort()
        for k in optionNames:
            v = self.options[k]
            if isinstance(v, ListType):
                result += '\t%s\n' % k
                for c in v:
                    if isinstance(c, ListType):
                        result += '\t\t%s\n' % ';'.join(c)
                    else:
                        result += '\t\t%s\n' % c
            else:
                result += '\t%s %s\n' % (k, v)
        return result

    def __str__(self):
        result = ''
        result += self._str_app_name()
        result += self._str_extra_options()
        result += self._str_options()
        return result

    def __unicode__(self):
        return unicode(self.__str__())

    def checksum(self):
        return wdr.util.sha512(str(self))


class _AppEventConsumer:
    def __init__(self):
        pass

    def consumeApp(self, filename, line, lineno, variables):
        logger.error(
            'manifest parsing error'
            ' - unexpected application definition at line %d',
            lineno
        )
        raise LoadError(
            'Unexpected application definition', filename, line, lineno
        )

    def consumeOption(self, filename, line, lineno, variables):
        logger.error(
            'manifest parsing error - unexpected option at line %d', lineno
        )
        raise LoadError('Unexpected option', filename, line, lineno)

    def consumeOptionValue(self, filename, line, lineno, variables):
        logger.error(
            'manifest parsing error - unexpected option value at line %d',
            lineno
        )
        raise LoadError('Unexpected option value', filename, line, lineno)

    def consumeComment(self, filename, line, lineno):
        pass


class _AppConsumer(_AppEventConsumer):
    def __init__(self, parentList):
        _AppEventConsumer.__init__(self)
        self.parentList = parentList

    def consumeApp(self, filename, line, lineno, variables):
        mat = _appNamePattern.match(line)
        name = mat.group('name')
        if name is None:
            name = mat.group('qname')
        name = substituteVariables(name, variables)
        archive = mat.group('path')
        if archive is None:
            archive = mat.group('qpath')
        archive = substituteVariables(archive, variables)
        dirname = os.path.dirname(os.path.normpath(os.path.abspath(filename)))
        archive = os.path.normpath(os.path.join(dirname, archive))
        obj = ApplicationObject(name, archive)
        self.parentList.append(obj)
        return [self, _AppOptionConsumer(obj)]


class _AppOptionConsumer(_AppEventConsumer):
    def __init__(self, parentObject):
        _AppEventConsumer.__init__(self)
        self.parentObject = parentObject

    def consumeOption(self, filename, line, lineno, variables):
        mat = _appOptionPattern.match(line)
        name = mat.group('name')
        value = mat.group('value')
        if name == 'appname':
            logger.error(
                'The \'appname\' option is not allowed in application manifest'
            )
            raise LoadError(
                'The \'appname\' option is not allowed in application manifest',
                filename, line, lineno
            )
        if name.startswith('*'):
            name = name[1:]
            if value is None:
                values = []
                self.parentObject.extras[name] = values
                return [self, _AppOptionValueConsumer(values)]
            else:
                self.parentObject.extras[name] = (
                    substituteVariables(value, variables)
                )
                return [self, _AppEventConsumer()]
            pass
        else:
            if value is None:
                values = []
                self.parentObject.options[name] = values
                return [self, _AppOptionValueConsumer(values)]
            else:
                self.parentObject.options[name] = (
                    substituteVariables(value, variables)
                )
                return [self, _AppEventConsumer()]


class _AppOptionValueConsumer(_AppEventConsumer):
    def __init__(self, parentList):
        _AppEventConsumer.__init__(self)
        self.parentList = parentList

    def consumeOptionValue(self, filename, line, lineno, variables):
        mat = _appOptionValuePattern.match(line)
        value = mat.group('value')
        self.parentList.append(substituteVariables(value, variables).split(';'))
        return [self, _AppEventConsumer()]


def _extraOptionProcessor_startingWeight(mo, name, value):
    wdr.config.getid1(
        '/Deployment:%s' % mo.name
    ).deployedObject.startingWeight = value


def _extraOptionProcessor_classLoadingMode(mo, name, value):
    wdr.config.getid1(
        '/Deployment:%s' % mo.name
    ).deployedObject.classloader.mode = value


def _extraOptionProcessor_webModuleClassLoadingMode(mo, name, value):
    for (uri, mode) in value:
        applied = 0
        for module in (
            wdr.config.getid1('/Deployment:%s' % mo.name).deployedObject.modules
        ):
            if module._type == 'WebModuleDeployment' and module.uri == uri:
                module.classloaderMode = mode
                applied = 1
        if not applied:
            logger.error(
                'webModuleClassLoadingMode option could not match module %s',
                uri
            )
            raise Exception(
                'webModuleClassLoadingMode option could not match module %s',
                uri
            )


def _extraOptionProcessor_clientWSPolicySetAttachments(mo, name, value):
    appName = mo.name
    for att in wdr.task.adminTaskAsDictList(
            AdminTask.getPolicySetAttachments(
                [
                    '-applicationName', appName,
                    '-attachmentType', 'client'
                ]
            )
    ):
        AdminTask.deletePolicySetAttachment(
            [
                '-attachmentId', att['id'],
                '-applicationName', appName,
                '-attachmentType', 'client'
            ]
        )
    for (policySet, resource, binding) in value:
        try:
            attId = AdminTask.createPolicySetAttachment(
                [
                    '-policySet', policySet,
                    '-resources', [resource],
                    '-applicationName', appName,
                    '-attachmentType', 'client'
                ]
            )
            if binding:
                try:
                    AdminTask.setBinding(
                        [
                            '-bindingScope', 'domain',
                            '-bindingName', binding,
                            '-attachmentType', 'client',
                            '-bindingLocation', [
                                ['application', appName],
                                ['attachmentId', attId]
                            ]
                        ]
                    )
                except:
                    AdminTask.setBinding(
                        [
                            '-bindingName', binding,
                            '-attachmentType', 'client',
                            '-bindingLocation', [
                                ['application', appName],
                                ['attachmentId', attId]
                            ]
                        ]
                    )
        except:
            logger.error(
                'failed to apply clientWSPolicySetAttachments for %s',
                [policySet, resource, binding]
            )
            raise


def _extraOptionProcessor_applicationWSPolicySetAttachments(mo, name, value):
    appName = mo.name
    for att in wdr.task.adminTaskAsDictList(
            AdminTask.getPolicySetAttachments(
                [
                    '-applicationName', appName,
                    '-attachmentType', 'application'
                ]
            )
    ):
        AdminTask.deletePolicySetAttachment(
            [
                '-attachmentId', att['id'],
                '-applicationName', appName,
                '-attachmentType', 'application'
            ]
        )
    for (policySet, resource, binding) in value:
        try:
            attId = AdminTask.createPolicySetAttachment(
                [
                    '-policySet', policySet,
                    '-resources', [resource],
                    '-applicationName', appName,
                    '-attachmentType', 'application'
                ]
            )
            if binding:
                try:
                    AdminTask.setBinding(
                        [
                            '-bindingScope', 'domain',
                            '-bindingName', binding,
                            '-attachmentType', 'application',
                            '-bindingLocation', [
                                ['application', appName],
                                ['attachmentId', attId]
                            ]
                        ]
                    )
                except:
                    AdminTask.setBinding(
                        [
                            '-bindingName', binding,
                            '-attachmentType', 'application',
                            '-bindingLocation', [
                                ['application', appName],
                                ['attachmentId', attId]
                            ]
                        ]
                    )
        except:
            logger.error(
                'failed to apply applicationWSPolicySetAttachments for %s',
                [policySet, resource, binding]
            )
            raise


def _extraOptionProcessor_systemTrustWSPolicySetAttachments(mo, name, value):
    pass


def _extraOptionProcessor_providerPolicySharingInfo(mo, name, value):
    appName = mo.name
    for si in wdr.task.adminTaskAsDictList(
        AdminTask.getProviderPolicySharingInfo(
            ['-applicationName', appName]
        )
    ):
        AdminTask.setProviderPolicySharingInfo(
            [
                '-applicationName', appName,
                '-resource', si['resource'],
                '-remove', 'true'
            ]
        )
    for row in value:
        (resource, methods) = row[0:2]
        wsMexPolicySetName = None
        wsMexPolicySetBinding = None
        if len(row) > 2:
            wsMexPolicySetName = row[2]
        if len(row) > 3:
            wsMexPolicySetBinding = row[3]
        args = [
            '-applicationName', appName,
            '-resource', resource,
            '-sharePolicyMethods', methods
        ]
        wsMexProperties = []
        if wsMexPolicySetName:
            wsMexProperties.append(['wsMexPolicySetName', wsMexPolicySetName])
        if wsMexPolicySetBinding:
            wsMexProperties.append(
                ['wsMexPolicySetBinding', wsMexPolicySetBinding]
            )
        if wsMexProperties:
            args.append(['-wsMexProperties', wsMexProperties])
        try:
            AdminTask.setProviderPolicySharingInfo(args)
        except:
            logger.error(
                'failed to apply providerPolicySharingInfo for %s', args
            )
            raise


def _extraOptionProcessor_scaImportWSBindings(mo, name, value):
    appName = mo.name
    for (moduleName, importName, endpoint) in value:
        args = [
            '-applicationName', appName,
            '-moduleName', moduleName,
            '-import', importName,
            '-endpoint', endpoint
        ]
        try:
            AdminTask.modifySCAImportWSBinding(args)
        except:
            logger.error('failed to apply scaImportWSBindings for %s', args)
            raise


def _extraOptionProcessor_scaModuleProperties(mo, name, value):
    appName = mo.name
    for (moduleName, propertyName, propertyValue) in value:
        args = [
            '-applicationName', appName,
            '-moduleName', moduleName,
            '-propertyName', propertyName,
            '-newPropertyValue', propertyValue
        ]
        try:
            AdminTask.modifySCAModuleProperty(args)
        except:
            logger.error('failed to apply scaModuleProperties for %s', args)
            raise


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
    'startingWeight':
    _extraOptionProcessor_startingWeight,
    'classLoadingMode':
    _extraOptionProcessor_classLoadingMode,
    'webModuleClassLoadingMode':
    _extraOptionProcessor_webModuleClassLoadingMode,
    'scaImportWSBindings':
    _extraOptionProcessor_scaImportWSBindings,
    'scaModuleProperties':
    _extraOptionProcessor_scaModuleProperties,
    'applicationWSPolicySetAttachments':
    _extraOptionProcessor_applicationWSPolicySetAttachments,
    'clientWSPolicySetAttachments':
    _extraOptionProcessor_clientWSPolicySetAttachments,
    'systemTrustWSPolicySetAttachments':
    _extraOptionProcessor_systemTrustWSPolicySetAttachments,
    'providerPolicySharingInfo':
    _extraOptionProcessor_providerPolicySharingInfo,
}


def processExtraAppOption(mo, name, value):
    extraOptionProcessor = _extraOptionProcessors.get(name)
    if extraOptionProcessor:
        extraOptionProcessor(mo, name, value)
    else:
        logger.error(
            'Extra option "%s" specified for %s is not supported', name,
            mo.name
        )
        raise Exception(
            'Extra option "%s" specified for %s is not supported'
            % (name, mo.name)
        )


def _importApplicationManifest(filename, variables):
    fi = open(filename, 'r')
    try:
        manifestObjects = []
        stack = [_AppConsumer(manifestObjects)]
        lineno = 0
        for line in fi.readlines():
            lineno += 1
            imat = _genericPattern.match(line)
            if not imat:
                logger.error('wrong indentation in line %d', lineno)
                raise LoadError('Wrong indentation', filename, line, lineno)
            indent = len(imat.group('tabs'))
            if len(stack) < indent + 1:
                return manifestObjects
            if _appNamePattern.match(line):
                stack = stack[0:indent] + stack[indent].consumeApp(
                    filename, line, lineno, variables
                )
            elif _appOptionPattern.match(line):
                stack = stack[0:indent] + stack[indent].consumeOption(
                    filename, line, lineno, variables
                )
            elif _appOptionValuePattern.match(line):
                stack = stack[0:indent] + stack[indent].consumeOptionValue(
                    filename, line, lineno, variables
                )
            elif _commentPattern.match(line):
                stack[indent].consumeComment(filename, line, lineno)
            else:
                logger.error('invalid manifest statement in line %s', lineno)
                raise LoadError('Not recognized', filename, line, lineno)
        return manifestObjects
    finally:
        fi.close()


def _defaultManifestPath():
    manifestPath = ['.']
    sysPathReversed = sys.path[:]
    sysPathReversed.reverse()
    manifestPath.extend(sysPathReversed)
    return manifestPath


def _isApplicationInstalled(appName):
    return appName in wdr.app.listApplications()


def _updateApplication(mo, listener):
    deployedObject = wdr.config.getid1(
        '/Deployment:%s/' % mo.name
    ).deployedObject
    deployedChecksumProperties = deployedObject.lookup(
        'Property',
        {'name': 'wdr.checksum'},
        'properties'
    )
    if deployedChecksumProperties:
        deployedChecksum = deployedChecksumProperties[0].value
    else:
        deployedChecksum = ''
    fileChecksum = wdr.util.generateSHA512(mo.archive)
    manifestChecksum = mo.checksum()
    calculatedChecksum = fileChecksum + ';' + manifestChecksum
    if deployedChecksum == calculatedChecksum:
        listener.skippedUpdate(mo.name, mo.archive)
        return 0
    else:
        listener.beforeUpdate(mo.name, mo.archive)
        logger.debug(
            'application %s will be updated. '
            'deployedChecksum(%s), '
            'calculatedChecksum(%s)',
            mo.name, deployedChecksum, calculatedChecksum
        )
        action = wdr.app.UpdateApp()
        for (k, v) in mo.options.items():
            action[k] = v or None
        action.contents = mo.archive
        action(mo.name)
        deployedObject = wdr.config.getid1(
            '/Deployment:%s/' % mo.name
        ).deployedObject
        deployedObject.assure(
            'Property', {'name': 'wdr.checksum'}, 'properties',
            value=calculatedChecksum,
            description=WDR_CHECKSUM_DESCRIPTION
        )
        listener.afterUpdate(mo.name, mo.archive)
        for extraOptionName in _extraOptionNamesOrdered:
            if mo.extras.has_key(extraOptionName):
                processExtraAppOption(
                    mo, extraOptionName, mo.extras[extraOptionName]
                )
        return 1


def _installApplication(mo, listener):
    listener.beforeInstall(mo.name, mo.archive)
    action = wdr.app.Install()
    for (k, v) in mo.options.items():
        action[k] = v or None
    action['appname'] = mo.name
    action(mo.archive)
    fileChecksum = wdr.util.generateSHA512(mo.archive)
    manifestChecksum = mo.checksum()
    calculatedChecksum = fileChecksum + ';' + manifestChecksum
    deployedObject = wdr.config.getid1(
        '/Deployment:%s/' % mo.name
    ).deployedObject
    deployedObject.assure(
        'Property',
        {'name': 'wdr.checksum'},
        'properties',
        value=calculatedChecksum,
        description=WDR_CHECKSUM_DESCRIPTION
    )
    listener.afterInstall(mo.name, mo.archive)
    for extraOptionName in _extraOptionNamesOrdered:
        if mo.extras.has_key(extraOptionName):
            processExtraAppOption(
                mo, extraOptionName, mo.extras[extraOptionName]
            )


def importApplicationManifest(
    filename, variables={}, listener=None, manifestPath=None
):
    listener = listener or ApplicationDeploymentListener()
    manifestPath = manifestPath or _defaultManifestPath()
    affectedApplications = []
    for mo in _importApplicationManifest(
        _locateManifestFile(filename, manifestPath), variables
    ):
        if _isApplicationInstalled(mo.name):
            if _updateApplication(mo, listener):
                affectedApplications.append(mo.name)
        else:
            _installApplication(mo, listener)
            affectedApplications.append(mo.name)
    return affectedApplications


def _locateManifestFile(filename, manifestPath):
    for dirname in manifestPath:
        dirname = os.path.abspath(dirname)
        candidate = os.path.normpath(os.path.join(dirname, filename))
        if os.path.isfile(candidate):
            return candidate
    raise Exception('Manifest file %s not found' % filename)


def _loadConfigurationManifest(filename, variables, manifestPath):
    filename = os.path.normpath(os.path.abspath(filename))
    logger.debug('loading file %s with variables %s', filename, variables)
    fi = open(filename, 'r')
    logger.debug('file %s successfully opened', filename)
    try:
        manifestObjects = []
        stack = [_ObjectConsumer(manifestObjects)]
        lineno = 0
        for line in fi.readlines():
            lineno += 1
            imat = _genericPattern.match(line)
            if not imat:
                logger.error('[%s(%d)] wrong indentation', filename, lineno)
                raise LoadError('Wrong indentation', filename, line, lineno)
            indent = len(imat.group('tabs'))
            if len(stack) < indent + 1:
                return manifestObjects
            if _typePattern.match(line):
                stack = stack[0:indent] + stack[indent].consumeObject(
                    filename, line, lineno, manifestPath
                )
            elif _keyPattern.match(line):
                stack = stack[0:indent] + stack[indent].consumeKey(
                    filename, line, lineno, variables, manifestPath
                )
            elif _attPattern.match(line):
                stack = stack[0:indent] + stack[indent].consumeAttribute(
                    filename, line, lineno, variables, manifestPath
                )
            elif _directivePattern.match(line):
                stack = stack[0:indent] + stack[indent].consumeDirective(
                    filename, line, lineno, variables, manifestPath
                )
            elif _commentPattern.match(line):
                stack[indent].consumeComment(
                    filename, line, lineno, manifestPath
                )
            else:
                logger.error(
                    '[%s(%d)] invalid manifest statement', filename, lineno
                )
                raise LoadError('Not recognized', filename, line, lineno)
        logger.debug('file %s successfuly parsed', filename)
    finally:
        fi.close()
    return manifestObjects


def importConfigurationManifest(filename, variables={}, manifestPath=None):
    manifestPath = manifestPath or _defaultManifestPath()
    anchors = {}
    attributeCache = wdr.config.AttributeValueCache()
    for mo in _loadConfigurationManifest(
        _locateManifestFile(filename, manifestPath),
        variables,
        manifestPath
    ):
        mo.apply(anchors, None, None, attributeCache)
