""" The ctraits module defines the CHasTraits and CTrait C extension types that
define the core performance oriented portions of the Traits package.

"""
from cpython.dict cimport PyDict_GetItem, PyDict_Check
from cpython.object cimport PyCallable_Check, PyObject_TypeCheck, PyObject_Call
from cpython.ref cimport PyObject, Py_TYPE
from cpython.tuple cimport PyTuple_CheckExact, PyTuple_GET_SIZE, PyTuple_GET_ITEM
from cpython.type cimport PyType_Check

cdef extern from 'Python.h':
    PyObject* PyObject_GenericGetAttr(PyObject*, PyObject*)

    ctypedef struct PyTypeObject:
        PyObject* tp_dict

# Constants
cdef object class_traits = "__class_traits__"
cdef object listener_traits = "__listener_traits__"
cdef object editor_property = "editor"
cdef object class_prefix = "__prefix__"
cdef object trait_added = "trait_added"
cdef object empty_tuple = tuple()
cdef object empty_dict = {}
cdef object Undefined           # Global 'Undefined' value */
cdef object Uninitialized       # Global 'Uninitialized' value */
cdef object TraitError          # TraitError exception */
cdef object DelegationError     # DelegationError exception */
cdef object TraitListObject     # TraitListObject class */
cdef object TraitSetObject      # TraitSetObject class */
cdef object TraitDictObject     # TraitDictObject class */
cdef object TraitValue          # TraitValue class */
cdef object adapt               # PyProtocols 'adapt' function */
cdef object validate_implements # 'validate implementation' function */
cdef object is_callable         # Marker for 'callable' value */
cdef object _trait_notification_handler # User supplied trait */
            # notification handler (intended for use by debugging tools) */
cdef PyTypeObject* ctrait_type  # Python-level CTrait type reference */


_HasTraits_monitors = []        # Object creation monitors. */

# Object has been intialized
DEF HASTRAITS_INITED = 0x00000001

# Do not send notifications when a trait changes value:
DEF HASTRAITS_NO_NOTIFY = 0x00000002

# Requests that no event notifications be sent when this object is assigned to 
# a trait
DEF HASTRAITS_VETO_NOTIFY = 0x00000004

#----------------------------------------------------------------------------
#  'CTrait' flag values:
#----------------------------------------------------------------------------

# The trait is a Property:
DEF TRAIT_PROPERTY = 0x00000001

# Should the delegate be modified (or the original object)?
DEF TRAIT_MODIFY_DELEGATE = 0x00000002

# Should a simple object identity test be performed (or a rich compare)?
DEF TRAIT_OBJECT_IDENTITY = 0x00000004

# Make 'setattr' store the original unvalidated value
DEF TRAIT_SETATTR_ORIGINAL_VALUE = 0x00000008

# Send the 'post_setattr' method the original unvalidated value
DEF TRAIT_POST_SETATTR_ORIGINAL_VALUE = 0x00000010

# Can a 'TraitValue' be assigned to override the trait definition? 
DEF TRAIT_VALUE_ALLOWED = 0x00000020

# Is this trait a special 'TraitValue' trait that uses a property?
DEF TRAIT_VALUE_PROPERTY = 0x00000040

# Does this trait have an associated 'mapped' trait? 
DEF TRAIT_IS_MAPPED = 0x00000080

# Should any old/new value test be performed before generating
# notifications? 
DEF TRAIT_NO_VALUE_TEST = 0x00000100

# Forward declarations

cdef class cTrait
cdef class CHasTraits
cdef class CTraitMethod

ctypedef object (*trait_validate)(cTrait, CHasTraits, object, object)
ctypedef object (*trait_getattr)(cTrait, CHasTraits, object)
ctypedef int (*trait_setattr)(cTrait, cTrait, CHasTraits, object , object)
ctypedef int (*trait_post_setattr)(cTrait, CHasTraits, object , object)
ctypedef object (*delegate_attr_name_func)(cTrait, CHasTraits, object)

cdef object validate_trait_type(cTrait trait, CHasTraits obj, object name, object value):
    """ Verifies a Python value is of a specified type (or None). """

    cdef object type_info = trait.py_validate
    cdef int kind = PyTuple_GET_SIZE(type_info)

    if (kind == 3 and value == None) or \
        PyObject_TypeCheck(
            value, <PyTypeObject*> PyTuple_GET_ITEM(type_info, kind -1)):
        return value
    else:
        trait.handler.error(obj, name, value)

