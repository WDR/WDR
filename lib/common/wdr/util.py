from pprint import PrettyPrinter
import jarray
import java.io
import java.lang
import java.math
import java.security
import java.util.zip
import com.ibm.websphere.crypto
import logging
import string
import types
import wdr

(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger('wdr.util')


def sync(quiet=0):
    # DMgr node can't be synchronized
    # this function requests synchronization only for nodes which contain
    # a nodeagent
    totalNodes = 0.0
    synchronizedNodes = 0.0
    for node in wdr.config.listConfigObjects('Node'):
        for srv in node.listConfigObjects('Server'):
            if srv.serverType == 'NODE_AGENT':
                totalNodes += 1.0
                for ns in wdr.control.queryMBeans(
                    type='NodeSync',
                    node=node.name
                ):
                    if not quiet:
                        logger.info('synchronizing node %s', node.name)
                    if ns.sync():
                        synchronizedNodes += 1.0
                    else:
                        if not quiet:
                            logger.warning(
                                'synchronization of %s'
                                ' did not complete successfully',
                                node.name
                            )
                    break
                else:
                    if not quiet:
                        logger.warning(
                            'unable to contact node synchronization service '
                            ' on node %s',
                            node.name
                        )
    # we want to leave ConfigSession clean after sync in order to avoid
    # creation of garbage in WebSphere's temporary directories
    if not wdr.config.hasChanges():
        wdr.config.reset()
    if totalNodes > 0.0:
        return synchronizedNodes / totalNodes
    else:
        return 1.0


# This utility function verifies WAS type registry. It may return some missing
# types.
# For WAS 6.1:
# wsadmin>wdr.util.checkTypeRegistryIntegrity()
# J2EEEAttribute.eContainingClass has unknown type: EClass
# J2EEEAttribute.eType has unknown type: EClassifier
# WebModuleRef.module has unknown type: Module
# J2EEEAttribute.eAnnotations has unknown type: EAnnotation
# ModuleRef.module has unknown type: Module
# ResourceEnvRef.type has unknown type: JavaClass
# JNDIEnvRefsGroup.serviceRefs has unknown type: ServiceRef
# ConnectorModuleRef.module has unknown type: Module
# Listener.listenerClass has unknown type: JavaClass
# ClientModuleRef.module has unknown type: Module
# ApplicationClientFile.deploymentDescriptor has unknown type: ApplicationClient
# WARFile.deploymentDescriptor has unknown type: WebApp
# EJBJarFile.deploymentDescriptor has unknown type: EJBJar
# EJBModuleRef.module has unknown type: Module
# wsadmin>
# For WAS 7.0:
# wsadmin>wdr.util.checkTypeRegistryIntegrity()
# ResourceEnvRef.type has unknown type: JavaClass
# WARFile.deploymentDescriptor has unknown type: WebApp
# ConnectorModuleRef.module has unknown type: Module
# EJBModuleRef.module has unknown type: Module
# EJBJarFile.deploymentDescriptor has unknown type: EJBJar
# Listener.listenerClass has unknown type: JavaClass
# InjectionTarget.injectionTargetClass has unknown type: JavaClass
# ModuleRef.module has unknown type: Module
# LifecycleCallbackType.lifecycleCallbackClass has unknown type: JavaClass
# ClientModuleRef.module has unknown type: Module
# J2EEEAttribute.eContainingClass has unknown type: EClass
# J2EEEAttribute.eType has unknown type: EClassifier
# J2EEEAttribute.eAnnotations has unknown type: EAnnotation
# ApplicationClientFile.deploymentDescriptor has unknown type: ApplicationClient
# JNDIEnvRefsGroup.serviceRefs has unknown type: ServiceRef
# WebModuleRef.module has unknown type: Module
# wsadmin>
def _checkTypeRegistryIntegrity():
    wdr.config.initializeTypeRegistry()
    for t in wdr.config._typeRegistry.values():
        for a in t.attributes.values():
            if a.type not in wdr.config._typeRegistry.keys():
                print '%s.%s has unknown type: %s' % (t.name, a.name, a.type)


def _findAllReferences():
    referenceRegistry = {}
    wdr.config.initializeTypeRegistry()
    for t in wdr.config._typeRegistry.values():
        for a in t.attributes.values():
            if a.reference:
                refs = referenceRegistry.get(t.name, [])
                refs.append(a.name)
                referenceRegistry[t.name] = refs
    return referenceRegistry


def _findListReferences():
    referenceRegistry = {}
    wdr.config.initializeTypeRegistry()
    for t in wdr.config._typeRegistry.values():
        for a in t.attributes.values():
            if a.reference and a.list:
                refs = referenceRegistry.get(t.name, [])
                refs.append(a.name)
                referenceRegistry[t.name] = refs
    return referenceRegistry


def _findSingleReferences():
    referenceRegistry = {}
    wdr.config.initializeTypeRegistry()
    for t in wdr.config._typeRegistry.values():
        for a in t.attributes.values():
            if a.reference and a.list:
                refs = referenceRegistry.get(t.name, [])
                refs.append(a.name)
                referenceRegistry[t.name] = refs
    return referenceRegistry


def _findAllAttributes():
    attributeRegistry = {}
    wdr.config.initializeTypeRegistry()
    for t in wdr.config._typeRegistry.values():
        for a in t.attributes.values():
            refs = attributeRegistry.get(t.name, [])
            refs.append(a.name)
            attributeRegistry[t.name] = refs
    return attributeRegistry


def _printAllReferences():
    pp = PrettyPrinter(indent=4)
    pp.pprint(_findAllReferences())


def _printListReferences():
    pp = PrettyPrinter(indent=4)
    pp.pprint(_findListReferences())


def _printSingleReferences():
    pp = PrettyPrinter(indent=4)
    pp.pprint(_findSingleReferences())


def _printAllAttributes():
    pp = PrettyPrinter(indent=4)
    pp.pprint(_findAllAttributes())


def generateUuid(length):
    rnd = java.security.SecureRandom()
    bytes = jarray.zeros(length, 'b')
    rnd.nextBytes(bytes)
    bigInt = java.math.BigInteger(bytes)
    return string.upper(bigInt.toString(16))


def _toHex(bytes):
    hexDigits = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D',
        'E', 'F'
    ]
    result = ''
    for b in bytes:
        result += hexDigits[(b & 0xf0) >> 4]
        result += hexDigits[b & 0x0f]
    return result


