#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# view_standalone.py --- Example of a view as a 
#                        standalone object
import wx
from enthought.traits.api import HasTraits, Int, Str, Trait
from enthought.traits.ui.api import View
import enthought.traits.ui

class Person(HasTraits):
    first_name = Str
    last_name = Str
    age = Int
    gender = Trait(None, 'M', 'F')
    name_view = View('first_name', 'last_name')

# Note that person_view is a standalone object.
person_view = View('first_name', 'last_name', 'age', 'gender')
                   
bill = Person()

class TraitApp ( wx.App ):

    def __init__ ( self, object, view ):
        self.object = object
        self.view = view
        wx.InitAllImageHandlers()
        wx.App.__init__( self, 1, 'debug.log' )
        self.MainLoop()
    
    def OnInit ( self ):
        # This is the call to the ui() method.
        ui = self.view.ui(self.object)
        self.SetTopWindow( ui.control )
        return True
    

#  Main program:
TraitApp( bill, person_view )

