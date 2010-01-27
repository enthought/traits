#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# override_editor.py --- Example of overriding a trait 
#                        editor
from enthought.traits.api import HasTraits, Trait
import enthought.traits.ui
from enthought.traits.ui.api import ColorEditor
from wxPython import wx

class Polygon(HasTraits):
    line_color = Trait(wx.wxColour(0, 0, 0),
                       editor=ColorEditor())
