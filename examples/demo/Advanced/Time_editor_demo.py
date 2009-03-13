#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
A Traits UI editor that wraps a WX timer control.
"""
import datetime

from enthought.traits.api import HasTraits, Time
from enthought.traits.ui.api import View, Item, TimeEditor


class TimeEditorDemo(HasTraits):
    """ Demo class. """
    time = Time(datetime.time(12, 0, 0))
    view = View(Item('time', label='Simple Editor'), 
                Item('time', label='Readonly Editor',
                     style='readonly',
                     # Show 24-hour mode instead of default 12 hour.
                     editor=TimeEditor(strftime='%H:%M:%S')
                     ),
                resizable=True)

    def _time_changed(self):
        """ Print each time the time value is changed in the editor. """
        print self.time


#-- Set Up The Demo ------------------------------------------------------------
    
demo = TimeEditorDemo()

if __name__ == "__main__":
    demo.configure_traits()        

#-- eof ----------------------------------------------------------------------- 
