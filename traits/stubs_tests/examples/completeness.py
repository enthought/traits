# (C) Copyright 2020-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
A selection of code snippets used to test completeness of the stubs.
"""

from traits.api import HasStrictTraits, Str, TraitError


class HasName(HasStrictTraits):
    name = Str()


def try_assigning_name(x: HasName, new_name: str):
    try:
        x.name = new_name
    except TraitError:
        raise ValueError(f"Bad name: {new_name}")
