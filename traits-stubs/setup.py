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
        author="Enthought",
        author_email="info@enthought.com",
        description="Type annotation integration stubs for the Traits library",
        long_description=get_long_description(),
        long_description_content_type="text/x-rst",
        install_requires=["traits"],
        extras_require={
            "test": ["mypy"],
        },
        packages=["traits-stubs",
                  "traits_stubs_tests",
                  "traits_stubs_tests.examples"],
        package_data={
            'traits-stubs': ['./*.pyi', './**/*.pyi'],
        },
        license="BSD",
        python_requires=">=3.5",
    )
