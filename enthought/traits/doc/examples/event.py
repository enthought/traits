# event.py --- Example of trait event
import wx
from enthought.traits.api import Event, HasTraits, List, Tuple, RGBAColor

point_2d = Tuple(0, 0)

class Line2D(HasTraits):
    points = List(point_2d)
    line_color = RGBAColor('black')
    updated = Event

    def redraw():
        pass # Not implemented for this example

    def _points_changed():
        self.updated = True

    def _updated_fired():
        self.redraw()
