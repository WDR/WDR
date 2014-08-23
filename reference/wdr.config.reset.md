---
layout: page
tagline: WDR Reference
title: reset
---

Discards all configuration changes made in current WDR/wsadmin session.
Deletes temporary files and cleans configuration cache of the WDR/wsadmin session.

_It's a good practice to always explicitly save or discard configuration session before exiting the script, even if no changes have been made. Configuration sessions abandoned witout reset/discard/save leave temporary files and directories on the server._

    reset()

## See also

* [hasChanges](wdr.config.hasChanges.html)
* [save](wdr.config.save.html)
