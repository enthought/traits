#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# enum_editor.py -- Example of using an enumeration editor

#--[Imports]--------------------------------------------------------------------
from traits.api import HasTraits, Enum
from traitsui.api import EnumEditor, View, Item

#--[Code]-----------------------------------------------------------------------

class EnumExample(HasTraits):
    priority = Enum('Medium', 'Highest',
                              'High',
                              'Medium',
                              'Low',
                              'Lowest')

    view = View( Item(name='priority',
                      editor=EnumEditor(values={
                          'Highest' : '1:Highest',
                          'High'    : '2:High',
                          'Medium'  : '3:Medium',
                          'Low'     : '4:Low',
                          'Lowest'  : '5:Lowest', })))

