from setuptools \
    import setup, Extension, find_packages

from enthought.traits.version import __version__


ctraits = Extension(
    'enthought.traits.ctraits',
    sources = [ 'enthought/traits/ctraits.c' ],
)

speedups = Extension(
    'enthought.traits.protocols._speedups',
    sources = [ 'enthought/traits/protocols/_speedups.c' ],
)

setup(
    name         = 'enthought.traits',
    version      = __version__,
    description  = 'Explicitly typed Python attributes package',
    author       = 'David C. Morrill',
    author_email = 'dmorrill@enthought.com',
    url          = 'http://code.enthought.com/traits',
    license      = 'BSD',
    zip_safe     = False,
    packages     = find_packages(),
    ext_modules  = [ ctraits, speedups ],
    include_package_data = True,

    install_requires = [
    ],

    extras_require = {
        'etsconfig': [ 'enthought.etsconfig >=2.0.0b1, <3.0.0' ],
        'array':     [ 'numpy >= 1.0.0' ],
        'ui':        [ 'enthought.pyface >=2.0.0b1, <3.0.0' ],
        'wx':        [ 'enthought.traits.ui.wx >=3.0.0b1, <4.0.0' ],
        'qt4':       [ 'enthought.traits.ui.qt4 >=3.0.0b1, <4.0.0' ],
    },

    namespace_packages = [
        'enthought',
        'enthought.traits',
        'enthought.traits.ui',
    ],
)
