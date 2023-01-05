# (C) Copyright 2005-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, Property, Float, Int


class TestClass(HasTraits):
    i = Int()
    prop1 = Property(Float)
    prop2 = Property(i)
    prop3 = Property(3)  # E: arg-type
    prop4 = Property(depends_on='i')
