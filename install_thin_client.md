---
layout: page
title: WDR installation with WebSphere Thin Client
---

Thin-client-based installation, although more complicated than the
[server-side one](install_server.html), can be a better choice in certain cases,
especially when multiple WAS cells need to be managed from one location, like a
Continuous Integration / Continuous Delivery server. The advantages of
client-side installation are:

* No need to pay licence fees for management node

* Client binaries are being managed independently from server software.
  WebSphere Client can be updated to a latest fixpacks, even if some servers
  have to remain a one or two FixPack levels behind

* A possibility to choose Jython and Java version on the management node,
  without impacting the runtime environment.

# How client-based setup works

The client-based setup uses `wdr.<sh|bat>` launcher script which essentialy
replaces the `wsadmin.<sh|bat>` script known from server-side setup.

The launcher script uses the following syntax on Linux/Unix systems:

```sh
${WDR_HOME}/wdr.sh <runtime> <environment> [jython_script] [script_arguments]
```

... and a similar one on Windows:

```bat
%WDR_HOME%\wdr.bat <runtime> <environment> [jython_script] [script_arguments]
```

The `<runtime>` is an alias that maps to a version of WAS client installed
locally. The definition of that alias consists of installation path, Java SDK
path, Jython version information and path to Jython implementation on disk.
Usually it has values like "was85", "was90" or "was90_jython21".

The `<environment>` is an easy to recall and meaningful name for WAS environment
being managed by WDR. Under the covers, the "environments" is a directory
containing a set of *.properties files, which point WDR to the managed server.

Subequent paragraphs describe the steps necessary to install and configure WDR,
runtimes and environments.

# Installation steps

In a nutshell:

* Installing WebSphere Application Client, together with FixPacks

* Installing WDR itself

* Extending WAS client with Jython

* Configuring aliases for installed WAS clients (aka. runtimes) in WDR

* Configuring access to WAS servers (aka. environments)

## Installing WebSphere Application Client

The installation will require:

* Installation images for "GA" version - available from Passport Advantage

* FixPack - available from IBM Support Portal

Please use official IBM documentation for detailed installation instructions and
troubleshootning.

### Obtaining installation images

