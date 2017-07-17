---
layout: default
tagline: Simpler WebSphere Application Server Scripting
---


# Features

* makes wsadmin scripts more "Pythonic" and readable and maintainable in result
* improves environment consistency with [application and configuration manifests](manifests.html)
* allows interoperability with "legacy" Jython scripts including mixing of classic wsadmin and WDR code
* works with currently supported WSAS versions (6.1 and later)
* Open Source, Apache License, Version 2.0

# Some highlights

The following examples implement similar scenarios with and without WDR.

## Listing all nodes and servers

With WDR:

```python
for node in listConfigObjects('Node'):
    print node.name
    for server in node.listConfigObjects('Server'):
        print " " + server.name
```

Without WDR:

```python
for node in AdminConfig.listConfigObjects('Node').splitlines():
    print AdminConfig.showAttribute(node, 'name')
    for server in AdminConfig.listConfigObjects('Server', node).splitlines():
        print ' ' + AdminConfig.showAttribute(server, 'name')
```

## Modifying configuration objects

With WDR:

```python
jvm = getid1('/Server:dmgr/JavaProcessDef:/JavaVirtualMachine:/')
jvm.initialHeapSize = 64
jvm.maximumHeapSize = 512
```

Without WDR:

```python
jvms = AdminConfig.getid('/Server:dmgr/JavaProcessDef:/JavaVirtualMachine:/').splitlines()
if len(jvms) != 1:
    # need to handle special conditions
    raise Exception("configuration object not found or multiple objects found")
jvm = jmvs[0]
AdminConfig.modify(jvm, [ [ 'initialHeapSize', 64 ] ])
AdminConfig.modify(jvm, [ [ 'maximumHeapSize', 512 ] ])
```

## Invoking MBean operations

With WDR:

```python
dmgr = getMBean1(type='Server', process='dmgr')
dmgr.restart()
```

Without WDR:

```python
dmgrs = AdminControl.queryNames( 'WebSphere:*,type=Server,name=dmgr' ).splitlines()
if len(dmgrs) != 1:
    # need to handle special conditions
    raise Exception("MBean not found or multiple MBeans found")
dmgr = dmgrs[0]
AdminControl.invoke(dmgr, 'restart')
```

## Configuring standard JVM attributes with a configuration manifest

You probably have some set of "standard" JVM settings that you always want to apply to all your environments. How many times you realize that it was not applied on some server? It would be nice to have a mechanism which automatically applies it for all your application servers.

This script will do it for you:

```python
for node in listConfigObjects('Node'):
    for server in node.listConfigObjects('Server'):
        if server.serverType == 'APPLICATION_SERVER':
            manifestVariables = { 'nodeName': node.name, 'serverName': server.name }
            importConfigurationManifest( 'standardJVM.wdrc', manifestVariables )
```

Using a nested loop, the script iterates all application servers and applies the following manifest to all of them. The manifest references `nodeName` and `serverName` variables which are being passed as `manifestVariables` dictionary to the `importConfigurationManifest` function.

The content of the manifest file ('standardJVM.wdr') referenced by the above script:

    Node
    	*name $[nodeName]
    	Server
    		*name $[serverName]
    		-processDefinitions
    			JavaProcessDef
    				-environment
    					Property
    						*name JAVA_DUMP_OPTS
    						-value ONOUTOFMEMORY(JAVADUMP,SYSDUMP[1]),ONANYSIGNAL(JAVADUMP)
    					Property
    						*name IBM_JAVACOREDIR
    						-value /shared/dumps/$[nodeName]/$[serverName]
    					Property
    						*name IBM_COREDIR
    						-value /shared/dumps/$[nodeName]/$[serverName]
    				-jvmEntries
    					JavaVirtualMachine
    						-genericJvmArguments -Xverbosegclog:${SERVER_LOG_ROOT}/gc.log,9,1000
    						-systemProperties
    							Property
    								*name com.ibm.cacheLocalHost
    								-value true
    							Property
    								*name java.net.preferIPv4Stack
    								-value true
    							Property
    								*name java.awt.headless
    								-value true
    							Property
    								*name sun.net.inetaddr.ttl
    								-value 3600
    							Property
    								*name sun.net.inetaddr.negative.ttl
    								-value 3600
    							Property
    								*name sun.net.client.defaultConnectTimeout
    								-value 60000
    							Property
    								*name sun.net.client.defaultReadTimeout
    								-value 600000
    							Property
    								*name sun.net.http.retryPost
    								-value false
    							Property
    								*name http.keepAlive
    								-value true
    							Property
    								*name http.maxConnections
    								-value 15

Without WDR:

... it would be just way too complex. Those who tried it, know what it means. Those who didn't, wouldn't be interested anyway.

# Get the code!

The source code is hosted on [WDR GitHub page](https://github.com/WDR/WDR).
You can clone the repository using Git client or download the [latest snapshot](https://github.com/WDR/WDR/archive/master.zip).

# Documentation

[Getting started](getting_started.html)

[Installing WDR](install.html)

[Reference](reference/index.html)
