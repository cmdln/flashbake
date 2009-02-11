from distutils.core import setup

setup(name='flashbake',
        version='0.14',
        author="Thomas Gideon",
        author_email="cmdln@thecommandline.net",
        url="http://thecommandline.net",
        license="http://creativecommons.org/licenses/by-nc-sa/3.0/us/",
        py_modules=['flashbake.commit', 'flashbake.context'],
        scripts=['bin/flashbake'])
