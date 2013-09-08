---
layout: page
tagline: WDR Reference
title: MBean
---

Represents a Managed Bean registered in one of accessible WebSphere processes. Instances of this class can be created using:

* [queryMBeans](wdr.control.queryMBeans.html)
* [getMBean](wdr.control.getMBean.html)
* [getMBean1](wdr.control.getMBean1.html)
* [mbean](wdr.control.mbean.html)
* [mbeans](wdr.control.mbeans.html)

`wdr.control.MBean` class exposes JMX attributes and operations to WDR/wsadmin scripts. Both attributes and operations can be accessed using convenient dot-notation.
Attribute values and operation arguments/results undergo standard wsadmin conversions, therefore use of this class usually results in more readable and maintainable scripts.

`wdr.control.MBean` class should be used in favour of [wdr.control.JMXMBean](wdr.control.JMXMBean.class.html) class whenever possible.

#### Accessing MBean attributes

Attributes can be accessed using dot-notation. The following example finds 'WebContainer' thread pool in the deployment manager and changes maximum number of threads from 50 to 30:

{% highlight python %}
tp = getMBean1(type='ThreadPool', name='WebContainer', node='wdrDMgrNode', process='dmgr')
print 'Maximum size of thread pool is: %d' % tp.maximumSize
tp.maximumSize = 30
print 'Maximum size of thread pool is: %d' % tp.maximumSize
{% endhighlight %}

    Maximum size of thread pool is: 50
    Maximum size of thread pool is: 30

#### Invoking MBean operations

Operations can be invoked on MBean instances using dot-notation:

{% highlight python %}
jvm = getMBean1(type='JVM', node='wdrDMgrNode', process='dmgr')
jvm.dumpThreads()
{% endhighlight %}

Some MBeans come with overloaded operations (more than one operation with the same name and different argument list). 'NodeAgent' MBean is such an example. According to that MBean's documentation, operation 'launchProcess' is available in 2 flavours:

_java.lang.Boolean launchProcess(java.lang.String processName)_

launch a new server process and wait for process initialization to complete

_java.lang.Boolean launchProcess(java.lang.String processName, java.lang.Integer timeout)_

launch a new server process and specify the timeout interval to wait for server initialization to complete

`wdr.control.MBean` class, based on parameter list, tries to figure out which operation should be invoked. In the following example, the frist (one-argument) version is being invoked.

{% highlight python %}
na = getMBean1(type='NodeAgent', node='wdrNode01')
print na.launchProcess('wdrServer')
{% endhighlight %}

In this example, the `na` object decided to invoke the second version of `launchProcess` operation because 2 arguments have been provided.
{% highlight python %}
na = getMBean1(type='NodeAgent', node='wdrNode01')
print na.launchProcess('wdrServer', 300)
{% endhighlight %}

In cases when you find the above 'guessing' mechanism ambiguous, you may prefer to explicitly advise `MBean` class which operation you want to invoke. Adding list of types in square brackets after operation name (before argument list) eliminates any ambiguity.

This example instructs `MBean` class to invoke one-argument operation with 'java.lang.String' argument:

{% highlight python %}
na = getMBean1(type='NodeAgent', node='wdrNode01')
na.launchProcess[ ['java.lang.String'] ]('wdrServer')
{% endhighlight %}

Whereas this example forces `MBean` class to use two-argument operation:

{% highlight python %}
na = getMBean1(type='NodeAgent', node='wdrNode01')
na.launchProcess[ ['java.lang.String', 'java.lang.Integer'] ]('wdrServer', 300)
{% endhighlight %}
