---
layout: page
tagline: WDR Reference
title: wdr.tools.exportApplicationManifestToFile
---


    wdr.tools.exportApplicationManifestToFile( <appName>, <filename> [, customTaskProcessors] )

Generates application manifest for existing deployment.

## Arguments

_appName_

application name, as seen in AdminConsole

_filename_

file name of exported manifests

_customTaskProcessors_

optional argument; a dictionary of task processors - components being
responsible for generation of certain parts of application manifest; defaults
to empty dictionary; this feature will evolve in the future

## Result

None
