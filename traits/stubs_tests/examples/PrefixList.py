# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, PrefixList


class Person(HasTraits):
    atr1 = PrefixList(('yes', 'no'))
    atr2 = PrefixList(['yes', 'no'])


p = Person()
p.atr1 = 5  # E: assignment
