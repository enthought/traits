#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   06/21/2002
#
#  Refactored into a separate module: 07/04/2003
#
#------------------------------------------------------------------------------

""" Defines common, low-level capabilities needed by the Traits package.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os
import sys

from os \
    import getcwd, makedirs

from os.path \
    import isdir, dirname, exists, join

from string \
    import lowercase, uppercase, capwords

from types \
    import ListType, TupleType, DictType, StringType, UnicodeType, IntType, \
           LongType, FloatType, ComplexType, ClassType, TypeType

# Set the Python version being used:           
vi = sys.version_info
python_version = vi[0] + (float( vi[1] ) / 10.0)

try:
    from enthought.etsconfig.api import ETSConfig
except:
    # If the ETSConfig package is not available, fake it:
    class ETSConfig ( object ):

        #-----------------------------------------------------------------------
        #  'object' interface:
        #-----------------------------------------------------------------------
    
        def __init__ ( self ):
            """ Constructor.
    
                Note that this constructor can only ever be called from within
                this module, since we don't expose the class.
            """
            # Shadow attributes for properties:
            self._application_data = None
            self._toolkit          = None
    
            return

        #-----------------------------------------------------------------------
        #  'ETSConfig' interface:
        #-----------------------------------------------------------------------
    
        #-- Property Implementations -------------------------------------------
    
        def _get_application_data ( self ):
            """ Property getter.
    
                This is a directory that applications and packages can safely 
                write non-user accessible data to i.e. configuration 
                information, preferences etc.
    
                Do not put anything in here that the user might want to navigate 
                to (e.g. projects, user data files, etc).
    
                The actual location differs between operating systems.
            """
            if self._application_data is None:
                self._application_data = self._initialize_application_data()
    
            return self._application_data
    
        def _set_application_data ( self, application_data ):
            """ Property setter.
            """
            self._application_data = application_data
    
        application_data = property( _get_application_data, 
                                     _set_application_data )

        def _get_toolkit ( self ):
            """
            Property getter for the GUI toolkit.  The value returned is, in 
            order of preference: the value set by the application; the value 
            passed on the command line using the '-toolkit' option; the value 
            specified by the 'ETS_TOOLKIT' environment variable; otherwise the 
            empty string.
            """
            if self._toolkit is None:
                self._toolkit = self._initialize_toolkit()
    
            return self._toolkit
    
        def _set_toolkit ( self, toolkit ):
            """
            Property setter for the GUI toolkit.  The toolkit can be set more 
            than once, but only if it is the same one each time.  An application 
            that is written for a particular toolkit can explicitly set it 
            before any other module that gets the value is imported.
    
            """
            if self._toolkit and (self._toolkit != toolkit):
                raise ValueError( 'Cannot set toolkit to %s because it has '
                         'already been set to %s' % ( toolkit, self._toolkit ) )
    
            self._toolkit = toolkit
    
            return
    
        toolkit = property( _get_toolkit, _set_toolkit )
        
        #-- Private Methods ----------------------------------------------------
        
        def _initialize_application_data ( self ):
            """ Initializes the (default) application data directory.
            """
            if sys.platform == 'win32':
                environment_variable = 'APPDATA'
                directory_name       = 'Enthought'
    
            else:
                environment_variable = 'HOME'
                directory_name       = '.enthought'
    
            # Lookup the environment variable:
            parent_directory = os.environ.get( environment_variable, None )
            if parent_directory is None:
                raise ValueError( 'Environment variable "%s" not set' % 
                                  environment_variable )
    
            application_data = os.path.join( parent_directory, directory_name )
    
            # If a file already exists with this name then make sure that it is
            # a directory!
            if os.path.exists( application_data ):
                if not os.path.isdir( application_data ):
                    raise ValueError( 'File "%s" already exists' % 
                                      application_data )
    
            # Otherwise, create the directory:
            else:
                os.makedirs( application_data )
    
            return application_data
            
        def _initialize_toolkit ( self ):
            """ Initializes the toolkit.
            """
            # We handle the command line option even though it doesn't have the
            # highest precedence because we always want to remove it from the
            # command line:
            if '-toolkit' in sys.argv:
                opt_idx = sys.argv.index( '-toolkit' )
    
                try:
                    opt_toolkit = sys.argv[ opt_idx + 1 ]
                except IndexError:
                    raise ValueError( 'The -toolkit command line argument must '
                                      'be followed by a toolkit name' )
    
                # Remove the option:
                del sys.argv[ opt_idx: opt_idx + 1 ]
            else:
                opt_toolkit = None
    
            if self._toolkit is not None:
                toolkit = self._toolkit
            elif opt_toolkit is not None:
                toolkit = opt_toolkit
            else:
                toolkit = os.environ.get( 'ETS_TOOLKIT', '' )
    
            return toolkit

    ETSConfig = ETSConfig()

#-------------------------------------------------------------------------------
#  Provide Python 2.3+ compatible definitions (if necessary):
#-------------------------------------------------------------------------------

try:
    from types import BooleanType
except ImportError:
    BooleanType = IntType

def _enumerate ( seq ):
    for i in xrange( len( seq) ):
        yield i, seq[i]
try:
    enumerate = enumerate
except:
    enumerate = _enumerate
del _enumerate

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

ClassTypes    = ( ClassType, TypeType )

SequenceTypes = ( ListType, TupleType )

ComplexTypes  = ( float, int )

TypeTypes     = ( StringType,  UnicodeType, IntType,   LongType, FloatType,
                  ComplexType, ListType,    TupleType, DictType, BooleanType )

TraitNotifier = '__trait_notifier__'

#-------------------------------------------------------------------------------
#  Singleton 'Undefined' object (used as undefined trait name and/or value):
#-------------------------------------------------------------------------------

class _Undefined ( object ):

   def __repr__ ( self ):
       return '<undefined>'

# Singleton object that indicates that a trait attribute has not yet had a
# value set (i.e., its value is undefined. This object is used instead of
# None, because None is often has other meanings, such as that a value
# is not used. When a trait attribute is first assigned a value, and its
# associated trait notification handlers are called, Undefined is passed
# as the *old* parameter, to indicate that the attribute previously had no
# value.
Undefined = _Undefined()

# Tell the C-base code about the 'Undefined' objects:
import ctraits
ctraits._undefined( Undefined )

#-------------------------------------------------------------------------------
#  Singleton 'Missing' object (used as missing method argument marker):
#-------------------------------------------------------------------------------

class _Missing ( object ):

   def __repr__ ( self ):
       return '<missing>'

# Singleton object that indicates that a method argument is missing from a
# type-checked method signature.
Missing = _Missing()

#-------------------------------------------------------------------------------
#  Singleton 'Self' object (used as object reference to current 'object'):
#-------------------------------------------------------------------------------

class _Self ( object ):

   def __repr__ ( self ):
       return '<self>'

# Singleton object that references the current 'object'.
Self = _Self()

#-------------------------------------------------------------------------------
#  Define a special 'string' coercion function:
#-------------------------------------------------------------------------------

def strx ( arg ):
    """ Wraps the built-in str() function to raise a TypeError if the
    argument is not of a type in StringTypes.
    """
    if type( arg ) in StringTypes:
       return str( arg )
    raise TypeError

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

StringTypes = ( StringType, UnicodeType, IntType, LongType, FloatType,
                ComplexType )

#-------------------------------------------------------------------------------
#  Define a mapping of coercable types:
#-------------------------------------------------------------------------------

# Mapping of coercable types.
CoercableTypes = {
    LongType:    ( 11, long, int ),
    FloatType:   ( 11, float, int ),
    ComplexType: ( 11, complex, float, int ),
    UnicodeType: ( 11, unicode, str )
}

#-------------------------------------------------------------------------------
#  Return a string containing the class name of an object with the correct
#  article (a or an) preceding it (e.g. 'an Image', 'a PlotValue'):
#-------------------------------------------------------------------------------

def class_of ( object ):
    """ Returns a string containing the class name of an object with the
    correct indefinite article ('a' or 'an') preceding it (e.g., 'an Image',
    'a PlotValue').
    """
    if isinstance( object, basestring ):
        return add_article( object )

    return add_article( object.__class__.__name__ )

#-------------------------------------------------------------------------------
#  Return a string containing the right article (i.e. 'a' or 'an') prefixed to
#  a specified string:
#-------------------------------------------------------------------------------

def add_article ( name ):
    """ Returns a string containing the correct indefinite article ('a' or 'an')
    prefixed to the specified string.
    """
    if name[:1].lower() in 'aeiou':
       return 'an ' + name

    return 'a ' + name

#----------------------------------------------------------------------------
#  Return a 'user-friendly' name for a specified trait:
#----------------------------------------------------------------------------

def user_name_for ( name ):
    """ Returns a "user-friendly" version of a string, with the first letter
    capitalized and with underscore characters replaced by spaces. For example,
    ``user_name_for('user_name_for')`` returns ``'User name for'``.
    """
    name       = name.replace( '_', ' ' )
    result     = ''
    last_lower = False

    for c in name:
        if (c in uppercase) and last_lower:
           result += ' '
        last_lower = (c in lowercase)
        result    += c

    return capwords( result )

#-------------------------------------------------------------------------------
#  Gets the path to the traits home directory:
#-------------------------------------------------------------------------------

_traits_home = None

def traits_home ( ):
    """ Gets the path to the Traits home directory.
    """
    global _traits_home

    if _traits_home is None:
        _traits_home = _verify_path( join( ETSConfig.application_data, 'traits' ) )

    return _traits_home

#-------------------------------------------------------------------------------
#  Verify that a specified path exists, and try to create it if it doesn't:
#-------------------------------------------------------------------------------

def _verify_path ( path ):
    """ Verify that a specified path exists, and try to create it if it
        does not exist.
    """
    if not exists( path ):
        try:
            os.mkdir( path )
        except:
            pass

    return path

#-------------------------------------------------------------------------------
#  Returns the name of the module the caller's caller is located in:
#-------------------------------------------------------------------------------

def get_module_name ( level = 2 ):
    """ Returns the name of the module that the caller's caller is located in.
    """
    return sys._getframe( level ).f_globals.get( '__name__', '__main__' )

#-------------------------------------------------------------------------------
#  Returns a resource path calculated from the caller's stack:
#-------------------------------------------------------------------------------

def get_resource_path ( level = 2 ):
    """Returns a resource path calculated from the caller's stack.
    """
    module = sys._getframe( level ).f_globals.get( '__name__', '__main__' )

    if module != '__main__':
        # Return the path to the module:
        try:
            return dirname( getattr( sys.modules.get( module ), '__file__' ) )
        except:
            # Apparently 'module' is not a registered module...treat it like
            # '__main__':
            pass

    # '__main__' is not a real module, so we need a work around:
    for path in [ dirname( sys.argv[0] ), getcwd() ]:
        if exists( path ):
            break

    return path

