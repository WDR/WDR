import java.util.List
import logging
import re
import sys
from java.util import Hashtable

import wdr
from wdr.config import * # noqa
from wdr.control import * # noqa
from wdr.manifest import * # noqa
import wdr.util

(
    AdminApp, AdminConfig, AdminControl, AdminTask, Help
) = wdr.WsadminObjects().getObjects()

logger = logging.getLogger('wdr.tools')

_diagnosticComments = 0

_defaultExportSpec = {}


class ManifestGenerationAdminApp:
    def __init__(self, adminApp, manifestFilename=None):
        shellField = (
            adminApp.__class__.getSuperclass().getDeclaredField('_shell')
        )
        shellField.setAccessible(1)
        self.langUtils = shellField.get(adminApp).getLangUtils()
        if manifestFilename is None:
            self.out = sys.stdout
        else:
            self.out = open(manifestFilename, 'w')

    def install(self, earfile, options):
        parsedOptions = self.langUtils.optionsToHashtable(options)
        self._dump(parsedOptions['appname'], earfile, parsedOptions)

    def update(self, appname, type, options):
        parsedOptions = self.langUtils.optionsToHashtable(options)
        self._dump(appname, parsedOptions['contents'], parsedOptions)

    def _dump(self, appname, earfile, options):
        f = self.out
        f.write('%s %s\n' % (appname, earfile))
        for e in options.entrySet():
            if e.key in (
                'operation', 'contents', 'installed.ear.destination', 'appname'
            ):
                continue
            if java.util.List.isAssignableFrom(e.value.__class__):
                f.write('\t%s\n' % e.key)
                if e.key == 'MapWebModToVH':
                    for v in e.value:
                        values = [el for el in v]
                        values[2] = '$[virtualHost]'
                        f.write('\t\t%s\n' % ';'.join(values))
                elif e.key == 'MapModulesToServers':
                    for v in e.value:
                        values = [el for el in v]
                        if values[1].endswith(',WEB-INF/web.xml'):
                            values[2] = '$[deploymentTargets]+$[webServers]'
                        else:
                            values[2] = '$[deploymentTargets]'
                        f.write('\t\t%s\n' % ';'.join(values))
                else:
                    for v in e.value:
                        f.write('\t\t%s\n' % ';'.join(v))
            else:
                f.write('\t%s %s\n' % (e.key, e.value))
        f.flush()

    def close(self):
        self.out.flush()
        if self.out != sys.stdout:
            self.out.close()


class Task:
    def __init__(self, task):
        self.name = task.name
        self.names = task.columnNames[:]
        self.columnInfo = {}
        for i in range(0, len(task.columnNames)):
            self.columnInfo[task.columnNames[i]] = {
                'name': task.columnNames[i],
                'mutable': task.mutableColumns[i],
                'required': task.requiredColumns[i]
            }
        self.data = []
        if task.taskData:
            for td in task.taskData[1:]:
                d = {}
                self.data.append(d)
                for i in range(0, len(task.columnNames)):
                    value = td[i]
                    d[task.columnNames[i]] = {
                        'name': task.columnNames[i],
                        'mutable': task.mutableColumns[i],
                        'required': task.requiredColumns[i],
                        'value': value
                    }


def processAppDeploymentOptions(task, manifest, columnNames):
    firstRow = task.data[0]
    for optionName in task.names:
        if task.columnInfo[optionName]['mutable']:
            if optionName == 'reloadInterval':
                value = firstRow[optionName]['value']
                if not value:
                    value = '3'
                manifest.options[optionName] = value
            elif optionName == 'installed.ear.destination':
                pass
            else:
                manifest.options[optionName] = firstRow[optionName]['value']


