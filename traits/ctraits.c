// (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
// All rights reserved.
//
// This software is provided without warranty under the terms of the BSD
// license included in LICENSE.txt and may be redistributed only under
// the conditions described in the aforementioned license. The license
// is also available online at http://www.enthought.com/licenses/BSD.txt
//
// Thanks for using Enthought open source!

/*-----------------------------------------------------------------------------
|  Includes:
+----------------------------------------------------------------------------*/

#include "Python.h"

/*-----------------------------------------------------------------------------
|  Constants:
+----------------------------------------------------------------------------*/

static PyObject *class_traits;    /* == "__class_traits__" */
static PyObject *listener_traits; /* == "__listener_traits__" */
static PyObject *editor_property; /* == "editor" */
static PyObject *class_prefix;    /* == "__prefix__" */
static PyObject *trait_added;     /* == "trait_added" */
static PyObject *Undefined;       /* Global 'Undefined' value */
static PyObject *Uninitialized;   /* Global 'Uninitialized' value */
static PyObject *TraitError;      /* TraitError exception */
static PyObject *DelegationError; /* DelegationError exception */
static PyObject *TraitListObject; /* TraitListObject class */
static PyObject *TraitSetObject;  /* TraitSetObject class */
static PyObject *TraitDictObject; /* TraitDictObject class */
static PyObject *adapt;           /* 'adapt' function */
static PyTypeObject *ctrait_type; /* Python-level CTrait type reference */

/*-----------------------------------------------------------------------------
|  Macro definitions:
+----------------------------------------------------------------------------*/

#define PyTrait_CheckExact(op) ((Py_TYPE(op)) == ctrait_type)

#define PyHasTraits_Check(op) PyObject_TypeCheck(op, &has_traits_type)

/* Notification related: */
#define has_notifiers(tnotifiers, onotifiers)                        \
    ((((tnotifiers) != NULL) && (PyList_GET_SIZE((tnotifiers)) > 0)) \
     || (((onotifiers) != NULL) && (PyList_GET_SIZE((onotifiers)) > 0)))

/*-----------------------------------------------------------------------------
|  Forward declarations:
+----------------------------------------------------------------------------*/

static PyTypeObject trait_type;
static PyTypeObject has_traits_type;

/*-----------------------------------------------------------------------------
|  'ctraits' module doc string:
+----------------------------------------------------------------------------*/

PyDoc_STRVAR(
    ctraits__doc__,
    "Fast base classes for HasTraits and CTrait.\n"
    "\n"
    "The ctraits module defines the CHasTraits and cTrait extension types\n"
    "that define the core performance-oriented portions of the Traits\n"
    "package. Users will rarely need to use this module directly. Instead,\n"
    "they should use the API-complete HasTraits and CTrait subclasses of \n"
    "CHasTraits and cTrait (respectively).\n"
);

/*-----------------------------------------------------------------------------
|  HasTraits behavior modification flags:
+----------------------------------------------------------------------------*/

/* Object has been initialized: */
#define HASTRAITS_INITED 0x00000001U

/* Do not send notifications when a trait changes value: */
#define HASTRAITS_NO_NOTIFY 0x00000002U

/* Requests that no event notifications be sent when this object is assigned to
   a trait: */
#define HASTRAITS_VETO_NOTIFY 0x00000004U

/*-----------------------------------------------------------------------------
|  'CHasTraits' instance definition:
|
|  Note: traits are normally stored in the type's dictionary, but are added to
|  the instance's traits dictionary 'trait_dict' when the traits are defined
|  dynamically or 'on_trait_change' is called on an instance of the trait.
|
|  All 'anytrait_changed' notification handlers are stored in the instance's
|  'notifiers' list.
+----------------------------------------------------------------------------*/

typedef struct {
    PyObject_HEAD              /* Standard Python object header */
    PyDictObject *ctrait_dict; /* Class traits dictionary */
    PyDictObject *itrait_dict; /* Instance traits dictionary */
    PyListObject *notifiers;   /* List of 'any trait changed' notification
                                  handlers */
    unsigned int flags;        /* Behavior modification flags */
    PyObject *obj_dict;        /* Object attribute dictionary ('__dict__') */
                               /* NOTE: 'obj_dict' field MUST be last field */
} has_traits_object;

static int
call_notifiers(
    PyListObject *, PyListObject *, has_traits_object *, PyObject *,
    PyObject *, PyObject *new_value);

/*-----------------------------------------------------------------------------
|  'CTrait' flag values:
+----------------------------------------------------------------------------*/

/* The trait is a Property: */
#define TRAIT_PROPERTY 0x00000001U

/* Should the delegate be modified (or the original object)? */
#define TRAIT_MODIFY_DELEGATE 0x00000002U

/* Make 'setattr' store the original unvalidated value */
#define TRAIT_SETATTR_ORIGINAL_VALUE 0x00000008U

/* Send the 'post_setattr' method the original unvalidated value */
#define TRAIT_POST_SETATTR_ORIGINAL_VALUE 0x00000010U

/* Does this trait have an associated 'mapped' trait? */
#define TRAIT_IS_MAPPED 0x00000080U

/* Mask for the comparison mode bits, which determine when
   notifications are emitted on trait assignment. */
#define TRAIT_COMPARISON_MODE_MASK 0x00000104U

/* Notify on every assignment. Corresponds to ComparisonMode.none. */
#define TRAIT_COMPARISON_MODE_NONE 0x00000100U

/* Notify if the new object "is not" the old one. Corresponds to
  ComparisonMode.identity. */
#define TRAIT_COMPARISON_MODE_IDENTITY 0x00000004U

/* Notify if the new object is not the old one, and is not equal to the old
   one. Corresponds to ComparisonMode.equality. */
#define TRAIT_COMPARISON_MODE_EQUALITY 0x00000000U

/*-----------------------------------------------------------------------------
| Default value type constants (see `default_value_for` method)
+----------------------------------------------------------------------------*/

/* The default_value of the trait is the default value */
#define CONSTANT_DEFAULT_VALUE 0

/* The default_value of the trait is Missing */
#define MISSING_DEFAULT_VALUE 1

/* The object containing the trait is the default value */
#define OBJECT_DEFAULT_VALUE 2

/* A new copy of the list specified by default_value is the default value */
#define LIST_COPY_DEFAULT_VALUE 3

/* A new copy of the dict specified by default_value is the default value */
#define DICT_COPY_DEFAULT_VALUE 4

/* A new instance of TraitListObject constructed using the default_value list
  is the default value */
#define TRAIT_LIST_OBJECT_DEFAULT_VALUE 5

/* A new instance of TraitDictObject constructed using the default_value dict
   is the default value */
#define TRAIT_DICT_OBJECT_DEFAULT_VALUE 6

/* The default_value is a tuple of the form: (*callable*, *args*, *kw*),
   where *callable* is a callable, *args* is a tuple, and *kw* is either a
   dictionary or None. The default value is the result obtained by invoking
  ``callable(\*args, \*\*kw)`` */
#define CALLABLE_AND_ARGS_DEFAULT_VALUE 7

/* The default_value is a callable. The default value is the result obtained
   by invoking *default_value*(*object*), where *object* is the object
   containing the trait. If the trait has a validate() method, the validate()
   method is also called to validate the result */
#define CALLABLE_DEFAULT_VALUE 8

/* A new instance of TraitSetObject constructed using the default_value set
   is the default value */
#define TRAIT_SET_OBJECT_DEFAULT_VALUE 9

/* Maximum legal value for default_value_type, for use in testing and
   validation. */
#define MAXIMUM_DEFAULT_VALUE_TYPE 9

/* The maximum value for comparison_mode. Valid values are between 0 and
   the maximum value. */
#define MAXIMUM_COMPARISON_MODE_VALUE 2

/*-----------------------------------------------------------------------------
|  'CTrait' instance definition:
+----------------------------------------------------------------------------*/

typedef struct _trait_object a_trait_object;
typedef PyObject *(*trait_getattr)(
    a_trait_object *, has_traits_object *, PyObject *);
typedef int (*trait_setattr)(
    a_trait_object *, a_trait_object *, has_traits_object *, PyObject *,
    PyObject *);
typedef int (*trait_post_setattr)(
    a_trait_object *, has_traits_object *, PyObject *, PyObject *);
typedef PyObject *(*trait_validate)(
    a_trait_object *, has_traits_object *, PyObject *, PyObject *);
typedef PyObject *(*delegate_attr_name_func)(
    a_trait_object *, has_traits_object *, PyObject *);

typedef struct _trait_object {
    PyObject_HEAD                    /* Standard Python object header */
    unsigned int flags;              /* Flag bits */
    trait_getattr getattr;           /* Get trait value handler */
    trait_setattr setattr;           /* Set trait value handler */
    trait_post_setattr post_setattr; /* Optional post 'setattr' handler */
    PyObject *py_post_setattr;       /* Python-based post 'setattr' handler */
    trait_validate validate;         /* Validate trait value handler */
    PyObject *py_validate;           /* Python-based validate value handler */
    int default_value_type;          /* Type of default value: see the
                                        'default_value_for' function */
    PyObject *default_value;         /* Default value for trait */
    PyObject *delegate_name;         /* Optional delegate name */
                                     /* Also used for 'property get' */
    PyObject *delegate_prefix;       /* Optional delegate prefix */
                                     /* Also used for 'property set' */
    delegate_attr_name_func delegate_attr_name; /* Optional routine to return*/
    /* the computed delegate attribute name */
    PyListObject *notifiers; /* Optional list of notification handlers */
    PyObject *handler;       /* Associated trait handler object */
                             /* NOTE: The 'obj_dict' field MUST be last */
    PyObject *obj_dict;      /* Standard Python object dictionary */
} trait_object;

/* Forward declarations: */
static void
trait_clone(trait_object *, trait_object *);

static PyObject *
has_traits_getattro(has_traits_object *obj, PyObject *name);

static int
has_traits_setattro(has_traits_object *obj, PyObject *name, PyObject *value);

static PyObject *
get_trait(has_traits_object *obj, PyObject *name, int instance);

static int
trait_property_changed(
    has_traits_object *obj, PyObject *name, PyObject *old_value,
    PyObject *new_value);

static int
setattr_event(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value);

static int
setattr_disallow(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value);

/*-----------------------------------------------------------------------------
|  Raise a TraitError:
+----------------------------------------------------------------------------*/

static PyObject *
raise_trait_error(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result;

    /* Clear any current exception. We are handling it by raising
     * a TraitError. */
    PyErr_Clear();

    result = PyObject_CallMethod(
        trait->handler, "error", "(OOO)", obj, name, value);
    Py_XDECREF(result);
    return NULL;
}

/*-----------------------------------------------------------------------------
|  Raise a fatal trait error:
+----------------------------------------------------------------------------*/

