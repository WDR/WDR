---
layout: page
title: WDR
tagline: Simpler WebSphere Application Server Scripting
---
{% include JB/setup %}

Jython library which aims at simplifying WebSphere scripting.

# Features

* makes wsadmin scripts more "Pythonic" and readable and maintainable in result
* allows interoperability with "legacy" Jython scripts including mixing of classic wsadmin and WDR code
* works with currently supported WSAS versions (6.1 and later)
* Open Source, Apache License, Version 2.0

# Some highlights

The following examples implement similar scenarios with and without WDR.

## Listing all nodes and servers

{% highlight python %}
for node in list('Node'):
    print node.name
    for server in node.list('Server'):
        print " " + server.name
{% endhighlight %}

The same code in wsadmin would look like as follows:

{% highlight python %}
for node in AdminConfig.list('Node').splitlines():
    print AdminConfig.showAttribute(node, 'name')
    for server in AdminConfig.list('Server', node).splitlines():
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

# Documentation

[Setting started](getting_started.html)

[Installing WDR](install.html)

[Reference](reference/index.html)
