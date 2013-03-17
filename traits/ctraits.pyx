""" The ctraits module defines the CHasTraits and CTrait C extension types that
define the core performance oriented portions of the Traits package.

"""
from cpython.dict cimport PyDict_GetItem, PyDict_Check
from cpython.int cimport PyInt_Check, PyInt_AS_LONG
from cpython.exc cimport PyErr_Clear
from cpython.float cimport PyFloat_Check, PyFloat_FromDouble, PyFloat_AS_DOUBLE
from cpython.object cimport PyCallable_Check, PyObject_TypeCheck, PyObject_Call, PyObject_RichCompareBool, Py_NE
from cpython.ref cimport PyObject, Py_TYPE, PyTypeObject
from cpython.string cimport PyString_Check
from cpython.tuple cimport PyTuple_CheckExact, PyTuple_GET_SIZE, PyTuple_GET_ITEM, PyTuple_SET_ITEM, PyTuple_New, PyTuple_Check
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
ctypedef int (*trait_setattr)(cTrait, cTrait, CHasTraits, object , object) except? -1
ctypedef int (*trait_post_setattr)(cTrait, CHasTraits, object , object)
ctypedef object (*delegate_attr_name_func)(cTrait, CHasTraits, object)

cdef object raise_trait_error(cTrait trait, CHasTraits obj, object name, object value):

    cdef object result = trait.handler.error(obj, name, value)

cdef object validate_trait_type(cTrait trait, CHasTraits obj, object name, object value):
    """ Verifies a Python value is of a specified type (or None). """

    print 'Validate trait type'
    cdef object type_info = trait.py_validate
    cdef int kind = PyTuple_GET_SIZE(type_info)

    if (kind == 3 and value is None) or \
        PyObject_TypeCheck(
            value, <PyTypeObject*> PyTuple_GET_ITEM(type_info, kind -1)):
        return value
    else:
        trait.handler.error(obj, name, value)

cdef object validate_trait_float(cTrait trait, CHasTraits obj, object name, object value):
    """ Verifies a Python value is a float within a specified range. """

    print 'Validate trait float'
    # FIXME: where defined as register in the C code
    cdef object low, high
    cdef long exlude_mask
    cdef double float_value

    cdef object type_info = trait.py_validate

    if not PyFloat_Check(value):
        if not PyInt_Check(value):
            raise_trait_error(trait, obj, name, value)
        float_value = <double> PyInt_AS_LONG(value)
        value = float(float_value)
    else:
        float_value = value

    low = type_info[1]
    high = type_info[2]
    exclude_mask = type_info[3]

    if low is not None:
        if (exclude_mask & 1) != 0:
            if float_value <= low:
                raise_trait_error(trait, obj, name, value)
        elif float_value < low:
            raise_trait_error(trait, obj, name, value)

    if high is not None:
        if exclude_mask & 2 != 0:
            if float_value >= high:
                raise_trait_error(trait, obj, name, value)
        elif float_value > high:
                raise_trait_error(trait, obj, name, value)

    return value

