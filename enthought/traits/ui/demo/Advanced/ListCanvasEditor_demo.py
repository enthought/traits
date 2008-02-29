"""
This demo is currently just a pastiche of some of the very basic capabilities
of the ListCanvasEditor.
"""

#-- Imports --------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, HasPrivateTraits, File, Constant, Int, Str, Property, \
           Instance, List, Tuple, Bool, Any, Range, Enum, implements, \
           cached_property, on_trait_change

from enthought.traits.ui.api \
    import View, Item, ListEditor, ValueEditor, TabularEditor
    
from enthought.traits.ui.ui_traits \
    import ATheme
    
from enthought.traits.ui.theme \
    import Theme
    
from enthought.traits.ui.tabular_adapter \
    import TabularAdapter
    
from enthought.traits.ui.wx.extra.list_canvas_editor \
    import ListCanvasAdapter, IListCanvasAware, ListCanvasEditor, \
           ListCanvasItemMonitor, ListCanvasItem, SnapInfo, GridInfo, \
           GuideInfo, Modified

#-- ListCanvasEditor Control Objects -------------------------------------------

snap_info  = SnapInfo( distance = 10 )
grid_info  = GridInfo( visible = 'always', snapping = False )
guide_info = GuideInfo()

#-- Demonstration of a 'ListCanvasAware' object --------------------------------

class CanvasItemsTabularAdapter ( TabularAdapter ):
    
    columns = [ ( 'Title', 'title' ) ]
    
    def _get_text ( self ):
        return self.item

class CanvasItems ( HasPrivateTraits ):
    
    implements( IListCanvasAware )
    
    #-- IListCanvasAware Implementation ------------------------------------
    
    # The list canvas item associated with this object:
    list_canvas_item = Instance( ListCanvasItem )
    
    #-- Private Traits -----------------------------------------------------
    
    # The titles of all list canvas items:
    titles = Property( depends_on = 'list_canvas_item:canvas:items.title' )
    
    # The index of the currently selected title:
    index = Int
    
    #-- Trait View Definitions ---------------------------------------------
    
    view = View(
        Item( 'titles', 
              show_label = False,
              editor     = TabularEditor(
                               selected_row = 'index',
                               editable     = False,
                               adapter      = CanvasItemsTabularAdapter()
                           )
        )
    )
    
    #-- Property Implementations -------------------------------------------
    
    @cached_property
    def _get_titles ( self ):
        if self.list_canvas_item is None:
            return []
            
        return [ item.title for item in self.list_canvas_item.canvas.items ]
        
    #-- Trait Event Handlers -----------------------------------------------
    
    def _index_changed ( self, index ):
        """ Handles the user selecting a title row.
        """
        self.list_canvas_item.canvas.items[ index ].activate()

#-- Another demonstration of a 'ListCanvasAware' object ------------------------

class ItemSnoop ( HasPrivateTraits ):
    
    #-- Private Traits -----------------------------------------------------
    
    # The list canvas item being snooped:
    item = Instance( ListCanvasItem )
    
    # The item's title:
    title = Property # ( Str )
    
    #-- Trait View Definitions ---------------------------------------------
    
    view = View(
        Item( 'item',
              show_label = False,
              editor     = ValueEditor()
        )
    )
    
    #-- Property Implementations -------------------------------------------
    
    def _get_title ( self ):
        return self.item.title
        
class CanvasSnoop ( HasPrivateTraits ):
    
    implements( IListCanvasAware )
    
    #-- IListCanvasAware Implementation ------------------------------------
    
    # The list canvas item associated with this object:
    list_canvas_item = Instance( ListCanvasItem )
    
    #-- Private Traits -----------------------------------------------------
    
    # The titles of all list canvas items:
    neighbors = List( ItemSnoop )
    
    #-- Trait View Definitions ---------------------------------------------
    
    view = View(
        Item( 'neighbors',
              show_label = False,
              style      = 'custom',
              editor     = ListEditor( use_notebook = True,
                                       dock_style   = 'tab',
                                       export       = 'DockWindowShell',
                                       page_name    = '.title' )
        )
    )
    
    #-- Trait Event Handlers -----------------------------------------------
    
    @on_trait_change( 'list_canvas_item:moved' )
    def _update_neighbors ( self ):
        if self.list_canvas_item is None:
            self.neighbors = []
        else:
            self.neighbors = [ ItemSnoop( item = item )
                               for item in self.list_canvas_item.neighbors ]

#-- A class for encapsulating another object's trait into a ListCanvas object --
                               
