from setuptools import setup, Extension, find_packages

from enthought.traits.version import __version__


ctraits = Extension(
    'enthought.traits.ctraits',
    sources = [ 'enthought/traits/ctraits.c' ],
    )

speedups = Extension(
    'enthought.traits.protocols._speedups',
    sources = [ 'enthought/traits/protocols/_speedups.c' ],
    )


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


# Declare our ETS project dependencies.
ETSCONFIG = etsdep('enthought.etsconfig', '2.0.0b1')
PYFACE = etsdep('enthought.pyface', '2.0.0b1')
TRAITSUIWX = etsdep('enthought.traits.ui.wx', '3.0.0b1')
TRAITSUIQT4 = etsdep('enthought.traits.ui.qt4', '3.0.0b1')


setup(
    author = 'David C. Morrill',
    author_email = 'dmorrill@enthought.com',
    description = 'Explicitly typed Python attributes package',
    extras_require = {
        'etsconfig': [
            ETSCONFIG,
            ],
        'array': [
            ],
        'ui': [
            PYFACE,
            ],
        'wx': [
            TRAITSUIWX,
            ],
        'qt4': [
            TRAITSUIQT4,
            ],

        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            'numpy >= 1.0.0',
            ],
        },
    ext_modules = [ ctraits, speedups ],
    include_package_data = True,
    install_requires = [
        ],
    license = 'BSD',
    name = 'enthought.traits',
    namespace_packages = [
        'enthought',
        'enthought.traits',
        'enthought.traits.ui',
        ],
    packages = find_packages(),
    tests_require = [
        'nose >= 0.9',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/traits',
    version = __version__,
    zip_safe = False,
    )

