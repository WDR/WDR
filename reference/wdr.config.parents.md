---
layout: page
tagline: WDR Reference
title: parents
---

Returns parent types of specified type.

    parents( <typeName> )

#### Arguments

_typeName_

name of configuration object type

#### Result

List of type names which contain specified type.

#### Examples

* Listing parents of `JDBCProvider` type

{% highlight python %}
print parents('JDBCProvider')
{% endhighlight %}

    ['Cell', 'Deployment', 'Node', 'Server', 'ServerCluster']

#### See also

* [attributes](wdr.config.attributes.html)
* [getObjectType](wdr.config.getObjectType.html)
