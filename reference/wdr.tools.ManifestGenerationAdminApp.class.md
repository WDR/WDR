---
layout: page
tagline: WDR Reference
title: ManifestGenerationAdminApp
---

    wdr.tools.ManifestGenerationAdminApp

**Deprecated feature**

> `ManifestGenerationAdminApp` was implemented as an experimental way of generating application manifests. Although it was doing its job very well, the other experimental function, `exportApplicationManifestToFile` received much better feedback from WDR users. Considering that, the `ManifestGenerationAdminApp` will not be further developed or even maintained and becomes deprecated.

`ManifestGenerationAdminApp` mocks wsadmin's `AdminApp` object exposing its `install` and `update` function, but instead of installing/updating applications it generates application manifest. A practical use case for this class is to generate jython script using AdminConsole's command assistance function and then use the commandassistance.log file with `ManifestGenerationAdminApp` class to generate manifest.

The following example saves application manifest in 'DefaultApplication.wdra' file:

{% highlight python %}
AdminApp = wdr.tools.ManifestGenerationAdminApp( AdminApp, 'DefaultApplication.wdra' )
# the following command comes from commandassistance.log file
AdminApp.install( ... )
{% endhighlight %}

#### See also

* [exportApplicationManifestToFile](wdr.tools.exportApplicationManifestToFile.html)