cdef trait_validate validate_handlers[20]
validate_handlers[0] = validate_trait_type
#    validate_trait_instance,
#    validate_trait_self_type,
#    validate_trait_int,
#    validate_trait_float,
#    validate_trait_enum,
#    validate_trait_map,
#    validate_trait_complex,
#    NULL,
#    validate_trait_tuple,
#    validate_trait_prefix_map,
#    validate_trait_coerce_type,
#    validate_cast_type,
#    validate_trait_function,
#    validate_trait_python,
#    # The following entries are used by the __getstate__ method ...
#    setattr_validate0,
#    setattr_validate1,
#    setattr_validate2,
#    setattr_validate3,
#    # End of __getstate__ method entries
#    validate_trait_adapt
#}

#-----------------------------------------------------------------------------
#  'CHasTraits' instance definition:
#
#  Note: traits are normally stored in the type's dictionary, but are added to
#  the instance's traits dictionary 'trait_dict' when the traits are defined
#  dynamically or 'on_trait_change' is called on an instance of the trait.
#
#  All 'anytrait_changed' notification handlers are stored in the instance's
#  'notifiers' list.
#----------------------------------------------------------------------------*/
cdef void trait_property_changed( CHasTraits obj, str name, object value_old, object None):
    pass


cdef class CHasTraits:

    cdef dict ctrait_dict  # Class traits dictionary
    cdef dict itrait_dict   # Instance traits dictionary
    cdef list notifiers    # List of any trait changed notification handler
    cdef int flags         # Behavior modification flags
    cdef dict obj_dict     # Object attribute dictionary ('__dict__')

    def __cinit__(self):
        cdef  PyTypeObject* pytype = Py_TYPE(self)
        cdef PyObject* class_traits_dict = PyDict_GetItem(<object>pytype.tp_dict, class_traits)
        # FIXME: add checks from has_traits_new !!!
        self.ctrait_dict = <dict>class_traits_dict


    def __dealloc__(self):
        # see has_traits_dealloc
        # Do we really need to do this? Or can we rely on Cython ?
        #PyObject_GC_UnTrack(self)
        #Py_TRASHCAN_SAFE_BEGIN(obj)
        self.has_traits_clear()
        #self.ob_type.tp_free(<object>obj)
        #Py_TRASHCAN_SAFE_END(self)

    cdef has_traits_clear(self):
        # Supposed to Py_CLEAR the members ... do we really want to do that? Or
        # will Cython do it for us?
        pass

    cdef cTrait get_prefix_trait(self, str name, int is_set):

        # __prefix_trait has been added by HasTraits subclasss
        cdef object trait = self.__prefix_trait__(name, is_set)
        if trait is not None:
            self.ctrait_dict[name] = trait

    cdef int setattr_value(self, cTrait trait, str name, object value):

        cdef cTrait trait_new = trait.as_ctrait(trait)
        if trait_new is not None and isinstance(trait, cTrait):
            raise TraitError("Result of 'as_ctrait' method was not a 'CTraits' instance.")

        if self.itrait_dict is not None:
            trait_old = self.itrait_dict.get(name, None)
            if trait_old is not None and trait_old.flags & TRAIT_VALUE_PROPERTY != 0:
                result = trait_old._unregister(self, name)
            if trait_new is None:
                del self.itrait_dict[name]
        else:
            self.itrait_dict = {}

        if is_property(trait_new):
            value_old = self.__getattr__(name)
            if self.obj_dict is not None:
                del self.obj_dict[name]

        self.itrait_dict[name] = trait_new

        if is_property(trait_new):
            trait_new._register(self, name)
            trait_property_changed(self, name, value_old, None)

    def __getattr__(self, name): # has_traits_getattro(self, name):
        cdef object value
        cdef cTrait trait

        if self.obj_dict is not None:
            # had a low level performance hack with support for unicode names
            value = <object>PyDict_GetItem(self.obj_dict, name)
            if value is None:
                raise KeyError('Invalid attribute error')
        if self.itrait_dict is not None:
            trait = <object>PyDict_GetItem(self.itrait_dict, name)
        else:
            trait = <object>PyDict_GetItem(self.ctrait_dict, name)

        if trait is not None:
            value = trait.getattr(trait, self, name)
        else:
            value = <object>PyObject_GenericGetAttr(<PyObject*>self, <PyObject*>name)
            if value is None:
                trait = self.get_prefix_trait(name, 0)
                if trait is not None:
                    value = trait.getattr(trait, self, name)

        return value

    def __setattr__(self, name, value):
        trait = getattr(self.itrait_dict, name, None)
        if trait is None:
            trait = getattr(self.ctrait_dict, name, None)
            if trait is None:
                trait = self.get_prefix_trait(name, 1)
        if trait is not None:
            if (trait.flags & TRAIT_VALUE_ALLOWED != 0) and isinstance(value, TraitValue):
                self.setattr_value(trait, name, value)
            else:
                trait.setattr(trait, trait, self, name, value)

    def _notifiers(self, force_create):
        """ Returns (and optionally creates) the anytrait 'notifiers' list """
        if self.notifiers is None and force_create:
            self.notifiers = []

        return self.notifiers

