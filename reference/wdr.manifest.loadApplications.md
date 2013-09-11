---
layout: page
tagline: WDR Reference
title: loadApplications
---

    loadApplications( <applicationManifestFilename>, <variables> )

Loads application manifest and installs/updates application.

Application manifests are simple tab-indented files describing application install/update options. They can be created manually or generated
using [ManifestGenerationAdminApp](wdr.tools.ManifestGenerationAdminApp.class.html).

The ``loadApplications`` function:

* parses the input manifest file
* substitutes variable references with their values
* for each application listed in the manifest, it calculates checksum of application deployment options and the actual application archive
* checksums are being compared with checksums saved in configuration during previous deployment
* if the application has not been deployed yet, it is being installed
* if the application was deployed before and checksums do not match the ones stored in configuration, the application is being updated
* if the application was deployed before and checksums in WAS configuration match checksums calculated above, the install/update step is being skipped
* if application was installed/updated, its manifest & EAR checksum is being saved in WAS configuration as custom property of the deployment

The deployment checksums used by ``loadApplications`` function are not visible in AdminConsole. It is possible to access them using a scrtipt:

{% highlight python %}
appName = 'DefaultApplication'
checksums = getid1('/Deployment:%s/ApplicationDeployment:/Property:wdr.checksum/' % appName).value

print 'Checksum of %s is %s' % (appName, checksums)
{% endhighlight %}

_Installing or updating the application via AdminConsole, wsadmin ``AdminApp.install`` or ``AdminApp.update`` will not generate ``wdr.checksum`` property._

> Application manifest MUST be tab-indented.
> The design decision to not use YAML, JSON or other standard format was dictated by [Jython 2.1](../jython21.html) being installed with WAS by default.
> The choice of supported text-processing libraries is very limited in that version of Jython.
> > Actually, there is no choice at all. One must develop a parser from scratch in Jython 2.1.

#### Arguments

_applicationManifestFilename_

application manifest file name with fully-qualified or relative path

_variables_

dictionary of variables used in the manifest

#### Result

List of application names installed or updated during manifest processing.

#### Examples

The example demonstrates installing or updating the ``DefaultApplication`` provided with WebSphere Application Server.

The application manifest may look as follows:

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

The manifest above was created using [ManifestGenerationAdminApp](wdr.tools.ManifestGenerationAdminApp.class.html) class.

Please note references to ``$[deploymentTargets]``, ``$[webServers]`` and ``$[virtualHost]`` variable references.
The actual values of these variables are being passed as a dictionary to ``loadApplications`` call:

{% highlight python %}
# these environment-specific values should be loaded from external file/script:
cellName = 'wdrCell'
clusterName = 'wdrCluster'
webServers = [ [ 'webServerNode01', 'webServer01' ], [ 'webServerNode02', 'webServer02' ] ]
virtualHost = 'wdr_host'
try:
    variables = {}
    variables['virtualHost'] = virtualHost
    # store 'WebSphere:cell=wdrCell,cluster=wdrCluster' under 'deploymentTargets' key
    variables[ 'deploymentTargets' ] = 'WebSphere:cell=%s,cluster=%s' % ( cellName, clusterName )
    # the following line will store 'webServers' entry with value of:
    # 'WebSphere:node=webServerNode01,server=webServer01+WebSphere:node=webServerNode02,server=webServer02'
    variables[ 'webServers' ] = '+'.join( [ 'WebSphere:node=%s,server=%s' % tuple(ws) for ws in webServers ] )
    loadApplications('DefaultApplication.wdra', variables)
    save()
    sync()
finally:
    reset()
{% endhighlight %}
