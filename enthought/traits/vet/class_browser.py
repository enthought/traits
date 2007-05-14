#-------------------------------------------------------------------------------
#  
#  Implements a Python class browser 'component' intended to serve as a base  
#  for other Python-based tools.
#  
#  Written by: David C. Morrill
#  
#  Date: 08/31/2005
#  
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:  
#-------------------------------------------------------------------------------

import pyclbr

from os \
    import listdir, environ, stat
    
from os.path \
    import join, isdir, exists, splitext, abspath
    
from cPickle \
    import dump, load

from enthought.traits.api \
    import HasPrivateTraits, Str, Int, List, Instance, Property, Any, Code, \
           Delegate, true
    
from enthought.traits.ui.api \
    import TreeEditor, TreeNode, ObjectTreeNode, TreeNodeObject, View, Item
    
#-------------------------------------------------------------------------------
#  'CBTreeNodeObject' class:  
#-------------------------------------------------------------------------------
        
class CBTreeNodeObject ( TreeNodeObject ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Cached result of 'tno_has_children':
    _has_children = Any
    
    # Cached result of 'tno_get_children':
    _get_children = Any
    
    #---------------------------------------------------------------------------
    #  Traits view definitions:  
    #---------------------------------------------------------------------------
        
    traits_view = View( [ 'text@', '|<>' ],
                        export = 'DockShellWindow',
                        dock   = 'tab' )

    #---------------------------------------------------------------------------
    #  Returns whether chidren of this object are allowed or not:  
    #---------------------------------------------------------------------------

    def tno_allows_children ( self, node ):
        """ Returns whether chidren of this object are allowed or not.
        """
        return True
    
    #---------------------------------------------------------------------------
    #  Returns whether or not the object has children:  
    #---------------------------------------------------------------------------

    def tno_has_children ( self, node = None ):
        """ Returns whether or not the object has children.
        """
        if self._has_children is None:
            self._has_children = self.has_children()
        return self._has_children
        
    #---------------------------------------------------------------------------
    #  Gets the object's children:  
    #---------------------------------------------------------------------------

    def tno_get_children ( self, node ):
        """ Gets the object's children.
        """
        if self._get_children is None:
            self._get_children = self.get_children()
        return self._get_children
        
    #---------------------------------------------------------------------------
    #  Returns whether or not the object has children:  
    #---------------------------------------------------------------------------

    def has_children ( self, node ):
        """ Returns whether or not the object has children.
        """
        raise NotImplementedError
        
    #---------------------------------------------------------------------------
    #  Gets the object's children:  
    #---------------------------------------------------------------------------

    def get_children ( self ):
        """ Gets the object's children.
        """
        raise NotImplementedError
        
    #---------------------------------------------------------------------------
    #  Extracts the Python source code for a specified item:  
    #---------------------------------------------------------------------------
    
    def extract_text ( self, text, line_number ):
        """ Extracts the Python source code for a specified item.
        """
        lines  = text.split( '\n' )
        indent = self.indent( lines[ line_number - 1 ] )
        
        for j in range( line_number, len( lines ) ):
            line = lines[j]
            if (not self.ignore( line )) and (self.indent( line ) <= indent):
                break
        else:
            j = len( lines )
            
        for j in range( j - 1, line_number - 2, -1 ):
            if not self.ignore( lines[j] ):
                j += 1
                break
                
        for i in range( line_number - 2, -1, -1 ):
            if not self.ignore( lines[i] ):
                break
        else:
            i = -1
            
        for i in range( i + 1, line_number ):
            if not self.is_blank( lines[i] ):
                break
           
        return '\n'.join( [ line[ indent: ] for line in lines[ i: j ] ] )
        
    #---------------------------------------------------------------------------
    #  Returns the amount of indenting of a specified line:  
    #---------------------------------------------------------------------------
    
    def indent ( self, line ):
        """ Returns the amount of indenting of a specified line.
        """
        return (len( line ) - len( line.lstrip() ))
        
    #---------------------------------------------------------------------------
    #  Returns whether or not a specified line should be ignored:
    #---------------------------------------------------------------------------
    
    def ignore ( self, line ):
        """ Returns whether or not a specified line should be ignored.
        """
        line = line.lstrip()
        return ((len( line ) == 0) or (line.lstrip()[:1] == '#'))
        
    #---------------------------------------------------------------------------
    #  Returns whether or not a specified line is blank:  
    #---------------------------------------------------------------------------
    
    def is_blank ( self, line ):
        """ Returns whether or not a specified line is blank.
        """
        return (len( line.strip() ) == 0)     
    
#-------------------------------------------------------------------------------
#  'CBMethod' class:  
#-------------------------------------------------------------------------------
        
class CBMethod ( CBTreeNodeObject ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------

    # The class containing this method:
    parent = Any
    
    # Name of the method:
    name = Str
    
    # The starting line number of the method within the source file:
    line_number = Int
    
    # The text of the method:
    text = Property( Code )
        
    #---------------------------------------------------------------------------
    #  Implementation of the 'text' property:  
    #---------------------------------------------------------------------------
                
    def _get_text ( self ):
        if self._text is None:
            self._text = self.extract_text( self.parent.parent.text, 
                                            self.line_number )
            
        return self._text
        
    def _set_text ( self, value ):
        pass
        
    #---------------------------------------------------------------------------
    #  Returns whether or not the object has children:  
    #---------------------------------------------------------------------------

    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        return False
        
    #---------------------------------------------------------------------------
    #  Gets the object's children:  
    #---------------------------------------------------------------------------

    def get_children ( self ):
        """ Gets the object's children.
        """
        return []
    
#-------------------------------------------------------------------------------
#  'CBClass' class:  
#-------------------------------------------------------------------------------
        
class CBClass ( CBTreeNodeObject ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # The module containing this class:
    parent = Any
    
    # Name of the class:
    name = Str
    
    # The 'pyclbr' class descriptor:
    descriptor = Any
    
    # The starting line number of the class within the source file:
    line_number = Property
    
    # Methods defined on the class:
    methods = List( CBMethod )
    
    # Should methods be displayed:
    show_methods = Delegate( 'parent' )
    
    # The text of the class:
    text = Property( Code )
    
    #---------------------------------------------------------------------------
    #  Implementation of the 'line_number' property:  
    #---------------------------------------------------------------------------
        
    def _get_line_number ( self ):
        return self.descriptor.lineno
        
    #---------------------------------------------------------------------------
    #  Implementation of the 'text' property:  
    #---------------------------------------------------------------------------
    
    def _get_text ( self ):
        if self._text is None:
            self._text = self.extract_text( self.parent.text, self.line_number )
            
        return self._text
            
    def _set_text ( self ):
        pass
        
    #---------------------------------------------------------------------------
    #  Returns whether or not the object has children:  
    #---------------------------------------------------------------------------

    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        return (self.show_methods and (len( self.descriptor.methods ) > 0))
        
    #---------------------------------------------------------------------------
    #  Gets the object's children:  
    #---------------------------------------------------------------------------

    def get_children ( self ):
        """ Gets the object's children.
        """
        methods = [ CBMethod( parent      = self, 
                              name        = name, 
                              line_number = line_number )
                    for name, line_number in self.descriptor.methods.items() ]
        methods.sort( lambda l, r: cmp( l.name, r.name ) )
        #self.methods = methods
        return methods
    
#-------------------------------------------------------------------------------
#  'CBModule' class:  
#-------------------------------------------------------------------------------
        
class CBModule ( CBTreeNodeObject ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # Parent of this module:
    parent = Any
    
    # Name of file system path to this module:
    path = Property
    
    # Fully qualified name of the module (i.e. package.module):
    full_name = Property
    
    # Name of the module:
    name = Str
    
    # Classes contained in the module:
    classes = List( CBClass )
    
    # Should methods be displayed:
    show_methods = Delegate( 'parent' )
    
    # Can we use cached 'pyclbr' file?
    cache = Delegate( 'parent' )
    
    # The text of the module:
    text = Property( Code )
    
    #---------------------------------------------------------------------------
    #  Implementation of the 'path' property:  
    #---------------------------------------------------------------------------
        
    def _get_path ( self ):
        return join( self.parent.path, self.name + '.py' )
    
    #---------------------------------------------------------------------------
    #  Implementation of the 'full_name' property:  
    #---------------------------------------------------------------------------
        
    def _get_full_name ( self ):
        return self.parent.full_name + self.name
        
    #---------------------------------------------------------------------------
    #  Implementation of the 'text' property:  
    #---------------------------------------------------------------------------
                
    def _get_text ( self ):
        if self._text is None:
            fh = open( self.path, 'rb' )
            self._text = fh.read()
            fh.close()
            
        return self._text    
        
    def _set_text ( self ):
        pass
        
    #---------------------------------------------------------------------------
    #  Returns the 'pyclbr' class browser data for the module:  
    #---------------------------------------------------------------------------
                
    def get_pyclbr ( self ):
        if not self.cache:
            return pyclbr.readmodule( self.full_name, [ self.parent.path ] )
            
        pyclbr_name = join( self.parent.path, self.name + '.pyclbr' )
        if exists( pyclbr_name ):
            pyclbr_stat = stat( pyclbr_name )
            py_stat     = stat( self.path )
            if pyclbr_stat.st_mtime >= py_stat.st_mtime:
                try:
                    file = open( pyclbr_name, 'rb' )
                    try:
                        dic = load( file )
                    finally:
                        file.close()
                    return dic
                except:
                    pass
                    
        dic = pyclbr.readmodule( self.full_name, [ self.parent.path ] )
        try:
            file = open( pyclbr_name, 'wb' )
            try:
                dump( dic, file )
            finally:
                file.close()
        except:
            pass
            
        return dic
        
    #---------------------------------------------------------------------------
    #  Returns whether or not the object has children:  
    #---------------------------------------------------------------------------

    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        dic     = self.get_pyclbr()
        path    = abspath( self.path )
        classes = [ CBClass( parent     = self, 
                             name       = name, 
                             descriptor = descriptor ) 
                    for name, descriptor in dic.items() 
                        if path == abspath( descriptor.file ) ]
        classes.sort( lambda l, r: cmp( l.name, r.name ) )
        self.classes = classes
        return (len( self.classes ) > 0)
        
    #---------------------------------------------------------------------------
    #  Gets the object's children:  
    #---------------------------------------------------------------------------

    def get_children ( self ):
        """ Gets the object's children.
        """
        self.tno_has_children()
        return self.classes
    
#-------------------------------------------------------------------------------
#  'CBPackageBase' class:  
#-------------------------------------------------------------------------------
        
class CBPackageBase ( CBTreeNodeObject ):
        
    #---------------------------------------------------------------------------
    #  Returns whether or not the object has children:  
    #---------------------------------------------------------------------------

    def has_children ( self ):
        """ Returns whether or not the object has children.
        """
        path = self.path
        for name in listdir( path ):
            cur_path = join( path, name )
            if isdir( cur_path ) and exists( join( cur_path, '__init__.py' ) ):
                return True
            module, ext = splitext( name )
            if ((ext == '.py') and
                CBModule( parent = self, name = module ).tno_has_children()):
                return True
        return False
        
    #---------------------------------------------------------------------------
    #  Gets the object's children:  
    #---------------------------------------------------------------------------

    def get_children ( self ):
        """ Gets the object's children.
        """
        packages = []
        modules  = []
        path     = self.path
        for name in listdir( path ):
            cur_path = join( path, name )
            if isdir( cur_path ) and exists( join( cur_path, '__init__.py' ) ):
                packages.append( CBPackage( parent = self, name = name ) )
            else:
                module, ext = splitext( name )
                if ext == '.py':
                    cbm = CBModule( parent = self, name = module )
                    if cbm.tno_has_children():
                        modules.append( cbm )
        packages.sort( lambda l, r: cmp( l.name, r.name ) )
        modules.sort(  lambda l, r: cmp( l.name, r.name ) )
        return (packages + modules)
    
#-------------------------------------------------------------------------------
#  'CBPackage' class:  
#-------------------------------------------------------------------------------
        
class CBPackage ( CBPackageBase ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
     
    # Parent of this package:
    parent = Any
    
    # Name of file system path to this package:
    path = Property
    
    # Fully qualified name of the package (i.e. package.package...):
    full_name = Property
    
    # Name of the package:
    name = Str
    
    # Should methods be displayed:
    show_methods = Delegate( 'parent' )
    
    # Can we use cached 'pyclbr' file?
    cache = Delegate( 'parent' )
    
    # The text of the package (i.e. the '__init__.py' file):
    text = Property( Code )
    
    #---------------------------------------------------------------------------
    #  Implementation of the 'path' property:  
    #---------------------------------------------------------------------------
        
    def _get_path ( self ):
        return join( self.parent.path, self.name )
    
    #---------------------------------------------------------------------------
    #  Implementation of the 'full_name' property:  
    #---------------------------------------------------------------------------
        
    def _get_full_name ( self ):
        return '%s%s.' % ( self.parent.full_name, self.name )
        
    #---------------------------------------------------------------------------
    #  Implementation of the 'text' property:  
    #---------------------------------------------------------------------------
    
    def _get_text ( self ):
        if self._text is None:
            fh = open( join( self.path, '__init__.py' ), 'rb' )
            self._text = fh.read()
            fh.close()
            
        return self._text    
            
    def _set_text ( self ):
        pass
     
#-------------------------------------------------------------------------------
#  'CBPath' class:  
#-------------------------------------------------------------------------------

class CBPath ( CBPackageBase ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Name of a file system directory used as a Python path:
    path = Str
    
    # Fully qualified name of the package (empty for a path):
    full_name = Str
    
    # Should methods be displayed:
    show_methods = true
    
    # Can we use cached 'pyclbr' file?
    cache = true
    
#-------------------------------------------------------------------------------
#  'ClassBrowserPaths' class:  
#-------------------------------------------------------------------------------

class ClassBrowserPaths ( HasPrivateTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
    
    # List of all Python source file paths in the name space:
    paths = List( CBPath )
    
#-------------------------------------------------------------------------------
#  Defines the class browser tree editor(s):  
#-------------------------------------------------------------------------------

# Define a tree-only version:

cb_tree_editor = TreeEditor(
    editable  = False,
    on_select = 'object.select',
    nodes     = [
        TreeNode(       node_for  = [ ClassBrowserPaths ],
                        auto_open = True,
                        children  = 'paths',
                        label     = '=Python Path' ),
        ObjectTreeNode( node_for = [ CBPath ],
                        label     = 'path' ),
        ObjectTreeNode( node_for   = [ CBPackage ],
                        label      = 'name',
                        icon_group = 'package',
                        icon_open  = 'package' ),
        ObjectTreeNode( node_for   = [ CBModule ],
                        label      = 'name',
                        icon_group = 'module',
                        icon_open  = 'module' ),
        ObjectTreeNode( node_for   = [ CBClass ],
                        label      = 'name',
                        icon_group = 'class', 
                        icon_open  = 'class' ),
        ObjectTreeNode( node_for   = [ CBMethod ],
                        label      = 'name',
                        icon_group = 'method', 
                        icon_open  = 'method' )
    ]
)

# Define a tree with source view version:

empty_view = View()

source_view = View( [ 'text@', '|<>' ] )

cb_tree_editor_with_source = TreeEditor(
    nodes = [
        TreeNode(       node_for   = [ ClassBrowserPaths ],
                        auto_open  = True,
                        view       = empty_view,
                        children   = 'paths',
                        label      = '=Python Path' ),
        ObjectTreeNode( node_for   = [ CBPath ],
                        label      = 'path',
                        view       = empty_view ),
        ObjectTreeNode( node_for   = [ CBPackage ],
                        label      = 'name',
                        view       = source_view,
                        icon_group = 'package',
                        icon_open  = 'package' ),
        ObjectTreeNode( node_for   = [ CBModule ],
                        label      = 'name',
                        view       = source_view,
                        icon_group = 'module',
                        icon_open  = 'module' ),
        ObjectTreeNode( node_for   = [ CBClass ],
                        label      = 'name',
                        view       = source_view,
                        icon_group = 'class', 
                        icon_open  = 'class' ),
        ObjectTreeNode( node_for   = [ CBMethod ],
                        label      = 'name',
                        view       = source_view,
                        icon_group = 'method', 
                        icon_open  = 'method' )
    ]
)
        
#-------------------------------------------------------------------------------
#  'ClassBrowser' class:
#-------------------------------------------------------------------------------

class ClassBrowser ( HasPrivateTraits ):
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------

    # Root of the class browser tree:
    root = Instance( ClassBrowserPaths )
    
    # Currently selected object node:
    object = Any
        
    #---------------------------------------------------------------------------
    #  Traits view definitions:  
    #---------------------------------------------------------------------------
        
    traits_view = View( [ Item( name   = 'root',
                                id     = 'root',
                                editor = cb_tree_editor ),
                          '|<>' ],
                        title     = 'Class browser',
                        id        = 'enthought.traits.vet.ClassBrowser',
                        resizable = True,
                        width     = .2,
                        height    = .3 )
                        
    imbedded_traits_view = View( [ Item( name   = 'root',
                                         editor = cb_tree_editor ),
                                   '|<>' ] )
        
    source_view = View( [ Item( name      = 'root', 
                                id        = 'source_root',
                                editor    = cb_tree_editor_with_source,
                                resizable = True ),
                          '|<>' ],
                        title     = 'Class browser',
                        id        = 'enthought.traits.vet.ClassBrowserSourceView',
                        resizable = True,
                        width     = .2,
                        height    = .3 )
        
    imbedded_source_view = View(
        [ Item( name      = 'root', 
                id        = 'imbedded_root',
                editor    = cb_tree_editor_with_source,
                resizable = True ),
          '|<>' ],
        id = 'enthought.traits.vet.ClassBrowserImbeddedSourceView'
    )
                        
    #---------------------------------------------------------------------------
    #  Handles a tree node being selected:    
    #---------------------------------------------------------------------------
                                          
    def select ( self, object ):
        """ Handles a tree node being selected.
        """
        self.object = object

#-------------------------------------------------------------------------------
#  Displays a class browser:  
#-------------------------------------------------------------------------------

def class_browser_for ( paths, configure    = False, 
                               show_methods = True,
                               show_source  = False,
                               cache        = True ):
    """ Displays a class browser.
    """
    if len( paths ) == 0:
        import sys
        paths = sys.path[:]
    paths.sort()
    cb = ClassBrowser( root  = ClassBrowserPaths( 
                       paths = [ CBPath( path         = path, 
                                         show_methods = show_methods,
                                         cache        = cache )
                                 for path in paths ] ) )
    view = 'traits_view'
    if show_source:
        view = 'source_view'
        
    if configure:
        cb.configure_traits( view = view )
    else:
        cb.edit_traits( view = view )
    
#-------------------------------------------------------------------------------
#  Test case:  
#-------------------------------------------------------------------------------
        
if __name__ == '__main__':
    class_browser_for( environ[ 'PYTHONPATH' ].split( ';' ), 
                       configure    = True,
                       cache        = True,
                       show_methods = True,
                       show_source  = True )
    
