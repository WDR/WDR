---
layout: page
title: Installing WDR
---

WDR is a pure Jython library running in `wsadmin` client and as such requires only a functional `wsadmin` setup plus some Jython scripts.

Most of `wsadmin` installations use `wsadmin.<bat|sh>` script provided by WebSphere Application Server (and derived products). Another way of setting up `wsadmin` was described by Peter Van Sickel in [Using the latest Jython with a WebSphere Application Server wsadmin thin client](http://www.ibm.com/developerworks/websphere/library/techarticles/1207_vansickel/1207_vansickel.html) in IBM developerWorks. WDR can be also used with such setup.

Each of these installation options is described in separate guides:

* [Server-side installation](install_server.html) - read this if you want to run your scripts on the deployment manager (or standalone server) or if you are developer and want to manage your local WebSphere test environment

* [Thin client installation](install_thin_client.html) - read this if you build an automation server or want to access remote instances of WAS. This setup is a bit more difficult then server-side installation, but it doesn't require you to install server binaries and helps you save money on WebSphere license costs
