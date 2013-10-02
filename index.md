---
layout: page
title: WDR
tagline: Simpler WebSphere Application Server Scripting
---
Jython library which aims at simplifying WebSphere scripting.

# Features

* makes wsadmin scripts more "Pythonic" and readable and maintainable in result
* improves environment consistency with [application and configuration manifests](manifests.html)
* allows interoperability with "legacy" Jython scripts including mixing of classic wsadmin and WDR code
* works with currently supported WSAS versions (6.1 and later)
* Open Source, Apache License, Version 2.0

# Some highlights

The following examples implement similar scenarios with and without WDR.

## Listing all nodes and servers

{% highlight python %}
for node in listConfigObjects('Node'):
    print node.name
    for server in node.listConfigObjects('Server'):
        print " " + server.name
{% endhighlight %}

The same code in wsadmin would look like as follows:

{% highlight python %}
for node in AdminConfig.listConfigObjects('Node').splitlines():
    print AdminConfig.showAttribute(node, 'name')
    for server in AdminConfig.listConfigObjects('Server', node).splitlines():
        print ' ' + AdminConfig.showAttribute(server, 'name')
{% endhighlight %}

## Modifying configuration objects

{% highlight python %}
jvm = getid1('/Server:dmgr/JavaProcessDef:/JavaVirtualMachine:/')
jvm.initialHeapSize = 64
jvm.maximumHeapSize = 512
{% endhighlight %}

## Invoking MBean operations

{% highlight python %}
dmgr = getMBean1(type='Server', process='dmgr')
dmgr.restart()
{% endhighlight %}

# Get the code

The source code is hosted on [WDR GitHub page](https://github.com/WDR/WDR).
You can clone the repository using Git client or download the [latest snapshot](https://github.com/WDR/WDR/archive/master.zip).

# Documentation

[Getting started](getting_started.html)

[Installing WDR](install.html)

[Reference](reference/index.html)
