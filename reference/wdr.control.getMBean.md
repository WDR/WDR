---
layout: page
tagline: WDR Reference
title: getMBean
---

Retrieves single instance of [wdr.control.MBean](wdr.control.MBean.class.html) matching specified criteria.
Value of `None` is returned if to MBeans match specified criteria.

    getMBean( [<domain>,] <criteria> )

## Arguments

_domain_

JMX domain being searched; optional argument, defauts to value of 'WebSphere'; in most of the cases you can skip this argument and rely on the default value

_criteria_

list of key/value pairs

## Result

Instance of [wdr.control.MBean](wdr.control.MBean.class) or value of `None`.

## Examples

```python
srv = getMBean(type='Server', name='dmgr')
print srv.state
```

## See also

* [getMBean1](wdr.control.getMBean1.html)
* [queryMBeans](wdr.control.queryMBeans.html)
* [getJMXMBean](wdr.control.getJMXMBean.html)
* [getJMXMBean1](wdr.control.getJMXMBean1.html)
* [queryJMXMBeans](wdr.control.queryJMXMBeans.html)
