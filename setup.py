# Copyright (c) 2008-2013 by Enthought, Inc.
# All rights reserved.
import glob
import os
import shutil

from os.path import join, relpath
from setuptools import setup, Extension, find_packages

from distutils.command.build_ext import build_ext as old_build_ext

if "DISTUTILS_WITH_COVERAGE" in os.environ:
    BUILD_WITH_COVERAGE = True
else:
    BUILD_WITH_COVERAGE = False

class BuildExtWithCoverage(old_build_ext):
    def run(self):
        old_build_ext.run(self)

        if BUILD_WITH_COVERAGE and self.inplace:
            for root, dirs, files in os.walk(self.build_temp):
                gcno_files = glob.glob(join(root, "*.gcno"))
                for gcno_file in gcno_files:
                    source = gcno_file
                    target = relpath(gcno_file, self.build_temp)
                    shutil.move(source, target)

d = {}
execfile(join('traits', '__init__.py'), d)


ctraits = Extension(
    'traits.ctraits',
    sources = ['traits/ctraits.c'],
    extra_compile_args = ['-DNDEBUG=1', '-O3'],
    )


setup(
    cmdclass = {"build_ext": BuildExtWithCoverage},
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
    ext_modules = [ctraits],
    include_package_data = True,
    license = 'BSD',
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe = False,
)
