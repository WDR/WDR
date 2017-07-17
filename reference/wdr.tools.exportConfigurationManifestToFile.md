---
layout: page
tagline: WDR Reference
title: wdr.tools.exportConfigurationManifestToFile
---

    wdr.tools.exportConfigurationManifestToFile( <configObjects>, <filename>, <exportSets>*)

Generates configuration manifests from existing configuration.

The exported manifest file will contain information about all objects
specified in `configObjects` argument and optionally child objects.

The behaviour of this function depends heavily on `exportSets` argument, which
specifies which types of objects will be exported, together with attributes of
those objects. A set of predefined exportSets exists in `wdr.export_sets`
module. In most cases, the `wdr.export_sets.all` exportSet is going to be most
appropriate.

## Arguments

_configObjects_

list of ConfigObject instances

_filename_

file name of exported manifest

_exportSets_

list of dictionaries specifying which types of objects and which attributes
need to be exported

## Result

None

## Examples

* Export of all clusters, together with resources defined in that cluster:

```python
wdr.tools.exportConfigurationManifestToFile(getid('/ServerCluster:/'), 'clusters.wdrc', wdr.export_sets.all)
```
