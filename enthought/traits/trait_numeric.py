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
# Date: 12/13/2004
#------------------------------------------------------------------------------
""" Trait definitions related to the Numeric library.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from trait_base \
    import SequenceTypes

from trait_errors \
    import TraitError
    
from trait_handlers \
    import TraitType
    
from trait_types \
    import Str, Any, Int as TInt, Float as TFloat
    
#-------------------------------------------------------------------------------
#  Deferred imports from numerix:
#-------------------------------------------------------------------------------

ArrayType = None
asarray   = None

#-------------------------------------------------------------------------------
#  Numeric type code mapping:
#-------------------------------------------------------------------------------

_type_codes = None

# Define it as a function, so we can defer imports until it is actually used:
def type_codes ( ):

    from enthought.util import numerix
    
    from enthought.util.numerix \
         import Character, UnsignedInt8, Int, Int0, Int8, Int16, Int32, Float, \
                Float0, Float8, Float16, Float32, Float64, Complex, Complex0, \
                Complex8, Complex16, Complex32, Complex64, PyObject
                    
    try:
        from enthought.util.numerix import Int64
    except:
        Int64 = None
                        
    try:
        from enthought.util.numerix import Int128
    except:
        Int128 = None
                        
    try:
        from enthought.util.numerix import Float128
    except:
        Float128 = None
                        
    try:
        from enthought.util.numerix import Complex128
    except:
        Complex128 = None
    
    global _type_codes
    
    if _type_codes is None:
        _type_codes = { 
            Character:    ( 'character', Str ),
            UnsignedInt8: ( 'unsigned 8 bit int', TInt ), 
            Int:          ( 'int', TInt ),
            Int0:         ( 'int', TInt ),
            Int8:         ( '8 bit int', TInt ),
            Int16:        ( '16 bit int', TInt ),
            Int32:        ( '32 bit int', TInt ),
            Int64:        ( '64 bit int', TInt ),
            Int128:       ( '128 bit int', TInt ),
            Float:        ( 'float', TFloat ),
            Float0:       ( 'float', TFloat ),
            Float8:       ( '8 bit float', TFloat ),
            Float16:      ( '16 bit float', TFloat ),
            Float32:      ( '32 bit float', TFloat ),
            Float64:      ( '64 bit float', TFloat ),
            Float128:     ( '128 bit float', TFloat ),
            Complex:      ( 'complex', Any ),
            Complex0:     ( 'complex', Any ),
            Complex8:     ( '8 bit complex', Any ),
            Complex16:    ( '16 bit complex', Any ),
            Complex32:    ( '32 bit complex', Any ), 
            Complex64:    ( '64 bit complex', Any ), 
            Complex128:   ( '128 bit complex', Any ),
            PyObject:     ( 'object', Any )
        }

        if numerix.which[0] == 'numarray':
            # Numarray types are not strings so we need to add the strings also
            for k, v in numerix.type2charmap.items():
                try:
                    _type_codes[v] = _type_codes[k]
                except KeyError:
                    pass
                    
    return _type_codes                    

#-------------------------------------------------------------------------------
#  'AbstractArray' trait base class:  
#-------------------------------------------------------------------------------
                
class AbstractArray ( TraitType ):
    """ Abstract base class for defining Numeric-based arrays.
    """
    
    def __init__ ( self, typecode = None, shape = None, value = None, 
                         coerce = False, **metadata ):
        """ Returns an AbstractArray trait.
        """
        global ArrayType, asarray
        
        try:
            from enthought.util.numerix import array, asarray, zeros
            
            ArrayType = type( array( [ 1 ] ) )
        except:
            raise TraitError( "Using Array or CArray trait types requires the "
                              "NumPy package to be installed." )
        
        # Mark this as being an 'array' trait:
        metadata[ 'array' ] = True
        
        # Normally use object identity to detect array values changing:
        metadata.setdefault( 'rich_compare', False )
    
        if isinstance( typecode, SequenceTypes ):
            shape, typecode = typecode, shape
    
        if (typecode is not None) and (typecode not in type_codes()):
            raise TraitError, ("typecode must be a valid Numeric typecode or "
                               "None")
    
        if shape is not None:
            if isinstance( shape, SequenceTypes ):
                for item in shape:
                    if ((item is None) or (type( item ) is int) or
                        (isinstance( item, SequenceTypes ) and
                         (len( item ) == 2) and
                         (type( item[0] ) is int) and (item[0] >= 0) and
                         ((item[1] is None) or ((type( item[1] ) is int) and
                           (item[0] <= item[1]))))):
                        continue
                    raise TraitError, "shape should be a list or tuple"
            else:
                raise TraitError, "shape should be a list or tuple"
    
            if (len( shape ) == 2) and (metadata.get( 'editor' ) is None):
                from enthought.traits.ui.api import ArrayEditor
                
                metadata.setdefault( 'editor', ArrayEditor )
    
        if value is None:
            if shape is None:
                value = zeros( ( 0, ), typecode )
            else:
                size = []
                for item in shape:
                    if item is None:
                        item = 1
                    elif type( item ) in SequenceTypes:
                        item = item[0]
                    size.append( item )
                value = zeros( size, typecode )
                
        self.typecode = typecode
        self.shape    = shape
        self.coerce   = coerce
        
        super( AbstractArray, self ).__init__( value, **metadata )
        
    def validate ( self, object, name, value ):
        """ Validates that the value is a valid array.
        """
        try:
            # Make sure the value is an array:
            type_value = type( value )
            if not isinstance( value, ArrayType ):    
                if not isinstance( value, SequenceTypes ):
                    self.error( object, name, value )
                    
                value = asarray( value, self.typecode )
                
            # Make sure the array is of the right type:
            if ((self.typecode is not None) and 
                (numerix.typecode( value ) != self.typecode)):
                if self.coerce:
                    value = value.astype( self.typecode )
                else:
                    value = asarray( value, self.typecode )
                    
            # If no shape requirements, then return the value:
            trait_shape = self.shape
            if trait_shape is None:
                return value
                
            # Else make sure that the value's shape is compatible:
            value_shape = value.shape
            if len( trait_shape ) == len( value_shape ):
                for i, dim in enumerate( value_shape ):
                    item = trait_shape[i]
                    if item is not None:
                        if type( item ) is int:
                            if dim != item:
                                break
                        elif ((dim < item[0]) or 
                              ((item[1] is not None) and (dim > item[1]))):
                            break
                else:
                    return value
        except:
            pass
            
        self.error( object, name, value ) 
        
    def info ( self ):
        """ Returns descriptive information about the trait.
        """
        typecode = shape = ''
        
        if self.shape is not None:
            shape = []
            for item in self.shape:
                if item is None:
                    item = '*'
                elif type( item ) is not int:
                    if item[1] is None:
                        item = '%d..' % item[0]
                    else:
                        item = '%d..%d' % item
                shape.append( item )
            shape = ' with shape %s' % ( tuple( shape ), )
             
        if self.typecode is not None:
            typecode = ' of %s values' % (type_codes()[ self.typecode ][0])
            
        return 'an array%s%s' % ( typecode, shape )

    def get_editor ( self ):
        """ Returns the default UI editor for the trait.
        """
        from enthought.traits.ui.api import TupleEditor
        
        if self.typecode is None:
            traits = TFloat
        else:
            traits = type_codes()[ self.typecode ][1]
            
        return TupleEditor( traits = traits,
                            labels = self.labels or [],
                            cols   = self.cols or 1  )

    #-- Private Methods --------------------------------------------------------
        
    def get_default_value ( self ):
        """ Returns the default value constructor for the type (called from the
            trait factory.
        """
        return ( 7, ( self.copy_default_value, 
                 ( self.validate( None, None, self.default_value ), ), None ) )
                  
    def copy_default_value ( self, value ):
        """ Returns a copy of the default value (called from the C code on 
            first reference to a trait with no current value).
        """
        return value.copy()        

#-------------------------------------------------------------------------------
#  'Array' trait:  
#-------------------------------------------------------------------------------
                
class Array ( AbstractArray ):
    """ Defines a trait whose value must be a Numeric array.
    """
        
    def __init__ ( self, typecode = None, shape = None, value = None, 
                   **metadata ):
        """ Returns an Array trait.
                       
        Parameters
        ----------
        typecode : a Numeric typecode (e.g., Float)
            The type of elements in the array; if omitted, no type-checking is
            performed on assigned values.
        shape : a tuple
            Describes the required shape of any assigned value. Wildcards and 
            ranges are allowed. The value None within the *shape* tuple means 
            that the corresponding dimension is not checked. (For example,
            ``shape=(None,3)`` means that the first dimension can be any size, 
            but the second must be 3.) A two-element tuple within the *shape* 
            tuple means that the dimension must be in the specified range. The
            second element can be None to indicate that there is no upper 
            bound. (For example, ``shape=((3,5),(2,None))`` means that the 
            first dimension must be in the range 3 to 5 (inclusive), and the 
            second dimension must be at least 2.)
        value : Numeric array
            A default value for the array
    
        Default Value
        -------------
        *value* or ``zeros(min(shape))``, where ``min(shape)`` refers to the 
        minimum shape allowed by the array. If *shape* is not specified, the
        minimum shape is (0,).
        
        Description
        -----------
        An Array trait allows only upcasting of assigned values that are 
        already Numeric arrays. It automatically casts tuples and lists of the 
        right shape to the specified *typecode* (just like Numeric's **array**
        does).
        """
        super( Array, self ).__init__( typecode, shape, value, False, 
                                       **metadata )

#-------------------------------------------------------------------------------
#  'CArray' trait:  
#-------------------------------------------------------------------------------
                     
class CArray ( AbstractArray ):
    """ Defines a trait whose value must be a Numeric array, with casting 
        allowed.
    """
    
    def __init__ ( self, typecode = None, shape = None, value = None, 
                   **metadata ):
        """ Returns a CArray trait.
    
        Parameters
        ----------
        typecode : a Numeric typecode (e.g., Float)
            The type of elements in the array
        shape : a tuple
            Describes the required shape of any assigned value. Wildcards and 
            ranges are allowed. The value None within the *shape* tuple means
            that the corresponding dimension is not checked. (For example,
            ``shape=(None,3)`` means that the first dimension can be any size,
            but the second must be 3.) A two-element tuple within the *shape*
            tuple means that the dimension must be in the specified range. The 
            second element can be None to indicate that there is no upper 
            bound. (For example, ``shape=((3,5),(2,None))`` means that the 
            first dimension must be in the range 3 to 5 (inclusive), and the 
            second dimension must be at least 2.)
        value : Numeric array
            A default value for the array
    
        Default Value
        -------------
        *value* or ``zeros(min(shape))``, where ``min(shape)`` refers to the
        minimum shape allowed by the array. If *shape* is not specified, the
        minimum shape is (0,).
    
        Description
        -----------
        The trait returned by CArray() is similar to that returned by Array(),
        except that it allows both upcasting and downcasting of assigned values
        that are already Numeric arrays. It automatically casts tuples and 
        lists of the right shape to the specified *typecode* (just like 
        Numeric's **array** does).
        """
        super( CArray, self ).__init__( typecode, shape, value, True, 
                                        **metadata )
                            
