---
layout: page
tagline: WDR Reference
title: ConfigObject
---

`ConfigObject` instance represents a configuration object in WAS config repository. Object attributes can be accessed using dot-notation.

```python
# retrieving Cell object and printing some of its attributes
cell = getid1('/Cell:/')
print 'Cell name: %s' % cell.name
print 'Cell type: %s' % cell.cellType
# retrieving Server object, then accessing and modifying one attribute
srv = getid1('/Server:wdrServer/')
print 'Original JVM arguments: %s' % srv.processDefinitions[0].jvmEntries[0].genericJvmArguments
srv.processDefinitions[0].jvmEntries[0].genericJvmArguments = '-Xquickstart -Xverbosegclog:/tmp/verbosegc'
print 'New JVM arguments: %s' % srv.processDefinitions[0].jvmEntries[0].genericJvmArguments
```

`ConfigObject` can be converted into a string using `str` function, which may be useful in scripts/solutions which mix WDR and non-WDR code:

```python
cell = getid1('/Cell:/')
print AdminConfig.showAttribute(str(cell), 'name')
```

## Methods

* [assure](wdr.config.ConfigObject.assure.html)
* [create](wdr.config.ConfigObject.create.html)
* [getAllAttributes](wdr.config.ConfigObject.getAllAttributes.html)
* [listConfigObjects](wdr.config.ConfigObject.listConfigObjects.html)
* [modify](wdr.config.ConfigObject.modify.html)
* [remove](wdr.config.ConfigObject.remove.html)
* [unset](wdr.config.ConfigObject.unset.html)
