"""
A Traits UI editor that wraps a WX calendar panel.
"""

from enthought.traits.api import HasTraits, Date
from enthought.traits.ui.api import View, Item


class DateEditorDemo(HasTraits):
    """ Demo class. """
    date = Date
    view = View(Item('date', show_label=False), resizable=True)

    def _date_changed(self):
        """ Print each time the date value is changed in the editor. """
        print self.date


#-- Set Up The Demo ------------------------------------------------------------

demo = DateEditorDemo()

if __name__ == "__main__":
    demo.configure_traits()        
    

#-- eof ----------------------------------------------------------------------- 
