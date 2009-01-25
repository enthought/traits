#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

"""
A mock application that demonstrates several advanced Traits UI techniques.

The scenario is as follows...

We are conducting a simulated experiment. The experiment contains a number of
variables, each of which will have a value for each of some number of sample
points. We wish to display a table containing a column for each variable in the
experiment, and a row for each sample point.

We will use the <b>MVC</b> (Model/View/Controller) design pattern to implement 
this application. The model will consist of:
    
 - <b>Experiment</b>: Defines the experiment, the set of variables, and the 
   number of sample points.
  
 - <b>Variable</b>: Defines a single experimental variable: its name, units, 
   description and the set of values for each experimental sample point.
  
Techniques worth studying:

 - Use of MVC (The <b>Experiment</b> and <b>Variable</b> model classes contain 
   no UI code).    
 - The main UI class (i.e. <b>ExperimentView</b>) is almost 100% declarative. 
   Most of the UI logic is in the <b>VariableAdapter</b> class, which adapts 
   the non-tabular model objects into a tabular format.
 - Use of the <i>dock</i> trait to allow the user to reorganize the UI.
 - Use of the <i>export</i> trait to allow the user to drag sub-views out of 
   the main window to make optimum use of all available screen real estate.
 - Use of <b>Theme</b> objects to enhance UI appearance.
 - Use of the <b>ThemedSliderEditor</b> as an alternative to the default slider
   editor.
 - Use of the <b>ThemedVerticalNotebookEditor</b> to allow easy access to the
   various <b>Variable</b> parameters.
 - Definition of the <b>Slider</b> class to simplify <b>View</b> creation.
 - The use of the <b>Controller</b> class to bind the model and view classes.
 - The <i>on_trait_change</i> decorator preceding the <i>_calculate_values</i> 
   method. It allows multiple events to trigger the same event handler.
 - The <i>on_trait_change decorator</i> preceding the <i>_register_variables</i>
   method. It provides a simpler form of event handling for list events.
 - The <i>columns</i> property of the <b>VariableAdapter</b> class. It allows 
   the <b>VariableAdapter</b> class to dynamically adapt to the number of 
   variables in the <b>Experiment</b> model.
  
Notes: 
 - This demo requires the <b>numpy</b> package.
 - Normally, use of the <b>ImageResource</b> class would not be necessary in 
   this program. However, because it is loaded dynamically by the demo program 
   framework, the search path must be specified explicitly.
 - Try commenting out the line <i>multiple_open = True</i>, which allows more 
   than one <b>Variable</b> object to be open at once.
 - Try dragging the handles along the top part of each view to reorganize the
   view layout. Whatever changes you make will be persisted from one invocation
   of the program to another. The persistence is enabled through the use of the
   <i>id</i> traits in the <b>View</b> and <b>Group</b> objects. The ability to
   rearrange the views is enabled via the <i>dock</i> trait set in several of
   the <b>Group</b> objects.
 - Try dragging a view completely out of the Traits UI demo program window and
   dropping it on your desktop. This feature is enabled via the <i>export</i>
   trait set in several of the <b>Group</b> objects.
"""

#-- Imports --------------------------------------------------------------------

import enthought.traits.ui

from numpy \
    import arange
    
from os.path \
    import join, dirname

from enthought.traits.api \
    import HasTraits, Str, List, Instance, Expression, Array, \
           Range, Property, Any, TraitListEvent, on_trait_change, \
           cached_property
    
from enthought.traits.ui.api \
    import Controller, View, HSplit, HGroup, VGroup, Item, Label, Theme, \
           TabularEditor
    
from enthought.traits.ui.ui_traits \
    import ATheme
    
from enthought.traits.ui.wx.themed_vertical_notebook_editor \
    import ThemedVerticalNotebookEditor
    
from enthought.traits.ui.wx.themed_slider_editor \
    import ThemedSliderEditor
    
from enthought.traits.ui.tabular_adapter \
    import TabularAdapter

from enthought.pyface.image_resource \
    import ImageResource
    
#-- Constants ------------------------------------------------------------------

# Necessary because of the dynamic way in which the demos are loaded:
search_path = [ join( dirname( enthought.traits.api.__file__ ),
                      '..', '..', 'examples', 'demo', 'Applications' ) ]
    
#-- Variable Class -------------------------------------------------------------

class Variable ( HasTraits ):

    # The name of the variable:
    name = Str

    # The units in which the variable is measured:
    units = Str

    # A description of what the variable is:
    description = Str
    
    # The value of the variable at each sample point:
    values = Array
    
    # The experiment the variable belongs to:
    experiment = Any
    
    # A formula used to calculate the values (for purposes of this demo only):
    formula = Expression
    
    # Formula coefficients (for purposes of this demo only):
    a = Range( -2.0, 2.0, 1.0 )
    b = Range( -2.0, 2.0, 0.0 )
    
    #-- Event Handlers ---------------------------------------------------------
    
    @on_trait_change( 'formula, a, b, experiment.index_values' ) 
    def _calculate_values ( self ):
        try:
            self.values = eval( self.formula_, globals(),
                                { 'x': self.experiment.index_values,
                                  'a': self.a,
                                  'b': self.b } )
        except:
            # You might not be keying in a valid formula...
            pass

#-- Experiment Class -----------------------------------------------------------

