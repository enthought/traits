"""
A Traits UI editor that wraps a WX timer control.
"""
import datetime

from enthought.traits.api import HasTraits, Time
from enthought.traits.ui.api import View, Item


class TimeEditorDemo(HasTraits):
    """ Demo class. """
    time = Time(datetime.time(12, 0, 0))
    view = View(Item('time', show_label=False), resizable=True)

    def _time_changed(self):
        """ Print each time the time value is changed in the editor. """
        print self.time


#-- Set Up The Demo ------------------------------------------------------------
    
demo = TimeEditorDemo()

if __name__ == "__main__":
    demo.configure_traits()        

#-- eof ----------------------------------------------------------------------- 
