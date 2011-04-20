#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

""" Demonstrates how to use the Dynamic Views facility.
"""

from traits.api \
    import Bool, HasTraits, Str, Instance, Button

from traitsui.api \
    import View, HGroup, Group, Item, Handler, Label, spring

from traits.has_dynamic_views \
    import DynamicView, HasDynamicViews

class HasFooView ( HasDynamicViews ):
    """ A base class declaring the existence of the 'foo' dynamic view.
    """

    def __init__ ( self, *args, **traits ):
        """ Constructor.

            Extended to declare our dynamic foo view.
        """
        super( HasFooView, self ).__init__( *args, **traits )

        # Declare and add our dynamic view:
        declaration = DynamicView(
            name     = 'foo',
            id       = 'traitsui.demos.dynamic_views',
            keywords = {
                'buttons':    [ 'OK' ],
                'dock':       'tab',
                'height':     0.4,
                'width':      0.4,
                'resizable':  True,
                'scrollable': True,
            },
            use_as_default = True,
        )
        self.declare_dynamic_view( declaration )

class MyInfoHandler ( Handler ):

    def object_first_changed ( self, info ):
        info.object.derived = info.object.first

class BaseFoo ( HasFooView ):
    """ A base class that puts some content in the 'foo' dynamic view.
    """

    first = Str( 'My first name' )
    last  = Str( 'My last name' )

    # A derived trait set by the handler associated with out dynamic view
    # contribution:
    derived = Str

    ui_person = Group(
        Item(label='On this tab, notice how the sub-handler keeps\n'
            'the derived value equal to the first name.\n\n'
            'On the next tab, change the selection in order to\n'
            'control which tabs are visible when the ui is \n'
            'displayed for the 2nd time.'
            ),
        spring,
        'first', 'last',
        spring,
        'derived',
        label = 'My Info',
        _foo_order    = 5,
        _foo_priority = 1,
        _foo_handler  = MyInfoHandler(),
    )

class FatherInfoHandler ( Handler ):

    def object_father_first_name_changed ( self, info ):
        info.object.father_derived = info.object.father_first_name

class DerivedFoo ( BaseFoo ):
    """ A derived class that puts additional content in the 'foo' dynamic view.
        Note that the additional content could also have been added via a traits
        category contribution, or even dynamic manipulation of metadata on a UI
        subelement.  The key is what the metadata represents when the view is
        *created*
    """

    knows_mother      = Bool( False )
    mother_first_name = Str( "My mother's first name" )
    mother_last_name  = Str( "My mother's last name" )

    knows_father      = Bool( True )
    father_first_name = Str( "My father's first name" )
    father_last_name  = Str( "My father's last name" )
    father_derived    = Str

    ui_parents = Group(
        'knows_mother',
        'knows_father',
        label         = 'Parents?',
        _foo_order    = 7,
        _foo_priority = 1,
    )

    ui_mother = Group(
        'mother_first_name',
        'mother_last_name',
        label         = "Mother's Info",
        _foo_priority = 1,
    )

    ui_father = Group(
        'father_first_name',
        'father_last_name',
        spring,
        'father_derived',
        label         = "Father's Info",
        _foo_order    = 15,
        _foo_priority = 1,
        _foo_handler  = FatherInfoHandler(),
    )

    def _knows_mother_changed ( self, old, new ):
        ui_mother = self.trait_view( 'ui_mother' )
        if new:
            ui_mother._foo_order = 10
        elif hasattr( ui_mother, '_foo_order' ):
            del ui_mother._foo_order

    def _knows_father_changed ( self, old, new ):
        ui_father = self.trait_view( 'ui_father' )
        if new:
            ui_father._foo_order = 15
        elif hasattr( ui_father, '_foo_order' ):
            del ui_father._foo_order


class FooDemo ( HasTraits ):
    """ Defines a class to run the demo.
    """

    foo       = Instance( DerivedFoo, () )
    configure = Button( 'Configure' )

    view = View(
        Label( "Try configuring several times, each time changing the items "
               "on the 'Parents?' tab." ),
        '_',
        HGroup( spring, Item( 'configure', show_label = False ) )
    )

    def _configure_changed ( self ):
        self.foo.configure_traits()

# Create the demo:
popup = FooDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()

