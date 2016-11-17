.. image:: https://readthedocs.org/projects/ssh-paramiko/badge/?version=master
   :target: http://ssh-paramiko.readthedocs.io/en/latest/?badge=master
   :alt: Documentation Status

.. image:: https://coveralls.io/repos/github/jonDel/ssh_paramiko/badge.svg?branch=master
   :target: https://coveralls.io/github/jonDel/ssh_paramiko?branch=master

.. image:: https://landscape.io/github/jonDel/ssh_paramiko/master/landscape.svg?style=flat
    :target: https://landscape.io/github/jonDel/ssh_paramiko/master
    :alt: Code Health

.. image:: https://www.versioneye.com/user/projects/582daf4ac8dd330040426fb0/badge.svg?style=flat
    :target: https://www.versioneye.com/user/projects/582daf4ac8dd330040426fb0


ssh_paramiko
============

**ssh_paramiko** is a wrapper utility around ssh, using paramiko, to execute commands and exchange files remotelly

Usage
=====

Executing a simple remote command
---------------------------------

.. code:: python

  >>> from ssh_paramiko import RemoteServer
  >>> ssh = RemoteServer('/tmp/sshkey',logFolder='.')
  >>> ssh.set_log_level('DEBUG')
  Log: Changing log level to DEBUG | Log level:DEBUG | Date:01/11/2016 12:04:40
  >>> ssh.set_log_rotate_handler(True) # set bzipped log files (ssh_paramiko.debug.log.bz2
    # and ssh_paramiko.error.log.bz2) to be rotated
  >>> ssh.connect_server('myServer')
  Log: Connecting to server myServer | Log level:DEBUG | Date:01/11/2016 12:04:41
  Log: Initiating connection with server myServer... | Log level:DEBUG | Date:01/11/2016 12:04:41
  Log: Instantiating transport object for sftp... | Log level:DEBUG | Date:01/11/2016 12:04:41
  (True, '')
  >>> ssh.execute_cmd('whoami')
  (True, 'root\n', '')
  >>> ssh.close_connection()
  Log: Connection with server myServer ended. | Log level:INFO | Date:01/11/2016 12:04:45
  True


Transfering a remote file to a local file
-----------------------------------------

.. code:: python

  >>> from ssh_paramiko import RemoteServer
  >>> ssh = RemoteServer('/tmp/sshkey',logFolder='.')
  >>> ssh.set_log_level('DEBUG')
  Log: Changing log level to DEBUG | Log level:DEBUG | Date:01/11/2016 12:04:40
  >>> ssh.set_log_rotate_handler(True) # set bzipped log files (ssh_paramiko.debug.log.bz2 and
    # ssh_paramiko.error.log.bz2) to be rotated
  >>> ssh.connect_server('myServer')
  Log: Connecting to server myServer | Log level:DEBUG | Date:01/11/2016 12:04:41
  Log: Initiating connection with server myServer... | Log level:DEBUG | Date:01/11/2016 12:04:41
  Log: Instantiating transport object for sftp... | Log level:DEBUG | Date:01/11/2016 12:04:41
  (True, '')
  >>> ssh.get_file('local_file.py', '/root/remote_file.py', callBack=ssh.transferProgressBar)
  Log: Transfering remote file /root/remote_file.py from server myServer to local file local_file.py
   | Log level:DEBUG | Date:01/11/2016 12:08:15
  TrueSize: 542 bytes(0.0 MB) || File transfered. [###################################] 100.0%
  >>> ssh.close_connection()
  Log: Connection with server myServer ended. | Log level:INFO | Date:01/11/2016 12:04:45
  True


Transfering a local file to a remote file
-----------------------------------------

.. code:: python

  >>> from ssh_paramiko import RemoteServer
  >>> ssh = RemoteServer('/tmp/sshkey',logFolder='.')
  >>> ssh.set_log_level('DEBUG')
  Log: Changing log level to DEBUG | Log level:DEBUG | Date:01/11/2016 12:07:40
  >>> ssh.set_log_rotate_handler(True) # set bzipped log files (ssh_paramiko.debug.log.bz2 and
    # ssh_paramiko.error.log.bz2) to be rotated
  >>> ssh.connect_server('myServer')
  Log: Connecting to server myServer | Log level:DEBUG | Date:01/11/2016 12:07:41
  Log: Initiating connection with server myServer... | Log level:DEBUG | Date:01/11/2016 12:07:41
  Log: Instantiating transport object for sftp... | Log level:DEBUG | Date:01/11/2016 12:07:41
  (True, '')
  >>> ssh.put_file('local_file.py', '/root/remote_file.py', callBack=ssh.transferProgressBar)
  Log: Transfering local file local_file.py to remote file /root/remote_file.py in server myServer |
   Log level:DEBUG | Date:01/11/2016 12:07:44
  TrueSize: 542 bytes(0.0 MB) || File transfered. [###################################] 100.0%
  >>> ssh.close_connection()
  Log: Connection with server myServer ended. | Log level:INFO | Date:01/11/2016 12:07:44
  True


Installation
------------

To install ssh_paramiko, simply run:

::

  $ pip install ssh_paramiko

ssh_paramiko is compatible with Python 2.6+

Documentation
-------------

https://ssh_paramiko.readthedocs.io

Source Code
-----------

Feel free to fork, evaluate and contribute to this project.

Source: https://github.com/jonDel/ssh_paramiko

License
-------

GPLv3 licensed.

