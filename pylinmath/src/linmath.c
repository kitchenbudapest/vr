/* INFO ************************************************************************
**                                                                            **
**                                  kibu-vr                                   **
**                                  =======                                   **
**                                                                            **
**        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         **
**                       Version: 0.1.2.381 (20150416)                        **
**                       File: pylinmath/src/linmath.c                        **
**                                                                            **
**               For more information about the project, visit                **
**                            <http://vr.kibu.hu>.                            **
**              Copyright (C) 2015 Peter Varo, Kitchen Budapest               **
**                                                                            **
**  This program is free software: you can redistribute it and/or modify it   **
**   under the terms of the GNU General Public License as published by the    **
**       Free Software Foundation, either version 3 of the License, or        **
**                    (at your option) any later version.                     **
**                                                                            **
**    This program is distributed in the hope that it will be useful, but     **
**         WITHOUT ANY WARRANTY; without even the implied warranty of         **
**            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.            **
**            See the GNU General Public License for more details.            **
**                                                                            **
**     You should have received a copy of the GNU General Public License      **
**     along with this program, most likely a file in the root directory,     **
**        called 'LICENSE'. If not, see <http://www.gnu.org/licenses>.        **
**                                                                            **
************************************************************************ INFO */

/* Include python header:
   Since Python may define some pre-processor definitions which affect the
   standard headers on some systems, you must include Python.h before any
   standard headers are included */
/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
#include <Python.h>/*
    type  : PyObject
            PyTypeObject
            destructor
            initproc
    const : Py_TPFLAGS_DEFAULT
            Py_TPFLAGS_BASETYPE
    macro : PyObject_HEAD
            PyObject_HEAD_INIT
            Py_TYPE
            Py_INCREF
            Py_XDECREF
            PyDoc_STRVAR
    func  : Py_BuildValue
            PyArg_ParseTuple
            PyArg_ParseTupleAndKeywords
            PyErr_SetString
            PyObject_CallObject
            PyType_Ready
*/

#include <structmember.h>/*
    type  : PyMemberDef
            PyMethodDef
            PyModuleDef
            PyMODINIT_FUNC
    macro : PyModuleDef_HEAD_INIT
    func  : PyModule_Create
            PyModule_AddObject
*/

/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
#include <linmath/linmath.h> /*
    type  : vec3
    func  : vec3_add
*/



/* Module level constants */
/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
#define PYTHON_RETURN_VALUE_SUCCESS             0
#define PYTHON_RETURN_VALUE_FAILURE            -1
#define PYTHON_MODULE_CAN_BE_REINITIALISED      1
#define PYTHON_MODULE_CAN_NOT_BE_REINITIALISED -1
#define MODULE_NAME                             "linmath"
#define REPR_BUFFER_SIZE                        256



/*----------------------------------------------------------------------------*/
typedef struct
{
    PyObject_HEAD
    vec3 vector;
} linmath_Vec3;

/* Forward declare Type */
static PyTypeObject linmath_Vec3Type;


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static int
linmath_Vec3_init(linmath_Vec3 *self,
                  PyObject *args,
                  PyObject *kwargs)
{
    /* Set default values */
    self->vector[0] = 0.f;
    self->vector[1] = 0.f;
    self->vector[2] = 0.f;

    /* Unpack and store arguments */
    static char *kwlist[] = {"x", "y", "z", NULL};
    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "|fff:__init__",
                                     kwlist,
                                     self->vector + 0,
                                     self->vector + 1,
                                     self->vector + 2))
        return PYTHON_RETURN_VALUE_FAILURE;
    /* If everything went fine */
    return PYTHON_RETURN_VALUE_SUCCESS;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static void
