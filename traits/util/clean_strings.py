# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Provides functions that mange strings to avoid characters that would be
    problematic in certain situations.
"""

# Standard library imports.
import keyword


def python_name(name):
    """ Attempt to make a valid Python identifier out of a name.
    """

    if len(name) > 0:
        # Replace spaces with underscores.
        name = name.replace(" ", "_").lower()

        # If the name is a Python keyword then prefix it with an
        # underscore.
        if keyword.iskeyword(name):
            name = "_" + name

        # If the name starts with a digit then prefix it with an
        # underscore.
        if name[0].isdigit():
            name = "_" + name

    return name
