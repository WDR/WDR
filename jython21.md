---
layout: page
title: Jython 2.1, wsadmin and WDR
---

# Jython 2.1 is obsolete, yet supported

Historically, the *wsadmin* tool provided by WAS was using very old version of
Jython implementation (2.1). This situation has improved with version 9.0 of WAS,
which officially supports Jython 2.7.

WDR officially supports both Jython 2.1 and 2.7 until futher notice.

This support statement comes with its benefits and drawbacks. The good news is
that all features of WDR are available even on WAS 6.1. The bad news is that
WDR itself can't make too much use of language features that are not available
in Jython 2.1 nor use any dependencies that do not work with Jython 2.1.
