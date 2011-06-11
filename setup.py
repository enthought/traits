# Copyright (c) 2008-2011 by Enthought, Inc.
# All rights reserved.

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
    description = 'explicitly typed attributes for Python',
    long_description = open('README.rst').read(),
    download_url = ('http://www.enthought.com/repo/ets/traits-%s.tar.gz' %
                    version),
    ext_modules = [ctraits, speedups],
    include_package_data = True,
    package_data = {'traits': ['protocols/_speedups.pyx']},
    license = 'BSD',
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
