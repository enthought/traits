#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of an InstanceEditor demo plugin for the Traits UI demo program.

This demo shows each of the four styles of the InstanceEditor

Fixme: This version of the demo only shows the old-style InstanceEditor
capabilities.
"""

# Imports:
from traits.api \
    import HasTraits, Str, Range, Bool, Instance

from traitsui.api \
    import Item, Group, View

#-------------------------------------------------------------------------------
#  Classes:
#-------------------------------------------------------------------------------

class SampleClass ( HasTraits ):
    """ This Sample class is used to demonstrate the InstanceEditor demo.
    """

    # The actual attributes don't matter here; we just need an assortment
    # to demonstrate the InstanceEditor's capabilities.:
    name             = Str
    occupation       = Str
    age              = Range( 21, 65 )
    registered_voter = Bool

    # The InstanceEditor uses whatever view is defined for the class.  The
    # default view lists the fields alphabetically, so it's best to define one
    # explicitly:
    view = View( 'name', 'occupation', 'age', 'registered_voter' )

class InstanceEditorDemo ( HasTraits ):
    """ This class specifies the details of the InstanceEditor demo.
    """

    # Create an Instance trait to view:
    sample_instance = Instance( SampleClass, () )


    # Items are used to define the demo display, one item per editor style:
    inst_group = Group(
        Item( 'sample_instance', style = 'simple',  label = 'Simple' ),
        Item( '_' ),
        Item( 'sample_instance', style = 'custom',  label = 'Custom' ),
        Item( '_' ),
        Item( 'sample_instance', style = 'text',    label = 'Text' ),
        Item( '_' ),
        Item( 'sample_instance', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo View:
    view = View(
        inst_group,
        title   = 'InstanceEditor',
        buttons = [ 'OK' ],
        resizable = True
    )

# Create the demo:
demo = InstanceEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

