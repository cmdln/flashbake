#!/usr/bin/env python
#
# setup.py for flashbake

from distutils.core import setup

setup(name='flashbake',
        version='0.20',
        author="Thomas Gideon",
        author_email="cmdln@thecommandline.net",
        url="http://thecommandline.net",
        license="http://creativecommons.org/licenses/by-nc-sa/3.0/us/",
        py_modules=['flashbake.commit',
            'flashbake.context',
            'flashbake.plugins.feed',
            'flashbake.plugins.timezone',
            'flashbake.plugins.uptime',
            'flashbake.plugins.weather'
            ],
        requires=['enum (>=0.4.3)'],
        scripts=['bin/flashbake'])
