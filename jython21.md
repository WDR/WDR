---
layout: page
title: Jython 2.1, wsadmin and WDR
---

# Jython 2.1 is obsolete

Jython version being used by wsadmin is really old. It is acutally ancient in terms of Internet. Version 2.1 was released on 25th of Sep 2002 [according to SourceForge](http://sourceforge.net/projects/jython/files/jython/).

Jython 2.1 is lacking in many areas and it bites badly those who try to implement some more complex solutions based on wsadmin. There has been a lot of improvements in Jython since 2.1.

# Does IBM have an idea how to update Jython in WAS?

It seems that IBM attempted to update Jython in 2008, but they failed for some reason. The issue tracker of Jython project has some traces of that attempt and
the reasons (be it valid or not) why it was not done:

* [Issue 1163](http://bugs.jython.org/issue1163) Jython 2.1 converts string to unicode

* [Issue 1792](http://bugs.jython.org/issue1792) Jython returns unicode string when using Jython 2.5.2 in WebSphere Application Server

IMHO it could have been done by allowing new values for wsadmin's `-lang` option, like 'jython25' or 'jython-latest', but for some reason it hasn't been done like this either.

WDR's design goal was to be work smoothly on unmodified installation of WebSphere, which made WDR's development a bit harder. The biggest challenge was lack of parsers for any human-readable serialization languages (YAML, TOML, JSON, etc.) and a need to invent our own document format.

# WDR's support statement for Jython

WDR officially supports Jython 2.1. Scripts you write are 100% compatible with unmodified installation of the product.

WDR is known to work without issues with Jython 2.5. Jython 2.7 also works, but only in non-interactive sessions; interactive sesssion with wsadmin and Jython 2.7 does not start due to API incompatibilities.

Future versions of WDR *must* work 100% with Jython 2.1 and any other versions of Jython shipped with WebSphere. WDR *should* work with newer versions of Jython, as long as wsadmin is able to start the interpreter correctly.

# Archived pages

Over time, some pages references from here may become unavailable. Should it be the case, you may check the following links:

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
