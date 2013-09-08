---
layout: page
tagline: WDR Reference
title: ConfigObject.create
---

Creates a new configuration object in configuration repository and returns its reference as [wdr.config.ConfigObject](wdr.config.ConfigObject.class.html).

    obj.create( <typeName>, [ <propertyName>, ], attributes )

#### Arguments

_typeName_

name of object type

_propertyName_

parent object's property in context of which the new object will be created

_attributes_

list of new object's attributes

#### Result

After successful execution, a reference to newly created [wdr.config.ConfigObject](wdr.config.ConfigObject.class.html) is being returned.

#### Examples

* Creating `Server` object in the scope of a `Node` and modifying the newly created object

{% highlight python %}
node = getid1('/Node:wdrNode01/')
server = node.create('Server', name = 'wdrServer02')
server.processDefinitions[0].jvmEntries[0].maximumHeapSize = 1024
{% endhighlight %}

* Creating a `Property` in scope of `JavaVirtualMachine` property `systemProperties`

{% highlight python %}
server = getid1('/Server:wdrServer/')
property = server.processDefinitions[0].jvmEntries[0].create('Property', 'systemProperties', name='user.language', value='pl')
property.description = 'This JVM is going to write logs in Polish language. Powodzenia :)'
{% endhighlight %}

### See also

* [parents](wdr.config.parents.html)
* [attributes](wdr.config.attributes.html)
* [wdr.config.ConfigObject.assure](wdr.config.ConfigObject.assure.html)
