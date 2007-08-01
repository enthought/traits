from setuptools import setup, find_packages

setup(
    name = 'enthought.traits.ui.qt4',
    version = '3.0.0b1',
    description  = 'PyQt backend for enthought.traits',
    author       = 'Phil Thompson',
    author_email = 'phil@riverbankcomputing.co.uk',
    url          = 'http://code.enthought.com/traits',
    license      = 'GPL',
    zip_safe     = False,
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        "enthought.model >=2.0.0b1, <3.0.0",
        "enthought.traits >=3.0.0b1, <4.0.0",
    ],
    namespace_packages = [
        "enthought",
        "enthought.traits",
        "enthought.traits.ui",
    ],
)
