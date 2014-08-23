---
layout: page
tagline: WDR Reference
title: listConfigObjects
---

Lists configuration objects of a specified type within either specified scope or matching specified pattern.

    listConfigObjects( <typeName>, [ <scope> | <pattern> ] )

## Arguments

_typeName_

name of configuration object type

_scope_

[wdr.config.Object](wdr.config.ConfigObject.class.html) instance

_pattern_

wildcard pattern for filtering the results

## Result

List of [wdr.config.ConfigObject](wdr.config.ConfigObject.class.html) objects.

## Examples

* Listing all `Server` objects

{% highlight python %}
print listConfigObjects('Server')
{% endhighlight %}

    [dmgr(cells/wdrCell/nodes/wdrDMgrNode/servers/dmgr|server.xml#Server_1), nodeagent(cells/wdrCell/nodes/wdrNode01/servers/nodeagent|server.xml#Server_1340355137285), wdrServer(cells/wdrCell/nodes/wdrNode01/servers/wdrServer|server.xml#Server_1340355496917)]

* Listing all `Server` objects in scope of node

{% highlight python %}
node = getid1('/Node:wdrNode01/')
print listConfigObjects('Server', node)
{% endhighlight %}

    [nodeagent(cells/wdrCell/nodes/wdrNode01/servers/nodeagent|server.xml#Server_1340355137285), wdrServer(cells/wdrCell/nodes/wdrNode01/servers/wdrServer|server.xml#Server_1340355496917)]


* Listing all `Server` objects matching specified wildcard

{% highlight python %}
print listConfigObjects('Server', 'nodeagent(*')
{% endhighlight %}

    [nodeagent(cells/wdrCell/nodes/wdrNode01/servers/nodeagent|server.xml#Server_1340355137285)]

## See also

* [wdr.config.ConfigObject.listConfigObjects](wdr.config.ConfigObject.listConfigObjects.html)
* [getid](wdr.config.getid.html)
* [getid1](wdr.config.getid1.html)
