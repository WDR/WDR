WDR
===

Jython library which aims to greatly simplify WebSphere scripting.

# Features
* makes wsadmin scripts more "Pythonic" and readable and maintainable in result
* allows interoperability with "legacy" Jython scripts including mixing of classic wsadmin and WDR code
* works with currently supported WSAS versions (6.1 and later)
* Open Source, Apache License, Version 2.0

# Some highlights

## Listing nodes and servers available in configuration

```python
for node in list('Node'):
    print node.name
    for server in node.list('Server'):
        print " " + server.name
```

The same code in wsadmin would look like as follows:
```python
for node in AdminConfig.list('Node').splitlines():
    print AdminConfig.showAttribute(node, 'name')
    for server in AdminConfig.list('Server', node).splitlines():
        print ' ' + AdminConfig.showAttribute(server, 'name')
```
## Modifying configuration objects

```python
jvm = getid1('/Server:dmgr/JavaProcessDef:/JavaVirtualMachine:/')
jvm.initialHeapSize = 64
jvm.maximumHeapSize = 512
```

## Invoking MBean operations

```python
dmgr = getMBean1(type='Server', process='dmgr')
dmgr.restart()
```

# Getting started

* Clone the latest repository with `git clone https://github.com/WDR/WDR.git`
* run wsadmin with 
 - `-profile $WDR_HOME/profile.py`
 - `-javaoption "-Dpython.path=$WDR_HOME"`

# Visit WDR home page for more...

For more documentation and examples check [WDR home page](http://wdr.github.io/WDR/). 

