---
layout: page
title: Installing WDR on WAS server
---

Installing on the server is the simplest way to get WDR working.

# Get the code

All you need to do is to either:

* clone the repository from [https://github.com/WDR/WDR.git](https://github.com/WDR/WDR.git)

* or [download the latest code](https://github.com/WDR/WDR/archive/master.zip)

# Configure your environment

Set 2 environment variables:

* `WAS_HOME` with a fully-qualified path of your WAS installation (or path to WAS profile)

* `WDR_HOME` with a fully-qualified path of a directory containg extracted/cloned WDR repository

# Start using it

Then run start `wsadmin` session with the following arguments:

{% highlight sh %}
${WAS_HOME}/bin/wsadmin.sh -lang jython -javaoption -Dcom.ibm.ws.scripting.exceptionPropagation=thrown -javaoption -Dpython.path=${WDR_HOME}/lib/legacy:${WDR_HOME}/lib/common:. -profile ${WDR_HOME}/profile.py
{% endhighlight %}

{% highlight bat %}
%WAS_HOME%\bin\wsadmin.bat -lang jython -javaoption -Dcom.ibm.ws.scripting.exceptionPropagation=thrown -javaoption "-Dpython.path=%WDR_HOME%\lib\legacy;%WDR_HOME%\lib\common;." -profile %WDR_HOME%\profile.py
{% endhighlight %}

If everything goes well, you should get the output similar to the following one:

    %WAS_HOME%\bin\wsadmin.bat -lang jython -javaoption -Dcom.ibm.ws.scripting.exceptionPropagation=thrown -javaoption "-Dpython.path=%WDR_HOME%\lib\common;%WDR_HOME%\lib\legacy" -profile %WDR_HOME%\profile.py
    WASX7209I: Connected to process "dmgr" on node wdrDMgrNode using SOAP connector;  The type of process is: DeploymentManager
    2013-09-04 17:06:06,766 [INFO] using WDR version 0.3
    2013-09-04 17:06:06,776 [INFO] the client is connected to host localhost:8879 using SOAP connector
    2013-09-04 17:06:06,782 [INFO] the target process is wdrCell/wdrDMgrNode/dmgr
    WASX7031I: For help, enter: "print Help.help()"
    wsadmin>print getJMXMBean1(type='Server',name='dmgr').state
    STARTED
    wsadmin>reset()
    wsadmin>exit

