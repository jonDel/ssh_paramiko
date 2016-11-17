from setuptools import setup

setup(
    name='ssh_paramiko',
    version='0.1.2',
    author='Jonatan Dellagostin',
    author_email='jdellagostin@gmail.com',
    url='https://github.com/jonDel/ssh_paramiko',
    packages=['ssh_paramiko'],
    license='GPLv3',
    description='Wrapper ssh using paramiko to interact with remote servers',
    classifiers=[
     'Development Status :: 3 - Alpha',
     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
     'Programming Language :: Python :: 2.6',
     'Programming Language :: Python :: 2.7',
     'Topic :: System :: Networking',
     'Topic :: System :: Systems Administration',
     'Topic :: Internet :: File Transfer Protocol (FTP)',
     'Topic :: System :: Shells',
    ],
    keywords='ssh secure sftp ftp shell remote paramiko',
    long_description=open('README.rst').read(),
    install_requires=[
        "loggers >= 0.1",
        "paramiko >= 1.0",
    ],
)
