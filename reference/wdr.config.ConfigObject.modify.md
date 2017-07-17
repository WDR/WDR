---
layout: page
tagline: WDR Reference
title: ConfigObject.modify
---

Modifies several object attributes in one call.

    obj.modify( <attributes> )

## Arguments

_attributes_

attributes that have to modified

## Result

Reference to the configuration object [wdr.config.ConfigObject](wdr.config.ConfigObject.class.html) being modified.

## Examples

* Changing two DataSource's ConnectionPool parameters in one call:

```python
getid1('/DataSource:Default Datasource/').connectionPool.modify(connectionTimeout=10, maxConnections=30)
```