class Experiment ( HasTraits ):

    # The name of the experiment:
    name = Str( 'Experiment' )

    # The set of experimental variables:
    variables = List( Variable )

    # The number of sample points:
    sample_points = Range( 2, 1000, 20 )  
    
    # The index values for each sample point:
    index_values = Array
    
    #-- Event Handlers ---------------------------------------------------------
        
    @on_trait_change( 'variables[]' )
    def _register_variables ( self, object, name, deleted, added ):
        """ Registers/unregisters the experiment a variable belongs to when it
            is added to or deleted from the experiment.
        """
        for variable in deleted:
            variable.experiment = None
            
        for variable in added:
            variable.experiment = self
            
    def _sample_points_changed ( self, n ):
        """ Recalculates the index values when the number of sample points 
            change.
        """
        self.index_values = arange( 0.0, 1.000001, 1.0 / (n - 1) )
        
#-- Tabular Adapter Definition -------------------------------------------------

class VariableAdapter ( TabularAdapter ):

    columns      = Property 
    font         = 'Courier 10'
    alignment    = 'right'
    format       = '%.4f'
    index_format = Str( '%d' )
    index_text   = Property
    at_text      = Property
    
    #-- Adapter Method Overrides -----------------------------------------------
    
    def len ( self, object, trait ):
        """ Returns the number of items in the specified *object.trait" list.
        """
        return object.sample_points
    
    #-- Property Implementations -----------------------------------------------
    
    @cached_property
    def _get_columns ( self ):
        variables = getattr( self.object, self.name )
        for i in range( len( variables ) ):
            self.add_trait( 'v_%d_text' % i, 
                            Property( VariableAdapter._get_variable_value ) )
            
        return ([ ( 'i', 'index' ), ( 'at', 'at' ) ] +
                [ ( var.name, 'v_%d' % i ) 
                  for i, var in enumerate( variables ) ])
                  
    def _get_index_text ( self ):
        return str( self.row )
        
    def _get_at_text ( self ):
        return '%.3f' % self.object.index_values[ self.row ]
        
    #-- Private Methods --------------------------------------------------------
    
    def _get_variable_value ( self, name ):
        variables = getattr( self.object, self.name )
        return '%.3f' % variables[ int( name[2:-5] ) ].values[ self.row ]

#-- Variable Traits View -------------------------------------------------------        

class Slider ( Item ):
    editor     = ThemedSliderEditor( slider_color = 0xC3D3FD )
    item_theme = ATheme( Theme( ImageResource( 'GG5', 
                                               search_path = search_path ), 
                                content = 1 ) )

variable_view = View(
    Item( 'units' ),
    Item( 'description', style = 'custom' ),
    Item( 'formula' ),
    Slider( 'a', label = 'a' ),
    Slider( 'b', label = 'b' )
)

label_theme = Theme( ImageResource( 'header', 
                                    search_path = search_path ),
                     label     = ( 0, 5 ),
                     alignment = 'center' )


#-- ExperimentView Controller Class --------------------------------------------

class ExperimentView ( Controller ):
    
    #-- Traits Views -----------------------------------------------------------
    
    view = View(
        HSplit(
            VGroup(
                Label( 'Experiment Variables', label_theme ), 
                '_',
                Item( 'variables',
                      show_label = False,
                      editor = ThemedVerticalNotebookEditor(
                          closed_theme = Theme( 
                              ImageResource( 'notebook_close', 
                                             search_path = search_path ) ),
                          open_theme = Theme(
                              ImageResource( 'notebook_open', 
                                             search_path = search_path ) ),
                          multiple_open = True,
                          scrollable    = True,
                          double_click  = False,
                          page_name     = '.name',
                          view          = variable_view
                      )
                ),
                label  = 'Variables',
                dock   = 'horizontal',
                export = 'DockWindowShell'
            ),
            VGroup(
                Label( 'Experiment Variables', label_theme ), 
                '_',
                Item( 'variables',
                      show_label = False,
                      editor     = TabularEditor( adapter = VariableAdapter() ),
                      item_theme = Theme( ImageResource( 'TFB', 
                                              search_path = search_path ) ),
                      id         = 'variables'
                ),
                HGroup( 
                    Slider( 'sample_points', springy = True ),
                    group_theme = Theme( ImageResource( 'TFB', 
                                             search_path = search_path ), 
                                         content = -5 )
                ),
                label  = 'Summary',
                dock   = 'horizontal',
                export = 'DockWindowShell'
            ),
            id = 'splitter'
        ),
        id = 'enthought.traits.ui.demo.application.display_variables.'
             'ExperimentView',
    )
    
    #-- Event Handlers ---------------------------------------------------------
    
    @on_trait_change( 'model:variables:values, model:sample_points' )
    def _update_variables ( self ):
        """ Force an update to the experiment variables if any of the
            values get recalculated.
        """
        self.model.trait_property_changed( 'variables_items', None, 
                                           TraitListEvent() )
    
#-- Set Up ---------------------------------------------------------------------

# Create the experiment model:
experiment = Experiment( name = 'Gravitational Constant' )
experiment.variables = [
    Variable( name = 'alpha', units = 'muons',   description = 'a thingy',
              formula = 'a*x*x-b*x' ),
    Variable( name = 'beta',  units = 'm/s',     description = 'a watzit',
              formula = '-a*x+b' ),
    Variable( name = 'gamma', units = 'quarks/s', description = 'a ducky',
              formula = 'a-x' )
]
experiment.sample_points = 50

# Create the controller:
demo = ExperimentView( model = experiment )

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    # Note: The following code is a work-around for a current design bug in
    # the Traits 'configure_traits' method that occurs when the object is a
    # subclass of Handler (as ExperimentView is):
    class ShowDemo ( HasTraits ):
        demo = Instance( ExperimentView )
        
        view = View( 
            Item( 'demo', style = 'custom', show_label = False ),
            title     = 'Experimental Results',
            id        = 'enthought.traits.ui.demo.application.'
                        'display_variables',
            width     = 0.5,
            height    = 0.7,
            resizable = True
        )
        
    ShowDemo( demo = demo ).configure_traits()
                  
