---
layout: page
title: Getting started with WDR
short_title: Getting started
---

This page should help you get your feet wet with WDR and learn some basic functionality of the library. Not all functions and objects have been described here, for a full list check Reference Reference.

# Installation

Depending on your needs, you may choose one of the following installation options:

* Adding WDR to your existing WebSphere installation

Use this option if you run your automation scripts on the same server your WebSphere Application Server is running.

See [server installation](install_server.html) for details.

* Installing WDR with WebSphere Application Server wsadmin thin client

Use this option if you run your scripts on a central automation server to manage multiple WAS environments.

See [thin client installation](install_thin_client.html) for details.

# First steps

WDR provides you with a set of functions and objects to work with WAS configuration, runtime and applications. The entire code is split into 3 main modules similarly to wsadmin model: config, control and app. The main goal of the framework is to help you make your scripts be more Pythonic. The fundamental rules of the API are:

* Use Python types wherever possible. For example, lists must be treated lists, no more splitline().
* Allow dot-notation wherever possible. No more "showAttribute", "modify", "getAttribute", "invoke".
* Allow accessing ALL configuration/runtime types, attributes and operations by doing live introspection of WAS object.
* Keep interoperability with "classic wsadmin" to allow mixing of WDR and non-WDR code in the same script.

## Working with configuration

We are going to do some non-desctructive configuration operations first

### Finding objects and accessing their attributes

```python
firstProvider = listConfigObjects('JDBCProvider')[0]
print 'name: ' + firstProvider.name
print 'description: ' + firstProvider.description
reset()
```

The above script:

* extracts list of JDBCProvider objects, retrieves first element from the list and assigns it to `firstProvider` variable
* prints 'name' attribute of JDBCProvider object
* prints 'description' attribute
* discards the workspace **it's a good practice to always reset() or save() to avoid garbage in WAS temporary directories**

The output of that script should look similarly to this one:

    name: Derby JDBC Provider (XA)
    description: Built-in Derby JDBC Provider (XA)

Our next script will modify that provider.

#### Modifying configuration object's attribute

```python
firstProvider = listConfigObjects('JDBCProvider')[0]
firstProvider.description = 'This description was modified with WDR script'
save()
sync()
```

The example is self-explanatory. You can check with AdminConsole if the description has changed.

#### Creating a new object

This tiny script creates a new DataSource and configures maximum size of its connection pool:

```python
firstProvider = listConfigObjects('JDBCProvider')[0]
newds = firstProvider.create('DataSource', name='NewlyCreatedDataSource', jndiName='jdbc/NewDataSource', description='... a word of description ...')
newds.connectionPool.maxConnections = 15
save()
sync()
```

#### Deleting object from configuration repository

Now we'll delete the dataSource we created previously. It also demonstrates some less-obvious behaviour of WDR/wsadmin

```python
ds = getid1('/DataSource:NewlyCreatedDataSource/').remove()
# the 'remove' method returns a reference to removed object
# if we discard changes, we can still work with that object
reset()
ds.description = ''
# ... but that was only a digression, we really want to delete it and save changes
# so: we remove it (again), save and synchronize changes
ds.remove()
save()
sync()
```

### Working with WAS runtime

Accessing MBean attributes and invoking MBean operations is another area where WDR helps you make your script more readable and maintainable.

#### MBean vs JMXMBean

The library provides you with two similar classes for working with JMX MBeans: `MBean` and `JMXMBean`. In most of the cases (the simpler ones) the `MBean` class should be simpler to use yet sufficient in functionality. In some cases you may need to resort to `JMXMBean`, especially if you need to deal with complex Java types in attributes or operation arguments/results. The use of `MBean` class is strongly preferred for simplicity, you should consider `JMXMBean` class only if some tasks is not feasible with `MBean`.

#### Using MBean objects

In this section we'll use `MBean` instances to access 'simple type' JMX attributes and invoke JMX operations accepting 'simple type' arguments and returning 'simple type' results.

##### Accessing MBean attributes

Not surprisingly, accessing JMX MBean attributes with WDR is achievable with familiar dot-notation.

```python
dmgr = getMBean1(type='Server', name='dmgr')
print 'state:                 ' + dmgr.state
print 'pid:                   ' + dmgr.pid
print 'threadMonitorInterval: ' + dmgr.threadMonitorInterval
```

Similarly, you can modify JXM MBean attributes using dot-notation and regular Python assignment.

```python
dmgr = getMBean1(type='Server', name='dmgr')
dmgr.threadMonitorInterval = 60

# JMX MBean attributes behave like normal Python object attributes:
tp = getMBean1(type='ThreadPool', name='WebContainer', process='dmgr')
tp.maximumSize += 10
```

##### Invoking MBean operations

Invoking an MBean operation looks like regular method invocation on a Python object.

```python
dmgr = getMBean1(type='Server', name='dmgr')
dmgr.restart()
# the Deployment Manager is restarting, hold on before invoking next operations
```

Operations accept and return regular Python types.

```python
appMgr = getMBean1(type='ApplicationManager', process='dmgr')
appMgr.stopApplication('isclite')
# AdminConsole is stopped now. Go and see!
appMgr.startApplication('isclite')
# AdminConsole is running again
```

##### Special note on overloaded operations

Some MBeans overload JMX operations, for example `NodeAgent` has two different versions of 'launchProcess':

* Boolean launchProcess(String processName)
* Boolean launchProcess(String processName, Integer timeout)

MBean class, based on provided argument list, tries to match your call to proper JMX operation. If the actual call and the operation signature have the same number of arguments, a match is successful. Should that mechanism be insufficient (when two or more operations accept the same number of arguments), you'll need to resolve that ambiguity by secifying operation's full signature.

```python
nodeAgent = getMBean1(type='NodeAgent', node='wdrNode01')
nodeAgent.launchProcess[ ['java.lang.String', 'java.lang.Integer'] ] ( 'wdrClusterMem01', 180 )
#                      ^ ^       ^                    ^          ^ ^
#                              this is where the magic comes
```

The above mechanism works for all operations, even those which are not overloaded. For readability of your scripts, you'll probably avoid it unless it's really necessary to disambiguate.
