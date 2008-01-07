from setuptools import setup, find_packages


# NOTE: EnthoughtBase should *never* depend on another ETS project!


setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = 'EnthoughtBase is the root project of all other ETS projects',
    extras_require = {
        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            ],
        },
    license = 'BSD',
    include_package_data = True,
    install_requires = [],
    name = 'EnthoughtBase',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(),
    tests_require = [
        'nose >= 0.9',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/ets',
    version = '3.0.0b1',
    zip_safe = False,
    )