def processGenericDeploymentOptions(task, manifest, columnNames):
    if _diagnosticComments:
        rows = []
        row = []
        rows.append(row)
        row.append('#columns')
        for columnName in task.names:
            row.append(columnName)
        row = []
        rows.append(row)
        row.append('#requiredColumns')
        for columnName in task.names:
            if task.columnInfo[columnName]['required']:
                row.append(columnName)
        row = []
        rows.append(row)
        row.append('#mutableColumns')
        for columnName in task.names:
            if task.columnInfo[columnName]['mutable']:
                row.append(columnName)
        for data in task.data:
            row = ['#']
            rows.append(row)
            for columnName in task.names:
                row.append('%s' % data[columnName]['value'])
        manifest.options['#%s' % task.name] = rows
    if columnNames:
        rows = []
        for data in task.data:
            row = []
            rows.append(row)
            for columnName in columnNames:
                value = data[columnName]['value']
                mutable = data[columnName]['mutable']
                if value is None:
                    if mutable:
                        value = ''
                    else:
                        value = 'null'
                else:
                    value = '%s' % value
                row.append(value)
        if rows:
            manifest.options[task.name] = rows


def processMapModulesToServers(task, manifest, columnNames):
    rows = []
    manifest.options['MapModulesToServers'] = rows
    for data in task.data:
        uri = data['uri']['value']
        if uri.endswith(',META-INF/ejb-jar.xml'):
            rows.append(
                [
                    data['module']['value'],
                    data['uri']['value'],
                    '$[deploymentTargets]'
                ]
            )
        elif uri.endswith(',WEB-INF/web.xml'):
            rows.append(
                [
                    data['module']['value'],
                    data['uri']['value'],
                    '$[deploymentTargets]+$[webServers]'
                ]
            )
        else:
            rows.append(
                [
                    data['module']['value'],
                    data['uri']['value'],
                    data['server']['value']
                ]
            )


def processMapWebModToVH(task, manifest, columnNames):
    rows = []
    manifest.options['MapWebModToVH'] = rows
    for data in task.data:
        rows.append(
            [
                data['webModule']['value'],
                data['uri']['value'],
                '$[virtualHost]'
            ]
        )


def processMapInitParamForServlet(task, manifest, columnNames):
    rows = []
    manifest.options['MapInitParamForServlet'] = rows
    for data in task.data:
        rows.append(
            [
                data['webModule']['value'],
                data['uri']['value'],
                data['web.servlet']['value'],
                data['prop.name']['value'],
                '.*',
                data['prop.value']['value']
            ]
        )


