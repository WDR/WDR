---
layout: page
tagline: WDR Reference
title: ConfigObject.listConfigObjects
---

Lists all child objects of a specified type.

    obj.listConfigObjects( <typeName> )

## Arguments

_typeName_

name of object type

## Result

List of [wdr.config.ConfigObject](wdr.config.ConfigObject.class.html) instances.

## Examples

* Retrieving list of JDBCProvider's DataSources

{% highlight python %}
print provider.listConfigObjects('DataSource')
{% endhighlight %}

    [Default Datasource(cells/wdrCell/nodes/wdrNode01/servers/wdrServer|resources.xml#DataSource_1124467080076)]

## See also

* [listConfigObjects](wdr.config.listConfigObjects.html)
