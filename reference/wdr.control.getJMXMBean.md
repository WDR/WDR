---
layout: page
tagline: WDR Reference
title: getJMXMBean
---

Retrieves single instance of [wdr.control.JMXMBean](wdr.control.JMXMBean.class.html) matching specified criteria.
Raises an exception if there are multiple matches.
Value of `None` is returned if to MBeans match specified criteria.

    getJMXMBean( <criteria> )

#### Arguments

_criteria_

list of key/value pairs

#### Result

Instance of (wdr.control.JMXMBean.class.html) or value of `None`.

#### Examples

{% highlight python %}
srv = getJMXMBean(type='Server', name='dmgr')
print srv.state
{% endhighlight %}

    STARTED

#### See also

* [getJMXMBean1](wdr.control.getJMXMBean1.html)
* [queryJMXMBeans](wdr.control.queryJMXMBeans.html)
* [getMBean](wdr.control.getMBean.html)
* [getMBean1](wdr.control.getMBean1.html)
* [queryMBeans](wdr.control.queryMBeans.html)