class ObjectTrait ( HasPrivateTraits ):
    
    # The object whose trait is being displayed:
    object = Instance( HasTraits )
    
    # The name of the object trait being displayed:
    name = Str
    
    # The value of the specified object trait:
    value = Property
    
    #-- Property Implementations -------------------------------------------
    
    def _get_value ( self ):
        return getattr( self.object, self.name )
        
    def _set_value ( self, value ):
        old = getattr( self.object, self.name )
        if value != old:
            setattr( self.object, self.name, value )
            self.trait_property_changed( 'value', old, value )
    
    #-- Method Overrides ---------------------------------------------------
    
    def trait_view ( self, *args, **traits ):
        name = self.name
        return View(
            Item( 'value', 
                  label  = name, 
                  editor = self.object.trait( name ).get_editor()
            )
        )
 
#-- An adapter for monitoring changes to a Person object on a ListCanvas -------

class PersonMonitor ( ListCanvasItemMonitor ):
    
    @on_trait_change( 'item:object:name' )
    def _name_modified ( self, name ):
        self.item.title = name
        
    @on_trait_change( 'item:moved' )
    def _position_modified ( self ):
        position = self.item.position
        self.adapter.status = '%s moved to (%s,%s) [%s]' % (
               self.item.title, position[0], position[1],
               ', '.join( [ item.title for item in self.item.neighbors ] ) )

#-- The main demo ListCanvas adapter class -------------------------------------               

Person_theme_active = ATheme( Theme( '@ui:GL5TB', label  = ( 14, 14, 25, 3 ),
                                                  border = ( 6, 6, 6, 6 ) ) )

Person_theme_inactive = ATheme( Theme( '@ui:GL5T', label  = ( 14, 14, 25, 3 ),
                                                   border = ( 6, 6, 6, 6 ) ) )

class TestAdapter ( ListCanvasAdapter ):
    
    Person_theme_active        = Person_theme_active
    Person_theme_inactive      = Person_theme_inactive
    Person_theme_hover         = Person_theme_inactive
    ObjectTrait_theme_active   = ATheme( Theme( '@J08', content = 3 ) )
    ObjectTrait_theme_inactive = ATheme( Theme( '@J07', content = 3 ) )
    ObjectTrait_theme_hover    = ATheme( Theme( '@J0A', content = 3 ) )
    
    CanvasItems_size    = Tuple( ( 180, 250 ) )
    CanvasSnoop_size    = Tuple( ( 250, 250 ) )
    
    Person_tooltip      = Property
    Person_can_drag     = Bool( True )
    Person_can_clone    = Bool( True )
    Person_can_delete   = Bool( True )
    # fixme: Why can't we use 'Constant' for this?...
    Person_monitor      = Any( PersonMonitor )
    Person_can_close    = Any( Modified )
    Person_title        = Property
    ListCanvas_can_receive_Person   = Bool( True )
    ListCanvas_can_receive_NoneType = Bool( True )
    File_view = Any( View( Item( 'path' ) ) )
    
    def _get_Person_title ( self ):
        return (self.item.name or '<undefined>')
        
    def _get_Person_tooltip ( self ):
        return ('A person named %s' % self.item.name)

#-- Some demo classes used to populate the canvas ------------------------------

class Person ( HasTraits ):
    name   = Str
    age    = Range( 0, 100 )
    gender = Enum( 'Male', 'Female' )
    
    view = View( 'name', 'age', 'gender' )
    
class AFile ( HasTraits ):
    file = File
    
    view = View( 
        Item( 'file', style = 'custom', show_label = False )
    )
    
class People ( HasTraits ):
    people = List
    
    view = View( 
        Item( 'people',
              show_label = False,
              editor = ListCanvasEditor(
                           scrollable = True,
                           adapter    = TestAdapter(),
                           operations = [ 'add', 'clear', 'load', 'save',
                                          'status' ],
                           add        = [ Person, AFile ],
                           snap_info  = snap_info,
                           grid_info  = grid_info,
                           guide_info = guide_info )
        ),
        title     = 'List Canvas Test',
        id        = 'enthought.traits.ui.wx.extra.list_canvas_editor',
        width     = 0.75,
        height    = 0.75,
        resizable = True 
    )

nick = Person( name   = 'Nick Adams', 
               age    = 37,
               gender = 'Male' )

#-- The initial set of objects used to populate the canvas ---------------------

people = [ 
    nick,
    Person( name   = 'Joan Thomas',
            age    = 42,
            gender = 'Female' ),
    Person( name   = 'John Jones',
            age    = 27,
            gender = 'Male' ),
    Person( name   = 'Tina Gerlitz',
            age    = 51,
            gender = 'Female' ),
    AFile(),
    AFile(),
    ObjectTrait( object = nick, name = 'name'   ), 
    ObjectTrait( object = nick, name = 'age'    ), 
    ObjectTrait( object = nick, name = 'gender' ), 
    snap_info, grid_info, guide_info, CanvasItems(), CanvasSnoop()
]

#-- Run the demo ---------------------------------------------------------------

# Create the demo:
demo = People( people = people )

# Run the demo ( if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
    
