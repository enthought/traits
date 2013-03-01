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

    print 'VALIDATONG TRAIT TYPE'
    cdef object type_info = trait.py_validate
    cdef int kind = PyTuple_GET_SIZE(type_info)

    if (kind == 3 and value == None) or \
        PyObject_TypeCheck(
            value, <PyTypeObject*> PyTuple_GET_ITEM(type_info, kind -1)):
        return value
    else:
        print 'Raising trait error'
        trait.handler.error(obj, name, value)

cdef object validate_trait_instance(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_self_type(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_int(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_float(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_enum(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_map(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_complex(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_tuple(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_prefix_map(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_coerce_type(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_cast_type(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_function(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_python(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

cdef object validate_trait_adapt(cTrait trait, CHasTraits obj, object name, object value):
    raise NotImplementedError()

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
            if new_value is None:
                return -1
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

        print 'get_prefix_trait ', name, is_set
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

        print 'get_trait ', name, instance
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



    cdef int setattr_value(self, cTrait trait, str name, object value):
        """ Assigns a special TraitValue to a specified trait attribute. """

        print 'setattr value ', trait, name, value

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
        self._internal_setattr(name, value)

    cdef int _internal_setattr(self, str name, object value):
        """  Handles the 'setattr' operation on a 'CHasTraits' instance. """

        # Equivalent of the has_traits_settro function

        print '_internal_setattr ', name, value
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
                    return -1
                else:
                    trait = prefix_trait

        if (trait.flags & TRAIT_VALUE_ALLOWED != 0) and isinstance(value, TraitValue):
            return self.setattr_value(trait, name, value)
        else:
            print 'Returning trait setattr'
            return trait.setattr(trait, trait, self, name, value)

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
        result = (<trait_setattr> traitd._post_setattr)(traito, traitd, obj, name, validated)
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
        return call_class(TraitListObject, trait, obj, name,
                          trait.internal_default_value)
    elif vtype == 6:
        return call_class(TraitDictObject, trait, obj, name,
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
        return call_class(TraitSetObject, trait, obj, name,
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
        if result is not None:
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

cdef object getattr_trait_not_implemented(cTrait trait, CHasTraits obj, object name):
    raise NotImplementedError()


cdef bint has_notifiers(object tnotifiers, object onotifiers):
    if (tnotifiers is not None and len(tnotifiers) > 0) or \
        (onotifiers is not None and len(onotifiers) > 0):
        return 1
    else: return 0

cdef int call_notifiers(list tnotifiers, list onotifiers, CHasTraits obj, object name, object old_value, object new_value):

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
                        result = PyObject_Call(temp[i], args, None)



cdef int setattr_trait(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value):

    print 'SETATTR TRAIT'
    cdef object object_dict = obj.obj_dict
    cdef int changed = traitd.flags & TRAIT_NO_VALUE_TEST

    if value is None:
        if object_dict is None:
            return 0

        if isinstance(name ,str):
            old_value = object_dict[name]
            if old_value is None:
                return 0

            del object_dict[name]

            rc = 0
            if obj.flags & HASTRAITS_NO_NOTIFY == 0:
                tnotifiers = traito.notifiers
                onotifiers = obj.notifiers
                if tnotifiers is not None or onotifiers is not None:
                    value = traito.getattr(traito, obj, name)
                    if value is None:
                        return -1

                    if not changed:
                        changed = old_value != value
                        if changed and (traitd.flags & TRAIT_OBJECT_IDENTITY == 0):
                            changed = old_value == value

                    if changed:
                        if traitd._post_setattr is not NULL:
                            rc = traitd._post_setattr(traitd, obj, name, value)
                        if rc ==0 and has_notifiers(tnotifiers, onotifiers):
                            rc = call_notifiers(tnotifiers, onotifiers, obj, name, old_value, value)

            return rc
        # FIXME: add support for unicode 

    else:
        original_value = value
        # If the object's value is Undefined, then do not call the validate
        # method (as the object's value has not yet been set).
        if traitd.validate is not NULL and value is not Undefined:
            value = traitd.validate(traitd, obj, name, value)
            if value is None:
                return -1
        if obj.obj_dict is None:
            obj.obj_dict = {}
        # FIXME: support unicode
        if not isinstance(name, str):
            # FIXME: check what invalid_attribute_error function does
            raise ValueError('Attribute must be a str.')

        if traitd.flags & TRAIT_SETATTR_ORIGINAL_VALUE:
            new_value = original_value
        else:
            new_value = value
        old_value = None

        tnotifiers = traito.notifiers
        onotifiers = obj.notifiers
        do_notifiers = has_notifiers(tnotifiers, onotifiers)
        post_setattr = traitd.post_setattr

        if post_setattr is not None and do_notifiers:
            old_value = obj.obj_dict.get(name, None)
            if old_value is None:
                if traitd != traito:
                    old_value = traito.getattr(traito, obj, name)
                else:
                    old_value = default_value_for(traitd, obj, name)
                if old_value is None:
                    return -1
            else:
                if not changed:
                    changed = old_value != value
                    flag_check = (traitd.flags & TRAIT_OBJECT_IDENTITY) == 0
                    if changed and flag_check:
                        raise NotImplementedError()
                        #changed = PyObject_RichCompareBool(old_value, value, Py_NE)

        obj.obj_dict[name] = new_value

        rc = 0

        if changed:
            if post_setattr is not None:
                flag_check = traitd.flags & TRAIT_POST_SETATTR_ORIGINAL_VALUE
                post_value = original_value if flag_check else value
                rc = post_setattr(traitd, obj, name, post_value)
                if rc == 0 and do_notifiers:
                    rc = call_notifiers(tnotifiers, onotifiers, obj, name, old_value, new_value)

        return rc

cdef int setattr_trait_not_implemented(cTrait traito, cTrait traitd, CHasTraits obj, object name, object value):
    pass

cdef trait_validate setattr_validate_handlers[4]
setattr_validate_handlers[0] = setattr_validate0
setattr_validate_handlers[1] = setattr_validate1
setattr_validate_handlers[2] = setattr_validate2
setattr_validate_handlers[3] = setattr_validate3

cdef trait_getattr getattr_handlers[13]
getattr_handlers[0] = getattr_trait
getattr_handlers[1] = getattr_trait_not_implemented
getattr_handlers[2] = getattr_trait_not_implemented
getattr_handlers[3] = getattr_trait_not_implemented
getattr_handlers[4] = getattr_trait_not_implemented
getattr_handlers[5] = getattr_trait_not_implemented
getattr_handlers[6] = getattr_trait_not_implemented
getattr_handlers[7] = getattr_trait_not_implemented
getattr_handlers[8] = getattr_trait_not_implemented
getattr_handlers[9] = getattr_trait_not_implemented
getattr_handlers[10] = getattr_trait_not_implemented
getattr_handlers[11] = getattr_trait_not_implemented
getattr_handlers[12] = getattr_trait_not_implemented
#getattr_python,    getattr_event,  getattr_delegate,
#    getattr_event,     getattr_disallow,  getattr_trait,  getattr_constant,
#    getattr_generic,
#/*  The following entries are used by the __getstate__ method: */
#    getattr_property0, getattr_property1, getattr_property2,
#    getattr_property3,
#/*  End of __getstate__ method entries */

cdef trait_setattr setattr_handlers[13]
setattr_handlers[0] = setattr_trait
setattr_handlers[1] = setattr_trait_not_implemented
setattr_handlers[2] = setattr_trait_not_implemented
setattr_handlers[3] = setattr_trait_not_implemented
setattr_handlers[4] = setattr_trait_not_implemented
setattr_handlers[5] = setattr_trait_not_implemented
setattr_handlers[6] = setattr_trait_not_implemented
setattr_handlers[7] = setattr_trait_not_implemented
setattr_handlers[8] = setattr_trait_not_implemented
setattr_handlers[9] = setattr_trait_not_implemented
setattr_handlers[10] = setattr_trait_not_implemented
setattr_handlers[11] = setattr_trait_not_implemented
setattr_handlers[12] = setattr_trait_not_implemented
#setattr_python,    setattr_event,     setattr_delegate,
#    setattr_event,     setattr_disallow,  setattr_readonly,  setattr_constant,
#    setattr_generic,
#/*  The following entries are used by the __getstate__ method: */
#    setattr_property0, setattr_property1, setattr_property2, setattr_property3,
#/*  End of __setstate__ method entries */


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
    cdef object py_validate # Python-based validat value handler
    cdef int default_value_type # Type of default value: see the default_value_for function
    cdef object internal_default_value # Default value for Trait
    cdef object delegate_name # Optional delegate name (also used for property get)
    cdef object delegate_prefix # Optional delate prefix (also usef for property set)
    cdef delegate_attr_name_func delegate_attr_name # Optional routirne to return the computed delegate attribute name
    cdef list notifiers # Optional list of notification handlers
    cdef object _handler # Associated trait handler object 
    cdef dict obj_dict # Standard Python object dict

    cdef public str instance_handler # ADDED BY DP
    cdef public object on_trait_change # ADDED BY DP
    cdef public object event # ADDED BY DP

    def __init__(self, int kind):

        if kind >= 0 and kind <= 8:
            print 'KIND ', kind
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
        if value_type is None and value is None:
            if self.internal_default_value is None:
                return None
            else:
                return (self.default_value_type, self.internal_default_value)
        if value_type < 0 and value_type > 9:
            raise ValueError('The default value type must be 0..9 but %s was'
                             ' specified' % value_type)
        self.value_type = value_type
        self.internal_default_value = value

    def set_validate(self, validate):
        """ Sets the value of the 'validate' field of a CTrait instance. """
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

    def __getattr__(self, name):
        print 'GETATTR cTRAIT ', name
        cdef PyObject* value = PyObject_GenericGetAttr(<PyObject*>self, <PyObject*>name)
        if value is not NULL:
            return <object>value

    def default_value_for(self, CHasTraits obj, object name):
        """ Gets the default value of a CTrait instance for a specified object and trait
            name.

        """

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

    def property(self, get, set, validate):
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


