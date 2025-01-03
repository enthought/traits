# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, Map


class Person(HasTraits):
    married = Map({'yes': 1, 'no': 0}, default_value="yes")
    married_2 = Map([], default_value="yes")  # E: arg-type


p = Person()

p.married = "yes"
