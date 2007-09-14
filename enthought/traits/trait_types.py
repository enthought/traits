#------------------------------------------------------------------------------
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date: 03/22/2007
#------------------------------------------------------------------------------

""" Core Trait definitions.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import re

from weakref \
    import ref

from enthought.traits.protocols._speedups \
    import adapt

from trait_base \
    import strx, get_module_name, class_of, SequenceTypes, TypeTypes, \
           ClassTypes, Undefined, python_version
    
from trait_handlers \
    import TraitType, TraitInstance, TraitListObject, TraitDictObject, \
           TraitDictEvent, ThisClass, items_event, RangeTypes
    
from traits \
    import Trait, Event, trait_from, _InstanceArgs, code_editor, html_editor, \
           password_editor, shell_editor

from trait_errors \
    import TraitError
    
from types \
    import FunctionType, MethodType, ClassType, InstanceType

#-------------------------------------------------------------------------------
#  Numeric type fast validator definitions:  
#-------------------------------------------------------------------------------

# The standard python definitions (without numpy):
int_fast_validate     = ( 11, int )
long_fast_validate    = ( 11, long,    None, int )
float_fast_validate   = ( 11, float,   None, int )
complex_fast_validate = ( 11, complex, None, float, int )
bool_fast_validate    = ( 11, bool )

try:
    from numpy import integer, floating, complexfloating, bool_

    # The numpy enhanced definitions:    
    int_fast_validate     = ( 11, int, integer )
    long_fast_validate    = ( 11, long, None, int, integer )
    float_fast_validate   = ( 11, float, floating, None, int, integer )
    complex_fast_validate = ( 11, complex, complexfloating, None, 
                                  float, floating, int, integer )
    bool_fast_validate    = ( 11, bool, bool_ )
except:
    pass
        
#-------------------------------------------------------------------------------
#  Returns a default text editor: 
#-------------------------------------------------------------------------------

def default_text_editor ( trait, type ):
    auto_set = trait.auto_set
    if auto_set is None:
        auto_set = True
        
    from enthought.traits.ui.api import TextEditor
    
    return TextEditor( auto_set  = auto_set,
                       enter_set = trait.enter_set or False,
                       evaluate  = type )

#-------------------------------------------------------------------------------
#  'Any' trait:  
#-------------------------------------------------------------------------------
                  
class Any ( TraitType ):
    """ Defines a trait whose value can be anything.
    """
    
    # Define the default value for the trait:
    default_value = None
    
    # A description of the type of value this trait accepts:
    info_text = 'any value'
                       
#-------------------------------------------------------------------------------
#  'BaseInt' and 'Int' traits:
#-------------------------------------------------------------------------------

class BaseInt ( TraitType ):
    """ Defines a trait whose value must be a Python int.
    """
    
    # The function to use for evaluating strings to this type:
    evaluate = int
    
    # Define the default value for the trait:
    default_value = 0
    
    # A description of the type of value this trait accepts:
    info_text = 'an integer'

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, int ):
            return value
            
        self.error( object, name, value )

    def create_editor ( self ):
        """ Returns the default traits UI editor for this type of trait.
        """
        return default_text_editor( self, int )

        
class Int ( BaseInt ):
    """ Defines a trait whose value must be a Python int using a C-level fast
        validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = int_fast_validate

#-------------------------------------------------------------------------------
#  'BaseLong' and 'Long' traits:
#-------------------------------------------------------------------------------

class BaseLong ( TraitType ):
    """ Defines a trait whose value must be a Python long.
    """
    
    # The function to use for evaluating strings to this type:
    evaluate = long
    
    # Define the default value for the trait:
    default_value = 0L
    
    # A description of the type of value this trait accepts:
    info_text = 'a long'

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, long ):
            return value
            
        if isinstance( value, int ):
            return long( value )
            
        self.error( object, name, value )

    def create_editor ( self ):
        """ Returns the default traits UI editor for this type of trait.
        """
        return default_text_editor( self, long )

        
class Long ( BaseLong ):
    """ Defines a trait whose value must be a Python long using a C-level fast
        validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = long_fast_validate

#-------------------------------------------------------------------------------
#  'BaseFloat' and 'Float' traits:
#-------------------------------------------------------------------------------

class BaseFloat ( TraitType ):
    """ Defines a trait whose value must be a Python float.
    """
    # The function to use for evaluating strings to this type:
    evaluate = float
    
    # Define the default value for the trait:
    default_value = 0.0
    
    # A description of the type of value this trait accepts:
    info_text = 'a float'

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, float ):
            return value
            
        if isinstance( value, int ):
            return float( value )
            
        self.error( object, name, value )
        
    def create_editor ( self ):
        """ Returns the default traits UI editor for this type of trait.
        """
        return default_text_editor( self, float )

        
class Float ( BaseFloat ):
    """ Defines a trait whose value must be a Python float using a C-level fast
        validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = float_fast_validate

#-------------------------------------------------------------------------------
#  'BaseComplex' and 'Complex' traits:
#-------------------------------------------------------------------------------

class BaseComplex ( TraitType ):
    """ Defines a trait whose value must be a Python complex.
    """
    
    # The function to use for evaluating strings to this type:
    evaluate = complex
    
    # Define the default value for the trait:
    default_value = 0.0 + 0.0j
    
    # A description of the type of value this trait accepts:
    info_text = 'a complex number'

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, complex ):
            return value
            
        if isinstance( value, ( float, int ) ):
            return complex( value )
            
        self.error( object, name, value )

    def create_editor ( self ):
        """ Returns the default traits UI editor for this type of trait.
        """
        return default_text_editor( self, complex )

        
class Complex ( BaseComplex ):
    """ Defines a trait whose value must be a Python complex using a C-level
        fast validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = complex_fast_validate

#-------------------------------------------------------------------------------
#  'BaseStr' and 'Str' traits:
#-------------------------------------------------------------------------------

class BaseStr ( TraitType ):
    """ Defines a trait whose value must be a Python string.
    """
    
    # Define the default value for the trait:
    default_value = ''
    
    # A description of the type of value this trait accepts:
    info_text = 'a string'

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, basestring ):
            return value
            
        self.error( object, name, value )

    def create_editor ( self ):
        """ Returns the default traits UI editor for this type of trait.
        """
        from traits import multi_line_text_editor
        
        return multi_line_text_editor()

        
class Str ( BaseStr ):
    """ Defines a trait whose value must be a Python string using a C-level
        fast validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 11, basestring )

#-------------------------------------------------------------------------------
#  'BaseUnicode' and 'Unicode' traits:
#-------------------------------------------------------------------------------