# Assigns a value to a specified property trait attribute 
cdef object getattr_property0(cTrait trait, CHasTraits obj, object name):
    return PyObject_Call(trait.delegate_name, tuple(), None)

cdef object getattr_property1(cTrait trait, CHasTraits obj, object name):
    cdef object args = (obj,)
    PyObject_Call(trait.delegate_name, args, None)

cdef object getattr_property2(cTrait trait, CHasTraits obj, object name):
    cdef object args = (obj, name)
    PyObject_Call(trait.delegate_name, args, None)

cdef object getattr_property3(cTrait trait, CHasTraits obj, object name):
    cdef object args = (obj, name, trait)
    PyObject_Call(trait.delegate_name, args, None)

cdef trait_getattr getattr_property_handlers[4]
getattr_property_handlers[0] = getattr_property0
getattr_property_handlers[1] = getattr_property1
getattr_property_handlers[2] = getattr_property2
getattr_property_handlers[3] = getattr_property3

cdef int setattr_validate_property(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value):

    cdef int result
    cdef object validated = traitd.validate(traitd, obj, name, value)
    if validated is not None:
        result = (<trait_setattr> traitd.post_setattr)(traito, traitd, obj, name, validated)
    return result

cdef void raise_delete_property_error(object obj, object name):
    raise TraitError("Cannot delete the '%.400s' property of '%.50s' object " % (obj, name))

cdef int setattr_property0(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value):

    if value is None:
        raise_delete_property_error(obj, name)

    cdef object args = tuple()
    result = PyObject_Call(traitd.delegate_prefix, args, None)
    if result is None:
        return -1
    else:
        return 0

cdef int setattr_property1(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value):

    if value is None:
        raise_delete_property_error(obj, name)

    cdef object args = (value)
    cdef object result = PyObject_Call(traitd.delegate_prefix, args, None)
    if result is None:
        return -1
    else:
        return 0

cdef int setattr_property2(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value):

    if value is None:
        raise_delete_property_error(obj, name)

    cdef object args = (obj, value)
    cdef object result = PyObject_Call(traitd.delegate_prefix, args, None)
    if result is None:
        return -1
    else:
        return 0

cdef int setattr_property3(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value):

    if value is None:
        raise_delete_property_error(obj, name)

    cdef object args = (obj, name, value)
    cdef object result = PyObject_Call(traitd.delegate_prefix, args, None)
    if result is None:
        return -1
    else:
        return 0

# Calls a Python-based trait post_setattr handler
cdef int post_setattr_trait_python(cTrait trait, CHasTraits obj, object name, object value):

    cdef object args = (obj, name, value)
    cdef object result = PyObject_Call(trait.py_post_setattr, args, None)
    if result is None:
        return -1
    else:
        return 0

#  Sets the 'property' value fields of a CTrait instance:
cdef trait_setattr setattr_property_handlers[5]
setattr_property_handlers[0] = setattr_property0
setattr_property_handlers[1] = setattr_property1
setattr_property_handlers[2] = setattr_property2
setattr_property_handlers[3] = setattr_property3
#  The following entries are used by the __getstate__ method__: */
setattr_property_handlers[4] = <trait_setattr> post_setattr_trait_python



cdef object setattr_validate0(cTrait trait, CHasTraits obj, object name, object value):
    cdef args = tuple()
    return PyObject_Call(trait.py_validate, args, None)

cdef object setattr_validate1(cTrait trait, CHasTraits obj, object name, object value):
    cdef args = (value,)
    return PyObject_Call(trait.py_validate, args, None)

cdef object setattr_validate2(cTrait trait, CHasTraits obj, object name, object value):
    cdef args = (obj, value,)
    return PyObject_Call(trait.py_validate, args, None)

