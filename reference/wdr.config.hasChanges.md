---
layout: page
tagline: WDR Reference
title: hasChanges
---

Returns 1 (true) if current WDR/wsadmin session has some unsaved configuration changes, 0 otherwise.

    hasChanges()

## Result

1 (true) if there are any unsaved changes in current session, 0 (false) otherwise.

## Examples

Script snippet cleaning up session state before exiting.

_It's a good practice to always explicitly save or discard configuration session before exiting the script, even if no changes have been made. Configuration sessions abandoned witout reset/discard/save leave temporary files and directories on the server._

```python
if hasChanges():
    save()
else:
    discard()
exit
```

## See also

* [save](wdr.config.save.html)
* [reset](wdr.config.reset) and [discard](wdr.config.discard.html)