class BaseUnicode ( TraitType ):
    """ Defines a trait whose value must be a Python unicode string.
    """
    
    # Define the default value for the trait:
    default_value = u''
    
    # A description of the type of value this trait accepts:
    info_text = 'a unicode string'

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, unicode ):
            return value
            
        if isinstance( value, str ):
            return unicode( value )
            
        self.error( object, name, value )

    def create_editor ( self ):
        """ Returns the default traits UI editor for this type of trait.
        """
        from traits import multi_line_text_editor
        
        return multi_line_text_editor()

        
class Unicode ( BaseUnicode ):
    """ Defines a trait whose value must be a Python unicode string using a 
        C-level fast validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 11, unicode, None, str )

#-------------------------------------------------------------------------------
#  'BaseBool' and 'Bool' traits:
#-------------------------------------------------------------------------------

class BaseBool ( TraitType ):
    """ Defines a trait whose value must be a Python boolean.
    """
    
    # The function to use for evaluating strings to this type:
    evaluate = bool
    
    # Define the default value for the trait:
    default_value = False
    
    # A description of the type of value this trait accepts:
    info_text = 'a boolean'

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        if isinstance( value, bool ):
            return value
            
        self.error( object, name, value )

    def create_editor ( self ):
        """ Returns the default traits UI editor for this type of trait.
        """
        from enthought.traits.ui.api import BooleanEditor
        
        return BooleanEditor()

        
class Bool ( BaseBool ):
    """ Defines a trait whose value must be a Python boolean using a C-level
        fast validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = bool_fast_validate

#-------------------------------------------------------------------------------
#  'BaseCInt' and 'CInt' traits:
#-------------------------------------------------------------------------------

class BaseCInt ( BaseInt ):
    """ Defines a trait whose value must be a Python int and which supports
        coercions of non-int values to int.
    """
    
    # The function to use for evaluating strings to this type:
    evaluate = int

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return int( value )
        except:
            self.error( object, name, value )

            
class CInt ( BaseCInt ):
    """ Defines a trait whose value must be a Python int and which supports
        coercions of non-int values to int using a C-level fast validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 12, int )

#-------------------------------------------------------------------------------
#  'BaseCLong' and 'CLong' traits:
#-------------------------------------------------------------------------------

class BaseCLong ( BaseLong ):
    """ Defines a trait whose value must be a Python long and which supports
        coercions of non-long values to long.
    """
    
    # The function to use for evaluating strings to this type:
    evaluate = long

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return long( value )
        except:
            self.error( object, name, value )

            
class CLong ( BaseCLong ):
    """ Defines a trait whose value must be a Python long and which supports
        coercions of non-long values to long using a C-level fast validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 12, long )

#-------------------------------------------------------------------------------
#  'BaseCFloat' and 'CFloat' traits:
#-------------------------------------------------------------------------------

class BaseCFloat ( BaseFloat ):
    """ Defines a trait whose value must be a Python float and which supports
        coercions of non-float values to float.
    """
    
    # The function to use for evaluating strings to this type:
    evaluate = float

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return float( value )
        except:
            self.error( object, name, value )

            
class CFloat ( BaseCFloat ):
    """ Defines a trait whose value must be a Python float and which supports
        coercions of non-float values to float using a C-level fast validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 12, float )

#-------------------------------------------------------------------------------
#  'BaseCComplex' and 'CComplex' traits:
#-------------------------------------------------------------------------------

class BaseCComplex ( BaseComplex ):
    """ Defines a trait whose value must be a Python complex and which supports
        coercions of non-complex values to complex.
    """
    
    # The function to use for evaluating strings to this type:
    evaluate = complex

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return complex( value )
        except:
            self.error( object, name, value )

            
class CComplex ( BaseCComplex ):
    """ Defines a trait whose value must be a Python complex and which supports
        coercions of non-complex values to complex using a C-level fast
        validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 12, complex )

#-------------------------------------------------------------------------------
#  'BaseCStr' and 'CStr' traits:
#-------------------------------------------------------------------------------

class BaseCStr ( BaseStr ):
    """ Defines a trait whose value must be a Python string and which supports
        coercions of non-string values to string.
    """

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return str( value )
        except:
            try:
                return unicode( value )
            except:
                self.error( object, name, value )

                
class CStr ( BaseCStr ):
    """ Defines a trait whose value must be a Python string and which supports
        coercions of non-string values to string using a C-level fast 
        validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 7, ( ( 12, str ), ( 12, unicode ) ) )

#-------------------------------------------------------------------------------
#  'BaseCUnicode' and 'CUnicode' traits:
#-------------------------------------------------------------------------------

class BaseCUnicode ( BaseUnicode ):
    """ Defines a trait whose value must be a Python unicode string and which
        supports coercions of non-unicode values to unicode.
    """

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return unicode( value )
        except:
            self.error( object, name, value )

            
class CUnicode ( BaseCUnicode ):
    """ Defines a trait whose value must be a Python unicode string and which
        supports coercions of non-unicode values to unicode using a C-level
        fast validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 12, unicode )

#-------------------------------------------------------------------------------
#  'BaseCBool' and 'CBool' traits:
#-------------------------------------------------------------------------------

class BaseCBool ( BaseBool ):
    """ Defines a trait whose value must be a Python boolean and which supports
        coercions of non-boolean values to boolean.
    """
    
    # The function to use for evaluating strings to this type:
    evaluate = bool

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        
            Note: The 'fast validator' version performs this check in C.
        """
        try:
            return bool( value )
        except:
            self.error( object, name, value )

            
class CBool ( BaseCBool ):
    """ Defines a trait whose value must be a Python boolean and which supports
        coercions of non-boolean values to boolean using a C-level fast
        validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 12, bool )

#-------------------------------------------------------------------------------
#  'String' trait:  
#-------------------------------------------------------------------------------

