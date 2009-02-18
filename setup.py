#!/usr/bin/env python
#
# setup.py for flashbake

from distutils.core import setup

setup(name='flashbake',
        version='0.19',
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
        scripts=['bin/flashbake'])
