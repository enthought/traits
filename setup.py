# Copyright (c) 2008-2013 by Enthought, Inc.
# All rights reserved.

from os.path import join
from setuptools import setup, Extension, find_packages
from Cython.Distutils import build_ext

d = {}
traits_init = join('traits', '__init__.py')
exec(compile(open(traits_init).read(), traits_init, 'exec'), d)


ctraits = Extension(
    'traits.ctraits',
    sources = ['traits/ctraits.c'],
    extra_compile_args = ['-DNDEBUG=1', '-O3' ]#, '-DPy_LIMITED_API'],
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
    ext_modules = [ctraits],
    include_package_data = True,
    license = 'BSD',
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    zip_safe = False,
    cmdclass = {'build_ext': build_ext},
    use_2to3 = True,
    use_2to3_exclude_fixers = ['lib2to3.fixes.fix_next']   # traits_listener.ListenerItem has a trait *next* which gets wrongly renamed
)
