#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   06/21/2002
#
#------------------------------------------------------------------------------

""" Defines a 'traits' package that allows other classes to easily define
    'type-checked' and/or 'delegated' traits for their instances.
    Part of the Traits project of the Enthought Tool Suite.

    Note: A 'trait' is similar to a 'property', but is used instead of the
    word 'property' to differentiate it from the Python language 'property'
    feature.
"""

from __future__ import absolute_import

try:
    # if the code is ran from an egg, the namespace must be declared
    __import__('pkg_resources').declare_namespace(__name__)
except:
    pass

# For py2app / py2exe support
try:
    import modulefinder
    for p in __path__:
        modulefinder.AddPackagePath(__name__, p)
except:
    pass