def _digestFile(md, filename):
    fis = java.io.BufferedInputStream(java.io.FileInputStream(filename))
    try:
        buf = jarray.zeros(1024, 'b')
        b = 0
        while b >= 0:
            b = fis.read(buf)
            if b > 0:
                md.update(buf, 0, b)
    finally:
        fis.close()


def generateMD5(filename):
    md = java.security.MessageDigest.getInstance('MD5')
    _digestFile(md, filename)
    return _toHex(md.digest())


def generateSHA1(filename):
    md = java.security.MessageDigest.getInstance('SHA1')
    _digestFile(md, filename)
    return _toHex(md.digest())


def generateSHA256(filename):
    md = java.security.MessageDigest.getInstance('SHA256')
    _digestFile(md, filename)
    return _toHex(md.digest())


def generateSHA384(filename):
    md = java.security.MessageDigest.getInstance('SHA384')
    _digestFile(md, filename)
    return _toHex(md.digest())


def generateSHA512(filename):
    md = java.security.MessageDigest.getInstance('SHA512')
    _digestFile(md, filename)
    return _toHex(md.digest())

def generateEarChecksum(filename):
    md = java.security.MessageDigest.getInstance('SHA512')
    fis = java.io.BufferedInputStream(java.io.FileInputStream(filename))
    try:
        zis = java.util.zip.ZipInputStream(fis)
        while 1:
            entry = zis.nextEntry
            if entry is None:
                break
            if entry.directory:
				md.update(entry.name)
            elif entry.name == 'MANIFEST.MF':
				continue #For now, completely skip EAR manifest
            elif entry.name.endswith('.jar') or entry.name.endswith('.war'):
                buf = jarray.zeros(1024, 'b')
                b = 1
                baos = java.io.ByteArrayOutputStream()
                while b > 0:
                    b = zis.read(buf)
                    if b > 0:
                        baos.write(buf, 0, b)
                _digestJarWarContents(md, baos.toByteArray())				
            else:
                buf = jarray.zeros(1024, 'b')
                b = 0
                while b >= 0:
                    b = zis.read(buf)
                    if b > 0:
                        md.update(buf, 0, b)
            zis.closeEntry()
    finally:
        fis.close()

    return _toHex(md.digest())

