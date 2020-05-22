# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Functions to help removing TraitsUI being a dependency of Traits.

Used internally by traits only.
"""
# All imports of TraitsUI should be delayed.


def check_traitsui_major_version(major):
    """ Raise RuntimeError if TraitsUI major version is less than the required
    value.

    Used internally in traits only.

    Parameters
    ----------
    major : int
        Required TraitsUI major version.

    Raises
    ------
    RuntimeError
    """
    from traitsui import __version__ as traitsui_version
    actual_major, _ = traitsui_version.split(".", 1)
    actual_major = int(actual_major)
    if actual_major < major:
        raise RuntimeError(
            "TraitsUI {} or higher is required. Got version {!r}".format(
                major, traitsui_version)
        )
