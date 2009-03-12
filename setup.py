#!/usr/bin/env python
#
# setup.py for flashbake
from setuptools import setup

setup(name='flashbake',
        version='0.23.3',
        author="Thomas Gideon",
        author_email="cmdln@thecommandline.net",
        url="http://thecommandline.net",
        license="GPLv3",
        py_modules=['flashbake.commit',
            'flashbake.context',
            'flashbake.plugins.feed',
            'flashbake.plugins.timezone',
            'flashbake.plugins.uptime',
            'flashbake.plugins.weather',
            'flashbake.plugins.microblog',
            'flashbake.plugins.music'
            ],
        install_requires='''
            enum >=0.4.3
            feedparser >=4.1
            ''',
        scripts=['bin/flashbake',
            'bin/flashbakeall'])