defaultTaskProcessors = {
    'AppDeploymentOptions': {
        'function': processAppDeploymentOptions,
        'columns': None
    },
    'MapModulesToServers': {
        'function': processMapModulesToServers,
        'columns': ['module', 'uri', 'server']
    },
    'MapWebModToVH': {
        'function': processMapWebModToVH,
        'columns': ['webModule', 'uri', 'virtualHost']
    },
    'CtxRootForWebMod': {
        'function': processGenericDeploymentOptions,
        'columns': ['webModule', 'uri', 'web.contextroot']
    },
    'MapRolesToUsers': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'role', 'role.everyone', 'role.all.auth.user', 'role.user',
            'role.group'
        ]
    },
    'MapRunAsRolesToUsers': {
        'function': processGenericDeploymentOptions,
        'columns': ['role', 'userName', 'password']
    },
    'BindJndiForEJBNonMessageBinding': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'EJBModule', 'EJB', 'uri', 'JNDI', 'localHomeJndi', 'remoteHomeJndi'
        ]
    },
    'BindJndiForEJBMessageBinding': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'EJBModule', 'EJB', 'uri', 'listenerPort', 'JNDI', 'jndi.dest',
            'actspec.auth'
        ]
    },
    'BindJndiForEJBBusiness': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'EJBModule', 'EJB', 'uri', 'ejbBusinessInterface',
            'ejbBusinessInterfaceJndi'
        ]
    },
    'MapEJBRefToEJB': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'module', 'EJB', 'uri', 'referenceBinding', 'class', 'JNDI'
        ]
    },
    'MapResRefToEJB': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'module', 'EJB', 'uri', 'referenceBinding', 'resRef.type', 'JNDI',
            'login.config.name', 'auth.props', 'dataSourceProps'
        ]
    },
    'MapResEnvRefToRes': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'module', 'EJB', 'uri', 'referenceBinding', 'resEnvRef.type', 'JNDI'
        ]
    },
    'DataSourceFor10EJBModules': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'EJBModule', 'uri', 'JNDI', 'userName', 'password',
            'login.config.name', 'auth.props'
        ]
    },
    'DataSourceFor20EJBModules': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'EJBModule', 'uri', 'JNDI', 'resAuth', 'login.config.name',
            'auth.props', 'dataSourceProps'
        ]
    },
    'DataSourceFor10CMPBeans': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'EJBModule', 'EJB', 'uri', 'JNDI', 'userName', 'password',
            'login.config.name', 'auth.props'
        ]
    },
    'DataSourceFor20CMPBeans': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'EJBModule', 'EJB', 'uri', 'JNDI', 'resAuth', 'login.config.name',
            'auth.props'
        ]
    },
    'MapInitParamForServlet': {
        'function': processMapInitParamForServlet,
        'columns': None
    },
    'MapEnvEntryForEJBMod': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'EJBModule', 'uri', 'EJB', 'prop.name', 'prop.type',
            'prop.description', 'prop.value'
        ]
    },
    'MapEnvEntryForWebMod': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'webModule', 'uri', 'prop.name', 'prop.type', 'prop.description',
            'prop.value'
        ]
    },
    'EnsureMethodProtectionFor10EJB': {
        'function': processGenericDeploymentOptions,
        'columns': ['EJBModule', 'uri', 'method.denyAllAccessPermission']
    },
    'EnsureMethodProtectionFor20EJB': {
        'function': processGenericDeploymentOptions,
        'columns': ['EJBModule', 'uri', 'method.protectionType']
    },
    'CorrectOracleIsolationLevel': {
        'function': processGenericDeploymentOptions,
        'columns': ['module', 'referenceBinding', 'JNDI', 'isolationLevel']
    },
    'MapMessageDestinationRefToEJB': {
        'function': processGenericDeploymentOptions,
        'columns': ['module', 'EJB', 'uri', 'messageDestinationObject', 'JNDI']
    },
    'BackendIdSelection': {
        'function': processGenericDeploymentOptions,
        'columns': ['EJBModule', 'uri', 'CurrentBackendId']
    },
    'MapSharedLibForMod': {
        'function': processGenericDeploymentOptions,
        'columns': ['module', 'uri', 'sharedLibName']
    },
    'SharedLibRelationship': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'module', 'uri', 'relationship', 'compUnitName', 'matchTarget'
        ]
    },
    'JSPCompileOptions': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'webModule', 'uri', 'jsp.classpath', 'useFullPackageNames',
            'jdkSourceLevel', 'disableJspRuntimeCompilation'
        ]
    },
    'ActSpecJNDI': {
        'function': processGenericDeploymentOptions,
        'columns': ['RARModule', 'uri', 'j2cid', 'j2c.jndiName']
    },
    'MetadataCompleteForModules': {
        'function': processGenericDeploymentOptions,
        'columns': ['module', 'uri', 'lockDeploymentDescriptor']
    },
    'CustomActivationPlan': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'module', 'uri', 'activation.plan.add', 'activation.plan.remove'
        ]
    },
    'WebServicesServerBindPort': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'webservices.cfgbnd_Module_Name', 'webservices.cfgbnd_Web_Service',
            'webservices.cfgbnd_Port', 'webservices.cfgbnd_Scope'
        ]
    },
    'WebServicesServerCustomProperty': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'webservices.cfgbnd_Module_Name', 'webservices.cfgbnd_Web_Service',
            'webservices.cfgbnd_Port', 'webservices.cfgbnd_Property',
            'webservices.cfgbnd_Value'
        ]
    },
    'WebServicesClientBindPortInfo': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'webservices.cfgbnd_Module_Name', 'webservices.cfgbnd_EJB',
            'webservices.cfgbnd_Web_Service', 'webservices.cfgbnd_Port',
            'webservices.cfgbnd_Timeout', 'webservices.cfgbnd_BasicAuth_ID',
            'webservices.cfgbnd_BasicAuth_Password',
            'webservices.cfgbnd_SSL_Config',
            'webservices.cfgbnd_Overridden_Endpoint',
            'webservices.cfgbnd_Overridden_BindingNamespace'
        ]
    },
    'WebServicesClientBindDeployedWSDL': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'webservices.cfgbnd_Module_Name', 'webservices.cfgbnd_EJB',
            'webservices.cfgbnd_Web_Service', 'webservices.cfgbnd_Deployed_WSDL'
        ]
    },
    'WebServicesClientBindPreferredPort': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'webservices.cfgbnd_Module_Name', 'webservices.cfgbnd_EJB',
            'webservices.cfgbnd_Web_Service', 'webservices.cfgbnd_Port_Type',
            'webservices.cfgbnd_Port'
        ]
    },
    'WebServicesClientCustomProperty': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'webservices.cfgbnd_Module_Name', 'webservices.cfgbnd_EJB',
            'webservices.cfgbnd_Web_Service', 'webservices.cfgbnd_Port',
            'webservices.cfgbnd_Property', 'webservices.cfgbnd_Value'
        ]
    },
    'EJBDeployOptions': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'deployejb.classpath', 'deployejb.rmic', 'deployejb.dbtype',
            'deployejb.dbschema', 'deployejb.complianceLevel',
            'deployejb.dbaccesstype', 'deployejb.sqljclasspath'
        ]
    },
    'JSPReloadForWebMod': {
        'function': processGenericDeploymentOptions,
        'columns': ['webModule', 'uri', 'jspReloadEnabled', 'jspReloadInterval']
    },
    'CorrectUseSystemIdentity': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'EJB', 'EJBModule', 'uri', 'method.signature', 'role', 'userName',
            'password'
        ]
    },
    'EmbeddedRar': {
        'function': processGenericDeploymentOptions,
        'columns': [
            'RARModule', 'uri', 'j2ctype', 'j2cid', 'j2c.name', 'j2c.jndiName'
        ]
    },
    'MapJaspiProvider': {
        'function': processGenericDeploymentOptions,
        'columns': None
    },
    'MapEnvEntryForClientMod': {
        'function': processGenericDeploymentOptions,
        'columns': None
    },
    'MapEnvEntryForApp': {
        'function': processGenericDeploymentOptions,
        'columns': None
    },
    'WebServicesPublishWSDLInfo': {
        'function': processGenericDeploymentOptions,
        'columns': None
    }
}


