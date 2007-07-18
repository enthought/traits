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
#  Original Date: 06/21/2002
#
#  Rewritten as a C-based type extension: 06/21/2004
#
#------------------------------------------------------------------------------

"""
Defines the 'core' traits for the Traits package. A trait is a type definition
that can be used for normal Python object attributes, giving the attributes
some additional characteristics:

Initialization:
    Traits have predefined values that do not need to be explicitly
    initialized in the class constructor or elsewhere.
Validation:
    Trait attributes have flexible, type-checked values.
Delegation:
    Trait attributes' values can be delegated to other objects.
Notification:
    Trait attributes can automatically notify interested parties when
    their values change.
Visualization:
    Trait attributes can automatically construct (automatic or
    programmer-defined) user interfaces that allow their values to be
    edited or displayed)

Note: 'trait' is a synonym for 'property', but is used instead of the
word 'property' to differentiate it from the Python language 'property'
feature.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import trait_handlers
import enthought.traits.protocols.interfaces as interfaces

from inspect \
    import stack

from ctraits \
    import cTrait, CTraitMethod

from trait_base \
    import SequenceTypes, Self, Undefined, Missing, TypeTypes, class_of, \
           add_article, enumerate, BooleanType

from trait_errors \
    import TraitError

from trait_handlers \
    import TraitHandler, TraitInstance, TraitList, TraitDict, TraitFunction, \
           TraitCoerceType, TraitCastType, TraitEnum, TraitCompound, TraitMap, \
           TraitString, ThisClass, TraitRange, TraitTuple, TraitCallable, \
           TraitExpression, TraitWeakRef, TraitType, _arg_count, _read_only, \
           _write_only, _undefined_get, _undefined_set

from types \
    import NoneType, IntType, LongType, FloatType, ComplexType, StringType, \
           UnicodeType, ListType, TupleType, DictType, FunctionType, \
           ClassType, ModuleType, MethodType, InstanceType, TypeType

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from 'ctrait' default value types to a string representation:
KindMap = {
   0: 'value',
   1: 'value',
   2: 'self',
   3: 'list',
   4: 'dict',
   5: 'list',
   6: 'dict',
   7: 'factory',
   8: 'method'
}

#-------------------------------------------------------------------------------
#  Editor factory functions:
#-------------------------------------------------------------------------------

PasswordEditor      = None
MultilineTextEditor = None
SourceCodeEditor    = None
HTMLTextEditor      = None
PythonShellEditor   = None

def password_editor ( ):
    """ Factory function that returns an editor for passwords.
    """
    global PasswordEditor

    if PasswordEditor is None:
        from enthought.traits.ui.api import TextEditor
        PasswordEditor = TextEditor( password = True )

    return PasswordEditor

def multi_line_text_editor ( ):
    """ Factory function that returns a text editor for multi-line strings.
    """
    global MultilineTextEditor

    if MultilineTextEditor is None:
        from enthought.traits.ui.api import TextEditor
        MultilineTextEditor = TextEditor( multi_line = True )

    return MultilineTextEditor

def code_editor ( ):
    """ Factory function that returns an editor that treats a multi-line string
    as source code.
    """
    global SourceCodeEditor

    if SourceCodeEditor is None:
        from enthought.traits.ui.api import CodeEditor
        SourceCodeEditor = CodeEditor()

    return SourceCodeEditor

def html_editor ( ):
    """ Factory function for an "editor" that displays a multi-line string as
    interpreted HTML.
    """
    global HTMLTextEditor

    if HTMLTextEditor is None:
        from enthought.traits.ui.api import HTMLEditor
        HTMLTextEditor = HTMLEditor()

    return HTMLTextEditor

def shell_editor ( ):
    """ Factory function that returns a Python shell for editing Python values.
    """
    global PythonShellEditor

    if PythonShellEditor is None:
        from enthought.traits.ui.api import ShellEditor
        PythonShellEditor = ShellEditor()

    return PythonShellEditor

#-------------------------------------------------------------------------------
#  'CTrait' class (extends the underlying cTrait c-based type):
#-------------------------------------------------------------------------------

class CTrait ( cTrait ):
    """ Extends the underlying C-based cTrait type.
    """

    #---------------------------------------------------------------------------
    #  Allows a derivative trait to be defined from this one:
    #---------------------------------------------------------------------------

    def __call__ ( self, *args, **metadata ):
        handler = self.handler
        if isinstance( handler, TraitType ):
            dict = (self.__dict__ or {}).copy()
            dict.update( metadata )

            return handler( *args, **dict )

        metadata.setdefault( 'parent', self )
        return Trait( *(args + ( self, )), **metadata )
        
    #---------------------------------------------------------------------------
    #  (Python) property definitions:
    #---------------------------------------------------------------------------
    
    def __get_default ( self ):
        kind, value = self.default_value()
        if kind in ( 2, 7, 8 ):
            return Undefined
         
        if kind in ( 4, 6 ):
            return value.copy()
         
        if kind in ( 3, 5 ):
            return value[:]
            
        return value
        
    default = property( __get_default )
    
    def __get_default_kind ( self ):
        return KindMap[ self.default_value()[0] ]
        
    default_kind = property( __get_default_kind )
    
    def __get_trait_type ( self ):
        handler = self.handler
        if handler is not None:
            return handler
            
        return Any
        
    trait_type = property( __get_trait_type )
    
    def __get_inner_traits ( self ):
        handler = self.handler
        if handler is not None:
            return handler.inner_traits()
            
        return ()
        
    inner_traits = property( __get_inner_traits )
    
    #---------------------------------------------------------------------------
    #  Returns whether or not this trait is of a specified trait type:
    #---------------------------------------------------------------------------
    
    def is_trait_type ( self, trait_type ):
        """ Returns whether or not this trait is of a specified trait type.
        """
        return isinstance( self.trait_type, trait_type )

    #---------------------------------------------------------------------------
    #  Returns the user interface editor associated with the trait:
    #---------------------------------------------------------------------------

    def get_editor ( self ):
        """ Returns the user interface editor associated with the trait.
        """
        from enthought.traits.ui.api import EditorFactory

        # See if we have an editor:
        editor = self.editor
        if editor is None:

            # Else see if the trait handler has an editor:
            handler = self.handler
            if handler is not None:
                editor = handler.get_editor( self )

            # If not, give up and use a default text editor:
            if editor is None:
                from enthought.traits.ui.api import TextEditor
                editor = TextEditor

        # If the result is not an EditoryFactory:
        if not isinstance( editor, EditorFactory ):
            # Then it should be a factory for creating them:
            args   = ()
            traits = {}
            if type( editor ) in SequenceTypes:
                for item in editor[:]:
                    if type( item ) in SequenceTypes:
                        args = tuple( item )
                    elif isinstance( item, dict ):
                        traits = item
                        if traits.get( 'trait', 0 ) is None:
                            traits = traits.copy()
                            traits[ 'trait' ] = self
                    else:
                        editor = item
            editor = editor( *args, **traits )

        # Cache the result:
        self.editor = editor

        # Return the resulting EditorFactory object:
        return editor

    #---------------------------------------------------------------------------
    #  Returns the help text for a trait:
    #---------------------------------------------------------------------------

    def get_help ( self, full = True ):
        """ Returns the help text for a trait.

        Parameters
        ----------
        full : Boolean
            Indicates whether to return the value of the *help* attribute of
            the trait itself.

        Description
        -----------
        If *full* is False or the trait does not have a **help** string,
        the returned string is constructed from the **desc** attribute on the
        trait and the **info** string on the trait's handler.
        """
        if full:
            help = self.help
            if help is not None:
                return help
        handler = self.handler
        if handler is not None:
            info = 'must be %s.' % handler.info()
        else:
            info = 'may be any value.'
        desc = self.desc
        if self.desc is None:
            return info.capitalize()
        return 'Specifies %s and %s' % ( desc, info )

    #---------------------------------------------------------------------------
    #  Returns a description of the trait:
    #---------------------------------------------------------------------------

    def info ( self ):
        """ Returns a description of the trait.
        """
        handler = self.handler
        if handler is not None:
            return handler.info()

        return 'any value'

    #---------------------------------------------------------------------------
    #  Returns the pickleable form of a CTrait object:
    #---------------------------------------------------------------------------

    def __reduce_ex__ ( self, protocol ):
        return ( __newobj__, ( self.__class__, 0 ), self.__getstate__() )

# Make sure the Python-level version of the trait class is known to all
# interested parties:
import ctraits
ctraits._ctrait( CTrait )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

ConstantTypes    = ( NoneType, IntType, LongType, FloatType, ComplexType,
                     StringType, UnicodeType )

PythonTypes      = ( StringType,   UnicodeType,  IntType,    LongType,
                     FloatType,    ComplexType,  ListType,   TupleType,
                     DictType,     FunctionType, MethodType, ClassType,
                     InstanceType, TypeType,     NoneType )

CallableTypes    = ( FunctionType, MethodType )

TraitTypes       = ( TraitHandler, CTrait )

MutableTypes     = ( list, dict )

DefaultValues = {
    StringType:  '',
    UnicodeType: u'',
    IntType:     0,
    LongType:    0L,
    FloatType:   0.0,
    ComplexType: 0j,
    ListType:    [],
    TupleType:   (),
    DictType:    {},
    BooleanType: False
}

DefaultValueSpecial = [ Missing, Self ]
DefaultValueTypes   = [ ListType, DictType ]

#-------------------------------------------------------------------------------
#  Function used to unpickle new-style objects:
#-------------------------------------------------------------------------------

def __newobj__ ( cls, *args ):
    """ Unpickles new-style objects.
    """
    return cls.__new__( cls, *args )

#-------------------------------------------------------------------------------
#  Returns the type of default value specified:
#-------------------------------------------------------------------------------

def _default_value_type ( default_value ):
    try:
        return DefaultValueSpecial.index( default_value ) + 1
    except:
        try:
            return DefaultValueTypes.index( type( default_value ) ) + 3
        except:
            return 0

#-------------------------------------------------------------------------------
#  'TraitFactory' class:
#-------------------------------------------------------------------------------

class TraitFactory ( object ):
    ### Need a docstring here.

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, maker_function = None ):
        if maker_function is not None:
            self.maker_function = maker_function

    #---------------------------------------------------------------------------
    #  Creates a CTrait instance:
    #---------------------------------------------------------------------------

    def __call__ ( self, *args, **metadata ):
        return self.maker_function( *args, **metadata )

class TraitImportError ( TraitFactory ):
    """ Defines a factory class for deferring import problems until encountering
        code that actually tries to use the unimportable trait.
    """

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, message ):
        self.message = message

    #---------------------------------------------------------------------------
    #  Creates a CTrait instance:
    #---------------------------------------------------------------------------

    def __call__ ( self, *args, **metadata ):
        raise TraitError( self.message )

#-------------------------------------------------------------------------------
#  Returns a trait created from a TraitFactory instance:
#-------------------------------------------------------------------------------

_trait_factory_instances = {}

def trait_factory ( trait ):
    global _trait_factory_instances

    tid = id( trait )
    if tid not in _trait_factory_instances:
        _trait_factory_instances[ tid ] = trait()
    return _trait_factory_instances[ tid ]

#-------------------------------------------------------------------------------
#  Casts a CTrait or TraitFactory to a CTrait but returns None if it is neither:
#-------------------------------------------------------------------------------

def trait_cast ( something ):
    """ Casts a CTrait, TraitFactory or TraitType to a CTrait but returns None
        if it is none of those.
    """
    if isinstance( something, CTrait ):
        return something

    if isinstance( something, TraitFactory ):
        return trait_factory( something )

    if isinstance( something, type ) and issubclass( something, TraitType ):
        return something().as_ctrait()

    if isinstance( something, TraitType ):
        return something.as_ctrait()

    return None

#-------------------------------------------------------------------------------
#  Attempts to cast a value to a trait. Returns either a trait or the original
#  value:
#-------------------------------------------------------------------------------

def try_trait_cast ( something ):
    """ Attempts to cast a value to a trait. Returns either a trait or the
        original value.
    """
    return trait_cast( something ) or something

#-------------------------------------------------------------------------------
#  Returns a trait derived from its input:
#-------------------------------------------------------------------------------

def trait_from ( something ):
    """ Returns a trait derived from its input.
    """
    from trait_types import Any

    if isinstance( something, CTrait ):
        return something

    if something is None:
        something = Any

    if isinstance( something, TraitFactory ):
        return trait_factory( something )

    if isinstance( something, type ) and issubclass( something, TraitType ):
        return something().as_ctrait()

    if isinstance( something, TraitType ):
        return something.as_ctrait()

    return Trait( something )

# Patch the reference to 'trait_from' in 'trait_handlers.py':
trait_handlers.trait_from = trait_from

#--- 'instance' traits ---------------------------------------------------------

class _InstanceArgs ( object ):

    def __init__ ( self, factory, args, kw ):
        self.args = ( factory, ) + args
        self.kw   = kw

#--- 'creates a run-time default value' ----------------------------------------

class Default ( object ):
    """ Generates a value the first time it is accessed.

    A Default object can be used anywhere a default trait value would normally
    be specified, to generate a default value dynamically.
    """
    def __init__ ( self, func = None, args = (), kw = None ):
        self.default_value = ( func, args, kw )

#-------------------------------------------------------------------------------
#  Factory function for creating constant traits:
#-------------------------------------------------------------------------------

def Constant ( value, **metadata ):
    """ Returns a read-only trait whose value is *value*.

    Parameters
    ----------
    value : any type except a list or dictionary
        The default value for the trait

    Default Value
    -------------
    *value*

    Description
    -----------
    Traits of this type are very space efficient (and fast) because *value* is
    not stored in each instance using the trait, but only in the trait object
    itself. The *value* cannot be a list or dictionary, because those types have
    mutable values.
    """
    if type( value ) in MutableTypes:
        raise TraitError, \
              "Cannot define a constant using a mutable list or dictionary"
    metadata[ 'type' ]      = 'constant'
    metadata[ 'transient' ] = True
    return Trait( value, **metadata )

#-------------------------------------------------------------------------------
#  Factory function for creating C-based events:
#-------------------------------------------------------------------------------

def Event ( *value_type, **metadata ):
    """ Returns a trait event whose assigned value must meet the specified criteria.

    Parameters
    ----------
    value_type : any valid arguments for Trait()
        Specifies the criteria for successful assignment to the trait event.

    Default Value
    -------------
    No default value because events do not store values.
    """
    metadata[ 'type' ]      = 'event'
    metadata[ 'transient' ] = True
    result = Trait( *value_type, **metadata )
    if 'instance_handler' in result.__dict__:
        del result.instance_handler
    return result

Event = TraitFactory( Event )

def Button ( label = '', image = None, style = 'button',
             orientation = 'vertical', width_padding = 7, height_padding = 5,
             **metadata ):
    """ Returns a trait event whose editor is a button.

    Parameters
    ----------
    label : string
        The label for the button
    image : enthought.pyface.ImageResource
        An image to display on the button
    style : one of: 'button', 'radio', 'toolbar', 'checkbox'
        The style of button to display
    orientation : one of: 'horizontal', 'vertical'
        The orientation of the label relative to the image
    width_padding : integer between 0 and 31
        Extra padding (in pixels) added to the left and right sides of the button
    height_padding : integer between 0 and 31
        Extra padding (in pixels) added to the top and bottom of the button

    Default Value
    -------------
    No default value because events do not store values.
    """

    from enthought.traits.ui.api import ButtonEditor

    return Event( editor = ButtonEditor(
                               label          = label,
                               image          = image,
                               style          = style,
                               orientation    = orientation,
                               width_padding  = width_padding,
                               height_padding = height_padding,
                               **metadata ) )

Button = TraitFactory( Button )

def ToolbarButton ( label = '', image = None, style = 'toolbar',
                    orientation = 'vertical', width_padding = 2,
                    height_padding = 2, **metadata ):
    """ Returns a trait even whose editor is a toolbar button.

    Parameters
    ----------
    label : string
        The label for the button
    image : enthought.pyface.ImageResource
        An image to display on the button
    style : one of: 'button', 'radio', 'toolbar', 'checkbox'
        The style of button to display
    orientation : one of: 'horizontal', 'vertical'
        The orientation of the label relative to the image
    width_padding : integer between 0 and 31
        Extra padding (in pixels) added to the left and right sides of the button
    height_padding : integer between 0 and 31
        Extra padding (in pixels) added to the top and bottom of the button

    Default Value
    -------------
    No default value because events do not store values.

    """
    return Button( label, image, style, orientation, width_padding,
                   height_padding, **metadata )

ToolbarButton = TraitFactory( ToolbarButton )

def UIDebugger ( **metadata ):
    ### JMS: Surely there's more to say about this...
    """ Returns a trait event whose editor is a button that opens debugger window.

    Default Value
    -------------
    No default value because events do not store values.
    """
    from enthought.traits.ui.wx.ui_debug_editor import ToolkitEditorFactory

    return Event( editor = ToolkitEditorFactory(), **metadata )

UIDebugger = TraitFactory( UIDebugger )

#  Handle circular module dependencies:
trait_handlers.Event = Event

#-------------------------------------------------------------------------------
#  Factory function for creating C-based traits:
#-------------------------------------------------------------------------------

def Trait ( *value_type, **metadata ):
    """ Creates a trait definition.

    Parameters
    ----------
    This function accepts a variety of forms of parameter lists:

    +-------------------+---------------+-------------------------------------+
    | Format            | Example       | Description                         |
    +===================+===============+=====================================+
    | Trait(*default*)  | Trait(150.0)  | The type of the trait is inferred   |
    |                   |               | from the type of the default value, |
    |                   |               | which must be in *ConstantTypes*.   |
    +-------------------+---------------+-------------------------------------+
    | Trait(*default*,  | Trait(None,   | The trait accepts any of the        |
    | *other1*,         | 0, 1, 2,      | enumerated values, with the first   |
    | *other2*, ...)    | 'many')       | value being the default value. The  |
    |                   |               | values must be of types in          |
    |                   |               | *ConstantTypes*, but they need not  |
    |                   |               | be of the same type. The *default*  |
    |                   |               | value is not valid for assignment   |
    |                   |               | unless it is repeated later in the  |
    |                   |               | list.                               |
    +-------------------+---------------+-------------------------------------+
    | Trait([*default*, | Trait([None,  | Similar to the previous format, but |
    | *other1*,         | 0, 1, 2,      | takes an explicit list or a list    |
    | *other2*, ...])   | 'many'])      | variable.                           |
    +-------------------+---------------+-------------------------------------+
    | Trait(*type*)     | Trait(Int)    | The *type* parameter must be a name |
    |                   |               | of a Python type (see               |
    |                   |               | *PythonTypes*). Assigned values     |
    |                   |               | must be of exactly the specified    |
    |                   |               | type; no casting or coercion is     |
    |                   |               | performed. The default value is the |
    |                   |               | appropriate form of zero, False,    |
    |                   |               | or emtpy string, set or sequence.   |
    +-------------------+---------------+-------------------------------------+
    | Trait(*class*)    |::             | Values must be instances of *class* |
    |                   |               | or of a subclass of *class*. The    |
    |                   | class MyClass:| default value is None, but None     |
    |                   |    pass       | cannot be assigned as a value.      |
    |                   | foo = Trait(  |                                     |
    |                   | MyClass)      |                                     |
    +-------------------+---------------+-------------------------------------+
    | Trait(None,       |::             | Similar to the previous format, but |
    | *class*)          |               | None *can* be assigned as a value.  |
    |                   | class MyClass:|                                     |
    |                   |   pass        |                                     |
    |                   | foo = Trait(  |                                     |
    |                   | None, MyClass)|                                     |
    +-------------------+---------------+-------------------------------------+
    | Trait(*instance*) |::             | Values must be instances of the     |
    |                   |               | same class as *instance*, or of a   |
    |                   | class MyClass:| subclass of that class. The         |
    |                   |    pass       | specified instance is the default   |
    |                   | i = MyClass() | value.                              |
    |                   | foo =         |                                     |
    |                   |   Trait(i)    |                                     |
    +-------------------+---------------+-------------------------------------+
    | Trait(*handler*)  | Trait(        | Assignment to this trait is         |
    |                   | TraitEnum     | validated by an object derived from |
    |                   |               | **enthought.traits.TraitHandler**.  |
    +-------------------+---------------+-------------------------------------+
    | Trait(*default*,  | Trait(0.0, 0.0| This is the most general form of    |
    | { *type* |        | 'stuff',      | the function. The notation:         |
    | *constant* |      | TupleType)    | ``{...|...|...}+`` means a list of  |
    | *dict* | *class* ||               | one or more of any of the items     |
    | *function* |      |               | listed between the braces. Thus, the|
    | *handler* |       |               | most general form of the function   |
    | *trait* }+ )      |               | consists of a default value,        |
    |                   |               | followed by one or more of several  |
    |                   |               | possible items. A trait defined by  |
    |                   |               | multiple items is called a          |
    |                   |               | "compound" trait.                   |
    +-------------------+---------------+-------------------------------------+

    All forms of the Trait function accept both predefined and arbitrary
    keyword arguments. The value of each keyword argument becomes bound to the
    resulting trait object as the value of an attribute having the same name
    as the keyword. This feature lets you associate metadata with a trait.

    The following predefined keywords are accepted:

    desc : string
        Describes the intended meaning of the trait. It is used in
        exception messages and fly-over help in user interfaces.
    label : string
        Provides a human-readable name for the trait. It is used to label user
        interface editors for traits.
    editor : instance of a subclass of enthought.traits.api.Editor
        Object to use when creating a user interface editor for the trait. See
        the "Traits UI User Guide" for more information on trait editors.
    rich_compare : Boolean
        Indicates whether the basis for considering a trait attribute value to
        have changed is a "rich" comparison (True, the default), or simple
        object identity (False). This attribute can be useful in cases
        where a detailed comparison of two objects is very expensive, or where
        you do not care whether the details of an object change, as long as the
        same object is used.

    """
    return _TraitMaker( *value_type, **metadata ).as_ctrait()

#  Handle circular module dependencies:
trait_handlers.Trait = Trait

#-------------------------------------------------------------------------------
#  '_TraitMaker' class:
#-------------------------------------------------------------------------------

class _TraitMaker ( object ):

    # Ctrait type map for special trait types:
    type_map = {
       'event':    2,
       'constant': 7
    }

    #---------------------------------------------------------------------------
    #  Initialize the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, *value_type, **metadata ):
        metadata.setdefault( 'type', 'trait' )
        self.define( *value_type, **metadata )

    #---------------------------------------------------------------------------
    #  Define the trait:
    #---------------------------------------------------------------------------

    def define ( self, *value_type, **metadata ):
        default_value_type = -1
        default_value      = handler = clone = None
        if len( value_type ) > 0:
            default_value = value_type[0]
            value_type    = value_type[1:]
            if ((len( value_type ) == 0) and
                (type( default_value ) in SequenceTypes)):
                default_value, value_type = default_value[0], default_value
            if len( value_type ) == 0:
                default_value = try_trait_cast( default_value )
                if default_value in PythonTypes:
                    handler       = TraitCoerceType( default_value )
                    default_value = DefaultValues.get( default_value )
                elif isinstance( default_value, CTrait ):
                    clone = default_value
                    default_value_type, default_value = clone.default_value()
                    metadata[ 'type' ] = clone.type
                elif isinstance( default_value, TraitHandler ):
                    handler       = default_value
                    default_value = None
                elif default_value is ThisClass:
                    handler       = ThisClass()
                    default_value = None
                else:
                    typeValue = type( default_value )
                    if isinstance(default_value, basestring):
                        string_options = self.extract( metadata, 'min_len',
                                                       'max_len', 'regex' )
                        if len( string_options ) == 0:
                            handler = TraitCastType( typeValue )
                        else:
                            handler = TraitString( **string_options )
                    elif typeValue in TypeTypes:
                        handler = TraitCastType( typeValue )
                    else:
                        metadata.setdefault( 'instance_handler',
                                             '_instance_changed_handler' )
                        handler = TraitInstance( default_value )
                        if default_value is handler.aClass:
                            default_value = DefaultValues.get( default_value )
            else:
                enum  = []
                other = []
                map   = {}
                self.do_list( value_type, enum, map, other )
                if (((len( enum )  == 1) and (enum[0] is None)) and
                    ((len( other ) == 1) and
                     isinstance( other[0], TraitInstance ))):
                    enum = []
                    other[0].allow_none()
                    metadata.setdefault( 'instance_handler',
                                         '_instance_changed_handler' )
                if len( enum ) > 0:
                    if (((len( map ) + len( other )) == 0) and
                        (default_value not in enum)):
                        enum.insert( 0, default_value )
                    other.append( TraitEnum( enum ) )
                if len( map ) > 0:
                    other.append( TraitMap( map ) )
                if len( other ) == 0:
                    handler = TraitHandler()
                elif len( other ) == 1:
                    handler = other[0]
                    if isinstance( handler, CTrait ):
                        clone, handler = handler, None
                        metadata[ 'type' ] = clone.type
                    elif isinstance( handler, TraitInstance ):
                        metadata.setdefault( 'instance_handler',
                                             '_instance_changed_handler' )
                        if default_value is None:
                            handler.allow_none()
                        elif isinstance( default_value, _InstanceArgs ):
                            default_value_type = 7
                            default_value = ( handler.create_default_value,
                                default_value.args, default_value.kw )
                        elif (len( enum ) == 0) and (len( map ) == 0):
                            aClass    = handler.aClass
                            typeValue = type( default_value )
                            if typeValue is dict:
                                default_value_type = 7
                                default_value = ( aClass, (), default_value )
                            elif not isinstance( default_value, aClass ):
                                if typeValue is not tuple:
                                    default_value = ( default_value, )
                                default_value_type = 7
                                default_value = ( aClass, default_value, None )
                else:
                    for i, item in enumerate( other ):
                        if isinstance( item, CTrait ):
                            if item.type != 'trait':
                                raise TraitError, ("Cannot create a complex "
                                    "trait containing %s trait." %
                                    add_article( item.type ) )
                            handler = item.handler
                            if handler is None:
                                break
                            other[i] = handler
                    else:
                        handler = TraitCompound( other )

        # Save the results:
        self.handler = handler
        self.clone   = clone
        if default_value_type < 0:
            if isinstance( default_value, Default ):
                default_value_type = 7
                default_value      = default_value.default_value
            else:
                if (handler is None) and (clone is not None):
                    handler = clone.handler
                if handler is not None:
                    default_value_type = handler.default_value_type
###                 fixme: Is this path every used??? Remove it if not...
###                 if default_value_type >= 0:
###                     if hasattr( handler, 'default_value' ):
###                         default_value = handler.default_value(default_value)
###                 else:
                    if default_value_type < 0:
                        try:
                            default_value = handler.validate( None, '',
                                                              default_value )
                        except:
                            pass
                if default_value_type < 0:
                    default_value_type = _default_value_type( default_value )
        self.default_value_type = default_value_type
        self.default_value      = default_value
        self.metadata           = metadata.copy()

    #---------------------------------------------------------------------------
    #  Determine the correct TraitHandler for each item in a list:
    #---------------------------------------------------------------------------

    def do_list ( self, list, enum, map, other ):
        for item in list:
            if item in PythonTypes:
                other.append( TraitCoerceType( item ) )
            else:
                item     = try_trait_cast( item )
                typeItem = type( item )
                if typeItem in ConstantTypes:
                    enum.append( item )
                elif typeItem in SequenceTypes:
                    self.do_list( item, enum, map, other )
                elif typeItem is DictType:
                    map.update( item )
                elif typeItem in CallableTypes:
                    other.append( TraitFunction( item ) )
                elif item is ThisClass:
                    other.append( ThisClass() )
                elif isinstance( item, TraitTypes ):
                    other.append( item )
                else:
                    other.append( TraitInstance( item ) )

    #---------------------------------------------------------------------------
    #  Returns a properly initialized 'CTrait' instance:
    #---------------------------------------------------------------------------

    def as_ctrait ( self ):
        metadata = self.metadata
        trait    = CTrait( self.type_map.get( metadata.get( 'type' ), 0 ) )
        clone    = self.clone
        if clone is not None:
            trait.clone( clone )
            if clone.__dict__ is not None:
                trait.__dict__ = clone.__dict__.copy()

        trait.default_value( self.default_value_type, self.default_value )

        handler = self.handler
        if handler is not None:
            trait.handler = handler
            if hasattr( handler, 'fast_validate' ):
                trait.set_validate( handler.fast_validate )
            else:
                trait.set_validate( handler.validate )
            if hasattr( handler, 'post_setattr' ):
                trait.post_setattr = handler.post_setattr

        trait.rich_comparison( metadata.get( 'rich_compare', True ) )

        if len( metadata ) > 0:
            if trait.__dict__ is None:
                trait.__dict__ = metadata
            else:
                trait.__dict__.update( metadata )

        return trait

    #---------------------------------------------------------------------------
    #  Extract a set of keywords from a dictionary:
    #---------------------------------------------------------------------------

    def extract ( self, from_dict, *keys ):
        to_dict = {}
        for key in keys:
            if key in from_dict:
                to_dict[ key ] = from_dict[ key ]
                del from_dict[ key ]
        return to_dict

#-------------------------------------------------------------------------------
#  Factory function for creating traits with standard Python behavior:
#-------------------------------------------------------------------------------

def TraitPython ( **metadata ):
    """ Returns a trait that has standard Python behavior.
    """
    metadata.setdefault( 'type', 'python' )
    trait = CTrait( 1 )
    trait.default_value( 0, Undefined )
    trait.__dict__ = metadata.copy()
    return trait

#-------------------------------------------------------------------------------
#  Factory function for creating C-based trait delegates:
#-------------------------------------------------------------------------------

def Delegate ( delegate, prefix = '', modify = False, **metadata ):
    """ Creates a "delegator" trait, whose definition and default value are
    delegated to a *delegate* trait attribute on another object.

    Parameters
    ----------
    delegate : string
        Name of the attribute on the current object which references the object
        that is the trait's delegate
    prefix : string
        A prefix or substitution applied to the original attribute when looking
        up the delegated attribute
    modify : Boolean
        Indicates whether changes are made to the delegate attribute,
        rather than to the delegator attribute

    Description
    -----------
    An object containing a delegator trait attribute must contain a second
    attribute that references the object containing the delegate trait attribute.
    The name of this second attribute is passed as the *delegate* argument to
    the Delegate() function.

    The following rules govern the application of the prefix parameter:

    * If *prefix* is empty or omitted, the delegation is to an attribute of
      the delegate object with the same name as the delegator attribute.
    * If *prefix* is a valid Python attribute name, then the delegation is
      to an attribute whose name is the value of *prefix*.
    * If *prefix* ends with an asterisk ('*') and is longer than one
      character, then the delegation is to an attribute whose name is the
      value of *prefix*, minus the trailing asterisk, prepended to the
      delegator attribute name.
    * If *prefix* is equal to a single asterisk, the delegation is to an
      attribute whose name is the value of the delegator object's
      __prefix__ attribute prepended to delegator attribute name.

    If *modify* is True, then any changes to the delegator attribute are
    actually applied to the delegate attribute.

    """
    if prefix == '':
        prefix_type = 0
    elif prefix[-1:] != '*':
        prefix_type = 1
    else:
        prefix = prefix[:-1]
        if prefix != '':
            prefix_type = 2
        else:
            prefix_type = 3

    trait = CTrait( 3 )
    trait.delegate( delegate, prefix, prefix_type, modify )

    # Use False instead of True so we can detect user explicitly setting
    # 'transient = True' in HasTraits.__getstate__:
    metadata.setdefault( 'transient' , False )
    metadata[ 'type' ]     = 'delegate'
    metadata[ 'delegate' ] = delegate
    metadata[ 'prefix' ]   = prefix

    trait.__dict__         = metadata.copy()
    return trait

#-------------------------------------------------------------------------------
#  Factory function for creating C-based trait properties:
#-------------------------------------------------------------------------------

def Property ( fget = None, fset = None, fvalidate = None, force = False,
               handler = None, trait = None, **metadata ):
    ### JMS: Need more detail in docstring
    """ Returns a trait whose value is a Python property.

    Parameters
    ----------
    fget : function
        The "getter" function for the property
    fset : function
        The "setter" function for the property
    fvalidate : function
        The validation function for the property
    force : Boolean
        Indicates whether to force WHAT?
    handler : function
        A trait handler function for the trait
    trait : a trait definition or value that can be converted to a trait
        A trait definition that constrains the values of the property trait

    Description
    -----------
    If no getter or setter functions are specified, it is assumed that they
    are defined elsewhere on the class whose attribute this trait is
    assigned to. For example::

        class Bar(HasTraits):
            foo = Property(Float)
            # Shadow trait attribute
            _foo = Float

            def _set_foo(self,x):
                self._foo = x

            def _get_foo(self):
                return self._foo

    """
    metadata[ 'type' ] = 'property'

    # If no parameters specified, must be a forward reference (if not forced):
    if (not force) and (fset is None):
        sum = ((fget      is not None) +
               (fvalidate is not None) +
               (trait     is not None))
        if sum <= 1:
            if sum == 0:
                return ForwardProperty( metadata )

            handler = None
            if fget is not None:
                trait = fget

            if trait is not None:
                trait = trait_cast( trait )
                if trait is not None:
                    fvalidate = handler = trait.handler
                    if fvalidate is not None:
                        fvalidate = handler.validate

            if (fvalidate is not None) or (trait is not None):
                if 'editor' not in metadata:
                    if (trait is not None) and (trait.editor is not None):
                        metadata[ 'editor' ] = trait.editor

                return ForwardProperty( metadata, fvalidate, handler )

    if fget is None:
        metadata[ 'transient' ] = True
        if fset is None:
            fget = _undefined_get
            fset = _undefined_set
        else:
            fget = _write_only

    elif fset is None:
        fset = _read_only
        metadata[ 'transient' ] = True

    if trait is not None:
        trait   = trait_cast( trait )
        handler = trait.handler
        if (fvalidate is None) and (handler is not None):
            fvalidate = handler.validate

        if ('editor' not in metadata) and (trait.editor is not None):
            metadata[ 'editor' ] = trait.editor

    if ((metadata.get( 'depends_on' ) is not None) and
        getattr( fget, 'cached_property', False )):
        metadata.setdefault( 'cached', True )

    n     = 0
    trait = CTrait( 4 )
    trait.__dict__ = metadata.copy()
    if fvalidate is not None:
        n = _arg_count( fvalidate )

    trait.property( fget,      _arg_count( fget ),
                    fset,      _arg_count( fset ),
                    fvalidate, n )
    trait.handler = handler

    return trait

Property = TraitFactory( Property )

class ForwardProperty ( object ):
    """ Used to implement Property traits where accessor functions are defined
    implicitly on the class.
    """
    def __init__ ( self, metadata, validate = None, handler = None ):
        self.metadata = metadata.copy()
        self.validate = validate
        self.handler  = handler

#-------------------------------------------------------------------------------
#  Dictionary used to handler return type mapping special cases:
#-------------------------------------------------------------------------------

SpecialNames = {
###   'int':     trait_factory( Int ),
###   'long':    trait_factory( Long ),
###   'float':   trait_factory( Float ),
###   'complex': trait_factory( Complex ),
###   'str':     trait_factory( Str ),
###   'unicode': trait_factory( Unicode ),
###   'bool':    trait_factory( Bool ),
###   'list':    trait_factory( List ),
###   'tuple':   trait_factory( Tuple ),
###   'dict':    trait_factory( Dict )
}

#-------------------------------------------------------------------------------
#  Create predefined, reusable trait instances:
#-------------------------------------------------------------------------------

# Function values only (i.e., types.FunctionType); default value is None.
Function = Trait( FunctionType )

# Method values only (i.e., types.MethodType); default value is None.
Method = Trait( MethodType )

# Class values (old-style, i.e., type.ClassType) only; default value is None.
Class = Trait( ClassType )

# Module values only (i.e., types.ModuleType); default value is None.
Module = Trait( ModuleType )

# Type values only (i.e., types.TypeType); default value is None.
Type = Trait( TypeType )

# Allows only class values of the same class (or a subclass) as the object
# containing the trait attribute; default value is None.
This = Trait( ThisClass )

# Same as This; default value is the object containing the trait attribute
# defined using this trait..
self = Trait( Self, ThisClass )

# Either(A,B,...,Z) allows any of the traits A,B,...,Z. ('Either' is
# grammatically imprecise, but it reads better than 'AnyOf' or 'OneOf'.)
Either = lambda *args: Trait(None, *args)

# This trait provides behavior identical to a standard Python attribute.
# That is, it allows any value to be assigned, and raises an ValueError if
# an attempt is made to get the value before one has been assigned. It has no
# default value. This trait is most often used in conjunction with wildcard
# naming. See the *Traits User Manual* for details on wildcards.
Python = TraitPython()

# Prevents any value from being assigned or read.
# That is, any attempt to get or set the value of the trait attribute raises
# an exception. This trait is most often used in conjunction with wildcard
# naming, for example, to catch spelling mistakes in attribute names. See the
# *Traits User Manual* for details on wildcards.
Disallow = CTrait( 5 )

# This trait is write-once, and then read-only.
# The initial value of the attribute is the special, singleton object
# Undefined. The trait allows any value to be assigned to the attribute
# if the current value is the Undefined object. Once any other value is
# assigned, no further assignment is allowed. Normally, the initial assignment
# to the attribute is performed in the class constructor, based on information
# passed to the constructor. If the read-only value is known in advance of
# run time, use the Constant() function instead of ReadOnly to define
# the trait.
ReadOnly = CTrait( 6 )
ReadOnly.default_value( 0, Undefined )  # This allows it to be written once

# Indicates that a parameter is missing from a type-checked method signature.
# Allows any value to be assigned; no type-checking is performed; default value
# is the singleton Missing object.
# See **enthought.traits.has_traits.method()**.
missing         = CTrait( 0 )
missing.handler = TraitHandler()
missing.default_value( 1, Missing )

# Generic trait with 'object' behavior:
generic_trait = CTrait( 8 )

# Callable values; default is None:
Callable = Trait( TraitCallable(), copy = 'ref' )

#-------------------------------------------------------------------------------
#  User interface related color and font traits:
#-------------------------------------------------------------------------------

def Color ( *args, **metadata ):
    """ Returns a trait whose value must be a GUI toolkit-specific color.

    Description
    -----------
    For wxPython, the returned trait accepts any of the following values:

    * A wx.Colour instance
    * A wx.ColourPtr instance
    * an integer whose hexadecimal form is 0x*RRGGBB*, where *RR* is the red
      value, *GG* is the green value, and *BB* is the blue value

    Default Value
    -------------
    For wxPython, 0x000000 (that is, white)
    """
    from enthought.traits.ui.api import ColorTrait
    return ColorTrait( *args, **metadata )

Color = TraitFactory( Color )

def RGBColor ( *args, **metadata ):
    """ Returns a trait whose value must be a GUI toolkit-specific RGB-based color.

    Description
    -----------
    For wxPython, the returned trait accepts any of the following values:

    * A tuple of the form (*r*, *g*, *b*), in which *r*, *g*, and *b* represent
      red, green, and blue values, respectively, and are floats in the range
      from 0.0 to 1.0
    * An integer whose hexadecimal form is 0x*RRGGBB*, where *RR* is the red
      value, *GG* is the green value, and *BB* is the blue value

    Default Value
    -------------
    For wxPython, (0.0, 0.0, 0.0) (that is, white)
    """
    from enthought.traits.ui.api import RGBColorTrait
    return RGBColorTrait( *args, **metadata )

RGBColor = TraitFactory( RGBColor )

def RGBAColor ( *args, **metadata ):
    """ Returns a trait whose value must be a GUI toolkit-specific RGBA-based color.

    Description
    -----------
    For wxPython, the returned trait accepts any of the following values:

    * A tuple of the form (*r*, *g*, *b*, *a*), in which *r*, *g*, *b*, and *a*
      represent red, green, blue, and alpha values, respectively, and are floats
      in the range from 0.0 to 1.0
    * An integer whose hexadecimal form is 0x*AARRGGBB*, where *AA* is the alpha
      (transparency) value, *RR* is the red value, *GG* is the green value, and
      *BB* is the blue value

    Default Value
    -------------
    For wxPython, (0.0, 0.0, 0.0, 1.0) (that is, opaque white)
    """
    from enthought.traits.ui.api import RGBAColorTrait
    return RGBAColorTrait( *args, **metadata )

RGBAColor = TraitFactory( RGBAColor )

def Font ( *args, **metadata ):
    """ Returns a trait whose value must be a GUI toolkit-specific font.

    Description
    -----------
    For wxPython, the returned trait accepts any of the following:

    * a wx.Font instance
    * a wx.FontPtr instance
    * a string describing the font, including one or more of the font family,
      size, weight, style, and typeface name.

    Default Value
    -------------
    For wxPython, 'Arial 10'
    """
    from enthought.traits.ui.api import FontTrait
    return FontTrait( *args, **metadata )

Font = TraitFactory( Font )

