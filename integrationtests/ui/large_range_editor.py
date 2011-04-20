#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

from traits.api import HasTraits, Float, List
from traitsui.api import View, Item, RangeEditor

# Tests the Large Range Slider editor. It also tests the case where the
# editor is embedded in a list.
class TestRangeEditor(HasTraits):
    x = Float
    low = Float(123.123)
    high = Float(1123.123)
    list = List(Float(
                     editor = RangeEditor(low_name='low',
                                          high_name = 'high',
                                          # These force the large range
                                          # slider to be used.
                                          low=100.0,
                                          high=10000.123)
                     )
               )
    view = View(Item(name='x',
                     editor = RangeEditor(low_name='low',
                                          high_name = 'high',
                                          # These force the large range
                                          # slider to be used.
                                          low=100.0,
                                          high=10000.123)
                     ),
                 Item('list'),
                 resizable=True
                )

def test():
    a = TestRangeEditor()
    a.x = 500
    a.list.append(500)
    a.edit_traits() # Just close the resulting dialog.
    assert a.x == 500
    assert a.list[0] == 500

test()
