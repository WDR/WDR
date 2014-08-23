---
layout: page
tagline: WDR Reference
title: ConfigObject.assure
---

    obj.assure( <type>, <keys>, [propertyName], <attributes> )

Assures that the object of specified `type` with specified `keys` exists in the scope of `obj`.

If the object exists at the time of `assure` invocation, no new object is being created. The existing object's attributes are only being modified accordingly to `attributes` parameter.

If no existing object matches `type` and `keys`, the `assure` method attempts to create a new object of type specified in `type` and attributes specified in `keys` and `attributes`.

If multiple objects match `type` and `keys`, an exception is being raised.

## Arguments

_type_

name of object type

_keys_

dictionary where keys are attribute names and values are attribute values

_propertyName_

parent object's property in context of which the new object will be created

_attributes_

list of attributes

## Result

After successful execution, a reference to the `ConfigObject` affected by the call is being returned (be it the created one or the modified one).

Exception will be raised if multiple objects matched specified criteria or if `ConfigObject` creation/modification failed.

## Examples

* The following script assures that a server named 'wdrServer02' exists in the scope of node 'wdrNode01' and also assures that a JVM property 'user.language' exists and it has value of 'pl'.

{% highlight python %}
node = getid1('/Node:wdrNode01/')
server = node.assure('Server',{'name':'wdrServer02'})
jvm = server.processDefinitions[0].jvmEntries[0]
jvm.assure('Property', {'name':'user.language'}, 'systemProperties', value='pl', description='This JVM is going to write logs in Polish language. Powodzenia :)')
{% endhighlight %}

## See also

* [parents](wdr.config.parents.html)
* [attributes](wdr.config.attributes.html)
* [wdr.config.ConfigObject.assure](wdr.config.ConfigObject.assure.html)
