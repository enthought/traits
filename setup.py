from setuptools import setup, Extension, find_packages

ctraits = Extension(
    'enthought.traits.ctraits',
    sources=['enthought/traits/ctraits.c'],
)

setup(
    name = 'enthought.traits',
    version = '1.1.0',
    description  = 'Explicitly typed Python attributes package',
    author       = 'David C. Morrill',
    author_email = 'dmorrill@enthought.com',
    url          = 'http://code.enthought.com/traits',
    license      = 'BSD',
    zip_safe     = False,
    packages = find_packages(),
    ext_modules = [ctraits],
    include_package_data = True,
    install_requires = [
        'numpy',
        'enthought.ets', 
        'enthought.resource',
        'enthought.pyface>=1.1.1',
    ],
    extras_require = {
        'wx' : ['enthought.traits.ui.wx'],
    },
    namespace_packages = [
        "enthought",
        "enthought.traits",
        "enthought.traits.ui",
    ],
)
