from setuptools import setup

setup(
    name='sshParamiko',
    version='0.1',
    author='Jonatan Dellagostin',
    author_email='jdellagostin@gmail.com',
    packages=['sshParamiko'],
    license='GPLv3',
    description='Wrapper ssh using paramiko to interact with remote servers',
    long_description=open('README.rst').read(),
    install_requires=[
        "loggers >= 0.1",
        "paramiko >= 1.0",
    ],
)
