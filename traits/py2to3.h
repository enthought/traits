/*
    This header contains version specific implementations of certain
    often used tasks, behind a version agnostic API.
*/
#include "Python.h"


/* Attribute names
*/

#if PY_MAJOR_VERSION < 3
PyObject *Py2to3_NormaliseAttrName(PyObject *name) {

    if( PyString_Check(name) ){
        return name;
#ifdef Py_USING_UNICODE
    } else if ( PyUnicode_Check( name ) ) {
        return PyUnicode_AsEncodedString( name, NULL, NULL );
#endif // #ifdef Py_USING_UNICODE
    }
    return NULL;
}
void Py2to3_FinishNormaliseAttrName(PyObject *name,PyObject *nname){
    if(nname != name){
        Py_DECREF(nname);
    }
}
PyObject *Py2to3_AttrNameCStr(PyObject *name) {
    return name;
}
#define Py2to3_AttrName_AS_STRING(name) PyString_AS_STRING(name)
void Py2to3_FinishAttrNameCStr(PyObject *nname){
};
#else
PyObject *Py2to3_NormaliseAttrName(PyObject *name) {

    if( PyUnicode_Check(name) ){
        return name;
    }
    return NULL;
}
void Py2to3_FinishNormaliseAttrName(PyObject *name,PyObject *nname){
}
PyObject *Py2to3_AttrNameCStr(PyObject *name) {
    return PyUnicode_AsUTF8String(name);
}
#define Py2to3_AttrName_AS_STRING(name) PyBytes_AS_STRING(name)
void Py2to3_FinishAttrNameCStr(PyObject *nname){
    Py_DECREF(nname);
};
#endif


/*
    Simple strings for PyErr formatting:
    * Python 2:
      - Attributes are ASCII
      - PyErr_Format uses PyString_FromFormat
    * Python 3:
      - Attributes are Unicode
      - PyErr_Format uses PyUnicode_FromFormat

    Thus SimpleString == PyString if Python < 3 else PyUnicode
*/
#if PY_MAJOR_VERSION >= 3

#define Py2to3_SimpleString_Check(name) PyUnicode_Check(name)
#define Py2to3_SimpleString_GET_SIZE(name) PyUnicode_GET_SIZE(name)
#define Py2to3_SimpleString_Type PyUnicode_Type
#define Py2to3_PYERR_SIMPLE_STRING_FMTCHR "U"
#define Py2to3_PYERR_PREPARE_SIMPLE_STRING(name) name
#define Py2to3_SimpleString_FromString(string) PyUnicode_FromString(string)

#else

#define Py2to3_SimpleString_Check(name) PyString_Check(name)
#define Py2to3_SimpleString_GET_SIZE(name) PyString_GET_SIZE(name)
#define Py2to3_SimpleString_Type PyString_Type
#define Py2to3_PYERR_SIMPLE_STRING_FMTCHR "s"
#define Py2to3_PYERR_PREPARE_SIMPLE_STRING(name) PyString_AS_STRING(name)
#define Py2to3_SimpleString_FromString(string) PyString_FromString(string)

#endif


/* The following macro is defined from Python 2.6 and differently in Python 3 */
#ifndef Py_TYPE
    #define Py_TYPE(ob) (((PyObject*)(ob))->ob_type)
#endif


/* In Python 3, all ints are longs */
#if PY_MAJOR_VERSION >= 3
    #define Py2to3_PyNum_Check PyLong_Check
    #define Py2to3_PyNum_FromLong PyLong_FromLong
    #define Py2to3_PyNum_AsLong PyLong_AsLong
#else
    #define Py2to3_PyNum_Check PyInt_Check
    #define Py2to3_PyNum_FromLong PyInt_FromLong
    #define Py2to3_PyNum_AsLong PyInt_AsLong
#endif

/* Get hash of an object, using cached value for attribute names

 */
#ifndef Py_hash_t
    #define Py_hash_t long
#endif

#if PY_MAJOR_VERSION < 3
long Py2to3_GetHash_wCache(PyObject *obj){
    long hash;

    if ( PyString_CheckExact( obj ) &&
     ((hash = ((PyStringObject *) obj)->ob_shash) != -1) ) {
        return hash;
    }
    return PyObject_Hash( obj );
}
#else
Py_hash_t Py2to3_GetHash_wCache(PyObject *obj){
#ifndef Py_LIMITED_API
    Py_hash_t hash = -1;
    if ( PyUnicode_CheckExact( obj ) ) {
#if PY_MAJOR_VERSION < 3 || PY_MINOR_VERSION < 3
        hash = ((PyUnicodeObject *) obj)->hash;
#else
        hash = ((PyUnicodeObject *) obj)->_base._base.hash;
#endif
//    } else if ( PyBytes_CheckExact( key )) {
//        hash = ((PyBytesObject *) key)->ob_shash;
    }
    if (hash == -1) {
        hash = PyObject_Hash( obj );
    }
    return hash;
#else
    return PyObject_Hash( obj );
#endif // #ifndef Py_LIMITED_API
}
#endif // #if PY_MAJOR_VERION < 3


