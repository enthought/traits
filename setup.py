# Copyright (c) 2008-2012 by Enthought, Inc.
# All rights reserved.

from os.path import join
from setuptools import setup, Extension, find_packages
from Cython.Distutils import build_ext


d = {}
execfile(join('traits', '__init__.py'), d)


ctraits = Extension(
    'traits.ctraits',
    sources = ['traits/ctraits.pyx'],
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
    name = 'traits',
    version = d['__version__'],
    url = 'http://code.enthought.com/projects/traits',
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
                    d['__version__']),
    ext_modules = [ctraits, speedups],
    include_package_data = True,
    package_data = {'traits': ['protocols/_speedups.pyx']},
    license = 'BSD',
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe = False,
    cmdclass = {'build_ext': build_ext},
)
