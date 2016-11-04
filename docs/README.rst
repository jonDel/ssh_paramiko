sshParamiko
===========

**sshParamiko** is a wrapper utility around ssh, using paramiko, to execute commands and exchange files remotelly


Executing a simple remote command
---------------------------------

.. code:: python

  >>> from sshParamiko import RemoteServer
  >>> ssh = RemoteServer('/tmp/sshkey',logFolder='.')
  >>> ssh.setLogLevel('DEBUG')
  Log: Changing log level to DEBUG | Log level:DEBUG | Date:01/11/2016 12:04:40
  >>> ssh.setLogRotateHandler(True) # set bzipped log files (sshParamiko.debug.log.bz2
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
  >>> ssh.setLogLevel('DEBUG')
  Log: Changing log level to DEBUG | Log level:DEBUG | Date:01/11/2016 12:04:40
  >>> ssh.setLogRotateHandler(True) # set bzipped log files (sshParamiko.debug.log.bz2 and
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
  >>> ssh.setLogLevel('DEBUG')
  Log: Changing log level to DEBUG | Log level:DEBUG | Date:01/11/2016 12:07:40
  >>> ssh.setLogRotateHandler(True) # set bzipped log files (sshParamiko.debug.log.bz2 and
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

https://sshParamiko.readthedocs.io/en/latest/index.html

Source Code
-----------

Feel free to fork, evaluate and contribute to this project.

Source: https://github.com/jonDel/sshParamiko

License
-------

GPLv3 licensed.

