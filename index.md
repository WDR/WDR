---
layout: page
title: WDR
tagline: Simpler WebSphere Application Server Scripting
---
{% include JB/setup %}

# WDR

Jython library which aims at simplifying WebSphere scripting.

# Features
* makes wsadmin scripts more "Pythonic" and readable and maintainable in result
* allows interoperability with "legacy" Jython scripts including mixing of classic wsadmin and WDR code
* works with currently supported WSAS versions (6.1 and later)
* Open Source, Apache License, Version 2.0

# Some highlights

## Listing nodes and servers available in configuration

```python
for node in list('Node'):
    print node.name
    for server in node.list('Server'):
        print " " + server.name
```

