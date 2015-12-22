---
layout: page
tagline: WDR Reference
title: importApplicationEmbeddedManifest
---

    importApplicationEmbeddedManifest( <applicationArchiveFilename> [, <variables> [, <listener>, [, <manifestPath>] ] ] )

Imports application manifest embedded in application archive.

The idea behind manifests is described on a
[page dedicated to manifests](../manifests.html).

The behaviour of this function is very similar to 
[importApplicationManifest](wdr.manifest.importApplicationManifest.html),
the only difference is the origin of the manifest file: instead of being a
standalone file, it is embedded in applicaiton archive.

Application-embedded manifests are handy when you're in control of application
build process or if you can convince the development team to use WDR or to at
least include manifest in the archive during the build process. The alternative
to embedded manifests are standalone manifests.

## Arguments

_applicationArchiveFilename_

path to application archive file, the archive must contain application manifest
under `META-INF/manifest.wdra` path

_variables_

dictionary of variables (and filters) being used during variable expansion

_listener_

listener objects receiving callbacks on different actions being performed
during application manifest import

_manifestPath_

currently not being used

## Result

List of application names that have been affected (installed or updated) during
manifest import. Application manifest may describe deployment of one or more
applications. Names of applications which haven't been installed/updated will
not be included in the returned list.

## Result

List of application names installed or updated during manifest processing.

## See also

* [importApplicationManifest](wdr.manifest.importApplicationManifest.html)
* [exportApplicationManifestToFile](wdr.tools.exportApplicationManifestToFile.html)
