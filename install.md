---
layout: page
title: Installing WDR
short_title: Install
---

WDR is a pure Jython library running in `wsadmin` client and as such requires
only a functional `wsadmin` setup plus some Jython scripts.

There are 2 installation modes:

* [Server-side installation](install_server.html) - read this if you want to run
 your scripts on the deployment manager (or standalone server) or if you are
 developer and want to manage your local WebSphere test environment. This way
 of installing WDR is the preferred one if you want to run scripts on the same
 machine where the application server or deployment manager is running.

* [Thin client installation](install_thin_client.html) - read this if you are
 building an automation server or want to access remote instances of WAS. This
 setup is a bit more involved than server-side installation, but it doesn't
 require you to install server binaries and helps you save money on WebSphere
 license costs.

WDR works equally well on every platform for which WebSphere binaries are
available, whether it's Windows or Linux/Unix.
