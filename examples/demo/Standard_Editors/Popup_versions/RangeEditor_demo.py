"""
Implementation of a RangeEditor demo plugin for the Traits UI demo program.

This demo shows each of the four styles of the RangeEditor Variations for a
small integer range, a medium-sized integer range, a large integer range
and a float range are demonstrated on separate tabs.
"""

from traits.api import HasTraits, Range
from traitsui.api import Item, Group, View

#-------------------------------------------------------------------------------
#  Demo Class
#-------------------------------------------------------------------------------

class RangeEditorDemo ( HasTraits ):
    """ This class specifies the details of the RangeEditor demo.
    """

    # Define a trait for each of four variants
    small_int_range  = Range( 1, 16 )
    medium_int_range = Range( 1, 25 )
    large_int_range  = Range( 1, 150 )
    float_range      = Range( 0.0, 150.0 )


    # RangeEditor display for narrow integer Range traits (< 17 wide):
    int_range_group1 = Group( Item('small_int_range',
                                    style='simple',
                                    label='Simple'),
                              Item('_'),
                              Item('small_int_range',
                                    style='custom',
                                    label='Custom'),
                              Item('_'),
                              Item('small_int_range',
                                    style='text',
                                    label='Text'),
                              Item('_'),
                              Item('small_int_range',
                                    style='readonly',
                                    label='ReadOnly'),
                              label = "Small Int")

    # RangeEditor display for medium-width integer Range traits (17 to 100):
    int_range_group2 = Group( Item('medium_int_range',
                                    style='simple',
                                    label='Simple'),
                              Item('_'),
                              Item('medium_int_range',
                                    style='custom',
                                    label='Custom'),
                              Item('_'),
                              Item('medium_int_range',
                                    style='text',
                                    label='Text'),
                              Item('_'),
                              Item('medium_int_range',
                                    style='readonly',
                                    label='ReadOnly'),
                              label = "Medium Int")

    # RangeEditor display for wide integer Range traits (> 100):
    int_range_group3 = Group( Item('large_int_range',
                                    style='simple',
                                    label='Simple'),
                              Item('_'),
                              Item('large_int_range',
                                    style='custom',
                                    label='Custom'),
                              Item('_'),
                              Item('large_int_range',
                                    style='text',
                                    label='Text'),
                              Item('_'),
                              Item('large_int_range',
                                    style='readonly',
                                    label='ReadOnly'),
                              label = "Large Int")

    # RangeEditor display for float Range traits:
    float_range_group = Group( Item('float_range',
                                     style='simple',
                                     label='Simple'),
                               Item('_'),
                               Item('float_range',
                                     style='custom',
                                     label='Custom'),
                               Item('_'),
                               Item('float_range',
                                     style='text',
                                     label='Text'),
                               Item('_'),
                               Item('float_range',
                                     style='readonly',
                                     label='ReadOnly'),
                               label = "Float")

    # The view includes one group per data type.  These will be displayed
    # on separate tabbed panels.
    view1 = View(int_range_group1,
                 int_range_group2,
                 int_range_group3,
                 float_range_group,
                 title = 'RangeEditor',
                 buttons = ['OK'])


# Create the demo:
popup =  RangeEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