static int
fatal_trait_error(void)
{
    PyErr_SetString(TraitError, "Non-trait found in trait dictionary");

    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an "attribute is not a string" error:
+----------------------------------------------------------------------------*/

static int
invalid_attribute_error(PyObject *name)
{
    const char *fmt =
        "attribute name must be an instance of <type 'str'>. "
        "Got %R (%.200s).";

    PyErr_Format(PyExc_TypeError, fmt, name, Py_TYPE(name)->tp_name);

    return -1;
}


/*-----------------------------------------------------------------------------
|  Raise an "cant set items error" error:
+----------------------------------------------------------------------------*/

static PyObject *
cant_set_items_error(void)
{
    PyErr_SetString(TraitError, "Can not set a collection's '_items' trait.");

    return NULL;
}

/*-----------------------------------------------------------------------------
|  Raise an "invalid trait definition" error:
+----------------------------------------------------------------------------*/

static int
bad_trait_value_error(void)
{
    PyErr_SetString(
        TraitError,
        "Result of 'as_ctrait' method was not a 'CTraits' instance.");

    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an invalid delegate error:
+----------------------------------------------------------------------------*/

static int
bad_delegate_error(has_traits_object *obj, PyObject *name)
{
    if (!PyUnicode_Check(name)) {
        return invalid_attribute_error(name);
    }
    PyErr_Format(
        DelegationError,
        "The '%.400U' attribute of a '%.50s' object"
        " delegates to an attribute which is not a defined trait.",
        name, Py_TYPE(obj)->tp_name);
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an invalid delegate error:
+----------------------------------------------------------------------------*/

static int
bad_delegate_error2(has_traits_object *obj, PyObject *name)
{
    if (!PyUnicode_Check(name)) {
        return invalid_attribute_error(name);
    }

    PyErr_Format(
        DelegationError,
        "The '%.400U' attribute of a '%.50s' object"
        " has a delegate which does not have traits.",
        name, Py_TYPE(obj)->tp_name);
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise a delegation recursion error:
+----------------------------------------------------------------------------*/

static int
delegation_recursion_error(has_traits_object *obj, PyObject *name)
{
    if (!PyUnicode_Check(name)) {
        return invalid_attribute_error(name);
    }

    PyErr_Format(
        DelegationError,
        "Delegation recursion limit exceeded while setting"
        " the '%.400U' attribute of a '%.50s' object.",
        name, Py_TYPE(obj)->tp_name);
    return -1;
}

static int
delegation_recursion_error2(has_traits_object *obj, PyObject *name)
{
    if (!PyUnicode_Check(name)) {
        return invalid_attribute_error(name);
    }

    PyErr_Format(
        DelegationError,
        "Delegation recursion limit exceeded while getting"
        " the definition of the '%.400U' attribute of a '%.50s' object.",
        name, Py_TYPE(obj)->tp_name);
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an attempt to delete read-only attribute error:
+----------------------------------------------------------------------------*/

static int
delete_readonly_error(has_traits_object *obj, PyObject *name)
{
    if (!PyUnicode_Check(name)) {
        return invalid_attribute_error(name);
    }

    PyErr_Format(
        TraitError,
        "Cannot delete the read only '%.400U' attribute of a '%.50s' object.",
        name, Py_TYPE(obj)->tp_name);
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an attempt to set a read-only attribute error:
+----------------------------------------------------------------------------*/

static int
set_readonly_error(has_traits_object *obj, PyObject *name)
{
    if (!PyUnicode_Check(name)) {
        return invalid_attribute_error(name);
    }

    PyErr_Format(
        TraitError,
        "Cannot modify the read only '%.400U' attribute of a '%.50s' object.",
        name, Py_TYPE(obj)->tp_name);
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an attempt to set an undefined attribute error:
+----------------------------------------------------------------------------*/

static int
set_disallow_error(has_traits_object *obj, PyObject *name)
{
    if (!PyUnicode_Check(name)) {
        return invalid_attribute_error(name);
    }

    PyErr_Format(
        TraitError,
        "Cannot set the undefined '%.400U' attribute of a '%.50s' object.",
        name, Py_TYPE(obj)->tp_name);
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an attempt to delete a property error:
+----------------------------------------------------------------------------*/

static int
set_delete_property_error(has_traits_object *obj, PyObject *name)
{
    if (!PyUnicode_Check(name)) {
        return invalid_attribute_error(name);
    }

    PyErr_Format(
        TraitError, "Cannot delete the '%.400U' property of a '%.50s' object.",
        name, Py_TYPE(obj)->tp_name);
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an undefined attribute error:
+----------------------------------------------------------------------------*/

static void
unknown_attribute_error(has_traits_object *obj, PyObject *name)
{
    PyErr_Format(
        PyExc_AttributeError, "'%.50s' object has no attribute '%.400U'",
        Py_TYPE(obj)->tp_name, name);
}

/*-----------------------------------------------------------------------------
|  Raise a '__dict__' must be set to a dictionary error:
+----------------------------------------------------------------------------*/

static int
dictionary_error(void)
{
    PyErr_SetString(PyExc_TypeError, "__dict__ must be set to a dictionary.");

    return -1;
}

/*-----------------------------------------------------------------------------
|  Gets/Sets a possibly NULL (or callable) value:
+----------------------------------------------------------------------------*/

static PyObject *
get_value(PyObject *value)
{
    if (value == NULL) {
        value = Py_None;
    }
    Py_INCREF(value);
    return value;
}

static int
set_value(PyObject **field, PyObject *value)
{
    PyObject *old_value;

    /* Caution: don't DECREF the old field contents until *after* the new
       contents are assigned, else there's a possibility for external code
       (triggered by the DECREF) to see an invalid field value. */
    old_value = *field;
    Py_XINCREF(value);
    *field = value;
    Py_XDECREF(old_value);
    return 0;
}

/*-----------------------------------------------------------------------------
|  Gets the value of a flag on a cTrait object specified by a mask.
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_flag(trait_object *trait, int mask)
{
    if (trait->flags & mask) {
        Py_RETURN_TRUE;
    }
    else {
        Py_RETURN_FALSE;
    }
}

/*-----------------------------------------------------------------------------
|  Sets the value of a flag on a cTrait object specified by a mask.
+----------------------------------------------------------------------------*/

static int
set_trait_flag(trait_object *trait, int mask, PyObject *value)
{
    int flag = PyObject_IsTrue(value);

    if (flag == -1) {
        return -1;
    }

    if (flag) {
        trait->flags |= mask;
    }
    else {
        trait->flags &= ~mask;
    }

    return 0;
}

/*-----------------------------------------------------------------------------
|  Returns the result of calling a specified 'class' object with 1 argument:
+----------------------------------------------------------------------------*/

static PyObject *
call_class(
    PyObject *class, trait_object *trait, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    PyObject *result;
    PyObject *args;

    args = PyTuple_Pack(4, trait->handler, (PyObject *)obj, name, value);
    if (args == NULL) {
        return NULL;
    }
    result = PyObject_Call(class, args, NULL);
    Py_DECREF(args);
    return result;
}

/*-----------------------------------------------------------------------------
|  Attempts to get the value of a key in a 'known to be a dictionary' object:
+----------------------------------------------------------------------------*/

static PyObject *
dict_getitem(PyDictObject *dict, PyObject *key)
{
    assert(PyDict_Check(dict));
    return PyDict_GetItem((PyObject *)dict, key);
}

/*-----------------------------------------------------------------------------
|  Gets the definition of the matching prefix based trait for a specified name:
|
|  - This should always return a trait definition unless a fatal Python error
|    occurs.
|  - The bulk of the work is delegated to a Python implemented method because
|    the implementation is complicated in C and does not need to be executed
|    very often relative to other operations.
|
| Note: returns a *borrowed* reference, to match dict_getitem.
+----------------------------------------------------------------------------*/

static trait_object *
get_prefix_trait(has_traits_object *obj, PyObject *name, int is_set)
{
    PyObject *trait = PyObject_CallMethod(
        (PyObject *)obj, "__prefix_trait__", "(Oi)", name, is_set);

    if (trait != NULL) {
        assert(obj->ctrait_dict != NULL);
        PyDict_SetItem((PyObject *)obj->ctrait_dict, name, trait);
        Py_DECREF(trait);

        if (has_traits_setattro(obj, trait_added, name) < 0) {
            return NULL;
        }

        trait = get_trait(obj, name, 0);
        /* We return a borrowed reference, to match dict_getitem. */
        Py_DECREF(trait);
    }

    return (trait_object *)trait;
}

/*-----------------------------------------------------------------------------
|  Handles the 'setattr' operation on a 'CHasTraits' instance:
+----------------------------------------------------------------------------*/

static int
has_traits_setattro(has_traits_object *obj, PyObject *name, PyObject *value)
{
    trait_object *trait;

    if ((obj->itrait_dict == NULL)
        || ((trait = (trait_object *)dict_getitem(obj->itrait_dict, name))
            == NULL)) {
        trait = (trait_object *)dict_getitem(obj->ctrait_dict, name);
        if ((trait == NULL)
            && ((trait = get_prefix_trait(obj, name, 1)) == NULL)) {
            return -1;
        }
    }

    return trait->setattr(trait, trait, obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Allocates a CTrait instance:
+----------------------------------------------------------------------------*/

PyObject *
has_traits_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    // Call PyBaseObject_Type.tp_new to do the actual construction.
    // This allows things like ABCMeta machinery to work correctly
    // which is implemented at the C level.
    PyObject *new_args, *new_kwds;
    has_traits_object *obj;

    new_args = PyTuple_New(0);
    if (new_args == NULL) {
        return NULL;
    }
    new_kwds = PyDict_New();
    if (new_kwds == NULL) {
        Py_DECREF(new_args);
        return NULL;
    }
    obj = (has_traits_object *)PyBaseObject_Type.tp_new(
        type, new_args, new_kwds);
    Py_DECREF(new_kwds);
    Py_DECREF(new_args);

    if (obj != NULL) {
        if (type->tp_dict == NULL) {
            PyErr_SetString(PyExc_RuntimeError, "No tp_dict");
            return NULL;
        }
        obj->ctrait_dict =
            (PyDictObject *)PyDict_GetItem(type->tp_dict, class_traits);
        if (obj->ctrait_dict == NULL) {
            PyErr_SetString(PyExc_RuntimeError, "No ctrait_dict");
            return NULL;
        }
        if (!PyDict_Check((PyObject *)obj->ctrait_dict)) {
            PyErr_SetString(PyExc_RuntimeError, "ctrait_dict not a dict");
            return NULL;
        }
        Py_INCREF(obj->ctrait_dict);
    }

    return (PyObject *)obj;
}

int
has_traits_init(PyObject *obj, PyObject *args, PyObject *kwds)
{
    PyObject *key;
    PyObject *value;
    int has_listeners;
    Py_ssize_t i = 0;

    /* Make sure no non-keyword arguments were specified: */
    if (!PyArg_ParseTuple(args, "")) {
        return -1;
    }

    /* Make sure all of the object's listeners have been set up: */
    has_listeners =
        (PyMapping_Size(PyDict_GetItem(Py_TYPE(obj)->tp_dict, listener_traits))
         > 0);
    if (has_listeners) {
        value = PyObject_CallMethod(obj, "_init_trait_listeners", NULL);
        if (value == NULL) {
            return -1;
        }
        Py_DECREF(value);
    }

    /* Make sure all of the object's observers have been set up: */
    value = PyObject_CallMethod(obj, "_init_trait_observers", NULL);
    if (value == NULL) {
        return -1;
    }
    Py_DECREF(value);

    /* Set any traits specified in the constructor: */
    if (kwds != NULL) {
        while (PyDict_Next(kwds, &i, &key, &value)) {
            if (has_traits_setattro((has_traits_object *)obj, key, value)
                == -1) {
                return -1;
            }
        }
    }

    /* Make sure all post constructor argument assignment listeners have been
       set up: */
    if (has_listeners) {
        value = PyObject_CallMethod(obj, "_post_init_trait_listeners", NULL);
        if (value == NULL) {
            return -1;
        }
        Py_DECREF(value);
    }

    /* Make sure all post constructor argument assignment observers have been
       set up: */
    value = PyObject_CallMethod(obj, "_post_init_trait_observers", NULL);
    if (value == NULL) {
        return -1;
    }
    Py_DECREF(value);

    /* Call the 'traits_init' method to finish up initialization: */
    value = PyObject_CallMethod(obj, "traits_init", NULL);
    if (value == NULL) {
        return -1;
    }
    Py_DECREF(value);

    /* Indicate that the object has finished being initialized: */
    ((has_traits_object *)obj)->flags |= HASTRAITS_INITED;

    return 0;
}

/*-----------------------------------------------------------------------------
|  Object clearing method:
+----------------------------------------------------------------------------*/

static int
has_traits_clear(has_traits_object *obj)
{
    Py_CLEAR(obj->ctrait_dict);
    Py_CLEAR(obj->itrait_dict);
    Py_CLEAR(obj->notifiers);
    Py_CLEAR(obj->obj_dict);

    return 0;
}

/*-----------------------------------------------------------------------------
|  Deallocates an unused 'CHasTraits' instance:
+----------------------------------------------------------------------------*/

static void
has_traits_dealloc(has_traits_object *obj)
{
    PyObject_GC_UnTrack(obj);
    Py_TRASHCAN_SAFE_BEGIN(obj);
    has_traits_clear(obj);
    Py_TYPE(obj)->tp_free((PyObject *)obj);
    Py_TRASHCAN_SAFE_END(obj);
}

/*-----------------------------------------------------------------------------
|  Garbage collector traversal method:
+----------------------------------------------------------------------------*/

static int
has_traits_traverse(has_traits_object *obj, visitproc visit, void *arg)
{
    Py_VISIT(obj->ctrait_dict);
    Py_VISIT(obj->itrait_dict);
    Py_VISIT(obj->notifiers);
    Py_VISIT(obj->obj_dict);

    return 0;
}

/*-----------------------------------------------------------------------------
|  Handles the 'getattr' operation on a 'CHasTraits' instance:
+----------------------------------------------------------------------------*/

static PyObject *
has_traits_getattro(has_traits_object *obj, PyObject *name)
{
    trait_object *trait;
    PyObject *value;
    /* The following is a performance hack to short-circuit the normal
       look-up when the value is in the object's dictionary.
*/
    PyDictObject *dict = (PyDictObject *)obj->obj_dict;

    if (dict != NULL) {
        assert(PyDict_Check(dict));

        if (!PyUnicode_Check(name)) {
            invalid_attribute_error(name);
            return NULL;
        }

        value = PyDict_GetItem((PyObject *)dict, name);
        if (value != NULL) {
            Py_INCREF(value);
            return value;
        }
    }
    /* End of performance hack */

    if (((obj->itrait_dict != NULL)
         && ((trait = (trait_object *)dict_getitem(obj->itrait_dict, name))
             != NULL))
        || ((trait = (trait_object *)dict_getitem(obj->ctrait_dict, name))
            != NULL)) {
        return trait->getattr(trait, obj, name);
    }

    /* Try normal Python attribute access, but if it fails with an
       AttributeError then get a prefix trait. */
    value = PyObject_GenericGetAttr((PyObject *)obj, name);
    if (value != NULL || !PyErr_ExceptionMatches(PyExc_AttributeError)) {
        return value;
    }

    PyErr_Clear();

    if ((trait = get_prefix_trait(obj, name, 0)) != NULL) {
        return trait->getattr(trait, obj, name);
    }

    return NULL;
}

/*-----------------------------------------------------------------------------
|  Returns (and optionally creates) a specified instance or class trait:
+----------------------------------------------------------------------------*/

static PyObject *
get_trait(has_traits_object *obj, PyObject *name, int instance)
{
    int i, n;
    PyDictObject *itrait_dict;
    trait_object *trait;
    trait_object *itrait;
    PyListObject *notifiers;
    PyListObject *inotifiers;
    PyObject *item;

    /* If there already is an instance specific version of the requested trait,
       then return it: */
    itrait_dict = obj->itrait_dict;
    if (itrait_dict != NULL) {
        trait = (trait_object *)dict_getitem(itrait_dict, name);
        if (trait != NULL) {
            assert(PyTrait_CheckExact(trait));
            Py_INCREF(trait);
            return (PyObject *)trait;
        }
    }

    /* If only an instance trait can be returned (but not created), then
       return None: */
    if (instance == 1) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    /* Otherwise, get the class specific version of the trait (creating a
       trait class version if necessary): */
    assert(obj->ctrait_dict != NULL);
    trait = (trait_object *)dict_getitem(obj->ctrait_dict, name);
    if (trait == NULL) {
        if (instance == 0) {
            Py_INCREF(Py_None);
            return Py_None;
        }
        if ((trait = get_prefix_trait(obj, name, 0)) == NULL) {
            return NULL;
        }
    }

    assert(PyTrait_CheckExact(trait));

    /* If an instance specific trait is not needed, return the class trait: */
    if (instance <= 0) {
        Py_INCREF(trait);
        return (PyObject *)trait;
    }

    /* Otherwise, create an instance trait dictionary if it does not exist: */
    if (itrait_dict == NULL) {
        obj->itrait_dict = itrait_dict = (PyDictObject *)PyDict_New();
        if (itrait_dict == NULL) {
            return NULL;
        }
    }

    /* Create a new instance trait and clone the class trait into it: */
    itrait = (trait_object *)PyType_GenericAlloc(ctrait_type, 0);
    trait_clone(itrait, trait);
    itrait->obj_dict = trait->obj_dict;
    Py_XINCREF(itrait->obj_dict);

    /* Copy the class trait's notifier list into the instance trait: */
    if ((notifiers = trait->notifiers) != NULL) {
        n = PyList_GET_SIZE(notifiers);
        itrait->notifiers = inotifiers = (PyListObject *)PyList_New(n);
        if (inotifiers == NULL) {
            return NULL;
        }

        for (i = 0; i < n; i++) {
            item = PyList_GET_ITEM(notifiers, i);
            PyList_SET_ITEM(inotifiers, i, item);
            Py_INCREF(item);
        }
    }

    /* Add the instance trait to the instance's trait dictionary and return
       the instance trait if successful: */
    if (PyDict_SetItem((PyObject *)itrait_dict, name, (PyObject *)itrait)
        >= 0) {
        return (PyObject *)itrait;
    }

    /* Otherwise, indicate that an error ocurred updating the dictionary: */
    return NULL;
}

/*-----------------------------------------------------------------------------
|  Returns (and optionally creates) a specified instance or class trait:
|
|  The legal values for 'instance' are:
|     2: Return instance trait (force creation if it does not exist)
|     1: Return existing instance trait (do not create)
|     0: Return existing instance or class trait (do not create)
|    -1: Return instance trait or force create class trait (i.e. prefix trait)
|    -2: Return the base trait (after all delegation has been resolved)
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_trait(has_traits_object *obj, PyObject *args)
{
    has_traits_object *delegate;
    has_traits_object *temp_delegate;
    trait_object *trait;
    PyObject *name;
    PyObject *daname;
    PyObject *daname2;
    PyObject *dict;
    int i, instance;

    /* Parse arguments, which specify the trait name and whether or not an
       instance specific version of the trait is needed or not: */
    if (!PyArg_ParseTuple(args, "Oi", &name, &instance)) {
        return NULL;
    }

    trait = (trait_object *)get_trait(obj, name, instance);
    if ((instance >= -1) || (trait == NULL)) {
        return (PyObject *)trait;
    }

    /* Follow the delegation chain until we find a non-delegated trait: */
    delegate = obj;
    Py_INCREF(delegate);

    daname = name;
    Py_INCREF(daname);
    for (i = 0;;) {
        if (trait->delegate_attr_name == NULL) {
            Py_DECREF(delegate);
            Py_DECREF(daname);
            return (PyObject *)trait;
        }

        dict = delegate->obj_dict;

        temp_delegate = NULL;
        if (dict != NULL) {
            temp_delegate = (has_traits_object *)PyDict_GetItem(
                dict, trait->delegate_name);
            /* PyDict_GetItem returns a borrowed reference,
               so we need to INCREF. */
            Py_XINCREF(temp_delegate);
        }
        if (temp_delegate == NULL) {
            /* has_traits_getattro returns a new reference,
               so no need to INCREF. */
            temp_delegate = (has_traits_object *)has_traits_getattro(
                delegate, trait->delegate_name);
        }
        if (temp_delegate == NULL) {
            break;
        }
        Py_DECREF(delegate);
        delegate = temp_delegate;

        if (!PyHasTraits_Check(delegate)) {
            bad_delegate_error2(obj, name);
            break;
        }

        daname2 = trait->delegate_attr_name(trait, obj, daname);
        Py_DECREF(daname);
        daname = daname2;
        Py_DECREF(trait);
        if (((delegate->itrait_dict == NULL)
             || ((trait = (trait_object *)dict_getitem(
                      delegate->itrait_dict, daname))
                 == NULL))
            && ((trait = (trait_object *)dict_getitem(
                     delegate->ctrait_dict, daname))
                == NULL)
            && ((trait = get_prefix_trait(delegate, daname2, 0)) == NULL)) {
            bad_delegate_error(obj, name);
            break;
        }

        if (Py_TYPE(trait) != ctrait_type) {
            fatal_trait_error();
            break;
        }

        if (++i >= 100) {
            delegation_recursion_error2(obj, name);
            break;
        }

        Py_INCREF(trait);
    }
    Py_DECREF(delegate);
    Py_DECREF(daname);

    return NULL;
}

/*-----------------------------------------------------------------------------
|  Calls notifiers when a trait 'property' is explicitly changed:
+----------------------------------------------------------------------------*/

static int
trait_property_changed(
    has_traits_object *obj, PyObject *name, PyObject *old_value,
    PyObject *new_value)
{
    trait_object *trait;
    PyListObject *tnotifiers;
    PyListObject *onotifiers;
    int null_new_value;
    int rc = 0;

    if ((trait = (trait_object *)get_trait(obj, name, -1)) == NULL) {
        return -1;
    }

    tnotifiers = trait->notifiers;
    onotifiers = obj->notifiers;
    Py_DECREF(trait);

    if (has_notifiers(tnotifiers, onotifiers)) {
        null_new_value = (new_value == NULL);
        if (null_new_value) {
            new_value = has_traits_getattro(obj, name);
            if (new_value == NULL) {
                return -1;
            }
        }

        rc = call_notifiers(
            tnotifiers, onotifiers, obj, name, old_value, new_value);

        if (null_new_value) {
            Py_DECREF(new_value);
        }
    }

    return rc;
}

/*-----------------------------------------------------------------------------
|  Calls notifiers when a trait 'property' is explicitly changed:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_property_changed(has_traits_object *obj, PyObject *args)
{
    PyObject *name, *old_value;
    PyObject *new_value = NULL;

    /* Parse arguments, which specify the name of the changed trait, the
       previous value, and the new value: */
    if (!PyArg_ParseTuple(args, "OO|O", &name, &old_value, &new_value)) {
        return NULL;
    }

    if (trait_property_changed(obj, name, old_value, new_value)) {
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Handles firing a traits 'xxx_items' event:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_items_event(has_traits_object *obj, PyObject *args)
{
    PyObject *name;
    PyObject *event_object;
    PyObject *event_trait;
    PyObject *result;
    trait_object *trait;
    int can_retry = 1;

    if (!PyArg_ParseTuple(args, "OOO", &name, &event_object, &event_trait)) {
        return NULL;
    }

    if (!PyTrait_CheckExact(event_trait)) {
        bad_trait_value_error();
        return NULL;
    }

    if (!PyUnicode_Check(name)) {
        invalid_attribute_error(name);
        return NULL;
    }
retry:
    if (((obj->itrait_dict == NULL)
         || ((trait = (trait_object *)dict_getitem(obj->itrait_dict, name))
             == NULL))
        && ((trait = (trait_object *)dict_getitem(obj->ctrait_dict, name))
            == NULL)) {
    add_trait:
        if (!can_retry) {
            return cant_set_items_error();
        }

        result = PyObject_CallMethod(
            (PyObject *)obj, "add_trait", "(OO)", name, event_trait);
        if (result == NULL) {
            return NULL;
        }

        Py_DECREF(result);
        can_retry = 0;
        goto retry;
    }

    if (trait->setattr == setattr_disallow) {
        goto add_trait;
    }

    if (trait->setattr(trait, trait, obj, name, event_object) < 0) {
        return NULL;
    }

    Py_INCREF(Py_None);

    return Py_None;
}

/*-----------------------------------------------------------------------------
| Reports whether trait change notifications are enabled for this object:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_notifications_enabled(
    has_traits_object *obj, PyObject *Py_UNUSED(ignored))
{
    if (obj->flags & HASTRAITS_NO_NOTIFY) {
        Py_RETURN_FALSE;
    }
    else {
        Py_RETURN_TRUE;
    }
}

/*-----------------------------------------------------------------------------
|  Enables/Disables trait change notification for the object:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_change_notify(has_traits_object *obj, PyObject *args)
{
    int enabled;

    /* Parse arguments, which specify the new trait notification
       enabled/disabled state: */
    if (!PyArg_ParseTuple(args, "p", &enabled)) {
        return NULL;
    }

    if (enabled) {
        obj->flags &= ~HASTRAITS_NO_NOTIFY;
    }
    else {
        obj->flags |= HASTRAITS_NO_NOTIFY;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
| Reports whether trait change notifications are enabled when this object is
| assigned to a trait:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_notifications_vetoed(
    has_traits_object *obj, PyObject *Py_UNUSED(ignored))
{
    if (obj->flags & HASTRAITS_VETO_NOTIFY) {
        Py_RETURN_TRUE;
    }
    else {
        Py_RETURN_FALSE;
    }
}

/*-----------------------------------------------------------------------------
|  Enables/Disables trait change notifications when this object is assigned to
|  a trait:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_veto_notify(has_traits_object *obj, PyObject *args)
{
    int enabled;

    /* Parse arguments, which specify the new trait notification veto
       enabled/disabled state: */
    if (!PyArg_ParseTuple(args, "p", &enabled)) {
        return NULL;
    }

    if (enabled) {
        obj->flags |= HASTRAITS_VETO_NOTIFY;
    }
    else {
        obj->flags &= ~HASTRAITS_VETO_NOTIFY;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  This method is called at the end of a HasTraits constructor and the
|  __setstate__ method to perform any final object initialization needed.
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_init(has_traits_object *obj, PyObject *Py_UNUSED(ignored))
{
    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Returns whether or not the object has finished being initialized.
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_inited(has_traits_object *obj, PyObject *Py_UNUSED(ignored))
{
    if (obj->flags & HASTRAITS_INITED) {
        Py_RETURN_TRUE;
    }
    else {
        Py_RETURN_FALSE;
    }
}


/*-----------------------------------------------------------------------------
|  Declare whether the has traits object has been initialized.
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_set_inited(has_traits_object *obj, PyObject *Py_UNUSED(ignored))
{
    obj->flags |= HASTRAITS_INITED;
    Py_RETURN_NONE;
}

/*-----------------------------------------------------------------------------
|  Returns the instance trait dictionary:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_instance_traits(
    has_traits_object *obj, PyObject *Py_UNUSED(ignored))
{
    if (obj->itrait_dict == NULL) {
        obj->itrait_dict = (PyDictObject *)PyDict_New();
    }

    Py_XINCREF(obj->itrait_dict);

    return (PyObject *)obj->itrait_dict;
}

/*-----------------------------------------------------------------------------
|  Returns the class trait dictionary:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_class_traits(has_traits_object *obj, PyObject *Py_UNUSED(ignored))
{
    PyObject *ctrait_dict;

    ctrait_dict = (PyObject *)obj->ctrait_dict;
    Py_INCREF(ctrait_dict);
    return ctrait_dict;
}

/*-----------------------------------------------------------------------------
|  Returns (and optionally creates) the anytrait 'notifiers' list:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_notifiers(has_traits_object *obj, PyObject *args)
{
    PyObject *result;
    PyObject *list;
    int force_create;

    if (!PyArg_ParseTuple(args, "p", &force_create)) {
        return NULL;
    }

    result = (PyObject *)obj->notifiers;
    if (result == NULL) {
        if (force_create) {
            list = PyList_New(0);
            if (list == NULL) {
                return NULL;
            }
            obj->notifiers = (PyListObject *)list;
            result = list;
        }
        else {
            result = Py_None;
        }
    }
    Py_INCREF(result);
    return result;
}

/*-----------------------------------------------------------------------------
|  Returns the object's instance dictionary:
+----------------------------------------------------------------------------*/

static PyObject *
get_has_traits_dict(has_traits_object *obj, void *closure)
{
    PyObject *obj_dict = obj->obj_dict;
    if (obj_dict == NULL) {
        obj->obj_dict = obj_dict = PyDict_New();
        if (obj_dict == NULL) {
            return NULL;
        }
    }
    Py_INCREF(obj_dict);

    return obj_dict;
}

/*-----------------------------------------------------------------------------
|  Sets the object's dictionary:
+----------------------------------------------------------------------------*/

static int
set_has_traits_dict(has_traits_object *obj, PyObject *value, void *closure)
{
    if (!PyDict_Check(value)) {
        return dictionary_error();
    }

    return set_value(&obj->obj_dict, value);
}

/*-----------------------------------------------------------------------------
|  'CHasTraits' instance methods:
+----------------------------------------------------------------------------*/

PyDoc_STRVAR(
    has_traits_trait_property_changed_doc,
    "trait_property_changed(name, old_value[, new_value])\n"
    "\n"
    "Call notifiers when a trait property value is explicitly changed.\n"
    "\n"
    "Calls trait and object notifiers for a property value change.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "name : str\n"
    "    Name of the trait whose value has changed\n"
    "old_value : any\n"
    "    Old value for this trait.\n"
    "new_value : any, optional\n"
    "    New value for this trait. If the new value is not provided,\n"
    "    it's looked up on the object.\n");

PyDoc_STRVAR(
    has_traits_trait_items_event_doc,
    "trait_items_event(name, event_object, event_trait)\n"
    "\n"
    "Fire an items event for changes to a Traits collection.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "name : str\n"
    "    Name of the item trait for which an event is being fired. (The name\n"
    "    will usually end in '_items'.)\n"
    "event_object : object\n"
    "    Object of type ``TraitListEvent``, ``TraitDictEvent`` or ``TraitSetEvent``\n"
    "    describing the changes to the underlying collection trait value.\n"
    "event_trait : CTrait\n"
    "    The items trait, of trait type ``Event``.\n");

PyDoc_STRVAR(
    has_traits__trait_change_notify_doc,
    "_trait_change_notify(enabled)\n"
    "\n"
    "Enable or disable trait change notifications for this object.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "enabled : bool\n"
    "    If true, enable trait change notifications for this object.\n"
    "    If false, disable trait change notifications for this object.\n");

PyDoc_STRVAR(
    has_traits__trait_veto_notify_doc,
    "_trait_veto_notify(vetoed)\n"
    "\n"
    "Enable or disable vetoing of trait change notifications by this object.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "vetoed : bool\n"
    "    If true, veto trait change notifications for this object: no\n"
    "    notifications will be issued when this object is assigned to\n"
    "    a trait. If false, notifications will be issued as usual.\n");

PyDoc_STRVAR(
    _trait_notifications_enabled_doc,
    "_trait_notifications_enabled()\n"
    "\n"
    "Report whether trait notifications are enabled for this object.\n"
    "\n"
    "Notifications can be enabled or disabled using the "
    "``_trait_change_notify``\n"
    "method. By default, notifications are enabled.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "enabled : bool\n"
    "    True if notifications are currently enabled for this object, else "
    "False.\n");

PyDoc_STRVAR(
    _trait_notifications_vetoed_doc,
    "_trait_notifications_vetoed()\n"
    "\n"
    "Report whether trait notifications are vetoed for this object.\n"
    "\n"
    "If trait notifications are vetoed for an object, assignment of that "
    "object\n"
    "to a trait will not generate a notification.\n"
    "This setting can be enabled or disabled using the "
    "``_trait_veto_notify``\n"
    "method. By default, notifications are not vetoed.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "vetoed : bool\n"
    "    True if notifications are currently vetoed for this object, else "
    "False.\n");

PyDoc_STRVAR(
    has_traits_traits_init_doc,
    "traits_init()\n"
    "\n"
    "Perform any final object initialization needed.\n"
    "\n"
    "For the CHasTraits base class, this method currently does nothing.\n");

PyDoc_STRVAR(
    has_traits_traits_inited_doc,
    "traits_inited()\n"
    "\n"
    "Get the initialization state of this object.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "initialized : bool\n"
    "    True if the object is initialized, else False.\n");

PyDoc_STRVAR(
    has_traits__trait_set_inited_doc,
    "_trait_set_inited()\n"
    "\n"
    "Declare that this object has been initialized.\n");

PyDoc_STRVAR(
    has_traits__trait_doc,
    "_trait(name, instance)\n"
    "\n"
    "Return and optionally create a specified instance or class trait.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "name : str\n"
    "    Name of the trait to be retrieved or created.\n"
    "instance : int\n"
    "    An integer determining the action to be taken. One of\n"
    "    {-2, -1, 0, 1, 2}. The meaning of the values is as follows:\n"
    "\n"
    "    2\n"
    "        Return an instance trait, creating a new trait if none exists.\n"
    "    1\n"
    "        Return an existing instance trait. Do not create a new trait.\n"
    "    0\n"
    "        Return an existing instance or class trait. Do not create a\n"
    "        new trait.\n"
    "    -1\n"
    "        Return an instance trait, or create a new class trait if no\n"
    "        instance trait exists.\n"
    "    -2\n"
    "        Return the base trait after resolving delegation.\n");

PyDoc_STRVAR(
    has_traits__instance_traits_doc,
    "_instance_traits()\n"
    "\n"
    "Return this object's instance traits dictionary.\n"
    "\n"
    "The object's instance traits dictionary is created if it doesn't\n"
    "already exist.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "instance_traits : dict\n"
    "    Dictionary mapping trait names to corresponding CTrait instances.\n");

PyDoc_STRVAR(
    has_traits__class_traits_doc,
    "_instance_traits()\n"
    "\n"
    "Return this object's class traits dictionary.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "class_traits : dict\n"
    "    Dictionary mapping trait names to corresponding CTrait instances.\n");

PyDoc_STRVAR(
    has_traits__notifiers_doc,
    "_notifiers(force_create)\n"
    "\n"
    "Return (and optionally create) the list of notifiers for this object.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "force_create : bool\n"
    "    Whether to automatically create the list of notifiers, if it\n"
    "    doesn't exist yet.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "notifiers : list of callables, or None\n"
    "    If the trait has no notifiers and *force_create* is false, return\n"
    "    None. Otherwise, return the list of notifiers for this object,\n"
    "    creating it first if necessary. Each notifier is a callable\n"
    "    accepting four arguments (object, trait_name, old, new).\n");

static PyMethodDef has_traits_methods[] = {
    {
        "trait_property_changed",
        (PyCFunction)_has_traits_property_changed,
        METH_VARARGS,
        has_traits_trait_property_changed_doc
    },
    {
        "trait_items_event",
        (PyCFunction)_has_traits_items_event,
        METH_VARARGS,
        has_traits_trait_items_event_doc
    },
    {
        "_trait_change_notify",
        (PyCFunction)_has_traits_change_notify,
        METH_VARARGS,
        has_traits__trait_change_notify_doc
    },
    {
        "_trait_notifications_enabled",
        (PyCFunction)_has_traits_notifications_enabled,
        METH_NOARGS,
        _trait_notifications_enabled_doc,
    },
    {
        "_trait_veto_notify",
        (PyCFunction)_has_traits_veto_notify,
        METH_VARARGS,
        has_traits__trait_veto_notify_doc
    },
    {
        "_trait_notifications_vetoed",
        (PyCFunction)_has_traits_notifications_vetoed,
        METH_NOARGS,
        _trait_notifications_vetoed_doc,
    },
    {
        "traits_init",
        (PyCFunction)_has_traits_init,
        METH_NOARGS,
        has_traits_traits_init_doc
    },
    {
        "traits_inited",
        (PyCFunction)_has_traits_inited,
        METH_VARARGS,
        has_traits_traits_inited_doc
    },
    {
        "_trait_set_inited",
        (PyCFunction)_has_traits_set_inited,
        METH_NOARGS,
        has_traits__trait_set_inited_doc
    },
    {
        "_trait",
        (PyCFunction)_has_traits_trait,
        METH_VARARGS,
        has_traits__trait_doc
    },
    {
        "_instance_traits",
        (PyCFunction)_has_traits_instance_traits,
        METH_NOARGS,
        has_traits__instance_traits_doc
    },
    {
        "_class_traits",
        (PyCFunction)_has_traits_class_traits,
        METH_NOARGS,
        has_traits__class_traits_doc
    },
    {
        "_notifiers",
        (PyCFunction)_has_traits_notifiers,
        METH_VARARGS,
        has_traits__notifiers_doc
    },
    {NULL, NULL},
};

/*-----------------------------------------------------------------------------
|  'CHasTraits' property definitions:
+----------------------------------------------------------------------------*/

static PyGetSetDef has_traits_properties[] = {
    {"__dict__", (getter)get_has_traits_dict, (setter)set_has_traits_dict},
    {0}};

/*-----------------------------------------------------------------------------
|  'CHasTraits' type definition:
+----------------------------------------------------------------------------*/

PyDoc_STRVAR(
    c_has_traits_doc,
    "Base class for HasTraits.\n"
    "\n"
    "The CHasTraits class is not intended to be instantiated directly.\n"
    "Instead, it serves as a base class for the HasTraits class.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "**traits : dict\n"
    "    Dictionary mapping trait names to trait values.\n"
);

static PyTypeObject has_traits_type = {
    PyVarObject_HEAD_INIT(NULL, 0) "traits.ctraits.CHasTraits",
    sizeof(has_traits_object),
    0,
    (destructor)has_traits_dealloc,    /* tp_dealloc */
    0,                                 /* tp_print */
    0,                                 /* tp_getattr */
    0,                                 /* tp_setattr */
    0,                                 /* tp_compare */
    0,                                 /* tp_repr */
    0,                                 /* tp_as_number */
    0,                                 /* tp_as_sequence */
    0,                                 /* tp_as_mapping */
    0,                                 /* tp_hash */
    0,                                 /* tp_call */
    0,                                 /* tp_str */
    (getattrofunc)has_traits_getattro, /* tp_getattro */
    (setattrofunc)has_traits_setattro, /* tp_setattro */
    0,                                 /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE
        | Py_TPFLAGS_HAVE_GC,                       /* tp_flags */
    c_has_traits_doc,                               /* tp_doc */
    (traverseproc)has_traits_traverse,              /* tp_traverse */
    (inquiry)has_traits_clear,                      /* tp_clear */
    0,                                              /* tp_richcompare */
    0,                                              /* tp_weaklistoffset */
    0,                                              /* tp_iter */
    0,                                              /* tp_iternext */
    has_traits_methods,                             /* tp_methods */
    0,                                              /* tp_members */
    has_traits_properties,                          /* tp_getset */
    0,                                              /* tp_base */
    0,                                              /* tp_dict */
    0,                                              /* tp_descr_get */
    0,                                              /* tp_descr_set */
    sizeof(has_traits_object) - sizeof(PyObject *), /* tp_dictoffset */
    has_traits_init,                                /* tp_init */
    0,                                              /* tp_alloc */
    has_traits_new                                  /* tp_new */
};

/*-----------------------------------------------------------------------------
|  Returns the default value associated with a specified trait:
+----------------------------------------------------------------------------*/

static PyObject *
default_value_for(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    PyObject *result = NULL, *value, *dv, *kw, *tuple;

    switch (trait->default_value_type) {
        case CONSTANT_DEFAULT_VALUE:
        case MISSING_DEFAULT_VALUE:
            result = trait->default_value;
            if (result == NULL) {
                result = Py_None;
            }
            Py_INCREF(result);
            break;
        case OBJECT_DEFAULT_VALUE:
            result = (PyObject *)obj;
            Py_INCREF(obj);
            break;
        case LIST_COPY_DEFAULT_VALUE:
            return PySequence_List(trait->default_value);
        case DICT_COPY_DEFAULT_VALUE:
            return PyDict_Copy(trait->default_value);
        case TRAIT_LIST_OBJECT_DEFAULT_VALUE:
            return call_class(
                TraitListObject, trait, obj, name, trait->default_value);
        case TRAIT_DICT_OBJECT_DEFAULT_VALUE:
            return call_class(
                TraitDictObject, trait, obj, name, trait->default_value);
        case CALLABLE_AND_ARGS_DEFAULT_VALUE:
            dv = trait->default_value;
            kw = PyTuple_GET_ITEM(dv, 2);
            if (kw == Py_None) {
                kw = NULL;
            }
            return PyObject_Call(
                PyTuple_GET_ITEM(dv, 0), PyTuple_GET_ITEM(dv, 1), kw);
        case CALLABLE_DEFAULT_VALUE:
            tuple = PyTuple_Pack(1, (PyObject *)obj);
            if (tuple == NULL) {
                return NULL;
            }
            result = PyObject_Call(trait->default_value, tuple, NULL);
            Py_DECREF(tuple);
            if ((result != NULL) && (trait->validate != NULL)) {
                value = trait->validate(trait, obj, name, result);
                if (trait->flags & TRAIT_SETATTR_ORIGINAL_VALUE) {
                    if (value == NULL) {
                        Py_DECREF(result);
                        return NULL;
                    }
                    Py_DECREF(value);
                    return result;
                }
                else {
                    Py_DECREF(result);
                    return value;
                }
            }
            break;
        case TRAIT_SET_OBJECT_DEFAULT_VALUE:
            return call_class(
                TraitSetObject, trait, obj, name, trait->default_value);
    }
    return result;
}

/*-----------------------------------------------------------------------------
|  Returns the value assigned to a standard Python attribute:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_python(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    return PyObject_GenericGetAttr((PyObject *)obj, name);
}

/*-----------------------------------------------------------------------------
|  Returns the value assigned to a generic Python attribute:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_generic(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    return PyObject_GenericGetAttr((PyObject *)obj, name);
}

/*-----------------------------------------------------------------------------
|  Returns the value assigned to an event trait:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_event(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    PyErr_Format(
        PyExc_AttributeError,
        "The %.400U"
        " trait of a %.50s instance is an 'event', which is write only.",
        name, Py_TYPE(obj)->tp_name);

    return NULL;
}

/*-----------------------------------------------------------------------------
|  Returns the value assigned to a standard trait:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_trait(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    int rc;
    PyListObject *tnotifiers;
    PyListObject *onotifiers;
    PyObject *result;
    PyObject *dict;

    /* This shouldn't ever happen. */
    if (!PyUnicode_Check(name)) {
        invalid_attribute_error(name);
        return NULL;
    }

    /* Create the object's __dict__ if it's not already present. */
    dict = obj->obj_dict;
    if (dict == NULL) {
        dict = PyDict_New();
        if (dict == NULL) {
            return NULL;
        }
        obj->obj_dict = dict;
    }

    /* Retrieve the default value, and set it in the dict. */
    result = default_value_for(trait, obj, name);
    if (result == NULL) {
        return NULL;
    }
    rc = PyDict_SetItem(dict, name, result);
    if (rc < 0) {
        goto error;
    }

    /* Call any post_setattr operations. */
    if (trait->post_setattr != NULL) {
        rc = trait->post_setattr(trait, obj, name, result);
        if (rc < 0) {
            goto error;
        }
    }

    /* Call notifiers. */
    tnotifiers = trait->notifiers;
    onotifiers = obj->notifiers;
    if (has_notifiers(tnotifiers, onotifiers)) {
        rc = call_notifiers(
            tnotifiers, onotifiers, obj, name, Uninitialized, result);
        if (rc < 0) {
            goto error;
        }
    }

    return result;

  error:
    Py_DECREF(result);
    return NULL;
}

/*-----------------------------------------------------------------------------
|  Returns the value assigned to a delegated trait:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_delegate(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    PyTypeObject *tp;
    PyObject *delegate_attr_name;
    PyObject *delegate;
    PyObject *result;
    PyObject *dict = obj->obj_dict;

    if ((dict == NULL)
        || ((delegate = PyDict_GetItem(dict, trait->delegate_name)) == NULL)) {
        // Handle the case when the delegate is not in the instance dictionary
        // (could be a method that returns the real delegate):
        delegate = has_traits_getattro(obj, trait->delegate_name);
        if (delegate == NULL) {
            return NULL;
        }
    }
    else {
        Py_INCREF(delegate);
    }

    if (!PyUnicode_Check(name)) {
        invalid_attribute_error(name);
        Py_DECREF(delegate);
        return NULL;
    }

    delegate_attr_name = trait->delegate_attr_name(trait, obj, name);
    tp = Py_TYPE(delegate);

    if (tp->tp_getattro != NULL) {
        result = (*tp->tp_getattro)(delegate, delegate_attr_name);
        goto done;
    }

    PyErr_Format(
        DelegationError,
        "The '%.50s' object has no attribute '%.400U' "
        "because its %.50s delegate has no attribute '%.400U'.",
        Py_TYPE(obj)->tp_name, name, tp->tp_name, delegate_attr_name);
    result = NULL;

done:
    Py_DECREF(delegate_attr_name);
    Py_DECREF(delegate);
    return result;
}

/*-----------------------------------------------------------------------------
|  Raises an exception when a disallowed trait is accessed:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_disallow(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    if (PyUnicode_Check(name)) {
        unknown_attribute_error(obj, name);
    }
    else {
        invalid_attribute_error(name);
    }

    return NULL;
}

/*-----------------------------------------------------------------------------
|  Returns the value of a constant trait:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_constant(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    Py_INCREF(trait->default_value);
    return trait->default_value;
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified property trait attribute:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_property0(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    PyObject *result;

    PyObject *args = PyTuple_New(0);
    if (args == NULL) {
        return NULL;
    }
    result = PyObject_Call(trait->delegate_name, args, NULL);
    Py_DECREF(args);
    return result;
}

static PyObject *
getattr_property1(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    PyObject *result;

    PyObject *args = PyTuple_Pack(1, (PyObject *)obj);
    if (args == NULL) {
        return NULL;
    }
    result = PyObject_Call(trait->delegate_name, args, NULL);
    Py_DECREF(args);

    return result;
}

static PyObject *
getattr_property2(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    PyObject *result;

    PyObject *args = PyTuple_Pack(2, (PyObject *)obj, name);
    if (args == NULL) {
        return NULL;
    }
    result = PyObject_Call(trait->delegate_name, args, NULL);
    Py_DECREF(args);

    return result;
}

static PyObject *
getattr_property3(trait_object *trait, has_traits_object *obj, PyObject *name)
{
    PyObject *result;

    PyObject *args = PyTuple_Pack(3, (PyObject *)obj, name, (PyObject *)trait);
    if (args == NULL) {
        return NULL;
    }

    result = PyObject_Call(trait->delegate_name, args, NULL);
    Py_DECREF(args);

    return result;
}

static trait_getattr getattr_property_handlers[] = {
    getattr_property0, getattr_property1, getattr_property2,
    getattr_property3};

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified standard Python attribute:
+----------------------------------------------------------------------------*/

static int
setattr_python(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    PyObject *dict = obj->obj_dict;

    if (value != NULL) {
        if (dict == NULL) {
            dict = PyDict_New();
            if (dict == NULL) {
                return -1;
            }
            obj->obj_dict = dict;
        }

        if (!PyUnicode_Check(name)) {
            return invalid_attribute_error(name);
        }

        if (PyDict_SetItem(dict, name, value) >= 0) {
            return 0;
        }
        if (PyErr_ExceptionMatches(PyExc_KeyError)) {
            PyErr_SetObject(PyExc_AttributeError, name);
        }

        return -1;
    }

    if (dict != NULL) {
        if (!PyUnicode_Check(name)) {
            return invalid_attribute_error(name);
        }

        if (PyDict_DelItem(dict, name) >= 0) {
            return 0;
        }

        if (PyErr_ExceptionMatches(PyExc_KeyError)) {
            unknown_attribute_error(obj, name);
        }

        return -1;
    }

    if (PyUnicode_Check(name)) {
        unknown_attribute_error(obj, name);

        return -1;
    }

    return invalid_attribute_error(name);
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified generic Python attribute:
+----------------------------------------------------------------------------*/

static int
setattr_generic(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    return PyObject_GenericSetAttr((PyObject *)obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Call all notifiers for a specified trait:
|
|  Parameters
|  ----------
|  tnotifiers : NULL or a list of callables.
|     Notifiers attached to the trait.
|  onotifiers : NULL or a list of callables.
|     Notifiers attached to the HasTraits instance.
|  obj : instance of HasTraits
|     Instance on which the trait changed.
|  name : str
|     Name of the trait changed.
|  old_value : any
|     Value of the trait before the change.
|  new_value : any
|     Value of the trait after the change.
|
|  Returns
|  -------
|  return_code : int
|      0 indicates success.
|     -1 indicates unexpected errors.
+----------------------------------------------------------------------------*/

static int
call_notifiers(
    PyListObject *tnotifiers, PyListObject *onotifiers, has_traits_object *obj,
    PyObject *name, PyObject *old_value, PyObject *new_value)
{
    Py_ssize_t i, t_len, o_len;
    int new_value_has_traits;
    PyObject *result, *item, *all_notifiers, *args;
    int rc = 0;

    // Do nothing if the user has explicitly requested no traits notifications
    // to be sent.
    if (obj->flags & HASTRAITS_NO_NOTIFY) {
        return rc;
    }

    args = PyTuple_Pack(4, (PyObject *)obj, name, old_value, new_value);
    if (args == NULL) {
        return -1;
    }

    new_value_has_traits = PyHasTraits_Check(new_value);

    if (tnotifiers != NULL) {
        t_len = PyList_GET_SIZE(tnotifiers);
    } else {
        t_len = 0;
    }
    if (onotifiers != NULL) {
        o_len = PyList_GET_SIZE(onotifiers);
    } else {
        o_len = 0;
    }

    // Concatenating trait notifiers and object notifiers.
    // Notifier lists are copied in order to prevent run-time modifications.
    all_notifiers = PyList_New(t_len + o_len);
    if (all_notifiers == NULL) {
        rc = -1;
        goto exit;
    }
    for (i = 0; i < t_len; i++) {
        item = PyList_GET_ITEM(tnotifiers, i);
        PyList_SET_ITEM(all_notifiers, i, item);
        Py_INCREF(item);
    }
    for (i = 0; i < o_len; i++) {
        item = PyList_GET_ITEM(onotifiers, i);
        PyList_SET_ITEM(all_notifiers, i + t_len, item);
        Py_INCREF(item);
    }

    for (i = 0; i < t_len + o_len; i++) {
        if (new_value_has_traits
            && ((has_traits_object *)new_value)->flags
                & HASTRAITS_VETO_NOTIFY) {
            break;
        }
        result = PyObject_Call(PyList_GET_ITEM(all_notifiers, i), args, NULL);
        if (result == NULL) {
            rc = -1;
            break;
        }
        Py_DECREF(result);
    }
    Py_DECREF(all_notifiers);

exit:
    Py_DECREF(args);
    return rc;
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified event trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_event(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    int rc = 0;
    PyListObject *tnotifiers;
    PyListObject *onotifiers;

    if (value != NULL) {
        if (traitd->validate != NULL) {
            value = traitd->validate(traitd, obj, name, value);
            if (value == NULL) {
                return -1;
            }
        }
        else {
            Py_INCREF(value);
        }

        tnotifiers = traito->notifiers;
        onotifiers = obj->notifiers;

        if (has_notifiers(tnotifiers, onotifiers)) {
            rc = call_notifiers(
                tnotifiers, onotifiers, obj, name, Undefined, value);
        }

        Py_DECREF(value);
    }

    return rc;
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified normal trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_trait(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    int rc;
    int changed;
    int do_notifiers;
    trait_post_setattr post_setattr;
    PyListObject *tnotifiers = NULL;
    PyListObject *onotifiers = NULL;
    PyObject *old_value = NULL;
    PyObject *original_value;
    PyObject *new_value;

    PyObject *dict = obj->obj_dict;

    changed = (traitd->flags & TRAIT_COMPARISON_MODE_NONE);

    if (value == NULL) {
        if (dict == NULL) {
            return 0;
        }

        if (!PyUnicode_Check(name)) {
            return invalid_attribute_error(name);
        }

        old_value = PyDict_GetItem(dict, name);
        if (old_value == NULL) {
            return 0;
        }

        Py_INCREF(old_value);
        if (PyDict_DelItem(dict, name) < 0) {
            Py_DECREF(old_value);
            return -1;
        }

        rc = 0;
        if (!(obj->flags & HASTRAITS_NO_NOTIFY)) {
            tnotifiers = traito->notifiers;
            onotifiers = obj->notifiers;
            if ((tnotifiers != NULL) || (onotifiers != NULL)) {
                value = traito->getattr(traito, obj, name);
                if (value == NULL) {
                    Py_DECREF(old_value);
                    return -1;
                }

                if (!changed) {
                    changed = (old_value != value);
                }

                if (changed) {
                    if (traitd->post_setattr != NULL) {
                        rc = traitd->post_setattr(traitd, obj, name, value);
                    }
                    if ((rc == 0) && has_notifiers(tnotifiers, onotifiers)) {
                        rc = call_notifiers(
                            tnotifiers, onotifiers, obj, name, old_value,
                            value);
                    }
                }

                Py_DECREF(value);
            }
        }
        Py_DECREF(old_value);
        return rc;
    }

    original_value = value;
    // If the object's value is Undefined, then do not call the validate
    // method (as the object's value has not yet been set).
    if ((traitd->validate != NULL) && (value != Undefined)) {
        value = traitd->validate(traitd, obj, name, value);
        if (value == NULL) {
            return -1;
        }
    }
    else {
        Py_INCREF(value);
    }

    if (dict == NULL) {
        obj->obj_dict = dict = PyDict_New();
        if (dict == NULL) {
            Py_DECREF(value);
            return -1;
        }
    }

    if (!PyUnicode_Check(name)) {
        Py_DECREF(value);
        return invalid_attribute_error(name);
    }

    new_value = (traitd->flags & TRAIT_SETATTR_ORIGINAL_VALUE) ? original_value
                                                               : value;
    old_value = NULL;

    tnotifiers = traito->notifiers;
    onotifiers = obj->notifiers;
    do_notifiers = has_notifiers(tnotifiers, onotifiers);

    post_setattr = traitd->post_setattr;
    if ((post_setattr != NULL) || do_notifiers) {
        old_value = PyDict_GetItem(dict, name);
        if (old_value == NULL) {
            if (traitd != traito) {
                old_value = traito->getattr(traito, obj, name);
                if (old_value == NULL) {
                    Py_DECREF(value);
                    return -1;
                }
            }
            else {
                old_value = default_value_for(traitd, obj, name);
                if (old_value == NULL) {
                    Py_DECREF(value);
                    return -1;
                }
                rc = PyDict_SetItem(dict, name, old_value);
                if (rc < 0) {
                    Py_DECREF(old_value);
                    Py_DECREF(value);
                    return -1;
                }
                if (post_setattr != NULL) {
                    rc = post_setattr(traitd, obj, name, old_value);
                    if (rc < 0) {
                        Py_DECREF(old_value);
                        Py_DECREF(value);
                        return -1;
                    }
                }
            }
        }
        else {
            Py_INCREF(old_value);
        }

        if (!changed) {
            changed = (old_value != value);
        }
    }

    if (PyDict_SetItem(dict, name, new_value) < 0) {
        if (PyErr_ExceptionMatches(PyExc_KeyError)) {
            PyErr_SetObject(PyExc_AttributeError, name);
        }
        Py_XDECREF(old_value);
        Py_DECREF(name);
        Py_DECREF(value);

        return -1;
    }

    rc = 0;

    if (changed) {
        if (post_setattr != NULL) {
            rc = post_setattr(
                traitd, obj, name,
                (traitd->flags & TRAIT_POST_SETATTR_ORIGINAL_VALUE)
                    ? original_value
                    : value);
        }

        if ((rc == 0) && do_notifiers) {
            rc = call_notifiers(
                tnotifiers, onotifiers, obj, name, old_value, new_value);
        }
    }

    Py_XDECREF(old_value);
    Py_DECREF(value);

    return rc;
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified delegate trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_delegate(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    PyObject *dict;
    PyObject *daname;
    PyObject *daname2;
    PyObject *temp;
    has_traits_object *delegate;
    has_traits_object *temp_delegate;
    int i, result;

    /* Follow the delegation chain until we find a non-delegated trait: */
    daname = name;
    Py_INCREF(daname);
    delegate = obj;
    for (i = 0;;) {
        dict = delegate->obj_dict;
        if ((dict != NULL)
            && ((temp_delegate = (has_traits_object *)PyDict_GetItem(
                     dict, traitd->delegate_name))
                != NULL)) {
            delegate = temp_delegate;
        }
        else {
            // Handle the case when the delegate is not in the instance
            // dictionary (could be a method that returns the real delegate):
            delegate = (has_traits_object *)has_traits_getattro(
                delegate, traitd->delegate_name);
            if (delegate == NULL) {
                Py_DECREF(daname);
                return -1;
            }
            Py_DECREF(delegate);
        }

        // Verify that 'delegate' is of type 'CHasTraits':
        if (!PyHasTraits_Check(delegate)) {
            Py_DECREF(daname);
            return bad_delegate_error2(obj, name);
        }

        daname2 = traitd->delegate_attr_name(traitd, obj, daname);
        Py_DECREF(daname);
        daname = daname2;
        if (((delegate->itrait_dict == NULL)
             || ((traitd = (trait_object *)dict_getitem(
                      delegate->itrait_dict, daname))
                 == NULL))
            && ((traitd = (trait_object *)dict_getitem(
                     delegate->ctrait_dict, daname))
                == NULL)
            && ((traitd = get_prefix_trait(delegate, daname, 1)) == NULL)) {
            Py_DECREF(daname);
            return bad_delegate_error(obj, name);
        }

        if (Py_TYPE(traitd) != ctrait_type) {
            Py_DECREF(daname);
            return fatal_trait_error();
        }

        if (traitd->delegate_attr_name == NULL) {
            if (traito->flags & TRAIT_MODIFY_DELEGATE) {
                result =
                    traitd->setattr(traitd, traitd, delegate, daname, value);
            }
            else {
                result = traitd->setattr(traito, traitd, obj, name, value);
                if (result >= 0) {
                    temp = PyObject_CallMethod(
                        (PyObject *)obj, "_remove_trait_delegate_listener",
                        "(Oi)", name, value != NULL);
                    if (temp == NULL) {
                        result = -1;
                    }
                    else {
                        Py_DECREF(temp);
                    }
                }
            }
            Py_DECREF(daname);

            return result;
        }

        if (++i >= 100) {
            return delegation_recursion_error(obj, name);
        }
    }
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified property trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_property0(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    PyObject *result;
    PyObject *args;

    if (value == NULL) {
        return set_delete_property_error(obj, name);
    }

    args = PyTuple_New(0);
    if (args == NULL) {
        return -1;
    }
    result = PyObject_Call(traitd->delegate_prefix, args, NULL);
    if (result == NULL) {
        return -1;
    }

    Py_DECREF(result);
    return 0;
}

static int
setattr_property1(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    PyObject *result;
    PyObject *args;

    if (value == NULL) {
        return set_delete_property_error(obj, name);
    }

    args = PyTuple_Pack(1, value);
    if (args == NULL) {
        return -1;
    }

    result = PyObject_Call(traitd->delegate_prefix, args, NULL);
    Py_DECREF(args);
    if (result == NULL) {
        return -1;
    }

    Py_DECREF(result);
    return 0;
}

static int
setattr_property2(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    PyObject *result;
    PyObject *args;

    if (value == NULL) {
        return set_delete_property_error(obj, name);
    }

    args = PyTuple_Pack(2, (PyObject *)obj, value);
    if (args == NULL) {
        return -1;
    }

    result = PyObject_Call(traitd->delegate_prefix, args, NULL);
    Py_DECREF(args);
    if (result == NULL) {
        return -1;
    }

    Py_DECREF(result);
    return 0;
}

static int
setattr_property3(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    PyObject *result;
    PyObject *args;

    if (value == NULL) {
        return set_delete_property_error(obj, name);
    }

    args = PyTuple_Pack(3, (PyObject *)obj, name, value);
    if (args == NULL) {
        return -1;
    }

    result = PyObject_Call(traitd->delegate_prefix, args, NULL);
    Py_DECREF(args);
    if (result == NULL) {
        return -1;
    }

    Py_DECREF(result);
    return 0;
}

/*-----------------------------------------------------------------------------
|  Validates then assigns a value to a specified property trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_validate_property(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    int result;
    PyObject *validated;

    if (value == NULL) {
        return set_delete_property_error(obj, name);
    }

    validated = traitd->validate(traitd, obj, name, value);
    if (validated == NULL) {
        return -1;
    }
    result = ((trait_setattr)traitd->post_setattr)(
        traito, traitd, obj, name, validated);
    Py_DECREF(validated);
    return result;
}

static PyObject *
setattr_validate0(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *validated;

    PyObject *args = PyTuple_New(0);
    if (args == NULL) {
        return NULL;
    }
    validated = PyObject_Call(trait->py_validate, args, NULL);
    Py_DECREF(args);
    return validated;
}

static PyObject *
setattr_validate1(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *validated;

    PyObject *args = PyTuple_Pack(1, value);
    if (args == NULL) {
        return NULL;
    }
    validated = PyObject_Call(trait->py_validate, args, NULL);
    Py_DECREF(args);
    return validated;
}

static PyObject *
setattr_validate2(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *validated;

    PyObject *args = PyTuple_Pack(2, (PyObject *)obj, value);
    if (args == NULL) {
        return NULL;
    }
    validated = PyObject_Call(trait->py_validate, args, NULL);
    Py_DECREF(args);
    return validated;
}

static PyObject *
setattr_validate3(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *validated;

    PyObject *args = PyTuple_Pack(3, (PyObject *)obj, name, value);
    if (args == NULL) {
        return NULL;
    }
    validated = PyObject_Call(trait->py_validate, args, NULL);
    Py_DECREF(args);
    return validated;
}

trait_validate setattr_validate_handlers[] = {
    setattr_validate0, setattr_validate1, setattr_validate2,
    setattr_validate3};

/*-----------------------------------------------------------------------------
|  Raises an exception when attempting to assign to a disallowed trait:
+----------------------------------------------------------------------------*/

static int
setattr_disallow(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    return set_disallow_error(obj, name);
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified read-only trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_readonly(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    PyObject *dict;
    PyObject *result;
    int rc;

    if (value == NULL) {
        return delete_readonly_error(obj, name);
    }

    if (traitd->default_value != Undefined) {
        return set_readonly_error(obj, name);
    }

    dict = obj->obj_dict;
    if (dict == NULL) {
        return setattr_python(traito, traitd, obj, name, value);
    }

    if (!PyUnicode_Check(name)) {
        return invalid_attribute_error(name);
    }

    result = PyDict_GetItem(dict, name);
    if ((result == NULL) || (result == Undefined)) {
        rc = setattr_python(traito, traitd, obj, name, value);
    }
    else {
        rc = set_readonly_error(obj, name);
    }

    return rc;
}

/*-----------------------------------------------------------------------------
|  Generates exception on attempting to assign to a constant trait:
+----------------------------------------------------------------------------*/

static int
setattr_constant(
    trait_object *traito, trait_object *traitd, has_traits_object *obj,
    PyObject *name, PyObject *value)
{
    if (PyUnicode_Check(name)) {
        PyErr_Format(
            TraitError,
            "Cannot modify the constant '%.400U'"
            " attribute of a '%.50s' object.",
            name, Py_TYPE(obj)->tp_name);
        return -1;
    }
    return invalid_attribute_error(name);
}

/*-----------------------------------------------------------------------------
|  Initializes a CTrait instance:
+----------------------------------------------------------------------------*/

static trait_getattr getattr_handlers[] = {
    getattr_trait, getattr_python, getattr_event, getattr_delegate,
    getattr_event, getattr_disallow, getattr_trait, getattr_constant,
    getattr_generic,
    /*  The following entries are used by the __getstate__ method: */
    getattr_property0, getattr_property1, getattr_property2, getattr_property3,
    /*  End of __getstate__ method entries */
    NULL};

static trait_setattr setattr_handlers[] = {
    setattr_trait, setattr_python, setattr_event, setattr_delegate,
    setattr_event, setattr_disallow, setattr_readonly, setattr_constant,
    setattr_generic,
    /*  The following entries are used by the __getstate__ method: */
    setattr_property0, setattr_property1, setattr_property2, setattr_property3,
    /*  End of __setstate__ method entries */
    NULL};


trait_object *
trait_new(PyTypeObject *trait_type, PyObject *args, PyObject *kw)
{
    int kind = 0;
    trait_object *trait;

    if (kw != NULL && PyDict_Size(kw) != (Py_ssize_t) 0) {
        PyErr_SetString(TraitError, "CTrait takes no keyword arguments");
        return NULL;
    }

    if (!PyArg_ParseTuple(args, "|i", &kind)) {
        return NULL;
    }

    if ((kind >= 0) && (kind <= 8)) {
        trait = (trait_object *)PyType_GenericNew(trait_type, args, kw);
        trait->getattr = getattr_handlers[kind];
        trait->setattr = setattr_handlers[kind];
        return trait;
    }

    PyErr_Format(
        TraitError,
        "Invalid argument to trait constructor. The argument `kind` "
        "must be an integer between 0 and 8 but a value of %d was provided.",
        kind);
    return NULL;
}

/*-----------------------------------------------------------------------------
|  Object clearing method:
+----------------------------------------------------------------------------*/

static int
trait_clear(trait_object *trait)
{
    Py_CLEAR(trait->default_value);
    Py_CLEAR(trait->py_validate);
    Py_CLEAR(trait->py_post_setattr);
    Py_CLEAR(trait->delegate_name);
    Py_CLEAR(trait->delegate_prefix);
    Py_CLEAR(trait->notifiers);
    Py_CLEAR(trait->handler);
    Py_CLEAR(trait->obj_dict);

    return 0;
}

/*-----------------------------------------------------------------------------
|  Deallocates an unused 'CTrait' instance:
+----------------------------------------------------------------------------*/

static void
trait_dealloc(trait_object *trait)
{
    PyObject_GC_UnTrack(trait);
    Py_TRASHCAN_SAFE_BEGIN(trait);
    trait_clear(trait);
    Py_TYPE(trait)->tp_free((PyObject *)trait);
    Py_TRASHCAN_SAFE_END(trait);
}

/*-----------------------------------------------------------------------------
|  Garbage collector traversal method:
+----------------------------------------------------------------------------*/

static int
trait_traverse(trait_object *trait, visitproc visit, void *arg)
{
    Py_VISIT(trait->default_value);
    Py_VISIT(trait->py_validate);
    Py_VISIT(trait->py_post_setattr);
    Py_VISIT(trait->delegate_name);
    Py_VISIT(trait->delegate_prefix);
    Py_VISIT((PyObject *)trait->notifiers);
    Py_VISIT(trait->handler);
    Py_VISIT(trait->obj_dict);

    return 0;
}

/*-----------------------------------------------------------------------------
|  Handles the 'getattr' operation on a 'CTrait' instance:
+----------------------------------------------------------------------------*/

static PyObject *
trait_getattro(trait_object *obj, PyObject *name)
{
    PyObject *value = PyObject_GenericGetAttr((PyObject *)obj, name);
    if (value != NULL || !PyErr_ExceptionMatches(PyExc_AttributeError)) {
        return value;
    }

    PyErr_Clear();

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Set the 'default_value_type' and 'default_value' fields
|  of a CTrait instance:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_set_default_value(trait_object *trait, PyObject *args)
{
    int value_type;
    PyObject *value, *old_value;

    if (!PyArg_ParseTuple(args, "iO", &value_type, &value)) {
        return NULL;
    }

    if ((value_type < 0) || (value_type > MAXIMUM_DEFAULT_VALUE_TYPE)) {
        PyErr_Format(
            PyExc_ValueError,
            "The default value type must be 0..%d, but %d was specified.",
            MAXIMUM_DEFAULT_VALUE_TYPE, value_type);
        return NULL;
    }

    trait->default_value_type = value_type;

    /* The DECREF on the old value can call arbitrary code, so take care not to
       DECREF until the trait is in a consistent state. (Newer CPython versions
       have a Py_XSETREF macro to do this safely.) */
    Py_INCREF(value);
    old_value = trait->default_value;
    trait->default_value = value;
    Py_XDECREF(old_value);

    Py_RETURN_NONE;
}

/*-----------------------------------------------------------------------------
|  Get or set the 'default_value_type' and 'default_value' fields
|  of a CTrait instance. Use of this function for setting the default
|  value information is deprecated; use set_default_value instead.
+----------------------------------------------------------------------------*/

static PyObject *
_trait_default_value(trait_object *trait, PyObject *args)
{
    if (PyArg_ParseTuple(args, "")) {
        if (trait->default_value == NULL) {
            return Py_BuildValue("iO", 0, Py_None);
        }
        else {
            return Py_BuildValue(
                "iO", trait->default_value_type, trait->default_value);
        }
    }

    PyErr_Clear();
    if (PyErr_WarnEx(
            PyExc_DeprecationWarning,
            "Use of the default_value method with arguments is deprecated. "
            "To set defaults, use set_default_value instead.",
            1)
        != 0) {
        return NULL;
    }
    return _trait_set_default_value(trait, args);
}

/*-----------------------------------------------------------------------------
|  Gets the default value of a CTrait instance for a specified object and trait
|  name:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_default_value_for(trait_object *trait, PyObject *args)
{
    PyObject *object;
    PyObject *name;

    if (!PyArg_ParseTuple(args, "OO", &object, &name)) {
        return NULL;
    }

    return default_value_for(trait, (has_traits_object *)object, name);
}

/*-----------------------------------------------------------------------------
|  Calls a Python-based trait validator:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_python(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result;
    PyObject *args;

    args = PyTuple_Pack(3, (PyObject *)obj, name, value);
    if (args == NULL) {
        return NULL;
    }
    result = PyObject_Call(trait->py_validate, args, NULL);
    Py_DECREF(args);

    return result;
}

/*-----------------------------------------------------------------------------
|  Calls the specified validator function:
+----------------------------------------------------------------------------*/

static PyObject *
call_validator(
    PyObject *validator, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result;
    PyObject *args;

    args = PyTuple_Pack(3, (PyObject *)obj, name, value);
    if (args == NULL) {
        return NULL;
    }
    result = PyObject_Call(validator, args, NULL);
    Py_DECREF(args);

    return result;
}

/*-----------------------------------------------------------------------------
|  Calls the specified type converter:
+----------------------------------------------------------------------------*/

static PyObject *
type_converter(PyObject *type, PyObject *value)
{
    PyObject *result;
    PyObject *args;

    args = PyTuple_Pack(1, value);
    if (args == NULL) {
        return NULL;
    }
    result = PyObject_Call(type, args, NULL);
    Py_DECREF(args);

    return result;
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is of a specified type (or None):
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_type(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *type_info = trait->py_validate;
    int kind = PyTuple_GET_SIZE(type_info);

    if (((kind == 3) && (value == Py_None))
        || PyObject_TypeCheck(
            value, (PyTypeObject *)PyTuple_GET_ITEM(type_info, kind - 1))) {
        Py_INCREF(value);
        return value;
    }

    return raise_trait_error(trait, obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is an instance of a specified type (or None):
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_instance(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *type_info = trait->py_validate;
    int kind = PyTuple_GET_SIZE(type_info);

    if (((kind == 3) && (value == Py_None))
        || (PyObject_IsInstance(value, PyTuple_GET_ITEM(type_info, kind - 1))
            > 0)) {
        Py_INCREF(value);
        return value;
    }

    return raise_trait_error(trait, obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is of a the same type as the object being assigned
|  to (or None):
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_self_type(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    if (((PyTuple_GET_SIZE(trait->py_validate) == 2) && (value == Py_None))
        || PyObject_TypeCheck(value, Py_TYPE(obj))) {
        Py_INCREF(value);
        return value;
    }

    return raise_trait_error(trait, obj, name, value);
}

/*
   Convert an integer-like Python object to an exact integer.

   Returns an object of exact type int (or possibly exact type long
   on Python 2, for values too large to fit in an int), or raises
   TypeError if the given object cannot be converted to an integer.

   Here, "integer-like" means either:

   - is an instance of int (or long in Python 2), or
   - can be converted to an integer via operator.index.

   The second case captures (for example) instances of NumPy
   integer types like np.int32, np.uint64, etc.

   Roughly equivalent to the Python code ``int(operator.index(value))``.
*/

static PyObject *
as_integer(PyObject *value)
{
    PyObject *index_of_value, *value_as_integer;

    /* Fast path for common case. */
    if (PyLong_CheckExact(value)) {
        Py_INCREF(value);
        return value;
    }

    /* Not of exact type int: call __index__ method if available. */
    index_of_value = PyNumber_Index(value);
    if (index_of_value == NULL) {
        return NULL;
    }

    /*
       We run the __index__ result through an extra int call to ensure that
       we get something of exact type int.

       Example problematic cases:

       - ``operator.index(True)`` gives ``True``, where we'd like ``1``.

       Related: https://bugs.python.org/issue17576
    */

    value_as_integer = PyNumber_Long(index_of_value);
    Py_DECREF(index_of_value);
    return value_as_integer;
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is a Python int
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_integer(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result = as_integer(value);
    /* A TypeError represents a type validation failure, and should be
       re-raised as a TraitError. Other exceptions should be propagated. */
    if (result == NULL && PyErr_ExceptionMatches(PyExc_TypeError)) {
        PyErr_Clear();
        return raise_trait_error(trait, obj, name, value);
    }
    return result;
}

/*
   Convert a float-like Python object to a float.

   Returns a new object of exact type float, or raises TypeError
   if the given object cannot be converted to a float.

   Here float-like means:

   - is an instance of float, or
   - can be converted to a float via its type's __float__ method

   Note: as of Python 3.8, objects having an __index__ method but
   no __float__ method can also be converted to float.
*/

static PyObject *
as_float(PyObject *value)
{
    double value_as_double;

    /* Fast path for common case. */
    if (PyFloat_CheckExact(value)) {
        Py_INCREF(value);
        return value;
    }

    /* General case: defer to the machinations of PyFloat_AsDouble. */
    value_as_double = PyFloat_AsDouble(value);
    if (value_as_double == -1.0 && PyErr_Occurred()) {
        return NULL;
    }
    return PyFloat_FromDouble(value_as_double);
}

/*-----------------------------------------------------------------------------
|  Verifies that a Python value is convertible to float
|
|  Will convert anything whose type has a __float__ method to a Python
|  float. Returns a Python object of exact type "float". Raises TraitError
|  with a suitable message if the given value isn't convertible to float.
|
|  Any exception other than TypeError raised by the value's __float__ method
|  will be propagated. A TypeError will be caught and turned into TraitError.
|
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_float(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result = as_float(value);
    /* A TypeError represents a type validation failure, and should be
       re-raised as a TraitError. Other exceptions should be propagated. */
    if (result == NULL && PyErr_ExceptionMatches(PyExc_TypeError)) {
        PyErr_Clear();
        return raise_trait_error(trait, obj, name, value);
    }
    return result;
}

/*
   Determine whether `value` lies in the range specified by `range_info`.

   * `value` must be of exact type float.
   * `range_info` is expected to be a tuple (*, low, high, exclude_mask)
     where `low` and `high` are object of exact type float and exclude_mask
     is a Python integer.

   Return 1 if `value` is within range, and 0 if not. If an exception occurs,
   return -1 and set an error.
*/

static int
in_float_range(PyObject *value, PyObject *range_info)
{
    PyObject *low, *high;
    long exclude_mask;

    low = PyTuple_GET_ITEM(range_info, 1);
    high = PyTuple_GET_ITEM(range_info, 2);
    exclude_mask = PyLong_AsLong(PyTuple_GET_ITEM(range_info, 3));
    if (exclude_mask == -1 && PyErr_Occurred()) {
        return -1;
    }

    if (low != Py_None) {
        if ((exclude_mask & 1) != 0) {
            if (PyFloat_AS_DOUBLE(value) <= PyFloat_AS_DOUBLE(low)) {
                return 0;
            }
        }
        else {
            if (PyFloat_AS_DOUBLE(value) < PyFloat_AS_DOUBLE(low)) {
                return 0;
            }
        }
    }

    if (high != Py_None) {
        if ((exclude_mask & 2) != 0) {
            if (PyFloat_AS_DOUBLE(value) >= PyFloat_AS_DOUBLE(high)) {
                return 0;
            }
        }
        else {
            if (PyFloat_AS_DOUBLE(value) > PyFloat_AS_DOUBLE(high)) {
                return 0;
            }
        }
    }

    return 1;
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is a float within a specified range:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_float_range(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result;
    int in_range;

    result = as_float(value);
    if (result == NULL) {
        if (PyErr_ExceptionMatches(PyExc_TypeError)) {
            /* Reraise any TypeError as a TraitError. */
            PyErr_Clear();
            return raise_trait_error(trait, obj, name, value);
        }
        /* Non-TypeErrors should be propagated. */
        return NULL;
    }

    in_range = in_float_range(result, trait->py_validate);
    if (in_range == 1) {
        return result;
    }
    else if (in_range == 0) {
        Py_DECREF(result);
        return raise_trait_error(trait, obj, name, value);
    }
    else {
        /* in_range must be -1, indicating an error; propagate it */
        Py_DECREF(result);
        return NULL;
    }
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is in a specified enumeration:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_enum(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *type_info = trait->py_validate;
    if (PySequence_Contains(PyTuple_GET_ITEM(type_info, 1), value) > 0) {
        Py_INCREF(value);
        return value;
    }

    return raise_trait_error(trait, obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is in a specified map (i.e. dictionary):
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_map(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *type_info = trait->py_validate;
    if (PyDict_GetItem(PyTuple_GET_ITEM(type_info, 1), value) != NULL) {
        Py_INCREF(value);
        return value;
    }

    return raise_trait_error(trait, obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is in a specified prefix map (i.e. dictionary):
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_prefix_map(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *type_info = trait->py_validate;
    PyObject *mapped_value =
        PyDict_GetItem(PyTuple_GET_ITEM(type_info, 1), value);
    if (mapped_value != NULL) {
        Py_INCREF(mapped_value);
        return mapped_value;
    }

    return call_validator(
        PyTuple_GET_ITEM(trait->py_validate, 2), obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is a tuple of a specified type and content:
+----------------------------------------------------------------------------*/

/* Note: this function does not follow standard CPython error-handling rules.
   There are three possible types of outcome for this function.

   If validation fails, NULL is returned and no Python exception is set
     (contrary to usual Python C-API conventions).
   If an unexpected exception occurs, NULL is returned and a Python exception
     is set.
   If validation succeeds, the validated object is returned.
*/

static PyObject *
validate_trait_tuple_check(
    PyObject *traits, has_traits_object *obj, PyObject *name, PyObject *value)
{
    trait_object *itrait;
    PyObject *bitem, *aitem, *tuple;
    int i, j, n;

    if (PyTuple_Check(value)) {
        n = PyTuple_GET_SIZE(traits);
        if (n == PyTuple_GET_SIZE(value)) {
            tuple = NULL;
            for (i = 0; i < n; i++) {
                bitem = PyTuple_GET_ITEM(value, i);
                itrait = (trait_object *)PyTuple_GET_ITEM(traits, i);
                if (itrait->validate == NULL) {
                    aitem = bitem;
                    Py_INCREF(aitem);
                }
                else {
                    aitem = itrait->validate(itrait, obj, name, bitem);
                }

                if (aitem == NULL) {
                    if (PyErr_ExceptionMatches(TraitError)) {
                        PyErr_Clear();
                    }
                    Py_XDECREF(tuple);
                    return NULL;
                }

                if (tuple != NULL) {
                    PyTuple_SET_ITEM(tuple, i, aitem);
                }
                else if (aitem != bitem) {
                    tuple = PyTuple_New(n);
                    if (tuple == NULL) {
                        return NULL;
                    }
                    for (j = 0; j < i; j++) {
                        bitem = PyTuple_GET_ITEM(value, j);
                        Py_INCREF(bitem);
                        PyTuple_SET_ITEM(tuple, j, bitem);
                    }
                    PyTuple_SET_ITEM(tuple, i, aitem);
                }
                else {
                    Py_DECREF(aitem);
                }
            }
            if (tuple != NULL) {
                return tuple;
            }

            Py_INCREF(value);
            return value;
        }
    }

    return NULL;
}

static PyObject *
validate_trait_tuple(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result = validate_trait_tuple_check(
        PyTuple_GET_ITEM(trait->py_validate, 1), obj, name, value);
    if (result != NULL || PyErr_Occurred()) {
        return result;
    }

    return raise_trait_error(trait, obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is of a specified (possibly coercable) type:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_coerce_type(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    int i, n;
    PyObject *type2;

    PyObject *type_info = trait->py_validate;
    PyObject *type = PyTuple_GET_ITEM(type_info, 1);
    if (PyObject_TypeCheck(value, (PyTypeObject *)type)) {
        Py_INCREF(value);
        return value;
    }

    n = PyTuple_GET_SIZE(type_info);
    for (i = 2; i < n; i++) {
        type2 = PyTuple_GET_ITEM(type_info, i);
        if (type2 == Py_None) {
            break;
        }

        if (PyObject_TypeCheck(value, (PyTypeObject *)type2)) {
            Py_INCREF(value);
            return value;
        }
    }

    for (i++; i < n; i++) {
        type2 = PyTuple_GET_ITEM(type_info, i);
        if (PyObject_TypeCheck(value, (PyTypeObject *)type2)) {
            return type_converter(type, value);
        }
    }

    return raise_trait_error(trait, obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is of a specified (possibly castable) type:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_cast_type(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result;

    PyObject *type_info = trait->py_validate;
    PyObject *type = PyTuple_GET_ITEM(type_info, 1);
    if (Py_TYPE(value) == (PyTypeObject *)type) {
        Py_INCREF(value);
        return value;
    }

    if ((result = type_converter(type, value)) != NULL) {
        return result;
    }

    return raise_trait_error(trait, obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value satisifies a specified function validator:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_function(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result;

    result = call_validator(
        PyTuple_GET_ITEM(trait->py_validate, 1), obj, name, value);
    if (result != NULL) {
        return result;
    }

    return raise_trait_error(trait, obj, name, value);
}


/*-----------------------------------------------------------------------------
|  Verifies a Python value is a callable (or None):
+----------------------------------------------------------------------------*/

/* Internal function for validation:

   Return 1 if the value is valid, 0 if it is invalid, and return -1
   and set an error condition if anything goes wrong.
*/

static int
_validate_trait_callable(PyObject *type_info, PyObject *value)
{
    if (value == Py_None) {
        if (PyTuple_GET_SIZE(type_info) < 2) {
            /* Backwards compatibility with old Callable */
            return 1;
        }
        else {
            /* 2nd element of tuple determines whether None is allowed */
            return PyObject_IsTrue(PyTuple_GET_ITEM(type_info, 1));
        }
    }
    else {
        return PyCallable_Check(value);
    }
}


static PyObject *
validate_trait_callable(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    int valid = _validate_trait_callable(trait->py_validate, value);

    if (valid == -1) {
        return NULL;
    }
    if (valid == 1) {
        Py_INCREF(value);
        return value;
    }
    return raise_trait_error(trait, obj, name, value);
}

/*-----------------------------------------------------------------------------
|  Attempts to 'adapt' an object to a specified interface:
|
|  If mode == 1, first tries to adapt the value to the given class, and
|  if that fails, but the value is already an instance of the class, returns
|  that value.
|
|  If mode == 2, first tries to adapt the value to the given class. If that
|  fails, and if the value is an instance of the class, the value is returned
|  unchanged. If neither of those holds, the default value is used.
|
|  Parameters
|  ----------
|  trait : cTrait
|      The trait being assigned to.
|  obj : HasTraits
|      The CHasTraits object that the trait belongs to.
|  name : str
|      The name of the trait in obj, for use in error messages.
|  value : object
|      The value to adapt
|
|  Raises
|  ------
|  TraitError
|      If the value cannot be adapted.
|
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_adapt(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result, *args, *type, *type_info;
    long mode, rc;

    type_info = trait->py_validate;

    /* If value is None and allow_none, return value; else fail validation */
    if (value == Py_None) {
        int allow_none = PyObject_IsTrue(PyTuple_GET_ITEM(type_info, 3));
        if (allow_none == -1) {
            return NULL;
        }
        if (allow_none) {
            Py_INCREF(value);
            return value;
        }
        else {
            return raise_trait_error(trait, obj, name, value);
        }
    }

    type = PyTuple_GET_ITEM(type_info, 1);
    mode = PyLong_AsLong(PyTuple_GET_ITEM(type_info, 2));
    if (mode == -1 && PyErr_Occurred()) {
        return NULL;
    }

    /* Adaptation mode 0: do a simple isinstance check. */
    if (mode == 0) {
        rc = PyObject_IsInstance(value, type);
        if (rc == -1 && PyErr_Occurred()) {
            return NULL;
        }
        if (rc) {
            Py_INCREF(value);
            return value;
        }
        else {
            return raise_trait_error(trait, obj, name, value);
        }
    }

    /* Try adaptation; return adapted value on success. */
    args = PyTuple_Pack(3, value, type, Py_None);
    if (args == NULL) {
        return NULL;
    }
    result = PyObject_Call(adapt, args, NULL);
    Py_DECREF(args);
    if (result == NULL) {
        return NULL;
    }
    if (result != Py_None) {
        return result;
    }
    Py_DECREF(result);

    /* Adaptation failed. Move on to an isinstance check. */
    rc = PyObject_IsInstance(value, type);
    if (rc == -1 && PyErr_Occurred()) {
        return NULL;
    }
    if (rc) {
        Py_INCREF(value);
        return value;
    }

    /* Adaptation and isinstance both failed. In mode 1, fail.
       Otherwise, return the default. */
    if (mode == 1) {
        return raise_trait_error(trait, obj, name, value);
    }
    else {
        return default_value_for(trait, obj, name);
    }
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value satisifies a complex trait definition:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_complex(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    int i, j, k, kind, in_range;
    long mode, rc;
    PyObject *result, *type_info, *type, *type2, *args;

    PyObject *list_type_info = PyTuple_GET_ITEM(trait->py_validate, 1);
    int n = PyTuple_GET_SIZE(list_type_info);
    for (i = 0; i < n; i++) {
        type_info = PyTuple_GET_ITEM(list_type_info, i);

        switch (PyLong_AsLong(PyTuple_GET_ITEM(type_info, 0))) {
            case 0: /* Type check: */
                kind = PyTuple_GET_SIZE(type_info);
                if (((kind == 3) && (value == Py_None))
                    || PyObject_TypeCheck(
                        value, (PyTypeObject *)PyTuple_GET_ITEM(
                                   type_info, kind - 1))) {
                    goto done;
                }
                break;

            case 1: /* Instance check: */
                kind = PyTuple_GET_SIZE(type_info);
                if (((kind == 3) && (value == Py_None))
                    || (PyObject_IsInstance(
                            value, PyTuple_GET_ITEM(type_info, kind - 1))
                        > 0)) {
                    goto done;
                }
                break;

            case 2: /* Self type check: */
                if (((PyTuple_GET_SIZE(type_info) == 2) && (value == Py_None))
                    || PyObject_TypeCheck(value, Py_TYPE(obj))) {
                    goto done;
                }
                break;

            case 4: /* Floating point range check: */
                result = as_float(value);
                if (result == NULL) {
                    if (PyErr_ExceptionMatches(PyExc_TypeError)) {
                        /* A TypeError should ultimately get re-raised
                           as a TraitError. */
                        PyErr_Clear();
                        break;
                    }
                    /* Non-TypeErrors should be propagated. */
                    return NULL;
                }

                in_range = in_float_range(result, type_info);
                if (in_range == 1) {
                    return result;
                }
                else if (in_range == 0) {
                    Py_DECREF(result);
                    break;
                }
                else {
                    /* in_range must be -1, indicating an error;
                       propagate it */
                    Py_DECREF(result);
                    return NULL;
                }

            case 5: /* Enumerated item check: */
                if (PySequence_Contains(PyTuple_GET_ITEM(type_info, 1), value)
                    > 0) {
                    goto done;
                }
                /* If the containment check failed (for example as a result of
                   checking whether an array is in a sequence), clear the
                   exception. See enthought/traits#376. */
                PyErr_Clear();
                break;
            case 6: /* Mapped item check: */
                if (PyDict_GetItem(PyTuple_GET_ITEM(type_info, 1), value)
                    != NULL) {
                    goto done;
                }
                PyErr_Clear();
                break;

            case 8: /* Perform 'slow' validate check: */
                result = PyObject_CallMethod(
                    PyTuple_GET_ITEM(type_info, 1), "slow_validate", "(OOO)",
                    obj, name, value);

                if (result == NULL && PyErr_ExceptionMatches(TraitError)) {
                    PyErr_Clear();
                    break;
                }
                return result;

            case 9: /* Tuple item check: */
                result = validate_trait_tuple_check(
                    PyTuple_GET_ITEM(type_info, 1), obj, name, value);
                if (result != NULL || PyErr_Occurred()) {
                    return result;
                }

                PyErr_Clear();
                break;

            case 10: /* Prefix map item check: */
                result = PyDict_GetItem(PyTuple_GET_ITEM(type_info, 1), value);
                if (result != NULL) {
                    Py_INCREF(result);
                    return result;
                }
                result = call_validator(
                    PyTuple_GET_ITEM(type_info, 2), obj, name, value);
                if (result != NULL) {
                    return result;
                }
                PyErr_Clear();
                break;

            case 11: /* Coercable type check: */
                type = PyTuple_GET_ITEM(type_info, 1);
                if (PyObject_TypeCheck(value, (PyTypeObject *)type)) {
                    goto done;
                }

                k = PyTuple_GET_SIZE(type_info);
                for (j = 2; j < k; j++) {
                    type2 = PyTuple_GET_ITEM(type_info, j);
                    if (type2 == Py_None) {
                        break;
                    }
                    if (PyObject_TypeCheck(value, (PyTypeObject *)type2)) {
                        goto done;
                    }
                }

                for (j++; j < k; j++) {
                    type2 = PyTuple_GET_ITEM(type_info, j);
                    if (PyObject_TypeCheck(value, (PyTypeObject *)type2)) {
                        return type_converter(type, value);
                    }
                }
                break;

            case 12: /* Castable type check */
                type = PyTuple_GET_ITEM(type_info, 1);
                if (Py_TYPE(value) == (PyTypeObject *)type) {
                    goto done;
                }

                if ((result = type_converter(type, value)) != NULL) {
                    return result;
                }

                PyErr_Clear();
                break;

            case 13: /* Function validator check: */
                result = call_validator(
                    PyTuple_GET_ITEM(type_info, 1), obj, name, value);
                if (result != NULL) {
                    return result;
                }

                PyErr_Clear();
                break;

                /* case 14: Python-based validator check: */

                /* case 15..18: Property 'setattr' validate checks: */

            case 19: /* Adaptable object check: */
                /* If value is None and allow_none, return value; else fail
                 * validation */
                if (value == Py_None) {
                    int allow_none =
                        PyObject_IsTrue(PyTuple_GET_ITEM(type_info, 3));
                    if (allow_none == -1) {
                        return NULL;
                    }
                    if (allow_none) {
                        goto done;
                    }
                    else {
                        break;
                    }
                }

                type = PyTuple_GET_ITEM(type_info, 1);
                mode = PyLong_AsLong(PyTuple_GET_ITEM(type_info, 2));
                if (mode == -1 && PyErr_Occurred()) {
                    return NULL;
                }

                /* Adaptation mode 0: do a simple isinstance check. */
                if (mode == 0) {
                    rc = PyObject_IsInstance(value, type);
                    if (rc == -1 && PyErr_Occurred()) {
                        return NULL;
                    }
                    if (rc) {
                        goto done;
                    }
                    else {
                        break;
                    }
                }

                /* Try adaptation; return adapted value on success. */
                args = PyTuple_Pack(3, value, type, Py_None);
                if (args == NULL) {
                    return NULL;
                }
                result = PyObject_Call(adapt, args, NULL);
                Py_DECREF(args);
                if (result == NULL) {
                    return NULL;
                }
                if (result != Py_None) {
                    return result;
                }
                Py_DECREF(result);

                /* Adaptation failed. Move on to an isinstance check. */
                rc = PyObject_IsInstance(value, type);
                if (rc == -1 && PyErr_Occurred()) {
                    return NULL;
                }
                if (rc) {
                    goto done;
                }

                /* Adaptation and isinstance both failed. In mode 1, fail.
                   Otherwise, return the default. */
                if (mode == 1) {
                    break;
                }
                else {
                    return default_value_for(trait, obj, name);
                }

            case 20: /* Integer check: */
                result = as_integer(value);
                /* A TypeError indicates that we don't have a match. Clear
                   the error and continue with the next item in the complex
                   sequence. Other errors are propagated. */
                if (result == NULL
                    && PyErr_ExceptionMatches(PyExc_TypeError)) {
                    PyErr_Clear();
                    break;
                }
                return result;

            case 21: /* Float check */
                /* A TypeError indicates that we don't have a match.
                   Clear the error and continue with the next item
                   in the complex sequence. */
                result = as_float(value);
                if (result == NULL
                    && PyErr_ExceptionMatches(PyExc_TypeError)) {
                    PyErr_Clear();
                    break;
                }
                return result;

            case 22: /* Callable check: */
                {
                    int valid = _validate_trait_callable(type_info, value);

                    if (valid == -1) {
                        return NULL;
                    }
                    if (valid == 1) {
                        goto done;
                    }
                    break;
                }

            default: /* Should never happen...indicates an internal error: */
                assert(0);  /* invalid validation type */
                goto error;
        }
    }
error:
    return raise_trait_error(trait, obj, name, value);
done:
    Py_INCREF(value);
    return value;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'validate' field of a CTrait instance:
+----------------------------------------------------------------------------*/

static trait_validate validate_handlers[] = {
    validate_trait_type,        /* case 0: Type check */
    validate_trait_instance,    /* case 1: Instance check */
    validate_trait_self_type,   /* case 2: Self type check */
    NULL,                       /* case 3: Integer range check (unused) */
    validate_trait_float_range, /* case 4: Floating-point range check */
    validate_trait_enum,        /* case 5: Enumerated item check */
    validate_trait_map,         /* case 6: Mapped item check */
    validate_trait_complex,     /* case 7: TraitComplex item check */
    NULL,                       /* case 8: 'Slow' validate check */
    validate_trait_tuple,       /* case 9: TupleOf item check */
    validate_trait_prefix_map,  /* case 10: Prefix map item check */
    validate_trait_coerce_type, /* case 11: Coercable type check */
    validate_trait_cast_type,   /* case 12: Castable type check */
    validate_trait_function,    /* case 13: Function validator check */
    validate_trait_python,      /* case 14: Python-based validator check */
    /*  The following entries are used by the __getstate__ method... */
    setattr_validate0, setattr_validate1, setattr_validate2, setattr_validate3,
    /*  ...End of __getstate__ method entries */
    validate_trait_adapt,   /* case 19: Adaptable object check */
    validate_trait_integer, /* case 20: Integer check */
    validate_trait_float,   /* case 21: Float check */
    validate_trait_callable,   /* case 22: Callable check */
};

static PyObject *
_trait_set_validate(trait_object *trait, PyObject *args)
{
    PyObject *validate;
    PyObject *v1, *v2, *v3;
    int n, kind;

    if (!PyArg_ParseTuple(args, "O", &validate)) {
        return NULL;
    }

    if (PyCallable_Check(validate)) {
        kind = 14;
        goto done;
    }

    if (PyTuple_CheckExact(validate)) {
        n = PyTuple_GET_SIZE(validate);
        if (n > 0) {
            kind = PyLong_AsLong(PyTuple_GET_ITEM(validate, 0));

            switch (kind) {
                case 0: /* Type check: */
                    if ((n <= 3)
                        && PyType_Check(PyTuple_GET_ITEM(validate, n - 1))
                        && ((n == 2)
                            || (PyTuple_GET_ITEM(validate, 1) == Py_None))) {
                        goto done;
                    }
                    break;

                case 1: /* Instance check: */
                    if ((n <= 3)
                        && ((n == 2)
                            || (PyTuple_GET_ITEM(validate, 1) == Py_None))) {
                        goto done;
                    }
                    break;

                case 2: /* Self type check: */
                    if ((n == 1)
                        || ((n == 2)
                            && (PyTuple_GET_ITEM(validate, 1) == Py_None))) {
                        goto done;
                    }
                    break;

                case 4: /* Floating point range check: */
                    if (n == 4) {
                        v1 = PyTuple_GET_ITEM(validate, 1);
                        v2 = PyTuple_GET_ITEM(validate, 2);
                        v3 = PyTuple_GET_ITEM(validate, 3);
                        if (((v1 == Py_None) || PyFloat_Check(v1))
                            && ((v2 == Py_None) || PyFloat_Check(v2))
                            && PyLong_Check(v3)) {
                            goto done;
                        }
                    }
                    break;

                case 5: /* Enumerated item check: */
                    if (n == 2) {
                        v1 = PyTuple_GET_ITEM(validate, 1);
                        if (PyTuple_CheckExact(v1)) {
                            goto done;
                        }
                    }
                    break;

                case 6: /* Mapped item check: */
                    if (n == 2) {
                        v1 = PyTuple_GET_ITEM(validate, 1);
                        if (PyDict_Check(v1)) {
                            goto done;
                        }
                    }
                    break;

                case 7: /* TraitComplex item check: */
                    if (n == 2) {
                        v1 = PyTuple_GET_ITEM(validate, 1);
                        if (PyTuple_CheckExact(v1)) {
                            goto done;
                        }
                    }
                    break;

                /* case 8: 'Slow' validate check: */
                case 9: /* TupleOf item check: */
                    if (n == 2) {
                        v1 = PyTuple_GET_ITEM(validate, 1);
                        if (PyTuple_CheckExact(v1)) {
                            goto done;
                        }
                    }
                    break;

                case 10: /* Prefix map item check: */
                    if (n == 3) {
                        v1 = PyTuple_GET_ITEM(validate, 1);
                        if (PyDict_Check(v1)) {
                            goto done;
                        }
                    }
                    break;

                case 11: /* Coercable type check: */
                    if (n >= 2) {
                        goto done;
                    }
                    break;

                case 12: /* Castable type check: */
                    if (n == 2) {
                        goto done;
                    }
                    break;

                case 13: /* Function validator check: */
                    if (n == 2) {
                        v1 = PyTuple_GET_ITEM(validate, 1);
                        if (PyCallable_Check(v1)) {
                            goto done;
                        }
                    }
                    break;

                /* case 14: Python-based validator check: */
                /* case 15..18: Property 'setattr' validate checks: */
                case 19: /* Adaptable object check: */
                    /* Note: We don't check the 'class' argument (item[1])
                       because some old-style code creates classes that are not
                       strictly classes or types (e.g. VTK), and yet they work
                       correctly with the rest of the Instance code */
                    if ((n == 4) && PyLong_Check(PyTuple_GET_ITEM(validate, 2))
                        && PyBool_Check(PyTuple_GET_ITEM(validate, 3))) {
                        goto done;
                    }
                    break;

                case 20: /* Integer check: */
                    if (n == 1) {
                        goto done;
                    }
                    break;

                case 21: /* Float check: */
                    if (n == 1) {
                        goto done;
                    }
                    break;

                case 22: /* Callable check: */
                    if (n == 1 || n == 2) {
                        goto done;
                    }
                    break;
            }
        }
    }

    PyErr_SetString(
        PyExc_ValueError, "The argument must be a tuple or callable.");

    return NULL;

done:
    trait->validate = validate_handlers[kind];
    Py_INCREF(validate);
    Py_XDECREF(trait->py_validate);
    trait->py_validate = validate;

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Gets the value of the 'validate' field of a CTrait instance:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_get_validate(trait_object *trait, PyObject *Py_UNUSED(ignored))
{
    if (trait->validate != NULL) {
        Py_INCREF(trait->py_validate);
        return trait->py_validate;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Validates that a particular value can be assigned to an object trait:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_validate(trait_object *trait, PyObject *args)
{
    PyObject *object, *name, *value;

    if (!PyArg_ParseTuple(args, "OOO", &object, &name, &value)) {
        return NULL;
    }

    if (trait->validate == NULL) {
        Py_INCREF(value);
        return value;
    }

    return trait->validate(trait, (has_traits_object *)object, name, value);
}

/*-----------------------------------------------------------------------------
|  Calls a Python-based trait post_setattr handler:
+----------------------------------------------------------------------------*/

static int
post_setattr_trait_python(
    trait_object *trait, has_traits_object *obj, PyObject *name,
    PyObject *value)
{
    PyObject *result;
    PyObject *args;

    args = PyTuple_Pack(3, (PyObject *)obj, name, value);
    if (args == NULL) {
        return -1;
    }
    result = PyObject_Call(trait->py_post_setattr, args, NULL);
    Py_DECREF(args);

    if (result == NULL) {
        return -1;
    }

    Py_DECREF(result);
    return 0;
}

/*-----------------------------------------------------------------------------
|  Returns the various forms of delegate names:
+----------------------------------------------------------------------------*/

static PyObject *
delegate_attr_name_name(
    trait_object *trait, has_traits_object *obj, PyObject *name)
{
    Py_INCREF(name);
    return name;
}

static PyObject *
delegate_attr_name_prefix(
    trait_object *trait, has_traits_object *obj, PyObject *name)
{
    Py_INCREF(trait->delegate_prefix);
    return trait->delegate_prefix;
}

static PyObject *
delegate_attr_name_prefix_name(
    trait_object *trait, has_traits_object *obj, PyObject *name)
{
    PyObject *result = PyUnicode_Concat(trait->delegate_prefix, name);
    return result;
}

static PyObject *
delegate_attr_name_class_name(
    trait_object *trait, has_traits_object *obj, PyObject *name)
{
    PyObject *prefix, *result;

    prefix = PyObject_GetAttr((PyObject *)Py_TYPE(obj), class_prefix);
    // fixme: Should verify that prefix is a string...
    if (prefix == NULL) {
        PyErr_Clear();

        Py_INCREF(name);
        return name;
    }

    result = PyUnicode_Concat(prefix, name);
    Py_DECREF(prefix);
    return result;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'post_setattr' field of a CTrait instance:
+----------------------------------------------------------------------------*/

static delegate_attr_name_func delegate_attr_name_handlers[] = {
    delegate_attr_name_name, delegate_attr_name_prefix,
    delegate_attr_name_prefix_name, delegate_attr_name_class_name, NULL};

static PyObject *
_trait_delegate(trait_object *trait, PyObject *args)
{
    PyObject *delegate_name;
    PyObject *delegate_prefix;
    int prefix_type;
    int modify_delegate;

    if (!PyArg_ParseTuple(
            args, "UUip", &delegate_name, &delegate_prefix, &prefix_type,
            &modify_delegate)) {
        return NULL;
    }
    Py_INCREF(delegate_name);
    Py_INCREF(delegate_prefix);

    if (modify_delegate) {
        trait->flags |= TRAIT_MODIFY_DELEGATE;
    }
    else {
        trait->flags &= ~TRAIT_MODIFY_DELEGATE;
    }

    trait->delegate_name = delegate_name;
    trait->delegate_prefix = delegate_prefix;
    if ((prefix_type < 0) || (prefix_type > 3)) {
        prefix_type = 0;
    }

    trait->delegate_attr_name = delegate_attr_name_handlers[prefix_type];

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the appropriate value comparison mode flags of a CTrait instance:
+----------------------------------------------------------------------------*/

static int
_set_trait_comparison_mode(trait_object *trait, PyObject *value, void *closure)
{
    long comparison_mode = PyLong_AsLong(value);

    if (comparison_mode == -1 && PyErr_Occurred()) {
        return -1;
    }

    switch (comparison_mode) {
        case 0:
            trait->flags &= ~TRAIT_COMPARISON_MODE_MASK;
            trait->flags |= TRAIT_COMPARISON_MODE_NONE;
            break;
        case 1:
            trait->flags &= ~TRAIT_COMPARISON_MODE_MASK;
            trait->flags |= TRAIT_COMPARISON_MODE_IDENTITY;
            break;
        case 2:
            trait->flags &= ~TRAIT_COMPARISON_MODE_MASK;
            trait->flags |= TRAIT_COMPARISON_MODE_EQUALITY;
            break;
        default:
            PyErr_Format(
                PyExc_ValueError,
                "The comparison mode must be 0..%d, but %ld was specified.",
                MAXIMUM_COMPARISON_MODE_VALUE, comparison_mode);
            return -1;
    }

    return 0;
}

/*-----------------------------------------------------------------------------
|  getter for trait comparison mode
+----------------------------------------------------------------------------*/

static PyObject *
_get_trait_comparison_mode_int(trait_object *trait, void *closure)
{
    int i_comparison_mode;

    unsigned int compare_flag = trait->flags & TRAIT_COMPARISON_MODE_MASK;

    if (compare_flag == TRAIT_COMPARISON_MODE_NONE) {
        i_comparison_mode = 0;
    }
    else if (compare_flag == TRAIT_COMPARISON_MODE_IDENTITY) {
        i_comparison_mode = 1;
    }
    else {
        assert(compare_flag == TRAIT_COMPARISON_MODE_EQUALITY);
        i_comparison_mode = 2;
    }

    return PyLong_FromLong(i_comparison_mode);
}

/*-----------------------------------------------------------------------------
|  Get the 'property' value fields of a CTrait instance:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_get_property(trait_object *trait, PyObject *Py_UNUSED(ignored))
{
    if (trait->flags & TRAIT_PROPERTY) {
        return PyTuple_Pack(
            3, trait->delegate_name, trait->delegate_prefix,
            trait->py_validate);
    }
    else {
        Py_RETURN_NONE;
    }
}

/*-----------------------------------------------------------------------------
|  Sets the 'property' value fields of a CTrait instance:
+----------------------------------------------------------------------------*/

static trait_setattr setattr_property_handlers[] = {
    setattr_property0, setattr_property1, setattr_property2, setattr_property3,
    /*  The following entries are used by the __getstate__ method__: */
    (trait_setattr)post_setattr_trait_python, NULL};

static PyObject *
_trait_set_property(trait_object *trait, PyObject *args)
{
    PyObject *get, *set, *validate;
    int get_n, set_n, validate_n;

    if (!PyArg_ParseTuple(
            args, "OiOiOi", &get, &get_n, &set, &set_n, &validate,
            &validate_n)) {
        return NULL;
    }

    if (!PyCallable_Check(get) || !PyCallable_Check(set)
        || ((validate != Py_None) && !PyCallable_Check(validate))
        || (get_n < 0) || (get_n > 3) || (set_n < 0) || (set_n > 3)
        || (validate_n < 0) || (validate_n > 3)) {
        PyErr_SetString(PyExc_ValueError, "Invalid arguments.");
        return NULL;
    }

    trait->flags |= TRAIT_PROPERTY;
    trait->getattr = getattr_property_handlers[get_n];
    if (validate != Py_None) {
        trait->setattr = setattr_validate_property;
        trait->post_setattr =
            (trait_post_setattr)setattr_property_handlers[set_n];
        trait->validate = setattr_validate_handlers[validate_n];
    }
    else {
        trait->setattr = setattr_property_handlers[set_n];
    }

    trait->delegate_name = get;
    trait->delegate_prefix = set;
    trait->py_validate = validate;
    Py_INCREF(get);
    Py_INCREF(set);
    Py_INCREF(validate);
    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Clones one trait into another:
+----------------------------------------------------------------------------*/

static void
trait_clone(trait_object *trait, trait_object *source)
{
    trait->flags = source->flags;
    trait->getattr = source->getattr;
    trait->setattr = source->setattr;
    trait->post_setattr = source->post_setattr;
    trait->py_post_setattr = source->py_post_setattr;
    trait->validate = source->validate;
    trait->py_validate = source->py_validate;
    trait->default_value_type = source->default_value_type;
    trait->default_value = source->default_value;
    trait->delegate_name = source->delegate_name;
    trait->delegate_prefix = source->delegate_prefix;
    trait->delegate_attr_name = source->delegate_attr_name;
    trait->handler = source->handler;
    Py_XINCREF(trait->py_post_setattr);
    Py_XINCREF(trait->py_validate);
    Py_XINCREF(trait->delegate_name);
    Py_XINCREF(trait->default_value);
    Py_XINCREF(trait->delegate_prefix);
    Py_XINCREF(trait->handler);
}

static PyObject *
_trait_clone(trait_object *trait, PyObject *args)
{
    trait_object *source;

    if (!PyArg_ParseTuple(args, "O!", ctrait_type, &source)) {
        return NULL;
    }

    trait_clone(trait, source);

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Returns (and optionally creates) the trait 'notifiers' list:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_notifiers(trait_object *trait, PyObject *args)
{
    PyObject *result;
    PyObject *list;
    int force_create;

    if (!PyArg_ParseTuple(args, "p", &force_create)) {
        return NULL;
    }

    result = (PyObject *)trait->notifiers;
    if (result == NULL) {
        result = Py_None;
        if (force_create && ((list = PyList_New(0)) != NULL)) {
            trait->notifiers = (PyListObject *)(result = list);
        }
    }

    Py_INCREF(result);
    return result;
}

/*-----------------------------------------------------------------------------
|  Converts a function to an index into a function table:
+----------------------------------------------------------------------------*/

static int
func_index(void *function, void **function_table)
{
    int i;

    for (i = 0; function != function_table[i]; i++) {
        ;
    }
    return i;
}

/*-----------------------------------------------------------------------------
|  Gets the pickleable state of the trait:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_getstate(trait_object *trait, PyObject *Py_UNUSED(ignored))
{
    PyObject *result;

    result = PyTuple_New(15);
    if (result == NULL) {
        return NULL;
    }

    PyTuple_SET_ITEM(
        result, 0,
        PyLong_FromLong(
            func_index((void *)trait->getattr, (void **)getattr_handlers)));
    PyTuple_SET_ITEM(
        result, 1,
        PyLong_FromLong(
            func_index((void *)trait->setattr, (void **)setattr_handlers)));
    PyTuple_SET_ITEM(
        result, 2,
        PyLong_FromLong(func_index(
            (void *)trait->post_setattr, (void **)setattr_property_handlers)));
    PyTuple_SET_ITEM(result, 3, get_value(trait->py_post_setattr));
    PyTuple_SET_ITEM(
        result, 4,
        PyLong_FromLong(
            func_index((void *)trait->validate, (void **)validate_handlers)));
    PyTuple_SET_ITEM(result, 5, get_value(trait->py_validate));
    PyTuple_SET_ITEM(result, 6, PyLong_FromLong(trait->default_value_type));
    PyTuple_SET_ITEM(result, 7, get_value(trait->default_value));
    PyTuple_SET_ITEM(result, 8, PyLong_FromUnsignedLong(trait->flags));
    PyTuple_SET_ITEM(result, 9, get_value(trait->delegate_name));
    PyTuple_SET_ITEM(result, 10, get_value(trait->delegate_prefix));
    PyTuple_SET_ITEM(
        result, 11,
        PyLong_FromLong(func_index(
            (void *)trait->delegate_attr_name,
            (void **)delegate_attr_name_handlers)));
    PyTuple_SET_ITEM(result, 12, get_value(NULL)); /* trait->notifiers */
    PyTuple_SET_ITEM(result, 13, get_value(trait->handler));
    PyTuple_SET_ITEM(result, 14, get_value(trait->obj_dict));

    return result;
}

/*-----------------------------------------------------------------------------
|  Restores the pickled state of the trait:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_setstate(trait_object *trait, PyObject *args)
{
    PyObject *ignore;
    int getattr_index, setattr_index, post_setattr_index, validate_index,
        delegate_attr_name_index;

    if (!PyArg_ParseTuple(
            args, "(iiiOiOiOIOOiOOO)", &getattr_index, &setattr_index,
            &post_setattr_index, &trait->py_post_setattr, &validate_index,
            &trait->py_validate, &trait->default_value_type,
            &trait->default_value, &trait->flags, &trait->delegate_name,
            &trait->delegate_prefix, &delegate_attr_name_index, &ignore,
            &trait->handler, &trait->obj_dict)) {
        return NULL;
    }

    trait->getattr = getattr_handlers[getattr_index];
    trait->setattr = setattr_handlers[setattr_index];
    trait->post_setattr =
        (trait_post_setattr)setattr_property_handlers[post_setattr_index];
    trait->validate = validate_handlers[validate_index];
    trait->delegate_attr_name =
        delegate_attr_name_handlers[delegate_attr_name_index];

    /*
       Backwards compatibility hack for old pickles. Versions of Traits
       prior to 6.0 replaced callables with a long value (-1).

       This backwards compatibility shim can be removed once we're
       sure that we don't need to handle pickles generated by Traits
       versions < 6.0.
    */
    if (PyLong_Check(trait->py_validate)) {
        trait->py_validate =
            PyObject_GetAttrString(trait->handler, "validate");
    }
    if (PyLong_Check(trait->py_post_setattr)) {
        trait->py_post_setattr =
            PyObject_GetAttrString(trait->handler, "post_setattr");
    }
    /* End backwards compatibility hack */

    Py_INCREF(trait->py_post_setattr);
    Py_INCREF(trait->py_validate);
    Py_INCREF(trait->default_value);
    Py_INCREF(trait->delegate_name);
    Py_INCREF(trait->delegate_prefix);
    Py_INCREF(trait->handler);
    Py_INCREF(trait->obj_dict);

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Returns the current trait dictionary:
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_dict(trait_object *trait, void *closure)
{
    PyObject *obj_dict = trait->obj_dict;
    if (obj_dict == NULL) {
        trait->obj_dict = obj_dict = PyDict_New();
        if (obj_dict == NULL) {
            return NULL;
        }
    }
    Py_INCREF(obj_dict);
    return obj_dict;
}

/*-----------------------------------------------------------------------------
|  Sets the current trait dictionary:
+----------------------------------------------------------------------------*/

static int
set_trait_dict(trait_object *trait, PyObject *value, void *closure)
{
    if (!PyDict_Check(value)) {
        return dictionary_error();
    }
    return set_value(&trait->obj_dict, value);
}

/*-----------------------------------------------------------------------------
|  Returns the current trait handler (if any):
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_handler(trait_object *trait, void *closure)
{
    return get_value(trait->handler);
}

/*-----------------------------------------------------------------------------
|  Sets the current trait dictionary:
+----------------------------------------------------------------------------*/

static int
set_trait_handler(trait_object *trait, PyObject *value, void *closure)
{
    return set_value(&trait->handler, value);
}

/*-----------------------------------------------------------------------------
|  Returns the current post_setattr (if any):
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_post_setattr(trait_object *trait, void *closure)
{
    return get_value(trait->py_post_setattr);
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'post_setattr' field of a CTrait instance:
+----------------------------------------------------------------------------*/

static int
set_trait_post_setattr(trait_object *trait, PyObject *value, void *closure)
{

    if (value != Py_None && !PyCallable_Check(value)) {
        PyErr_SetString(
            PyExc_ValueError, "The assigned value must be callable or None.");
        return -1;
    }

    if (value == Py_None) {
        value = NULL;
        trait->post_setattr = NULL;
    }
    else {
        trait->post_setattr = post_setattr_trait_python;
    }

    return set_value(&trait->py_post_setattr, value);
}

/*-----------------------------------------------------------------------------
|  Returns the current property flag value:
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_property_flag(trait_object *trait, void *closure)
{
    return get_trait_flag(trait, TRAIT_PROPERTY);
}

/*-----------------------------------------------------------------------------
|  Returns the current modify_delegate flag value:
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_modify_delegate_flag(trait_object *trait, void *closure)
{
    return get_trait_flag(trait, TRAIT_MODIFY_DELEGATE);
}

/*-----------------------------------------------------------------------------
|  Sets the current modify_delegate flag value:
+----------------------------------------------------------------------------*/

static int
set_trait_modify_delegate_flag(
    trait_object *trait, PyObject *value, void *closure)
{
    return set_trait_flag(trait, TRAIT_MODIFY_DELEGATE, value);
}


/*-----------------------------------------------------------------------------
|  Returns the current setattr_original_value flag value:
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_setattr_original_value_flag(trait_object *trait, void *closure)
{
    return get_trait_flag(trait, TRAIT_SETATTR_ORIGINAL_VALUE);
}

/*-----------------------------------------------------------------------------
|  Sets the current setattr_original_value flag value:
+----------------------------------------------------------------------------*/

static int
set_trait_setattr_original_value_flag(
    trait_object *trait, PyObject *value, void *closure)
{
    return set_trait_flag(trait, TRAIT_SETATTR_ORIGINAL_VALUE, value);
}

/*-----------------------------------------------------------------------------
|  Returns the current post_setattr_original_value flag value:
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_post_setattr_original_value_flag(trait_object *trait, void *closure)
{
    return get_trait_flag(trait, TRAIT_POST_SETATTR_ORIGINAL_VALUE);
}

/*-----------------------------------------------------------------------------
|  Sets the current post_setattr_original_value flag value:
+----------------------------------------------------------------------------*/

static int
set_trait_post_setattr_original_value_flag(
    trait_object *trait, PyObject *value, void *closure)
{
    return set_trait_flag(trait, TRAIT_POST_SETATTR_ORIGINAL_VALUE, value);
}

/*-----------------------------------------------------------------------------
|  Returns the current is_mapped flag value:
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_is_mapped_flag(trait_object *trait, void *closure)
{
    return get_trait_flag(trait, TRAIT_IS_MAPPED);
}

/*-----------------------------------------------------------------------------
|  Sets the current is_mapped flag value:
+----------------------------------------------------------------------------*/

static int
set_trait_is_mapped_flag(trait_object *trait, PyObject *value, void *closure)
{
    return set_trait_flag(trait, TRAIT_IS_MAPPED, value);
}

/*-----------------------------------------------------------------------------
|  'CTrait' instance methods:
+----------------------------------------------------------------------------*/

PyDoc_STRVAR(
    default_value_doc,
    "default_value()\n"
    "\n"
    "Return tuple giving default value information for this trait.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "default_value_type : int\n"
    "    An integer representing the kind of the default value\n"
    "default_value : value\n"
    "    A value or callable providing the default\n");

PyDoc_STRVAR(
    set_default_value_doc,
    "set_default_value(default_value_type, default_value)\n"
    "\n"
    "Set the default value information for this trait.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "default_value_type : int\n"
    "    An integer representing the kind of the default value\n"
    "default_value : value\n"
    "    A value or callable providing the default\n");

PyDoc_STRVAR(
    default_value_for_doc,
    "default_value_for(object, name)\n"
    "\n"
    "Return the default value of this CTrait instance for a specified object\n"
    "and trait name.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "object : HasTraits\n"
    "    The object the trait is attached to.\n"
    "name : str\n"
    "    The name of the trait.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "default_value : value\n"
    "    The default value for the given object and name.\n");

PyDoc_STRVAR(
    set_validate_doc,
    "set_validate(validator)\n"
    "\n"
    "Set the validator of a CTrait instance\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "validator : callable or tuple\n"
    "    Either a callable used for validation, or a tuple representing\n"
    "    validation information.\n"
    "\n"
    "    A callable used for validation should have signature\n"
    "    validator(obj, name, value) -> value, and should return the\n"
    "    validated (and possibly transformed) value. It should raise\n"
    "    TraitError on failure to validate.\n"
    "\n"
    "    If the validator is a tuple, its first entry will be an integer\n"
    "    specifying the type of validation, and the remaining entries\n"
    "    in the tuple (if any) provide additional information specific\n"
    "    to the validation type\n"
    "\n"
    "Raises\n"
    "------\n"
    "ValueError\n"
    "    If the given tuple does not have any of the expected forms.\n");

PyDoc_STRVAR(
    get_validate_doc,
    "get_validate()\n"
    "\n"
    "Return the validator of a CTrait instance.\n"
    "\n"
    "Returns the current validator for a CTrait instance, or None\n"
    "if the trait has no validator. See also the set_validate\n"
    "method.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "validator : tuple, callable, or None\n");

PyDoc_STRVAR(
    validate_doc,
    "validate(object, name, value)\n"
    "\n"
    "Perform validation and appropriate conversions on a value for this "
    "trait.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "object : HasTraits\n"
    "    The HasTraits object that validation is being performed for.\n"
    "name : str\n"
    "    The name of the trait.\n"
    "value : object\n"
    "    The value to be validated.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "The validated, converted value.\n"
    "\n"
    "Raises\n"
    "------\n"
    "TraitError\n"
    "    If the given value is invalid for this trait.\n");

PyDoc_STRVAR(
    delegate_doc,
    "delegate(delegate_name, prefix, prefix_type, modify_delegate)\n"
    "\n"
    "Set another trait as the delegate of this trait.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "delegate_name : str\n"
    "    Name of an attribute on the current object with references the\n"
    "    object that is the trait's delegate.\n"
    "delegate_prefix : str\n"
    "    A prefix or substitution applied to the original attribute when\n"
    "    looking up the delegated attribute.\n"
    "prefix_type : int\n"
    "    An integer between 0 and 3, inclusive. This controls how the\n"
    "    delegator attribute name is mapped to an attribute name on the\n"
    "    delegate object. The meanings of the values are as follows:\n"
    "\n"
    "    0\n"
    "        The delegation is to an attribute on the delegate object with\n"
    "        the same name as the delegator attribute. *delegate_prefix*\n"
    "        is unused.\n"
    "    1\n"
    "        The delegation is to an attribute with name given directly by\n"
    "        *delegate_prefix*.\n"
    "    2\n"
    "        The delegation is to an attribute whose name is the value of\n"
    "        *delegate_prefix*, prepended to the delegator attribute name.\n"
    "    3\n"
    "        The delegation is to an attribute whose name is the value of\n"
    "        the delegator object's ``__prefix__`` attribute, prepended to\n"
    "        the delegator attribute name.\n"
    "modify_delegate : bool\n"
    "    Whether to modify the delegate when the value of this trait\n"
    "    is modified.\n");

PyDoc_STRVAR(
    _trait_get_property_doc,
    "_trait_get_property()\n"
    "\n"
    "Get the property fields for this trait.\n"
    "\n"
    "This method returns a tuple (get, set, validate) of length 3 containing\n"
    "the getter, setter and validator for this property trait.\n"
    "\n"
    "When called on a non-property trait, this method returns *None*.\n");

PyDoc_STRVAR(
    _trait_set_property_doc,
    "_trait_set_property(get, get_n, set, set_n, validate, validate_n)\n"
    "\n"
    "This method expects six arguments, and uses these arguments to set the\n"
    "get, set and validation for the trait. It also sets the property flag \n"
    "on the trait.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "get : callable\n"
    "    Function called when getting the value of this property trait.\n"
    "    This function will be called with one of the following argument\n"
    "    combinations, depending on the value of *get_n*.\n"
    "\n"
    "    - no arguments\n"
    "    - a single argument ``obj``\n"
    "    - a pair of arguments ``obj, name``\n"
    "    - a triple of arguments ``obj, name, trait``\n"
    "\n"
    "get_n : int\n"
    "    Number of arguments to supply to the getter. This should be\n"
    "    between 0 and 3, inclusive.\n"
    "set : callable\n"
    "    Function called when setting the value of this property trait.\n"
    "    This function will be called with one of the following argument\n"
    "    combinations, depending on the value of *set_n*.\n"
    "\n"
    "    - no arguments\n"
    "    - a single argument ``value``\n"
    "    - a pair of arguments ``obj, value``\n"
    "    - a triple of arguments ``obj, name, value``\n"
    "\n"
    "set_n : int\n"
    "    Number of arguments to supply to the setter. This should be\n"
    "    between 0 and 3, inclusive.\n"
    "validate : callable or None\n"
    "    Function called for validation. This function will be called\n"
    "    with one of the following argument combinations, depending on\n"
    "    the value of *validate_n*.\n"
    "\n"
    "    - no arguments\n"
    "    - a single argument ``value``\n"
    "    - a pair of arguments ``obj, value``\n"
    "    - a triple of arguments ``obj, name, value``\n"
    "\n"
    "validate_n : int\n"
    "    Number of arguments to supply to the validator. This should be\n"
    "    between 0 and 3, inclusive.\n");

PyDoc_STRVAR(
    clone_doc,
    "clone(source)\n"
    "\n"
    "Clone state of another trait into this one.\n"
    "\n"
    "This method copies all of the state of the *source* trait into\n"
    "this trait, with the exception of the trait notifiers and the\n"
    "trait __dict__. The copy is a simple shallow copy: for example,\n"
    "after the copy, the handler for this trait will be the same\n"
    "object as the handler for the *source* trait.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "source : CTrait\n"
    "    The source trait.\n");

PyDoc_STRVAR(
    _notifiers_doc,
    "_notifiers(force_create)\n"
    "\n"
    "Return (and optionally create) the list of notifiers for this trait.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "force_create : bool\n"
    "    Whether to automatically create the list of notifiers, if it\n"
    "    doesn't exist yet.\n"
    "\n"
    "Returns\n"
    "-------\n"
    "notifiers : list of callables, or None\n"
    "    If the trait has no notifiers, and *force_create* is false, return "
    "None.\n"
    "    Otherwise, return the list of notifiers for this trait, creating it "
    "\n"
    "    first if necessary. Each notifier is a\n"
    "    callable accepting four arguments (object, trait_name, old, new).\n");

static PyMethodDef trait_methods[] = {
    {"__getstate__", (PyCFunction)_trait_getstate, METH_NOARGS,
     PyDoc_STR("__getstate__()")},
    {"__setstate__", (PyCFunction)_trait_setstate, METH_VARARGS,
     PyDoc_STR("__setstate__(state)")},
    {"default_value", (PyCFunction)_trait_default_value, METH_VARARGS,
     default_value_doc},
    {"set_default_value", (PyCFunction)_trait_set_default_value, METH_VARARGS,
     set_default_value_doc},
    {"default_value_for", (PyCFunction)_trait_default_value_for, METH_VARARGS,
     default_value_for_doc},
    {"set_validate", (PyCFunction)_trait_set_validate, METH_VARARGS,
     set_validate_doc},
    {"get_validate", (PyCFunction)_trait_get_validate, METH_NOARGS,
     get_validate_doc},
    {"validate", (PyCFunction)_trait_validate, METH_VARARGS, validate_doc},
    {"delegate", (PyCFunction)_trait_delegate, METH_VARARGS,
     delegate_doc},
    {"_get_property", (PyCFunction)_trait_get_property, METH_NOARGS,
     _trait_get_property_doc},
    {"_set_property", (PyCFunction)_trait_set_property, METH_VARARGS,
     _trait_set_property_doc},
    {"clone", (PyCFunction)_trait_clone, METH_VARARGS,
     clone_doc},
    {"_notifiers", (PyCFunction)_trait_notifiers, METH_VARARGS,
     _notifiers_doc},
    {NULL, NULL},
};

/*-----------------------------------------------------------------------------
|  'CTrait' property definitions:
+----------------------------------------------------------------------------*/

PyDoc_STRVAR(
    ctrait_handler_doc,
    "The trait handler underlying this trait.\n"
    "\n"
    "The value of this property should be an instance of\n"
    "``BaseTraitHandler``.\n"
);

PyDoc_STRVAR(
    ctrait_post_setattr_doc,
    "Callable called after a successful value assignment to this trait.\n"
    "\n"
    "The value of this property is either a callable or *None*.\n"
    "If the value is a callable, this callable allows the trait to do\n"
    "additional processing after a value has successfully been assigned.\n"
    "The callable is called with arguments (object, name, value), and the\n"
    "return value of the callable is ignored.\n"
);

PyDoc_STRVAR(
    ctrait_is_property_doc,
    "True if this trait is a property trait, else False.\n"
    "\n"
    "This property is read-only.\n"
);

PyDoc_STRVAR(
    ctrait_modify_delegate_doc,
    "Indicate whether modifications affect the delegate.\n"
    "\n"
    "For delegated traits, this is a boolean indicating whether\n"
    "modifications to this trait also modify the delegated trait.\n"
);

PyDoc_STRVAR(
    ctrait_setattr_original_value_doc,
    "Whether setattr stores the original or the validated value.\n"
    "\n"
    "If true, setattr will store the original, unvalidated, value set on\n"
    "the trait to the object's dictionary. If false, the value returned\n"
    "from the validator will be stored.\n"
);

PyDoc_STRVAR(
    ctrait_post_setattr_original_value_doc,
    "Whether post_setattr receives the original or the validated value.\n"
    "\n"
    "If true, the post_setattr callable for this trait (if defined)\n"
    "receives the original, unvalidated value assigned to the trait.\n"
    "If false, the validated value is provided to post_setattr.\n"
);

PyDoc_STRVAR(
    ctrait_is_mapped_doc,
    "True if this is a mapped trait, else False.\n"
);

PyDoc_STRVAR(
    ctrait_comparison_mode_doc,
    "Integer constant indicating when notifiers are executed.\n"
    "\n"
    "The value of this constant is the integer corresponding to a member\n"
    "of the :data:`~traits.constants.ComparisonMode` enumeration.\n"
);


static PyGetSetDef trait_properties[] = {
    {"__dict__",
     (getter)get_trait_dict,
     (setter)set_trait_dict,
     NULL, NULL},
    {"handler",
     (getter)get_trait_handler,
     (setter)set_trait_handler,
     ctrait_handler_doc,
     NULL},
    {"post_setattr",
     (getter)get_trait_post_setattr,
     (setter)set_trait_post_setattr,
     ctrait_post_setattr_doc,
     NULL},
    {"is_property",
     (getter)get_trait_property_flag,
     NULL,
     ctrait_is_property_doc,
     NULL},
    {"modify_delegate",
     (getter)get_trait_modify_delegate_flag,
     (setter)set_trait_modify_delegate_flag,
     ctrait_modify_delegate_doc,
     NULL},
    {"setattr_original_value",
     (getter)get_trait_setattr_original_value_flag,
     (setter)set_trait_setattr_original_value_flag,
     ctrait_setattr_original_value_doc,
     NULL},
    {"post_setattr_original_value",
     (getter)get_trait_post_setattr_original_value_flag,
     (setter)set_trait_post_setattr_original_value_flag,
     ctrait_post_setattr_original_value_doc,
     NULL},
    {"is_mapped",
     (getter)get_trait_is_mapped_flag,
     (setter)set_trait_is_mapped_flag,
     ctrait_is_mapped_doc,
     NULL},
    {"comparison_mode",
     (getter)_get_trait_comparison_mode_int,
     (setter)_set_trait_comparison_mode,
     ctrait_comparison_mode_doc,
     NULL},
    {NULL}};

/*-----------------------------------------------------------------------------
|  'CTrait' type definition:
+----------------------------------------------------------------------------*/

PyDoc_STRVAR(
    ctrait_doc,
    "Base class for CTrait.\n"
    "\n"
    "The cTrait class is not intended to be instantiated directly.\n"
    "Instead, it serves as a base class for CTrait.\n"
    "\n"
    "Parameters\n"
    "----------\n"
    "kind : int, optional\n"
    "    Integer between 0 and 8 representing the kind of this trait, with\n"
    "    the default value being 0. The kind determines how attribute get\n"
    "    and set operations behave for attributes using this trait. The\n"
    "    values for *kind* correspond to the members of the ``TraitKind``\n"
    "    enumeration type.\n");

static PyTypeObject trait_type = {
    PyVarObject_HEAD_INIT(NULL, 0) "traits.ctraits.cTrait",
    sizeof(trait_object),
    0,
    (destructor)trait_dealloc,    /* tp_dealloc */
    0,                            /* tp_print */
    0,                            /* tp_getattr */
    0,                            /* tp_setattr */
    0,                            /* tp_compare */
    0,                            /* tp_repr */
    0,                            /* tp_as_number */
    0,                            /* tp_as_sequence */
    0,                            /* tp_as_mapping */
    0,                            /* tp_hash */
    0,                            /* tp_call */
    0,                            /* tp_str */
    (getattrofunc)trait_getattro, /* tp_getattro */
    0,                            /* tp_setattro */
    0,                            /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE
        | Py_TPFLAGS_HAVE_GC,                  /* tp_flags */
    ctrait_doc,                                /* tp_doc */
    (traverseproc)trait_traverse,              /* tp_traverse */
    (inquiry)trait_clear,                      /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    trait_methods,                             /* tp_methods */
    0,                                         /* tp_members */
    trait_properties,                          /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    sizeof(trait_object) - sizeof(PyObject *), /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    (newfunc)trait_new                         /* tp_new */
};

/*-----------------------------------------------------------------------------
|  Sets the global 'TraitListObject', TraitSetObject and 'TraitDictObject'
|  classes:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_list_classes(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(
            args, "OOO", &TraitListObject, &TraitSetObject,
            &TraitDictObject)) {
        return NULL;
    }

    Py_INCREF(TraitListObject);
    Py_INCREF(TraitSetObject);
    Py_INCREF(TraitDictObject);

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the global 'adapt' reference to the 'adapt' function:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_adapt(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "O", &adapt)) {
        return NULL;
    }

    Py_INCREF(adapt);

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the global 'ctrait_type' class reference:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_ctrait(PyObject *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "O", &ctrait_type)) {
        return NULL;
    }

    Py_INCREF(ctrait_type);

    Py_INCREF(Py_None);
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  'CTrait' instance methods:
+----------------------------------------------------------------------------*/

static PyMethodDef ctraits_methods[] = {
    {"_list_classes", (PyCFunction)_ctraits_list_classes, METH_VARARGS,
     PyDoc_STR(
         "_list_classes(TraitListObject,TraitSetObject,TraitDictObject)")},
    {"_adapt", (PyCFunction)_ctraits_adapt, METH_VARARGS,
     PyDoc_STR("_adapt(adaptation_function)")},
    {"_ctrait", (PyCFunction)_ctraits_ctrait, METH_VARARGS,
     PyDoc_STR("_ctrait(CTrait_class)")},
    {NULL, NULL},
};

/*-----------------------------------------------------------------------------
|  Performs module and type initialization:
+----------------------------------------------------------------------------*/

static struct PyModuleDef ctraitsmodule = {
    PyModuleDef_HEAD_INIT, "ctraits", ctraits__doc__, -1, ctraits_methods};

PyMODINIT_FUNC
PyInit_ctraits(void)
{
    /* Create the 'ctraits' module: */
    PyObject *module;
    PyObject *trait_base;
    PyObject *trait_errors;
    int error;

    module = PyModule_Create(&ctraitsmodule);
    if (module == NULL) {
        return NULL;
    }

    /* Create the 'CHasTraits' type: */
    has_traits_type.tp_base = &PyBaseObject_Type;
    has_traits_type.tp_alloc = PyType_GenericAlloc;
    if (PyType_Ready(&has_traits_type) < 0) {
        return NULL;
    }

    Py_INCREF(&has_traits_type);
    if (PyModule_AddObject(module, "CHasTraits", (PyObject *)&has_traits_type)
        < 0) {
        return NULL;
    }

    /* Create the 'CTrait' type: */
    trait_type.tp_base = &PyBaseObject_Type;
    trait_type.tp_alloc = PyType_GenericAlloc;
    if (PyType_Ready(&trait_type) < 0) {
        return NULL;
    }

    Py_INCREF(&trait_type);
    if (PyModule_AddObject(module, "cTrait", (PyObject *)&trait_type) < 0) {
        return NULL;
    }

    /* Predefine a Python string == "__class_traits__": */
    class_traits = PyUnicode_FromString("__class_traits__");

    /* Predefine a Python string == "__listener_traits__": */
    listener_traits = PyUnicode_FromString("__listener_traits__");

    /* Predefine a Python string == "editor": */
    editor_property = PyUnicode_FromString("editor");

    /* Predefine a Python string == "__prefix__": */
    class_prefix = PyUnicode_FromString("__prefix__");

    /* Predefine a Python string == "trait_added": */
    trait_added = PyUnicode_FromString("trait_added");

    /* Import Undefined and Uninitialized */
    trait_base = PyImport_ImportModule("traits.trait_base");
    if (trait_base == NULL) {
        return NULL;
    }
    Undefined = PyObject_GetAttrString(trait_base, "Undefined");
    if (Undefined == NULL) {
        Py_DECREF(trait_base);
        return NULL;
    }
    Uninitialized = PyObject_GetAttrString(trait_base, "Uninitialized");
    if (Uninitialized == NULL) {
        Py_DECREF(trait_base);
        return NULL;
    }
    Py_DECREF(trait_base);

    /* Import TraitError and DelegationError */
    trait_errors = PyImport_ImportModule("traits.trait_errors");
    if (trait_errors == NULL) {
        return NULL;
    }
    TraitError = PyObject_GetAttrString(trait_errors, "TraitError");
    if (TraitError == NULL) {
        Py_DECREF(trait_errors);
        return NULL;
    }
    DelegationError = PyObject_GetAttrString(trait_errors, "DelegationError");
    if (DelegationError == NULL) {
        Py_DECREF(trait_errors);
        return NULL;
    }
    Py_DECREF(trait_errors);

    /* Export default-value constants, so that they can be re-used in
       the DefaultValue enumeration. */
    error = PyModule_AddIntConstant(
        module,
        "_CONSTANT_DEFAULT_VALUE",
        CONSTANT_DEFAULT_VALUE
    );
    if (error < 0) {
        return NULL;
    }
    error = PyModule_AddIntConstant(
        module,
        "_MISSING_DEFAULT_VALUE",
        MISSING_DEFAULT_VALUE
    );
    if (error < 0) {
        return NULL;
    }
    error = PyModule_AddIntConstant(
        module,
        "_OBJECT_DEFAULT_VALUE",
        OBJECT_DEFAULT_VALUE
    );
    if (error < 0) {
        return NULL;
    }
    error = PyModule_AddIntConstant(
        module,
        "_LIST_COPY_DEFAULT_VALUE",
        LIST_COPY_DEFAULT_VALUE
    );
    if (error < 0) {
        return NULL;
    }
    error = PyModule_AddIntConstant(
        module,
        "_DICT_COPY_DEFAULT_VALUE",
        DICT_COPY_DEFAULT_VALUE
    );
    if (error < 0) {
        return NULL;
    }
    error = PyModule_AddIntConstant(
        module,
        "_TRAIT_LIST_OBJECT_DEFAULT_VALUE",
        TRAIT_LIST_OBJECT_DEFAULT_VALUE
    );
    if (error < 0) {
        return NULL;
    }
    error = PyModule_AddIntConstant(
        module,
        "_TRAIT_DICT_OBJECT_DEFAULT_VALUE",
        TRAIT_DICT_OBJECT_DEFAULT_VALUE
    );
    if (error < 0) {
        return NULL;
    }
    error = PyModule_AddIntConstant(
        module,
        "_TRAIT_SET_OBJECT_DEFAULT_VALUE",
        TRAIT_SET_OBJECT_DEFAULT_VALUE
    );
    if (error < 0) {
        return NULL;
    }
    error = PyModule_AddIntConstant(
        module,
        "_CALLABLE_DEFAULT_VALUE",
        CALLABLE_DEFAULT_VALUE
    );
    if (error < 0) {
        return NULL;
    }
    error = PyModule_AddIntConstant(
        module,
        "_CALLABLE_AND_ARGS_DEFAULT_VALUE",
        CALLABLE_AND_ARGS_DEFAULT_VALUE
    );
    if (error < 0) {
        return NULL;
    }
    error = PyModule_AddIntConstant(
        module,
        "_MAXIMUM_DEFAULT_VALUE_TYPE",
        MAXIMUM_DEFAULT_VALUE_TYPE
    );
    if (error < 0) {
        return NULL;
    }

    return module;
}