linmath_Vec3_dealloc(linmath_Vec3 *self)
{
    /* Free self as a python object */
    Py_TYPE(self)->tp_free((PyObject *)self);
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
// static PyObject *
// linmath_Vec3___getitem__(linmath_Vec3 *self,
//                          PyObject     *index)
// {
//     /* Check if index is an integer (long) or not */
//     if (!PyLong_Check(index))
//     {
//         PyErr_SetString(PyExc_TypeError, "type of 'index' is not 'int'")
//         return NULL;
//     }
//     long i = PyLong_AsLong(index);
//     if (i > 2)
//     {
//         PyErr_SetString(PyExc_IndexError, "index is out of range");
//         return NULL;
//     }
//     /* If so, return the corresponding float value */
//     return Py_BuildValue("f", self->vector[i]);
// }


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Vec3___add__(linmath_Vec3 *self,
                     PyObject     *other)
{
    vec3 *other_vec;
    if (PyTuple_Check(other))
    {
        vec3 tuple;
        /* If tuple's length is lesser than 3, PyTuple_GetItem will raise
           an IndexError, so this function can safely return */
        for (size_t i=0; i<3; i++)
            if (!PyArg_ParseTuple(other,
                                  "fff",
                                  tuple + 0,
                                  tuple + 1,
                                  tuple + 2))
                return NULL;
        other_vec = &tuple;
    }
    else if (PyObject_IsInstance(other, (PyObject *)&linmath_Vec3Type))
        other_vec = &((linmath_Vec3 *)other)->vector;
    else
    {
        PyErr_SetString(PyExc_TypeError, "type of 'other' is not 'Vec3'");
        return NULL;
    }

    /* Create result vector, calculate and then return result */
    PyObject *result = PyObject_CallObject((PyObject *)&linmath_Vec3Type, NULL);
    vec3_add(((linmath_Vec3 *)result)->vector,
             ((linmath_Vec3 *)self)->vector,
             *other_vec);
    return result;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Vec3___repr__(linmath_Vec3 *self)
{
    char repr_buffer[REPR_BUFFER_SIZE];
    snprintf(repr_buffer,
             REPR_BUFFER_SIZE,
             "Vec3(x=%f, y=%f, z=%f)",
             self->vector[0],
             self->vector[1],
             self->vector[2]);
    return Py_BuildValue("s", repr_buffer);
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
// static PyMethodDef oculus_OculusRiftDK2_methods[] = {
//     {"__add__",     (PyCFunction)linmath_Vec3___add__,
//                     METH_O,
//                     "Add two vectors, returns a new Vec3 object"},
//     {"__getitem__", (PyCFunction)linmath_Vec3___getitem__,
//                     METH_O,
//                     ""},
//     {NULL, NULL, 0, NULL}
// };


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyNumberMethods linmath_Vec3_number_methods = {
    .nb_add                  = (binaryfunc)linmath_Vec3___add__, // binaryfunc
    .nb_subtract             = 0,                                // binaryfunc
    .nb_multiply             = 0,                                // binaryfunc
    .nb_remainder            = 0,                                // binaryfunc
    .nb_divmod               = 0,                                // binaryfunc
    .nb_power                = 0,                                // ternaryfunc
    .nb_negative             = 0,                                // unaryfunc
    .nb_positive             = 0,                                // unaryfunc
    .nb_absolute             = 0,                                // unaryfunc
    .nb_bool                 = 0,                                // inquiry
    .nb_invert               = 0,                                // unaryfunc
    .nb_lshift               = 0,                                // binaryfunc
    .nb_rshift               = 0,                                // binaryfunc
    .nb_and                  = 0,                                // binaryfunc
    .nb_xor                  = 0,                                // binaryfunc
    .nb_or                   = 0,                                // binaryfunc
    .nb_int                  = 0,                                // unaryfunc
    .nb_reserved             = 0,                                // void*
    .nb_float                = 0,                                // unaryfunc
    .nb_inplace_add          = 0,                                // binaryfunc
    .nb_inplace_subtract     = 0,                                // binaryfunc
    .nb_inplace_multiply     = 0,                                // binaryfunc
    .nb_inplace_remainder    = 0,                                // binaryfunc
    .nb_inplace_power        = 0,                                // ternaryfunc
    .nb_inplace_lshift       = 0,                                // binaryfunc
    .nb_inplace_rshift       = 0,                                // binaryfunc
    .nb_inplace_and          = 0,                                // binaryfunc
    .nb_inplace_xor          = 0,                                // binaryfunc
    .nb_inplace_or           = 0,                                // binaryfunc
    .nb_floor_divide         = 0,                                // binaryfunc
    .nb_true_divide          = 0,                                // binaryfunc
    .nb_inplace_floor_divide = 0,                                // binaryfunc
    .nb_inplace_true_divide  = 0,                                // binaryfunc
    .nb_index                = 0,                                // unaryfunc
};


/*----------------------------------------------------------------------------*/
PyDoc_STRVAR(Vec3_doc,
             "Represents a vector of 3 floats");

static PyTypeObject linmath_Vec3Type = {
    PyObject_HEAD_INIT(NULL)
    .tp_name           = MODULE_NAME ".Vec3",
    .tp_basicsize      = sizeof(linmath_Vec3),
    .tp_itemsize       = 0,
    .tp_dealloc        = (destructor)linmath_Vec3_dealloc,
    .tp_print          = 0,
    .tp_getattr        = 0,
    .tp_setattr        = 0,
    .tp_reserved       = 0,
    .tp_repr           = (reprfunc)linmath_Vec3___repr__,
    .tp_as_number      = &linmath_Vec3_number_methods,
    .tp_as_sequence    = 0,
    .tp_as_mapping     = 0,
    .tp_hash           = 0,
    .tp_call           = 0,
    .tp_str            = 0,
    .tp_getattro       = 0,
    .tp_setattro       = 0,
    .tp_as_buffer      = 0,
    .tp_flags          = Py_TPFLAGS_DEFAULT |
                         Py_TPFLAGS_BASETYPE, /* Can be subtyped */
    .tp_doc            = Vec3_doc,
    .tp_traverse       = 0,
    .tp_clear          = 0,
    .tp_richcompare    = 0,
    .tp_weaklistoffset = 0,
    .tp_iter           = 0,
    .tp_iternext       = 0,
    .tp_methods        = 0, // oculus_OculusRiftDK2_methods,
    .tp_members        = 0,
    .tp_getset         = 0,
    .tp_base           = 0,
    .tp_dict           = 0,
    .tp_descr_get      = 0,
    .tp_descr_set      = 0,
    .tp_dictoffset     = 0,
    .tp_init           = (initproc)linmath_Vec3_init,
    .tp_alloc          = 0,
    .tp_new            = PyType_GenericNew,
    // .tp_free           = 0,
    // .tp_is_gc          = 0,
    // .tp_bases          = 0,
    // .tp_mro            = 0,
    // .tp_cache          = 0,
    // .tp_subclasses     = 0,
    // .tp_weaklist       = 0,
    // .tp_del            = 0,
    // .tp_version_tag    = 0,
    // .tp_finalize       = 0,
};


/*----------------------------------------------------------------------------*/
PyDoc_STRVAR(linmath_module_doc,
             "linmath module is a wrapper around the linmath.h "
             "(https://github.com/datenwolf/linmath.h) which by definition: "
             "\"A lean linear math library, aimed at graphics programming. "
             "Supports vec3, vec4, mat4x4 and quaternions\"");

static struct PyModuleDef linmath_module = {
    PyModuleDef_HEAD_INIT,
    .m_name     = MODULE_NAME,
    .m_doc      = linmath_module_doc,
    .m_size     = PYTHON_MODULE_CAN_BE_REINITIALISED,
    .m_methods  = NULL,
    .m_reload   = NULL,
    .m_traverse = NULL,
    .m_clear    = NULL,
    .m_free     = NULL,
};


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
PyMODINIT_FUNC
PyInit_linmath(void)
{
    /* Create module */
    PyObject *module = PyModule_Create(&linmath_module);
    if (!module)
        goto Module_Init_Error;

    /* Finalise Vec3 class */
    if (PyType_Ready(&linmath_Vec3Type))
        goto Module_Make_Object_Ready_Error;

    /* Insert Vec3 class into module */
    Py_INCREF((PyObject *)&linmath_Vec3Type);
    if (!PyModule_AddObject(module,
                            "Vec3",
                            (PyObject *)&linmath_Vec3Type) < 0)
    {
        Py_XDECREF((PyObject *)&linmath_Vec3Type);
        goto Module_Add_Object_Error;
    }

    /* If everything went fine */
    return module;

    /* If there was a problem */
    Module_Add_Object_Error:
    Module_Make_Object_Ready_Error:
        Py_XDECREF(module);
    Module_Init_Error:
        return NULL;
}
