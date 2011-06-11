#!/usr/bin/env python
#
# Copyright (c) 2008-2011 by Enthought, Inc.
# All rights reserved.

"""
Explicitly typed attributes for Python.

The Traits project is at the center of all Enthought Tool Suite development
and has changed the mental model used at Enthought for programming in the
already extremely efficient Python programming language. We encourage everyone
to join us in enjoying the productivity gains from using such a powerful
approach.

The Traits project allows Python programmers to use a special kind of type
definition called a *trait*, which gives object attributes some additional
characteristics:

- **Initialization**: A trait has a *default value*, which is
  automatically set as the initial value of an attribute before its
  first use in a program.
- **Validation**: A trait attribute's type is *explicitly declared*. The
  type is evident in the code, and only values that meet a
  programmer-specified set of criteria (i.e., the trait definition) can
  be assigned to that attribute.
- **Delegation**: The value of a trait attribute can be contained either
  in the defining object or in another object *delegated* to by the
  trait.
- **Notification**: Setting the value of a trait attribute can *notify*
  other parts of the program that the value has changed.
- **Visualization**: User interfaces that allow a user to *interactively
  modify* the value of a trait attribute can be automatically
  constructed using the trait's definition. (This feature requires that
  a supported GUI toolkit be installed. If this feature is not used, the
  Traits project does not otherwise require GUI support.)

A class can freely mix trait-based attributes with normal Python attributes,
or can opt to allow the use of only a fixed or open set of trait attributes
within the class. Trait attributes defined by a classs are automatically
inherited by any subclass derived from the class.

Prerequisites
-------------
You must have the following libraries installed before building or installing
Traits:

* `Numpy <http://pypi.python.org/pypi/numpy>`_ to support the trait types
  for arrays.
"""

from os.path import join
from setuptools import setup, Extension, find_packages


d = {}
execfile(join('traits', '__init__.py'), d)
version = d['__version__']


ctraits = Extension(
    'traits.ctraits',
    sources = ['traits/ctraits.c'],
    extra_compile_args = ['-DNDEBUG=1', '-O3'],
    )


speedups = Extension(
    'traits.protocols._speedups',
    # fixme: Use the generated sources until Pyrex 0.9.6 and setuptools can
    # play with each other. See #1364
    sources = ['traits/protocols/_speedups.c'],
    extra_compile_args = ['-DNDEBUG=1', '-O3'],
    )


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")

setup(
    author = 'David C. Morrill, et. al.',
    author_email = 'dmorrill@enthought.com',
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
        Programming Language :: C
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.strip()) > 0],
    description = DOCLINES[1],
    download_url = ('http://www.enthought.com/repo/ets/traits-%s.tar.gz' %
                    version),
    ext_modules = [ctraits, speedups],
    include_package_data = True,
    package_data = {'traits': ['protocols/_speedups.pyx']},
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = 'traits',
    packages = find_packages(exclude = [
        'docs',
        'docs.*',
        'integrationtests',
        'integrationtests.*',
        ]),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/traits',
    version = version,
    zip_safe = False,
)
