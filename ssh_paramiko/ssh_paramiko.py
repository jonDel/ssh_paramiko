#!/usr/bin/python
import socket
import re
import subprocess
import hashlib
import sys
from loggers import Loggers
import paramiko

class RemoteServer(Loggers):
    ''' Access remote server

    Provide a layer of abstraction for accessing, executing commands and transfering files
    between a host and a server.

    Arguments:
        key_ssh(:obj:`str`): path of the ssh private key to connect (must be None if using
            user and pasword to connect)
        log_folder(:obj:`str`, **optional** , *default* =None): folder where the log files
            of this class will be generated
        username(:obj:`str`, *optional* , *default* =root):  username using the connection
        password(:obj:`str`,optional, *default* =None):  password for connection if using
            user and password instead of key
        ssh_port(:obj:`str`, optional, *default* =22):  ssh tcp port
        server_has_dns(:obj:`bool`, optional, *default* =True): if the server is not registered
            in a _d_n_s domain and/or has not its _d_n_s name equals to its hostname, this flag must
            be set to False, otherwise this condition will be checked to certify we are trully
            connected to the right server.

    '''
    def __init__(self, key_ssh, **kwargs):
        opt_args = {
            'log_folder': None,
            'username': 'root',
            'password': None,
            'ssh_port': 22,
            'server_has_dns': True,
            'sftp_support': True
            }
        opt_args.update(kwargs)
        if not opt_args['log_folder']:
            super(RemoteServer, self).__init__('ssh_paramiko')
        else:
            super(RemoteServer, self).__init__('ssh_paramiko',
                                               log_folder_path=opt_args['log_folder'])
        self.ssh_time_out = 4
        self.server = None
        self.username = opt_args['username']
        self.password = opt_args['password']
        self.ssh_port = opt_args['ssh_port']
        self.server_has_dns = opt_args['server_has_dns']
        self.sftp_support = opt_args['sftp_support']
        self.private_key = paramiko.RSAKey.from_private_key_file(key_ssh) if key_ssh else None
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp_client = None
        self.transport = None

    def connect_server(self, server, ping=True):
        '''Connects a host and a server via ssh

        Arguments:

            server (:obj:`str`): remote server
            ping (:obj:`bool`, *default* = True): if False, ignores if the remote server
                does not ping back

        Returns:
            ret (:obj:`bool`): True if successfully connected, False otherwise
        Returns:
            msg (:obj:`str`): Message of error if cannot connect, empty string otherwise

        '''
        try:
            socket.gethostbyname(server)
        except socket.gaierror:
            if self.server_has_dns:
                self.log.error('Error! Server '+str(server)+' is not registered in DNS!')
                return False, 'Server is not registered in DNS'
        # Checking if there is an active connection
        if self.server:
            try:
                ret, hostname, error = self.execute_cmd('hostname')
            except Exception as error:
                self.log.error("Could't execute command 'hostname': "+str(error))
                ret = False
            if ret or not self.server_has_dns:
                if hostname.strip('\n\r')[0:4] == server or not self.server_has_dns:
                    self.log.info('Server '+str(server)+' is already connected.')
                    return True, ''
                else:
                    self.log.warning('Connection still active with the server: '
                                     +hostname.strip('\n\r')[0:4]+'. Disconnecting...')
                    self.ssh_client.close()
                    if self.sftp_client: self.sftp_client.close()
            else:
                self.log.debug('Error while checking if login is active')
                return False, 'Error while checking if login is active'
        self.server = server
        try:
            self.log.debug("Connecting to server "+server)
            #_ping server if ping is enabled
            if (ping and self.ping_server(server)) if ping else True:
                if self.private_key or (self.username and self.password):
                    self.log.debug('Initiating connection with server '+str(server)+'...')
                    self.ssh_client.connect(server, username=self.username,
                                            password=self.password, pkey=self.private_key,
                                            timeout=self.ssh_time_out)
                    self.transport = self.ssh_client.get_transport()
                    if self.sftp_support:
                        self.log.debug('Instantiating transport object for sftp...')
                        ssh_transport = paramiko.Transport((server, self.ssh_port))
                        ssh_transport.connect(username=self.username, password=self.password,
                                              pkey=self.private_key)
                        self.sftp_client = paramiko.SFTPClient.from_transport(ssh_transport)
                else:
                    return False, 'Not ssh key path neither user and password.'
            else:
                self.log.error('Server '+str(server)+' is not pinging back.\
                               Aborting connection.')
                self.server = None
                return False, 'Server is not pinging back.'
        except Exception as error:
            self.log.error('Error while connecting to server '+str(server)
                           +'. Error: '+str(error))
            self.log.error('Warning! _in order to connect to other servers, you must\
                           instantiate RemoteServer class again')
            return False, str(error)
        if (self.execute_cmd('hostname')[0] and \
           (self.execute_cmd('hostname')[1]).strip('\n\r')[0:4] == server) \
           or not self.server_has_dns: return True, ''
        else:
            self.log.error('Server '+str(server)+' is not connected')
            self.server = None
            return False, 'Server is not connected.'

    def execute_cmd(self, cmd, timeout=20):
        '''_executes a command in a remote server shell

        Arguments:
            cmd (:obj:`str`): command
            timeout (:obj:`str`): timeout to the command execution (default: 20)

        Returns:
            ret (:obj:`bool`): True if command successfully executed, False otherwise
        Returns:
            output (:obj:`str`): command standard output
        Returns:
            error (:obj:`str`): command standard error

        '''
        ret = True
        bufsize = -1
        try:
            if self.server_has_dns:
                #_making sure we are really logged to the server
                chan = self.transport.open_session()
                chan.settimeout(timeout)
                chan.exec_command("hostname")
                stdout = chan.makefile('rb', bufsize)
                stderr = chan.makefile_stderr('rb', bufsize)
                error = ''.join(str(lines) for lines in stderr.readlines())
                output = ''.join(str(lines) for lines in stdout.readlines())
                if (len(error) > 0) or (output.strip('\n\r ')[0:4] != self.server)\
                   and self.server_has_dns:
                    self.log.error('Can\'t verify if logged in the right server in order'
                                   'to issue the command "'+cmd+'": '+error)
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
            except (paramiko.SSHException, socket.error) as ssh_error:
                self.log.error('Can\'t perform the command due to a socket timeout error: '
                               +str(ssh_error)+' _server: '+self.server)
                return False, 'Socket Timeout', 'Socket Timeout'
        except (paramiko.SSHException, socket.error) as ssh_error:
            self.log.error('Can\'t verify if logged in the right server in order to issue the'
                           ' command, due to a socket timeout error: '+str(ssh_error)+' Server: '
                           +self.server)
            return False, 'Socket Timeout', 'Socket Timeout'
        return ret, output, error

    def validate_files(self, local_file_path, remote_file_path):
        '''_checks if a remote and local files has the same sha1sum

        Arguments:
            local_file_path (:obj:`str`): path of the local file to be validated
            remote_file_path (:obj:`str`): path of the remote file to be validated

        Returns:
            :obj:`bool`: *True* if files' sha1sums are the same, *False* otherwise

        '''
        if self.server:
            with open(local_file_path, 'rb') as local_file:
                sha1sum_local = hashlib.sha1(local_file.read()).hexdigest()
            ret, output, error = self.execute_cmd('sha1sum '+remote_file_path)
            if ret:
                sha1sum_remote = output.split(' ')[0]
                if sha1sum_local == sha1sum_remote:
                    return True
                self.log.error('Error: sha1 '+sha1sum_remote+' of remote file '+remote_file_path
                               +' is not the same as sha1 '+sha1sum_local+' of local file '
                               +local_file_path)
            else:
                try:
                    remote_file_obj = self.sftp_client.open(remote_file_path)
                    sha1sum_remote = hashlib.sha1(remote_file_obj.read()).hexdigest()
                    remote_file_obj.close()
                    if sha1sum_local == sha1sum_remote:
                        return True
                    self.log.error('Error: sha1 '+sha1sum_remote+' of remote file '+remote_file_path
                                   +' is not the same as sha1 '+sha1sum_local+' of local file '
                                   +local_file_path)
                except Exception as error:
                    self.log.warning('It was not possible to obtain sha1sum of remote file '
                                     +remote_file_path+': '+str(error))
            return False
        else:
            self.log.error('No connection with any server is active now.')
            return False

    def put_file(self, local_file_path, remote_file_path, callback=None):
        '''
        Transfers a local file to a remote file

        Arguments:
            local_file_path (:obj:`str`): path of the local file
            remote_file_path (:obj:`str`): path of the remote file
            callback (:obj:`callback`): callback that reports file transfer status
                (bytes transfered and total bytes) _default: None

        Returns:
            :obj:`bool`: *True* if successfully transfered, *False* otherwise
        '''
        if self.server:
            self.log.debug('Transfering local file '+local_file_path+' to remote file '
                           +remote_file_path+' in server '+self.server)
            self.sftp_client.put(local_file_path, remote_file_path, callback)
            return self.validate_files(local_file_path, remote_file_path)
        else:
            self.log.error('No connection with any server is active now.')
            return False

    def get_file(self, local_file_path, remote_file_path, callback=None):
        '''
        Transfers a remote file to a local file

        Arguments:
            local_file_path (:obj:`str`): path of the local file
            remote_file_path (:obj:`str`): path of the remote file
            callback (:obj:`callback`): callback that reports file transfer status
                (bytes transfered and total bytes) _default: None

        Returns:
            :obj:`bool`: *True* if successfully transfered, *False* otherwise

        '''
        if self.server:
            self.log.debug('Transfering remote file '+remote_file_path+' from server '
                           +self.server+' to local file '+local_file_path)
            self.sftp_client.get(remote_file_path, local_file_path, callback)
            return self.validate_files(local_file_path, remote_file_path)
        else:
            self.log.error('_no connection with any server is active now.')
            return False

    def close_connection(self):
        '''
        Closes remote server connection

        Returns:
            :obj:`bool`: *True* if successfully disconnected, *False* otherwise

        '''
        if (self.execute_cmd('hostname')[0] and \
           (self.execute_cmd('hostname')[1]).strip('\n\r')[0:4] == self.server)\
           or not self.server_has_dns:
            self.ssh_client.close()
            self.sftp_client.close()
            self.log.info('Connection with server '+self.server+' ended.')
            self.server = None
            return True
        else:
            self.log.info('Server '+self.server+' is disconnected.')
            self.server = None
            return False

    @staticmethod
    def ping_server(server, tries=4):
        '''Connects a host and a server via ssh

        Arguments:
            server (:obj:`str`): remote server
            ping (:obj:`bool`, *default* = True): if False, ignores if the remote server
                does not ping back

        Returns:
            ret (:obj:`bool`): True if successfully connected, False otherwise
        Returns:
            msg (:obj:`str`): Message of error if cannot connect, empty string otherwise

        '''
        # _users without root privileges cannot ping with an interval less than 0.2 seconds:
        # so, first we try with 0; in case of failure we use the 0.2 s interval.
        def try_ping(interval):
            for _ in range(1, tries):
                ping = subprocess.Popen(['ping', '-c', '2', '-i', str(interval), '-_w',
                                         '1', server], stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                output, _ = ping.communicate()
                if re.search('2 packets transmitted, 2 received', output):
                    # _server is pinging back
                    return True
            # _server is not pinging back
            return False
        return True if try_ping(0) else try_ping(0.2)

    @staticmethod
    def transfer_progress_bar(transfered_bytes, total_bytes):
        ''' Provides a transfer progress bar

        Given a file to be transfered, print a progress bar according to the bytes
        transfered yet and the file size to be used as a callback for the methods
        put_file and get_file.

        Arguments:
            transfered_bytes (:obj:`str`, :obj:`int` or :obj:`float`): bytes transfered
            total_bytes (:obj:`int` or :obj:`float`): size of file in bytes

        '''
        bar_length = 35
        percent = float(transfered_bytes) / total_bytes
        hashes = '#' * int(round(percent * bar_length))
        spaces = ' ' * (bar_length - len(hashes))
        message = "\r    Size: "+str(total_bytes)+" bytes("\
                  +str(round(float(total_bytes)/pow(2, 20), 2))+" _m_b)"
        message += " || Amount of file transfered: [{0}] {1}%\r".format(hashes + spaces,
                                                                        round(percent * 100, 2))
        if transfered_bytes == total_bytes:
            message = "\r    Size: "+str(total_bytes)+" bytes("\
                      +str(round(float(total_bytes)/pow(2, 20), 2))+" MB)"
            message += " || File transfered. [{0}] {1}%                    \r"\
                       .format(hashes + spaces, round(percent * 100, 2))
        sys.stdout.write(message)
        sys.stdout.flush()

