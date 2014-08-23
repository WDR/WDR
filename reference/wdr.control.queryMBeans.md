---
layout: page
tagline: WDR Reference
title: queryMBeans
---

Retrieves list of [wdr.control.MBean](wdr.control.MBean.class.html) instances matching specified criteria.

    queryMBeans( [<domain>,] <criteria> )

## Arguments

_domain_

JMX domain being searched; optional argument, defauts to value of 'WebSphere'; in most of the cases you can skip this argument and rely on the default value

_criteria_

list of key/value pairs

## Result

List of [wdr.control.MBean](wdr.control.MBean.class.html) instances.

## Examples

* Printing free and available memory for each JVM MBean found

{% highlight python %}
for jvm in queryMBeans(type='JVM'):
    print 'Free/max memory: %d/%d' % (jvm.freeMemory, jvm.maxMemory)
{% endhighlight %}

* Printing attribute value of one of custom MBeans, registered in 'ACME' domain

{% highlight python %}
for tp in queryMBeans('ACME', type='com.acme.tasks.TaskProcessor', module='OrderProcessing'):
    print 'Failed/total number of orders: %d/%d' % (tp.failed, tp.total)
{% endhighlight %}

## See also

* [getMBean](wdr.control.getMBean.html)
* [getMBean1](wdr.control.getMBean1.html)
* [getJMXMBean](wdr.control.getJMXMBean.html)
* [getJMXMBean1](wdr.control.getJMXMBean1.html)
* [queryJMXMBeans](wdr.control.queryJMXMBeans.html)
