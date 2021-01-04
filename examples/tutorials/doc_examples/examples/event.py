# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# event.py --- Example of a trait event

# --<Imports>------------------------------------------------------------------
from traits.api import Event, HasTraits, List, Tuple
from traitsui.api import RGBColor

# --[Code]---------------------------------------------------------------------

point_2d = Tuple(0, 0)


class Line2D(HasTraits):
    points = List(point_2d)
    line_color = RGBColor("black")
    updated = Event

    def redraw(self):
        pass  # Not implemented for this example

    def _points_changed(self):
        self.updated = True

    def _updated_fired(self):
        self.redraw()
