# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import numpy as np

from traits.api import Array, ArrayOrNone, CArray, HasTraits


class HasArrayTraits(HasTraits):
    spectrum = Array(shape=(None,), dtype=np.float64)
    complex_shape = Array(shape=((512, None), (512, None), (3, 4)))
    list_shape = Array(shape=[(512, None), (512, None), (3, 4)])
    str_dtype = Array(dtype="f4")
    dtype_dtype = Array(dtype=np.dtype("float"))
    with_default_value = Array(value=np.zeros(5))
    with_list_default = Array(value=[1, 2, 3, 4, 5])
    with_tuple_default = Array(value=(1, 2, 3, 4, 5))
    with_casting = Array(casting="same_kind")

    maybe_image = ArrayOrNone(shape=(None, None, 3), dtype=np.float64)
    cspectrum = CArray(shape=(None,), dtype=np.float64)

    # Bad trait declarations
    bad_dtype = Array(dtype=62)  # E: arg-type
    bad_default = Array(value=123)  # E: arg-type
    bad_shape = Array(shape=3)  # E: arg-type
    bad_shape_element = Array(shape=(3, (None, None)))  # E: arg-type


obj = HasArrayTraits()
obj.spectrum = np.array([2, 3, 4], dtype=np.float64)
obj.spectrum = "not an array"  # E: assignment
obj.spectrum = None  # E: assignment

obj.maybe_image = None
obj.maybe_image = np.zeros((5, 5, 3))
obj.maybe_image = 2.3  # E: assignment
