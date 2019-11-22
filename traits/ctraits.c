/******************************************************************************
*
*  Description: C based implementation of the Traits package
*
*  Copyright (c) 2005, Enthought, Inc.
*  All rights reserved.
*
*  This software is provided without warranty under the terms of the BSD
*  license included in enthought/LICENSE.txt and may be redistributed only
*  under the conditions described in the aforementioned license.  The license
*  is also available online at http://www.enthought.com/licenses/BSD.txt
*
*  Thanks for using Enthought open source!
*
*  Author: David C. Morrill
*  Date:   06/15/2004
*
******************************************************************************/

/*-----------------------------------------------------------------------------
|  Includes:
+----------------------------------------------------------------------------*/

#include "Python.h"
#include "structmember.h"

#include "py2to3.h"

/*-----------------------------------------------------------------------------
|  Constants:
+----------------------------------------------------------------------------*/

static PyObject * class_traits;        /* == "__class_traits__" */
static PyObject * listener_traits;     /* == "__listener_traits__" */
static PyObject * editor_property;     /* == "editor" */
static PyObject * class_prefix;        /* == "__prefix__" */
static PyObject * trait_added;         /* == "trait_added" */
static PyObject * empty_tuple;         /* == () */
static PyObject * empty_dict;          /* == {} */
static PyObject * Undefined;           /* Global 'Undefined' value */
static PyObject * Uninitialized;       /* Global 'Uninitialized' value */
static PyObject * TraitError;          /* TraitError exception */
static PyObject * DelegationError;     /* DelegationError exception */
static PyObject * TraitListObject;     /* TraitListObject class */
static PyObject * TraitSetObject;      /* TraitSetObject class */
static PyObject * TraitDictObject;     /* TraitDictObject class */
static PyObject * TraitValue;          /* TraitValue class */
static PyObject * adapt;               /* PyProtocols 'adapt' function */
static PyObject * validate_implements; /* 'validate implementation' function */
static PyObject * is_callable;         /* Marker for 'callable' value */
static PyObject * _trait_notification_handler; /* User supplied trait */
                /* notification handler (intended for use by debugging tools) */
static PyTypeObject * ctrait_type;     /* Python-level CTrait type reference */

/*-----------------------------------------------------------------------------
|  Macro definitions:
+----------------------------------------------------------------------------*/

/* The following macro is automatically defined in Python 2.4 and later: */
#ifndef Py_VISIT
#define Py_VISIT(op) \
do { \
    if (op) { \
        int vret = visit((PyObject *)(op), arg);        \
        if (vret) return vret; \
    } \
} while (0)
#endif

/* The following macro is automatically defined in Python 2.4 and later: */
#ifndef Py_CLEAR
#define Py_CLEAR(op) \
do { \
    if (op) { \
        PyObject *tmp = (PyObject *)(op); \
        (op) = NULL;     \
        Py_DECREF(tmp); \
    } \
} while (0)
#endif

#define DEFERRED_ADDRESS(ADDR) NULL
#define PyTrait_CheckExact(op) ((op)->ob_type == ctrait_type)

#define PyHasTraits_Check(op) PyObject_TypeCheck(op, &has_traits_type)
#define PyHasTraits_CheckExact(op) ((op)->ob_type == &has_traits_type)

/* Trait method related: */

#if PY_MAJOR_VERSION < 3
#define TP_DESCR_GET(t) \
    (PyType_HasFeature(t, Py_TPFLAGS_HAVE_CLASS) ? (t)->tp_descr_get : NULL)
#else
#define TP_DESCR_GET(t) \
    ((t)->tp_descr_get)
#endif

/* Notification related: */
#define has_notifiers(tnotifiers,onotifiers) \
    ((((tnotifiers) != NULL) && (PyList_GET_SIZE((tnotifiers))>0)) || \
     (((onotifiers) != NULL) && (PyList_GET_SIZE((onotifiers))>0)))

/* Python version dependent macros: */
#if ( (PY_MAJOR_VERSION == 2) && (PY_MINOR_VERSION < 3) )
#define PyMODINIT_FUNC void
#define PyDoc_VAR(name) static char name[]
#define PyDoc_STRVAR(name,str) PyDoc_VAR(name) = PyDoc_STR(str)
#ifdef WITH_DOC_STRINGS
#define PyDoc_STR(str) str
#else
#define PyDoc_STR(str) ""
#endif
#endif
#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

/*-----------------------------------------------------------------------------
|  Forward declarations:
+----------------------------------------------------------------------------*/

static PyTypeObject trait_type;
static PyTypeObject has_traits_type;

/*-----------------------------------------------------------------------------
|  'ctraits' module doc string:
+----------------------------------------------------------------------------*/

PyDoc_STRVAR( ctraits__doc__,
"The ctraits module defines the CHasTraits and CTrait C extension types that\n"
"define the core performance oriented portions of the Traits package." );

/*-----------------------------------------------------------------------------
|  HasTraits behavior modification flags:
+----------------------------------------------------------------------------*/

/* Object has been initialized: */
#define HASTRAITS_INITED      0x00000001

/* Do not send notifications when a trait changes value: */
#define HASTRAITS_NO_NOTIFY   0x00000002

/* Requests that no event notifications be sent when this object is assigned to
   a trait: */
#define HASTRAITS_VETO_NOTIFY 0x00000004

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
    PyObject_HEAD               /* Standard Python object header */
        PyDictObject * ctrait_dict; /* Class traits dictionary */
        PyDictObject * itrait_dict; /* Instance traits dictionary */
    PyListObject * notifiers;   /* List of 'any trait changed' notification
                                   handlers */
    int            flags;       /* Behavior modification flags */
        PyObject     * obj_dict;    /* Object attribute dictionary ('__dict__') */
                                /* NOTE: 'obj_dict' field MUST be last field */
} has_traits_object;

static int call_notifiers ( PyListObject *, PyListObject *,
                            has_traits_object *, PyObject *, PyObject *,
                            PyObject * new_value );

/*-----------------------------------------------------------------------------
|  'CTrait' flag values:
+----------------------------------------------------------------------------*/

/* The trait is a Property: */
#define TRAIT_PROPERTY 0x00000001

/* Should the delegate be modified (or the original object)? */
#define TRAIT_MODIFY_DELEGATE 0x00000002

/* Should a simple object identity test be performed (or a rich compare)? */
#define TRAIT_OBJECT_IDENTITY 0x00000004

/* Make 'setattr' store the original unvalidated value */
#define TRAIT_SETATTR_ORIGINAL_VALUE 0x00000008

/* Send the 'post_setattr' method the original unvalidated value */
#define TRAIT_POST_SETATTR_ORIGINAL_VALUE 0x00000010

/* Can a 'TraitValue' be assigned to override the trait definition? */
#define TRAIT_VALUE_ALLOWED 0x00000020

/* Is this trait a special 'TraitValue' trait that uses a property? */
#define TRAIT_VALUE_PROPERTY 0x00000040

/* Does this trait have an associated 'mapped' trait? */
#define TRAIT_IS_MAPPED 0x00000080

/* Should any old/new value test be performed before generating
   notifications? */
#define TRAIT_NO_VALUE_TEST 0x00000100


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


/*-----------------------------------------------------------------------------
|  'CTrait' instance definition:
+----------------------------------------------------------------------------*/

typedef struct _trait_object a_trait_object;
typedef PyObject * (*trait_getattr)( a_trait_object *, has_traits_object *,
                                     PyObject * );
typedef int (*trait_setattr)( a_trait_object *, a_trait_object *,
                              has_traits_object *, PyObject *, PyObject * );
typedef int (*trait_post_setattr)( a_trait_object *, has_traits_object *,
                                   PyObject *, PyObject * );
typedef PyObject * (*trait_validate)( a_trait_object *, has_traits_object *,
                              PyObject *, PyObject * );
typedef PyObject * (*delegate_attr_name_func)( a_trait_object *,
                                             has_traits_object *, PyObject * );

typedef struct _trait_object {
    PyObject_HEAD                    /* Standard Python object header */
    int                flags;        /* Flag bits */
    trait_getattr      getattr;      /* Get trait value handler */
    trait_setattr      setattr;      /* Set trait value handler */
    trait_post_setattr post_setattr; /* Optional post 'setattr' handler */
    PyObject *         py_post_setattr; /* Python-based post 'setattr' hndlr */
    trait_validate     validate;     /* Validate trait value handler */
    PyObject *         py_validate;  /* Python-based validate value handler */
    int                default_value_type; /* Type of default value: see the
                                              'default_value_for' function */
    PyObject *         default_value;   /* Default value for trait */
    PyObject *         delegate_name;   /* Optional delegate name */
                                        /* Also used for 'property get' */
    PyObject *         delegate_prefix; /* Optional delegate prefix */
                                        /* Also used for 'property set' */
    delegate_attr_name_func delegate_attr_name; /* Optional routine to return*/
                                  /* the computed delegate attribute name */
    PyListObject *     notifiers; /* Optional list of notification handlers */
    PyObject *         handler;   /* Associated trait handler object */
                                  /* NOTE: The 'obj_dict' field MUST be last */
    PyObject *         obj_dict;  /* Standard Python object dictionary */
} trait_object;

/* Forward declarations: */
static void trait_clone ( trait_object *, trait_object * );

static PyObject * has_traits_getattro ( has_traits_object * obj,
                                        PyObject          * name );

static int has_traits_setattro ( has_traits_object * obj,
                                 PyObject          * name,
                                 PyObject          * value );

static PyObject * get_trait ( has_traits_object * obj,
                              PyObject          * name,
                              int                 instance );

static int trait_property_changed ( has_traits_object * obj,
                                    PyObject          * name,
                                    PyObject          * old_value,
                                    PyObject          * new_value );

static int setattr_event ( trait_object      * traito,
                           trait_object      * traitd,
                           has_traits_object * obj,
                           PyObject          * name,
                           PyObject          * value );

static int setattr_disallow ( trait_object      * traito,
                              trait_object      * traitd,
                              has_traits_object * obj,
                              PyObject          * name,
                              PyObject          * value );

/*-----------------------------------------------------------------------------
|  Raise a TraitError:
+----------------------------------------------------------------------------*/

static PyObject *
raise_trait_error ( trait_object * trait, has_traits_object * obj,
                                    PyObject * name, PyObject * value ) {
    PyObject * result;

    /* Clear any current exception. We are handling it by raising
     * a TraitError. */
    PyErr_Clear();

    result = PyObject_CallMethod( trait->handler,
                                  "error", "(OOO)", obj, name, value );
    Py_XDECREF( result );
    return NULL;
}

/*-----------------------------------------------------------------------------
|  Raise a fatal trait error:
+----------------------------------------------------------------------------*/

