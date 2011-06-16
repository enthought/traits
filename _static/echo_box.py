from traits.api import *

class EchoBox(HasTraits):
    input =  Str()
    output = Str()

    def _input_changed(self):
        self.output = self.input

EchoBox().configure_traits()

