.. image:: https://readthedocs.org/projects/sshparamiko/badge/?version=master
   :target: http://sshparamiko.readthedocs.io/en/latest/?badge=master
   :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/jonDel/sshParamiko/badge.svg?branch=master
   :target: https://coveralls.io/github/jonDel/sshParamiko?branch=master

.. image:: https://landscape.io/github/jonDel/sshParamiko/master/landscape.svg?style=flat
    :target: https://landscape.io/github/jonDel/sshParamiko/master
    :alt: Code Health

.. image:: https://www.versioneye.com/user/projects/5821e46a89f0a91dbb44b40f/badge.svg?style=flat
    :target: https://www.versioneye.com/user/projects/5821e46a89f0a91dbb44b40f


sshParamiko
===========

**sshParamiko** is a wrapper utility around ssh, using paramiko, to execute commands and exchange files remotelly

Usage
=====

Executing a simple remote command
---------------------------------

.. code:: python

  >>> from sshParamiko import RemoteServer
  >>> ssh = RemoteServer('/tmp/sshkey',logFolder='.')
  >>> ssh.set_log_level('DEBUG')
  Log: Changing log level to DEBUG | Log level:DEBUG | Date:01/11/2016 12:04:40
  >>> ssh.set_log_rotate_handler(True) # set bzipped log files (sshParamiko.debug.log.bz2
    # and sshParamiko.error.log.bz2) to be rotated
  >>> ssh.connectServer('myServer')
  Log: Connecting to server myServer | Log level:DEBUG | Date:01/11/2016 12:04:41
  Log: Initiating connection with server myServer... | Log level:DEBUG | Date:01/11/2016 12:04:41
  Log: Instantiating transport object for sftp... | Log level:DEBUG | Date:01/11/2016 12:04:41
  (True, '')
  >>> ssh.executeCmd('whoami')
  (True, 'root\n', '')
  >>> ssh.closeConnection()
  Log: Connection with server myServer ended. | Log level:INFO | Date:01/11/2016 12:04:45
  True


Transfering a remote file to a local file
-----------------------------------------

.. code:: python

  >>> from sshParamiko import RemoteServer
  >>> ssh = RemoteServer('/tmp/sshkey',logFolder='.')
  >>> ssh.set_log_level('DEBUG')
  Log: Changing log level to DEBUG | Log level:DEBUG | Date:01/11/2016 12:04:40
  >>> ssh.set_log_rotate_handler(True) # set bzipped log files (sshParamiko.debug.log.bz2 and
    # sshParamiko.error.log.bz2) to be rotated
  >>> ssh.connectServer('myServer')
  Log: Connecting to server myServer | Log level:DEBUG | Date:01/11/2016 12:04:41
  Log: Initiating connection with server myServer... | Log level:DEBUG | Date:01/11/2016 12:04:41
  Log: Instantiating transport object for sftp... | Log level:DEBUG | Date:01/11/2016 12:04:41
  (True, '')
  >>> ssh.getFile('localFile.py', '/root/remoteFile.py', callBack=ssh.transferProgressBar)
  Log: Transfering remote file /root/remoteFile.py from server myServer to local file localFile.py
   | Log level:DEBUG | Date:01/11/2016 12:08:15
  TrueSize: 542 bytes(0.0 MB) || File transfered. [###################################] 100.0%
  >>> ssh.closeConnection()
  Log: Connection with server myServer ended. | Log level:INFO | Date:01/11/2016 12:04:45
  True


Transfering a local file to a remote file
-----------------------------------------

.. code:: python

  >>> from sshParamiko import RemoteServer
  >>> ssh = RemoteServer('/tmp/sshkey',logFolder='.')
  >>> ssh.set_log_level('DEBUG')
  Log: Changing log level to DEBUG | Log level:DEBUG | Date:01/11/2016 12:07:40
  >>> ssh.set_log_rotate_handler(True) # set bzipped log files (sshParamiko.debug.log.bz2 and
    # sshParamiko.error.log.bz2) to be rotated
  >>> ssh.connectServer('myServer')
  Log: Connecting to server myServer | Log level:DEBUG | Date:01/11/2016 12:07:41
  Log: Initiating connection with server myServer... | Log level:DEBUG | Date:01/11/2016 12:07:41
  Log: Instantiating transport object for sftp... | Log level:DEBUG | Date:01/11/2016 12:07:41
  (True, '')
  >>> ssh.putFile('localFile.py', '/root/remoteFile.py', callBack=ssh.transferProgressBar)
  Log: Transfering local file localFile.py to remote file /root/remoteFile.py in server myServer |
   Log level:DEBUG | Date:01/11/2016 12:07:44
  TrueSize: 542 bytes(0.0 MB) || File transfered. [###################################] 100.0%
  >>> ssh.closeConnection()
  Log: Connection with server myServer ended. | Log level:INFO | Date:01/11/2016 12:07:44
  True


Installation
------------

To install sshParamiko, simply run:

::

  $ pip install sshParamiko

sshParamiko is compatible with Python 2.6+

Documentation
-------------

https://sshparamiko.readthedocs.io

Source Code
-----------

Feel free to fork, evaluate and contribute to this project.

Source: https://github.com/jonDel/sshParamiko

License
-------

GPLv3 licensed.

