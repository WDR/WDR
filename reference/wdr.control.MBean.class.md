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

## Accessing MBean attributes

Attributes can be accessed using dot-notation. The following example finds 'WebContainer' thread pool in the deployment manager and changes maximum number of threads from 50 to 30:

```python
tp = getMBean1(type='ThreadPool', name='WebContainer', node='wdrDMgrNode', process='dmgr')
print 'Maximum size of thread pool is: %d' % tp.maximumSize
tp.maximumSize = 30
print 'Maximum size of thread pool is: %d' % tp.maximumSize
```

    Maximum size of thread pool is: 50
    Maximum size of thread pool is: 30

## Invoking MBean operations

Operations can be invoked on MBean instances using dot-notation:

```python
jvm = getMBean1(type='JVM', node='wdrDMgrNode', process='dmgr')
jvm.dumpThreads()
```

Some MBeans come with overloaded operations (more than one operation with the same name and different argument list). 'NodeAgent' MBean is such an example. According to that MBean's documentation, operation 'launchProcess' is available in 2 flavours:

_java.lang.Boolean launchProcess(java.lang.String processName)_

launch a new server process and wait for process initialization to complete

_java.lang.Boolean launchProcess(java.lang.String processName, java.lang.Integer timeout)_

launch a new server process and specify the timeout interval to wait for server initialization to complete

`wdr.control.MBean` class, based on parameter list, tries to figure out which operation should be invoked. In the following example, the frist (one-argument) version is being invoked.

```python
na = getMBean1(type='NodeAgent', node='wdrNode01')
print na.launchProcess('wdrServer')
```

In this example, the `na` object decided to invoke the second version of `launchProcess` operation because 2 arguments have been provided.

```python
na = getMBean1(type='NodeAgent', node='wdrNode01')
print na.launchProcess('wdrServer', 300)
```

In cases when you find the above 'guessing' mechanism ambiguous, you may prefer to explicitly advise `MBean` class which operation you want to invoke. Adding list of types in square brackets after operation name (before argument list) eliminates any ambiguity.

This example instructs `MBean` class to invoke one-argument operation with 'java.lang.String' argument:

```python
na = getMBean1(type='NodeAgent', node='wdrNode01')
na.launchProcess[ ['java.lang.String'] ]('wdrServer')
```

Whereas this example forces `MBean` class to use two-argument operation:

```python
na = getMBean1(type='NodeAgent', node='wdrNode01')
na.launchProcess[ ['java.lang.String', 'java.lang.Integer'] ]('wdrServer', 300)
```

## JMX notification support

MBean's `waitForNotification` method allow the script to wait for JMX notifications for a specified amount of time. The syntax is:

    waitForNotification( [<typeOrTypes> [, <propertiesOrPropertiesList> [, timeout = 300.0] ] ] ):

The arguments (all optional) are:

_typeOrTypes_

string, list of strings or tuple of strings containing names of notifications the function should wait for

_propertiesOrPropertiesList_

dictionary or a list of dictionaries describing properties of the notification the function should wait for

_timeout_

maximum number of seconds the function will wait for notification

The return value is the notification received or a value of None in case of timeout.

A practical example is a function which starts an application server process:

```python
def startProcess(node, process, timeout):
    # finding the nodeagent
    nodeAgent = getMBean1(type='NodeAgent', node=node)
    # requesting the nodeagent to launch the process; the second argument is timeout
    # value of 1 means that launchProcess will block only for 1 second
    nodeAgent.launchProcess(process, 1)
    # waiting for notification meeting the following criteria:
    # - type of 'websphere.process.running' or 'websphere.process.failed'
    # - processName property equal to application server's name
    notification = nodeAgent.waitForNotification(('websphere.process.running', 'websphere.process.failed'), {'processName': process}, timeout)
    # the notification may be None if the notification hasn't been received within timeout
    if (notification is None) or (notification.type != 'websphere.process.running'):
        raise Exception( 'server %s / %s failed to start' % (node, process) )
    print 'started process %s / %s', node, process
```
