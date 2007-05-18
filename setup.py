from setuptools \
    import setup, Extension, find_packages

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
    version      = '2.1.0',
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
        'app_data': [ 'enthought.ets' ], 
        'array':    [ 'numpy >= 1.0.0' ],
        'ui':       [ 'enthought.pyface' ],
        'wx':       [ 'enthought.traits.ui.wx' ],
    },
    
    namespace_packages = [
        'enthought',
        'enthought.traits',
        'enthought.traits.ui',
    ],
)
