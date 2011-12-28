#!/usr/bin/env python
#
# setup.py for flashbake
from setuptools import setup, find_packages



setup(name='flashbake',
        version='0.27',
        author="Thomas Gideon",
        author_email="cmdln@thecommandline.net",
        maintainer="Thomas Gideon",
        maintainer_email="cmdln@thecommandline.net",
        description="Automation to feed life log into version control message stream.",
        long_description=""" Flashbake was designed to help technically savvy
writers use version control by compiling information from the variety of
sources that make up the user's life log and automating the inclusion of
that information in a commit stream, as part of the messages in the
history.""",
        platforms=[ "noarch" ],
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Topic :: Artistic Software'
        ],
        url="http://thecommandline.net",
        download_url="https://github.com/commandline/flashbake/downloads",
        license="GPLv3",
        package_dir={'': 'src'},
        packages=find_packages(where='./src/', exclude=('./test/')),
        install_requires='''
            enum >=0.4.3
            feedparser >=4.1
            ''',
        entry_points={
                'console_scripts': [ 'flashbake = flashbake.console:main',
                                     'flashbakeall = flashbake.console:multiple_projects' ]
                },
        include_package_data = True,
        exclude_package_data = { '' : [ 'test/*' ] }
        )
