---
layout: page
tagline: WDR Reference
title: sync
---

Synchronizes all available nodes with the deployment manager.
Warnings are being logged if some nodeagents are not started or not available.

    sync(quiet = 0)

## Arguments

_quiet_

boolean value with the default value of 0 (false)

## Result

Floating-point numer in the range between 0.0 and 1.0 representing percentage of nodes which have been synchronized with ``sync()`` call. The value of 1.0 means that 100% of nodes have been synchronized, whereas 0.0 means that none of nodes synchronized successfully.

## See also

* [save](wdr.config.save)
