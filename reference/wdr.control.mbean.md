---
layout: page
tagline: WDR Reference
title: mbean
---

Constructs [wdr.control.MBean](wdr.control.MBean.class.html) object from string representation of MBean ObjectName.

    mbean( objectName )

This function comes helpful when mixing classic wsadmin code with WDR-based code. JMX ObjectName obtained by wsadmin ``AdminControl.queryNames`` or by other means can be easily converted into [wdr.control.MBean](wdr.control.MBean.class.html) object.

## Arguments

_objectName_

string representation of ObjectName

## Result

[wdr.control.MBean](wdr.control.MBean.class.html) instance

## Examples

{% highlight python %}
# objectName variable will contain a single-line string representing ObjectName of dmgr Server
objectName = AdminControl.queryNames('WebSphere:*,type=Server,name=dmgr')
dmgr = mbean(objectName)
print dmgr.state
{% endhighlight %}
