---
layout: page
tagline: WDR Reference
title: JMXMBean
---

Represents a Managed Bean registered in one of accessible WebSphere processes. Instances of this class can be created using:
* [queryJMXMBeans](wdr.control.queryJMXMBeans.html)
* [getJMXMBean](wdr.control.getJMXMBean.html)
* [getJMXMBean1](wdr.control.getJMXMBean1.html)
* [jmxmbean](wdr.control.jmxmbean.html)
* [jmxmbeans](wdr.control.jmxmbeans.html)

`wdr.control.JMXMBean` class is quite similar in its semantics to [wdr.control.MBean](wdr.control.MBeans.class.html) class except for automatic value conversions. With `JMXMBean` class you are able (an you have to) use Java types for arguments and attributes. No Java/Python conversions are being performed. In most of the cases you'll find these conversions desirable and prefer to use `MBean` class in favour of `JMXMBean`. However, there are rare use cases when you need to work with Java types.

The `AntAgent` type is going to be used in all `JMXMBean` examples due to the fact of using `byte[]`, `java.lang.String` and `java.lang.String[]` in argument lists and results.

Products based on WebSphere Application Server (like IBM BPM) expose more MBeans accepting/returning complex Java objects. The `JMXMBean` class has been introduced into WDR library specifically in order to interact with these MBeans.

`AntAgent` MBean executes Apache-Ant build scripts on the server. We'll need to prepare a simple script for the purpose of this example:

{% highlight xml %}
<?xml version="1.0"?>
<project name="WDR" default="hello">
    <target name="hello">
        <echo>Hello from WDR! Properties: p1=${p1}, p2=${p2}</echo>
    </target>
</project>
{% endhighlight %}

For simplicity, we're not going to save the above build script as local file. We'll rather store its content in a string variable named 'xml'.

{% highlight python %}
# string variable containing Ant script
xml = '<?xml version="1.0"?> <project name="WDR" default="hello"> <target name="hello"> <echo>Hello from WDR! Properties: p1=${p1}, p2=${p2}</echo> </target> </project>'

# now we need to import Java type into Jython, in this case it is java.lang.String class, then we construct Java object from Python object
from java.lang import String
str = String(xml)

# time to extract byte array from Java string:
bytes = str.getBytes()

# obtaining reference to AntAgent MBean:
antAgent = getJMXMBean1(type='AntAgent', node='wdrNode01', process='nodeagent')

# uploading Ant script to the server:
antAgent.putScript(String('hello.ant.xml'), bytes)

# building property list:
import jarray
props = jarray.array( ['p1=v1', 'p2=v2'], String)

# invoking Ant script:
antAgent.invokeAnt(props, String('hello.ant.xml'), String('hello'))

# retrieving script results and printing them:
print String(antAgent.getLastLog())
{% endhighlight %}

    Detected Java version: 1.5 in: C:\tools\was7\java\jre
    Detected OS: Windows 7
    Adding reference: ant.ComponentHelper
    Adding reference: ant.projectHelper
    Adding reference: ant.parsing.context
    Adding reference: ant.targets
    parsing buildfile C:\tools\was7\profiles\wdrNode01\temp\hello.ant.xml with URI = file:///C:/tools/was7/profiles/wdrNode01/temp/hello.ant.xml
    Setting ro project property: ant.project.name -> WDR
    Adding reference: WDR
    Setting ro project property: ant.file.WDR -> C:\tools\was7\profiles\wdrNode01\temp\hello.ant.xml
    Project base dir set to: C:\tools\was7\profiles\wdrNode01\temp
     +Target:
     +Target: hello
    Build sequence for target(s) `hello' is [hello]
    Complete build sequence is [hello, ]

    hello:
         [echo] Hello from WDR! Properties: p1=v1, p2=v2

    BUILD SUCCESSFUL
    Total time: 0 seconds
