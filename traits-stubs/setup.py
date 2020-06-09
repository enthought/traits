# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import setuptools


def get_long_description():
    """ Read long description from README.rst. """
    with open("README.rst", "r", encoding="utf-8") as readme:
        return readme.read()


if __name__ == "__main__":
    setuptools.setup(
        name="traits-stubs",
        version="6.1.0",
        url="https://github.com/enthought/traits",
        author="Enthought",
        author_email="info@enthought.com",
        classifiers=[
            c.strip()
            for c in """
            Development Status :: 4 - Beta
            Intended Audience :: Developers
            Intended Audience :: Science/Research
            License :: OSI Approved :: BSD License
            Operating System :: MacOS :: MacOS X
            Operating System :: Microsoft :: Windows
            Operating System :: POSIX :: Linux
            Programming Language :: Python
            Programming Language :: Python :: 3
            Programming Language :: Python :: 3.5
            Programming Language :: Python :: 3.6
            Programming Language :: Python :: 3.7
            Programming Language :: Python :: 3.8
            Programming Language :: Python :: Implementation :: CPython
            Topic :: Scientific/Engineering
            Topic :: Software Development
            Topic :: Software Development :: Libraries
            Topic :: Software Development :: User Interfaces
            Typing :: Typed
            """.splitlines()
            if len(c.strip()) > 0
        ],
        description="Type annotations for the Traits package",
        long_description=get_long_description(),
        long_description_content_type="text/x-rst",
        download_url="https://pypi.python.org/pypi/traits-stubs",
        install_requires=["traits"],
        extras_require={"test": ["mypy"]},
        packages=[
            "traits-stubs",
            "traits_stubs_tests",
            "traits_stubs_tests.examples",
        ],
        package_data={"traits-stubs": ["./*.pyi", "./**/*.pyi"]},
        license="BSD",
        python_requires=">=3.5",
    )
