---
layout: page
tagline: WDR Reference
title: unset
---

'Unsets' specified attributes or sets them to default values.

    obj.unset( <attributeList> )

#### Arguments

_attributeList_

list of attribute names to unset

#### Result

Reference to the object being modified

#### Examples

* Unsetting `initialHeapSize` and `maximumHeapSize` for server's JVM

{% highlight python %}
server = getid1('/Node:wdrNode01/Server:wdrServer/')
jvm = server.processDefinitions[0].jvmEntries[0]
jvm.unset(['initialHeapSize','maximumHeapSize'])
{% endhighlight %}
