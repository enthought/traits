#!/usr/bin/env python
#
# Copyright (c) 2008-2010 by Enthought, Inc.
# All rights reserved.

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
from setuptools import setup, find_packages


# FIXME: This works around a setuptools bug which gets setup_data.py metadata
# from incorrect packages. Ticket #1592
#from setup_data import INFO
setup_data = dict(__name__='', __file__='setup_data.py')
execfile('setup_data.py', setup_data)
INFO = setup_data['INFO']


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")

# The actual setup call.
setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    download_url = (
        'http://www.enthought.com/repo/ETS/EnthoughtBase-%s.tar.gz' %
        INFO['version']),
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
    description = DOCLINES[1],
    include_package_data = True,
    package_data = {'enthought': ['logger/plugin/*.ini',
                                  'logger/plugin/view/images/*.png']},
    install_requires = INFO['install_requires'],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = 'EnthoughtBase',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/enthought_base.php',
    version = INFO['version'],
    zip_safe = False,
)