def _digestJarWarContents(md, byteArray):
    try:
		jarWarIS = java.util.zip.ZipInputStream(java.io.ByteArrayInputStream(byteArray))
	    while 1:
            entry = jarWarIS.nextEntry
            if entry is None:
                break
            if entry.directory:
				md.update(entry.name)
			elif entry.name == 'MANIFEST.MF':
				continue #For now, completely skip JAR manifest
			elif entry.name.endswith('.jar'):
                buf = jarray.zeros(1024, 'b')
                b = 1
                baos = java.io.ByteArrayOutputStream()
                while b > 0:
                    b = jarWarIS.read(buf)
                    if b > 0:
                        baos.write(buf, 0, b)
                _digestJarContents(md, baos.toByteArray())				
			else:
                buf = jarray.zeros(1024, 'b')
                b = 0
                while b >= 0:
                    b = jarWarIS.read(buf)
                    if b > 0:
                        md.update(buf, 0, b)
            jarWarIS.closeEntry()
    finally:
        jarWarIS.close()
	return md

	
def md5(str):
    md = java.security.MessageDigest.getInstance('MD5')
    md.update(java.lang.String(str).getBytes('UTF-8'))
    return _toHex(md.digest())


def sha1(str):
    md = java.security.MessageDigest.getInstance('SHA1')
    md.update(java.lang.String(str).getBytes('UTF-8'))
    return _toHex(md.digest())


def sha256(str):
    md = java.security.MessageDigest.getInstance('SHA256')
    md.update(java.lang.String(str).getBytes('UTF-8'))
    return _toHex(md.digest())


def sha384(str):
    md = java.security.MessageDigest.getInstance('SHA384')
    md.update(java.lang.String(str).getBytes('UTF-8'))
    return _toHex(md.digest())


def sha512(str):
    md = java.security.MessageDigest.getInstance('SHA512')
    md.update(java.lang.String(str).getBytes('UTF-8'))
    return _toHex(md.digest())


def readZipEntry(filename, entryname):
    content = None
    fis = java.io.BufferedInputStream(java.io.FileInputStream(filename))
    try:
        zis = java.util.zip.ZipInputStream(fis)
        while 1:
            entry = zis.nextEntry
            if entry is None:
                break
            if entry.name == entryname and not entry.directory:
                buf = jarray.zeros(1024, 'b')
                b = 1
                baos = java.io.ByteArrayOutputStream()
                while b > 0:
                    b = zis.read(buf)
                    if b > 0:
                        baos.write(buf, 0, b)
                content = java.lang.String(baos.toByteArray(), 'UTF-8')
            zis.closeEntry()
    finally:
        fis.close()
    return content


def _mergeVariables(d, u):
    for (k, v) in u.items():
        if isinstance(v, types.DictType):
            r = _mergeVariables(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def mergeVariables(*scopes):
    result = {}
    for s in scopes:
        result = _mergeVariables(result, s)
    return result


def encodePassword(str):
    return com.ibm.websphere.crypto.PasswordUtil.encode(str)


def decodePassword(str):
    return com.ibm.websphere.crypto.PasswordUtil.decode(str)
