---
layout: page
tagline: WDR Reference
title: importConfigurationManifest
---

    importConfigurationManifest( <filename> [, <variables> [, <manifestPath> ] ] )

Imports configuration manifest into WAS configuration repository.

The idea behind manifests is described on a [page dedicated to manifests](../manifests.html).

## Arguments

_filename_

path to configuration manifest file, relative to `manifestPath`

_variables_

dictionary of variables (and filters) being used during variable expansion

_manifestPath_

list of paths where the `filename` is going to be looked up; optional, defaults to reversed Jython's `sys.path`

## Result

None
