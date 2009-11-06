#!/usr/bin/env python
#
# setup.py for flashbake
from setuptools import setup, find_packages



setup(name='flashbake',
        version='0.26',
        author="Thomas Gideon",
        author_email="cmdln@thecommandline.net",
        url="http://thecommandline.net",
        license="GPLv3",
        packages=find_packages(exclude=['test.*']),
        install_requires='''
            enum >=0.4.3
            feedparser >=4.1
            ''',
        entry_points={
                'console_scripts': [ 'flashbake = flashbake.console:main',
                                     'flashbakeall = flashbake.console:multiple_projects' ]
                }
        )