def exportApplicationManifestToFile(appName, filename, customTaskProcessors={}):
    fi = open(filename, 'w')
    try:
        fi.write(str(exportApplicationManifest(appName, customTaskProcessors)))
    finally:
        fi.close()


def exportApplicationManifest(appName, customTaskProcessors={}):
    taskProcessors = {}
    taskProcessors.update(defaultTaskProcessors)
    taskProcessors.update(customTaskProcessors)
    prefs = Hashtable()
    appManagement = getJMXMBean1(type='AppManagement')
    manifest = ApplicationObject(appName, '../applications/%s.ear' % appName)
    deployment = getid1('/Deployment:%s/' % appName)
    appDeployment = deployment.deployedObject
    manifest.extras['startingWeight'] = '%d' % appDeployment.startingWeight
    manifest.extras['classLoadingMode'] = '%s' % appDeployment.classloader.mode
    webModuleClassLoadingModes = []
    for module in appDeployment.modules:
        if module._type == 'WebModuleDeployment':
            webModuleClassLoadingModes.append(
                [module.uri, module.classloaderMode]
            )
    if webModuleClassLoadingModes:
        manifest.extras['webModuleClassLoadingMode'] = (
            webModuleClassLoadingModes
        )
    scaMapping = {}
    try:
        for moduleInfo in [
            l.split(':') for l in AdminTask.listSCAModules().splitlines()
        ]:
            scaMapping[moduleInfo[1]] = moduleInfo[0]
    except AttributeError:
        pass
    scaModuleName = scaMapping.get(appName)
    if scaModuleName:
        try:
            manifest.extras['scaModuleProperties'] = [
                [scaModuleName] + l.split('=')
                for l in AdminTask.showSCAModuleProperties(
                    [
                        '-moduleName', scaModuleName,
                        '-applicationName', appName
                    ]
                ).splitlines()
            ]
        except:
            pass
        try:
            scaImportWSBindings = []
            deployedEndpointPat = re.compile(r'.*deployedEndpoint=([^,]+),.*')
            for importName in AdminTask.listSCAImports(
                [
                    '-moduleName', scaModuleName,
                    '-applicationName', appName
                ]
            ).splitlines():
                try:
                    importBinding = AdminTask.showSCAImportWSBinding([
                        '-moduleName', scaModuleName,
                        '-applicationName', appName,
                        '-import', importName
                    ])
                    deployedEndpointMat = (
                        deployedEndpointPat.match(importBinding)
                    )
                    if deployedEndpointMat:
                        scaImportWSBindings.append(
                            [
                                scaModuleName,
                                importName,
                                deployedEndpointMat.group(1)
                            ]
                        )
                except:
                    pass
            if scaImportWSBindings:
                manifest.extras['scaImportWSBindings'] = scaImportWSBindings
        except:
            pass
    applicationWSPolicySetAttachments = wdr.task.adminTaskAsDictList(
        AdminTask.getPolicySetAttachments([
            '-applicationName', appName,
            '-attachmentType', 'application'
        ]))
    if applicationWSPolicySetAttachments:
        applicationWSPolicySetAttachmentList = []
        for att in applicationWSPolicySetAttachments:
            applicationWSPolicySetAttachmentList.append(
                [
                    att['name'], att['pattern.0'], att.get('binding', '')
                ]
            )
        manifest.extras['applicationWSPolicySetAttachments'] = (
            applicationWSPolicySetAttachmentList
        )
    clientWSPolicySetAttachments = wdr.task.adminTaskAsDictList(
        AdminTask.getPolicySetAttachments(
            [
                '-applicationName', appName,
                '-attachmentType', 'client'
            ]
        )
    )
    if clientWSPolicySetAttachments:
        clientWSPolicySetAttachmentList = []
        for att in clientWSPolicySetAttachments:
            clientWSPolicySetAttachmentList.append(
                [
                    att['name'], att['pattern.0'], att.get('binding', '')
                ]
            )
        manifest.extras['clientWSPolicySetAttachments'] = (
            clientWSPolicySetAttachmentList
        )
    providerPolicySharingInfo = wdr.task.adminTaskAsDictList(
        AdminTask.getProviderPolicySharingInfo(['-applicationName', appName]))
    if providerPolicySharingInfo:
        providerPolicySharingInfoList = []
        for psi in providerPolicySharingInfo:
            providerPolicySharingInfoList.append(
                [
                    psi['resource'], psi['sharePolicyMethods'],
                    psi.get('wsMexPolicySetName', ''),
                    psi.get('wsMexPolicySetBinding', '')
                ]
            )
        manifest.extras['providerPolicySharingInfo'] = (
            providerPolicySharingInfoList
        )
    for task in appManagement.getApplicationInfo(appName, prefs, None):
        taskProcessor = taskProcessors.get(task.name)
        if taskProcessor:
            taskProcessor['function'](
                Task(task), manifest, taskProcessor.get('columns')
            )
    for n in manifest.options.keys():
        v = manifest.options[n]
        if isinstance(v, ListType):
            v.sort()
    for n in manifest.extras.keys():
        v = manifest.extras[n]
        if isinstance(v, ListType):
            v.sort()
    return manifest


