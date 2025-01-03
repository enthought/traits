# (C) Copyright 2005-2025 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from math import pow
from traits.api import HasTraits, Callable


class Test(HasTraits):
    var = Callable()


obj = Test()
obj.var = pow
obj.var = None

obj.var = "someuuid"  # E: assignment

obj.var = 5  # E: assignment

obj.var = False  # E: assignment
obj.var = 5.5  # E: assignment

obj.var = 5 + 4j  # E: assignment
obj.var = True  # E: assignment

obj.var = (True,)  # E: assignment
