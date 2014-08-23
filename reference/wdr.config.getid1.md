---
layout: page
tagline: WDR Reference
title: getid1
---

A convenience function for retrieving single configuration object matching specified criteria. In contrast to [getid](wdr.config.getid.html) function, this function returns configuration object instance, not an array of objects. If no matches exist or more than one match exists, `getid1` raises an exception.

    getid1 ( <criteria> )

#### Arguments

_criteria_

a string in the form of `(/<type>:[<name>]/)+`

#### Result

An instance of [wdr.config.ConfigObject](wdr.config.ConfigObject.class.html) object.

#### Examples

* Retrieving `Cell` object

{% highlight python %}
print getid1('/Cell:/')
{% endhighlight %}

    wdrCell(cells/wdrCell|cell.xml#Cell_1)

* Retrieving `JavaProcessDef` from a named server

{% highlight python %}
print getid1('/Server:wdrServer/JavaProcessDef:/')
{% endhighlight %}

    (cells/wdrCell/nodes/wdrNode/servers/wdrServer|server.xml#JavaProcessDef_1335359012301)

#### See also

* [getid](wdr.config.getid.html)
* [wdr.config.ConfigObject.getid](wdr.config.ConfigObject.getid.html)