def _normalizeExportSpecs(exportSpecs):
    exportSpec = {}
    for es in exportSpecs:
        for (k, v) in es.items():
            exportSpec[k] = v.copy()
    for (k, v) in exportSpec.items():
        for p in v.get('parents', []):
            items = exportSpec.get(p, {}).get('items', [])
            if {'child': k} not in items:
                items.append({'child': k})
            exportSpec.get(p, {})['items'] = items
    return exportSpec


def exportConfigurationManifestToFile(
    configObjects,
    filename,
    *exportSpecs
):
    exportSpec = _normalizeExportSpecs(exportSpecs)
    fi = open(filename, 'w')
    try:
        s = {}
        fi.write(
            reduce(
                lambda x, y: x + str(y),
                [
                    exportConfigurationManifest(co, exportSpec, s)
                    for co in configObjects
                ],
                ''
            )
        )
    finally:
        fi.close()


def exportConfigurationManifest(configObject, exportSpec, exportedObjects):
    typeName = configObject._type
    typeInfo = wdr.config.getTypeInfo(typeName)
    result = wdr.manifest.ManifestConfigObject(typeName)
    if exportSpec.has_key(typeName):
        typeExportSpec = exportSpec[typeName]
    else:
        return result
    attributes = configObject.getAllAttributes()
    for n in typeExportSpec.get('keys', []):
        if attributes.has_key(n):
            attInfo = typeInfo.attributes[n]
            attTypeInfo = wdr.config.getTypeInfo(attInfo.type)
            v = attributes[n]
            if attTypeInfo.converter:
                if attInfo.list:
                    result.keys[n] = ';'.join(
                        [attTypeInfo.converter.toAdminConfig(e) for e in v]
                    )
                else:
                    result.keys[n] = attTypeInfo.converter.toAdminConfig(v)
    for item in typeExportSpec.get('items', []):
        if item.get('attribute'):
            name = item['attribute']
            if attributes.has_key(name):
                attInfo = typeInfo.attributes[name]
                attTypeInfo = wdr.config.getTypeInfo(attInfo.type)
                v = attributes[name]
                if attTypeInfo.converter:
                    if attInfo.list:
                        result.items.append(
                            {
                                'attribute': 1,
                                'name': name,
                                'value': ';'.join(
                                    [
                                        attTypeInfo.converter.toAdminConfig(e)
                                        for e in v
                                    ]
                                ),
                            }
                        )
                    else:
                        result.items.append(
                            {
                                'attribute': 1,
                                'name': name,
                                'value': attTypeInfo.converter.toAdminConfig(v),
                            }
                        )
                else:
                    if attInfo.list:
                        values = []
                        for e in v:
                            if exportSpec.has_key(e._type):
                                values.append(
                                    exportConfigurationManifest(
                                        e, exportSpec, exportedObjects
                                    )
                                )
                        if values:
                            result.items.append(
                                {
                                    'attribute': 1,
                                    'name': name,
                                    'value': values,
                                }
                            )
                    else:
                        if exportSpec.has_key(v._type):
                            result.items.append(
                                {
                                    'attribute': 1,
                                    'name': name,
                                    'value': exportConfigurationManifest(
                                        v, exportSpec, exportedObjects
                                    ),
                                }
                            )
        elif item.get('ref'):
            name = item['ref']
            if attributes.has_key(name):
                attInfo = typeInfo.attributes[name]
                attTypeInfo = wdr.config.getTypeInfo(attInfo.type)
                if not attTypeInfo.converter:
                    values = []
                    if attInfo.list:
                        v = attributes[name]
                        for e in v:
                            if exportedObjects.has_key(str(e)):
                                exportedObject = exportedObjects[str(e)]
                                exportedObject['manifestObject'].anchor = \
                                    exportedObject['id']
                                mo = wdr.manifest.ManifestConfigObject(
                                    exportedObject['manifestObject'].type
                                )
                                mo.reference = exportedObject['id']
                                values.append(mo)
                    else:
                        v = attributes[name]
                        if v and exportedObjects.has_key(str(v)):
                            exportedObject = exportedObjects[str(v)]
                            exportedObject['manifestObject'].anchor = \
                                exportedObject['id']
                            mo = wdr.manifest.ManifestConfigObject(
                                exportedObject['manifestObject'].type
                            )
                            mo.reference = exportedObject['id']
                            values.append(mo)
                    if values:
                        result.items.append(
                            {
                                'attribute': 1,
                                'name': name,
                                'value': values,
                            }
                        )
        elif item.get('child'):
            c = item['child']
            for co in configObject.lookup(c, {}):
                result.items.append(
                    {
                        'child': 1,
                        'value': exportConfigurationManifest(
                            co, exportSpec, exportedObjects
                        ),
                    }
                )
    return result
