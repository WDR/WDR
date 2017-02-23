---
layout: page
title: Application and configuration manifests
short_title: Manifests
---

<!--
The document contains snippets of WDR application and configuration manifests
Make sure that you preserve original indentation in this document (both spaces AND tabs)
-->

Managing deployments and configurations of a complex WAS cells can be challenging. Doing it with multiple (non-production, production, DR) environments without introducing inconsistencies raises the complexity exponentially with each new environment. Automated configuration becomes a must. While it is possible to script everything in wsadmin (with or without WDR), the complexity is being shifted from product configuration management to management of scripts and script libraries. Comparing two versions of a script and understanding what exact changes will be introduced after script execution is not that trivial either. Developing a fully idempotent script, which you can run end-to-end without risk of creating duplicates or missing some changes makes your scripts even more complex and difficult to maintain. The fact that your organisation uses ND and BASE cells introduces another dimension to the problem space. This is where manifests come to the rescue.

One of the main motivations for automating management of WebSphere is to keep multiple environments in sync. This goal can be difficult to achieve using just scripts. As stated previously, the main challenges are:

* idempotency
* variable externalization
* reuse and collaboration
* change review

WDR tries to address these challenges with application and configuration manifests.
The concept of manifests was borrowed from system configuration management tools:
[Ansible](http://www.ansibleworks.com/), [Chef](http://www.opscode.com/), [Puppet](http://www.puppetlabs.com/)
and [others](http://en.wikipedia.org/wiki/Comparison_of_open_source_configuration_management_software).

**Idempotency**

> In short: making sure that the same configuration can be safely applied over and over without breaking anything. Manifests describe the desired state of the resource, not actions. The process of importing a manifest determines what changes (if any) are necessary and performs these changes.

**Variable externalization**

> The structure of configuration objects and the deployment process are generic and do not change between different staging environments.
> The variable parts are stored in separate files.

**Reuse and collaboration**

> Configuration manifests can reference other manifests. This feature allows for reuse of some common configuration manifests across different configuration objects (for example: a list of custom JVM properties being applied to multiple JVMs) and reuse the same manifests in totally different topologies (for example a DataSource object being created at ServerCluster scope in ND cell or at Server scope in BASE cell on developer's workstation).

**Change review**

> Possibility of comparing different versions of configurations or deployments and identifying the differences. Manifests are meant to be more readable and diff-friendly than scripts. They are also more restricted than scripts: application manifest may only install/update applications, configuration manifest may only create/modify configuration objects. Syntax and capability constraints of application and configuration manifests make them more review-friendly.

In multiple areas, the manifests address the complexity and change-management issues in WAS configuration management better than scripts do:

* manifests are simple text files, hence they are easy to review
* you can externalize environment-specific variables from the manifest and make the manifest portable across staging environment
* the process of importing of manifest is idempotent
* manifests are diff-friendly, it is generally much easier to review changes introduced to manifest than new version of a script
* they are not executable, hence you know that they only change configuration or install/update applications, cannot interact with WAS runtime, etc.
* the scope potential manifest impact can be easily determined in advance by looking at root objects of the manifest
* variable expansion allows for environment-specific customisations
* referencing configuration manifest from other manifests reduces development and maintenance effort
* manifest reuse promotes collaboration between development and operations teams

Application & configuration manifests are tab-indented text files. They can be imported into WAS environment using [importApplicationManifest](reference/wdr.manifest.importApplicationManifest.html) or [importConfigurationManifest](reference/wdr.manifest.importConfigurationManifest.html) functions. Manifests may contain variable references, the actual values of these variables are being expanded during the import process.

> WDR manifests MUST be tab-indented. Check [Jython 2.1](jython21.html) page to understand why.

# Application manifests

The application manifests describe application deployment options. Manifest importing process detects changes made to application binaries and the manifest itself and, depending on the result of comparisons, installs the application, updates it or simply skips changes.

The manifests can be "standalone" files, but they can also be embedded in the
application binary itself under the `META-INF/manifest.wdra` location.

Standalone manifests are more suitable if you mainly look after WAS
infrastructure and do not control the build of application archives. You'll
probably choose to keep them in some sort of version-controlled repository,
together with scripts and configuration manifests.

Embedded manifests on the other hand are part of the application archive
itself and are version-controlled together with application code. During
the build process, they need to be included into application archive under
`META-INF/manifest.wdra` path. You should probably choose embedded manifests if
you are in control of application build process, especially if you also store
application archives in a binary repository like Artifactory or Nexus and/or
the application manifests change frequently, deployment rollbacks are a
concern, etc.

## Creating application manifests

Application manifests can be edited manually or generated based on existing
deployment using
[wdr.tools.exportApplicationManifestToFile](reference/wdr.tools.exportApplicationManifestToFile.html)
function.

## Importing application manifests

Application manifests can be imported using

* [wdr.manifest.importApplicationManifest](reference/wdr.manifest.importApplicationManifest.html)
    for importing standalone manifests

* [wdr.manifest.importApplicationEmbeddedManifest](reference/wdr.manifest.importApplicationEmbeddedManifest.html)
    for importing embedded manifests

## Application manifest syntax and structure

An example application manifest may look as follows

    DefaultApplication ../applications/DefaultApplication.ear
    	DataSourceFor20CMPBeans
    		Increment EJB module;Increment;Increment.jar,META-INF/ejb-jar.xml;jdbc/DefaultEJBTimerDataSource;cmpBinding.perConnectionFactory;;
    	filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755
    	MapModulesToServers
    		Increment EJB module;Increment.jar,META-INF/ejb-jar.xml;$[deploymentTargets]
    		Default Web Application;DefaultWebApplication.war,WEB-INF/web.xml;$[deploymentTargets]+$[webServers]
    	noprocessEmbeddedConfig
    	DataSourceFor20EJBModules
    		Increment EJB module;Increment.jar,META-INF/ejb-jar.xml;jdbc/DefaultEJBTimerDataSource;cmpBinding.perConnectionFactory;;;
    	nouseAutoLink
    	distributeApp
    	noreloadEnabled
    	asyncRequestDispatchType DISABLED
    	validateinstall warn
    	noallowDispatchRemoteInclude
    	noallowServiceRemoteInclude
    	MapRolesToUsers
    		All Role;AppDeploymentOption.No;AppDeploymentOption.No;;;AppDeploymentOption.Yes;;
    	nodeployws
    	nouseMetaDataFromBinary
    	nodeployejb
    	createMBeansForResources
    	MapWebModToVH
    		Default Web Application;DefaultWebApplication.war,WEB-INF/web.xml;$[virtualHost]
    	nopreCompileJSPs

### Application name and path to application archive

The first line of the manifest contains application name (as displayed in
AdminConsole) and path to EAR/WAR archive. The path is relative to application
manifest. Note that the first line is not indented.

The application name is mandatory.

The path to archive is mandatory for standalone manifests. Embedded manifests
must not have archive path.

The first line in standalone manifests will look as follows:

    ApplicationName path/to/application.ear

Embedded manifests will specify only the applicaiton name:

    ApplicationName

### WDR-specific options

Application manifest may contain WDR-specific application installation/update options. They syntax is similar to standard AdminApp options described below. Names of special options have to be prefixed with asterisk.

The following is a list of all extra options supported by current version of WDR. The list may be extended in subsequent releases, based on users' feedback:

* **startingWeight** specifies the startup weight of the application. The value is an integer describing application's starting weight. More details on staring weight can be found in WAS InfoCenter.

Example:

    	*startingWeight 1

* **classLoadingMode** specifies class loader mode for the application. Two possible values are `PARENT_FIRST` and `PARENT_LAST`. See WAS InfoCenter for more details on application class loading mode.

Example:

    	*classLoadingMode PARENT_FIRST

* **webModuleClassLoadingMode** specifies class loader mode for individual web module in the application. This option accepts multiple values, one per web module. For more details on web module's class loading mode see WAS InfoCenter.

Example:

    	*webModuleClassLoadingMode
    		firstWebModule.war;PARENT_FIRST
    		secondWebModule.war;PARENT_FIRST

* **applicationWSPolicySetAttachments** assures that application (provider) policy set attachment and binding exists for specified resource exists.

The syntax of this option is:

    	*applicationWSPolicySetAttachments
    		policySet;resources;binding

The policySet, resources, binding have the same meaning as in `AdminTask.createPolicySetAttachment` function.

* **clientWSPolicySetAttachments** assures that client policy set attachment and binding exist for specified resource exists.

The syntax of this option is:

    	*applicationWSPolicySetAttachments
    		policySet;resources;binding

The policySet, resources, binding have the same meaning as in `AdminTask.createPolicySetAttachment` function.

* **providerPolicySharingInfo** assures that policy sharing information is set for a service.

The syntax of this option is:

    	*applicationWSPolicySetAttachments
    		resource;sharePolicyMethods[;wsMexPolicySetName;wsMexPolicySetBinding]
    		secondWebModule.war;PARENT_FIRST

The resource, sharePolicyMethods, wsMexPolicySetName and wsMexPolicySetBinding have the same meaning as in `AdminTask.getProviderPolicySharingInfo` function.

### AdminApp options

Subsequent lines contain standard installation/update options. All the values supported by AdminApp are supported except _appname_.

The simplest category of option is a no-value flag:

    	nodeployejb

Some option may have single values:

    	asyncRequestDispatchType DISABLED

Other category of options is list of lists. Elements of the outer list are provided in separate lines, while sub-list elements are separated by semicolons. All elements, including empty ones, must be provided:

    	DataSourceFor20EJBModules
    		Increment EJB module;Increment.jar,META-INF/ejb-jar.xml;jdbc/DefaultEJBTimerDataSource;cmpBinding.perConnectionFactory;;;

### Comments

Lines which start from '#' are being treated as comments.

### Variable references

Application manifest can reference variables which are being resolved during import time. Variable can be specified in option values. Here, the value ``virtualHost`` is being referenced:

    	MapModulesToServers
    		Increment EJB module;Increment.jar,META-INF/ejb-jar.xml;$[deploymentTargets]
    		Default Web Application;DefaultWebApplication.war,WEB-INF/web.xml;$[deploymentTargets]+$[webServers]

Please note that manifest variables have nothing in common with *WebSphere variables* nor *environment variables*.

### Complete example

The complete example with options, special options, variables and comments may look as follows:

    ApplicationName path/to/application.ear
    	# special installation options start with asterisk
    	*startingWeight 100
    	# the installation options follow, option names match those from AdminApp.install / AdminApp.update
    	# list values are separated with semicolons, empty values must be provided
    	DataSourceFor20CMPBeans
    		Increment EJB module;Increment;Increment.jar,META-INF/ejb-jar.xml;jdbc/DefaultEJBTimerDataSource;cmpBinding.perConnectionFactory;;
    	# atomic (non-list) values are specified after the
    	filepermission .*\.dll=755#.*\.so=755#.*\.a=755#.*\.sl=755
    	# some options accept list of lists, please note variable references
    	MapModulesToServers
    		Increment EJB module;Increment.jar,META-INF/ejb-jar.xml;$[deploymentTargets]
    		Default Web Application;DefaultWebApplication.war,WEB-INF/web.xml;$[deploymentTargets]+$[webServers]
    	# an option without a value:
    	noprocessEmbeddedConfig
    	DataSourceFor20EJBModules
    		Increment EJB module;Increment.jar,META-INF/ejb-jar.xml;jdbc/DefaultEJBTimerDataSource;cmpBinding.perConnectionFactory;;;
    	nouseAutoLink
    	distributeApp
    	noreloadEnabled
    	asyncRequestDispatchType DISABLED
    	validateinstall warn
    	noallowDispatchRemoteInclude
    	noallowServiceRemoteInclude
    	MapRolesToUsers
    		All Role;AppDeploymentOption.No;AppDeploymentOption.No;;;AppDeploymentOption.Yes;;
    	nodeployws
    	nouseMetaDataFromBinary
    	nodeployejb
    	createMBeansForResources
    	MapWebModToVH
    		Default Web Application;DefaultWebApplication.war,WEB-INF/web.xml;$[virtualHost]
    	nopreCompileJSPs

# Configuration manifests

Configuration manifests describe structure and attribute values of configuration objects. A configuration manifest can be applied ("imported") into your WAS configuration using assuring that the configuration objects and their attributes look exactly as stated in the manifest.

Importing of manifests is idempotent, which means that the same manifests can be safely imported again and only the necessary changes will be applied:

* object which do not exist, will be created with specified attributes and their values
* if the object already exists, its attribute values will be compared with the ones listed in configuration manifest and only the ones which differ will be modified
* if the object exists and all attribute values are as specified in the manifest, no changes will be made

In short: you can safely import the same manifest over and over.

## Authoring configuration manifests

Configuration manifests are **tab-indented** files. You can create and modify
them using any text editor. They can also be exported from existing
environment using
[wdr.tools.exportConfigurationManifestToFile](reference/wdr.tools.exportConfigurationManifestToFile.html)
function.

When authoring configuration manifests, you will find `WebSphere Application And Configuration Model Documentation` useful as a reference of object types and their attributes. This reference documentation can be found `<WAS_HOME>/web/configDocs` directory.

## Configuration manifest syntax

The configuration objects

    RootObjectType1
    	*keyAttr1 key1
    	*keyAttr2 key2
    	-attr1 val1
    	-attr2 val2
    	ChildType1
    		*childKey k
    		-childAttr1 v1
    		-childAttr2 v2
    RootObjectType2
    	*keyAttr1 key1
    	*keyAttr2 key2
    	-attr1 val1
    	-attr2 val2
    	ChildType1
    		*childKey k
    		-childAttr1 v1
    		-childAttr2 v2

Complete example of `DataSource` configuration:

    Cell
    	Security
    		JAASAuthData
    			*alias Db2AuthAlias
    			-userId db2admin
    			-password db2admin
    ServerCluster
    	*name wdrCluster
    	VariableMap
    		-entries
    			VariableSubstitutionEntry
    				*symbolicName DB2_JCC_DRIVER_PATH
    				-value /opt/was/jars/db2jcc
    	JDBCProvider
    		*name TheDb2Provider
    		-providerType DB2 Using IBM JCC Driver
    		-implementationClassName com.ibm.db2.jcc.DB2XADataSource
    		-classpath ${DB2_JCC_DRIVER_PATH}/db2jcc4.jar;${DB2_JCC_DRIVER_PATH}/db2jcc_license_cu.jar
    		DataSource
    			*name MyDataSource
    			-jndiName jdbc/MyDS
    			-authDataAlias Db2AuthAlias
    			-mapping
    				MappingModule
    					-mappingConfigAlias DefaultPrincipalMapping
    					-authDataAlias Db2AuthAlias
    			-propertySet
    				J2EEResourcePropertySet
    					-resourceProperties
    						J2EEResourceProperty
    							*name databaseName
    							-value SAMPLE
    							-type java.lang.String
    						J2EEResourceProperty
    							*name serverName
    							-value db2host.example.com
    							-type java.lang.String
    						J2EEResourceProperty
    							*name portNumber
    							-value 50000
    							-type java.lang.Integer
    						J2EEResourceProperty
    							*name driverType
    							-value 4
    							-type java.lang.Integer


JVM configuration example:

    Cell
    	*name wdrCell
    	Node
    		*name wdrDMgrNode
    		Server
    			*name dmgr
    			-processDefinitions
    				JavaProcessDef
    					-jvmEntries
    						JavaVirtualMachine
    							-initialHeapSize 128
    							-maximumHeapSize 512
    	Node
    		*name wdrNode01
    		Server
    			*name nodeagent
    			-processDefinitions
    				JavaProcessDef
    					-jvmEntries
    						JavaVirtualMachine
    							-initialHeapSize 128
    							-maximumHeapSize 256

## Reuse of manifests and the manifestPath

When importing configuration or application manifests, the manifest file is being looked up in a list of directories known as `manifestPath`. If the script doesn't specify any `manifestPath`, manifest import functions will default to **reversed** Python's `sys.path`.

Both [importApplicationManifest](reference/wdr.manifest.importApplicationManifest.html) and [importConfigurationManifest](reference/wdr.manifest.importConfigurationManifest.html) functions support `manifestPath` when looking up for manifest to import.

### The `@import` and `@include` directives in configuration manifests

Manifests can import and include other manifests using `@import` and `@include` directives. Both of them work in a very similar, the only difference is that import follows the manifestPath, while include uses paths relative to including manifest.

The directives insert content of included/imported manifest at exactly the place they occur in including/importing manifest.

A practical use case for importing manifests is applying JVM properties across all JVMs in the cell. Suppose you want to configure certain set of properties on all JVMs and only certain properties on application servers. In such a case, you build a master manifest like the one below and import manifests which specify standard JVM properties and properties applicable to servers. With such structuring of manifests you avoid duplication and make your manifest even more readable and maintainable.


The main manifest:

    Cell
    	*name wdrCell
    	Node
    		*name wdrDMgrNode
    		Server
    			*name dmgr
    			-processDefinitions
    				JavaProcessDef
    					-jvmEntries
    						JavaVirtualMachine
    							-initialHeapSize 128
    							-maximumHeapSize 512
    							-systemProperties
    								@import template/standardJvmProperties.wdrc
    	Node
    		*name wdrNode01
    		Server
    			*name nodeagent
    			-processDefinitions
    				JavaProcessDef
    					-jvmEntries
    						JavaVirtualMachine
    							-initialHeapSize 128
    							-maximumHeapSize 256
    							-systemProperties
    								@import template/standardJvmProperties.wdrc
    		Server
    			*name wdrClusterMem01
    			-processDefinitions
    				JavaProcessDef
    					-jvmEntries
    						JavaVirtualMachine
    							-initialHeapSize 128
    							-maximumHeapSize 1024
    							-systemProperties
    								@import template/standardJvmProperties.wdrc
    								@import solutionAbc/appServerJvmProperties.wdrc
    	Node
    		*name wdrNode02
    		Server
    			*name nodeagent
    			-processDefinitions
    				JavaProcessDef
    					-jvmEntries
    						JavaVirtualMachine
    							-initialHeapSize 128
    							-maximumHeapSize 256
    							-systemProperties
    								@import template/standardJvmProperties.wdrc
    		Server
    			*name wdrClusterMem02
    			-processDefinitions
    				JavaProcessDef
    					-jvmEntries
    						JavaVirtualMachine
    							-initialHeapSize 128
    							-maximumHeapSize 1024
    							-systemProperties
    								@import template/standardJvmProperties.wdrc
    								@import solutionAbc/appServerJvmProperties.wdrc

Now let's take a look at imported manifests. The `template/standardJvmProperties.wdrc` defines properties that you set everywhere. The `template` directory is in your `manifestPath` and contains manifests that you reuse across different cells, kind of company standard.

    Property
    	*name com.ibm.cacheLocalHost
    	-value true
    Property
    	*name java.net.preferIPv4Stack
    	-value true
    Property
    	*name java.awt.headless
    	-value true

The other manifest being imported in the scope of application servers' JVMs is specific to your solution. Again, the `solutionAbc/appServerJvmProperties.wdrc` is resolvable in `manifestPath`. This manifest is solution-specific, you apply it only to certain configurations.

    Property
    	*name com.abc.app.specific.property
    	-value 1
    Property
    	*name sun.net.inetaddr.ttl
    	-value 3600
    Property
    	*name sun.net.inetaddr.negative.ttl
    	-value 3600
    Property
    	*name sun.net.client.defaultConnectTimeout
    	-value 1000
    Property
    	*name sun.net.client.defaultReadTimeout
    	-value 60000
    Property
    	*name sun.net.http.retryPost
    	-value false
    Property
    	*name http.keepAlive
    	-value true
    Property
    	*name http.maxConnections
    	-value 25

## Variable expansion

Configuration and application manifests perform variable substitution during import. The syntax of variable references is identical for both types of manifests. Variables (and filters, which may assist in variable expansion) are being passed to [importApplicationManifest](reference/wdr.manifest.importApplicationManifest.html) or [importConfigurationManifest](reference/wdr.manifest.importConfigurationManifest.html) functions in a Jython/Python dictionary.

### Flat dictionary

The most straightforward option is to declare all variables in a flat dictionary and reference them in the manifest:

    Cell
    	Security
    		JAASAuthData
    			*alias Db2AuthAlias
    			-userId $[databaseUser]
    			-password $[databasePassword]

The code for importing the manifest above could look as follows:

{% highlight python %}
manifestVariables = {
    'databaseUser': 'db2admin',
    'databasePassword': 'db2admin'
    }
importConfigurationManifest( 'solutionAbc/authenticationAliases.wdrc', manifestVariables )
{% endhighlight %}

### Nested dictionaries and dot-notation

As the number of variables increases, you may want to group them together in nested dictionaries. Then the manifest references them using dot-notation, where dot-separated segments are keys to dictionary entries in each level.

    Cell
    	Security
    		JAASAuthData
    			*alias Db2AuthAlias
    			-userId $[database.user]
    			-password $[database.password]

The script which imports such manifest needs to declare a nested dictionary like the one below:

{% highlight python %}
manifestVariables = {
    'database': {
        'user': 'db2admin',
        'password': 'db2admin'
        },
    'mq': {
        'user': 'mqmadm',
        'password': 'mqmadm'
        }
    }
importConfigurationManifest( 'solutionAbc/authenticationAliases.wdrc', manifestVariables )
{% endhighlight %}

### Filters

In more advanced cases it may be desirable to do some sort of processing of variables. Let's take as an example a list of deployment targets in application manifest. The following manifest references `deploymentTargets` and `webServers` variables:

    DefaultApplication ../applications/DefaultApplication.ear
    	MapModulesToServers
    		Increment EJB module;Increment.jar,META-INF/ejb-jar.xml;$[deploymentTargets]
    		Default Web Application;DefaultWebApplication.war,WEB-INF/web.xml;$[deploymentTargets]+$[webServers]

{% highlight python %}
manifestVariables = {
    'deploymentTargets': 'WebSphere:cell=wdrCell,cluster=wdrCluster',
    'webServers': 'WebSphere:cell=wdrCell,node=httpNode01,server=wdrHttpServer01+WebSphere:cell=wdrCell,node=httpNode02,server=wdrHttpServer02'
    }
importApplicationManifest( 'solutionAbc/defaultApplication.wdra', manifestVariables )
{% endhighlight %}

The `webServers` variable is not easily readable and as the complexity of the environment (number of HTTP servers) increases, the script becomes more and more difficult to maintain.

The definition of variables would be more readable if it could be specified as in the example below and then somehow converted into a string which wsadmin likes.

{% highlight python %}
manifestVariables = {
    'deploymentTargets': 'WebSphere:cell=wdrCell,cluster=wdrCluster',
    'webServers': [
            {
                'cell': 'wdrCell',
                'node': 'httpNode01',
                'server': 'wdrHttpServer01'
            }, {
                'cell': 'wdrCell',
                'node': 'httpNode02',
                'server': 'wdrHttpServer02'
            }
        ]
    }
{% endhighlight %}

Here's where filters become handy. Filter is a function which takes one argument of any type and returns a string. Filter function, once defined, must be added into variables dictionary. Then the filter can be easily referenced in a manifest, like in the example below:

    DefaultApplication ../applications/DefaultApplication.ear
    	MapModulesToServers
    		Increment EJB module;Increment.jar,META-INF/ejb-jar.xml;$[deploymentTargets]
    		Default Web Application;DefaultWebApplication.war,WEB-INF/web.xml;$[deploymentTargets]+$[webServers|makeWebServerString]

The `makeWebServerString` is a key of filter function in variables.

{% highlight python %}
def makeWebServerStringFilter( webServerList ):
    formattedWebServerList = []
    for srv in webServerList:
        formattedWebServerList.append( 'WebSphere:cell=%(cells)s,node=%(node)s,server=%(server)s' % srv )
    return '+'.join( formattedWebServerList )

manifestVariables = {
    'deploymentTargets': 'WebSphere:cell=wdrCell,cluster=wdrCluster',
    'webServers': [
            {
                'cell': 'wdrCell',
                'node': 'httpNode01',
                'server': 'wdrHttpServer01'
            }, {
                'cell': 'wdrCell',
                'node': 'httpNode02',
                'server': 'wdrHttpServer02'
            }
        ],
    'makeWebServerString': makeWebServerStringFilter
    }
importApplicationManifest( 'solutionAbc/defaultApplication.wdra', manifestVariables )
{% endhighlight %}

A more fluent Jythonist would probably shorten this function:

{% highlight python %}
def makeWebServerStringFilter( webServerList ):
    return '+'.join( [ 'WebSphere:cell=%(cells)s,node=%(node)s,server=%(server)s' % srv for srv in webServerList ] )

manifestVariables = {
    'deploymentTargets': 'WebSphere:cell=wdrCell,cluster=wdrCluster',
    'webServers': [
            {
                'cell': 'wdrCell',
                'node': 'httpNode01',
                'server': 'wdrHttpServer01'
            }, {
                'cell': 'wdrCell',
                'node': 'httpNode02',
                'server': 'wdrHttpServer02'
            }
        ],
    'makeWebServerString': makeWebServerStringFilter
    }
importApplicationManifest( 'solutionAbc/defaultApplication.wdra', manifestVariables )
{% endhighlight %}

.. or even use lambda form:

{% highlight python %}
manifestVariables = {
    'deploymentTargets': 'WebSphere:cell=wdrCell,cluster=wdrCluster',
    'webServers': [
            {
                'cell': 'wdrCell',
                'node': 'httpNode01',
                'server': 'wdrHttpServer01'
            }, {
                'cell': 'wdrCell',
                'node': 'httpNode02',
                'server': 'wdrHttpServer02'
            }
        ],
    'makeWebServerString': lambda ws : '+'.join( [ 'WebSphere:cell=%(cells)s,node=%(node)s,server=%(server)s' % s for s in ws ] )
    }
importApplicationManifest( 'solutionAbc/defaultApplication.wdra', manifestVariables )
{% endhighlight %}

## Best practices

### Use variables

Variables help you build portable manifests. The same manifest can be applied to different environments without modifications. Properly parametrized manifest can be used across all of your environments, incuding developer's workstation, all test environments, production, DR, etc.

### Use name-based keys whenever possible

The process of importing a manifest to WAS configuration was optimized for object lookups based on `name` attribute. Other types of lookup do work correctly, but they are significantly slower. If possible, avoid non-name-based keys and use them only for configuration objects which do not have `name` attribute (like VariableSubstitutionEntry, HostAlias, JAASAuthData, NamedEndPoint, etc).

### Keep your solution in a version-control repository

If your organisation has an application development team, try using the same type of version control system they use. Consider sharing your automation repository with them.

No developers in your company? Version control allows you to safely share your code with rest of your team.

One-man-team? You may still consider version-control. This is probably the best way to deliver your scripts to continuous integration server, gives you a backup and history of your solution.

### Make use of manifestPath with import and include directives

The `manifestPath` together with `@import` and `@include` directives allow for reuse of manifests and scripts and sharing generic setting while still allowing project (or product) specific settings. By adding multiple paths to `manifestPath`, the `@import` directive, `importConfigurationManifest` and `importApplicationManifest` functions can find manifests in multiple directories. Based on that you can build reusable libraries of manifests and scripts.
