---
layout: page
tagline: WDR Reference
title: jmxmbeans
---

Constructs list of [wdr.control.JMXMBean](wdr.control.JMXMBean.class.html) object from multi-line string representation of MBean ObjectNames. Each line in the string contains one ObjectName.

    jmxmbeans( objectNames )

This function comes helpful when mixing classic wsadmin code with WDR-based code. JMX ObjectNames obtained by wsadmin ``AdminControl.queryNames`` or by other means can be easily converted into list of [wdr.control.JMXMBean](wdr.control.JMXMBean.class.html) objects.

#### Arguments

_objectNames_

multi-line string representation of ObjectName

#### Result

list of [wdr.control.JMXMBean](wdr.control.JMXMBean.class.html) instances

#### Examples

{% highlight python %}
# objectName variable will contain a multi-line string where each
# line represents ObjectName of a Server
objectNames = AdminControl.queryNames('WebSphere:*,type=Server')
for srv in jmxmbeans(objectNames):
    print srv.name, ': ', srv.state
{% endhighlight %}
