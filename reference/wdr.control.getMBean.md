---
layout: page
tagline: WDR Reference
title: getMBean
---

Retrieves single instance of [wdr.control.MBean](wdr.control.MBean.class.html) matching specified criteria.
Value of `None` is returned if to MBeans match specified criteria.

    getMBean( <criteria> )

#### Arguments

_criteria_

list of key/value pairs

#### Result

Instance of [wdr.control.MBean](wdr.control.MBean.class) or value of `None`.

#### Examples

{% highlight python %}
srv = getMBean(type='Server', name='dmgr')
print srv.state
{% endhighlight %}

#### See also

* [getMBean1](wdr.control.getMBean1.html)
* [queryMBeans](wdr.control.queryMBeans.html)
* [getJMXMBean](wdr.control.getJMXMBean.html)
* [getJMXMBean1](wdr.control.getJMXMBean1.html)
* [queryJMXMBeans](wdr.control.queryJMXMBeans.html)