cdef object setattr_validate3(cTrait trait, CHasTraits obj, object name, object value):
    cdef args = (obj, name, value,)
    return PyObject_Call(trait.py_validate, args, None)

cdef trait_validate setattr_validate_handlers[4]
setattr_validate_handlers[0] = setattr_validate0
setattr_validate_handlers[1] = setattr_validate1
setattr_validate_handlers[2] = setattr_validate2
setattr_validate_handlers[3] = setattr_validate3

cdef class cTrait:

    cdef int flags # Flags bits
    cdef trait_getattr getattr
    cdef trait_setattr setattr
    cdef trait_post_setattr post_setattr
    cdef object py_post_setattr # Pyton=based post 'setattr' handler
    cdef trait_validate validate
    cdef object py_validate # Python-based validat value handler
    cdef int default_value_type # Type of default value: see the default_value_for function
    cdef object default_value # Default value for Trait
    cdef object delegate_name # Optional delegate name (also used for property get)
    cdef object delegate_prefix # Optional delate prefix (also usef for property set)
    cdef delegate_attr_name_func delegate_attr_name # Optional routirne to return the computed delegate attribute name
    cdef list notifiers # Optional list of notification handlers
    cdef public object handler # Associated trait handler object (Note: the obj_dict field must be last)
    cdef dict obj_dict # Standard Python object dict

    cdef public str instance_handler # ADDED BY DP
    cdef public object on_trait_change # ADDED BY DP
    cdef public object event # ADDED BY DP

    def __cinit__(self):

        self._notifiers = []

    def value_allowed(self, int value_allowed):
        if value_allowed:
            self.flags |= TRAIT_NO_VALUE_TEST
        else:
            self.flags &= ~TRAIT_VALUE_ALLOWED

    def default_value(self, value_type=None, value=None):
        """ Sets the value of the 'default_value' field of a CTrait instance.

        Parameters
        ----------
        value_type: int
            The type of default value. Must be between 0 and 1
        value: object
            The default value
        """
        if value_type is None and value is None:
            return (self.default_value_type, self.default_value)
        if value_type < 0 and value_type > 9:
            raise ValueError('The default value type must be 0..9 but %s was'
                             ' specified' % value_type)
        self.value_type = value_type
        self.default_value = value

    def set_validate(self, validate):
        cdef int n, kind

        if PyCallable_Check(validate):
            kind = 14

        if PyTuple_CheckExact(validate):
            n = len(validate)
            if n > 0:
                kind = validate[0]
                if kind == 0: # Type check
                    if n == 2 and PyType_Check(validate[-1]) or validate[1] == None:
                        pass
                    else:
                        raise ValueError('The argument must be a tuple or callable.')
                elif kind == 1: # Instance check
                    if n <=3 and (n == 2 or  validate[1]  == None):
                        pass
                    else:
                        raise ValueError('The argument must be a tuple or callable.')
                elif kind == 2: # Self type check
                    if n == 1 or (n ==2 and validate[1] == None):
                        pass
                    else:
                        raise ValueError('The argument must be a tuple or callable.')
                elif kind == 3: # Integer range check
                    if n == 4:
                        v1 = validate[1]
                        v2 = validate[2]
                        v3 = validate[3]
                        if (v1 is None or isinstance(v1, int)) and \
                           (v2 is None or isinstance(v2, int)) and \
                           isinstance(v3, int):
                            pass
                        else:
                            raise ValueError('The argument must be a tuple or callable.')
                elif kind == 5: # Enumerated item check:
                    if n == 2:
                        if PyTuple_CheckExact(validate[1]):
                            pass
                        else:
                            raise ValueError('The argument must be a tuple or callable.')
                elif kind == 10: # Prefix map item check
                    if n == 3:
                        if PyDict_Check(validate[1]):
                            pass
                        else:
                            raise ValueError('The argument must be a tuple or callable.')

                elif kind == 11: # Coercable type check
                    if n >= 2:
                        pass
                    else:
                        raise ValueError('The argument must be a tuple or callable.')
                elif kind == 12: # Castable type check
                    if n ==2 :
                        pass
                    else:
                        raise ValueError('The argument must be a tuple or callable.')
                elif kind == 13:
                    if n ==2 and PyCallable_Check(validate[1]):
                        pass
                    else:
                        raise ValueError('The argument must be a tuple or callable.')
                # case 14: Python-based validator check
                # case 15..18: Property 'setattr' validate checks
                elif kind == 19:  # PyProtocols 'adapt' check
                    if n == 4 and isinstance(validate[2], int) and isinstance(validate[3], bool):
                        pass
                    else:
                        raise ValueError('The argument must be a tuple or callable.')
                else:
                    raise NotImplementedError('Work in progress. {}'.format(kind))

        self.validate = validate_handlers[kind]
        self.py_validate = validate


    def get_validate(self):
        if self.validate is not NULL:
            return self.py_validate

    def clone(self, cTrait trait):
        self.flags = trait.flags
        self.getattr = trait.getattr
        self.setattr = trait.setattr
        self.post_setattr = trait.post_setattr
        self.py_post_setattr = trait.py_post_setattr
        self.validate = trait.validate
        self.py_validate = trait.py_validate
        self.default_value_type = trait.default_value_type
        self.default_value = trait.default_value
        self.delegate_name = trait.delegate_name
        self.delegate_prefix = trait.delegate_prefix
        self.delegate_attr_name = trait.delegate_attr_name
        self.handler = trait.handler

    def _notifiers(self, force_create):
        """ Returns (and optionally creates) the anytrait 'notifiers' list """

        if self.notifiers is None and force_create == 1:
            self.notifiers = []

        return self.notifiers

    def property(self, *args):

        if len(args) == 0:
            if self.flags & TRAIT_PROPERTY:
                result = (self.delegate_name, self.delegate_prefix, self.py_validate)
                return result
        else:
            get, get_n, set_, set_n, validate, validate_n = args
            if not PyCallable_Check(get) or not PyCallable_Check(set_) or \
                (validate is not None and not PyCallable_Check(validate)) or \
                get_n < 0 or get_n > 3 or set_n < 0 or set_n > 3 or \
                validate_n < 0 or validate_n > 3:
                raise ValueError('Invalid arguments')

            self.flags |= TRAIT_PROPERTY
            self.getattr = getattr_property_handlers[get_n]
            if (validate is not None):
                self.setattr = setattr_validate_property
                self.post_setattr = <trait_post_setattr> setattr_property_handlers[set_n]
                self.validate = setattr_validate_handlers[validate_n]
            else:
                self.setattr = setattr_property_handlers[set_n]

            self.delegate_name = get
            self.delegate_prefix = set
            self.py_validate = validate

    def is_mapped(self, int is_mapped):
        """ Sets the value of the 'is_mapped' flag of a CTrait instance (used in the
            processing of the default value of a trait with a 'post_settattr' handler).

        """

        if is_mapped != 0:
            self.flags |= TRAIT_IS_MAPPED
        else:
            self.flags &= ~TRAIT_IS_MAPPED

        return self

    def setattr_original_value(self, int original_value):
        """ Sets the value of the 'setattr_original_value' flag of a CTrait instance. """
        if original_value != 0:
            self.flags |= TRAIT_SETATTR_ORIGINAL_VALUE
        else:
            self.flags &= ~TRAIT_SETATTR_ORIGINAL_VALUE

        return self

