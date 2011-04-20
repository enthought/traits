from traits import *
from pyface.api import GUI
from traitsui import View, Item, ButtonEditor

class Counter(HasTraits):
    value =  Int()
    add_one = Button()

    def _add_one_fired(self):
        self.value +=1

    view = View('value', Item('add_one', show_label=False ))

Counter().edit_traits()
GUI().start_event_loop()

