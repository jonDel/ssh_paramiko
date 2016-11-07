#!/usr/bin/python
import socket
import re
import subprocess
from loggers import Loggers
import hashlib
import sys
import paramiko

class RemoteServer(Loggers):
	'''
	Provide a layer of abstraction for accessing, executing commands and transfering files between a host and a server.
	
	Arguments:
			keySSH(:obj:`str`): path of the ssh private key to connect (must be None if using user and pasword to connect)
			logFolder(:obj:`str`, **optional** , *default* =None): folder where the log files of this class will be generated
			username(:obj:`str`, *optional* , *default* =root):  username using the connection
			password(:obj:`str`,optional, *default* =None):  password for connection if using user and password instead of key
			sshPort(:obj:`str`, optional, *default* =22):  ssh tcp port
			serverHasDns(:obj:`bool`, optional, *default* =True): if the server is not registered in a DNS domain and/or has
				not its DNS name equals to its hostname, this flag must de set to False, otherwise this condition will be
				checked to certify we are trukky connected to the right server.
	'''
	def __init__(self, keySSH, **kwargs):
		optArgs = {
			'logFolder'    : None,
			'username'     : 'root',
			'password'     : None,
			'sshPort'      : 22,
			'serverHasDns'  : True,
			'sftpSupport'  : True
		}
		optArgs.update(kwargs)
		if not optArgs['logFolder']:
			super(RemoteServer, self).__init__('sshParamiko')
		else:
			super(RemoteServer, self).__init__('sshParamiko',logFolderPath=optArgs['logFolder'])
		self.sshTimeOut = 4
		self.server   = None
		self.username = optArgs['username']
		self.password = optArgs['password']
		self.sshPort = optArgs['sshPort']
		self.serverHasDns = optArgs['serverHasDns']
		self.sftpSupport = optArgs['sftpSupport']
		self.privateKey = paramiko.RSAKey.from_private_key_file(keySSH) if keySSH else None
		self.sshClient = paramiko.SSHClient()
		self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	def connectServer(self, server, ping=True):
		'''
		Connects a host and a server via ssh
		
		Arguments:
			server (:obj:`str`): remote server
			ping (:obj:`bool`): if False, ignores if the remote server does not ping back ( *default* =True)
		Returns:
			ret (:obj:`bool`): True if successfully connected, False otherwise
		Returns:
			msg (:obj:`str`): Message of error if cannot connect, empty string otherwise
		'''
		try:
			socket.gethostbyname(server)
		except:
			if self.serverHasDns:
				self.log.error ('Error! Server '+str(server)+' is not registered in DNS!')
				return False, 'Server is not registered in DNS'
		finally:
			# Checking if there is an active connection
			if self.server:
				try:
					ret, hostname, error = self.executeCmd('hostname')
				except:
					ret = False
				if ret or not (self.serverHasDns):
					if hostname.strip('\n\r')[0:4] == server or not (self.serverHasDns):
						self.log.info('Server '+str(server)+' is already connected.')
						return True, ''
					else:
						self.log.warning('Connection still active with the server: '+hostname.strip('\n\r')[0:4]+'. Disconnecting...')
						self.sshClient.close()
						self.sftpClient.close()
				else:
					self.log.debug('Error while checking if login is active')
					return False, 'Error while checking if login is active'
			self.server = server
			try:
				self.log.debug("Connecting to server "+server)
				#Ping server if ping is enabled
				if ((ping and self.pingServer(server)) if ping else True):
					if self.privateKey or (self.username and self.password):
						self.log.debug('Initiating connection with server '+str(server)+'...')
						self.sshClient.connect(server, username=self.username, password=self.password, pkey=self.privateKey, timeout=self.sshTimeOut)
						self.transport = self.sshClient.get_transport()
						if self.sftpSupport:
							self.log.debug('Instantiating transport object for sftp...')
							sshTransport = paramiko.Transport((server,self.sshPort))
							sshTransport.connect( username=self.username, password=self.password, pkey=self.privateKey)
							self.sftpClient = paramiko.SFTPClient.from_transport(sshTransport)
					else:
						return False, 'Not ssh key path neither user and password.'
				else:
					self.log.error('Server '+str(server)+' is not pinging back. Aborting connection.')
					self.server = None
					return False, 'Server is not pinging back.'
			except Exception as error:
				self.log.error('Error while connecting to server '+str(server)+'. Error: '+str(error))
				self.log.error('Warning! In order to connect to other servers, you must instantiate RemoteServer class again')
				return False, str(error)
			if (self.executeCmd('hostname')[0] and (self.executeCmd('hostname')[1]).strip('\n\r')[0:4] == server) or not (self.serverHasDns):
				return True, ''
			else:
				self.log.error('Server '+str(server)+' is not connected')
				self.server = None
				return False, 'Server is not connected.'

	def executeCmd(self, cmd, timeout=20):
		'''
		Executes a command in a remote server shell
		
		Arguments:
			cmd (:obj:`str`): command
			timeout (:obj:`str`): timeout to the command execution (default: 20)
		Returns:
			ret (:obj:`bool`): True if command successfully executed, False otherwise
		Returns:
			output (:obj:`str`): command standard output
		Returns:
			error (:obj:`str`):  command standard error
		'''
		ret = True
		bufsize=-1
		try:
			if self.serverHasDns:
				#Making sure we are really logged to the server
				chan = self.transport.open_session()
				chan.settimeout(timeout)
				chan.exec_command("hostname")
				stdout = chan.makefile('rb', bufsize)
				stderr = chan.makefile_stderr('rb', bufsize)
				error = ''.join(str(lines) for lines in stderr.readlines())
				output = ''.join(str(lines) for lines in stdout.readlines())
				if (len(error) > 0) or (output.strip('\n\r ')[0:4] != self.server) and self.serverHasDns:
					self.log.error('Can\'t verify if logged in the right server in order to issue the command "'+cmd+'": '+error)
					return False, output
			else:
				pass
			try:
				chan = self.transport.open_session()
				chan.settimeout(timeout)
				chan.exec_command(cmd)
				stdout = chan.makefile('rb', bufsize)
				stderr = chan.makefile_stderr('rb', bufsize)
				error = ''.join(str(lines) for lines in stderr.readlines())
				output = ''.join(str(lines) for lines in stdout.readlines())
				if len(error) > 0:
					self.log.error('Error while executing command "'+cmd+'": '+error)
					self.log.error('Command "'+cmd+'" output: '+output)
					ret = False
			except (paramiko.SSHException, socket.error) as se:
				self.log.error('Can\'t perform the command due to a socket timeout error: '+str(se)+' Server: '+self.server)
				return False,'Socket Timeout','Socket Timeout'
		except (paramiko.SSHException, socket.error) as se:
			self.log.error('Can\'t verify if logged in the right server in order to issue the command, due to a socket timeout error: '+str(se)+' Server: '+self.server)
			return False,'Socket Timeout','Socket Timeout'
		return ret, output, error

	def validateFiles(self, localFilePath,remoteFilePath):
		'''
		Checks if a remote and local files has the same sha1sum
		
		Arguments:
			localFilePath (:obj:`str`): path of the local file to be validated
			remoteFilePath (:obj:`str`): path of the remote file to be validated
		Returns:
			:obj:`bool`: *True* if files' sha1sums are the same, *False* otherwise
		'''
		if self.server:
			with open(localFilePath, 'rb') as f:
				sha1sumLocal = hashlib.sha1(f.read()).hexdigest()
			ret,output,error = self.executeCmd('sha1sum '+remoteFilePath)
			if ret:
				sha1sumRemote = output.split(' ')[0]
				if sha1sumLocal == sha1sumRemote:
					return True
				self.log.error('Error: sha1 '+sha1sumRemote+' of remote file '+remoteFilePath+' is not the same as sha1 '+sha1sumLocal+' of local file '+localFilePath)
			else:
				try:
					remoteFileObj =self.sftpClient.open(remoteFilePath)
					sha1sumRemote = hashlib.sha1(remoteFileObj.read()).hexdigest()
					remoteFileObj.close()
					if sha1sumLocal == sha1sumRemote:
						return True
					self.log.error('Error: sha1 '+sha1sumRemote+' of remote file '+remoteFilePath+' is not the same as sha1 '+sha1sumLocal+' of local file '+localFilePath)
				except Exception as error:
					self.log.warning('I was not possible to obtain sha1sum of remote file '+remoteFilePath+': '+str(error))
			return False
		else:
			self.log.error('No connection with any server is active now.')
			return False

	def putFile(self, localFilePath, remoteFilePath, callBack=None):
		'''
		Transfers a local file to a remote file
		
		Arguments:
			localFilePath (:obj:`str`): path of the local file
			remoteFilePath (:obj:`str`): path of the remote file
			callBack (:obj:`callback`): callback that reports file transfer status (bytes transfered and total bytes) Default: None
		Returns:
			:obj:`bool`: *True* if successfully transfered, *False* otherwise
		'''
		if self.server:
			self.log.debug('Transfering local file '+localFilePath+' to remote file '+remoteFilePath+' in server '+self.server)
			self.sftpClient.put(localFilePath,remoteFilePath,callBack)
			return self.validateFiles(localFilePath,remoteFilePath)
		else:
			self.log.error('No connection with any server is active now.')
			return False

	def getFile(self, localFilePath, remoteFilePath, callBack=None):
		'''
		Transfers a remote file to a local file
		
		Arguments:
			localFilePath (:obj:`str`): path of the local file
			remoteFilePath (:obj:`str`): path of the remote file
			callBack (:obj:`callback`): callback that reports file transfer status (bytes transfered and total bytes) Default: None
		Returns:
			:obj:`bool`: *True* if successfully transfered, *False* otherwise
		'''
		if self.server:
			self.log.debug('Transfering remote file '+remoteFilePath+' from server '+self.server+' to local file '+localFilePath)
			self.sftpClient.get(remoteFilePath,localFilePath,callBack)
			return self.validateFiles(localFilePath,remoteFilePath)
		else:
			self.log.error('No connection with any server is active now.')
			return False

	def closeConnection(self):
		'''
		Description: closes remote server connection
		
		Returns:
			:obj:`bool`: *True* if successfully disconnected, *False* otherwise
		'''
		if (self.executeCmd('hostname')[0] and (self.executeCmd('hostname')[1]).strip('\n\r')[0:4] == self.server) or not (self.serverHasDns):
			self.sshClient.close()
			self.sftpClient.close()
			self.log.info('Connection with server '+self.server+' ended.')
			self.server = None
			return True
		else:
			self.log.info('Server '+self.server+' is disconnected.')
			self.server = None
			return False

	@staticmethod
	def pingServer(server, tries = 4):
		'''
		Ping a remote server
		
		Arguments:
			server(:obj:`str`): server name or ip
			tries (:obj:`str`, **optional** ): number of ping tries before quiting. Default:4
		Returns:
			:obj:`bool`: *True* if server pings back, *False* otherwise
		'''
		# Users without root privileges cannot ping with an interval less than 0.2 seconds:
		# so, first we try with 0; in case of failure we use the 0.2 s interval.
		def tryPing(interval):
			for i in range(1,tries):
				ping = subprocess.Popen(['ping','-c','2','-i',str(interval),'-W','1',server], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				output, error = ping.communicate()
				if re.search('2 packets transmitted, 2 received',output):
					# Server is pinging back
					return True
			# Server is not pinging back
			return False
		return True if tryPing(0) else tryPing(0.2)

	@staticmethod
	def transferProgressBar(transferedBytes,totalBytes):
		'''
		Given a file to be transfered, print a progress bar according to the bytes transfered yet and the file size
		to be used as a callback for the methods putFile and getFile.

		Arguments:
			transferedBytes (:obj:`str`, :obj:`int` or :obj:`float`): bytes transfered
			totalBytes (:obj:`int` or :obj:`float`): size of file in bytes
		'''
		bar_length = 35
		percent = float(transferedBytes) / totalBytes
		hashes = '#' * int(round(percent * bar_length))
		spaces = ' ' * (bar_length - len(hashes))
		message = "\r    Size: "+str(totalBytes)+" bytes("+str(round(float(totalBytes)/pow(2,20),2))+" MB)"
		message = message+" || Amount of file transfered: [{0}] {1}%\r".format(hashes + spaces, round(percent * 100,2))
		if transferedBytes == totalBytes:
			message = "\r    Size: "+str(totalBytes)+" bytes("+str(round(float(totalBytes)/pow(2,20),2))+" MB)"
			message = message+" || File transfered. [{0}] {1}%                    \r".format(hashes + spaces, round(percent * 100,2))
		sys.stdout.write(message)
		sys.stdout.flush()