/* Get a value from a dict whose keys are attribute names.

  If *name* is of a type unfitting for an attribute name,
  *bad_attr* is returned.

  Does use the hash cache where possible.

  Precondition: *dict* is a valid PyDictObject
 */
#if PY_MAJOR_VERSION < 3

#ifdef Py_USING_UNICODE
#define Py2to3_AttrNameCheck(name) (PyString_Check(name) || PyUnicode_Check(name))
#else
#define Py2to3_AttrNameCheck(name) (PyString_Check(name))
#endif

PyObject *Py2to3_GetAttrDictValue(PyDictObject * dict, PyObject *name, PyObject *bad_attr) {

    long hash;
    PyObject *nname;
    PyObject *value;
    if ( PyString_CheckExact( name ) ) {
        if ( (hash = ((PyStringObject *) name)->ob_shash) == -1 )
           hash = PyObject_Hash( name );
        return (dict->ma_lookup)( dict, name, hash )->me_value;
    }

    nname = Py2to3_NormaliseAttrName(name);
    if( nname == NULL ){
        PyErr_Clear();
        return bad_attr;
    }

    hash = PyObject_Hash( nname );
    if( hash == -1 ){
        Py2to3_FinishNormaliseAttrName(name,nname);
        PyErr_Clear();
        return NULL;
    }
    value = (dict->ma_lookup)( dict, nname, hash )->me_value;
    Py2to3_FinishNormaliseAttrName(name,nname);
    return value;
}

#else // #if PY_MAJOR_VERSION < 3

#define Py2to3_AttrNameCheck(name) (PyUnicode_Check(name))

PyObject *Py2to3_GetAttrDictValue(PyDictObject * dict, PyObject *name, PyObject *bad_attr) {
#if !defined(Py_LIMITED_API) && (PY_MAJOR_VERSION < 3 || PY_MINOR_VERSION < 3) && 0 // this does not work as intended! don't use it!
    Py_hash_t hash;
    if( PyUnicode_CheckExact( name ) ) {
#if PY_MINOR_VERSION < 3
        hash = ((PyUnicodeObject *) dict)->hash;
#else
        // currently not usable, as dict->ma_lookup does not exist either
        hash = ((PyUnicodeObject *) dict)->_base._base.hash;
#endif
        if( hash == -1)
           hash = PyObject_Hash( name );
        return (dict->ma_lookup)( dict, name, hash )->me_value;
    }
#endif // #ifndef Py_LIMITED_API
    if( !PyUnicode_Check(name) )
        return bad_attr;

    return PyDict_GetItem((PyObject *)dict, name);
}

#endif // #if PY_MAJOR_VERSION < 3


/*
*/

double Py2to3_PyNum_AsDouble(PyObject *value) {
#if PY_MAJOR_VERSION < 3
    if ( PyInt_Check( value ) ) {
        return (double) PyInt_AS_LONG( value );
    } else if( !PyLong_Check(value) ){
#else
    if ( !PyLong_Check( value ) ) {
#endif  // #if PY_MAJOR_VERSION < 3
        PyErr_SetNone( PyExc_TypeError );
        return -1.;
    }
    return PyLong_AsDouble( value );
}


#ifndef PyVarObject_HEAD_INIT
    #define PyVarObject_HEAD_INIT(type, size) \
        PyObject_HEAD_INIT(type) size,
#endif



#if PY_MAJOR_VERSION >= 3
  #define Py2to3_MOD_ERROR_VAL NULL
  #define Py2to3_MOD_SUCCESS_VAL(val) val
  #define Py2to3_MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
  #define Py2to3_MOD_DEF(ob, name, doc, methods) \
          static struct PyModuleDef moduledef = { \
            PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
          ob = PyModule_Create(&moduledef);
#else
  #define Py2to3_MOD_ERROR_VAL
  #define Py2to3_MOD_SUCCESS_VAL(val)
  #define Py2to3_MOD_INIT(name) void init##name(void)
  #define Py2to3_MOD_DEF(ob, name, doc, methods) \
          ob = Py_InitModule3(name, methods, doc);
#endif
