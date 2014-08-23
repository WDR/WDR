---
layout: page
tagline: WDR Reference
title: getid
---

Retrieves configuration objects based on provided criteria.

    getid ( <criteria> )

## Arguments

_criteria_

 a string in the form of `(/<type>:[<name>]/)+`

## Result

An array of [wdr.config.ConfigObject](wdr.config.ConfigObject.class.html) objects.

## Examples

* Retrieving `Cell` object

{% highlight python %}
print getid('/Cell:/')[0]
{% endhighlight %}

    wdrCell(cells/wdrCell|cell.xml#Cell_1)

* Retrieving a named `DataSource`

{% highlight python %}
print getid('/DataSource:DefaultEJBTimerDataSource/')
{% endhighlight %}

    [DefaultEJBTimerDataSource(cells/wdrCell/nodes/wdrNode/servers/wdrServer|resources.xml#DataSource_1000001)]

* Retrieving `JavaProcessDef` from a named server

{% highlight python %}
print getid('/Server:wdrServer/JavaProcessDef:/')
{% endhighlight %}

    [(cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#JavaProcessDef_1335359012301)]

## See also

* [wdr.config.ConfigObject.getid](wdr.config.ConfigObject.getid.html)
* [getid1](wdr.config.getid1.html)
