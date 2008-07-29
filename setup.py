#!/usr/bin/env python
#
# Copyright (c) 2008 by Enthought, Inc.
# All rights reserved.
#

"""
PyQt backend for Traits and Pyface.

<description text needed>
"""


from setuptools import setup, find_packages


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


# Function to convert simple ETS project names and versions to a requirements
# spec that works for both development builds and stable builds.  Allows
# a caller to specify a max version, which is intended to work along with
# Enthought's standard versioning scheme -- see the following write up:
#    https://svn.enthought.com/enthought/wiki/EnthoughtVersionNumbers
def etsdep(p, min, max=None, literal=False):
    require = '%s >=%s.dev' % (p, min)
    if max is not None:
        if literal is False:
            require = '%s, <%s.a' % (require, max)
        else:
            require = '%s, <%s' % (require, max)
    return require


# Declare our ETS project dependencies:
ENTHOUGHTBASE = etsdep('EnthoughtBase', '3.0.0b1')
DEVTOOLS_DEVELOPER = etsdep('DevTools[developer]', '3.0.0b1')
TRAITS = etsdep('Traits', '3.0.0b1')
TRAITSGUI = etsdep('TraitsGUI', '3.0.0b1')


setup(
    author = 'Phil Thompson',
    author_email = 'phil@riverbankcomputing.co.uk',
    classifiers = """\
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: GNU General Public License (GPL)
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines(),
    dependency_links = [
         'http://code.enthought.com/enstaller/eggs/source',
         ],
    description = DOCLINES[0],
    extras_require = {

        # Extra denoting that complete developer debug support for the ETS FBI
        # debugger should be installed:
        'debug': [
            DEVTOOLS_DEVELOPER,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            ],
        },
    include_package_data = True,
    install_requires = [
        ENTHOUGHTBASE,
        TRAITS,
        TRAITSGUI,
        ],
    license = 'GPL',
    long_description = '\n'.join(DOCLINES[2:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = 'TraitsBackendQt',
    namespace_packages   = [
        "enthought",
        "enthought.pyface",
        "enthought.pyface.ui",
        "enthought.traits",
        "enthought.traits.ui",
        ],
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    tests_require = [
        'nose >= 0.10.3',
        ],
    # test_suite = 'nose.collector',
    url = 'http://code.enthought.com/ets',
    version = '3.0.0b1',
    zip_safe = False,
    )