class String ( TraitType ):                                      
    """ Defines a trait whose value must be a Python string whose length is
        optionally in a specified range, and which optionally matches a 
        specified regular expression.
    """
                                      
    def __init__ ( self, value = '', minlen = 0, maxlen = sys.maxint, 
                   regex = '', **metadata ):
        """ Creates a String trait.

        Parameters
        ----------
        value : string
            The default value for the string
        minlen : integer
            The minimum length allowed for the string
        maxlen : integer
            The maximum length allowed for the string
        regex : string
            A Python regular expression that the string must match

        """
        super( String, self ).__init__( value, **metadata )
        self.minlen = max( 0, minlen )
        self.maxlen = max( self.minlen, maxlen )
        self.regex  = regex
        self._init()

    def _init ( self ):
        """ Completes initialization of the trait at construction or unpickling
            time.
        """
        self._validate = 'validate_all'
        if self.regex != '':
            self.match = re.compile( self.regex ).match
            if (self.minlen == 0) and (self.maxlen == sys.maxint):
                self._validate = 'validate_regex'
        elif (self.minlen == 0) and (self.maxlen == sys.maxint):
            self._validate = 'validate_str'
        else:
            self._validate = 'validate_len'
            
    def validate ( self, object, name, value ):
        """ Validates that the value is a valid string.
        """
        return getattr( self, self._validate )( object, name, value )

    def validate_all ( self, object, name, value ):
        """ Validates that the value is a valid string in the specified length 
            range which matches the specified regular expression.
        """
        try:
            value = strx( value )
            if ((self.minlen <= len( value ) <= self.maxlen) and
                (self.match( value ) is not None)):
                return value
        except:
            pass
            
        self.error( object, name, self.repr( value ) )

    def validate_str ( self, object, name, value ):
        """ Validates that the value is a valid string.
        """
        try:
            return strx( value )
        except:
            pass
            
        self.error( object, name, self.repr( value ) )

    def validate_len ( self, object, name, value ):
        """ Validates that the value is a valid string in the specified length 
            range.
        """
        try:
            value = strx( value )
            if self.minlen <= len( value ) <= self.maxlen:
                return value
        except:
            pass
            
        self.error( object, name, self.repr( value ) )

    def validate_regex ( self, object, name, value ):
        """ Validates that the value is a valid string which matches the 
            specified regular expression.
        """
        try:
            value = strx( value )
            if self.match( value ) is not None:
                return value
        except:
            pass
            
        self.error( object, name, self.repr( value ) )

    def info ( self ):
        """ Returns a description of the trait.
        """
        msg = ''
        if (self.minlen != 0) and (self.maxlen != sys.maxint):
            msg = ' between %d and %d characters long' % (
                  self.minlen, self.maxlen )
        elif self.maxlen != sys.maxint:
            msg = ' <= %d characters long' % self.maxlen
        elif self.minlen != 0:
            msg = ' >= %d characters long' % self.minlen
        if self.regex != '':
            if msg != '':
                msg += ' and'
            msg += (" matching the pattern '%s'" % self.regex)
        return 'a string' + msg

    def __getstate__ ( self ):
        """ Returns the current state of the trait. 
        """
        result = self.__dict__.copy()
        for name in [ 'validate', 'match' ]:
            if name in result:
                del result[ name ]
                
        return result

    def __setstate__ ( self, state ):
        """ Sets the current state of the trait.
        """
        self.__dict__.update( state )
        self._init()
        
#-------------------------------------------------------------------------------
#  'Regex' trait:
#-------------------------------------------------------------------------------

class Regex ( String ):
    """ Defines a trait whose value is a Python string that matches a specified
        regular expression.
    """
    
    def __init__ ( self, value = '', regex = '.*', **metadata ):
        """ Creates a Regex trait.
    
        Parameters
        ----------
        value : string
            The default value of the trait
        regex : string
            The regular expression that the trait value must match.
    
        Default Value
        -------------
        *value* or ''
        """
        super( Regex, self ).__init__( value = value, regex = regex,
                                       **metadata )
        
#-------------------------------------------------------------------------------
#  'Code' trait:
#-------------------------------------------------------------------------------

class Code ( String ):
    """ Defines a trait whose value is a Python string that represents source
        code in some language.
    """
    
    metadata = { 'editor': code_editor }

#-------------------------------------------------------------------------------
#  'HTML' trait:  
#-------------------------------------------------------------------------------
                
class HTML ( String ):
    """ Defines a trait whose value must be a string that is interpreted as
    being HTML. By default the value is parsed and displayed as HTML in
    TraitsUI views. The validation of the value does not enforce HTML syntax.
    """
    
    metadata = { 'editor': html_editor }

#-------------------------------------------------------------------------------
#  'Password' trait:  
#-------------------------------------------------------------------------------
                
class Password ( String ):
    """ Defines a trait whose value must be a string, optionally of constrained
    length or matching a regular expression.

    The trait is indentical to a String trait except that by default it uses a 
    PasswordEditor in TraitsUI views, which obscures text entered by the user.
    """
    
    metadata = { 'editor': password_editor }

#-------------------------------------------------------------------------------
#  'Expression' class:
#-------------------------------------------------------------------------------

class Expression ( TraitType ):
    """ Defines a trait whose value must be a valid Python expression. The 
        compiled form of a valid expression is stored as the mapped value of 
        the trait.
    """
    
    # Define the default value for the trait:
    default_value = '0'
    
    # A description of the type of value this trait accepts:
    info_text = 'a valid Python expression'

    # Indicate that this is a mapped trait:    
    is_mapped = True

    def validate ( self, object, name, value ):
        """ Validates that a specified value is valid for this trait.
        """
        try:
            compile( value, '<string>', 'eval' )
            return value
        except:
            self.error( object, name, value )

    def post_setattr ( self, object, name, value ):
        """ Performs additional post-assignment processing.
        """
        object.__dict__[ name + '_' ] = compile( value, '<string>', 'eval' )

#-------------------------------------------------------------------------------
#  'PythonValue' trait:
#-------------------------------------------------------------------------------

class PythonValue ( Any ):
    """ Defines a trait whose value can be of any type, and whose default 
    editor is a Python shell.
    """
    
    metadata = { 'editor': shell_editor }

#-------------------------------------------------------------------------------
#  'BaseFile' and 'File' traits:
#-------------------------------------------------------------------------------

class BaseFile ( BaseStr ):
    """ Defines a trait whose value must be the name of a file.
    """
    
    # A description of the type of value this trait accepts:
    info_text = 'a file name'
    
    def __init__ ( self, value = '', filter = None, auto_set = False,
                   **metadata ):
        """ Creates a File trait.

        Parameters
        ----------
        value : string
            The default value for the trait
        filter : string
            A wildcard string to filter filenames in the file dialog box used by
            the attribute trait editor.
        auto_set : boolean
            Indicates whether the file editor updates the trait value after
            every key stroke.
            
        Default Value
        -------------
        *value* or ''
        """
        from enthought.traits.ui.editors import FileEditor
        
        metadata.setdefault( 'editor', FileEditor( filter   = filter or [],
                                                   auto_set = auto_set ) )
        super( BaseFile, self ).__init__( value, **metadata )

        
