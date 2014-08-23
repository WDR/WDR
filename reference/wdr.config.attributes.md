---
layout: page
tagline: WDR Reference
title: attributes
---

Retrieves list of attribute names of specified type or configuration object.

    attributes ( <typeName> | <configObject> )

## Arguments

_typeName_

name of configuration object type

_configObject_

instance of ConfigObject

## Result

List of configuration attribute names of type/object as array of strings.

## Examples

* Retrieving attributes of a type

{% highlight python %}
print attributes('Cell')
{% endhighlight %}

    ['adminAgentRegistration', 'cellDiscoveryProtocol', 'cellRegistered', 'cellType', 'discoveryAddressEndpointName', 'foreignCells', 'multicastDiscoveryAddressEndpointName', 'name', 'properties', 'shortName']

* Retrieving attributes of an object

{% highlight python %}
server = getid('/Server:/')[0]
print attributes(server)
{% endhighlight %}

    ['adjustPort', 'changeGroupAfterStartup', 'changeUserAfterStartup', 'clusterName', 'components', 'customServices', 'developmentMode', 'errorStreamRedirect', 'modelId', 'name', 'outputStreamRedirect', 'parallelStartEnabled', 'processDefinition', 'processDefinitions', 'provisionComponents', 'serverInstance', 'serverType', 'services', 'shortName', 'stateManagement', 'statisticsProvider', 'uniqueId']
