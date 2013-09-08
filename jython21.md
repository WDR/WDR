---
layout: page
title: Jython 2.1 and wsadmin
---

# Jython 2.1 is obsolete

Jython version being used by wsadmin is really old. It is ancient in terms of Internet. Version 2.1 was released on 25th of Sep 2002 [according to SourceForge](http://sourceforge.net/projects/jython/files/jython/).

Jython 2.1 is really lacking in many areas and it bites badly those who try to implement some more complex solutions based on wsadmin. There has been a lot of improvements in Jython since 2.1.

# Does IBM have an idea how to update Jython in WAS?

It seems that IBM attempted to update Jython in 2008, but they failed for some reason. The issue tracker of Jython project has some traces of that attempt:

* [Issue 1163](http://bugs.jython.org/issue1163) Jython 2.1 converts string to unicode

* [Issue 1792](http://bugs.jython.org/issue1792) Jython returns unicode string when using Jython 2.5.2 in WebSphere Application Server

I really can not understand why they have not added another value for `-lang` option. That option accepts `jython` and `jacl` currently. Why it could not accept `jython25` or simply `jython-latest`?

# Ancient version of Jython in WAS impacts WDR and you

One of fundamental requirements of WDR was to be 100% compatible with default wsadmin in order to allow seamless migration from "legacy" wsadmin scripts to WDR. That means that WDR must work with Jython 2.1.

If you ever wonder why WDR does not use YAML, JSON or at least XML, why the old class notation is being used, why a legacy version of "logging" is bundled with WDR, etc - you get the answer. It is not our fault. Complain to "market leader" being 11 years behind with Jython (so far).

# Does anyone support Jython 2.1?

You may get frustrated working with Jython 2.1 also when trying to install a standalone version of Jython 2.1. In order to save you some time, please be adviced: it is not installable on a modern OS:

* Jython 2.1 installer crashes when running on a decent JVM (may also crash a less decent JVM).

* Jython 2.1 can only be installed using JDK 1.3. That JDK also will not install on a decent OS.

Instead of wasting time trying to install it, rather copy it from existing WAS installation. You may wonder how IBM "supports" that old Jython release...

IBM support seems to be also impacted occasionally. Then they seek help from Open Source Community without getting it, obviously:

* [Issue 1360](http://bugs.jython.org/issue1360) The write permission is required on jython.jar ?

# Is there a solution?

No. There are only _workarounds_ to the problem. _THE SOLUTION_ is in hands of IBM.

It would be really nice if IBM could catch up a bit. The question is: how to convince them to update Jython?

The official support channel probably will not work. If you open a PMR and complain on pre-historical Jython, your PMR may get closed with "works as designed" explanation (Jython 2.1 is explicitly listed in WAS documentation). The other option is to open a "feature request" and hope for change in one of subsequent releases. Chances are bad that such request can gain enough attention at IBM. The only way to push it forward is probably to name and shame, hoping that one day IBM is going to be ashamed enough, update Jython and obsolete this page...

In the interim you have two choices, each of them has some drawbacks:

* Stay with Jython 2.1 if compatibility with default istallation is important. You will have to live with all the shortcomings of Jython 2.1 though.

* Upgrade your Jython, preferably by adding it to [thin client installation](install_thin_client.html) and benefit from all the improvements made. Compatibility of your scripts will be impacted though.

# Archived pages

Over time, some pages mentioned here may become unavailable. Should it be the case, you may check the following links:

* Jython releases

  * [Wayback Machine on Jython releases](http://web.archive.org/web/20120827132430/http://sourceforge.net/projects/jython/files/jython/)

* Jython issue 1163

  * [Issue 1163 in Wayback Machine](http://web.archive.org/web/20120816055710/http://bugs.jython.org/issue1163)

  * [Issue 1163 in peeep.us](http://www.peeep.us/6c69e92d)

* Jython issue 1792

  * [Issue 1792 in Wayback Machine](http://web.archive.org/web/20130904194339/http://bugs.jython.org/issue1792)

  * [Issue 1792 in peeep.us](http://www.peeep.us/4884b502)

* Jython issue 1360

  * [Issue 1360 in Wayback Machine](http://web.archive.org/web/20100707121750/http://bugs.jython.org/issue1360)

  * [Issue 1360 in peeep.us](http://www.peeep.us/8637cd02)
