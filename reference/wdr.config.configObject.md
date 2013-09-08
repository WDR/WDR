---
layout: page
tagline: WDR Reference
title: configObject
---

Constructs [wdr.config.ConfigObject](wdr.config.ConfigObject.class.html) object from string.

This function is especially useful for integrating with existing wsadmin scripts. Configuration IDs from classic wsadmin script can be easily converted into WDR ConfigObject.

    configObject( objectIdentifier )

#### Arguments

_objectIdentifier_

string identifier of a single configuration object

#### Result

ConfigObject representing a configuration object

#### Examples

{% highlight python %}
o = configObject('wdrCell(cells/wdrCell|cell.xml#Cell_1)')
{% endhighlight %}