class File ( BaseFile ):
    """ Defines a trait whose value must be the name of a file using a C-level
        fast validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 11, basestring )
        
#-------------------------------------------------------------------------------
#  'BaseDirectory' and 'Directory' traits:
#-------------------------------------------------------------------------------

class BaseDirectory ( BaseStr ):
    """ Defines a trait whose value must be the name of a directory.
    """
    
    # A description of the type of value this trait accepts:
    info_text = 'a directory name'
                                                        
    def __init__ ( self, value = '', auto_set = False, **metadata ):
        """ Creates a Directory trait.

        Parameters
        ----------
        value : string
            The default value for the trait
        auto_set : boolean
            Indicates whether the directory editor updates the trait value 
            after every key stroke.
        
        Default Value
        -------------
        *value* or ''
        """
        from enthought.traits.ui.editors import DirectoryEditor
        
        metadata.setdefault( 'editor', DirectoryEditor( auto_set = auto_set ) )
        super( BaseDirectory, self ).__init__( value, **metadata )

        
class Directory ( BaseDirectory ):
    """ Defines a trait whose value must be the name of a directory using a 
        C-level fast validator.
    """
    
    # Define the C-level fast validator to use:
    fast_validate = ( 11, basestring )
   
#-------------------------------------------------------------------------------
#  'BaseRange' and 'Range' traits:  
#-------------------------------------------------------------------------------
                    
class BaseRange ( TraitType ):
    """ Defines a trait whose numeric value must be in a specified range.
    """
    
    def __init__ ( self, low = None, high = None, value = None,
                         exclude_low = False, exclude_high = False, 
                         **metadata ):
        """ Creates a Range trait.

        Parameters
        ----------
        low : integer or float
            The low end of the range.
        high : integer or float
            The high end of the range.
        value : integer or float
            The default value of the trait
        exclude_low : Boolean
            Indicates whether the low end of the range is exclusive.
        exclude_high : Boolean
            Indicates whether the high end of the range is exclusive.
      
        The *low*, *high*, and *value* arguments must be of the same type 
        (integer or float).
      
        Default Value
        -------------
        *value*; if *value* is None or omitted, the default value is *low*,
        unless *low* is None or omitted, in which case the default value is
        *high*.
        """
        if value is None:
            if low is not None:
                value = low
            else:
                value = high
                
        super( BaseRange, self ).__init__( value, **metadata )

        vtype = type( high )
        if (low is not None) and (vtype is not float):
            vtype = type( low )
            
        if vtype not in RangeTypes:
            raise TraitError, ("TraitRange can only be use for int, long or "
                               "float values, but a value of type %s was "
                               "specified." % vtype)
                               
        if vtype is float:
            self._validate  = 'float_validate'
            kind            = 4
            self._type_desc = 'a floating point number'
            if low is not None:
                low = float( low )
                
            if high is not None:
                high = float( high )
                
        elif vtype is long:
            self._validate  = 'long_validate'
            self._type_desc = 'a long integer'
            if low is not None:
                low = long( low )
                
            if high is not None:
                high = long( high )
                
        else:
            self._validate  = 'int_validate'
            kind            = 3
            self._type_desc = 'an integer'
            if low is not None:
                low = int( low )
                
            if high is not None:
                high = int( high )
                
        exclude_mask = 0
        if exclude_low:
            exclude_mask |= 1
            
        if exclude_high:
            exclude_mask |= 2
            
        if vtype is not long:
            self.init_fast_validator( kind, low, high, exclude_mask )

        # Assign type-corrected arguments to handler attributes:
        self._low          = low
        self._high         = high
        self._exclude_low  = exclude_low
        self._exclude_high = exclude_high
        
    def init_fast_validator ( self, *args ):
        """ Does nothing for the BaseRange class. Used in the Range class to 
            set up the fast validator.
        """
        pass

    def validate ( self, object, name, value ):
        """ Validate that the value is in the specified range.
        """
        return getattr( self, self._validate )( object, name, value )

    def float_validate ( self, object, name, value ):
        """ Validate that the value is a float value in the specified range.
        """
        try:
            if (isinstance( value, RangeTypes ) and
                ((self._low is None) or
                 (self._exclude_low and (self._low < value)) or
                 ((not self._exclude_low) and (self._low <= value))) and
                ((self._high is None) or
                 (self._exclude_high and (self._high > value)) or
                 ((not self._exclude_high) and (self._high >= value)))):
               return float( value )
        except:
            pass
            
        self.error( object, name, self.repr( value ) )

    def int_validate ( self, object, name, value ):
        """ Validate that the value is an int value in the specified range.
        """
        try:
            if (isinstance( value, int ) and
                ((self._low is None) or
                 (self._exclude_low and (self._low < value)) or
                 ((not self._exclude_low) and (self._low <= value))) and
                ((self._high is None) or
                 (self._exclude_high and (self._high > value)) or
                 ((not self._exclude_high) and (self._high >= value)))):
               return value
        except:
            pass
            
        self.error( object, name, self.repr( value ) )

    def long_validate ( self, object, name, value ):
        """ Validate that the value is a long value in the specified range.
        """
        try:
            if (isinstance( value, long ) and
                ((self._low is None) or
                 (self._exclude_low and (self._low < value)) or
                 ((not self._exclude_low) and (self._low <= value))) and
                ((self._high is None) or
                 (self._exclude_high and (self._high > value)) or
                 ((not self._exclude_high) and (self._high >= value)))):
               return value
        except:
            pass
            
        self.error( object, name, self.repr( value ) )

    def info ( self ):
        """ Returns a description of the trait.
        """
        if self._low is None:
            if self._high is None:
                return self._type_desc
                
            return '%s <%s %s' % (
                   self._type_desc, '='[ self._exclude_high: ], self._high )
                   
        elif self._high is None:
            return  '%s >%s %s' % (
                    self._type_desc, '='[ self._exclude_low: ], self._low )
                    
        return '%s <%s %s <%s %s' % (
               self._low, '='[ self._exclude_low: ], self._type_desc,
               '='[ self._exclude_high: ], self._high )

    def create_editor ( self ):
        """ Returns the default UI editor for the trait.
        """
        auto_set = self.auto_set
        if auto_set is None:
            auto_set = True
            
        from enthought.traits.ui.api import RangeEditor
        
        return RangeEditor( self,
                            mode       = self.mode or 'auto',
                            cols       = self.cols or 3,
                            auto_set   = auto_set,
                            enter_set  = self.enter_set or False,
                            low_label  = self.low  or '',
                            high_label = self.high or '' )

                            
class Range ( BaseRange ):                            
    """ Defines a trait whose numeric value must be in a specified range using
        a C-level fast validator.
    """
    
    def init_fast_validator ( self, *args ):
        """ Set up the C-level fast validator.
        """
        self.fast_validate = args 
        
#-------------------------------------------------------------------------------
#  'BaseEnum' and 'Enum' traits:  
#-------------------------------------------------------------------------------
                   
class BaseEnum ( TraitType ):
    """ Defines a trait whose value must be one of a specified set of values.
    """
    
    def __init__ ( self, *values, **metadata ):
        """ Returns an Enum trait.
    
        Parameters
        ----------
        values : list or tuple
            The enumeration of all legal values for the trait
    
        Default Value
        -------------
        values[0]
        """
        default_value = values[0]
        if (len( values ) == 1) and (type( values[0] ) in SequenceTypes): 
            values        = default_value
            default_value = values[0]
        elif (len( values ) == 2) and isinstance( values[1], SequenceTypes ):
            values = values[1]
            
        self.values = tuple( values )
        self.init_fast_validator( 5, self.values )
            
        super( BaseEnum, self ).__init__( default_value, **metadata )
        
    def init_fast_validator ( self, *args ):
        """ Does nothing for the BaseEnum class. Used in the Enum class to set 
            up the fast validator.
        """
        pass

    def validate ( self, object, name, value ):
        """ Validates that the value is one of the enumerated set of valid 
            values.
        """
        if value in self.values:
            return value
            
        self.error( object, name, self.repr( value ) )

    def info ( self ):
        """ Returns a description of the trait.
        """
        return ' or '.join( [ repr( x ) for x in self.values ] )

    def create_editor ( self ):
        """ Returns the default UI editor for the trait.
        """
        from enthought.traits.ui.api import EnumEditor
        
        return EnumEditor( values   = self,
                           cols     = self.cols or 3,
                           evaluate = self.evaluate,
                           mode     = self.mode or 'radio' )

                           
class Enum ( BaseEnum ):
    """ Defines a trait whose value must be one of a specified set of values
        using a C-level fast validator.
    """
    
    def init_fast_validator ( self, *args ):
        """ Set up the C-level fast validator.
        """
        self.fast_validate = args 

#-------------------------------------------------------------------------------
#  'BaseTuple' and 'Tuple' traits:  
#-------------------------------------------------------------------------------
                    
class BaseTuple ( TraitType ):
    """ Defines a trait whose value must be a tuple of specified trait types.
    """
    
    def __init__ ( self, *traits, **metadata ):
        """ Returns a Tuple trait.

        Parameters
        ----------
        traits : zero or more arguments
            Definition of the default and allowed tuples. If the first item of 
            *traits* is a tuple, it is used as the default value. 
            The remaining argument list is used to form a tuple that constrains
            the  values assigned to the returned trait. The trait's value must 
            be a tuple of the same length as the remaining argument list, whose
            elements must match the types specified by the corresponding items
            of the remaining argument list.
    
        Default Value
        -------------
         1. If no arguments are specified, the default value is ().
         2. If a tuple is specified as the first argument, it is the default
            value.
         3. If a tuple is not specified as the first argument, the default 
            value is a tuple whose length is the length of the argument list, 
            and whose values are the default values for the corresponding trait
            types.
    
        Example for case #2::
    
            mytuple = Tuple(('Fred', 'Betty', 5))
    
        The trait's value must be a 3-element tuple whose first and second 
        elements are strings, and whose third element is an integer. The 
        default value is ('Fred', 'Betty', 5).
    
        Example for case #3::
    
            mytuple = Tuple('Fred', 'Betty', 5)
    
        The trait's value must be a 3-element tuple whose first and second 
        elements are strings, and whose third element is an integer. The 
        default value is ('','',0).
        """
        if len( traits ) == 0:
            self.init_fast_validator( 11, tuple, None, list )
            
            super( BaseTuple, self ).__init__( (), **metadata )
            
            return

        default_value = None
        
        if isinstance( traits[0], tuple ):
            default_value, traits = traits[0], traits[1:]
            if len( traits ) == 0:
                traits = [ Trait( element ) for element in default_value ]
                
        self.traits = tuple( [ trait_from( trait ) for trait in traits ] )
        self.init_fast_validator( 9, self.traits )
                
        if default_value is None:
            default_value = tuple( [ trait.default_value()[1] 
                                     for trait in self.traits ] )
                                     
        super( BaseTuple, self ).__init__( default_value, **metadata )
        
    def init_fast_validator ( self, *args ):
        """ Saves the validation parameters. 
        """
        self.no_type_check = (args[0] == 11) 

    def validate ( self, object, name, value ):
        """ Validates that the value is a valid tuple.
        """
        if self.no_type_check:
            if isinstance( value, tuple ):
                return value
                
            if isinstance( value, list ):
                return tuple( value )
                
            self.error( object, name, value )
            
        try:
            if isinstance( value, list ):
                value = tuple( value )
                
            if isinstance( value, tuple ):
                traits = self.traits
                if len( value ) == len( traits ):
                    values = []
                    for i, trait in enumerate( traits ):
                        values.append( trait.validate( object, name, 
                                                       value[i] ) )
                                                       
                    return tuple( values )
        except:
            pass
            
        self.error( object, name, value )

    def info ( self ):
        """ Returns a description of the trait.
        """
        if self.no_type_check:
            return 'a tuple'
            
        return 'a tuple of the form: (%s)' % (', '.join( [ trait.info() 
                                                   for trait in self.traits ] ))

    def create_editor ( self ):
        """ Returns the default UI editor for the trait.
        """
        from enthought.traits.ui.api import TupleEditor
        
        return TupleEditor( traits = self.traits,
                            labels = self.labels or [],
                            cols   = self.cols or 1 )
                    
class Tuple ( BaseTuple ):
    """ Defines a trait whose value must be a tuple of specified trait types
        using a C-level fast validator.
    """
    
    def init_fast_validator ( self, *args ):
        """ Set up the C-level fast validator.
        """
        super( Tuple, self ).init_fast_validator( *args )
        
        self.fast_validate = args 
        
#-------------------------------------------------------------------------------
#  'List' trait: 
#-------------------------------------------------------------------------------

class List ( TraitType ):
    """ Defines a trait whose value must be a list whose items are of the 
        specified trait type.
    """    

    info_trait         = None
    default_value_type = 5
    _items_event       = None
    
    def __init__ ( self, trait = None, value = None, minlen = 0, 
                   maxlen = sys.maxint, items = True, **metadata ):
        """ Returns a List trait.
    
        Parameters
        ----------
        trait : a trait or value that can be converted to a trait using Trait()
            The type of item that the list contains. If not specified, the list 
            can contain items of any type.
        value :
            Default value for the list
        minlen : integer
            The minimum length of a list that can be assigned to the trait.
        maxlen : integer
            The maximum length of a list that can be assigned to the trait.
    
        The length of the list assigned to the trait must be such that::
    
            minlen <= len(list) <= maxlen
    
        Default Value
        -------------
        *value* or None
        """
        metadata.setdefault( 'copy', 'deep' )
        
        if isinstance( trait, SequenceTypes ):
            trait, value = value, list( trait )
            
        if value is None:
            value = []
            
        self.item_trait = trait_from( trait )
        self.minlen     = max( 0, minlen )
        self.maxlen     = max( minlen, maxlen )
        self.has_items  = items
            
        if self.item_trait.instance_handler == '_instance_changed_handler':
            metadata.setdefault( 'instance_handler', '_list_changed_handler' )
            
        super( List, self ).__init__( value, **metadata )

    def validate ( self, object, name, value ):
        """ Validates that the values is a valid list.
        """
        if (isinstance( value, list ) and
           (self.minlen <= len( value ) <= self.maxlen)):
            if object is None:
                return value
            return TraitListObject( self, object, name, value )
            
        self.error( object, name, value )

    def info ( self ):
        """ Returns a description of the trait.
        """
        if self.minlen == 0:
            if self.maxlen == sys.maxint:
                size = 'items'
            else:
                size = 'at most %d items' % self.maxlen
        else:
            if self.maxlen == sys.maxint:
                size = 'at least %d items' % self.minlen
            else:
                size = 'from %s to %s items' % (
                       self.minlen, self.maxlen )
            
        return 'a list of %s which are %s' % ( size, self.item_trait.info() )

    def create_editor ( self ):
        """ Returns the default UI editor for the trait.
        """
        handler = self.item_trait.handler
        if isinstance( handler, TraitInstance ) and (self.mode != 'list'):
            from enthought.traits.api import HasTraits
            
            if issubclass( handler.aClass, HasTraits ):
                try:
                    object = handler.aClass()
                    from enthought.traits.ui.table_column import ObjectColumn
                    from enthought.traits.ui.table_filter import \
                         EvalFilterTemplate, RuleFilterTemplate, \
                         MenuFilterTemplate, EvalTableFilter
                    from enthought.traits.ui.api import TableEditor
                    
                    return TableEditor(
                            columns = [ ObjectColumn( name = name )
                                        for name in object.editable_traits() ],
                            filters     = [ RuleFilterTemplate,
                                            MenuFilterTemplate,
                                            EvalFilterTemplate ],
                            edit_view   = '',
                            orientation = 'vertical',
                            search      = EvalTableFilter(),
                            deletable   = True,
                            row_factory = handler.aClass )
                except:
                    pass

        from enthought.traits.ui.api import ListEditor
        
        return ListEditor( trait_handler = self,
                           rows          = self.rows or 5,
                           use_notebook  = self.use_notebook is True,
                           page_name     = self.page_name or '' )

    def inner_traits ( self ):
        """ Returns the *inner trait* (or traits) for this trait.
        """
        return ( self.item_trait, )
                           
    #-- Private Methods --------------------------------------------------------
    
    def items_event ( self ):
        return items_event()
        
#-------------------------------------------------------------------------------
#  'Dict' trait:  
#-------------------------------------------------------------------------------
          
class Dict ( TraitType ):
    """ Defines a trait whose value must be a dictionary, optionally with
        specified types for keys and values.
    """
    
    info_trait         = None
    default_value_type = 6
    _items_event       = None

    def __init__ ( self, key_trait = None, value_trait = None, value = None,
                   items = True, **metadata ):
        """ Returns a Dict trait.

        Parameters
        ----------
        key_trait : a trait or value that can convert to a trait using Trait()
            The trait type for keys in the dictionary; if not specified, any 
            values can be used as keys.
        value_trait : a trait or value that can convert to a trait using Trait()
            The trait type for values in the dictionary; if not specified, any
            values can be used as dictionary values.
        value : a dictionary
            The default value for the returned trait
        items : Boolean
            Indicates whether the value contains items
    
        Default Value
        -------------
        *value* or {}
        """
        if isinstance( key_trait, dict ):
            key_trait, value_trait, value = value_trait, value, key_trait
            
        if value is None:
            value = {}

        self.key_trait   = trait_from( key_trait )
        self.value_trait = trait_from( value_trait )
        self.has_items   = items
        
        handler = self.value_trait.handler
        if (handler is not None) and handler.has_items:
            handler = handler.clone()
            handler.has_items = False
        self.value_handler = handler
        
        super( Dict, self ).__init__( value, **metadata )

    def validate ( self, object, name, value ):
        """ Validates that the value is a valid dictionary.
        """
        if isinstance( value, dict ):
            if value is None:
                return value
            return TraitDictObject( self, object, name, value )
            
        self.error( object, name, value )

    def info ( self ):
        """ Returns a description of the trait.
        """
        return ('a dictionary with keys which are %s and with values which '
                'are %s') % ( self.key_trait.info(), self.value_trait.info() ) 

    def create_editor ( self ):
        """ Returns the default UI editor for the trait.
        """
        from enthought.traits.ui.api import TextEditor
        
        return TextEditor( evaluate = eval )

    def inner_traits ( self ):
        """ Returns the *inner trait* (or traits) for this trait.
        """
        return ( self.key_trait, self.value_trait )

    #-- Private Methods --------------------------------------------------------
        
    def items_event ( self ):
        cls = self.__class__
        if cls._items_event is None:
            cls._items_event = Event( TraitDictEvent, is_base = False )
            
        return cls._items_event

#-------------------------------------------------------------------------------
#  'BaseInstance' and 'Instance' traits:  
#-------------------------------------------------------------------------------

# Allowed values and mappings for the 'adapt' keyword:
AdaptMap = {
   'no':     -1,
   'yes':     0,
   'default': 1
}
                
class BaseInstance ( TraitType ):
    """ Defines a trait whose value must be an instance of a specified class,
        or one of its subclasses.
    """

    def __init__ ( self, klass = None, factory = None, args = None, kw = None, 
                   allow_none = True, adapt = 'yes', module = None,
                   **metadata ):
        """ Returns an Instance trait.
    
        Parameters
        ----------
        klass : class or instance
            The object that forms the basis for the trait; if it is an 
            instance, then trait values must be instances of the same class or 
            a subclass. This object is not the default value, even if it is an 
            instance.
        factory : callable
            A callable, typically a class, that when called with *args* and 
            *kw*, returns the default value for the trait. If not specified, 
            or *None*, *klass* is used as the factory.
        args : tuple
            Positional arguments for generating the default value.
        kw : dictionary
            Keyword arguments for generating the default value.
        allow_none : boolean
            Indicates whether None is allowed as a value.
        adapt : string
            A string specifying how adaptation should be applied. The possible
            values are:
                - 'no': Adaptation is not allowed.
                - 'yes': Adaptation is allowed. If adaptation fails, an 
                    exception should be raised.
                - 'default': Adapation is allowed. If adaptation fails, the 
                    default value for the trait should be used.
    
        Default Value
        -------------
        **None** if *klass* is an instance or if it is a class and *args* and 
        *kw* are not specified. Otherwise, the default value is the instance 
        obtained by calling ``klass(*args, **kw)``. Note that the constructor 
        call is performed each time a default value is assigned, so each 
        default value assigned is a unique instance.
        """
        if klass is None:
            raise TraitError( "An Instance trait must have a class specified." )
            
        metadata.setdefault( 'copy', 'deep' )
        metadata.setdefault( 'instance_handler', '_instance_changed_handler' )
        
        if adapt not in AdaptMap:
            raise TraitError( "'adapt' must be 'yes', 'no' or 'default'." )
                       
        if (args is None) and isinstance( factory, tuple ):
            args, factory = factory, klass
        elif (kw is None) and isinstance( factory, dict ):
            kw, factory = factory, klass
        elif ((args is not None) or (kw is not None)) and (factory is None):
            factory = klass
            
        self._allow_none = allow_none
        self.adapt       = AdaptMap[ adapt ]
        self.module      = module or get_module_name()
        
        if isinstance( klass, basestring ):
            self.klass = klass
        else:
            if not isinstance( klass, ClassTypes ):
                klass = klass.__class__
            self.klass = klass
            self.init_fast_validate()
        
        value = factory
        if factory is not None:
            if args is None:
                args = ()
                
            if kw is None:
                if isinstance( args, dict ):
                    kw   = args
                    args = ()
                else:
                    kw = {}
            elif not isinstance( kw, dict ):
                raise TraitError( "The 'kw' argument must be a dictionary." )
                
            if ((not callable( factory )) and 
                (not isinstance( factory, basestring ))):
                if (len( args ) > 0) or (len( kw ) > 0):
                    raise TraitError( "'factory' must be callable" )
            else:
                value = _InstanceArgs( factory, args, kw )
           
        self.default_value = value
        
        super( BaseInstance, self ).__init__( value, **metadata )

    def validate ( self, object, name, value ):
        """ Validates that the value is a valid object instance.
        """
        if value is None:
            if self._allow_none:
                return value
                
            self.validate_failed( object, name, value )
                
        if isinstance( self.klass, basestring ):
            self.resolve_class( object, name, value )
            
        if self.adapt < 0:
            if isinstance( value, self.klass ):
                return value
                
        elif self.adapt == 0:
            try:
                return adapt( value, self.klass )
            except:
                pass
        else:
            result = adapt( value, self.klass, None )
            if result is None:
                result = self.default_value
                if isinstance( result, _InstanceArgs ):
                    result = result[0]( *result[1], **result[2] )
                    
            return result
            
        self.validate_failed( object, name, value )

    def post_setattr ( self, object, name, value ):
        """ Performs additional post-assignment processing.
        """
        # Save the original, unadapted value in the mapped trait:
        object.__dict__[ name + '_' ] = value

    def info ( self ):
        """ Returns a description of the trait.
        """
        klass = self.klass
        if type( klass ) is not str:
            klass = klass.__name__
            
        if self.adapt < 0:
            result = class_of( klass )
        else:
            result = ('an implementor of, or can be adapted to implement, %s' % 
                      klass)
                      
        if self._allow_none:
            return result + ' or None'
            
        return result
        
    def get_default_value ( self ):
        """ Returns a tuple of the form: ( default_value_type, default_value )
            which describes the default value for this trait.
        """
        dv  = self.default_value
        dvt = self.default_value_type
        if dvt < 0:
            if not isinstance( dv, _InstanceArgs ):
                return super( BaseInstance, self ).get_default_value()
            self.default_value_type = dvt = 7
            dv = ( self.create_default_value, dv.args, dv.kw )
        
        return ( dvt, dv )

    def create_editor ( self ):
        """ Returns the default traits UI editor for this type of trait.
        """
        from enthought.traits.ui.api import InstanceEditor
        
        return InstanceEditor( label = self.label or '',
                               view  = self.view  or '',
                               kind  = self.kind  or 'live' )
        
    #-- Private Methods --------------------------------------------------------

    def as_ctrait ( self ):
        """ Returns a CTrait corresponding to the trait defined by this class.
        """
        ctrait = super( BaseInstance, self ).as_ctrait()
        
        # Tell the C code that the 'post_setattr' method wants the original,
        # unadapted value passed to 'setattr':
        ctrait.original_value( True )
        
        return ctrait 
     
    def validate_class ( self, klass ):
        return klass

    def create_default_value ( self, *args, **kw ):
        klass = args[0]
        if isinstance( klass, basestring ):
            klass = self.validate_class( self.find_class( klass ) )
            if klass is None:
                raise TraitError, 'Unable to locate class: ' + args[0]
                
        return klass( *args[1:], **kw )

    # fixme: Do we still need this method using the new style?...
    def allow_none ( self ):
        self._allow_none = True
        self.init_fast_validate()

    def init_fast_validate ( self ):
        """ Does nothing for the BaseInstance' class. Used by the 'Instance'
            class to set up the C-level fast validator.
        """
        pass

    def resolve_class ( self, object, name, value ):
        klass = self.validate_class( self.find_class( self.klass ) )
        if klass is None:
            self.validate_failed( object, name, value )
        self.klass = klass

        # fixme: The following is quite ugly, because it wants to try and fix
        # the trait referencing this handler to use the 'fast path' now that the
        # actual class has been resolved. The problem is finding the trait,
        # especially in the case of List(Instance('foo')), where the
        # object.base_trait(...) value is the List trait, not the Instance
        # trait, so we need to check for this and pull out the List
        # 'item_trait'. Obviously this does not extend well to other traits
        # containing nested trait references (Dict?)...
        self.init_fast_validate()
        trait   = object.base_trait( name )
        handler = trait.handler
        if handler is not self:
            item_trait = getattr( handler, 'item_trait', None )
            if item_trait is not None:
                trait = item_trait
            
        if self.fast_validate is not None:
            trait.set_validate( self.fast_validate )

    def find_class ( self, klass ):
        module = self.module
        col    = klass.rfind( '.' )
        if col >= 0:
            module = klass[ : col ]
            klass = klass[ col + 1: ]
            
        theClass = getattr( sys.modules.get( module ), klass, None )
        if (theClass is None) and (col >= 0):
            try:
                mod = __import__( module )
                for component in module.split( '.' )[1:]:
                    mod = getattr( mod, component )
                theClass = getattr( mod, klass, None )
            except:
                pass
                
        return theClass

    def validate_failed ( self, object, name, value ):
        kind = type( value )
        if kind is InstanceType:
            msg = 'class %s' % value.__class__.__name__
        else:
            msg = '%s (i.e. %s)' % ( str( kind )[1:-1], repr( value ) )
            
        self.error( object, name, msg )
                
class Instance ( BaseInstance ):
    """ Defines a trait whose value must be an instance of a specified class,
        or one of its subclasses using a C-level fast validator.
    """

    def init_fast_validate ( self ):
        """ Sets up the C-level fast validator.
        """
        if self.adapt < 0:
            fast_validate = [ 1, self.klass ]
            if self._allow_none:
                fast_validate = [ 1, None, self.klass ]
                
            if self.klass in TypeTypes:
                fast_validate[0] = 0
                
            self.fast_validate = tuple( fast_validate )
        else:
            self.fast_validate = ( 19, self.klass, self.adapt, 
                                   self._allow_none )

    
if python_version >= 2.5:
    
    import uuid 
    
    #---------------------------------------------------------------------------
    #  'UUID' trait:  
    #---------------------------------------------------------------------------
                       
    class UUID ( TraitType ):
        """ Defines a trait whose value is a globally unique UUID (type 4).
        """
    
        # A description of the type of value this trait accepts:
        info_text = 'a read-only UUID'
        
        def __init__ ( self, **metadata ):
            """ Returns a UUID trait.
            """
            super( UUID, self ).__init__( None, **metadata )
    
        def validate ( self, object, name, value ):
            """ Raises an error, since no values can be assigned to the trait.
            """
            raise TraitError( "The '%s' trait of %s instance is a read-only "
                              "UUID." % ( name, class_of( object ) ) )
            
        def get_default_value ( self ):
            return ( 7, ( self._create_uuid, (), None ) )
             
        #-- Private Methods ---------------------------------------------------
         
        def _create_uuid ( self ):
            return uuid.uuid4()         

#-------------------------------------------------------------------------------
#  'WeakRef' trait:
#-------------------------------------------------------------------------------

class WeakRef ( Instance ):
    """ Returns a trait whose value must be an instance of the same type
    (or a subclass) of the specified *klass*, which can be a class or an
    instance. Note that the trait only maintains a weak reference to the
    assigned value.
    """

    def __init__ ( self, klass = 'enthought.traits.HasTraits', 
                         allow_none = False, adapt = 'yes', **metadata ):
        """ Returns a WeakRef trait.
        
        Only a weak reference is maintained to any object assigned to a WeakRef
        trait. If no other references exist to the assigned value, the value 
        may be garbage collected, in which case the value of the trait becomes 
        None. In all other cases, the value returned by the trait is the 
        original object.
    
        Parameters
        ----------
        klass : class or instance
            The object that forms the basis for the trait. If *klass* is 
            omitted, then values must be an instance of HasTraits.
        allow_none : boolean
            Indicates whether None can be assigned
    
        Default Value
        -------------
        **None** (even if allow_none==False)
        """
    
        metadata.setdefault( 'copy', 'ref' )
        
        super( WeakRef, self ).__init__( klass, allow_none = allow_none,
                         adapt = adapt, module = get_module_name(), **metadata )

    def get ( self, object, name ):
        value = getattr( object, name + '_', None )
        if value is not None:
            return value.value()
            
        return None

    def set ( self, object, name, value ):
        if value is not None:
            value = HandleWeakRef( object, name, value )
            
        object.__dict__[ name + '_' ] = value

    def resolve_class ( self, object, name, value ):
        # fixme: We have to override this method to prevent the 'fast validate'
        # from being set up, since the trait using this is a 'property' style
        # trait which is not currently compatible with the 'fast_validate'
        # style (causes internal Python SystemError messages).
        klass = self.find_class( self.klass )
        if klass is None:
            self.validate_failed( object, name, value )
            
        self.klass = klass
     
#-- Private Class --------------------------------------------------------------

class HandleWeakRef ( object ):
    
    def __init__ ( self, object, name, value ):
        self.object = ref( object )
        self.name   = name
        self.value  = ref( value, self._value_freed )
        
    def _value_freed ( self, ref ):
        object = self.object()
        if object is not None:
            object.trait_property_changed( self.name, Undefined, None )

#-------------------------------------------------------------------------------
#  'RGBColor' trait:
#-------------------------------------------------------------------------------

class RGBColor ( TraitType ):
    """ Defines a trait whose value represents an abstract color as a tuple of
        the form: ( red, green, blue ), where *red*, *green* and *blue* are
        floats in the range from 0.0 to 1.0.

        Description
        -----------
        For wxPython, the trait accepts any of the following values:
    
        * A tuple of the form (*r*, *g*, *b*), in which *r*, *g*, and *b* 
          represent red, green, and blue values, respectively, and are floats 
          in the range from 0.0 to 1.0.
        * An integer whose hexadecimal form is 0x*RRGGBB*, where *RR* is the red
          value, *GG* is the green value, and *BB* is the blue value.
        * A string specifying a color name (e.g. "red"). Any of the standard
          SVG color names can be used. The names are not case sensitive.
    
        Default Value
        -------------
        (0.0, 0.0, 0.0) (that is, white).
    """
    # fixme: Finish implementing this...

#-------------------------------------------------------------------------------
#  Create predefined, reusable trait instances:
#-------------------------------------------------------------------------------

# Synonym for Bool; default value is False.
false = Bool

# Boolean values only; default value is True.
true = Bool( True )

# Allows any value to be assigned; no type-checking is performed.
# Default value is Undefined.
undefined = Any( Undefined )

#-- List Traits ----------------------------------------------------------------

# List of integer values; default value is [].
ListInt = List( int )

# List of float values; default value is [].
ListFloat = List( float )

# List of string values; default value is [].
ListStr = List( str )

# List of Unicode string values; default value is [].
ListUnicode = List( unicode )

# List of complex values; default value is [].
ListComplex = List( complex )

# List of Boolean values; default value is [].
ListBool = List( bool )

# List of function values; default value is [].
ListFunction = List( FunctionType )

# List of method values; default value is [].
ListMethod = List( MethodType )

# List of class values; default value is [].
ListClass = List( ClassType )

# List of instance values; default value is [].
ListInstance = List( InstanceType )

# List of container type values; default value is [].
ListThis = List( ThisClass )

#-- Dictionary Traits ----------------------------------------------------------

# Only a dictionary of string:Any values can be assigned; only string keys can
# be inserted. The default value is {}.
DictStrAny = Dict( str, Any )

# Only a dictionary of string:string values can be assigned; only string keys 
# with string values can be inserted. The default value is {}.
DictStrStr = Dict( str, str )

# Only a dictionary of string:integer values can be assigned; only string keys
# with integer values can be inserted. The default value is {}.
DictStrInt = Dict( str, int )

# Only a dictionary of string:long-integer values can be assigned; only string
# keys with long-integer values can be inserted. The default value is {}.
DictStrLong = Dict( str, long )

# Only a dictionary of string:float values can be assigned; only string keys 
# with float values can be inserted. The default value is {}.
DictStrFloat = Dict( str, float )

# Only a dictionary of string:Boolean values can be assigned; only string keys
# with Boolean values can be inserted. The default value is {}.
DictStrBool = Dict( str, bool )

# Only a dictionary of string:list values can be assigned; only string keys 
# with list values can be assigned. The default value is {}.
DictStrList = Dict( str, list )
        
