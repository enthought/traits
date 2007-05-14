# false.py --- example of 'false' trait
from enthought.traits.api import false, true, HasTraits

class GUIControl(HasTraits): # Base class for GUI objects
    readonly = false 
    enabled  = true
