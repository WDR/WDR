---
layout: page
tagline: WDR Reference
title: wdr.tools.exportApplicationManifestToFile
---


    wdr.tools.exportApplicationManifestToFile( <appName>, <filename> [, customTaskProcessors] )

Generates application manifest for existing deployment.

#### Arguments

_appName_

application name, as seen in AdminConsole

_filename_

file name of exported manifests

_customTaskProcessors_

optional argument; a dictionary of task processors - components being responsible for generation of certain parts of application manifest; defaults to empty dictionary; this feature is subject to change in the future

#### Result

None

#### See also

* [getMBean](wdr.control.getMBean.html)
* [getMBean1](wdr.control.getMBean1.html)
* [getJMXMBean](wdr.control.getJMXMBean.html)
* [getJMXMBean1](wdr.control.getJMXMBean1.html)
* [queryJMXMBeans](wdr.control.queryJMXMBeans.html)
