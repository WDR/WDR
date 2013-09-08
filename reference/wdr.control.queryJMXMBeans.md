---
layout: page
tagline: WDR Reference
title: queryJMXMBeans
---

Retrieves list of [wdr.control.JMXMBean](wdr.control.JMXMBean.class.html) instances matching specified criteria.

    queryJMXMBeans( <criteria> )


#### Arguments

_criteria_

list of key/value pairs

#### Result

List of [wdr.control.JMXMBean](wdr.control.JMXMBean.class.html) instances.

#### Examples

* Printing free and available memory for each JVM MBean found

{% highlight python %}
for jvm in queryJMXMBeans(type='JVM'):
    print 'Free/max memory: %d/%d' % (jvm.freeMemory, jvm.maxMemory)
{% endhighlight %}

#### See also

* [getMBean](wdr.control.getMBean.html)
* [getMBean1](wdr.control.getMBean1.html)
* [getJMXMBean](wdr.control.getJMXMBean.html)
* [getJMXMBean1](wdr.control.getJMXMBean1.html)
* [queryJMXMBeans](wdr.control.queryMBeans.html)
