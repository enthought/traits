#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: David C. Morrill
# Date: 01/12/2005
# Description: Traits DB Viewing Tool (TV)
# ------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import tdb, HasTraits, HasStrictTraits, Property, Instance, Str, CTrait, \
           List
           
from enthought.traits.ui.api \
    import TreeEditor, TreeNode, View, Item

#-------------------------------------------------------------------------------
#  'TVPackage' class:  
#-------------------------------------------------------------------------------

class TVPackage ( HasStrictTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    name    = Str
    package = Str
    items   = List

    #---------------------------------------------------------------------------
    #  Default value implementation:  
    #---------------------------------------------------------------------------
        
    def _items_default ( self ):
        package = self.package
        return ([ TVPackage( package = '%s.%s' % ( package, name ) )
                  for name in tdb.packages( package ) ] +
                [ TVTrait( fq_name = '%s.%s' % ( package, name ) )
                  for name in tdb.names( package ) ])
        
    def _name_default ( self ):
        return self.package[ self.package.rfind( '.' ) + 1: ]

#-------------------------------------------------------------------------------
#  'TVPackages' class:  
#-------------------------------------------------------------------------------

class TVPackages ( HasStrictTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    packages = List( TVPackage )

    #---------------------------------------------------------------------------
    #  Default value implementation:  
    #---------------------------------------------------------------------------
        
    def _packages_default ( self ):
        return [ TVPackage( package = name ) for name in tdb.packages() ] 

#-------------------------------------------------------------------------------
#  'TVTrait' class:  
#-------------------------------------------------------------------------------

class TVTrait ( HasStrictTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    name    = Str
    fq_name = Str    
    trait   = Instance( CTrait )
    
    #---------------------------------------------------------------------------
    #  Default value implementations:  
    #---------------------------------------------------------------------------
        
    def _name_default ( self ):
        return self.fq_name[ self.fq_name.rfind( '.' ) + 1: ]
        
    #---------------------------------------------------------------------------
    #  Event handlers:  
    #---------------------------------------------------------------------------
        
    def _fq_name_changed ( self ):
        self.trait = tdb( self.fq_name ) 

#-------------------------------------------------------------------------------
#  'TVCategory' class:  
#-------------------------------------------------------------------------------

class TVCategory ( HasStrictTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    category = Str               # Name of category
    traits   = List( TVTrait )   # Traits defined in this category

    #---------------------------------------------------------------------------
    #  Default value implementation:  
    #---------------------------------------------------------------------------
        
    def _traits_default ( self ):
        return [ TVTrait( fq_name = fq_name ) 
                 for fq_name in tdb.categories( self.category ) ]
        
#-------------------------------------------------------------------------------
#  'TVCategories' class:  
#-------------------------------------------------------------------------------

class TVCategories ( HasStrictTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    categories = List( TVCategory )  # List of all categories

    #---------------------------------------------------------------------------
    #  Default value implementation:  
    #---------------------------------------------------------------------------
        
    def _categories_default ( self ):
        return [ TVCategory( category = category ) 
                 for category in tdb.categories() ]
                                
#-------------------------------------------------------------------------------
#  'TDBView' class: 
#-------------------------------------------------------------------------------

class TDBView ( HasStrictTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    items = List( [ TVPackages(), TVCategories() ] )
    
#-------------------------------------------------------------------------------
#  'TraitTest' class:  
#-------------------------------------------------------------------------------
        
class TraitTest ( HasTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    desc = Str
    help = Str
    
    #---------------------------------------------------------------------------
    #  Traits view definition:  
    #---------------------------------------------------------------------------
        
    traits_view = View( [ [ '_', 
                            Item( 'desc{Description}',
                                  style = 'readonly' ),
                            Item( 'help',
                                  style     = 'readonly',
                                  resizable = True ), '_',
                            '|{Trait Information}' ],
                          [ '_', 
                            Item( 'value{Simple}',   style = 'simple'   ), '_', 
                            Item( 'value{Custom}',   style = 'custom'   ), '_', 
                            Item( 'value{Text}',     style = 'text'     ), '_', 
                            Item( 'value{Readonly}', style = 'readonly' ),
                            '|{Trait Editors}' ],
                        '|<>' ],
                        resizable = True )
    
#-------------------------------------------------------------------------------
#  'TDB' class:  
#-------------------------------------------------------------------------------
        
class TDB ( HasStrictTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    view = Instance( TDBView, () )
    test = Instance( TraitTest )
    
#-------------------------------------------------------------------------------
#  Handles a trait (or other object) being selected:  
#-------------------------------------------------------------------------------
        
def select_trait ( object ):
    """ Handles a trait (or other object) being selected.
    """
    if isinstance( object, TVTrait ):
        trait = object.trait
        test  = TraitTest( desc = trait.desc or '', 
                           help = trait.help or '' )
        test.add_trait( 'value', trait )
        try:
            test.value
            the_tdb.test = test
            
            return
        except:
            pass
            
    the_tdb.test = None
    
#-------------------------------------------------------------------------------
#  Define the tree editor:  
#-------------------------------------------------------------------------------

tdb_editor = TreeEditor(
    editable  = False,
    on_select = select_trait, 
    nodes     = [
        TreeNode( node_for   = [ TDBView ],
                  children   = 'items',
                  copy       = False,
                  delete     = False,
                  rename     = False,
                  label      = '=Traits DB',
                  icon_group = '<group>',
                  icon_open  = '<open>'
        ),
        TreeNode( node_for   = [ TVPackages ],
                  auto_open  = True,
                  children   = 'packages',
                  copy       = False,
                  delete     = False,
                  rename     = False,
                  label      = '=Packages',
                  icon_group = '<group>',
                  icon_open  = '<open>'
        ),
        TreeNode( node_for   = [ TVPackage ],
                  auto_close = True,
                  children   = 'items',
                  copy       = False,
                  delete     = False,
                  rename     = False,
                  label      = 'name',
                  icon_group = '<group>',
                  icon_open  = '<open>'
        ), 
        TreeNode( node_for   = [ TVCategories ],
                  auto_open  = True,
                  children   = 'categories',
                  copy       = False,
                  delete     = False,
                  rename     = False,
                  label      = '=Categories',
                  icon_group = '<group>',
                  icon_open  = '<open>'
        ),
        TreeNode( node_for   = [ TVCategory ],
                  auto_close = True,
                  children   = 'traits',
                  copy       = False,
                  delete     = False,
                  rename     = False,
                  label      = 'category',
                  icon_group = '<group>',
                  icon_open  = '<open>'
        ),
        TreeNode( node_for   = [ TVTrait ],
                  label      = 'name',
                  icon_item  = '<item>'
        )
    ]
)
    
#-------------------------------------------------------------------------------
#  Run the viewer:  
#-------------------------------------------------------------------------------

the_tdb = TDB()
the_tdb.configure_traits( view = View( 
        [ Item( 'view', 
              editor    = tdb_editor,
              resizable = True ), 
          Item( 'test',
                style     = 'custom',
                resizable = True ), 
          '-splitter1:=<>' ],
        title     = 'Traits Data Base Viewer',
        id        = 'enthought.traits.vet.tv',
        resizable = True,
        width     = .40,
        height    = .75,
    )
)
