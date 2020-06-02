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

if __name__ == "__main__":
    setuptools.setup(
        name="traits-stubs",
        version="0.1.0",
        description="type annotation integration stubs for traits",
        install_requires=["mypy", "traits"],
        packages=["traits-stubs",
                  "traits_stubs_tests",
                  "traits_stubs_tests.examples"],
        package_data={
            'traits-stubs': ['./*.pyi', './**/*.pyi'],
        },
    )
