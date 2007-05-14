# instanceeditor.py --- Example of using an InstanceEditor
from enthought.traits.api import HasTraits, Int, Range, Trait
from enthought.traits.ui.api import Group, Item, InstanceEditor, View

class InstanceExample(HasTraits):
    integer_text = Int(1)
    enumeration  = Trait('one', 'two', 'three','four',
                         'five', 'six', cols=3)
    float_range  = Range(0.0, 10.0, 10.0)
    int_range    = Range(1, 5)
    boolean      = True
    
    view         = View('integer_text', 'enumeration',
                        'float_range', 'int_range',
                        'boolean' )

class InstanceTest(HasTraits):
    instance = Trait(InstanceExample())
    view = View( Group(Item('instance', label='Simple'),  '_',
                       Item('instance', label='Custom', 
                           style='custom'), '_',
                       Item('instance', label='Text', 
                           style='text'),   '_',
                       Item('instance', label='Readonly', 
                           style='readonly'),
                       label='Instance', 
                       )
                 )
