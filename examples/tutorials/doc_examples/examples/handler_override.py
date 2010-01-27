#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# handler_override.py -- Example of a Handler that overrides setattr(), and
#                        that has a user interface notification method

#--[Imports]--------------------------------------------------------------------

from enthought.traits.api import HasTraits, Bool
from enthought.traits.ui.api import View, Handler

#--[Code]-----------------------------------------------------------------------

class TC_Handler(Handler):

    def setattr(self, info, object, name, value):
        Handler.setattr(self, info, object, name, value)
        info.object._updated = True

    def object__updated_changed(self, info):
        if info.initialized:
            info.ui.title += "*"

class TestClass(HasTraits):
    b1 = Bool
    b2 = Bool
    b3 = Bool
    _updated = Bool(False)

view1 = View('b1', 'b2', 'b3', 
             title="Alter Title", 
             handler=TC_Handler(),
             buttons = ['OK', 'Cancel'])

tc = TestClass()
tc.configure_traits(view=view1)

