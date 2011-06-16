from traits.api import *
import wx

class Counter(HasTraits):
    value =  Int()

Counter().edit_traits()
wx.PySimpleApp().MainLoop()

