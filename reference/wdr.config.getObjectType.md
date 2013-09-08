---
layout: page
tagline: WDR Reference
title: getObjectType
---

Returns type name of configuration object

    getObjectType( <configObject> )

#### Arguments

_configObject_

configuration object

#### Examples

{% highlight python %}
o = getid('/Cell:/')[0]
print getObjectType(o)
{% endhighlight %}

    Cell
