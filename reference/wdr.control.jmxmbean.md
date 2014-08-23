---
layout: page
tagline: WDR Reference
title: jmxmbean
---

Constructs [wdr.control.JMXMBean](wdr.control.JMXMBean.class.html) object from string representation of MBean ObjectName.

    jmxmbean( objectName )

This function comes helpful when mixing classic wsadmin code with WDR-based code. JMX ObjectName obtained by wsadmin ``AdminControl.queryNames`` or by other means can be easily converted into [wdr.control.JMXMBean](wdr.control.JMXMBean.class.html) object.

## Arguments

_objectName_

string representation of ObjectName

## Result

[wdr.control.JMXMBean](wdr.control.JMXMBean.class.html) instance

## Examples

{% highlight python %}
# objectName variable will contain a single-line string representing ObjectName of dmgr Server
objectName = AdminControl.queryNames('WebSphere:*,type=Server,name=dmgr')
dmgr = jmxmbean(objectName)
print dmgr.state
{% endhighlight %}
