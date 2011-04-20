#--(NumPy Array Example)--------------------------------------------------------
"""
This lesson demonstrates how the **TabularEditor** can be used to display
(large) NumPy arrays. In this example, the array consists of 100,000 random 3D
points from a unit cube.

In addition to showing the coordinates of each point, the example code also
displays the index of each point in the array, as well as a red flag if the
point lies within 0.25 of the center of the cube.

As with the other tabular editor tutorials, this example shows how to set up a
**TabularEditor** and create an appropriate **TabularAdapter** subclass.

In this case, it also shows:

- An example of using array indices as *column_id* values.
- Using the *format* trait to format the numeric values for display.
- Creating a *synthetic* index column for displaying the point's array index
  (the *index_text* property), as well as a flag image for points close to the
  cube's center (the *index_image* property).
"""

#--<Imports>--------------------------------------------------------------------

from os.path \
    import join, dirname

from numpy \
    import sqrt

from numpy.random \
    import random

from traits.api \
    import HasTraits, Property, Array

from traitsui.api \
    import View, Item, TabularEditor

from traitsui.tabular_adapter \
    import TabularAdapter

from traitsui.menu \
    import NoButtons

from pyface.image_resource \
    import ImageResource

#--<Constants>------------------------------------------------------------------

# Necessary because of the dynamic way in which the demos are loaded:
import traitsui.api

search_path = [ join( dirname( traitsui.api.__file__ ),
                      'demo', 'Advanced' ) ]

#--[Tabular Adapter Definition]-------------------------------------------------

class ArrayAdapter ( TabularAdapter ):

    columns = [ ( 'i', 'index' ), ( 'x', 0 ), ( 'y', 1 ),  ( 'z', 2 ) ]

    font        = 'Courier 10'
    alignment   = 'right'
    format      = '%.4f'
    index_text  = Property
    index_image = Property

    def _get_index_text ( self ):
        return str( self.row )

    def _get_index_image ( self ):
        x, y, z = self.item
        if sqrt( (x - 0.5) ** 2 + (y - 0.5) ** 2 + (z - 0.5) ** 2 ) <= 0.25:
            return 'red_flag'
        return None

#--[Tabular Editor Definition]--------------------------------------------------

tabular_editor = TabularEditor(
    adapter = ArrayAdapter(),
    images  = [ ImageResource( 'red_flag', search_path = search_path ) ]
)

#--[ShowArray Class]------------------------------------------------------------

class ShowArray ( HasTraits ):

    data = Array

    view = View(
        Item( 'data', editor = tabular_editor, show_label = False ),
        title     = 'Array Viewer',
        width     = 0.3,
        height    = 0.8,
        resizable = True,
        buttons   = NoButtons
    )

#--[Example Code*]--------------------------------------------------------------

demo = ShowArray( data = random( ( 100000, 3 ) ) )

