#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# trait_reuse.py --- Example of reusing trait definitions

from traits.api import HasTraits, Range

#--[Code]----------------------------------------------------------------------
coefficient = Range(-1.0, 1.0, 0.0)


class quadratic(HasTraits):
    c2 = coefficient
    c1 = coefficient
    c0 = coefficient
    x = Range(-100.0, 100.0, 0.0)