cdef class CTraitMethod:
    pass

def _undefined(Undefined_, Uninitialized_):
    """ Sets the global Undefined and Uninitialized values. """
    global Undefined, Uninitialized
    Undefined = Undefined_
    Unitialized = Uninitialized_

def _exceptions(TraitError_, DelegationError_):
    """ Sets the global TraitError and DelegationError exception types. """

    global TraitError, DelegationError
    TraitError = TraitError_
    DelegationError = DelegationError_

def _list_classes(TraitListObject_, TraitSetObject_, TraitDictObject_):
    """ Sets the global TraitListObject, TraitSetObject and TraitDictObject
    classes.

    """

    global TraitListObject, TraitSetObject, TraitDictObject
    TraitListObject = TraitListObject_
    TraitSetObject = TraitSetObject_
    TraitDictObject = TraitDictObject_

def _adapt(adapt_):
    """Sets the global 'adapt' reference to the PyProtocols adapt function. """
    global adapt
    adapt = adapt_

def _ctrait(CTrait_):
    """ Sets the global ctrait_type class reference. """
    global ctrait_type
    ctrait_type = <PyTypeObject*>CTrait_

def _validate_implements(validate_implements_):
    """ Sets the global 'validate_implements' reference to the Python level
    function.

    """
    global validate_implements
    validate_implements = validate_implements_

def _value_class(TraitValue_):
    global TraitValue
    TraitValue = TraitValue_

cdef void trait_clone(cTrait trait1, cTrait trait2):
    pass

cdef int is_property(cTrait trait):
    return trait.flags & TRAIT_VALUE_PROPERTY != 0