cdef object validate_trait_self_type(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError('vt')

cdef object validate_trait_int(cTrait trait, CHasTraits obj, object name, object value):
    print 'Validate trait int'
    # FIXME: where defined as register in the C code
    cdef object low, high
    cdef object type_info = trait.py_validate
    cdef long int_value, exclude_mask

    if PyInt_Check(value):
        int_value = PyInt_AS_LONG(value)
        low = type_info[1]
        high = type_info[2]
        exclude_mask = PyInt_AS_LONG(type_info[3])

        if low is not None:
            if exclude_mask & 1 != 0:
                if int_value <= PyInt_AS_LONG(low):
                    raise_trait_error(trait, obj, name, value)
            elif int_value < PyInt_AS_LONG(low):
                raise_trait_error(trait, obj, name, value)

        if high is not None:
            if exclude_mask & 2 != 0:
                if int_value >= PyInt_AS_LONG(high):
                    raise_trait_error(trait, obj, name, value)
            elif int_value > PyInt_AS_LONG(high):
                raise_trait_error(trait, obj, name, value)

        return value
    else:
        raise_trait_error(trait, obj, name, value)




cdef object validate_trait_instance(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError('vti')

cdef object validate_trait_enum(cTrait trait, CHasTraits obj, object name, object value):
    """ Verifies a Python value is in a specified enumeration. """

    print 'Validate trait enum'
    cdef object type_info = trait.py_validate
    if value in type_info[1]:
        return value
    else:
        raise_trait_error(trait, obj, name, value)

cdef object validate_trait_map(cTrait trait, CHasTraits obj, object name, object value):
    """  Verifies a Python value is in a specified map (i.e. dictionary). """
    print 'Validate trait map'
    cdef object type_info = trait.py_validate
    if value in type_info[1]:
        return value
    else:
        raise_trait_error(trait, obj, name, value)

cdef object validate_trait_complex(cTrait trait, CHasTraits obj, object name, object value):
    """ Verifies a Python value satisifies a complex trait definition. """

    print 'Validate trait complex'
    cdef int i, j, k, kind
    cdef long int_value, exclude_mask, mode, rc
    cdef double float_value
    cdef object low, high, result, type_info, type_, type2_, args
    cdef object list_type_info = trait.py_validate[1]
    cdef int n = len(list_type_info)

    print 'N is ', n
    for i in xrange(n):
        type_info = list_type_info[i]
        check = type_info[0]

        print 'Check is', check
        if check == 0: # Type check
            kind = len(type_info)
            if (kind == 3 and value is None) or \
                not PyObject_TypeCheck(value, <PyTypeObject*>type_info[kind-1]):
                    return value
        elif check == 1: # Instance check
            kind = len(type_info)
            if (kind == 3 and value is None) or \
                   isinstance(value, type_info[kind-1]):
                return value
        elif check == 2: # Self type check
            type_ = type(obj)
            if (len(type_info) == 2 and value is None) or \
                   PyObject_TypeCheck(value, <PyTypeObject*> type_):
                return value
        elif check == 3: # Integer range check
            if PyInt_Check(value):
                int_value = PyInt_AS_LONG(value)
                low = type_info[1]
                high = type_info[2]
                exclude_mask = PyInt_AS_LONG(type_info[3])

                if low is not None:
                    if (exclude_mask & 1) != 0:
                        below_low = int_value <= PyInt_AS_LONG(low)
                    else:
                        below_low = int_value < PyInt_AS_LONG(low)

                if high is not None:
                    if (exclude_mask & 2) != 0:
                        above_high = int_value >= PyInt_AS_LONG(high)
                    else:
                        above_high = int_value > PyInt_AS_LONG(high)

                print low, high, int_value, exclude_mask, below_low, above_high
                if below_low or above_high:
                    continue
                else:
                    return value
        elif check == 4: # Floating point range check
            if not PyFloat_Check(value):
                if PyInt_Check(value):
                    float_value = <double> PyInt_AS_LONG(value)
                    value = PyFloat_FromDouble(float_value)
                else:
                    raise_trait_error(trait, obj, name, value)
            else:
                float_value = PyFloat_AS_DOUBLE(value)

            low = type_info[1]
            high = type_info[2]
            exclude_mask = PyInt_AS_LONG(type_info[3])

            if low is not None:
                if exclude_mask & 1 != 0:
                    below_low = float_value > PyFloat_AS_DOUBLE(low)
                else:
                    below_low = float_value >= PyFloat_AS_DOUBLE(low)
            if high is not None:
                if exclude_mask & 2 != 0:
                    above_high = float_value < PyFloat_AS_DOUBLE(high)
                else:
                    above_high = float_value <= PyFloat_AS_DOUBLE(high)
            if below_low or above_high:
                continue
            else:
                return value
        elif check == 5: #Enumerated item check
            if value in type_info[1]:
                return value
        elif check == 6: # Mapped item check
            if value in type_info[1]:
                return value
        elif check == 8: # Perform 'slow' validate check
            result = type_info[1].slow_validate(obj, name, value)
            return result
        elif check == 9: # Tuple item check
            return validate_trait_tuple_check(type_info[1], obj, name, value)
        elif check == 10: # PRefix map item check
            try:
                result = type_info[1][value]
                return result
            except:
                result = type_info[2](obj, name, value)
                return result
            else:
                raise_trait_error(trait, obj, name, value)
        elif check == 11: # Coercable type check
            type_ = type_info[1]
            if isinstance(value, type_):
                return value
            else:
                k = len(type_info)
                for j in xrange(2, k):
                    type2_ = type_info[j]
                    if type2_ is None:
                        break
                    if issubclass(value, type2_):
                        return value
                old_j = j+1
                for j in xrange(old_j,k):
                    type2_ = type_info[j]
                    if isinstance(value, type2_):
                        return type_(value)
        else:
            raise NotImplementedError('Complex validation not implemented for %d' % check)

    # If we hit this line, it means the validation was not successful.
    raise_trait_error(trait, obj, name, value)

cdef object validate_trait_tuple(cTrait trait, CHasTraits obj, object name, object value):
    print 'Validate trait tuple'
    return validate_trait_tuple_check(trait.py_validate[1], obj, name, value)

cdef object validate_trait_tuple_check(cTrait trait, CHasTraits obj, object name, object value):
    "" "Verifies a Python value is a tuple of a specified type and content. """

    print 'Validate trait tuple check'
    cdef cTrait itrait
    cdef object bitm, aitem
    cdef tuple tuple_
    cdef int i, j, n

    if PyTuple_Check(trait):
        n = len(trait)
        if n == len(value):
            for i in xrange(n):
                bitem = value[i]
                itrait = trait[i]
                if itrait.validate is NULL:
                    aitem = bitem
                else:
                    aitem = itrait.valiate(itrait, obj, name, bitem)
                if tuple_ is not None:
                    PyTuple_SET_ITEM(tuple_, i, aitem)
                elif aitem != bitem:
                    tuple_ = PyTuple_New(n)
                    for j in xrange(i):
                        bitem = value[j]
                        PyTuple_SET_ITEM(tuple_, j, bitem)
                    PyTuple_SET_ITEM(tuple_, i, aitem)
            if tuple_ is not None:
                return tuple_
            else:
                return value
    else:
        raise_trait_error(trait, obj, name, value)

cdef object validate_trait_prefix_map(cTrait trait, CHasTraits obj, object name, object value):
    """ Verifies a Python value is in a specified prefix map (i.e. dictionary). """

    print 'Validate trait prefix map'
    cdef object type_info = trait.py_validate
    cdef object mapped_value = type_info[1]
    cdef object result

    print value, mapped_value
    if value in mapped_value:
        result = mapped_value[value]
    else:
        result =  trait.py_validate[2](obj, name, value)

    return result

cdef object validate_trait_coerce_type(cTrait trait, CHasTraits obj, object name, object value):
    """  Verifies a Python value is of a specified (possibly coercable) type. """

    print 'Validate trait coerce type'
    cdef int i, n
    cdef object type2

    cdef object type_info = trait.py_validate
    cdef object type_     = type_info[1]
    if PyObject_TypeCheck(value, <PyTypeObject*>type_):
        return value

    n = len(type_info)

    for i in range(2, n):
        type2 = type_info[i]
        if type2 is None:
            break
        else:
            if PyObject_TypeCheck(value, <PyTypeObject*>type2):
                return value

    restart = i
    for i in range(restart, n):

        type2 = type_info[i]
        if type2 is None:
            break
        else:
            if PyObject_TypeCheck(value, <PyTypeObject*>type2):
                return type_(value)

    raise_trait_error( trait, obj, name, value );

cdef object validate_trait_cast_type(cTrait trait, CHasTraits obj, object name, object value):
    """ Verifies a Python value is of a specified (possibly castable) type. """

    print 'Validate trait cast type'
    cdef object type_info = trait.py_validate
    if isinstance(value, type_info[1]):
        return value
    else:
        try:
            return type_info[1](value)
        except:
            raise_trait_error(trait, obj, name, value)

cdef object validate_trait_function(cTrait trait, CHasTraits obj, object name, object value):
    """ Verifies a Python value satisifies a specified function validator. """

    print 'Validate trait function'
    return trait.py_validate[1](obj, name, value)

cdef object validate_trait_python(cTrait trait, CHasTraits obj, object name, object value):
    """ Calls a Python-based trait validator. """

    print 'Validate trait python'
    return trait.py_validate[1](obj, name, value)

cdef object validate_trait_adapt(cTrait trait, CHasTraits obj, object name, object value):
    """  Attempts to 'adapt' an object to a specified interface. """

    print 'Validate trait adapt', trait, obj, name, value
    cdef object result, args, type_
    cdef object type_info = trait.py_validate
    cdef long mode, rc

    if value is None:
        if type_info[3] == 0:
            return value
        else:
            raise_trait_error( trait, obj, name, value );

    type_ = type_info[1]
    mode = type_info[2]

    if mode == 2:
        args = (value, type_, None)
    else:
        args = (value, type_)

    result = adapt(*args)
    if result is not None:
        if mode > 0 or result == value:
            return result
    else:
        result = validate_implements(*args)
        rc = PyInt_AS_LONG(result)
        if rc:
            return value
        else:
            try:
                result = default_value_for(trait, obj, name)
            except Exception:
                raise_trait_error( trait, obj, name, value)

    # Check implements
    result = validate_implements(*args)
    rc = PyInt_AS_LONG(result)
    if rc:
        return value
    else:
        raise_trait_error( trait, obj, name, value )



cdef trait_validate validate_handlers[20]
validate_handlers[0] = validate_trait_type
validate_handlers[1] = validate_trait_instance
validate_handlers[2] = validate_trait_self_type
validate_handlers[3] = validate_trait_int
validate_handlers[4] = validate_trait_float
validate_handlers[5] = validate_trait_enum
validate_handlers[6] = validate_trait_map
validate_handlers[7] = validate_trait_complex
validate_handlers[8] = NULL
validate_handlers[9] = validate_trait_tuple
validate_handlers[10] = validate_trait_prefix_map
validate_handlers[11] = validate_trait_coerce_type
validate_handlers[12] = validate_trait_cast_type
validate_handlers[13] = validate_trait_function
validate_handlers[14] = validate_trait_python
#    # The following entries are used by the __getstate__ method ...
validate_handlers[15] = setattr_validate0
validate_handlers[16] = setattr_validate1
validate_handlers[17] = setattr_validate2
validate_handlers[18] = setattr_validate3
#    # End of __getstate__ method entries
validate_handlers[19] = validate_trait_adapt


cdef int trait_property_changed( CHasTraits obj, str name, object old_value, object new_value):

    cdef cTrait trait
    cdef list tnotifiers, onotifiers
    cdef int null_new_value
    cdef int rc = 0

    trait = obj.get_trait(name, -1)
    if trait is None:
        return -1

    tnotifiers = trait.notifiers
    onotifiers = obj.notifiers

    if has_notifiers(tnotifiers, onotifiers):
        if new_value is None:
            new_value = getattr(obj, name)
        rc = call_notifiers(tnotifiers, onotifiers, obj, name, old_value,
                            new_value)
    return rc

cdef class CHasTraits:
    ''' CHasTraits class definition

     .. note::

        Traits are normally stored in the type's dictionary, but are added to
        the instance's traits dictionary 'trait_dict' when the traits are defined
        dynamically or 'on_trait_change' is called on an instance of the trait.

     All 'anytrait_changed' notification handlers are stored in the instance's
     'notifiers' list.

    '''
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
        # FIXME: make sure to clean up this method
        # Do we really need to do this? Or can we rely on Cython ?
        #PyObject_GC_UnTrack(self)
        #Py_TRASHCAN_SAFE_BEGIN(obj)
        self.has_traits_clear()
        #self.ob_type.tp_free(<object>obj)
        #Py_TRASHCAN_SAFE_END(self)

    cdef has_traits_clear(self):
        # FIXME: 
        # Supposed to Py_CLEAR the members ... do we really want to do that? Or
        # will Cython do it for us?
        pass

    cdef cTrait get_prefix_trait(self, str name, int is_set):

        # __prefix_trait has been added by HasTraits subclasss
        cdef object trait = self.__prefix_trait__(name, is_set)
        if trait is not None:
            self.ctrait_dict[name] = trait
            result = self._internal_setattr(trait_added, name)
            if result >= 0:
                trait = self.get_trait(name, 0)

        return trait

    cdef cTrait get_trait(self, str name, int instance):
        """ Returns (and optionaly creates) a specified instance or class trait. 
        """

        cdef int i, n
        cdef cTrait trait, itrait
        cdef list notifiers, inotifiers
        cdef object item

        # If there already is an instance specific version of the requested trait,
        # then return it
        if self.itrait_dict is not None:
            trait = self.itrait_dict.get(name, None)
            if trait is not None:
                return trait

        # If only an instance trait can be returned (but not created), then
        # return None
        if instance == 1:
            return None

        # Otherwise, get the class specific version of the trait (creating a
        # trait class version if necessary)
        trait = self.ctrait_dict.get(name, None)
        if trait is None:
            if instance == 0:
                return None
            trait = self.get_prefix_trait(name, 0)
            if trait is None:
                return None

        assert(isinstance(trait, cTrait))

        # If an instance specific trait is not needed, return the class trait: */
        if instance <= 0:
            return trait


        # Otherwise, create an instance trait dictionary if it does not exist: */
        if self.itrait_dict is None:
            self.itrait_dict = {}

        # Create a new instance trait and clone the class trait into it
        itrait = cTrait()
        trait_clone(itrait, trait)
        itrait.obj_dict = trait.obj_dict

        # Copy the class trait's notifier list into the instance trait
        if trait.notifiers is not None:
            itrait.notifiers = trait.notifiers[:]

        # Add the instance trait to the instance's trait dictionary and return
        # the instance trait if successful
        self.itrait_dict[name] = itrait

        return itrait


    cdef int setattr_value(self, cTrait trait, str name, object value) except? -1:
        """ Assigns a special TraitValue to a specified trait attribute. """


        print 'SETTING ', name
        cdef cTrait trait_new = trait.as_ctrait(trait)
        if trait_new is None:
            return -1
        else:
            if not isinstance(trait, cTrait):
                raise TraitError("Result of 'as_ctrait' method was not a 'CTraits' instance.")

        if self.itrait_dict is not None:
            trait_old = self.itrait_dict.get(name, None)
            if trait_old is not None and trait_old.flags & TRAIT_VALUE_PROPERTY != 0:
                result = trait_old._unregister(self, name)
            if trait_new is None and trait_old is not None:
                del self.itrait_dict[name]
                return 0
        else:
            self.itrait_dict = {}

        if is_trait_property(trait_new) != 0:
            value_old = self.__getattr__(name)
            if self.obj_dict is not None:
                del self.obj_dict[name]

        self.itrait_dict[name] = trait_new

        if is_trait_property(trait_new):
            result = trait_new._register(self, name)
            if result is None:
                return -1
            result = trait_property_changed(self, name, value_old, None)
            if result != 0:
                return -1

        return 0

    def __getattr__(self, name): # has_traits_getattro(self, name):
        cdef object obj_value
        cdef object value
        cdef cTrait trait
        cdef PyObject* res

        if self.obj_dict is not None:
            # had a low level performance hack with support for unicode names
            obj_value = self.obj_dict.get( name, None)
            if obj_value is not None:
                return obj_value
        if self.itrait_dict is not None:
            trait = self.itrait_dict.get(name, None)
        else:
            trait = self.ctrait_dict.get(name, None)

        if trait is not None:
            value = trait.getattr(trait, self, name)
        else:
            res = PyObject_GenericGetAttr(<PyObject*>self, <PyObject*>name)
            if res is NULL:
                trait = self.get_prefix_trait(name, 0)
                if trait is not None:
                    value = trait.getattr(trait, self, name)

        return value

    def __setattr__(self, name, value):
        print 'SETTING ATTR', name, value
        self._internal_setattr(name, value)

    cdef int _internal_setattr(self, str name, object value) except? -1:
        """  Handles the 'setattr' operation on a 'CHasTraits' instance. """

        # Equivalent of the has_traits_settro function

        cdef cTrait trait

        if self.itrait_dict is not None:
            trait = self.itrait_dict.get(name, None)
        else:
            trait = None

        if trait is None:
            trait = self.ctrait_dict.get(name, None)
            if trait is None:
                prefix_trait = self.get_prefix_trait(name, 1)
                if prefix_trait is None:
                    result = -1
                else:
                    trait = prefix_trait

        if (trait.flags & TRAIT_VALUE_ALLOWED != 0) and isinstance(value, TraitValue):
            print 'setattr value'
            result = self.setattr_value(trait, name, value)
        else:
            print 'trait setattr'
            result = trait.setattr(trait, trait, self, name, value)

        if result < 0:
            raise_trait_error(trait, self, name, value)


    def _notifiers(self, force_create):
        """ Returns (and optionally creates) the anytrait 'notifiers' list """
        if self.notifiers is None and force_create:
            self.notifiers = []

        return self.notifiers

    property __dict__:
        def __get__(self):
            if self.obj_dict is None:
                self.obj_dict = {}
            return self.obj_dict

        def __set__(self, value):
            if isinstance(value, dict):
                self.obj_dict = value

    def trait_property_changed(self, old, value, new_value=None):
        raise NotImplementedError('_has_traits_property_changed')

    def trait_items_event(self, name, event_object, event_trait):
        """ Handles firing a traits 'xxx_items' event. """

        print 'TRAITS ITEMS EVENT ', name, event_object, event_trait
        cdef cTrait trait
        cdef int can_retry = 1

        if not PyObject_TypeCheck(event_trait, ctrait_type):
            raise TraitError('Invalid argment to trait constructor.')

        if not PyString_Check(name):
            raise TypeError('Attribute name must be a string.')

        if (self.itrait_dict is None or name not in self.itrait_dict) and \
            name not in self.ctrait_dict:

            if not can_retry:
                raise TraitError("Can't set a collection's '_items' trait.")

            result = self.add_trait(name, event_trait)
            can_retry = 0
        else:
            if self.itrait_dict is not None:
                trait = self.itrait_dict.get(name, None)
            else:
                trait = None
            if trait is None:
                trait = self.ctrait_dict.get(name, None)

            if trait.setattr == setattr_dissalow:
                raise NotImplementedError('Check logic in C code')
            if trait.setattr(trait, trait, self, name, event_object) > 0:
                return None

    def _trait_change_notify(self, notify):
        raise NotImplementedError('_has_traits_change_notify')

    def _trait_veto_notify(self, notify):
        raise NotImplementedError()

    def traits_init(self):
        raise NotImplementedError()

    def traits_inited(self, flag):
        raise NotImplementedError()

    def _trait(self, name, instance):
        """ Returns (and optionally creates) a specified instance or class trait

        The legal values for 'instance' are:

         * 2: Return instance trait (force creation if it does not exist)
         * 1: Return existing instance trait (do not create)
         * 0: Return existing instance or class trait (do not create)
         * -1: Return instance trait or force create class trait (i.e. prefix trait)
         * -2: Return the base trait (after all delegation has been resolved)

        """
        # _has_traits_trait C function

        cdef CHasTraits delegate = self
        cdef object daname, daname2

        trait = self.get_trait(name, instance)
        if instance >= -1 or trait is None:
            return trait

        # Follow the delegation chain until we find a non-delegated trait:

        daname = name
        cdef int i = 0
        while True:
            if trait.delegate_attr_name is None:
                return trait
            dict_ = delegate.obj_dict
            if dict_ is not None:
                temp_delegate = dict_.get(trait.delegate_name, None)
                if temp_delegate is None:
                    temp_delegate = getattr(delegate, trait.delegate_name)
                    if temp_delegate:
                        break
            else:
                break

            delegate = temp_delegate
            if not PyObject_TypeCheck(delegate, <PyTypeObject*>CHasTraits):
                raise DelegationError(
                    "The '%.400s' attribute of a '%.50s' object has a delegate "
                    " which does not have traits." % (
                        name, type(self))
                )

            daname2 = trait.delegate_attr_name(trait, self, daname)
            daname = daname2
            if delegate.itrait_dict is not None:
                trait = delegate.itrait_dict.get(daname, None)
            else:
                trait = delegate.ctrait_dict.get(daname, None)
            if trait is None:
                trait = delegate.get_prefix_trait(daname2, 0)
                if trait is None:
                    raise DelegationError(
                        "The '%.400s' attribute of a '%.50s' object delegates "
                        " to an attribute which is not a defined trait." % (
                            name, type(self))
                    )

            if not PyObject_TypeCheck(trait, ctrait_type):
                raise TraitError('Non-trait found in a trait dictionnary.')

            i += 1
            if i >= 100:
                raise DelegationError(
                    "Delegation recursion limit exceeded while getting the "
                    " definiton of '%.400s' trait of a '%0.5s' object." % (
                        name, type(self))
                )


# Assigns a value to a specified property trait attribute 
cdef object getattr_property0(cTrait trait, CHasTraits obj, object name):
    return trait.delegate_name()

cdef object getattr_property1(cTrait trait, CHasTraits obj, object name):
    return trait.delegate_name(obj)

cdef object getattr_property2(cTrait trait, CHasTraits obj, object name):
    return trait.delegate_name(obj, name)

cdef object getattr_property3(cTrait trait, CHasTraits obj, object name):
    return trait.delegate_name(obj, name, trait)

cdef trait_getattr getattr_property_handlers[4]
getattr_property_handlers[0] = getattr_property0
getattr_property_handlers[1] = getattr_property1
getattr_property_handlers[2] = getattr_property2
getattr_property_handlers[3] = getattr_property3

cdef int setattr_validate_property(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:

    cdef int result
    cdef object validated = traitd.validate(traitd, obj, name, value)
    if validated is not None:
        result = (<trait_setattr> traitd._post_setattr)(traito, traitd, obj, name, validated)
    return result

cdef void raise_delete_property_error(object obj, object name):
    raise TraitError("Cannot delete the '%.400s' property of '%.50s' object " % (obj, name))

cdef int setattr_property0(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:

    if value is None:
        raise_delete_property_error(obj, name)

    cdef object args = tuple()
    result = PyObject_Call(traitd.delegate_prefix, args, None)
    if result is None:
        return -1
    else:
        return 0

cdef int setattr_property1(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:

    if value is None:
        raise_delete_property_error(obj, name)

    cdef object args = (value)
    cdef object result = PyObject_Call(traitd.delegate_prefix, args, None)
    if result is None:
        return -1
    else:
        return 0

cdef int setattr_property2(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:

    if value is None:
        raise_delete_property_error(obj, name)

    cdef object args = (obj, value)
    cdef object result = PyObject_Call(traitd.delegate_prefix, args, None)
    if result is None:
        return -1
    else:
        return 0

cdef int setattr_property3(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:

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

cdef object default_value_for(cTrait trait, CHasTraits obj, str name):
    cdef object result, value, dv, kw, tuple_

    cdef int vtype = trait.default_value_type

    if vtype == 0 or vtype == 1:
        result = trait.internal_default_value
    elif vtype == 2:
        result = obj
    elif vtype == 3:
        return trait.internal_default_value[:]
    elif vtype == 4:
        return trait.internal_default_value.copy()
    elif vtype == 5:
        return TraitListObject(trait.handler, obj, name,
                          trait.internal_default_value)
    elif vtype == 6:
        return TraitDictObject(trait.handler, obj, name,
                          trait.internal_default_value)
    elif vtype == 7:
        dv = trait.internal_default_value
        return PyObject_Call(dv[0], dv[1], dv[2])
    elif vtype == 8:
        tuple_ = (obj,)
        result = PyObject_Call(trait.internal_default_value, tuple, None)
        if result is not None and trait.validate is not NULL:
            value = trait.validate(trait, obj, name, result)
            return value
    elif vtype == 9:
        return TraitSetObject(trait.handler, obj, name,
                          trait.internal_default_value)

    return result


cdef object getattr_trait(cTrait trait, CHasTraits obj, object name):
    """ Returns the value assigned to a standard trait. """

    cdef int rc
    cdef object result
    cdef list tnotifiers, onotifiers

    if obj.obj_dict is None:
        obj.obj_dict = dict()

    if isinstance(name, str):
        result = default_value_for(trait, obj, name)
        obj.obj_dict[name] = result
        rc = 0
        if trait._post_setattr is not NULL and \
            (trait.flags & TRAIT_IS_MAPPED == 0):
            rc = trait._post_setattr(trait, obj, name, result)
        if rc == 0:
            tnotifiers = trait.notifiers
            onotifiers = obj.notifiers
            if has_notifiers(tnotifiers, onotifiers):
                rc = call_notifiers(tnotifiers, onotifiers, obj, name,
                                    Uninitialized, result)
        if rc == 0:
            return result
    else:
        raise TypeError('Attribute name must be a string')

cdef object getattr_event(cTrait trait, CHasTraits obj, object name):
    """  Returns the value assigned to an event trait Returns the value assigned to an event trait. """
    raise AttributeError(
        "The %.400s trait of a %.50s instance is an 'event', which is write"
        " only." % (name, type(obj))
    )

cdef object getattr_python(cTrait trait, CHasTraits obj, object name):
    """ Returns the value assigned to a standard Python attribute. """


    cdef PyObject* _obj = <PyObject*>obj
    cdef PyObject* _name = <PyObject*>name
    if _obj is NULL or _name is NULL:
        raise ValueError('Input cannot be null')
    print 'Calling ', obj, name
    cdef PyObject* result = PyObject_GenericGetAttr(_obj, _name)
    if result is NULL:
        raise_trait_error(trait, obj, name, None)

cdef object getattr_generic(cTrait trait, CHasTraits obj, object name):
    """ Returns the value assigned to a generic Python attribute. """

    cdef PyObject* _obj = <PyObject*>obj
    cdef PyObject* _name = <PyObject*>name
    if _obj is NULL or _name is NULL:
        raise ValueError('Input cannot be null')
    cdef PyObject* result = PyObject_GenericGetAttr(_obj, _name)
    if result is NULL:
        raise_trait_error(trait, obj, name, None)

cdef object getattr_delegate(cTrait trait, CHasTraits obj, object name):
    raise NotImplementedError('getattr delegate NOT IMPL.')

cdef object getattr_disallow(cTrait trait, CHasTraits obj, object name):
    raise NotImplementedError('getattr disallow NOT IMPL.')

cdef object getattr_constant(cTrait trait, CHasTraits obj, object name):
    raise NotImplementedError('getattr constant NOT IMPL.')

cdef bint has_notifiers(object tnotifiers, object onotifiers):
    if (tnotifiers is not None and len(tnotifiers) > 0) or \
        (onotifiers is not None and len(onotifiers) > 0):
        return 1
    else:
        return 0

cdef int call_notifiers(list tnotifiers, list onotifiers, CHasTraits obj, object name, object old_value, object new_value) except? -1:

    cdef int i, n, new_value_has_traits
    cdef object result, item, temp
    cdef int rc = 0

    new_value_has_traits = PyObject_TypeCheck(new_value, <PyTypeObject*>CHasTraits)

    cdef object arg_temp = None
    cdef object user_args = None
    cdef object args = (obj, name, old_value, new_value)

    # Do nothing if the user has explicitely requested no traits notifications
    # to be sent.
    if obj.flags & HASTRAITS_NO_NOTIFY:
        return rc
    else:
        if _trait_notification_handler != None:
            user_args = (arg_temp, args)

        for notifiers in [tnotifiers, onotifiers]:
            if notifiers is not None:
                n = len(notifiers)
                temp = notifiers[:]
                for i in xrange(n):
                    if new_value_has_traits and ((<CHasTraits>new_value).flags & HASTRAITS_VETO_NOTIFY):
                        return rc
                    if _trait_notification_handler != None and user_args is not None:
                        arg_temp = temp[i]
                        user_args[0] = arg_temp
                        result = PyObject_Call(_trait_notification_handler, user_args, None)
                    else:
                        result = temp[i](*args)



cdef int setattr_trait(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:
    """ Assigns a value to a specified normal trait attribute. """

    print 'setattr_trait'

    cdef object object_dict = obj.obj_dict
    cdef int changed = traitd.flags & TRAIT_NO_VALUE_TEST

    # This block is value == NULL in C. Do we really have calls to this
    # function with a NULL pointer?
    #if value is None:
    #    if object_dict is None:
    #        return 0
    #
    #    if PyString_Check(name):
    #        old_value = object_dict[name]
    #
    #        del object_dict[name]
    #
    #        # notify
    #        rc = 0
    #        if obj.flags & HASTRAITS_NO_NOTIFY == 0:
    #            tnotifiers = traito.notifiers
    #            onotifiers = obj.notifiers
    #            if tnotifiers is not None or onotifiers is not None:
    #                value = traito.getattr(traito, obj, name)
    #                if value is None:
    #                    return -1
    #
    #                if not changed:
    #                    changed = old_value != value
    #                    if changed and (traitd.flags & TRAIT_OBJECT_IDENTITY == 0):
    #                        changed = old_value == value
    #
    #                if changed:
    #                    if traitd._post_setattr is not NULL:
    #                        rc = traitd._post_setattr(traitd, obj, name, value)
    #                    if rc ==0 and has_notifiers(tnotifiers, onotifiers):
    #                        rc = call_notifiers(tnotifiers, onotifiers, obj, name, old_value, value)
    #
    #        return rc
    #    # FIXME: add support for unicode 
    #
    #else:

    original_value = value
    # If the object's value is Undefined, then do not call the validate
    # method (as the object's value has not yet been set).
    if traitd.validate is not NULL and value is not Undefined:
        value = traitd.validate(traitd, obj, name, value)
        print 'value is after validate ', value
    if obj.obj_dict is None:
        obj.obj_dict = {}
    # FIXME: support unicode
    if not PyString_Check(name):
        raise ValueError('Attribute name must be a string.')

    if traitd.flags & TRAIT_SETATTR_ORIGINAL_VALUE:
        new_value = original_value
    else:
        new_value = value
    old_value = None

    tnotifiers = traito.notifiers
    onotifiers = obj.notifiers
    do_notifiers = has_notifiers(tnotifiers, onotifiers)
    post_setattr = traitd.post_setattr

    if post_setattr is not None or do_notifiers:
        old_value = obj.obj_dict.get(name, None)
        if old_value is None:
            if traitd != traito:
                old_value = traito.getattr(traito, obj, name)
            else:
                old_value = default_value_for(traitd, obj, name)
        if not changed:
            changed = old_value != value
            flag_check = (traitd.flags & TRAIT_OBJECT_IDENTITY) == 0
            if changed and flag_check:
                changed = PyObject_RichCompareBool(old_value, value, Py_NE)
                if changed == -1:
                    PyErr_Clear()

    try:
        obj.obj_dict[name] = new_value
    except KeyError:
        raise AttributeError(name)

    rc = 0

    print 'Changed ? ', changed, post_setattr
    if changed:
        if post_setattr is not None:
            flag_check = traitd.flags & TRAIT_POST_SETATTR_ORIGINAL_VALUE
            post_value = original_value if flag_check else value
            rc = post_setattr(obj, name, post_value)
        if rc == 0 and do_notifiers:
            rc = call_notifiers(tnotifiers, onotifiers, obj, name, old_value, new_value)

    return rc

cdef int setattr_python(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:
    cdef int rc

    if value is not None:
        if obj.obj_dict is None:
            obj.obj_dict = {}

        obj.obj_dict[name] = value

        return 0

    if obj.obj_dict is not None:
        if name not in obj.obj_dict:
            raise AttributeError('Unknown attribute %s in %s' % (name, obj))

    raise AttributeError('Unknown attribute %s in %s' % (name, obj))

cdef int setattr_event(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:

    cdef int rc = 0
    cdef list tnotifiers, onotifiers

    if value is not None:
        if traitd.validate is not NULL:
            value = traitd.validate(traitd, obj, name, value)
            if value is None:
                return -1

        tnotifiers = traito.notifiers
        onotifiers = obj.notifiers

        if has_notifiers(tnotifiers, onotifiers):
            rc = call_notifiers(tnotifiers, onotifiers, obj, name,
                                Undefined, value)
    return rc


cdef int setattr_delegate(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:
    raise NotImplementedError('No support for delegate')

cdef int setattr_dissalow(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:
    raise NotImplementedError('No support for dissalow')

cdef int setattr_readonly(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:
    raise NotImplementedError('No support for readonly')

cdef int setattr_constant(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:
    raise NotImplementedError('No support for constant')

cdef int setattr_generic(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value) except? -1:
    raise NotImplementedError('No support for generic')


cdef trait_validate setattr_validate_handlers[4]
setattr_validate_handlers[0] = setattr_validate0
setattr_validate_handlers[1] = setattr_validate1
setattr_validate_handlers[2] = setattr_validate2
setattr_validate_handlers[3] = setattr_validate3

cdef trait_getattr getattr_handlers[13]
getattr_handlers[0] = getattr_trait
getattr_handlers[1] = getattr_python
getattr_handlers[2] = getattr_event
getattr_handlers[3] = getattr_delegate
getattr_handlers[4] = getattr_event
getattr_handlers[5] = getattr_disallow
getattr_handlers[6] = getattr_trait
getattr_handlers[7] = getattr_constant
getattr_handlers[8] = getattr_generic
getattr_handlers[9] = getattr_property0
getattr_handlers[10] = getattr_property1
getattr_handlers[11] = getattr_property2
getattr_handlers[12] = getattr_property3

cdef trait_setattr setattr_handlers[13]
setattr_handlers[0] = setattr_trait
setattr_handlers[1] = setattr_python
setattr_handlers[2] = setattr_event
setattr_handlers[3] = setattr_delegate
setattr_handlers[4] = setattr_event
setattr_handlers[5] = setattr_dissalow
setattr_handlers[6] = setattr_readonly
setattr_handlers[7] = setattr_constant
setattr_handlers[8] = setattr_generic
setattr_handlers[9] = setattr_property0
setattr_handlers[10] = setattr_property1
setattr_handlers[11] = setattr_property2
setattr_handlers[12] = setattr_property3

cdef object delegate_attr_name_name(cTrait trait, CHasTraits obj, object name):
    return name

cdef object delegate_attr_name_prefix(cTrait trait, CHasTraits obj, object name):
    return trait.delegate_prefix

cdef object delegate_attr_name_prefix_name(cTrait trait, CHasTraits obj, object name):

   # TODO: if needed, could be optimized for speed ...
   return '%s%s' % (trait.delegate_prefix, name)

cdef object delegate_attr_name_class_name(cTrait trait, CHasTraits obj, object name):

    prefix = getattr(obj.__class, class_prefix, None)
    if prefix is None:
        return name
    else:
        return '%s%s' % (prefix, name)

cdef delegate_attr_name_func delegate_attr_name_handlers[4]
delegate_attr_name_handlers[0] = delegate_attr_name_name
delegate_attr_name_handlers[1] = delegate_attr_name_prefix
delegate_attr_name_handlers[2] = delegate_attr_name_prefix_name
delegate_attr_name_handlers[3] = delegate_attr_name_class_name

cdef object call_class(object class_, cTrait trait, CHasTraits obj, object name, object value):

    cdef object result
    cdef object args = (trait.handler, obj, name, value)
    result = PyObject_Call(class_, args, None)
    return result

cdef int has_value_for(CHasTraits obj, str name):
    """ Returns whether an object's '__dict__' value is defined or not. """
    if obj.obj_dict.has_key(name):
        return 1
    else:
        return 0

cdef class cTrait:

    cdef int flags # Flags bits
    cdef trait_getattr getattr
    cdef trait_setattr setattr
    cdef trait_post_setattr _post_setattr
    cdef object py_post_setattr # Pyton=based post 'setattr' handler
    cdef trait_validate validate
    cdef object py_validate # Python-based validate value handler
    cdef int default_value_type # Type of default value: see the default_value_for function
    cdef object internal_default_value # Default value for Trait
    cdef object delegate_name # Optional delegate name (also used for property get)
    cdef object delegate_prefix # Optional delate prefix (also usef for property set)
    cdef delegate_attr_name_func delegate_attr_name # Optional routirne to return the computed delegate attribute name
    cdef list notifiers # Optional list of notification handlers
    cdef object _handler # Associated trait handler object 
    cdef dict obj_dict # Standard Python object dict

    def __init__(self, int kind):

        if kind >= 0 and kind <= 8:
            self.getattr = getattr_handlers[kind]
            self.setattr = setattr_handlers[kind]

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
        print 'Set default value to ', value_type, value
        if value_type is None and value is None:
            if self.internal_default_value is None:
                return None
            else:
                return (self.default_value_type, self.internal_default_value)
        if value_type < 0 or value_type > 9:
            raise ValueError('The default value type must be 0..9 but %s was'
                             ' specified' % value_type)
        self.default_value_type = value_type
        self.internal_default_value = value

    def set_validate(self, validate):
        """ Sets the value of the 'validate' field of a CTrait instance. """
        cdef int n, kind

        if PyCallable_Check(validate):
            kind = 14
        elif PyTuple_CheckExact(validate):
            n = len(validate)
            if n > 0:
                kind = validate[0]
                if kind == 0: # Type check
                    if n == 2 and PyType_Check(validate[-1]) or validate[1] is None:
                        pass
                    else:
                        raise ValueError('The argument must be a tuple or callable.')
                elif kind == 1: # Instance check
                    if n <=3 and (n == 2 or  validate[1]  is None):
                        pass
                    else:
                        raise ValueError('The argument must be a tuple or callable.')
                elif kind == 2: # Self type check
                    if n == 1 or (n ==2 and validate[1] is None):
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
                elif kind == 4: # Floating point range check
                    if n ==4:
                        v1 = validate[1]
                        v2 = validate[2]
                        v3 = validate[3]
                        if (v1 is None or isinstance(v1, float)) and \
                           (v2 is None or isinstance(v2, float)) and \
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
                elif kind == 6:  # Mapped item check
                    if  n == 2 :
                        if PyDict_Check(validate[1]):
                            pass
                        else:
                            raise ValueError('The argument must be a tuple or callable.')
                elif kind == 7: # TraitComplex item check
                    if n == 2:
                        v1 = validate[1]
                        if not isinstance(v1, tuple):
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
        self._post_setattr = trait._post_setattr
        self.py_post_setattr = trait.py_post_setattr
        self.validate = trait.validate
        self.py_validate = trait.py_validate
        self.default_value_type = trait.default_value_type
        self.internal_default_value = trait.internal_default_value
        self.delegate_name = trait.delegate_name
        self.delegate_prefix = trait.delegate_prefix
        self.delegate_attr_name = trait.delegate_attr_name
        self._handler = trait._handler

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
                self._post_setattr = <trait_post_setattr> setattr_property_handlers[set_n]
                self.validate = setattr_validate_handlers[validate_n]
            else:
                self.setattr = setattr_property_handlers[set_n]

            self.delegate_name = get
            self.delegate_prefix = set_
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

    def __getattr__(self, name):
        """ Handles the 'getattr' operation on a 'CHasTraits' instance . """
        print '__getattr__ for ', name
        cdef PyObject* value = PyObject_GenericGetAttr(<PyObject*>self, <PyObject*>name)
        if value is not NULL:
            return <object>value
        else:
            PyErr_Clear()

        return None

    def default_value_for(self, CHasTraits obj, object name):
        """ Gets the default value of a CTrait instance for a specified object and trait
            name.

        """

        print 'CTrait default value for ...'
        if self.flags & TRAIT_PROPERTY and has_value_for(<CHasTraits>obj, name):
            return default_value_for(self, obj, name)

        return self.getattr(self, obj, name)

    property __dict__:
        def __get__(self):
            if self.obj_dict is None:
                self.obj_dict = {}
            return self.obj_dict

        def __set__(self, value):
            if not isinstance(value, dict):
                raise ValueError('__dict__ maust be a dictionary. ')
            self.obj_dict = value

    property handler:
        def __get__(self):
            return self._handler
        def __set__(self, value):
            self._handler = value

    property post_setattr:
        def __get__(self):
            return self.py_post_setattr
        def __set__(self, value):
            if not PyCallable_Check(value):
                raise ValueError('The assigned value must be a callable.')
            self._post_setattr = post_setattr_trait_python
            self.py_post_setattr = value

    def delegate(self, str name, str prefix, int prefix_type, int modify_delegate):

        if modify_delegate:
            self.flags |= TRAIT_MODIFY_DELEGATE
        else:
            self.flags &= ~TRAIT_MODIFY_DELEGATE

        self.delegate_name = name
        self.delegate_prefix = prefix

        if prefix_type < 0 or prefix_type > 3:
            prefix_type = 0

        self.delegate_attr_name = delegate_attr_name_handlers[prefix_type]

    def __setstate__(self, state):
        raise NotImplementedError('Work in progress')

    def __getstate__(self):
        raise NotImplementedError('Work in progress')

    def get_validate(self):
        raise NotImplementedError('Work in progress')

    def rich_comparison(self, rich_comparison_boolean):
        raise NotImplementedError('Work in progress')

    def comparison_mode(self, comparison_mode_enum):
        raise NotImplementedError('Work in progress')

    def value_allowed(self, value_allowed_boolean):
        raise NotImplementedError('Work in progress')

    def value_property(value_trait_boolean):
        raise NotImplementedError('Work in progress')

    def post_setattr_original_value(original_value_boolean):
        raise NotImplementedError('Work in progress')

    def cast(self, value):
        raise NotImplementedError('Work in progress')


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

def traits_inited(value):
    raise NotImplementedError('traits_inited method not yet implemented.')

def _trait(name, instance):
    raise NotImplementedError('_trait method not yet implemented.')

def _value_class(TraitValue_):
    global TraitValue
    TraitValue = TraitValue_

cdef void trait_clone(cTrait trait1, cTrait trait2):
    pass

cdef int is_trait_property(cTrait trait):
    return trait.flags & TRAIT_VALUE_PROPERTY != 0


