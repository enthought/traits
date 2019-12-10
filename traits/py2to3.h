/*
    This header contains version specific implementations of certain
    often used tasks, behind a version agnostic API.
*/
#include "Python.h"


/* Attribute names
*/

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

/* Get hash of an object, using cached value for attribute names. */

Py_hash_t Py2to3_GetHash_wCache(PyObject *obj){
#ifndef Py_LIMITED_API
    Py_hash_t hash = -1;
    if ( PyUnicode_CheckExact( obj ) ) {
        hash = ((PyUnicodeObject *) obj)->_base._base.hash;
    }
    if (hash == -1) {
        hash = PyObject_Hash( obj );
    }
    return hash;
#else
    return PyObject_Hash( obj );
#endif // #ifndef Py_LIMITED_API
}


/* Get a value from a dict whose keys are attribute names.

  If *name* is of a type unfitting for an attribute name,
  *bad_attr* is returned.

  Does use the hash cache where possible.

  Precondition: *dict* is a valid PyDictObject
 */

#define Py2to3_AttrNameCheck(name) (PyUnicode_Check(name))

PyObject *Py2to3_GetAttrDictValue(PyDictObject * dict, PyObject *name, PyObject *bad_attr) {
    if( !PyUnicode_Check(name) )
        return bad_attr;

    return PyDict_GetItem((PyObject *)dict, name);
}


double Py2to3_PyNum_AsDouble(PyObject *value) {
    if ( !PyLong_Check( value ) ) {
        PyErr_SetNone( PyExc_TypeError );
        return -1.;
    }
    return PyLong_AsDouble( value );
}


#define Py2to3_MOD_ERROR_VAL NULL
#define Py2to3_MOD_SUCCESS_VAL(val) val
#define Py2to3_MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)
#define Py2to3_MOD_DEF(ob, name, doc, methods) \
        static struct PyModuleDef moduledef = { \
        PyModuleDef_HEAD_INIT, name, doc, -1, methods, }; \
        ob = PyModule_Create(&moduledef);
