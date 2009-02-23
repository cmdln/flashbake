#!/usr/bin/env python
#
# setup.py for flashbake

from distutils.core import setup

setup(name='flashbake',
        version='0.21',
        author="Thomas Gideon",
        author_email="cmdln@thecommandline.net",
        url="http://thecommandline.net",
        license="GPLv3",
        py_modules=['flashbake.commit',
            'flashbake.context',
            'flashbake.plugins.feed',
            'flashbake.plugins.timezone',
            'flashbake.plugins.uptime',
            'flashbake.plugins.weather'
            ],
        requires=['enum (>=0.4.3)'],
        scripts=['bin/flashbake'])
