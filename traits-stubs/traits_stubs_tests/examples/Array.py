# (C) Copyright 2005-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import numpy as np

from traits.api import Array, ArrayOrNone, HasTraits


class HasArrayTraits(HasTraits):
    spectrum = Array(shape=(None,), dtype=np.float64)
    maybe_image = ArrayOrNone(shape=(None, None, 3), dtype=np.float64)


obj = HasArrayTraits()
obj.spectrum = np.array([2, 3, 4], dtype=np.float64)
obj.spectrum = "not an array"  # E: assignment
obj.spectrum = None  # E: assignment

obj.maybe_image = None
obj.maybe_image = np.zeros((5, 5, 3))
obj.maybe_image = 2.3  # E: assignment