Follow release-specific instruction to download installation images (the package
you need is usually called "WAS Supplements") for versions
[6.1](http://www-01.ibm.com/support/docview.wss?uid=swg27007645),
[7.0](http://www-01.ibm.com/support/docview.wss?uid=swg27012960),
[8.0](http://www-01.ibm.com/support/docview.wss?uid=swg27021166),
[8.5](http://www-01.ibm.com/support/docview.wss?uid=swg27024154),
[8.5.5](http://www-01.ibm.com/support/docview.wss?uid=swg27038624),
[9.0](http://www-01.ibm.com/support/docview.wss?uid=swg27048323).

### Admin Client installation

Thin Client installation comes with GUI, console and silent installers. This
installation instruction focuses on silent install.

#### WAS 6.1 client

In the first step, create a response file and save it to
`/root/was61client.rsp`. Feel free to customize installation settings:

```
-OPT silentInstallLicenseAcceptance="true"
-OPT allowNonRootSilentInstall="false"
-OPT disableOSPrereqChecking="true"
-OPT disableNonBlockingPrereqChecking="true"
-OPT setupTypeUnix="custom"
-OPT installLocation="/opt/IBM/WebSphere/AppClient61"
-OPT selectJ2eeClient="true"
-OPT selectJ2eeSamples="false"
-OPT selectIBMSdk="true"
-OPT selectWsThinClient="true"
-OPT selectAdminThinClient="true"
-OPT serverHostname="localhost"
-OPT serverPort="2809"
```

Having the response file, run the following command in the directory where
you extracted the installation image:

```sh
./install -options "/root/was61client.rsp" -silent
```

#### WAS 7.0 client

Similarly to WAS 6.1 client, create a response file and save it in
`/root/was70client.rsp`:

```
-OPT silentInstallLicenseAcceptance="true"
-OPT allowNonRootSilentInstall="false"
-OPT disableOSPrereqChecking="true"
-OPT disableNonBlockingPrereqChecking="true"
-OPT setupTypeUnix="custom"
-OPT installLocation="{{ was70client.root }}"
-OPT selectJ2eeClient="true"
-OPT selectJ2eeSamples="false"
-OPT selectIBMSdk="true"
-OPT selectThinClients="true"
-OPT selectThinClientsSamples="false"
-OPT selectAdminThinClient="true"
-OPT serverHostname="localhost"
-OPT serverPort="2809"
```

Then run the following command from the directory where installation image was
extracted:

```sh
./install -options "/root/was70client.rsp" -silent
```

#### WAS 8.0 client

From WAS 8.0 onwards, the installation is being done using IBM Installation
Manager. Use the following command to install WAS 8.0 client. Replace
`<WAS_8_0_CLIENT_URL>` with the URL or path to a directory where the
installation image was extracted.

```sh
/opt/IBM/InstallationManager/eclipse/tools/imcl install \
        com.ibm.websphere.APPCLIENT.v80,javaee.thinclient.core.feature,javaruntime,developerkit,standalonethinclient.resourceadapter.runtime,embeddablecontainer \
        -repositories <WAS_8_0_CLIENT_URL> \
        -installationDirectory /opt/IBM/WebSphere/AppClient80 \
        -acceptLicense \
        -properties user.appclient.serverHostname=localhost,user.appclient.serverPort=2809 \
        -preferences com.ibm.cic.common.core.preferences.preserveDownloadedArtifacts=false
```

#### WAS 8.5 or 8.5.5 client

Similarly to WAS 8.0 client, use this command to install 8.5/8.5.5 client,
replacing `<WAS_8_5_CLIENT_URL>` with the URL or directory where installation
image was extracted.

```sh
/opt/IBM/InstallationManager/eclipse/tools/imcl install \
    com.ibm.websphere.APPCLIENT.v85,javaee.thinclient.core.feature,javaruntime,developerkit,standalonethinclient.resourceadapter.runtime,embeddablecontainer \
    -repositories <WAS_8_5_CLIENT_URL> \
    -installationDirectory /opt/IBM/WebSphere/AppClient85 \
    -acceptLicense \
    -properties user.appclient.serverHostname=localhost,user.appclient.serverPort=2809 \
    -preferences com.ibm.cic.common.core.preferences.preserveDownloadedArtifacts=false
```

#### WAS 9.0 client

Just like in cae of WAS 8.0 client above, run this command to install WAS 9.0
client, replacing `<WAS_9_0_CLIENT_URL>` `<SDK_8_0_URL>` with the URLs or
directories where installation images for WAS Client and SDK were extracted.

```sh
/opt/IBM/InstallationManager/eclipse/tools/imcl install \
    com.ibm.websphere.APPCLIENT.v90,javaee.thinclient.core.feature,standalonethinclient.resourceadapter.runtime,embeddablecontainer \
    com.ibm.java.jdk.v8,com.ibm.sdk.8 \
    -repositories <WAS_9_0_CLIENT_URL>,<SDK_8_0_URL> \
    -installationDirectory /opt/IBM/WebSphere/AppClient90 \
    -acceptLicense \
    -properties user.appclient.serverHostname=localhost,user.appclient.serverPort=2809 \
    -preferences com.ibm.cic.common.core.preferences.preserveDownloadedArtifacts=false
```

#### Linux-specific pre-requisites

Linux distrubution, including the most popular ones, may not install some
prerequisites by default. WebSphere installers tend to fail in such situation in
a cryptic way. Therefore it might be a good idea to install those prerequisites
upfront.

For RedHat-based systems (RHEL, CentOS, Fedora) `compat-libstdc++-33` library
is required.

The dependency can be added to 64-bit OS using this command:

```sh
sudo yum install compat-libstdc++-33.x86_64
```

On a 32-bit system or when installing 32-bit flavour of the client on a 64-bit
OS, the command looks as follows:

```sh
sudo yum install compat-libstdc++-33.i686
```

Debian-based systems (including Ubuntu and other relatives) will require
`gcc-multilib` library:

```sh
sudo apt-get install gcc-multilib
```

Ubuntu uses `dash` as the default shell, but WebSphere scripts are not
compatible with this shell and fail in a cryptic way. The default shell can be
changed to `bash` using this command:

```sh
sudo update-alternatives --install /bin/sh sh /bin/bash 100
```

## Installing WDR

Installing WDR means essentially getting the source code from git repository on
GitHub. There are two ways to achieve that:

* cloning the repository

```sh
git clone https://github.com/WDR/WDR.git
```

* downloading the [snaphot](https://github.com/WDR/WDR/archive/master.zip) and
  extracting it

From now on, the directory where WDR repo was cloned or the archive extracted to
will be referred to as *WDR_HOME*.

## Installing Jython

WebSphere client does not set up Jython, so the installation needs to be done
explicitly. The easiest way to install Jython is to use WDR-provided script,
which works identically between hardware/OS platforms.

The recipe differs slightly between WAS clients version 9.0+ and previous
versions, due to the fact that prior to WAS 9 only Jython 2.1 was supported.

So, for WAS 6.1, 7.0, 8.0, 8.5 and 8.5.5 the installation is done using this way:

```sh
${WAS_CLIENT_HOME}/bin/ws_ant.sh -f ${WDR_HOME}/utilities/client-setup/build.xml jython_pre9
```

For WAS 9.0 and newer, Jython is installed like this:

```sh
${WAS_CLIENT_HOME}/bin/ws_ant.sh -f ${WDR_HOME}/utilities/client-setup/build.xml jython_9
```

The installation may take a little while depending on internet connection speed.

Some URLs accessed during Jython installation may use strong ciphers, which in
turn requires installing [unrestricted SDK JCE policy files](https://www-01.ibm.com/marketing/iwm/iwm/web/reg/pick.do?source=jcesdk)
to WAS Client's Java SDK.

### Troubleshootning and sppeding up Jython installation

The installer downloads Jython distributions from public Maven repository. In
case of any issues with this download (no Internet access, slow link, firewall,
etc.), the installer can make use custom URLs for downloads.

The URLs can be configured in `~/.wdr/wdr.jython.urls.properties` file. The
template can be copied from `${WDR_HOME/utilities/client-setup/wdr.jython.urls.properties`.

The installer may also use proxy, which can be configured via *ANT_OPTS*
variable.

On Linux/Unix:

```sh
export ANT_OPTS="-Dhttp.proxyHost=proxy -Dhttp.proxyPort=8080"
```

On Windows:

```bat
set ANT_OPTS="-Dhttp.proxyHost=proxy -Dhttp.proxyPort=8080"
```

## Configuring installed WAS runtimes in WDR

WDR can utilize multiple WAS client installations coexisting on the same machine
in order to connect to different versions of WAS. WAS clients are called
*runtimes* in WDR terminology. WDR needs to know where WAS clients were
installed in order to make use of them.

> In previous versions of WDR, the runtimes used to be configured in
``<WDR_HOME>/runtimes.<bat|sh>`` files. This configuration has been deprecated
since version 0.8. If the `runtimes.<bat|sh>` file exists, it is still being
used, however a deprecation warning is being logged. The old way of configuring
runtimes will be removed in future releases of WDR, therefore it is recommended
to switch to new method of configuring environments by removing the
`runtime.<sh|bat>` file and following instructions below.

A *runtime* is an alias for locally installed WAS client, its Java SDK and
Jython. The name of the alias maps to a script that defines certain variables.
The launcher script for WDR (the `wdr.<sh|bat>` mentioned before) looks up
runtime scripts in certain well-known directories in specific order. The
ordering of those lookups is strictly determined, allowing for overriding of
defaults that come with WDR, without a need to modify any files and without
risking any conflicts during WDR updates.

On Unix/Linux, a `<runtime>.sh` file is being looked up in the following
*runtimes* directories:

* `${HOME}/.wdr/runtimes`
* `${WDR_HOME}/runtimes`
* `${WDR_HOME}/runtimes.default`

On Windows, the runtime is defined in `<runtime>.bat` and is being looked up in:

* `%USERPROFILE%\.wdr\runtimes`
* `%WDR_HOME%\runtimes`
* `%WDR_HOME%\runtimes.default`

The `<WDR_HOME>/runtimes.default` contains WDR-predefined runtimes. Those are
not meant to be modified by the user. Should any customization to those files be
necessary, it is recommended to copy relevant files to either
`<WDR_HOME>/runtimes` (possibly creating the directory first) or
`<HOME>/.wdr/runtimes` and then editing the copy. This way of defining
environments allows users to override WDR definitions without a risk of running
into conflicts with WDR updates in the future.

## Configuring access to WAS environments

In WDR terminology, the *environment* is an alias (easy to recall and type) to
a WAS cell. The alias maps to a name of directory containing a set of files that
tell WAS client where to connect to, what credentials to use, what SSL certs to
trust, etc. The environments are completely isolated from each other.

The directory representing the environment resides in
`<HOME>/.wdr/environments/<environent>` directory and contains:

* soap.properties

* wsadmin.properties

* ssl.client.props

* key.p12 and trust.p12

An environment can be defined by creating an environment's directory and
populating necessary .properties files based on templates below. The *key.p12*
and *trust.p12* files (which represent the key store and the trust store) can be
created automatically during the first connection attempt or managed using
`ikeyman` or `keytool`.

Sections below provide templates for .properties files required.

### soap.properties

```properties
com.ibm.SOAP.securityEnabled=true

com.ibm.SOAP.authenticationTarget=BasicAuth
com.ibm.SOAP.loginUserid=<WAS_ADMIN_USERID>
com.ibm.SOAP.loginPassword=<WAS_ADMIN_PASSWORD>

com.ibm.SOAP.loginSource=none
com.ibm.SOAP.requestTimeout=180
com.ibm.ssl.alias=DefaultSSLSettings

com.ibm.ws.management.connector.soap.keepAlive=true
```

### wsadmin.properties

```properties
com.ibm.ws.scripting.connectionType=SOAP
java.net.preferIPv4Stack=true
com.ibm.ws.scripting.defaultLang=jython
com.ibm.ws.scripting.echoparams=false
com.ibm.ws.scripting.traceFile=tmp/wsadmin.traceout
com.ibm.ws.scripting.validationOutput=tmp/wsadmin.valout
com.ibm.ws.scripting.tempdir=tmp/
com.ibm.ws.scripting.connectionType=SOAP
com.ibm.ws.scripting.host=<SERVER_HOST_NAME>
com.ibm.ws.scripting.port=<SOAP_CONNECTOR_PORT>
```

### ssl.client.props

```properties
#-------------------------------------------------------------------------
# Global SSL Properties (applies to entire process)
#-------------------------------------------------------------------------
com.ibm.ssl.defaultAlias=DefaultSSLSettings
com.ibm.ssl.performURLHostNameVerification=true
com.ibm.ssl.validationEnabled=true
com.ibm.security.useFIPS=false
user.root=props

#-------------------------------------------------------------------------
# This SSL configuration is used for all client SSL connections, by default
#-------------------------------------------------------------------------
com.ibm.ssl.alias=DefaultSSLSettings
com.ibm.ssl.protocol=SSL_TLSv2
com.ibm.ssl.securityLevel=HIGH
com.ibm.ssl.trustManager=IbmPKIX
com.ibm.ssl.keyManager=IbmX509
com.ibm.ssl.contextProvider=IBMJSSE2
com.ibm.ssl.enableSignerExchangePrompt=gui

# KeyStore information
com.ibm.ssl.keyStoreName=ClientDefaultKeyStore
com.ibm.ssl.keyStore=${user.root}/key.p12
# feel free to change this password:
com.ibm.ssl.keyStorePassword=WebAS
com.ibm.ssl.keyStoreType=PKCS12
com.ibm.ssl.keyStoreProvider=IBMJCE
com.ibm.ssl.keyStoreFileBased=true

# TrustStore information
com.ibm.ssl.trustStoreName=ClientDefaultTrustStore
com.ibm.ssl.trustStore=${user.root}/trust.p12
# feel free to change this password:
com.ibm.ssl.trustStorePassword=WebAS
com.ibm.ssl.trustStoreType=PKCS12
com.ibm.ssl.trustStoreProvider=IBMJCE
com.ibm.ssl.trustStoreFileBased=true
com.ibm.ssl.trustStoreReadOnly=false
```

# Verifying your installation and configuration

Once WDR, WAS client, Jython, runtimes and environents are set up, everything
can be tested by simply launching WDR.

On Linux/Unix:

```sh
<WDR_HOME>/wdr.sh <runtime> <environent>
```

On Windows:

```bat
<WDR_HOME>/wdr.bat <runtime> <environent>
```

More specifically, the command to connect to *prod_hr* environment using
*was90* runtime, if WDR is installed in `/opt/WDR`, would look like this on
Linux/Unix:

```sh
/opt/WDR/wdr.sh was90 prod_hr
```

The command on Windows, if WDR is installed in `C:\WDR`, would look as follows:

```bat
C:\WDR\wdr.bat was90 prod_hr
```

The initial connection may display a prompt to accept server's signer
certificate.

On successful connection, an interactive WDR session will open:

    WASX7209I: Connected to process "dmgr" on node wdrDMgrNode using SOAP connector;  The type of process is: DeploymentManager
    2017-03-06 12:06:06,766 [INFO] using WDR version 0.8
    2017-03-06 12:06:06,776 [INFO] the client is connected to host wdrdmgr:8879 using SOAP connector
    2017-03-06 12:06:06,782 [INFO] the target process is wdrCell/wdrDMgrNode/dmgr
    WASX7031I: For help, enter: "print Help.help()"
    wsadmin>print getJMXMBean1(type='Server',name='dmgr').state
    STARTED
    wsadmin>reset()
    wsadmin>exit

# Optional, yet very convenient - `rlwrap`

Built-in interactive shell for WDR/wsadmin/Jython can be extended to include
command history and more convenient command-line-editing features on Linux/Unix
by installing `rlwrap` tool. Please consult OS-specific instructions on how to
install *rlwrap* package.
