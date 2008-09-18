#!/usr/bin/env python
#
# Copyright (c) 2008 by Enthought, Inc.
# All rights reserved.
#

"""
Core packages for the Enthought Tool Suite.

The EnthoughtBase project includes a few core packages that are used by many
other projects in the Enthought Tool Suite:

- **enthought.etsconfig**: Supports configuring settings that need to be shared
  across multiple projects or programs on the same system. Most significant of
  these is the GUI toolkit to be used. You can also configure locations for
  writing application data and user data, and the name of the company
  responsible for the software (which is used in the application and user data
  paths on some systems).
- **enthought.logger**: Provides convenience functions for creating logging
  handlers.
- **enthought.util**: Provides miscellaneous utility functions.

Prerequisites
-------------
If you want to build EnthoughtBase from source, you must first install 
`setuptools <http://pypi.python.org/pypi/setuptools/0.6c8>`_.

"""


from distutils import log
from distutils.command.build import build as distbuild
from setuptools import setup, find_packages
from setuptools.command.develop import develop
import os
import zipfile

# FIXME: This works around a setuptools bug which gets setup_data.py metadata
# from incorrect packages. Ticket #1592
#from setup_data import INFO
setup_data = dict(__name__='', __file__='setup_data.py')
execfile('setup_data.py', setup_data)
INFO = setup_data['INFO']

# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


class MyDevelop(develop):
    def run(self):
        develop.run(self)
        self.run_command('build_docs')

class MyBuild(distbuild):
    def run(self):
        distbuild.run(self)
        self.run_command('build_docs')


# The actual setup call.
setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    classifiers = [c.strip() for c in """\
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.strip()) > 0],
    cmdclass = {
        'develop': MyDevelop,
        'build': MyBuild
    },
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = DOCLINES[1],
    extras_require = INFO['extras_require'],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    include_package_data = True,
    install_requires = INFO['install_requires'],
    name = 'EnthoughtBase',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    setup_requires = 'setupdocs',
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/enthought_base.php',
    version = INFO['version'],
    zip_safe = False,
    )

