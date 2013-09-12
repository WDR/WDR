---
layout: page
title: Application and configuration manifests
---
One of the main motivations for automating management of WebSphere is to keep multiple environments in sync.
This goal is difficult to achieve using just scripts. The challenges are:

* idempotency
* variable externalization
* change review

WDR tries to address these challenges with application and configuration manifests.
The concept of manifests was borrowed from system configuration management tools:
[Ansible](http://www.ansibleworks.com/), [Chef](http://www.opscode.com/), [Puppet](http://www.puppetlabs.com/)
and [others](http://en.wikipedia.org/wiki/Comparison_of_open_source_configuration_management_software).

**Idempotency**

> In short: making sure that the same configuration can be safely applied over and over without breaking anything. Manifests describe the desired state of the resource. The process of loading of manifest determines what changes (if any) are necessary and performs these changes.

**Variable externalization**

> The structure of configuration objects and the deployment process are generic and do not change between different staging environments.
> The variable parts are stored in separate files.

**Change review**

> Possibility of comparing different versions of configurations or deployments and identifying the differences. Manifests are meant to be more readable and diff-friendly than scripts. They are also more restricted than scripts: application manifest may only install/update applications, configuration manifest may only create/modify configuration objects.

Application & configuration manifests are tab-indented text files. They can be imported into WAS environment using [loadApplications](reference/wdr.manifest.loadApplications.html) or [loadConfiguration](reference/wdr.manifest.loadConfiguration.html) functions. Manifests may contain variable references, the actual values of these variables are being expanded during the import process.

> WDR manifests MUST be tab-indented.
> The design decision to not use YAML, JSON or other standard format was dictated by [Jython 2.1](jython21.html) being installed with WAS by default.
> The choice of supported text-processing libraries is very limited in that version of Jython.
> > Actually, there is no choice. One must develop a parser from scratch in Jython 2.1. Nobody supports Python 2.1 & Jython 2.1 any more.

# Application manifests

The application manifests describe application deployment options. Manifest loading process detects changes made to application binaries and the manifest itself and, depending on the result of comparisons, installs the application, updates it or simply skips changes.

## Creating application manifests

Application manifests can be edited manually or generated from "command assistance" logs by [wdr.tools.ManifestGenerationAdminApp](reference/wdr.tools.ManifestGenerationAdminApp.class.html) object.

Future versions of WDR may support generation of application manifests from existing deployments.

## Importing application manifests

Application manifests can be loaded using [wdr.manifest.loadApplications](reference/wdr.manifest.loadApplications.html) functions.

## Application manifest syntax

An example application manifest may look as follows

    DefaultApplication /opt/IBM/WebSphere/AppServer/installableApps/DefaultApplication.ear
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

The first line of the manifest contains application name (as visible in AdminConsole) and path to EAR file. The path may be either absolute or relative to current directory. Note that the first line is not indented.

    ApplicationName /path/to/application.ear

### WDR-specific options

Application manifest may contain WDR-specific application installation/update options. They syntax is similar to standard AdminApp options described below. Names of special options have to be prefixed with asterisk.

Currently, only one special option is supported by WDR. The list will be extended in subsequent releases:

* **startingWeight** specifies the startup weight of the application. More details on staring weight can be found in WAS InfoCenter.

Example:

    	*startingWeight 100

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

### Complete example

The complete example with options, special options, variables and comments may look as follows:

    ApplicationName /path/to/application.ear
    	# special installation options start with asterisk (there is only "startingWeight" for now)
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

