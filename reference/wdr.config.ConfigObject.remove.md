---
layout: page
tagline: WDR Reference
title: ConfigObject.remove
---

Removes object from WebSphere configuration repository.

    obj.remove()

## Result

Reference to [wdr.config.ConfigObject](wdr.config.ConfigObject.class.html) removed from configuration repository.

_Please note that this reference is no longer pointing to an existing object. It may only be referenced again (become valid) after [reset](wdr.config.reset.html), [discard](wdr.config.discard.html) or AdminConfig.reset() invocation._

## Examples

* Removig a DataSource object

{% highlight python %}
ds = getid1('/Node:wdrNode01/Server:wdrServer/JDBCProvider:Derby JDBC Provider/DataSource:Default Datasource/')
ds.remove()
{% endhighlight %}
