#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

# cached_prop.py - Example of @cached_property decorator
#--[Imports]-------------------------------------------------------------------
from traits.api import HasPrivateTraits, List, Int, Property, cached_property


#--[Code]----------------------------------------------------------------------
class TestScores(HasPrivateTraits):

    scores = List(Int)
    average = Property(depends_on='scores')

    @cached_property
    def _get_average(self):
        s = self.scores
        return float(reduce(lambda n1, n2: n1 + n2, s, 0)) / len(s)
