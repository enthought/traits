# (C) Copyright 2005-2026 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" This module provides functions to be advertised in the distribution
entry points.
"""

import importlib.resources


def introduction(request):
    """ Return a configuration for contributing examples to the
    Demo application.

    Parameters
    ----------
    request : dict
        Information provided by the demo application.
        Currently this is a placeholder.

    Returns
    -------
    response : dict
    """
    return dict(
        version=1,
        name="Traits Introduction",
        root=str(
            importlib.resources.files("traits.examples") / "introduction"
        ),
    )
