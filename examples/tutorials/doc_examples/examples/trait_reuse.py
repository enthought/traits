# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# trait_reuse.py --- Example of reusing trait definitions

from traits.api import HasTraits, Range

# --[Code]---------------------------------------------------------------------
coefficient = Range(-1.0, 1.0, 0.0)


class quadratic(HasTraits):
    c2 = coefficient
    c1 = coefficient
    c0 = coefficient
    x = Range(-100.0, 100.0, 0.0)
