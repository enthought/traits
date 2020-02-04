# (C) Copyright 2005-2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# cached_prop.py - Example of @cached_property decorator
# --[Imports]-------------------------------------------------------------------
from traits.api import HasPrivateTraits, List, Int, Property, cached_property


# --[Code]----------------------------------------------------------------------
class TestScores(HasPrivateTraits):

    scores = List(Int)
    average = Property(depends_on="scores")

    @cached_property
    def _get_average(self):
        s = self.scores
        return sum(s) / len(s)
