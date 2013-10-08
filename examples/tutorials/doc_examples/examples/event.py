#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# event.py --- Example of a trait event

#--<Imports>-------------------------------------------------------------------
from traits.api import Event, HasTraits, List, RGBColor, Tuple

#--[Code]----------------------------------------------------------------------

point_2d = Tuple(0, 0)


class Line2D(HasTraits):
    points = List(point_2d)
    line_color = RGBColor('black')
    updated = Event

    def redraw(self):
        pass  # Not implemented for this example

    def _points_changed(self):
        self.updated = True

    def _updated_fired(self):
        self.redraw()