static int
fatal_trait_error ( void ) {

    PyErr_SetString( TraitError, "Non-trait found in trait dictionary" );

    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an "attribute is not a string" error:
+----------------------------------------------------------------------------*/

static int
invalid_attribute_error ( PyObject * name ) {

#if PY_MAJOR_VERSION >= 3
    const char* fmt = "attribute name must be an instance of <type 'str'>. "
                      "Got %R (%.200s).";
    PyErr_Format(PyExc_TypeError, fmt, name, name->ob_type->tp_name);
#else
    // Python 2.6 doesn't support %R in PyErr_Format, so we compute and
    // insert the repr explicitly.
    const char* fmt = "attribute name must be an instance of <type 'str'>. "
                      "Got %.200s (%.200s).";
    PyObject *obj_repr;

    obj_repr = PyObject_Repr(name);
    if ( obj_repr == NULL ) {
        return -1;
    }
    PyErr_Format(PyExc_TypeError, fmt, PyString_AsString(obj_repr),
                 name->ob_type->tp_name);
    Py_DECREF( obj_repr );
#endif

    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an "invalid trait definition" error:
+----------------------------------------------------------------------------*/

static int
bad_trait_error ( void ) {

    PyErr_SetString( TraitError, "Invalid argument to trait constructor." );

    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an "cant set items error" error:
+----------------------------------------------------------------------------*/

static PyObject *
cant_set_items_error ( void ) {

    PyErr_SetString( TraitError, "Can not set a collection's '_items' trait." );

    return NULL;
}

/*-----------------------------------------------------------------------------
|  Raise an "invalid trait definition" error:
+----------------------------------------------------------------------------*/

static int
bad_trait_value_error ( void ) {

    PyErr_SetString( TraitError,
        "Result of 'as_ctrait' method was not a 'CTraits' instance." );

    return -1;
}


/*-----------------------------------------------------------------------------
|  Raise an invalid delegate error:
+----------------------------------------------------------------------------*/

static int
bad_delegate_error ( has_traits_object * obj, PyObject * name ) {

    if ( !Py2to3_SimpleString_Check( name ) ) {
        return invalid_attribute_error( name );
    }
    PyErr_Format(
        DelegationError,
        "The '%.400" Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'"
            " attribute of a '%.50s' object"
            " delegates to an attribute which is not a defined trait.",
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( name ),
        Py_TYPE(obj)->tp_name
    );
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an invalid delegate error:
+----------------------------------------------------------------------------*/

static int
bad_delegate_error2 ( has_traits_object * obj, PyObject * name ) {

    if ( !Py2to3_SimpleString_Check( name ) ) {
        return invalid_attribute_error( name );
    }

    PyErr_Format(
        DelegationError,
        "The '%.400" Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'"
            " attribute of a '%.50s' object"
            " has a delegate which does not have traits.",
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( name ),
        Py_TYPE(obj)->tp_name
    );
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise a delegation recursion error:
+----------------------------------------------------------------------------*/

static int
delegation_recursion_error ( has_traits_object * obj, PyObject * name ) {

    if ( !Py2to3_SimpleString_Check( name ) ) {
        return invalid_attribute_error( name );
    }

    PyErr_Format(
        DelegationError,
        "Delegation recursion limit exceeded while setting"
            " the '%.400" Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'"
            " attribute of a '%.50s' object.",
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( name ),
        Py_TYPE(obj)->tp_name
    );
    return -1;
}

static int
delegation_recursion_error2 ( has_traits_object * obj, PyObject * name ) {

    if ( !Py2to3_SimpleString_Check( name ) ) {
        return invalid_attribute_error( name );
    }

    PyErr_Format(
        DelegationError,
        "Delegation recursion limit exceeded while getting"
            " the definition of"
            " the '%.400" Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'"
            " attribute of a '%.50s' object.",
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( name ),
        Py_TYPE(obj)->tp_name
    );
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an attempt to delete read-only attribute error:
+----------------------------------------------------------------------------*/

static int
delete_readonly_error ( has_traits_object * obj, PyObject * name ) {

    if ( !Py2to3_SimpleString_Check( name ) ) {
        return invalid_attribute_error( name );
    }

    PyErr_Format(
        TraitError,
        "Cannot delete the read only '%.400" Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'"
            " attribute of a '%.50s' object.",
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( name ),
        Py_TYPE(obj)->tp_name
    );
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an attempt to set a read-only attribute error:
+----------------------------------------------------------------------------*/

static int
set_readonly_error ( has_traits_object * obj, PyObject * name ) {

    if ( !Py2to3_SimpleString_Check( name ) ) {
        return invalid_attribute_error( name );
    }

    PyErr_Format(
        TraitError,
        "Cannot modify the read only '%.400" Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'"
            " attribute of a '%.50s' object.",
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( name ),
        Py_TYPE(obj)->tp_name
    );
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an attempt to set an undefined attribute error:
+----------------------------------------------------------------------------*/

static int
set_disallow_error ( has_traits_object * obj, PyObject * name ) {

    PyObject *nname = Py2to3_NormaliseAttrName(name);
    if (nname == NULL) {
        return invalid_attribute_error( name );
    }

    PyErr_Format(
        TraitError,
        "Cannot set the undefined '%.400" Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'"
            " attribute of a '%.50s' object.",
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( nname ),
        Py_TYPE(obj)->tp_name
    );
    Py2to3_FinishNormaliseAttrName(name, nname);
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an attempt to delete a property error:
+----------------------------------------------------------------------------*/

static int
set_delete_property_error ( has_traits_object * obj, PyObject * name ) {

    if ( !Py2to3_SimpleString_Check( name ) ) {
        return invalid_attribute_error( name );
    }

    PyErr_Format(
        TraitError,
        "Cannot delete the '%.400" Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'"
            " property of a '%.50s' object.",
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( name ),
        Py_TYPE(obj)->tp_name
    );
    return -1;
}

/*-----------------------------------------------------------------------------
|  Raise an undefined attribute error:
+----------------------------------------------------------------------------*/

static void
unknown_attribute_error ( has_traits_object * obj, PyObject * name ) {

    PyErr_Format(
        PyExc_AttributeError,
        "'%.50s' object has no attribute '%.400" Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'",
        Py_TYPE(obj)->tp_name,
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( name )
    );
}

/*-----------------------------------------------------------------------------
|  Raise a '__dict__' must be set to a dictionary error:
+----------------------------------------------------------------------------*/

static int
dictionary_error ( void ) {

    PyErr_SetString( PyExc_TypeError,
                     "__dict__ must be set to a dictionary." );

    return -1;
}

/*-----------------------------------------------------------------------------
|  Gets/Sets a possibly NULL (or callable) value:
+----------------------------------------------------------------------------*/

static PyObject *
get_callable_value ( PyObject * value ) {
    PyObject * tuple, * temp;
    if ( value == NULL ) {
        value = Py_None;
        Py_INCREF( value );
    } else if ( PyCallable_Check( value ) ) {
        value = is_callable;
        Py_INCREF( value );
    } else if ( PyTuple_Check( value ) &&
              ( PyTuple_GET_SIZE( value ) >= 3 ) &&
              ( Py2to3_PyNum_AsLong( PyTuple_GET_ITEM( value, 0 ) ) == 10) ) {
        tuple = PyTuple_New( 3 );
        if ( tuple != NULL ) {
            PyTuple_SET_ITEM( tuple, 0, temp = PyTuple_GET_ITEM( value, 0 ) );
            Py_INCREF( temp );
            PyTuple_SET_ITEM( tuple, 1, temp = PyTuple_GET_ITEM( value, 1 ) );
            Py_INCREF( temp );
            PyTuple_SET_ITEM( tuple, 2, is_callable );
            Py_INCREF( is_callable );
            value = tuple;
        } else {
            value = NULL;
        }
    } else {
        Py_INCREF( value );
    }
    return value;
}

static PyObject *
get_value ( PyObject * value ) {
    if ( value == NULL )
        value = Py_None;
    Py_INCREF( value );
    return value;
}

static int
set_value ( PyObject ** field, PyObject * value ) {

    Py_INCREF( value );
    Py_XDECREF( *field );
    *field = value;
    return 0;
}

/*-----------------------------------------------------------------------------
|  Returns the result of calling a specified 'class' object with 1 argument:
+----------------------------------------------------------------------------*/

static PyObject *
call_class ( PyObject * class, trait_object * trait, has_traits_object * obj,
             PyObject * name, PyObject * value ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 4 );
    if ( args == NULL )
        return NULL;
    PyTuple_SET_ITEM( args, 0, trait->handler );
    PyTuple_SET_ITEM( args, 1, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 2, name );
    PyTuple_SET_ITEM( args, 3, value );
    Py_INCREF( trait->handler );
    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    result = PyObject_Call( class, args, NULL );
    Py_DECREF( args );
    return result;
}

/*-----------------------------------------------------------------------------
|  Attempts to get the value of a key in a 'known to be a dictionary' object:
+----------------------------------------------------------------------------*/

static PyObject *
dict_getitem ( PyDictObject * dict, PyObject *key ) {
#if !defined(Py_LIMITED_API) && (PY_MAJOR_VERSION < 3 || PY_MINOR_VERSION < 3)
    Py_hash_t hash;
#endif

    assert( PyDict_Check( dict ) );

#if !defined(Py_LIMITED_API) && (PY_MAJOR_VERSION < 3 || PY_MINOR_VERSION < 3)
    hash = Py2to3_GetHash_wCache( key );
    if ( hash == -1 ) {
        PyErr_Clear();
        return NULL;
    }

    return (dict->ma_lookup)( dict, key, hash )->me_value;
#else
    return PyDict_GetItem((PyObject *)dict,key);
#endif
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
+----------------------------------------------------------------------------*/

static trait_object *
get_prefix_trait ( has_traits_object * obj, PyObject * name, int is_set ) {

    PyObject * trait = PyObject_CallMethod( (PyObject *) obj,
                           "__prefix_trait__", "(Oi)", name, is_set );

    if ( trait != NULL ) {
        assert( obj->ctrait_dict != NULL );
            PyDict_SetItem( (PyObject *) obj->ctrait_dict, name, trait );
        Py_DECREF( trait );

        if ( has_traits_setattro( obj, trait_added, name ) < 0 )
            return NULL;

        trait = get_trait( obj, name, 0 );
        Py_DECREF( trait );
    }

    return (trait_object *) trait;
}

/*-----------------------------------------------------------------------------
|  Assigns a special TraitValue to a specified trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_value ( trait_object      * trait,
                has_traits_object * obj,
                PyObject          * name,
                PyObject          * value ) {

    PyDictObject * dict;
    PyObject * trait_new, * result, * obj_dict;
    PyObject * trait_old = NULL;
    PyObject * value_old = NULL;

    trait_new = PyObject_CallMethod( value, "as_ctrait", "(O)", trait );
    if ( trait_new == NULL )
        goto error2;

    if ( (trait_new != Py_None) && (!PyTrait_CheckExact( trait_new )) ) {
        Py_DECREF( trait_new );
        return bad_trait_value_error();
    }

    dict = obj->itrait_dict;
    if ( (dict != NULL) &&
         ((trait_old = dict_getitem( dict, name )) != NULL) &&
         ((((trait_object *) trait_old)->flags & TRAIT_VALUE_PROPERTY) != 0) ) {
        result = PyObject_CallMethod( trait_old, "_unregister",
                                      "(OO)", obj, name );
        if ( result == NULL )
            goto error1;

        Py_DECREF( result );
    }

    if ( trait_new == Py_None ) {
        if ( trait_old != NULL ) {
            PyDict_DelItem( (PyObject *) dict, name );
        }
        goto success;
    }

    if ( dict == NULL ) {
        obj->itrait_dict = dict = (PyDictObject *) PyDict_New();
        if ( dict == NULL )
            goto error1;
    }

    if ( (((trait_object *) trait_new)->flags & TRAIT_VALUE_PROPERTY) != 0 ) {
        if ( (value_old = has_traits_getattro( obj, name )) == NULL )
            goto error1;

        obj_dict = obj->obj_dict;
        if ( obj_dict != NULL )
            PyDict_DelItem( obj_dict, name );
    }

    if ( PyDict_SetItem( (PyObject *) dict, name, trait_new ) < 0 )
        goto error0;

    if ( (((trait_object *) trait_new)->flags & TRAIT_VALUE_PROPERTY) != 0 ) {
        result = PyObject_CallMethod( trait_new, "_register",
                                      "(OO)", obj, name );
        if ( result == NULL )
            goto error0;

        Py_DECREF( result );

        if ( trait_property_changed( obj, name, value_old, NULL ) )
            goto error0;

        Py_DECREF( value_old );
    }
success:
    Py_DECREF( trait_new );
    return 0;

error0:
    Py_XDECREF( value_old );
error1:
    Py_DECREF( trait_new );
error2:
    return -1;
}

/*-----------------------------------------------------------------------------
|  Handles the 'setattr' operation on a 'CHasTraits' instance:
+----------------------------------------------------------------------------*/

static int
has_traits_setattro ( has_traits_object * obj,
                      PyObject          * name,
                      PyObject          * value ) {

    trait_object * trait;

    if ( (obj->itrait_dict == NULL) ||
         ((trait = (trait_object *) dict_getitem( obj->itrait_dict, name )) ==
           NULL) ) {
        trait = (trait_object *) dict_getitem( obj->ctrait_dict, name );
        if ( (trait == NULL) &&
             ((trait = get_prefix_trait( obj, name, 1 )) == NULL) )
            return -1;
    }

    if ( ((trait->flags & TRAIT_VALUE_ALLOWED) != 0) &&
          (PyObject_IsInstance( value, TraitValue ) > 0) ) {
        return setattr_value( trait, obj, name, value );
    }

    return trait->setattr( trait, trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Allocates a CTrait instance:
+----------------------------------------------------------------------------*/

PyObject *
has_traits_new ( PyTypeObject * type, PyObject * args, PyObject * kwds ) {

    // Call PyBaseObject_Type.tp_new to do the actual construction.
    // This allows things like ABCMeta machinery to work correctly
    // which is implemented at the C level.
    has_traits_object * obj = (has_traits_object *) PyBaseObject_Type.tp_new(type, empty_tuple, empty_dict);
    if ( obj != NULL ) {
        if (type->tp_dict == NULL) {
            PyErr_SetString(PyExc_RuntimeError, "No tp_dict");
            return NULL;
        }
        obj->ctrait_dict = (PyDictObject *) PyDict_GetItem( type->tp_dict,
                                                            class_traits );
        if (obj->ctrait_dict == NULL) {
            PyErr_SetString(PyExc_RuntimeError, "No ctrait_dict");
            return NULL;
        }
        if (!PyDict_Check( (PyObject *) obj->ctrait_dict ) ) {
            PyErr_SetString(PyExc_RuntimeError, "ctrait_dict not a dict");
            return NULL;
        }
        Py_INCREF( obj->ctrait_dict );
    }

    return (PyObject *) obj;
}

int
has_traits_init ( PyObject * obj, PyObject * args, PyObject * kwds ) {

    PyObject * key;
    PyObject * value;
    int has_listeners;
    Py_ssize_t i = 0;

    /* Make sure no non-keyword arguments were specified: */
    if ( !PyArg_ParseTuple( args, "" ) )
        return -1;

    /* Make sure all of the object's listeners have been set up: */
    has_listeners = (PyMapping_Size( PyDict_GetItem( obj->ob_type->tp_dict,
                                     listener_traits ) ) > 0);
    if ( has_listeners ) {
        value = PyObject_CallMethod( obj, "_init_trait_listeners", "()" );
        if ( value == NULL )
            return -1;

        Py_DECREF( value );
    }

    /* Set any traits specified in the constructor: */
    if ( kwds != NULL ) {
        while ( PyDict_Next( kwds, &i, &key, &value ) ) {
            if ( has_traits_setattro( (has_traits_object *) obj, key, value )
                 == -1 )
                return -1;
        }
    }

    /* Make sure all post constructor argument assignment listeners have been
       set up: */
    if ( has_listeners ) {
        value = PyObject_CallMethod( obj, "_post_init_trait_listeners", "()" );
        if ( value == NULL )
            return -1;

        Py_DECREF( value );
    }

    /* Call the 'traits_init' method to finish up initialization: */
    value = PyObject_CallMethod( obj, "traits_init", "()" );
    if ( value == NULL )
        return -1;

    Py_DECREF( value );

    /* Indicate that the object has finished being initialized: */
    ((has_traits_object *) obj)->flags |= HASTRAITS_INITED;

    return 0;
}

/*-----------------------------------------------------------------------------
|  Object clearing method:
+----------------------------------------------------------------------------*/

static int
has_traits_clear ( has_traits_object * obj ) {

    Py_CLEAR( obj->ctrait_dict );
    Py_CLEAR( obj->itrait_dict );
    Py_CLEAR( obj->notifiers );
    Py_CLEAR( obj->obj_dict );

    return 0;
}

/*-----------------------------------------------------------------------------
|  Deallocates an unused 'CHasTraits' instance:
+----------------------------------------------------------------------------*/

static void
has_traits_dealloc ( has_traits_object * obj ) {

    PyObject_GC_UnTrack(obj);
    Py_TRASHCAN_SAFE_BEGIN(obj);
    has_traits_clear( obj );
    Py_TYPE(obj)->tp_free( (PyObject *) obj );
    Py_TRASHCAN_SAFE_END(obj);
}

/*-----------------------------------------------------------------------------
|  Garbage collector traversal method:
+----------------------------------------------------------------------------*/

static int
has_traits_traverse ( has_traits_object * obj, visitproc visit, void * arg ) {

    Py_VISIT( obj->ctrait_dict );
    Py_VISIT( obj->itrait_dict );
    Py_VISIT( obj->notifiers );
    Py_VISIT( obj->obj_dict );

        return 0;
}

/*-----------------------------------------------------------------------------
|  Handles the 'getattr' operation on a 'CHasTraits' instance:
+----------------------------------------------------------------------------*/

static PyObject *
has_traits_getattro ( has_traits_object * obj, PyObject * name ) {

    trait_object * trait;
    PyObject *value;
    PyObject *bad_attr_marker;
    /* The following is a performance hack to short-circuit the normal
       look-up when the value is in the object's dictionary.
*/
    PyDictObject * dict = (PyDictObject *) obj->obj_dict;

    if ( dict != NULL ) {
        assert( PyDict_Check( dict ) );

        bad_attr_marker = name;
        value = Py2to3_GetAttrDictValue(dict, name, bad_attr_marker);
        // there is a slight performance-hit here:
        // Py2to3_GetAttrDictValue cannot signal invalid attributes
        // unambiguously, so we have to reckeck in case the marker value is
        // returned. Make sure to pick an unlikely marker value.
        if((value==bad_attr_marker) && !Py2to3_AttrNameCheck(name)) {
            invalid_attribute_error( name );
            return NULL;
        }
        if( value != NULL ){
            Py_INCREF( value );
            return value;
        }
    }
    /* End of performance hack */

    if ( ((obj->itrait_dict != NULL) &&
         ((trait = (trait_object *) dict_getitem( obj->itrait_dict, name )) !=
          NULL)) ||
         ((trait = (trait_object *) dict_getitem( obj->ctrait_dict, name )) !=
          NULL) )
    {
        return trait->getattr( trait, obj, name );
    }

    if ( (value = PyObject_GenericGetAttr( (PyObject *) obj, name )) != NULL )
        return value;

    PyErr_Clear();

    if ( (trait = get_prefix_trait( obj, name, 0 )) != NULL )
        return trait->getattr( trait, obj, name );

    return NULL;
}


/*-----------------------------------------------------------------------------
|  Returns (and optionally creates) a specified instance or class trait:
+----------------------------------------------------------------------------*/

static PyObject *
get_trait ( has_traits_object * obj, PyObject * name, int instance ) {

    int i, n;
    PyDictObject * itrait_dict;
    trait_object * trait;
    trait_object * itrait;
    PyListObject * notifiers;
    PyListObject * inotifiers;
    PyObject     * item;

    /* If there already is an instance specific version of the requested trait,
       then return it: */
    itrait_dict = obj->itrait_dict;
    if ( itrait_dict != NULL ) {
        trait = (trait_object *) dict_getitem( itrait_dict, name );
        if ( trait != NULL ) {
            assert( PyTrait_CheckExact( trait ) );
            Py_INCREF( trait );
            return (PyObject *) trait;
        }
    }

    /* If only an instance trait can be returned (but not created), then
       return None: */
    if ( instance == 1 ) {
        Py_INCREF( Py_None );
        return Py_None;
    }

    /* Otherwise, get the class specific version of the trait (creating a
       trait class version if necessary): */
    assert( obj->ctrait_dict != NULL );
    trait = (trait_object *) dict_getitem( obj->ctrait_dict, name );
    if ( trait == NULL ) {
        if ( instance == 0 ) {
            Py_INCREF( Py_None );
            return Py_None;
        }
        if ( (trait = get_prefix_trait( obj, name, 0 )) == NULL )
            return NULL;
    }

    assert( PyTrait_CheckExact( trait ) );

    /* If an instance specific trait is not needed, return the class trait: */
    if ( instance <= 0 ) {
        Py_INCREF( trait );
        return (PyObject *) trait;
    }

    /* Otherwise, create an instance trait dictionary if it does not exist: */
    if ( itrait_dict == NULL ) {
                obj->itrait_dict = itrait_dict = (PyDictObject *) PyDict_New();
                if ( itrait_dict == NULL )
            return NULL;
    }

    /* Create a new instance trait and clone the class trait into it: */
    itrait = (trait_object *) PyType_GenericAlloc( ctrait_type, 0 );
    trait_clone( itrait, trait );
    itrait->obj_dict = trait->obj_dict;
    Py_XINCREF( itrait->obj_dict );

    /* Copy the class trait's notifier list into the instance trait: */
    if ( (notifiers = trait->notifiers) != NULL ) {
        n = PyList_GET_SIZE( notifiers );
        itrait->notifiers = inotifiers = (PyListObject *) PyList_New( n );
        if ( inotifiers == NULL )
            return NULL;

        for ( i = 0; i < n; i++ ) {
            item = PyList_GET_ITEM( notifiers, i );
            PyList_SET_ITEM( inotifiers, i, item );
            Py_INCREF( item );
        }
    }

    /* Add the instance trait to the instance's trait dictionary and return
       the instance trait if successful: */
    if ( PyDict_SetItem( (PyObject *) itrait_dict, name,
                         (PyObject *) itrait ) >= 0 )
        return (PyObject *) itrait;

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
_has_traits_trait ( has_traits_object * obj, PyObject * args ) {

    has_traits_object * delegate;
    has_traits_object * temp_delegate;
    trait_object      * trait;
    PyObject          * name;
    PyObject          * daname;
    PyObject          * daname2;
    PyObject          * dict;
    int i, instance;

    /* Parse arguments, which specify the trait name and whether or not an
       instance specific version of the trait is needed or not: */
        if ( !PyArg_ParseTuple( args, "Oi", &name, &instance ) )
        return NULL;

    trait = (trait_object *) get_trait( obj, name, instance );
    if ( (instance >= -1) || (trait == NULL) )
        return (PyObject *) trait;

    /* Follow the delegation chain until we find a non-delegated trait: */
    delegate = obj;
    Py_INCREF( delegate );

    daname = name;
    Py_INCREF( daname );
    for ( i = 0; ; ) {

        if ( trait->delegate_attr_name == NULL ) {
            Py_DECREF( delegate );
            Py_DECREF( daname );
            return (PyObject *) trait;
        }

        dict = delegate->obj_dict;

        temp_delegate = NULL;
        if (dict != NULL) {
            temp_delegate = (has_traits_object *) PyDict_GetItem(
                dict, trait->delegate_name );
            /* PyDict_GetItem returns a borrowed reference,
               so we need to INCREF. */
            Py_XINCREF( temp_delegate );
        }
        if (temp_delegate == NULL) {
            /* has_traits_getattro returns a new reference,
               so no need to INCREF. */
            temp_delegate = (has_traits_object *) has_traits_getattro(
                delegate, trait->delegate_name );
        }
        if (temp_delegate == NULL) {
            break;
        }
        Py_DECREF( delegate );
        delegate = temp_delegate;

        if ( !PyHasTraits_Check( delegate ) ) {
            bad_delegate_error2( obj, name );
            break;
        }

        daname2 = trait->delegate_attr_name( trait, obj, daname );
        Py_DECREF( daname );
        daname = daname2;
        Py_DECREF( trait );
        if ( ((delegate->itrait_dict == NULL) ||
              ((trait = (trait_object *) dict_getitem( delegate->itrait_dict,
                      daname )) == NULL)) &&
             ((trait = (trait_object *) dict_getitem( delegate->ctrait_dict,
                      daname )) == NULL) &&
             ((trait = get_prefix_trait( delegate, daname2, 0 )) == NULL) ) {
            bad_delegate_error( obj, name );
            break;
        }

        if ( Py_TYPE(trait) != ctrait_type ) {
            fatal_trait_error();
            break;
        }

        if ( ++i >= 100 ) {
            delegation_recursion_error2( obj, name );
            break;
        }

        Py_INCREF( trait );
    }
    Py_DECREF( delegate );
    Py_DECREF( daname );

    return NULL;
}

/*-----------------------------------------------------------------------------
|  Calls notifiers when a trait 'property' is explicitly changed:
+----------------------------------------------------------------------------*/

static int
trait_property_changed ( has_traits_object * obj, PyObject * name,
                         PyObject * old_value, PyObject * new_value ) {

    trait_object * trait;
    PyListObject * tnotifiers;
    PyListObject * onotifiers;
    int null_new_value;
    int rc = 0;

    if ( (trait = (trait_object *) get_trait( obj, name, -1 )) == NULL )
        return -1;

    tnotifiers = trait->notifiers;
    onotifiers = obj->notifiers;
    Py_DECREF( trait );

    if ( has_notifiers( tnotifiers, onotifiers ) ) {

        null_new_value = (new_value == NULL);
        if ( null_new_value ) {
           new_value = has_traits_getattro( obj, name );
           if ( new_value == NULL )
               return -1;
        }

        rc = call_notifiers( tnotifiers, onotifiers, obj, name,
                             old_value, new_value );

        if ( null_new_value ) {
            Py_DECREF( new_value );
        }
    }

    return rc;
}

/*-----------------------------------------------------------------------------
|  Calls notifiers when a trait 'property' is explicitly changed:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_property_changed ( has_traits_object * obj, PyObject * args ) {

    PyObject * name, * old_value;
    PyObject * new_value = NULL;

    /* Parse arguments, which specify the name of the changed trait, the
       previous value, and the new value: */
        if ( !PyArg_ParseTuple( args, "OO|O", &name, &old_value, &new_value ) )
        return NULL;

    if ( trait_property_changed( obj, name, old_value, new_value ) )
        return NULL;

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Handles firing a traits 'xxx_items' event:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_items_event ( has_traits_object * obj, PyObject * args ) {

    PyObject * name;
    PyObject * event_object;
    PyObject * event_trait;
    PyObject * result;
    trait_object * trait;
    int can_retry = 1;

        if ( !PyArg_ParseTuple( args, "OOO", &name, &event_object, &event_trait ) )
        return NULL;

    if ( !PyTrait_CheckExact( event_trait ) ) {
        bad_trait_value_error();
        return NULL;
    }

    if ( !Py2to3_AttrNameCheck( name ) ) {
        invalid_attribute_error( name );
        return NULL;
    }
retry:
    if ( ((obj->itrait_dict == NULL) ||
          ((trait = (trait_object *) dict_getitem( obj->itrait_dict, name )) ==
            NULL)) &&
          ((trait = (trait_object *) dict_getitem( obj->ctrait_dict, name )) ==
            NULL) ) {
add_trait:
        if ( !can_retry )
            return cant_set_items_error();

        result = PyObject_CallMethod( (PyObject *) obj, "add_trait",
                                      "(OO)", name, event_trait );
        if ( result == NULL )
            return NULL;

        Py_DECREF( result );
        can_retry = 0;
        goto retry;
    }

    if ( trait->setattr == setattr_disallow )
        goto add_trait;

    if ( trait->setattr( trait, trait, obj, name, event_object ) < 0 )
        return NULL;

    Py_INCREF( Py_None );

    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Enables/Disables trait change notification for the object:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_change_notify ( has_traits_object * obj, PyObject * args ) {

    int enabled;

    /* Parse arguments, which specify the new trait notification
       enabled/disabled state: */
        if ( !PyArg_ParseTuple( args, "i", &enabled ) )
        return NULL;

    if ( enabled ) {
        obj->flags &= (~HASTRAITS_NO_NOTIFY);
    } else {
        obj->flags |= HASTRAITS_NO_NOTIFY;
    }

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Enables/Disables trait change notifications when this object is assigned to
|  a trait:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_veto_notify ( has_traits_object * obj, PyObject * args ) {

    int enabled;

    /* Parse arguments, which specify the new trait notification veto
       enabled/disabled state: */
        if ( !PyArg_ParseTuple( args, "i", &enabled ) )
        return NULL;

    if ( enabled ) {
        obj->flags |= HASTRAITS_VETO_NOTIFY;
    } else {
        obj->flags &= (~HASTRAITS_VETO_NOTIFY);
    }

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  This method is called at the end of a HasTraits constructor and the
|  __setstate__ method to perform any final object initialization needed.
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_init ( has_traits_object * obj ) {

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Returns whether or not the object has finished being initialized:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_inited ( has_traits_object * obj, PyObject * args ) {

    int traits_inited = -1;

        if ( !PyArg_ParseTuple( args, "|i", &traits_inited ) )
        return NULL;

    if ( traits_inited > 0 )
        obj->flags |= HASTRAITS_INITED;

    if ( obj->flags & HASTRAITS_INITED ) {
        Py_INCREF( Py_True );
        return Py_True;
    }
    Py_INCREF( Py_False );
    return Py_False;
}

/*-----------------------------------------------------------------------------
|  Returns the instance trait dictionary:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_instance_traits ( has_traits_object * obj, PyObject * args ) {

        if ( !PyArg_ParseTuple( args, "" ) )
        return NULL;

    if ( obj->itrait_dict == NULL )
                obj->itrait_dict = (PyDictObject *) PyDict_New();

    Py_XINCREF( obj->itrait_dict );

    return (PyObject *) obj->itrait_dict;
}

/*-----------------------------------------------------------------------------
|  Returns (and optionally creates) the anytrait 'notifiers' list:
+----------------------------------------------------------------------------*/

static PyObject *
_has_traits_notifiers ( has_traits_object * obj, PyObject * args ) {

    PyObject * result;
    PyObject * list;
    int force_create;

    if ( !PyArg_ParseTuple( args, "i", &force_create ) )
        return NULL;

    result = (PyObject *) obj->notifiers;
    if ( result == NULL ) {
        if ( force_create ) {
            list = PyList_New(0);
            if (list == NULL)
                return NULL;
            obj->notifiers = (PyListObject *)list;
            result = list;
        }
        else {
            result = Py_None;
        }
    }
    Py_INCREF( result );
    return result;
}

/*-----------------------------------------------------------------------------
|  Returns the object's instance dictionary:
+----------------------------------------------------------------------------*/

static PyObject *
get_has_traits_dict ( has_traits_object * obj, void * closure ) {

    PyObject * obj_dict = obj->obj_dict;
    if ( obj_dict == NULL ) {
        obj->obj_dict = obj_dict = PyDict_New();
        if ( obj_dict == NULL )
            return NULL;
    }
    Py_INCREF( obj_dict );

    return obj_dict;
}

/*-----------------------------------------------------------------------------
|  Sets the object's dictionary:
+----------------------------------------------------------------------------*/

static int
set_has_traits_dict ( has_traits_object * obj, PyObject * value,
                      void * closure ) {

    if ( !PyDict_Check( value ) )
        return dictionary_error();

    return set_value( &obj->obj_dict, value );
}

/*-----------------------------------------------------------------------------
|  'CHasTraits' instance methods:
+----------------------------------------------------------------------------*/

static PyMethodDef has_traits_methods[] = {
        { "trait_property_changed", (PyCFunction) _has_traits_property_changed,
      METH_VARARGS,
      PyDoc_STR( "trait_property_changed(name,old_value[,new_value])" ) },
        { "trait_items_event", (PyCFunction) _has_traits_items_event, METH_VARARGS,
      PyDoc_STR( "trait_items_event(event_trait,name,items_event)" ) },
        { "_trait_change_notify", (PyCFunction) _has_traits_change_notify,
      METH_VARARGS,
      PyDoc_STR( "_trait_change_notify(boolean)" ) },
        { "_trait_veto_notify", (PyCFunction) _has_traits_veto_notify,
      METH_VARARGS,
      PyDoc_STR( "_trait_veto_notify(boolean)" ) },
        { "traits_init", (PyCFunction) _has_traits_init,
      METH_NOARGS,
      PyDoc_STR( "traits_init()" ) },
        { "traits_inited", (PyCFunction) _has_traits_inited,       METH_VARARGS,
      PyDoc_STR( "traits_inited([True])" ) },
        { "_trait",           (PyCFunction) _has_traits_trait,     METH_VARARGS,
      PyDoc_STR( "_trait(name,instance) -> trait" ) },
        { "_instance_traits", (PyCFunction) _has_traits_instance_traits,
      METH_VARARGS,
      PyDoc_STR( "_instance_traits() -> dict" ) },
        { "_notifiers",       (PyCFunction) _has_traits_notifiers, METH_VARARGS,
      PyDoc_STR( "_notifiers(force_create) -> list" ) },
        { NULL, NULL },
};

/*-----------------------------------------------------------------------------
|  'CHasTraits' property definitions:
+----------------------------------------------------------------------------*/

static PyGetSetDef has_traits_properties[] = {
        { "__dict__",  (getter) get_has_traits_dict,
                   (setter) set_has_traits_dict },
        { 0 }
};

/*-----------------------------------------------------------------------------
|  'CHasTraits' type definition:
+----------------------------------------------------------------------------*/

static PyTypeObject has_traits_type = {
        PyVarObject_HEAD_INIT( DEFERRED_ADDRESS( &PyType_Type ), 0)
        "traits.ctraits.CHasTraits",
        sizeof( has_traits_object ),
        0,
        (destructor) has_traits_dealloc,                    /* tp_dealloc */
        0,                                                  /* tp_print */
        0,                                                  /* tp_getattr */
        0,                                                  /* tp_setattr */
        0,                                                  /* tp_compare */
        0,                                                  /* tp_repr */
        0,                                                  /* tp_as_number */
        0,                                                  /* tp_as_sequence */
        0,                                                  /* tp_as_mapping */
        0,                                                  /* tp_hash */
        0,                                                  /* tp_call */
        0,                                                  /* tp_str */
        (getattrofunc) has_traits_getattro,                 /* tp_getattro */
        (setattrofunc) has_traits_setattro,                 /* tp_setattro */
        0,                                                                      /* tp_as_buffer */
        Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,/* tp_flags */
        0,                                                  /* tp_doc */
        (traverseproc) has_traits_traverse,                 /* tp_traverse */
        (inquiry) has_traits_clear,                         /* tp_clear */
        0,                                                  /* tp_richcompare */
        0,                                                  /* tp_weaklistoffset */
        0,                                                  /* tp_iter */
        0,                                                  /* tp_iternext */
        has_traits_methods,                                 /* tp_methods */
        0,                                                  /* tp_members */
        has_traits_properties,                              /* tp_getset */
        DEFERRED_ADDRESS( &PyBaseObject_Type ),             /* tp_base */
        0,                                                                      /* tp_dict */
        0,                                                                      /* tp_descr_get */
        0,                                                                      /* tp_descr_set */
        sizeof( has_traits_object ) - sizeof( PyObject * ), /* tp_dictoffset */
        has_traits_init,                                    /* tp_init */
        DEFERRED_ADDRESS( PyType_GenericAlloc ),            /* tp_alloc */
        has_traits_new                                      /* tp_new */
};

/*-----------------------------------------------------------------------------
|  Returns the default value associated with a specified trait:
+----------------------------------------------------------------------------*/

static PyObject *
default_value_for ( trait_object      * trait,
                    has_traits_object * obj,
                    PyObject          * name ) {

    PyObject * result = NULL, * value, * dv, * kw, * tuple;

    switch ( trait->default_value_type ) {
        case CONSTANT_DEFAULT_VALUE:
        case MISSING_DEFAULT_VALUE:
            result = trait->default_value;
            if (result == NULL) {
                result = Py_None;
            }
            Py_INCREF( result );
            break;
        case OBJECT_DEFAULT_VALUE:
            result = (PyObject *) obj;
            Py_INCREF( obj );
            break;
        case LIST_COPY_DEFAULT_VALUE:
            return PySequence_List( trait->default_value );
        case DICT_COPY_DEFAULT_VALUE:
            return PyDict_Copy( trait->default_value );
        case TRAIT_LIST_OBJECT_DEFAULT_VALUE:
            return call_class( TraitListObject, trait, obj, name,
                               trait->default_value );
        case TRAIT_DICT_OBJECT_DEFAULT_VALUE:
            return call_class( TraitDictObject, trait, obj, name,
                               trait->default_value );
        case CALLABLE_AND_ARGS_DEFAULT_VALUE:
            dv = trait->default_value;
            kw = PyTuple_GET_ITEM( dv, 2 );
            if ( kw == Py_None )
                kw = NULL;
            return PyObject_Call( PyTuple_GET_ITEM( dv, 0 ),
                                  PyTuple_GET_ITEM( dv, 1 ), kw );
        case CALLABLE_DEFAULT_VALUE:
            if ( (tuple = PyTuple_New( 1 )) == NULL )
                return NULL;
            PyTuple_SET_ITEM( tuple, 0, (PyObject *) obj );
            Py_INCREF( obj );
            result = PyObject_Call( trait->default_value, tuple, NULL );
            Py_DECREF( tuple );
            if ( (result != NULL) && (trait->validate != NULL) ) {
                value = trait->validate( trait, obj, name, result );
                Py_DECREF( result );
                return value;
            }
            break;
        case TRAIT_SET_OBJECT_DEFAULT_VALUE:
            return call_class( TraitSetObject, trait, obj, name,
                               trait->default_value );
    }
    return result;
}

/*-----------------------------------------------------------------------------
|  Returns the value assigned to a standard Python attribute:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_python ( trait_object      * trait,
                 has_traits_object * obj,
                 PyObject          * name ) {

    return PyObject_GenericGetAttr( (PyObject *) obj, name );
}

/*-----------------------------------------------------------------------------
|  Returns the value assigned to a generic Python attribute:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_generic ( trait_object      * trait,
                  has_traits_object * obj,
                  PyObject          * name ) {

    return PyObject_GenericGetAttr( (PyObject *) obj, name );
}

/*-----------------------------------------------------------------------------
|  Returns the value assigned to an event trait:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_event ( trait_object      * trait,
                has_traits_object * obj,
                PyObject          * name ) {

    PyErr_Format( PyExc_AttributeError,
        "The %.400" Py2to3_PYERR_SIMPLE_STRING_FMTCHR
            " trait of a %.50s instance is an 'event', which is write only.",
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( name ), Py_TYPE(obj)->tp_name );

    return NULL;
}

/*-----------------------------------------------------------------------------
|  Returns the value assigned to a standard trait:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_trait ( trait_object      * trait,
                has_traits_object * obj,
                PyObject          * name ) {

    int rc;
    PyListObject * tnotifiers;
    PyListObject * onotifiers;
    PyObject * result;
    PyObject * nname;
    PyObject * dict = obj->obj_dict;

    if ( dict == NULL ) {
        dict = PyDict_New();
        if ( dict == NULL )
            return NULL;

        obj->obj_dict = dict;
        }

        if ( Py2to3_SimpleString_Check( name ) ) {
        if ( (result = default_value_for( trait, obj, name )) != NULL ) {
            if ( PyDict_SetItem( dict, name, result ) >= 0 ) {

                rc = 0;
                if ( (trait->post_setattr != NULL) &&
                     ((trait->flags & TRAIT_IS_MAPPED) == 0) )
                    rc = trait->post_setattr( trait, obj, name, result );

                if (rc == 0) {
                    tnotifiers = trait->notifiers;
                    onotifiers = obj->notifiers;
                    if ( has_notifiers( tnotifiers, onotifiers ) )
                        rc = call_notifiers( tnotifiers, onotifiers, obj, name,
                                             Uninitialized, result );
                }
                if ( rc == 0 )
                    return result;
            }
            Py_DECREF( result );
        }

        return NULL;
    }

    nname = Py2to3_NormaliseAttrName(name);

    if( nname == NULL ){
        invalid_attribute_error( name );
        return NULL;
    }

    if ( (result = default_value_for( trait, obj, nname )) != NULL ) {
        if ( PyDict_SetItem( dict, nname, result ) >= 0 ) {

            rc = 0;
            if ( (trait->post_setattr != NULL) &&
                 ((trait->flags & TRAIT_IS_MAPPED) == 0) )
                rc = trait->post_setattr( trait, obj, nname, result );

            if (rc == 0) {
                tnotifiers = trait->notifiers;
                onotifiers = obj->notifiers;
                if ( has_notifiers( tnotifiers, onotifiers ) )
                    rc = call_notifiers( tnotifiers, onotifiers, obj, nname,
                                         Uninitialized, result );
            }
            if ( rc == 0 ){
                Py2to3_FinishNormaliseAttrName(name,nname);
                return result;
            }
        }
        Py_DECREF( result );
    }

    if ( PyErr_ExceptionMatches( PyExc_KeyError ) )
        PyErr_SetObject( PyExc_AttributeError, nname );

    Py2to3_FinishNormaliseAttrName(name,nname);
    Py_DECREF( name );
    return NULL;
}

/*-----------------------------------------------------------------------------
|  Returns the value assigned to a delegated trait:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_delegate ( trait_object      * trait,
                   has_traits_object * obj,
                   PyObject          * name ) {

    PyTypeObject * tp;
    PyObject     * delegate_attr_name;
    PyObject     * delegate;
    PyObject     * result;
    PyObject     * nname;
    PyObject     * dict = obj->obj_dict;

    if ( (dict == NULL) ||
         ((delegate = PyDict_GetItem( dict, trait->delegate_name )) == NULL) ){
        // Handle the case when the delegate is not in the instance dictionary
        // (could be a method that returns the real delegate):
        delegate = has_traits_getattro( obj, trait->delegate_name );
        if ( delegate == NULL )
            return NULL;
    } else {
        Py_INCREF( delegate );
    }

    nname = Py2to3_NormaliseAttrName(name);

    if( nname == NULL ){
        invalid_attribute_error( name );
        Py_DECREF( delegate );
        return NULL;
    }

    delegate_attr_name = trait->delegate_attr_name( trait, obj, nname );
    tp = Py_TYPE(delegate);

    if ( tp->tp_getattro != NULL ) {
        result = (*tp->tp_getattro)( delegate, delegate_attr_name );
        goto done;
    }

    if ( tp->tp_getattr != NULL ) {
        PyObject *delegate_attr_name_c_str = Py2to3_AttrNameCStr( delegate_attr_name );
        if(delegate_attr_name_c_str == NULL){
            result = NULL;
        } else {
            result = (*tp->tp_getattr)( delegate,
                             Py2to3_AttrName_AS_STRING( delegate_attr_name_c_str ) );
            Py2to3_FinishAttrNameCStr(delegate_attr_name_c_str);
            goto done;
        }
    }

    PyErr_Format( DelegationError,
        "The '%.50s' object has no attribute '%.400"
            Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'"
            " because its %.50s delegate has no attribute '%.400"
            Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'.",
        Py_TYPE(obj)->tp_name,
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( name ),
        tp->tp_name,
        Py2to3_PYERR_PREPARE_SIMPLE_STRING( delegate_attr_name )
    );
    result = NULL;

done:
    Py_DECREF( delegate_attr_name );
    Py2to3_FinishNormaliseAttrName(name,nname);
    Py_DECREF( delegate );
    return result;
}

/*-----------------------------------------------------------------------------
|  Raises an exception when a disallowed trait is accessed:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_disallow ( trait_object      * trait,
                   has_traits_object * obj,
                   PyObject          * name ) {

    if ( Py2to3_SimpleString_Check( name ) )
        unknown_attribute_error( obj, name );
    else
        invalid_attribute_error( name );

    return NULL;
}

/*-----------------------------------------------------------------------------
|  Returns the value of a constant trait:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_constant ( trait_object      * trait,
                   has_traits_object * obj,
                   PyObject          * name ) {

    Py_INCREF( trait->default_value );
    return trait->default_value;
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified property trait attribute:
+----------------------------------------------------------------------------*/

static PyObject *
getattr_property0 ( trait_object      * trait,
                    has_traits_object * obj,
                    PyObject          * name ) {

    return PyObject_Call( trait->delegate_name, empty_tuple, NULL );
}

static PyObject *
getattr_property1 ( trait_object      * trait,
                    has_traits_object * obj,
                    PyObject          * name ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 1 );
    if ( args == NULL )
        return NULL;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    Py_INCREF( obj );
    result = PyObject_Call( trait->delegate_name, args, NULL );
    Py_DECREF( args );

    return result;
}

static PyObject *
getattr_property2 ( trait_object      * trait,
                    has_traits_object * obj,
                    PyObject          * name ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 2 );
    if ( args == NULL )
        return NULL;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    Py_INCREF( obj );
    PyTuple_SET_ITEM( args, 1, name );
    Py_INCREF( name );
    result = PyObject_Call( trait->delegate_name, args, NULL );
    Py_DECREF( args );

    return result;
}

static PyObject *
getattr_property3 ( trait_object      * trait,
                    has_traits_object * obj,
                    PyObject          * name ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 3 );
    if ( args == NULL )
        return NULL;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    Py_INCREF( obj );
    PyTuple_SET_ITEM( args, 1, name );
    Py_INCREF( name );
    PyTuple_SET_ITEM( args, 2, (PyObject *) trait );
    Py_INCREF( trait );
    result = PyObject_Call( trait->delegate_name, args, NULL );
    Py_DECREF( args );

    return result;
}

static trait_getattr getattr_property_handlers[] = {
    getattr_property0, getattr_property1, getattr_property2, getattr_property3
};

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified standard Python attribute:
+----------------------------------------------------------------------------*/

static int
setattr_python ( trait_object      * traito,
                 trait_object      * traitd,
                 has_traits_object * obj,
                 PyObject          * name,
                 PyObject          * value ) {

    PyObject *nname;
    PyObject * dict = obj->obj_dict;

    if ( value != NULL ) {
        if ( dict == NULL ) {
            dict = PyDict_New();
            if ( dict == NULL )
                return -1;
                obj->obj_dict = dict;
        }

        nname = Py2to3_NormaliseAttrName( name );
        if( nname == NULL )
            return invalid_attribute_error( name );

        if ( PyDict_SetItem( dict, nname, value ) >= 0 ){
            Py2to3_FinishNormaliseAttrName(name,nname);
            return 0;
        }
        if ( PyErr_ExceptionMatches( PyExc_KeyError ) )
            PyErr_SetObject( PyExc_AttributeError, nname );

        Py2to3_FinishNormaliseAttrName(name,nname);
        return -1;
    }

    if ( dict != NULL ) {
        PyObject *nname = Py2to3_NormaliseAttrName( name );
        if( nname == NULL )
            return invalid_attribute_error( name );

        if ( PyDict_DelItem( dict, nname ) >= 0 ){
            Py2to3_FinishNormaliseAttrName(name,nname);
            return 0;
        }

        if ( PyErr_ExceptionMatches( PyExc_KeyError ) )
            unknown_attribute_error( obj, nname );

        Py2to3_FinishNormaliseAttrName(name,nname);
        return -1;
    }

    if ( Py2to3_SimpleString_Check( name ) ) {
        unknown_attribute_error( obj, name );

        return -1;
    }

    return invalid_attribute_error( name );
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified generic Python attribute:
+----------------------------------------------------------------------------*/

static int
setattr_generic ( trait_object      * traito,
                  trait_object      * traitd,
                  has_traits_object * obj,
                  PyObject          * name,
                  PyObject          * value ) {

    return PyObject_GenericSetAttr( (PyObject *) obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Call all notifiers for a specified trait:
+----------------------------------------------------------------------------*/

static int
call_notifiers ( PyListObject      * tnotifiers,
                 PyListObject      * onotifiers,
                 has_traits_object * obj,
                 PyObject          * name,
                 PyObject          * old_value,
                 PyObject          * new_value ) {

    int i, n, new_value_has_traits;
    PyObject * result, * item, * temp;

    int rc = 0;

    PyObject * arg_temp  = Py_None;
    PyObject * user_args = NULL;
    PyObject * args      = PyTuple_New( 4 );
    if ( args == NULL )
        return -1;

    new_value_has_traits = PyHasTraits_Check( new_value );
    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, old_value );
    PyTuple_SET_ITEM( args, 3, new_value );
    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( old_value );
    Py_INCREF( new_value );

    // Do nothing if the user has explicitly requested no traits notifications
    // to be sent.
    if ( (obj->flags & HASTRAITS_NO_NOTIFY) != 0 )
       goto exit2;

    if ( _trait_notification_handler != NULL ) {
        user_args = PyTuple_New( 2 );
        if ( user_args == NULL ) {
            Py_DECREF( args );
            return -1;
        }
        PyTuple_SET_ITEM( user_args, 0, arg_temp );
        PyTuple_SET_ITEM( user_args, 1, args );
        Py_INCREF( arg_temp );
        Py_INCREF( args );
    }

    if ( tnotifiers != NULL ) {
        n    = PyList_GET_SIZE( tnotifiers );
        temp = NULL;
        if ( n > 1 ) {
            temp = PyList_New( n );
            if ( temp == NULL ) {
                rc = -1;
                goto exit2;
            }
            for ( i = 0; i < n; i++ ) {
                item = PyList_GET_ITEM( tnotifiers, i );
                PyList_SET_ITEM( temp, i, item );
                Py_INCREF( item );
            }
            tnotifiers = (PyListObject *) temp;
        }
        for ( i = 0; i < n; i++ ) {
            if ( new_value_has_traits &&
                 (((has_traits_object *) new_value)->flags &
                    HASTRAITS_VETO_NOTIFY) ) {
                goto exit;
            }
            if ( (_trait_notification_handler != NULL) && (user_args != NULL) ){
                Py_DECREF( arg_temp );
                arg_temp = PyList_GET_ITEM( tnotifiers, i );
                Py_INCREF( arg_temp );
                PyTuple_SET_ITEM( user_args, 0, arg_temp );
                result = PyObject_Call( _trait_notification_handler,
                                        user_args, NULL );
            } else {
                result = PyObject_Call( PyList_GET_ITEM( tnotifiers, i ),
                                        args, NULL );
            }
            if ( result == NULL ) {
                rc = -1;
                goto exit;
            }
            Py_DECREF( result );
        }
        Py_XDECREF( temp );
    }

    temp = NULL;
    if ( onotifiers != NULL ) {
        n = PyList_GET_SIZE( onotifiers );
        if ( n > 1 ) {
            temp = PyList_New( n );
            if ( temp == NULL ) {
                rc = -1;
                goto exit2;
            }
            for ( i = 0; i < n; i++ ) {
                item = PyList_GET_ITEM( onotifiers, i );
                PyList_SET_ITEM( temp, i, item );
                Py_INCREF( item );
            }
            onotifiers = (PyListObject *) temp;
        }
        for ( i = 0; i < n; i++ ) {
            if ( new_value_has_traits &&
                 (((has_traits_object *) new_value)->flags &
                    HASTRAITS_VETO_NOTIFY) ) {
                break;
            }
            if ( (_trait_notification_handler != NULL) && (user_args != NULL) ){
                Py_DECREF( arg_temp );
                arg_temp = PyList_GET_ITEM( onotifiers, i );
                Py_INCREF( arg_temp );
                PyTuple_SET_ITEM( user_args, 0, arg_temp );
                result = PyObject_Call( _trait_notification_handler,
                                        user_args, NULL );
            } else {
                result = PyObject_Call( PyList_GET_ITEM( onotifiers, i ),
                                        args, NULL );
            }
            if ( result == NULL ) {
                rc = -1;
                goto exit;
            }
            Py_DECREF( result );
        }
    }
exit:
    Py_XDECREF( temp );
exit2:
    Py_XDECREF( user_args );
    Py_DECREF( args );

    return rc;
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified event trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_event ( trait_object      * traito,
                trait_object      * traitd,
                has_traits_object * obj,
                PyObject          * name,
                PyObject          * value ) {

    int rc = 0;
    PyListObject * tnotifiers;
    PyListObject * onotifiers;

    if ( value != NULL ) {
        if ( traitd->validate != NULL ) {
            value = traitd->validate( traitd, obj, name, value );
            if ( value == NULL )
                return -1;
        } else {
            Py_INCREF( value );
        }

        tnotifiers = traito->notifiers;
        onotifiers = obj->notifiers;

        if ( has_notifiers( tnotifiers, onotifiers ) )
            rc = call_notifiers( tnotifiers, onotifiers, obj, name,
                                 Undefined, value );

        Py_DECREF( value );
    }

    return rc;
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified normal trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_trait ( trait_object      * traito,
                trait_object      * traitd,
                has_traits_object * obj,
                PyObject          * name,
                PyObject          * value ) {

    int rc;
    int changed;
    int do_notifiers;
    trait_post_setattr post_setattr;
    PyListObject * tnotifiers = NULL;
    PyListObject * onotifiers = NULL;
    PyObject     * old_value  = NULL;
    PyObject     * original_value;
    PyObject     * new_value;

    PyObject *nname;

    PyObject * dict = obj->obj_dict;


    changed = (traitd->flags & TRAIT_NO_VALUE_TEST);

    if ( value == NULL ) {
        if ( dict == NULL )
            return 0;

        nname = Py2to3_NormaliseAttrName(name);
        if( nname == NULL )
            return invalid_attribute_error( name );

        old_value = PyDict_GetItem( dict, nname );
        if ( old_value == NULL ) {
            Py2to3_FinishNormaliseAttrName( name, nname );
            return 0;
        }

        Py_INCREF( old_value );
        if ( PyDict_DelItem( dict, nname ) < 0 ) {
            Py_DECREF( old_value );
            Py2to3_FinishNormaliseAttrName( name, nname );
            return -1;
        }

        rc = 0;
        if ( (obj->flags & HASTRAITS_NO_NOTIFY) == 0 ) {
            tnotifiers = traito->notifiers;
            onotifiers = obj->notifiers;
            if ( (tnotifiers != NULL) || (onotifiers != NULL) ) {
                value = traito->getattr( traito, obj, nname );
                if ( value == NULL ) {
                    Py_DECREF( old_value );
                    Py2to3_FinishNormaliseAttrName( name, nname );
                    return -1;
                }

                if ( !changed ) {
                    changed = (old_value != value );
                    if ( changed &&
                         ((traitd->flags & TRAIT_OBJECT_IDENTITY) == 0) ) {
                        changed = PyObject_RichCompareBool( old_value,
                                                            value, Py_NE );
                        if ( changed == -1 ) {
                            PyErr_Clear();
                        }
                    }
                }

                if ( changed ) {
                    if ( traitd->post_setattr != NULL )
                        rc = traitd->post_setattr( traitd, obj, nname,
                                                   value );
                    if ( (rc == 0) &&
                         has_notifiers( tnotifiers, onotifiers ) )
                        rc = call_notifiers( tnotifiers, onotifiers,
                                             obj, nname, old_value, value );
                }

                Py_DECREF( value );
            }
        }
        Py_DECREF( old_value );
        Py2to3_FinishNormaliseAttrName( name, nname );
        return rc;
    }

    original_value = value;
    // If the object's value is Undefined, then do not call the validate
    // method (as the object's value has not yet been set).
    if ( ( traitd->validate != NULL ) &&
         ( value != Undefined ) ) {
        value = traitd->validate( traitd, obj, name, value );
        if ( value == NULL ) {
            return -1;
        }
    } else {
        Py_INCREF( value );
    }

    if ( dict == NULL ) {
        obj->obj_dict = dict = PyDict_New();
        if ( dict == NULL ) {
            Py_DECREF( value );
            return -1;
        }
    }



    nname = Py2to3_NormaliseAttrName(name);
    if( nname == NULL ){
        Py_DECREF( value );
        return invalid_attribute_error( name );
    }

    new_value    = (traitd->flags & TRAIT_SETATTR_ORIGINAL_VALUE)?
                   original_value: value;
    old_value    = NULL;

    tnotifiers    = traito->notifiers;
    onotifiers    = obj->notifiers;
    do_notifiers  = has_notifiers( tnotifiers, onotifiers );

    post_setattr = traitd->post_setattr;
    if ( (post_setattr != NULL) || do_notifiers ) {
        old_value = PyDict_GetItem( dict, nname );
        if ( old_value == NULL ) {
            if ( traitd != traito ) {
                old_value = traito->getattr( traito, obj, nname );
            } else {
                old_value = default_value_for( traitd, obj, nname );
            }
            if ( old_value == NULL ) {
                Py2to3_FinishNormaliseAttrName( name, nname );
                Py_DECREF( value );

                return -1;
            }
        } else {
            Py_INCREF( old_value );
        }

        if ( !changed ) {
            changed = (old_value != value);
            if ( changed &&
                 ((traitd->flags & TRAIT_OBJECT_IDENTITY) == 0) ) {
                changed = PyObject_RichCompareBool( old_value, value, Py_NE );
                if ( changed == -1 ) {
                    PyErr_Clear();
                }
            }
        }
    }

    if ( PyDict_SetItem( dict, nname, new_value ) < 0 ) {
        if ( PyErr_ExceptionMatches( PyExc_KeyError ) )
            PyErr_SetObject( PyExc_AttributeError, nname );
        Py_XDECREF( old_value );
        Py_DECREF( name );
        Py2to3_FinishNormaliseAttrName( name, nname );
        Py_DECREF( value );

        return -1;
    }

    rc = 0;

    if ( changed ) {
        if ( post_setattr != NULL )
            rc = post_setattr( traitd, obj, nname,
                    (traitd->flags & TRAIT_POST_SETATTR_ORIGINAL_VALUE)?
                    original_value: value );

        if ( (rc == 0) && do_notifiers )
            rc = call_notifiers( tnotifiers, onotifiers, obj, nname,
                                 old_value, new_value );
    }

    Py_XDECREF( old_value );
    Py2to3_FinishNormaliseAttrName( name, nname );
    Py_DECREF( value );

    return rc;
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified delegate trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_delegate ( trait_object      * traito,
                   trait_object      * traitd,
                   has_traits_object * obj,
                   PyObject          * name,
                   PyObject          * value ) {

        PyObject          * dict;
    PyObject          * daname;
    PyObject          * daname2;
    PyObject          * temp;
    has_traits_object * delegate;
    has_traits_object * temp_delegate;
        int i, result;

    /* Follow the delegation chain until we find a non-delegated trait: */
    daname = name;
    Py_INCREF( daname );
    delegate = obj;
    for ( i = 0; ; ) {
        dict = delegate->obj_dict;
        if ( (dict != NULL) &&
             ((temp_delegate = (has_traits_object *) PyDict_GetItem( dict,
                                          traitd->delegate_name )) != NULL) ) {
            delegate = temp_delegate;
        } else {
            // Handle the case when the delegate is not in the instance
            // dictionary (could be a method that returns the real delegate):
            delegate = (has_traits_object *) has_traits_getattro( delegate,
                                                       traitd->delegate_name );
            if ( delegate == NULL ) {
                Py_DECREF( daname );
                return -1;
            }
            Py_DECREF( delegate );
        }

        // Verify that 'delegate' is of type 'CHasTraits':
        if ( !PyHasTraits_Check( delegate ) ) {
            Py_DECREF( daname );
            return bad_delegate_error2( obj, name );
        }

        daname2 = traitd->delegate_attr_name( traitd, obj, daname );
        Py_DECREF( daname );
        daname = daname2;
        if ( ((delegate->itrait_dict == NULL) ||
              ((traitd = (trait_object *) dict_getitem( delegate->itrait_dict,
                      daname )) == NULL)) &&
             ((traitd = (trait_object *) dict_getitem( delegate->ctrait_dict,
                      daname )) == NULL) &&
             ((traitd = get_prefix_trait( delegate, daname, 1 )) == NULL) ) {
            Py_DECREF( daname );
            return bad_delegate_error( obj, name );
        }

        if ( Py_TYPE(traitd) != ctrait_type ) {
            Py_DECREF( daname );
            return fatal_trait_error();
        }

        if ( traitd->delegate_attr_name == NULL ) {
            if ( traito->flags & TRAIT_MODIFY_DELEGATE ) {
                result = traitd->setattr( traitd, traitd, delegate, daname,
                                          value );
            } else {
                result = traitd->setattr( traito, traitd, obj, name, value );
                if ( result >= 0 ) {
                    temp = PyObject_CallMethod( (PyObject *) obj,
                               "_remove_trait_delegate_listener", "(Oi)",
                               name, value != NULL );
                    if ( temp == NULL ) {
                        result = -1;
                    } else {
                        Py_DECREF( temp );
                    }
                }
            }
            Py_DECREF( daname );

            return result;
        }

        if ( ++i >= 100 )
            return delegation_recursion_error( obj, name );
    }
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified property trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_property0 ( trait_object      * traito,
                    trait_object      * traitd,
                    has_traits_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * result;

    if ( value == NULL )
        return set_delete_property_error( obj, name );

    result = PyObject_Call( traitd->delegate_prefix, empty_tuple, NULL );
    if ( result == NULL )
        return -1;

    Py_DECREF( result );
    return 0;
}

static int
setattr_property1 ( trait_object      * traito,
                    trait_object      * traitd,
                    has_traits_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * result;
    PyObject * args;

    if ( value == NULL )
        return set_delete_property_error( obj, name );

    args = PyTuple_New( 1 );
    if ( args == NULL )
        return -1;

    PyTuple_SET_ITEM( args, 0, value );
    Py_INCREF( value );
    result = PyObject_Call( traitd->delegate_prefix, args, NULL );
    Py_DECREF( args );
    if ( result == NULL )
        return -1;

    Py_DECREF( result );
    return 0;
}

static int
setattr_property2 ( trait_object      * traito,
                    trait_object      * traitd,
                    has_traits_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * result;
    PyObject * args;

    if ( value == NULL )
        return set_delete_property_error( obj, name );

    args = PyTuple_New( 2 );
    if ( args == NULL )
        return -1;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, value );
    Py_INCREF( obj );
    Py_INCREF( value );
    result = PyObject_Call( traitd->delegate_prefix, args, NULL );
    Py_DECREF( args );
    if ( result == NULL )
        return -1;

    Py_DECREF( result );
    return 0;
}

static int
setattr_property3 ( trait_object      * traito,
                    trait_object      * traitd,
                    has_traits_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * result;
    PyObject * args;

    if ( value == NULL )
        return set_delete_property_error( obj, name );

    args = PyTuple_New( 3 );
    if ( args == NULL )
        return -1;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, value );
    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    result = PyObject_Call( traitd->delegate_prefix, args, NULL );
    Py_DECREF( args );
    if ( result == NULL )
        return -1;

    Py_DECREF( result );
    return 0;
}

/*-----------------------------------------------------------------------------
|  Validates then assigns a value to a specified property trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_validate_property ( trait_object      * traito,
                            trait_object      * traitd,
                            has_traits_object * obj,
                            PyObject          * name,
                            PyObject          * value ) {

    int result;
    PyObject * validated;

    if ( value == NULL )
        return set_delete_property_error( obj, name );

    validated = traitd->validate( traitd, obj, name, value );
    if ( validated == NULL )
        return -1;
    result = ((trait_setattr) traitd->post_setattr)( traito, traitd, obj, name,
                                                             validated );
    Py_DECREF( validated );
    return result;
}

static PyObject *
setattr_validate0 ( trait_object      * trait,
                    has_traits_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    return PyObject_Call( trait->py_validate, empty_tuple, NULL );
}

static PyObject *
setattr_validate1 ( trait_object      * trait,
                    has_traits_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * validated;

    PyObject * args = PyTuple_New( 1 );
    if ( args == NULL )
        return NULL;
    PyTuple_SET_ITEM( args, 0, value );
    Py_INCREF( value );
    validated = PyObject_Call( trait->py_validate, args, NULL );
    Py_DECREF( args );
    return validated;
}

static PyObject *
setattr_validate2 ( trait_object      * trait,
                    has_traits_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * validated;

    PyObject * args = PyTuple_New( 2 );
    if ( args == NULL )
        return NULL;
    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, value );
    Py_INCREF( obj );
    Py_INCREF( value );
    validated = PyObject_Call( trait->py_validate, args, NULL );
    Py_DECREF( args );
    return validated;
}

static PyObject *
setattr_validate3 ( trait_object      * trait,
                    has_traits_object * obj,
                    PyObject          * name,
                    PyObject          * value ) {

    PyObject * validated;

    PyObject * args = PyTuple_New( 3 );
    if ( args == NULL )
        return NULL;
    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, value );
    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    validated = PyObject_Call( trait->py_validate, args, NULL );
    Py_DECREF( args );
    return validated;
}

trait_validate setattr_validate_handlers[] = {
    setattr_validate0, setattr_validate1, setattr_validate2, setattr_validate3
};

/*-----------------------------------------------------------------------------
|  Raises an exception when attempting to assign to a disallowed trait:
+----------------------------------------------------------------------------*/

static int
setattr_disallow ( trait_object      * traito,
                   trait_object      * traitd,
                   has_traits_object * obj,
                   PyObject          * name,
                   PyObject          * value ) {

    return set_disallow_error( obj, name );
}

/*-----------------------------------------------------------------------------
|  Assigns a value to a specified read-only trait attribute:
+----------------------------------------------------------------------------*/

static int
setattr_readonly ( trait_object      * traito,
                   trait_object      * traitd,
                   has_traits_object * obj,
                   PyObject          * name,
                   PyObject          * value ) {

    PyObject * dict;
    PyObject * result;
    PyObject * nname;
    int rc;

    if ( value == NULL )
        return delete_readonly_error( obj, name );

    if ( traitd->default_value != Undefined )
        return set_readonly_error( obj, name );

        dict = obj->obj_dict;
    if ( dict == NULL )
        return setattr_python( traito, traitd, obj, name, value );

    nname = Py2to3_NormaliseAttrName(name);
    if( nname == NULL ){
        return invalid_attribute_error( name );
    }

    result = PyDict_GetItem( dict, nname );
    if ( (result == NULL) || (result == Undefined) )
        rc = setattr_python( traito, traitd, obj, nname, value );
    else
        rc = set_readonly_error( obj, nname );

    Py2to3_FinishNormaliseAttrName(name,nname);
    return rc;
}

/*-----------------------------------------------------------------------------
|  Generates exception on attempting to assign to a constant trait:
+----------------------------------------------------------------------------*/

static int
setattr_constant ( trait_object      * traito,
                   trait_object      * traitd,
                   has_traits_object * obj,
                   PyObject          * name,
                   PyObject          * value ) {

    if ( Py2to3_SimpleString_Check( name ) ) {
        PyErr_Format( TraitError,
            "Cannot modify the constant '%.400"
                Py2to3_PYERR_SIMPLE_STRING_FMTCHR "'"
                " attribute of a '%.50s' object.",
            Py2to3_PYERR_PREPARE_SIMPLE_STRING( name ),
            Py_TYPE(obj)->tp_name
        );
        return -1;
    }
    return invalid_attribute_error( name );
}

/*-----------------------------------------------------------------------------
|  Initializes a CTrait instance:
+----------------------------------------------------------------------------*/

static trait_getattr getattr_handlers[] = {
    getattr_trait,     getattr_python,    getattr_event,  getattr_delegate,
    getattr_event,     getattr_disallow,  getattr_trait,  getattr_constant,
    getattr_generic,
/*  The following entries are used by the __getstate__ method: */
    getattr_property0, getattr_property1, getattr_property2,
    getattr_property3,
/*  End of __getstate__ method entries */
    NULL
};

static trait_setattr setattr_handlers[] = {
    setattr_trait,     setattr_python,    setattr_event,     setattr_delegate,
    setattr_event,     setattr_disallow,  setattr_readonly,  setattr_constant,
    setattr_generic,
/*  The following entries are used by the __getstate__ method: */
    setattr_property0, setattr_property1, setattr_property2, setattr_property3,
/*  End of __setstate__ method entries */
    NULL
};

static int
trait_init ( trait_object * trait, PyObject * args, PyObject * kwds ) {

    int kind;

        if ( !PyArg_ParseTuple( args, "i", &kind ) )
                return -1;

    if ( (kind >= 0) && (kind <= 8) ) {
        trait->getattr = getattr_handlers[ kind ];
        trait->setattr = setattr_handlers[ kind ];
        return 0;
    }

    return bad_trait_error();
}

/*-----------------------------------------------------------------------------
|  Object clearing method:
+----------------------------------------------------------------------------*/

static int
trait_clear ( trait_object * trait ) {

    Py_CLEAR( trait->default_value );
    Py_CLEAR( trait->py_validate );
    Py_CLEAR( trait->py_post_setattr );
    Py_CLEAR( trait->delegate_name );
    Py_CLEAR( trait->delegate_prefix );
    Py_CLEAR( trait->notifiers );
    Py_CLEAR( trait->handler );
    Py_CLEAR( trait->obj_dict );

    return 0;
}

/*-----------------------------------------------------------------------------
|  Deallocates an unused 'CTrait' instance:
+----------------------------------------------------------------------------*/

static void
trait_dealloc ( trait_object * trait ) {

    PyObject_GC_UnTrack(trait);
    Py_TRASHCAN_SAFE_BEGIN(trait);
    trait_clear( trait );
    Py_TYPE(trait)->tp_free( (PyObject *) trait );
    Py_TRASHCAN_SAFE_END(trait);
}

/*-----------------------------------------------------------------------------
|  Garbage collector traversal method:
+----------------------------------------------------------------------------*/

static int
trait_traverse ( trait_object * trait, visitproc visit, void * arg ) {

    Py_VISIT( trait->default_value );
    Py_VISIT( trait->py_validate );
    Py_VISIT( trait->py_post_setattr );
    Py_VISIT( trait->delegate_name );
    Py_VISIT( trait->delegate_prefix );
    Py_VISIT( (PyObject *) trait->notifiers );
    Py_VISIT( trait->handler );
    Py_VISIT( trait->obj_dict );

        return 0;
}

/*-----------------------------------------------------------------------------
|  Casts a 'CTrait' which attempts to validate the argument passed as being a
|  valid value for the trait:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_cast ( trait_object * trait, PyObject * args ) {

    PyObject * obj;
    PyObject * name;
    PyObject * value;
    PyObject * result;
    PyObject * info;

    switch ( PyTuple_GET_SIZE( args ) ) {
        case 1:
            obj   = name = Py_None;
            value = PyTuple_GET_ITEM( args, 0 );
            break;
        case 2:
            name  = Py_None;
            obj   = PyTuple_GET_ITEM( args, 0 );
            value = PyTuple_GET_ITEM( args, 1 );
            break;
        case 3:
            obj   = PyTuple_GET_ITEM( args, 0 );
            name  = PyTuple_GET_ITEM( args, 1 );
            value = PyTuple_GET_ITEM( args, 2 );
            break;
        default:
            PyErr_Format( PyExc_TypeError,
#if PY_VERSION_HEX >= 0x02050000
                "Trait cast takes 1, 2 or 3 arguments (%zd given).",
#else
                "Trait cast takes 1, 2 or 3 arguments (%u given).",
#endif
                PyTuple_GET_SIZE( args ) );
            return NULL;
    }
    if ( trait->validate == NULL ) {
        Py_INCREF( value );
        return value;
    }

        result = trait->validate( trait, (has_traits_object *) obj, name, value );
    if ( result == NULL ) {
        PyErr_Clear();
        info = PyObject_CallMethod( trait->handler, "info", NULL );
        if ( (info != NULL) && Py2to3_SimpleString_Check( info ) )
            PyErr_Format( PyExc_ValueError,
                "Invalid value for trait, the value should be %"
                Py2to3_PYERR_SIMPLE_STRING_FMTCHR ".",
                Py2to3_PYERR_PREPARE_SIMPLE_STRING( info ) );
        else
            PyErr_Format( PyExc_ValueError, "Invalid value for trait." );
        Py_XDECREF( info );
    }

    return result;
}

/*-----------------------------------------------------------------------------
|  Handles the 'getattr' operation on a 'CHasTraits' instance:
+----------------------------------------------------------------------------*/

static PyObject *
trait_getattro ( trait_object * obj, PyObject * name ) {

    PyObject * value = PyObject_GenericGetAttr( (PyObject *) obj, name );
    if ( value != NULL )
        return value;

    PyErr_Clear();

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'default_value' field of a CTrait instance:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_default_value ( trait_object * trait, PyObject * args ) {

    int        value_type;
    PyObject * value;

    if ( PyArg_ParseTuple( args, "" ) ) {
        if ( trait->default_value == NULL )
            return Py_BuildValue( "iO", 0, Py_None );

        return Py_BuildValue( "iO", trait->default_value_type,
                                    trait->default_value );
    }

    if ( !PyArg_ParseTuple( args, "iO", &value_type, &value ) )
        return NULL;

    PyErr_Clear();
    if ( (value_type < 0) || (value_type > 9) ) {
        PyErr_Format( PyExc_ValueError,
                "The default value type must be 0..9, but %d was specified.",
                value_type );

        return NULL;
    }

    Py_INCREF( value );
    Py_XDECREF( trait->default_value );
    trait->default_value_type = value_type;
    trait->default_value = value;

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Gets the default value of a CTrait instance for a specified object and trait
|  name:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_default_value_for ( trait_object * trait, PyObject * args ) {

    PyObject * object;
    PyObject * name;

    if ( !PyArg_ParseTuple( args, "OO", &object, &name ) )
        return NULL;

    return default_value_for( trait, (has_traits_object *) object, name );
}

/*-----------------------------------------------------------------------------
|  Calls a Python-based trait validator:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_python ( trait_object * trait, has_traits_object * obj,
                        PyObject * name, PyObject * value ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 3 );
    if ( args == NULL )
        return NULL;

    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, value );
    result = PyObject_Call( trait->py_validate, args, NULL );
    Py_DECREF( args );

    return result;
}

/*-----------------------------------------------------------------------------
|  Calls the specified validator function:
+----------------------------------------------------------------------------*/

static PyObject *
call_validator ( PyObject * validator, has_traits_object * obj,
                 PyObject * name, PyObject * value ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 3 );
    if ( args == NULL )
        return NULL;

    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, value );
    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    result = PyObject_Call( validator, args, NULL );
    Py_DECREF( args );

    return result;
}

/*-----------------------------------------------------------------------------
|  Calls the specified type convertor:
+----------------------------------------------------------------------------*/

static PyObject *
type_converter ( PyObject * type, PyObject * value ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 1 );
    if ( args == NULL )
        return NULL;

    PyTuple_SET_ITEM( args, 0, value );
    Py_INCREF( value );
    result = PyObject_Call( type, args, NULL );
    Py_DECREF( args );

    return result;
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is of a specified type (or None):
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_type ( trait_object * trait, has_traits_object * obj,
                      PyObject * name, PyObject * value ) {

    PyObject * type_info = trait->py_validate;
    int kind = PyTuple_GET_SIZE( type_info );

    if ( ((kind == 3) && (value == Py_None)) ||
         PyObject_TypeCheck( value,
                 (PyTypeObject *) PyTuple_GET_ITEM( type_info, kind - 1 ) ) ) {

        Py_INCREF( value );
        return value;
    }

    return raise_trait_error( trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is an instance of a specified type (or None):
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_instance ( trait_object * trait, has_traits_object * obj,
                          PyObject * name, PyObject * value ) {

    PyObject * type_info = trait->py_validate;
    int kind = PyTuple_GET_SIZE( type_info );

    if ( ((kind == 3) && (value == Py_None)) ||
        (PyObject_IsInstance( value,
             PyTuple_GET_ITEM( type_info, kind - 1 ) ) > 0) ) {
        Py_INCREF( value );
        return value;
    }

    return raise_trait_error( trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is of a the same type as the object being assigned
|  to (or None):
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_self_type ( trait_object * trait, has_traits_object * obj,
                           PyObject * name, PyObject * value ) {

    if ( ((PyTuple_GET_SIZE( trait->py_validate ) == 2) &&
          (value == Py_None)) ||
          PyObject_TypeCheck( value, Py_TYPE(obj) ) ) {
        Py_INCREF( value );
        return value;
    }

    return raise_trait_error( trait, obj, name, value );
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
as_integer(PyObject *value) {
    PyObject *index_of_value, *value_as_integer;

    /* Fast path for common case. */
#if PY_MAJOR_VERSION < 3
    if (PyInt_CheckExact(value)) {
        Py_INCREF(value);
        return value;
    }
#else
    if (PyLong_CheckExact(value)) {
        Py_INCREF(value);
        return value;
    }
#endif
    /* Not of exact type int: call __index__ method if available. */
    index_of_value = PyNumber_Index(value);
    if (index_of_value == NULL) {
        return NULL;
    }

    /*
       We run the __index__ result through an extra int call to ensure that
       we get something of exact type int or long, and (for Python 2) to
       ensure that we only get a long if the target value is outside the
       range of an int.

       Example problematic cases:

       - ``operator.index(True)`` gives ``True``, where we'd like ``1``.
       - On Python 2, ``operator.index(np.uint64(3))`` gives ``3L``, where
         we'd like ``3``.

       Related: https://bugs.python.org/issue17576
    */

#if PY_MAJOR_VERSION < 3
    value_as_integer = PyNumber_Int(index_of_value);
#else
    value_as_integer = PyNumber_Long(index_of_value);
#endif
    Py_DECREF(index_of_value);
    return value_as_integer;
}


/*-----------------------------------------------------------------------------
|  Verifies a Python value is an int within a specified range:
+----------------------------------------------------------------------------*/
#if PY_MAJOR_VERSION < 3
static PyObject *
validate_trait_int ( trait_object * trait, has_traits_object * obj,
                     PyObject * name, PyObject * value ) {

    register PyObject * low;
    register PyObject * high;
    long exclude_mask;
    long int_value;

    PyObject * type_info = trait->py_validate;

    if ( PyInt_Check( value ) ) {
        int_value    = PyInt_AS_LONG( value );
        low          = PyTuple_GET_ITEM( type_info, 1 );
        high         = PyTuple_GET_ITEM( type_info, 2 );
        exclude_mask = PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 3 ) );
        if ( low != Py_None ) {
            if ( (exclude_mask & 1) != 0 ) {
                if ( int_value <= PyInt_AS_LONG( low ) )
                    goto error;
            } else {
                if ( int_value < PyInt_AS_LONG( low ) )
                    goto error;
            }
        }

        if ( high != Py_None ) {
            if ( (exclude_mask & 2) != 0 ) {
                if ( int_value >= PyInt_AS_LONG( high ) )
                    goto error;
            } else {
                if ( int_value > PyInt_AS_LONG( high ) )
                    goto error;
            }
        }

        Py_INCREF( value );
        return value;
    }
error:
    return raise_trait_error( trait, obj, name, value );
}
#endif  // #if PY_MAJOR_VERSION < 3

/*-----------------------------------------------------------------------------
|  Verifies a Python value is a Python integer (an int or long)
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_integer(trait_object *trait, has_traits_object *obj,
                       PyObject *name, PyObject *value) {
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
as_float(PyObject *value) {
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
validate_trait_float(trait_object * trait, has_traits_object * obj,
                     PyObject * name, PyObject * value) {
    PyObject* result = as_float(value);
    /* A TypeError represents a type validation failure, and should be
       re-raised as a TraitError. Other exceptions should be propagated. */
    if (result == NULL && PyErr_ExceptionMatches(PyExc_TypeError)) {
        PyErr_Clear();
        return raise_trait_error(trait, obj, name, value);
    }
    return result;
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is a float within a specified range:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_float_range ( trait_object * trait, has_traits_object * obj,
                             PyObject * name, PyObject * value ) {

    register PyObject * low;
    register PyObject * high;
    long exclude_mask;
    double float_value;

    PyObject * type_info = trait->py_validate;

    if ( !PyFloat_Check( value ) ) {
        float_value = Py2to3_PyNum_AsDouble( value );
        if( float_value==-1 && PyErr_Occurred() )
            goto error;
        value       = PyFloat_FromDouble( float_value );
        if ( value == NULL )
            goto error;
        Py_INCREF( value );
    } else {
        float_value = PyFloat_AS_DOUBLE( value );
    }

    low          = PyTuple_GET_ITEM( type_info, 1 );
    high         = PyTuple_GET_ITEM( type_info, 2 );
#if PY_MAJOR_VERSION < 3
    exclude_mask = PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 3 ) );
#else
    exclude_mask = PyLong_AsLong( PyTuple_GET_ITEM( type_info, 3 ) );
    if( exclude_mask==-1 && PyErr_Occurred()){
        goto error;
    }
#endif  // #if PY_MAJOR_VERSION < 3

    if ( low != Py_None ) {
        if ( (exclude_mask & 1) != 0 ) {
            if ( float_value <= PyFloat_AS_DOUBLE( low ) )
                goto error;
        } else {
            if ( float_value < PyFloat_AS_DOUBLE( low ) )
                goto error;
        }
    }

    if ( high != Py_None ) {
        if ( (exclude_mask & 2) != 0 ) {
            if ( float_value >= PyFloat_AS_DOUBLE( high ) )
                goto error;
        } else {
            if ( float_value > PyFloat_AS_DOUBLE( high ) )
                goto error;
        }
    }

    Py_INCREF( value );
    return value;
error:
    return raise_trait_error( trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is in a specified enumeration:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_enum ( trait_object * trait, has_traits_object * obj,
                      PyObject * name, PyObject * value ) {

    PyObject * type_info = trait->py_validate;
    if ( PySequence_Contains( PyTuple_GET_ITEM( type_info, 1 ), value ) > 0 ) {
        Py_INCREF( value );
        return value;
    }

    return raise_trait_error( trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is in a specified map (i.e. dictionary):
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_map ( trait_object * trait, has_traits_object * obj,
                     PyObject * name, PyObject * value ) {

    PyObject * type_info = trait->py_validate;
    if ( PyDict_GetItem( PyTuple_GET_ITEM( type_info, 1 ), value ) != NULL ) {
        Py_INCREF( value );
        return value;
    }

    return raise_trait_error( trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is in a specified prefix map (i.e. dictionary):
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_prefix_map ( trait_object * trait, has_traits_object * obj,
                            PyObject * name, PyObject * value ) {

    PyObject * type_info    = trait->py_validate;
    PyObject * mapped_value = PyDict_GetItem( PyTuple_GET_ITEM( type_info, 1 ),
                                              value );
    if ( mapped_value != NULL ) {
        Py_INCREF( mapped_value );
        return mapped_value;
    }

    return call_validator( PyTuple_GET_ITEM( trait->py_validate, 2 ),
                           obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is a tuple of a specified type and content:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_tuple_check ( PyObject * traits, has_traits_object * obj,
                             PyObject * name, PyObject * value ) {

    trait_object * itrait;
    PyObject     * bitem, * aitem, * tuple;
    int i, j, n;

    if ( PyTuple_Check( value ) ) {
        n = PyTuple_GET_SIZE( traits );
        if ( n == PyTuple_GET_SIZE( value ) ) {
            tuple = NULL;
            for ( i = 0; i < n; i++ ) {
                bitem  = PyTuple_GET_ITEM( value, i );
                itrait = (trait_object *) PyTuple_GET_ITEM( traits, i );
                if ( itrait->validate == NULL ) {
                    aitem = bitem;
                    Py_INCREF( aitem );
                } else
                    aitem = itrait->validate( itrait, obj, name, bitem );

                if ( aitem == NULL ) {
                    PyErr_Clear();
                    Py_XDECREF( tuple );
                    return NULL;
                }

                if ( tuple != NULL )
                    PyTuple_SET_ITEM( tuple, i, aitem );
                else if ( aitem != bitem ) {
                    tuple = PyTuple_New( n );
                    if ( tuple == NULL )
                        return NULL;
                    for ( j = 0; j < i; j++ ) {
                        bitem = PyTuple_GET_ITEM( value, j );
                        Py_INCREF( bitem );
                        PyTuple_SET_ITEM( tuple, j, bitem );
                    }
                    PyTuple_SET_ITEM( tuple, i, aitem );
                } else
                    Py_DECREF( aitem );
            }
            if ( tuple != NULL )
                return tuple;

            Py_INCREF( value );
            return value;
        }
    }

    return NULL;
}

static PyObject *
validate_trait_tuple ( trait_object * trait, has_traits_object * obj,
                       PyObject * name, PyObject * value ) {

    PyObject * result = validate_trait_tuple_check(
                            PyTuple_GET_ITEM( trait->py_validate, 1 ),
                            obj, name, value );
    if ( result != NULL )
        return result;

    return raise_trait_error( trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is of a specified (possibly coercable) type:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_coerce_type ( trait_object * trait, has_traits_object * obj,
                             PyObject * name, PyObject * value ) {

    int i, n;
    PyObject * type2;

    PyObject * type_info = trait->py_validate;
    PyObject * type      = PyTuple_GET_ITEM( type_info, 1 );
    if ( PyObject_TypeCheck( value, (PyTypeObject *) type ) ) {
        Py_INCREF( value );
        return value;
    }

    n = PyTuple_GET_SIZE( type_info );
    for ( i = 2; i < n; i++ ) {
        type2 = PyTuple_GET_ITEM( type_info, i );
        if ( type2 == Py_None )
            break;

        if ( PyObject_TypeCheck( value, (PyTypeObject *) type2 ) ) {
            Py_INCREF( value );
            return value;
        }
    }

    for ( i++; i < n; i++ ) {
        type2 = PyTuple_GET_ITEM( type_info, i );
        if ( PyObject_TypeCheck( value, (PyTypeObject *) type2 ) )
            return type_converter( type, value );
    }

    return raise_trait_error( trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value is of a specified (possibly castable) type:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_cast_type ( trait_object * trait, has_traits_object * obj,
                           PyObject * name, PyObject * value ) {

    PyObject * result;

    PyObject * type_info = trait->py_validate;
    PyObject * type      = PyTuple_GET_ITEM( type_info, 1 );
    if ( PyObject_TypeCheck( value, (PyTypeObject *) type ) ) {
        Py_INCREF( value );
        return value;
    }

    if ( (result = type_converter( type, value )) != NULL )
        return result;

    return raise_trait_error( trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value satisifies a specified function validator:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_function ( trait_object * trait, has_traits_object * obj,
                          PyObject * name, PyObject * value ) {

    PyObject * result;

    result = call_validator( PyTuple_GET_ITEM( trait->py_validate, 1 ),
                             obj, name, value );
    if ( result != NULL )
        return result;

    return raise_trait_error( trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Attempts to 'adapt' an object to a specified interface:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_adapt ( trait_object * trait, has_traits_object * obj,
                       PyObject * name, PyObject * value ) {

    PyObject * result;
    PyObject * args;
    PyObject * type;
    PyObject * type_info = trait->py_validate;
    long mode, rc;

    if ( value == Py_None ) {
#if PY_MAJOR_VERSION < 3
        if ( PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 3 ) ) ) {
#else
        mode = PyLong_AsLong( PyTuple_GET_ITEM( type_info, 3 ) );
        if( mode==-1 && PyErr_Occurred())
            return NULL;
        if ( mode ) {
#endif // #if PY_MAJOR_VERSION < 3
            Py_INCREF( value );
            return value;
        }
        return raise_trait_error( trait, obj, name, value );
    }

    type = PyTuple_GET_ITEM( type_info, 1 );
#if PY_MAJOR_VERSION < 3
    mode = PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 2 ) );
#else
    mode = PyLong_AsLong( PyTuple_GET_ITEM( type_info, 2 ) );
    if( mode==-1 && PyErr_Occurred())
        return NULL;
#endif // #if PY_MAJOR_VERSION < 3

    if ( mode == 2 ) {
        args = PyTuple_New( 3 );
        if ( args == NULL )
            return NULL;

        PyTuple_SET_ITEM( args, 2, Py_None );
        Py_INCREF( Py_None );
    } else {
        args = PyTuple_New( 2 );
        if ( args == NULL )
            return NULL;
    }

    PyTuple_SET_ITEM( args, 0, value );
    PyTuple_SET_ITEM( args, 1, type );
    Py_INCREF( value );
    Py_INCREF( type );
    result = PyObject_Call( adapt, args, NULL );
    if ( result != NULL ) {
        if ( result != Py_None ) {
            if ( (mode > 0) || (result == value) ) {
                Py_DECREF( args );
                return result;
            }
            Py_DECREF( result );
            goto check_implements;
        }

        Py_DECREF( result );
        result = PyObject_Call( validate_implements, args, NULL );
#if PY_MAJOR_VERSION < 3
        rc     = PyInt_AS_LONG( result );
#else
        rc     = PyLong_AsLong( result );
#endif
        Py_DECREF( args );
        Py_DECREF( result );
#if PY_MAJOR_VERSION >= 3
        if( rc==-1 && PyErr_Occurred()){
            return NULL;
        }
#endif
        if ( rc ) {
            Py_INCREF( value );
            return value;
        }

        result = default_value_for( trait, obj, name );
        if ( result != NULL )
            return result;

        PyErr_Clear();
        return raise_trait_error( trait, obj, name, value );
    }
    PyErr_Clear();
check_implements:
    result = PyObject_Call( validate_implements, args, NULL );
#if PY_MAJOR_VERSION < 3
    rc     = PyInt_AS_LONG( result );
#else
    rc     = PyLong_AsLong( result );
#endif
    Py_DECREF( args );
    Py_DECREF( result );
#if PY_MAJOR_VERSION >= 3
    if( rc==-1 && PyErr_Occurred()){
        return NULL;
    }
#endif
    if ( rc ) {
        Py_INCREF( value );
        return value;
    }

    return raise_trait_error( trait, obj, name, value );
}

/*-----------------------------------------------------------------------------
|  Verifies a Python value satisifies a complex trait definition:
+----------------------------------------------------------------------------*/

static PyObject *
validate_trait_complex ( trait_object * trait, has_traits_object * obj,
                         PyObject * name, PyObject * value ) {

    int    i, j, k, kind;
    long   exclude_mask, mode, rc;
    double float_value;
    PyObject * low, * high, * result, * type_info, * type, * type2, * args;

    PyObject * list_type_info = PyTuple_GET_ITEM( trait->py_validate, 1 );
    int n = PyTuple_GET_SIZE( list_type_info );
    for ( i = 0; i < n; i++ ) {

        type_info = PyTuple_GET_ITEM( list_type_info, i );

        switch ( Py2to3_PyNum_AsLong( PyTuple_GET_ITEM( type_info, 0 ) ) ) {

            case 0:  /* Type check: */
                kind = PyTuple_GET_SIZE( type_info );
                if ( ((kind == 3) && (value == Py_None)) ||
                     PyObject_TypeCheck( value, (PyTypeObject *)
                                    PyTuple_GET_ITEM( type_info, kind - 1 ) ) )
                    goto done;
                break;

            case 1:  /* Instance check: */
                kind = PyTuple_GET_SIZE( type_info );
                if ( ((kind == 3) && (value == Py_None)) ||
                    (PyObject_IsInstance( value,
                         PyTuple_GET_ITEM( type_info, kind - 1 ) ) > 0) )
                    goto done;
                break;

            case 2:  /* Self type check: */
                if ( ((PyTuple_GET_SIZE( type_info ) == 2) &&
                      (value == Py_None)) ||
                      PyObject_TypeCheck( value, Py_TYPE(obj) ) )
                    goto done;
                break;

#if PY_MAJOR_VERSION < 3
            case 3:  /* Integer range check: */
                if ( PyInt_Check( value ) ) {
                    long int_value;
                    int_value    = PyInt_AS_LONG( value );
                    low          = PyTuple_GET_ITEM( type_info, 1 );
                    high         = PyTuple_GET_ITEM( type_info, 2 );
                    exclude_mask = PyInt_AS_LONG(
                                       PyTuple_GET_ITEM( type_info, 3 ) );
                    if ( low != Py_None ) {
                        if ( (exclude_mask & 1) != 0 ) {
                            if ( int_value <= PyInt_AS_LONG( low  ) )
                                break;
                        } else {
                            if ( int_value < PyInt_AS_LONG( low  ) )
                                break;
                        }
                    }
                    if ( high != Py_None ) {
                        if ( (exclude_mask & 2) != 0 ) {
                            if ( int_value >= PyInt_AS_LONG( high ) )
                                break;
                        } else {
                            if ( int_value > PyInt_AS_LONG( high ) )
                                break;
                        }
                    }
                    goto done;
                }
                break;
#endif

            case 4:  /* Floating point range check: */
                if ( !PyFloat_Check( value ) ) {
                    float_value = Py2to3_PyNum_AsDouble( value );
                    if( float_value==-1 && PyErr_Occurred() ){
                        PyErr_Clear();
                        break;
                    }

                    value       = PyFloat_FromDouble( float_value );
                    if ( value == NULL ) {
                        PyErr_Clear();
                        break;
                    }
                } else {
                    float_value = PyFloat_AS_DOUBLE( value );
                    Py_INCREF( value );
                }
                low          = PyTuple_GET_ITEM( type_info, 1 );
                high         = PyTuple_GET_ITEM( type_info, 2 );
#if PY_MAJOR_VERSION < 3
                exclude_mask = PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 3 ) );
#else
                exclude_mask = PyLong_AsLong( PyTuple_GET_ITEM( type_info, 3 ) );
                if( exclude_mask==-1 && PyErr_Occurred()){
                    PyErr_Clear();
                    break;
                }
#endif  // #if PY_MAJOR_VERSION < 3


                if ( low != Py_None ) {
                    if ( (exclude_mask & 1) != 0 ) {
                        if ( float_value <= PyFloat_AS_DOUBLE( low ) )
                            break;
                    } else {
                        if ( float_value < PyFloat_AS_DOUBLE( low ) )
                            break;
                    }
                }
                if ( high != Py_None ) {
                    if ( (exclude_mask & 2) != 0 ) {
                        if ( float_value >= PyFloat_AS_DOUBLE( high ) )
                            break;
                    } else {
                        if ( float_value > PyFloat_AS_DOUBLE( high ) )
                            break;
                    }
                }
                goto done2;

            case 5:  /* Enumerated item check: */
                if ( PySequence_Contains( PyTuple_GET_ITEM( type_info, 1 ),
                                          value ) > 0 )
                    goto done;
                /* If the containment check failed (for example as a result of
                   checking whether an array is in a sequence), clear the
                   exception. See enthought/traits#376. */
                PyErr_Clear();
                break;
            case 6:  /* Mapped item check: */
                if ( PyDict_GetItem( PyTuple_GET_ITEM( type_info, 1 ),
                                     value ) != NULL )
                    goto done;
                PyErr_Clear();
                break;

            case 8:  /* Perform 'slow' validate check: */
                result = PyObject_CallMethod( PyTuple_GET_ITEM( type_info, 1 ),
                                  "slow_validate", "(OOO)", obj, name, value );
                if ( result != NULL )
                    return result;

                PyErr_Clear();
                break;

            case 9:  /* Tuple item check: */
                result = validate_trait_tuple_check(
                             PyTuple_GET_ITEM( type_info, 1 ),
                             obj, name, value );
                if ( result != NULL )
                    return result;

                PyErr_Clear();
                break;

            case 10:  /* Prefix map item check: */
                result = PyDict_GetItem( PyTuple_GET_ITEM( type_info, 1 ),
                                         value );
                if ( result != NULL ) {
                    Py_INCREF( result );
                    return result;
                }
                result = call_validator( PyTuple_GET_ITEM( type_info, 2 ),
                                         obj, name, value );
                if ( result != NULL )
                    return result;
                PyErr_Clear();
                break;

            case 11:  /* Coercable type check: */
                type = PyTuple_GET_ITEM( type_info, 1 );
                if ( PyObject_TypeCheck( value, (PyTypeObject *) type ) )
                    goto done;

                k = PyTuple_GET_SIZE( type_info );
                for ( j = 2; j < k; j++ ) {
                    type2 = PyTuple_GET_ITEM( type_info, j );
                    if ( type2 == Py_None )
                        break;
                    if ( PyObject_TypeCheck( value, (PyTypeObject *) type2 ) )
                        goto done;
                }

                for ( j++; j < k; j++ ) {
                    type2 = PyTuple_GET_ITEM( type_info, j );
                    if ( PyObject_TypeCheck( value, (PyTypeObject *) type2 ) )
                        return type_converter( type, value );
                }
                break;

            case 12:  /* Castable type check */
                type = PyTuple_GET_ITEM( type_info, 1 );
                if ( PyObject_TypeCheck( value, (PyTypeObject *) type ) )
                    goto done;

                if ( (result = type_converter( type, value )) != NULL )
                    return result;

                PyErr_Clear();
                break;

            case 13:  /* Function validator check: */
                result = call_validator( PyTuple_GET_ITEM( type_info, 1 ),
                                         obj, name, value );
                if ( result != NULL )
                    return result;

                PyErr_Clear();
                break;

            /* case 14: Python-based validator check: */

            /* case 15..18: Property 'setattr' validate checks: */

            case 19:  /* PyProtocols 'adapt' check: */
                if ( value == Py_None ) {
#if PY_MAJOR_VERSION < 3
                    if ( PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 3 ) ) )
#else
                    mode = PyLong_AsLong( PyTuple_GET_ITEM( type_info, 2 ) );
                    if( mode==-1 && PyErr_Occurred())
                        return NULL;
                    if( mode )
#endif // #if PY_MAJOR_VERSION < 3
                        goto done;
                    break;
                }
                type = PyTuple_GET_ITEM( type_info, 1 );
#if PY_MAJOR_VERSION < 3
                mode = PyInt_AS_LONG( PyTuple_GET_ITEM( type_info, 2 ) );
#else
                mode = PyLong_AsLong( PyTuple_GET_ITEM( type_info, 2 ) );
                if( mode==-1 && PyErr_Occurred())
                    return NULL;
#endif // #if PY_MAJOR_VERSION < 3
                if ( mode == 2 ) {
                    args = PyTuple_New( 3 );
                    if ( args == NULL )
                        return NULL;

                    PyTuple_SET_ITEM( args, 2, Py_None );
                    Py_INCREF( Py_None );
                } else {
                    args = PyTuple_New( 2 );
                    if ( args == NULL )
                        return NULL;
                }

                PyTuple_SET_ITEM( args, 0, value );
                PyTuple_SET_ITEM( args, 1, type );
                Py_INCREF( value );
                Py_INCREF( type );
                result = PyObject_Call( adapt, args, NULL );
                if ( result != NULL ) {
                    if ( result != Py_None ) {
                        if ( (mode == 0) && (result != value) ) {
                            Py_DECREF( result );
                            goto check_implements;
                        }
                        Py_DECREF( args );
                        return result;
                    }

                    Py_DECREF( result );
                    result = PyObject_Call( validate_implements, args, NULL );
#if PY_MAJOR_VERSION < 3
                    rc = PyInt_AS_LONG( result );
#else
                    rc = PyLong_AsLong( result );
                    if( rc==-1 && PyErr_Occurred()){
                        PyErr_Clear();
                        Py_DECREF( args );
                        Py_DECREF( result );
                        break;
                    }
#endif // #if PY_MAJOR_VERSION < 3
                    Py_DECREF( args );
                    Py_DECREF( result );
                    if ( rc )
                        goto done;
                    result = default_value_for( trait, obj, name );
                    if ( result != NULL )
                        return result;

                    PyErr_Clear();
                    break;
                }
                PyErr_Clear();
check_implements:
                result = PyObject_Call( validate_implements, args, NULL );
#if PY_MAJOR_VERSION < 3
                rc = PyInt_AS_LONG( result );
#else
                rc = PyLong_AsLong( result );
                if( rc==-1 && PyErr_Occurred()){
                    PyErr_Clear();
                    Py_DECREF( args );
                    Py_DECREF( result );
                    break;
                }
#endif // #if PY_MAJOR_VERSION < 3
                Py_DECREF( args );
                Py_DECREF( result );
                if ( rc )
                    goto done;
                break;

            case 20:  /* Integer check: */
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

            case 21:  /* Float check */
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

            default:  /* Should never happen...indicates an internal error: */
                goto error;
        }
    }
error:
    return raise_trait_error( trait, obj, name, value );
done:
    Py_INCREF( value );
done2:
    return value;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'validate' field of a CTrait instance:
+----------------------------------------------------------------------------*/

static trait_validate validate_handlers[] = {
    validate_trait_type,        validate_trait_instance,
#if PY_MAJOR_VERSION < 3
    validate_trait_self_type,   validate_trait_int,
#else
    validate_trait_self_type,   NULL,
#endif // #if PY_MAJOR_VERSION < 3
    validate_trait_float_range, validate_trait_enum,
    validate_trait_map,         validate_trait_complex,
    NULL,                       validate_trait_tuple,
    validate_trait_prefix_map,  validate_trait_coerce_type,
    validate_trait_cast_type,   validate_trait_function,
    validate_trait_python,
/*  The following entries are used by the __getstate__ method... */
    setattr_validate0,           setattr_validate1,
    setattr_validate2,           setattr_validate3,
/*  ...End of __getstate__ method entries */
    validate_trait_adapt,        validate_trait_integer,
    validate_trait_float,
};

static PyObject *
_trait_set_validate ( trait_object * trait, PyObject * args ) {

    PyObject * validate;
    PyObject * v1, * v2, * v3;
    int        n, kind;

    if ( !PyArg_ParseTuple( args, "O", &validate ) )
        return NULL;

    if ( PyCallable_Check( validate ) ) {
        kind = 14;
        goto done;
    }

    if ( PyTuple_CheckExact( validate ) ) {
        n = PyTuple_GET_SIZE( validate );
        if ( n > 0 ) {

            kind = Py2to3_PyNum_AsLong( PyTuple_GET_ITEM( validate, 0 ) );

            switch ( kind ) {
                case 0:  /* Type check: */
                    if ( (n <= 3) &&
                         PyType_Check( PyTuple_GET_ITEM( validate, n - 1 ) ) &&
                         ((n == 2) ||
                          (PyTuple_GET_ITEM( validate, 1 ) == Py_None)) )
                        goto done;
                    break;

                case 1:  /* Instance check: */
                    if ( (n <= 3) &&
                         ((n == 2) ||
                          (PyTuple_GET_ITEM( validate, 1 ) == Py_None)) )
                        goto done;
                    break;

                case 2:  /* Self type check: */
                    if ( (n == 1) ||
                         ((n == 2) &&
                          (PyTuple_GET_ITEM( validate, 1 ) == Py_None)) )
                        goto done;
                    break;

#if PY_MAJOR_VERSION < 3
                case 3:  /* Integer range check: */
                    if ( n == 4 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        v2 = PyTuple_GET_ITEM( validate, 2 );
                        v3 = PyTuple_GET_ITEM( validate, 3 );
                        if ( ((v1 == Py_None) || PyInt_Check( v1 )) &&
                             ((v2 == Py_None) || PyInt_Check( v2 )) &&
                             PyInt_Check( v3 ) )
                            goto done;
                    }
                    break;
#endif // #if PY_MAJOR_VERSION < 3

                case 4:  /* Floating point range check: */
                    if ( n == 4 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        v2 = PyTuple_GET_ITEM( validate, 2 );
                        v3 = PyTuple_GET_ITEM( validate, 3 );
                        if ( ((v1 == Py_None) || PyFloat_Check( v1 )) &&
                             ((v2 == Py_None) || PyFloat_Check( v2 )) &&
                             Py2to3_PyNum_Check( v3 ) )
                            goto done;
                    }
                    break;

                case 5:  /* Enumerated item check: */
                    if ( n == 2 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyTuple_CheckExact( v1 ) )
                            goto done;
                    }
                    break;

                case 6:  /* Mapped item check: */
                    if ( n == 2 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyDict_Check( v1 ) )
                            goto done;
                    }
                    break;

                case 7:  /* TraitComplex item check: */
                    if ( n == 2 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyTuple_CheckExact( v1 ) )
                            goto done;
                    }
                    break;

                /* case 8: 'Slow' validate check: */
                case 9:  /* TupleOf item check: */
                    if ( n == 2 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyTuple_CheckExact( v1 ) )
                            goto done;
                    }
                    break;

                case 10:  /* Prefix map item check: */
                    if ( n == 3 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyDict_Check( v1 ) )
                            goto done;
                    }
                    break;

                case 11:  /* Coercable type check: */
                    if ( n >= 2 )
                       goto done;
                    break;

                case 12:  /* Castable type check: */
                    if ( n == 2 )
                       goto done;
                    break;

                case 13:  /* Function validator check: */
                    if ( n == 2 ) {
                        v1 = PyTuple_GET_ITEM( validate, 1 );
                        if ( PyCallable_Check( v1 ) )
                            goto done;
                    }
                    break;

                /* case 14: Python-based validator check: */
                /* case 15..18: Property 'setattr' validate checks: */
                case 19:  /* PyProtocols 'adapt' check: */
                    /* Note: We don't check the 'class' argument (item[1])
                       because some old-style code creates classes that are not
                       strictly classes or types (e.g. VTK), and yet they work
                       correctly with the rest of the Instance code */
                    if ( (n == 4) &&
                         Py2to3_PyNum_Check(  PyTuple_GET_ITEM( validate, 2 ) )  &&
                         PyBool_Check( PyTuple_GET_ITEM( validate, 3 ) ) ) {
                        goto done;
                    }
                    break;

                case 20:  /* Integer check: */
                    if ( n == 1 )
                        goto done;
                    break;

                case 21:  /* Float check: */
                    if ( n == 1 )
                        goto done;
                    break;

            }
        }
    }

    PyErr_SetString( PyExc_ValueError,
                     "The argument must be a tuple or callable." );

    return NULL;

done:
    trait->validate = validate_handlers[ kind ];
    Py_INCREF( validate );
    Py_XDECREF( trait->py_validate );
    trait->py_validate = validate;

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Gets the value of the 'validate' field of a CTrait instance:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_get_validate ( trait_object * trait ) {

    if ( trait->validate != NULL ) {
        Py_INCREF( trait->py_validate );
        return trait->py_validate;
    }

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Validates that a particular value can be assigned to an object trait:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_validate ( trait_object * trait, PyObject * args ) {

    PyObject * object, * name, * value;

    if ( !PyArg_ParseTuple( args, "OOO", &object, &name, &value ) )
        return NULL;

    if ( trait->validate == NULL ) {
        Py_INCREF( value );
        return value;
    }

    return trait->validate( trait, (has_traits_object *)object, name, value );
}

/*-----------------------------------------------------------------------------
|  Calls a Python-based trait post_setattr handler:
+----------------------------------------------------------------------------*/

static int
post_setattr_trait_python ( trait_object * trait, has_traits_object * obj,
                            PyObject * name, PyObject * value ) {

    PyObject * result;

    PyObject * args = PyTuple_New( 3 );
    if ( args == NULL )
        return -1;

    Py_INCREF( obj );
    Py_INCREF( name );
    Py_INCREF( value );
    PyTuple_SET_ITEM( args, 0, (PyObject *) obj );
    PyTuple_SET_ITEM( args, 1, name );
    PyTuple_SET_ITEM( args, 2, value );
    result = PyObject_Call( trait->py_post_setattr, args, NULL );
    Py_DECREF( args );

    if ( result == NULL )
        return -1;

    Py_DECREF( result );
    return 0;
}

/*-----------------------------------------------------------------------------
|  Returns the various forms of delegate names:
+----------------------------------------------------------------------------*/

static PyObject *
delegate_attr_name_name ( trait_object      * trait,
                          has_traits_object * obj,
                          PyObject          * name ) {

    Py_INCREF( name );
    return name;
}

static PyObject *
delegate_attr_name_prefix ( trait_object      * trait,
                            has_traits_object * obj,
                            PyObject          * name ) {

    Py_INCREF( trait->delegate_prefix );
    return trait->delegate_prefix;
}

static PyObject *
delegate_attr_name_prefix_name ( trait_object      * trait,
                                 has_traits_object * obj,
                                 PyObject          * name ) {


#if PY_MAJOR_VERSION < 3
    char * p;
    int prefix_len    = PyString_GET_SIZE( trait->delegate_prefix );
    int name_len      = PyString_GET_SIZE( name );
    int total_len     = prefix_len + name_len;
    PyObject * result = PyString_FromStringAndSize( NULL, total_len );

    if ( result == NULL ) {
        Py_INCREF( Py_None );
        return Py_None;
    }

    p = PyString_AS_STRING( result );
    memcpy( p, PyString_AS_STRING( trait->delegate_prefix ), prefix_len );
    memcpy( p + prefix_len, PyString_AS_STRING( name ), name_len );
#else
    PyObject *result = PyUnicode_Concat( trait->delegate_prefix, name );
#endif

    return result;
}

static PyObject *
delegate_attr_name_class_name ( trait_object      * trait,
                                has_traits_object * obj,
                                PyObject          * name ) {

    PyObject * prefix, * result;
#if PY_MAJOR_VERSION < 3
    char * p;
    int prefix_len, name_len, total_len;
#endif

    prefix = PyObject_GetAttr( (PyObject *) Py_TYPE(obj), class_prefix );
// fixme: Should verify that prefix is a string...
    if ( prefix == NULL ) {
            PyErr_Clear();

    Py_INCREF( name );
            return name;
    }

#if PY_MAJOR_VERSION < 3
    prefix_len = PyString_GET_SIZE( prefix );
    name_len   = PyString_GET_SIZE( name );
    total_len  = prefix_len + name_len;
    result     = PyString_FromStringAndSize( NULL, total_len );
    if ( result == NULL ) {
        Py_INCREF( Py_None );
        return Py_None;
    }

    p = PyString_AS_STRING( result );
    memcpy( p, PyString_AS_STRING( prefix ), prefix_len );
    memcpy( p + prefix_len, PyString_AS_STRING( name ), name_len );
#else
    result = PyUnicode_Concat( prefix, name );
#endif
    Py_DECREF( prefix );
    return result;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'post_setattr' field of a CTrait instance:
+----------------------------------------------------------------------------*/

static delegate_attr_name_func delegate_attr_name_handlers[] = {
    delegate_attr_name_name,         delegate_attr_name_prefix,
    delegate_attr_name_prefix_name,  delegate_attr_name_class_name,
    NULL
};

static PyObject *
_trait_delegate ( trait_object * trait, PyObject * args ) {

    PyObject * delegate_name;
    PyObject * delegate_prefix;
    int prefix_type;
    int modify_delegate;

#if PY_MAJOR_VERSION < 3
    {
        const char *delegate_name_str;
        const char *delegate_prefix_str;
        if ( !PyArg_ParseTuple( args, "ssii",
                                &delegate_name_str, &delegate_prefix_str,
                                &prefix_type,   &modify_delegate ) )
            return NULL;
        delegate_name = PyString_FromString(delegate_name_str);
        delegate_prefix = PyString_FromString(delegate_prefix_str);
        if(!delegate_name || !delegate_prefix){
            Py_XDECREF(delegate_name);
            Py_XDECREF(delegate_prefix);
            return NULL;
        }
    }
#else
    if ( !PyArg_ParseTuple( args, "UUii",
                            &delegate_name, &delegate_prefix,
                            &prefix_type,   &modify_delegate ) )
        return NULL;
    Py_INCREF( delegate_name );
    Py_INCREF( delegate_prefix );
#endif

    if ( modify_delegate ) {
        trait->flags |= TRAIT_MODIFY_DELEGATE;
    } else {
        trait->flags &= (~TRAIT_MODIFY_DELEGATE);
    }

    trait->delegate_name   = delegate_name;
    trait->delegate_prefix = delegate_prefix;
    if ( (prefix_type < 0) || (prefix_type > 3) )
        prefix_type = 0;

    trait->delegate_attr_name = delegate_attr_name_handlers[ prefix_type ];

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'comparison' mode of a CTrait instance:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_rich_comparison ( trait_object * trait, PyObject * args ) {

    int compare_type;

    if ( !PyArg_ParseTuple( args, "i", &compare_type ) )
        return NULL;

    trait->flags &= (~(TRAIT_NO_VALUE_TEST | TRAIT_OBJECT_IDENTITY));
    if ( compare_type == 0 )
        trait->flags |= TRAIT_OBJECT_IDENTITY;

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the appropriate value comparison mode flags of a CTrait instance:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_comparison_mode ( trait_object * trait, PyObject * args ) {

    int comparison_mode;

    if ( !PyArg_ParseTuple( args, "i", &comparison_mode ) )
        return NULL;

    trait->flags &= (~(TRAIT_NO_VALUE_TEST | TRAIT_OBJECT_IDENTITY));
    switch ( comparison_mode ) {
        case 0:  trait->flags |= TRAIT_NO_VALUE_TEST;
                 break;
        case 1:  trait->flags |= TRAIT_OBJECT_IDENTITY;
        default: break;
    }

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'value allowed' mode of a CTrait instance:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_value_allowed ( trait_object * trait, PyObject * args ) {

    int value_allowed;

    if ( !PyArg_ParseTuple( args, "i", &value_allowed ) )
        return NULL;

    if ( value_allowed ) {
        trait->flags |= TRAIT_VALUE_ALLOWED;
    } else {
        trait->flags &= (~TRAIT_VALUE_ALLOWED);
    }

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'value trait' mode of a CTrait instance:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_value_property ( trait_object * trait, PyObject * args ) {

    int value_trait;

    if ( !PyArg_ParseTuple( args, "i", &value_trait ) )
        return NULL;

    if ( value_trait ) {
        trait->flags |= TRAIT_VALUE_PROPERTY;
    } else {
        trait->flags &= (~TRAIT_VALUE_PROPERTY);
    }

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'setattr_original_value' flag of a CTrait instance:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_setattr_original_value ( trait_object * trait, PyObject * args ) {

    int original_value;

    if ( !PyArg_ParseTuple( args, "i", &original_value ) )
        return NULL;

    if ( original_value != 0 ) {
        trait->flags |= TRAIT_SETATTR_ORIGINAL_VALUE;
    } else {
        trait->flags &= (~TRAIT_SETATTR_ORIGINAL_VALUE);
    }

    Py_INCREF( trait );
    return (PyObject *) trait;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'post_setattr_original_value' flag of a CTrait
|  instance (used in the processing of 'post_settattr' calls):
+----------------------------------------------------------------------------*/

static PyObject *
_trait_post_setattr_original_value ( trait_object * trait, PyObject * args ) {

    int original_value;

    if ( !PyArg_ParseTuple( args, "i", &original_value ) )
        return NULL;

    if ( original_value != 0 ) {
        trait->flags |= TRAIT_POST_SETATTR_ORIGINAL_VALUE;
    } else {
        trait->flags &= (~TRAIT_POST_SETATTR_ORIGINAL_VALUE);
    }

    Py_INCREF( trait );
    return (PyObject *) trait;
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'is_mapped' flag of a CTrait instance (used in the
|  processing of the default value of a trait with a 'post_settattr' handler):
+----------------------------------------------------------------------------*/

static PyObject *
_trait_is_mapped ( trait_object * trait, PyObject * args ) {

    int is_mapped;

    if ( !PyArg_ParseTuple( args, "i", &is_mapped ) )
        return NULL;

    if ( is_mapped != 0 ) {
        trait->flags |= TRAIT_IS_MAPPED;
    } else {
        trait->flags &= (~TRAIT_IS_MAPPED);
    }

    Py_INCREF( trait );
    return (PyObject *) trait;
}

/*-----------------------------------------------------------------------------
|  Sets the 'property' value fields of a CTrait instance:
+----------------------------------------------------------------------------*/

static trait_setattr setattr_property_handlers[] = {
    setattr_property0, setattr_property1, setattr_property2, setattr_property3,
/*  The following entries are used by the __getstate__ method__: */
    (trait_setattr) post_setattr_trait_python, NULL
};

static PyObject *
_trait_property ( trait_object * trait, PyObject * args ) {

    PyObject * get, * set, * validate, * result, * temp;
    int get_n, set_n, validate_n;

    if ( PyTuple_GET_SIZE( args ) == 0 ) {
        if ( trait->flags & TRAIT_PROPERTY ) {
            result = PyTuple_New( 3 );
            if ( result != NULL ) {
                PyTuple_SET_ITEM( result, 0, temp = trait->delegate_name );
                Py_INCREF( temp );
                PyTuple_SET_ITEM( result, 1, temp = trait->delegate_prefix );
                Py_INCREF( temp );
                PyTuple_SET_ITEM( result, 2, temp = trait->py_validate );
                Py_INCREF( temp );
                return result;
            }
            return NULL;
        } else {
            Py_INCREF( Py_None );
            return Py_None;
        }
    }

    if ( !PyArg_ParseTuple( args, "OiOiOi", &get, &get_n, &set, &set_n,
                                            &validate, &validate_n ) )
        return NULL;
    if ( !PyCallable_Check( get ) || !PyCallable_Check( set )     ||
         ((validate != Py_None) && !PyCallable_Check( validate )) ||
         (get_n < 0)      || (get_n > 3) ||
         (set_n < 0)      || (set_n > 3) ||
         (validate_n < 0) || (validate_n > 3) ) {
        PyErr_SetString( PyExc_ValueError, "Invalid arguments." );
        return NULL;
    }

    trait->flags  |= TRAIT_PROPERTY;
    trait->getattr = getattr_property_handlers[ get_n ];
        if ( validate != Py_None ) {
        trait->setattr      = setattr_validate_property;
        trait->post_setattr = (trait_post_setattr) setattr_property_handlers[
                                                                      set_n ];
        trait->validate     = setattr_validate_handlers[ validate_n ];
        } else
        trait->setattr = setattr_property_handlers[ set_n ];

    trait->delegate_name   = get;
    trait->delegate_prefix = set;
    trait->py_validate     = validate;
    Py_INCREF( get );
    Py_INCREF( set );
    Py_INCREF( validate );
    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Clones one trait into another:
+----------------------------------------------------------------------------*/

static void
trait_clone ( trait_object * trait, trait_object * source ) {

    trait->flags              = source->flags;
    trait->getattr            = source->getattr;
    trait->setattr            = source->setattr;
    trait->post_setattr       = source->post_setattr;
    trait->py_post_setattr    = source->py_post_setattr;
    trait->validate           = source->validate;
    trait->py_validate        = source->py_validate;
    trait->default_value_type = source->default_value_type;
    trait->default_value      = source->default_value;
    trait->delegate_name      = source->delegate_name;
    trait->delegate_prefix    = source->delegate_prefix;
    trait->delegate_attr_name = source->delegate_attr_name;
    trait->handler            = source->handler;
    Py_XINCREF( trait->py_post_setattr );
    Py_XINCREF( trait->py_validate );
    Py_XINCREF( trait->delegate_name );
    Py_XINCREF( trait->default_value );
    Py_XINCREF( trait->delegate_prefix );
    Py_XINCREF( trait->handler );
}

static PyObject *
_trait_clone ( trait_object * trait, PyObject * args ) {

    trait_object * source;

        if ( !PyArg_ParseTuple( args, "O!", ctrait_type, &source ) )
        return NULL;

    trait_clone( trait, source );

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Returns (and optionally creates) the trait 'notifiers' list:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_notifiers ( trait_object * trait, PyObject * args ) {

    PyObject * result;
    PyObject * list;
    int force_create;

        if ( !PyArg_ParseTuple( args, "i", &force_create ) )
        return NULL;

    result = (PyObject *) trait->notifiers;
    if ( result == NULL ) {
        result = Py_None;
        if ( force_create && ((list = PyList_New( 0 )) != NULL) )
            trait->notifiers = (PyListObject *) (result = list);
    }

    Py_INCREF( result );
    return result;
}

/*-----------------------------------------------------------------------------
|  Converts a function to an index into a function table:
+----------------------------------------------------------------------------*/

static int
func_index ( void * function, void ** function_table ) {

    int i;

    for ( i = 0; function != function_table[i]; i++ );
    return i;
}

/*-----------------------------------------------------------------------------
|  Gets the pickleable state of the trait:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_getstate ( trait_object * trait, PyObject * args ) {

    PyObject * result;

    if ( !PyArg_ParseTuple( args, "" ) )
        return NULL;

    result = PyTuple_New( 15 );
    if ( result == NULL )
        return NULL;

    PyTuple_SET_ITEM( result,  0, Py2to3_PyNum_FromLong( func_index(
                  (void *) trait->getattr, (void **) getattr_handlers ) ) );
    PyTuple_SET_ITEM( result,  1, Py2to3_PyNum_FromLong( func_index(
                  (void *) trait->setattr, (void **) setattr_handlers ) ) );
    PyTuple_SET_ITEM( result,  2, Py2to3_PyNum_FromLong( func_index(
                  (void *) trait->post_setattr,
                  (void **) setattr_property_handlers ) ) );
    PyTuple_SET_ITEM( result,  3, get_callable_value( trait->py_post_setattr ));
    PyTuple_SET_ITEM( result,  4, Py2to3_PyNum_FromLong( func_index(
                  (void *) trait->validate, (void **) validate_handlers ) ) );
    PyTuple_SET_ITEM( result,  5, get_callable_value( trait->py_validate ) );
    PyTuple_SET_ITEM( result,  6, Py2to3_PyNum_FromLong( trait->default_value_type ) );
    PyTuple_SET_ITEM( result,  7, get_value( trait->default_value ) );
    PyTuple_SET_ITEM( result,  8, Py2to3_PyNum_FromLong( trait->flags ) );
    PyTuple_SET_ITEM( result,  9, get_value( trait->delegate_name ) );
    PyTuple_SET_ITEM( result, 10, get_value( trait->delegate_prefix ) );
    PyTuple_SET_ITEM( result, 11, Py2to3_PyNum_FromLong( func_index(
                  (void *) trait->delegate_attr_name,
                  (void **) delegate_attr_name_handlers ) ) );
    PyTuple_SET_ITEM( result, 12, get_value( NULL ) ); /* trait->notifiers */
    PyTuple_SET_ITEM( result, 13, get_value( trait->handler ) );
    PyTuple_SET_ITEM( result, 14, get_value( trait->obj_dict ) );

    return result;
}

/*-----------------------------------------------------------------------------
|  Restores the pickled state of the trait:
+----------------------------------------------------------------------------*/

static PyObject *
_trait_setstate ( trait_object * trait, PyObject * args ) {

    PyObject * ignore, * temp, *temp2;
    int getattr_index, setattr_index, post_setattr_index, validate_index,
        delegate_attr_name_index;

    if ( !PyArg_ParseTuple( args, "(iiiOiOiOiOOiOOO)",
                &getattr_index,             &setattr_index,
                &post_setattr_index,        &trait->py_post_setattr,
                &validate_index,            &trait->py_validate,
                &trait->default_value_type, &trait->default_value,
                &trait->flags,              &trait->delegate_name,
                &trait->delegate_prefix,    &delegate_attr_name_index,
                &ignore,                    &trait->handler,
                &trait->obj_dict ) )
        return NULL;

    trait->getattr      = getattr_handlers[ getattr_index ];
    trait->setattr      = setattr_handlers[ setattr_index ];
    trait->post_setattr = (trait_post_setattr) setattr_property_handlers[
                              post_setattr_index ];
    trait->validate     = validate_handlers[ validate_index ];
    trait->delegate_attr_name = delegate_attr_name_handlers[
                                    delegate_attr_name_index ];

    /* Convert any references to callable methods on the handler back into
       bound methods: */
    temp = trait->py_validate;
    if ( Py2to3_PyNum_Check( temp ) )
        trait->py_validate = PyObject_GetAttrString( trait->handler,
                                                     "validate" );
    else if ( PyTuple_Check( temp ) &&
              (Py2to3_PyNum_AsLong( PyTuple_GET_ITEM( temp, 0 ) ) == 10) ) {
        temp2 = PyObject_GetAttrString( trait->handler, "validate" );
        Py_INCREF( temp2 );
        Py_DECREF( PyTuple_GET_ITEM( temp, 2 ) );
        PyTuple_SET_ITEM( temp, 2, temp2 );
    }

    if ( Py2to3_PyNum_Check( trait->py_post_setattr ) )
        trait->py_post_setattr = PyObject_GetAttrString( trait->handler,
                                                         "post_setattr" );

    Py_INCREF( trait->py_post_setattr );
    Py_INCREF( trait->py_validate );
    Py_INCREF( trait->default_value );
    Py_INCREF( trait->delegate_name );
    Py_INCREF( trait->delegate_prefix );
    Py_INCREF( trait->handler );
    Py_INCREF( trait->obj_dict );

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Returns the current trait dictionary:
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_dict ( trait_object * trait, void * closure ) {

    PyObject * obj_dict = trait->obj_dict;
    if ( obj_dict == NULL ) {
        trait->obj_dict = obj_dict = PyDict_New();
        if ( obj_dict == NULL )
            return NULL;
    }
    Py_INCREF( obj_dict );
    return obj_dict;
}

/*-----------------------------------------------------------------------------
|  Sets the current trait dictionary:
+----------------------------------------------------------------------------*/

static int
set_trait_dict ( trait_object * trait, PyObject * value, void * closure ) {

    if ( !PyDict_Check( value ) )
        return dictionary_error();
    return set_value( &trait->obj_dict, value );
}

/*-----------------------------------------------------------------------------
|  Returns the current trait handler (if any):
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_handler ( trait_object * trait, void * closure ) {

    return get_value( trait->handler );
}

/*-----------------------------------------------------------------------------
|  Sets the current trait dictionary:
+----------------------------------------------------------------------------*/

static int
set_trait_handler ( trait_object * trait, PyObject * value, void * closure ) {

    return set_value( &trait->handler, value );
}

/*-----------------------------------------------------------------------------
|  Returns the current post_setattr (if any):
+----------------------------------------------------------------------------*/

static PyObject *
get_trait_post_setattr ( trait_object * trait, void * closure ) {

    return get_value( trait->py_post_setattr );
}

/*-----------------------------------------------------------------------------
|  Sets the value of the 'post_setattr' field of a CTrait instance:
+----------------------------------------------------------------------------*/

static int
set_trait_post_setattr ( trait_object * trait, PyObject * value,
                         void * closure ) {

    if ( !PyCallable_Check( value ) ) {
        PyErr_SetString( PyExc_ValueError,
                         "The assigned value must be callable." );
        return -1;
    }
    trait->post_setattr = post_setattr_trait_python;
    return set_value( &trait->py_post_setattr, value );
}

/*-----------------------------------------------------------------------------
|  'CTrait' instance methods:
+----------------------------------------------------------------------------*/

static PyMethodDef trait_methods[] = {
        { "__getstate__", (PyCFunction) _trait_getstate,       METH_VARARGS,
                PyDoc_STR( "__getstate__()" ) },
        { "__setstate__", (PyCFunction) _trait_setstate,       METH_VARARGS,
                PyDoc_STR( "__setstate__(state)" ) },
        { "default_value", (PyCFunction) _trait_default_value, METH_VARARGS,
                PyDoc_STR( "default_value(default_value)" ) },
        { "default_value_for", (PyCFunction) _trait_default_value_for, METH_VARARGS,
                PyDoc_STR( "default_value_for(object,name)" ) },
        { "set_validate",  (PyCFunction) _trait_set_validate,  METH_VARARGS,
                PyDoc_STR( "set_validate(validate_function)" ) },
        { "get_validate",  (PyCFunction) _trait_get_validate,  METH_NOARGS,
                PyDoc_STR( "get_validate()" ) },
        { "validate",      (PyCFunction) _trait_validate,      METH_VARARGS,
                PyDoc_STR( "validate(object,name,value)" ) },
        { "delegate",      (PyCFunction) _trait_delegate,      METH_VARARGS,
                PyDoc_STR( "delegate(delegate_name,prefix,prefix_type,modify_delegate)" ) },
        { "rich_comparison",  (PyCFunction) _trait_rich_comparison,  METH_VARARGS,
                PyDoc_STR( "rich_comparison(rich_comparison_boolean)" ) },
        { "comparison_mode",  (PyCFunction) _trait_comparison_mode,  METH_VARARGS,
                PyDoc_STR( "comparison_mode(comparison_mode_enum)" ) },
        { "value_allowed",  (PyCFunction) _trait_value_allowed,  METH_VARARGS,
                PyDoc_STR( "value_allowed(value_allowed_boolean)" ) },
        { "value_property",  (PyCFunction) _trait_value_property, METH_VARARGS,
                PyDoc_STR( "value_property(value_trait_boolean)" ) },
        { "setattr_original_value",
        (PyCFunction) _trait_setattr_original_value,       METH_VARARGS,
                PyDoc_STR( "setattr_original_value(original_value_boolean)" ) },
        { "post_setattr_original_value",
        (PyCFunction) _trait_post_setattr_original_value,  METH_VARARGS,
                PyDoc_STR( "post_setattr_original_value(original_value_boolean)" ) },
        { "is_mapped", (PyCFunction) _trait_is_mapped,  METH_VARARGS,
                PyDoc_STR( "is_mapped(is_mapped_boolean)" ) },
        { "property",      (PyCFunction) _trait_property,      METH_VARARGS,
                PyDoc_STR( "property([get,set,validate])" ) },
        { "clone",         (PyCFunction) _trait_clone,         METH_VARARGS,
                PyDoc_STR( "clone(trait)" ) },
        { "cast",          (PyCFunction) _trait_cast,          METH_VARARGS,
                PyDoc_STR( "cast(value)" ) },
        { "_notifiers",    (PyCFunction) _trait_notifiers,     METH_VARARGS,
                PyDoc_STR( "_notifiers(force_create)" ) },
        { NULL, NULL },
};

/*-----------------------------------------------------------------------------
|  'CTrait' property definitions:
+----------------------------------------------------------------------------*/

static PyGetSetDef trait_properties[] = {
        { "__dict__",     (getter) get_trait_dict,    (setter) set_trait_dict },
        { "handler",      (getter) get_trait_handler, (setter) set_trait_handler },
        { "post_setattr", (getter) get_trait_post_setattr,
                      (setter) set_trait_post_setattr },
        { 0 }
};

/*-----------------------------------------------------------------------------
|  'CTrait' type definition:
+----------------------------------------------------------------------------*/

static PyTypeObject trait_type = {
    PyVarObject_HEAD_INIT( DEFERRED_ADDRESS( &PyType_Type ), 0 )
    "traits.ctraits.cTrait",
    sizeof( trait_object ),
    0,
    (destructor) trait_dealloc,                    /* tp_dealloc */
    0,                                             /* tp_print */
    0,                                             /* tp_getattr */
    0,                                             /* tp_setattr */
    0,                                             /* tp_compare */
    0,                                             /* tp_repr */
    0,                                             /* tp_as_number */
    0,                                             /* tp_as_sequence */
    0,                                             /* tp_as_mapping */
    0,                                             /* tp_hash */
    0,                                             /* tp_call */
    0,                                             /* tp_str */
    (getattrofunc) trait_getattro,                 /* tp_getattro */
    0,                                             /* tp_setattro */
    0,                                                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,/* tp_flags */
    0,                                             /* tp_doc */
    (traverseproc) trait_traverse,                 /* tp_traverse */
    (inquiry) trait_clear,                         /* tp_clear */
    0,                                             /* tp_richcompare */
    0,                                             /* tp_weaklistoffset */
    0,                                             /* tp_iter */
    0,                                             /* tp_iternext */
    trait_methods,                                 /* tp_methods */
    0,                                             /* tp_members */
    trait_properties,                              /* tp_getset */
    DEFERRED_ADDRESS( &PyBaseObject_Type ),        /* tp_base */
    0,                                             /* tp_dict */
    0,                                             /* tp_descr_get */
    0,                                             /* tp_descr_set */
    sizeof( trait_object ) - sizeof( PyObject * ), /* tp_dictoffset */
    (initproc) trait_init,                         /* tp_init */
    DEFERRED_ADDRESS( PyType_GenericAlloc ),       /* tp_alloc */
    DEFERRED_ADDRESS( PyType_GenericNew )          /* tp_new */
};

/*-----------------------------------------------------------------------------
|  Sets the global 'Undefined' and 'Uninitialized' values:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_undefined ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "OO", &Undefined, &Uninitialized ) )
        return NULL;

    Py_INCREF( Undefined );
    Py_INCREF( Uninitialized );

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the global 'TraitError' and 'DelegationError' exception types:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_exceptions ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "OO", &TraitError, &DelegationError ) )
        return NULL;

    Py_INCREF( TraitError );
    Py_INCREF( DelegationError );

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the global 'TraitListObject', TraitSetObject and 'TraitDictObject'
|  classes:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_list_classes ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "OOO", &TraitListObject, &TraitSetObject,
                                         &TraitDictObject ) )
        return NULL;

    Py_INCREF( TraitListObject );
    Py_INCREF( TraitSetObject );
    Py_INCREF( TraitDictObject );

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the global 'TraitValue' class:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_value_class ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "O", &TraitValue ) )
        return NULL;

    Py_INCREF( TraitValue );

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the global 'adapt' reference to the PyProtocols 'adapt' function:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_adapt ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "O", &adapt ) )
        return NULL;

    Py_INCREF( adapt );

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the global 'validate_implements' reference to the Python level
|  function:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_validate_implements ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "O", &validate_implements ) )
        return NULL;

    Py_INCREF( validate_implements );

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the global 'ctrait_type' class reference:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_ctrait ( PyObject * self, PyObject * args ) {

    if ( !PyArg_ParseTuple( args, "O", &ctrait_type ) )
        return NULL;

    Py_INCREF( ctrait_type );

    Py_INCREF( Py_None );
    return Py_None;
}

/*-----------------------------------------------------------------------------
|  Sets the global 'trait_notification_handler' function, and returns the
|  previous value:
+----------------------------------------------------------------------------*/

static PyObject *
_ctraits_trait_notification_handler ( PyObject * self, PyObject * args ) {

    PyObject * result = _trait_notification_handler;

    if ( !PyArg_ParseTuple( args, "O", &_trait_notification_handler ) ) {
        return NULL;
    }

    if ( _trait_notification_handler == Py_None ) {
        _trait_notification_handler = NULL;
    } else {
        Py_INCREF( _trait_notification_handler );
    }

    if ( result == NULL ) {
        Py_INCREF( Py_None );
        result = Py_None;
    }

    return result;
}

/*-----------------------------------------------------------------------------
|  'CTrait' instance methods:
+----------------------------------------------------------------------------*/

static PyMethodDef ctraits_methods[] = {
        { "_undefined",    (PyCFunction) _ctraits_undefined,    METH_VARARGS,
                PyDoc_STR( "_undefined(Undefined,Uninitialized)" ) },
        { "_exceptions",   (PyCFunction) _ctraits_exceptions,   METH_VARARGS,
                PyDoc_STR( "_exceptions(TraitError,DelegationError)" ) },
        { "_list_classes", (PyCFunction) _ctraits_list_classes, METH_VARARGS,
                PyDoc_STR( "_list_classes(TraitListObject,TraitSetObject,TraitDictObject)" ) },
        { "_value_class", (PyCFunction) _ctraits_value_class,   METH_VARARGS,
                PyDoc_STR( "_value_class(TraitValue)" ) },
        { "_adapt", (PyCFunction) _ctraits_adapt, METH_VARARGS,
                PyDoc_STR( "_adapt(PyProtocols._speedups.adapt)" ) },
        { "_validate_implements", (PyCFunction) _ctraits_validate_implements,
        METH_VARARGS, PyDoc_STR( "_validate_implements(validate_implements)" )},
        { "_ctrait",       (PyCFunction) _ctraits_ctrait,       METH_VARARGS,
                PyDoc_STR( "_ctrait(CTrait_class)" ) },
        { "_trait_notification_handler",
        (PyCFunction) _ctraits_trait_notification_handler,  METH_VARARGS,
        PyDoc_STR( "_trait_notification_handler(handler)" ) },
        { NULL, NULL },
};

/*-----------------------------------------------------------------------------
|  Performs module and type initialization:
+----------------------------------------------------------------------------*/

Py2to3_MOD_INIT(ctraits) {
    /* Create the 'ctraits' module: */
    PyObject * module;

    Py2to3_MOD_DEF(
        module,
        "ctraits",
        ctraits__doc__,
        ctraits_methods
    );

    if ( module == NULL )
       return Py2to3_MOD_ERROR_VAL;

    /* Create the 'CHasTraits' type: */
    has_traits_type.tp_base  = &PyBaseObject_Type;
    has_traits_type.tp_alloc = PyType_GenericAlloc;
    if ( PyType_Ready( &has_traits_type ) < 0 )
       return Py2to3_MOD_ERROR_VAL;

    Py_INCREF( &has_traits_type );
    if ( PyModule_AddObject( module, "CHasTraits",
                         (PyObject *) &has_traits_type ) < 0 )
       return Py2to3_MOD_ERROR_VAL;

    /* Create the 'CTrait' type: */
    trait_type.tp_base  = &PyBaseObject_Type;
    trait_type.tp_alloc = PyType_GenericAlloc;
    trait_type.tp_new   = PyType_GenericNew;
    if ( PyType_Ready( &trait_type ) < 0 )
       return Py2to3_MOD_ERROR_VAL;

    Py_INCREF( &trait_type );
    if ( PyModule_AddObject( module, "cTrait",
                         (PyObject *) &trait_type ) < 0 )
       return Py2to3_MOD_ERROR_VAL;

    /* Predefine a Python string == "__class_traits__": */
    class_traits = Py2to3_SimpleString_FromString( "__class_traits__" );

    /* Predefine a Python string == "__listener_traits__": */
    listener_traits = Py2to3_SimpleString_FromString( "__listener_traits__" );

    /* Predefine a Python string == "editor": */
    editor_property = Py2to3_SimpleString_FromString( "editor" );

    /* Predefine a Python string == "__prefix__": */
    class_prefix = Py2to3_SimpleString_FromString( "__prefix__" );

    /* Predefine a Python string == "trait_added": */
    trait_added = Py2to3_SimpleString_FromString( "trait_added" );

    /* Create an empty tuple: */
    empty_tuple = PyTuple_New( 0 );

    /* Create an empty dict: */
    empty_dict = PyDict_New();

    /* Create the 'is_callable' marker: */
    is_callable = Py2to3_PyNum_FromLong( -1 );

    return Py2to3_MOD_SUCCESS_VAL(module);
}
