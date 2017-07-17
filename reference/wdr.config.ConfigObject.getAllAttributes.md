---
layout: page
tagline: WDR Reference
title: ConfigObject.getAllAttributes
---

Retrieves all attributes with their values in one call.

    obj.getAllAttributes()

## Result

A dictionary where keys are attribute names and values are the actual values of these attributes.

## Examples

* Retrieving all attributes of DataSource's ConnectionPool

```python
print getid1('/DataSource:Default Datasource/').connectionPool.getAllAttributes()
```

    {'stuckThreshold': 0, 'unusedTimeout': 1800L, 'maxConnections': 10, 'stuckTimerTime': 0, 'testConnectionInterval': 0, 'properties': [], 'minConnections': 1, 'surgeThreshold': -1, 'connectionTimeout': 180L, 'purgePolicy': 'EntirePool', 'surgeCreationInterval': 0, 'numberOfUnsharedPoolPartitions': 0, 'stuckTime': 0, 'agedTimeout': 0L, 'reapTime': 180L, 'testConnection': 0, 'numberOfSharedPoolPartitions': 0, 'freePoolDistributionTableSize': 0, 'numberOfFreePoolPartitions': 0}
