#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# view_multi_object.py --- Example of a view for
#                          editing multiple objects
import wx
from traits.api import HasTraits, Int, Str, Trait
from traitsui.api import View
import traitsui

class Person(HasTraits):
    first_name = Str
    last_name = Str

class Company(HasTraits):
    company_name = Str

# Standalone View object referencing objects in the UI context
employee_view = View('e.first_name', 'e.last_name',
                     'c.company_name')

bill = Person(first_name='Bill')
acme = Company(company_name='Acme Products')

class TraitApp ( wx.App ):

    def __init__ ( self, obj1, obj2, view ):
        self.obj1 = obj1
        self.obj2 = obj2
        self.view = view
        wx.InitAllImageHandlers()
        wx.App.__init__( self, 1, 'debug.log' )
        self.MainLoop()

    def OnInit ( self ):
        # This is the call to the ui() method, which includes a
        # context dictionary
        ui = self.view.ui({'e':self.obj1, 'c':self.obj2})
        self.SetTopWindow( ui.control )
        return True


#  Main program:
TraitApp( bill, acme, employee_view )

