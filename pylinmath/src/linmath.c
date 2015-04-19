/* INFO ************************************************************************
**                                                                            **
**                                  kibu-vr                                   **
**                                  =======                                   **
**                                                                            **
**        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         **
**                       Version: 0.1.2.480 (20150419)                        **
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
#include <stdio.h> /*
    func  : snprintf
*/

#include <string.h> /*
    func  : strncat
*/

/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
#include <linmath/linmath.h> /*
    type  : vec3
            mat4x4
    func  : vec3_add
            vec3_sub
            vec3_len
            vec3_norm
            vec3_scale
            vec3_reflect
            vec3_mul_inner
            vec3_mul_cross
            mat4x4_add
            mat4x4_sub
            mat4x4_mul
            mat4x4_scale
            mat4x4_identity
*/



/* Module level constants */
/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
#define PYTHON_RETURN_VALUE_SUCCESS             0
#define PYTHON_RETURN_VALUE_FAILURE            -1
#define PYTHON_MODULE_CAN_BE_REINITIALISED      1
#define PYTHON_MODULE_CAN_NOT_BE_REINITIALISED -1
#define MODULE_NAME                             "linmath"
#define REPR_BUFFER_SIZE                        256
#define UNSUPPORTED_TYPE_OTHER                  "Unsupported type for 'other'"
#define VEC3_LENGTH                             3
#define MAT4X4_LENGTH                           4
#define UNUSED_PARAMETER(parameter)             (void)parameter



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
    for (size_t i=0; i<VEC3_LENGTH; i++)
        self->vector[i] = 0.f;

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
static PyObject *
linmath_Vec3___add__(linmath_Vec3 *self,
                     PyObject     *other)
{
    vec3 *other_vec;
    if (PyTuple_Check(other))
    {
        vec3 tuple = {0.f, 0.f, 0.f};
        /* If tuple's length is lesser than 3, PyTuple_GetItem will raise
           an IndexError, so this function can safely return */
        if (!PyArg_ParseTuple(other,
                              "ff|f:__add__",
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
        PyErr_SetString(PyExc_TypeError, UNSUPPORTED_TYPE_OTHER);
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
linmath_Vec3___sub__(linmath_Vec3 *self,
                     PyObject     *other)
{
    vec3 *other_vec;
    if (PyTuple_Check(other))
    {
        vec3 tuple = {0.f, 0.f, 0.f};
        /* If tuple's length is lesser than 3, PyTuple_GetItem will raise
           an IndexError, so this function can safely return */
        if (!PyArg_ParseTuple(other,
                              "ff|f:__sub__",
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
        PyErr_SetString(PyExc_TypeError, UNSUPPORTED_TYPE_OTHER);
        return NULL;
    }

    /* Create result vector, calculate and then return result */
    PyObject *result = PyObject_CallObject((PyObject *)&linmath_Vec3Type, NULL);
    vec3_sub(((linmath_Vec3 *)result)->vector,
             ((linmath_Vec3 *)self)->vector,
             *other_vec);
    return result;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Vec3___mul__(linmath_Vec3 *self,
                     PyObject     *other)
{
    float scalar = 1.f;
    vec3 *other_vec;
    PyObject *result;

    if (PyLong_Check(other))
    {
        scalar = (float)PyLong_AsLong(other);
        goto Scale_Vector;
    }
    else if (PyFloat_Check(other))
    {
        scalar = (float)PyFloat_AsDouble(other);
        goto Scale_Vector;
    }
    else if (PyTuple_Check(other))
    {
        vec3 tuple = {0.f, 0.f, 0.f};
        /* If tuple's length is lesser than 3, PyTuple_GetItem will raise
           an IndexError, so this function can safely return */
        if (!PyArg_ParseTuple(other,
                              "ff|f:__mul__",
                              tuple + 0,
                              tuple + 1,
                              tuple + 2))
            return NULL;
        other_vec = &tuple;
        goto Dot_Product_Vector;
    }
    else if (PyObject_IsInstance(other, (PyObject *)&linmath_Vec3Type))
    {
        other_vec = &((linmath_Vec3 *)other)->vector;
        goto Dot_Product_Vector;
    }
    else
    {
        PyErr_SetString(PyExc_TypeError, UNSUPPORTED_TYPE_OTHER);
        return NULL;
    }

    Dot_Product_Vector:
        return PyFloat_FromDouble(vec3_mul_inner(((linmath_Vec3 *)self)->vector,
                                                 *other_vec));
    Scale_Vector:
        /* Create result vector, calculate and then return result */
        result = PyObject_CallObject((PyObject *)&linmath_Vec3Type, NULL);
        vec3_scale(((linmath_Vec3 *)result)->vector,
                   ((linmath_Vec3 *)self)->vector,
                   scalar);
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
static Py_ssize_t
linmath_Vec3___len__(linmath_Vec3 *self)
{
    UNUSED_PARAMETER(self);
    return VEC3_LENGTH;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Vec3___getitem__(linmath_Vec3 *self,
                         Py_ssize_t   index)
{
    if (index < VEC3_LENGTH)
        return PyFloat_FromDouble(self->vector[index]);
    PyErr_SetString(PyExc_IndexError, "Vec3 index out of range");
    return NULL;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Vec3_getlength(linmath_Vec3 *self,
                       void         *closure)
{
    UNUSED_PARAMETER(closure);
    return PyFloat_FromDouble(vec3_len(((linmath_Vec3 *)self)->vector));
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Vec3_from_line(linmath_Vec3 *self,
                       PyObject     *args,
                       PyObject     *kwargs)
{
    UNUSED_PARAMETER(self);
    float x1 = 0.f, y1 = 0.f, z1 = 0.f,
          x2 = 0.f, y2 = 0.f, z2 = 0.f;
    static char *kwlist[] = {"x1", "y1", "z1",
                             "x2", "y2", "z2", NULL};
    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "|ffffff:from_line",
                                     kwlist,
                                     &x1, &y1, &z1,
                                     &x2, &y2, &z2))
        return NULL;

    PyObject *result = PyObject_CallObject((PyObject *)&linmath_Vec3Type, NULL);
    ((linmath_Vec3 *)result)->vector[0] = x2 - x1;
    ((linmath_Vec3 *)result)->vector[1] = y2 - y1;
    ((linmath_Vec3 *)result)->vector[2] = z2 - z1;

    /* If everything went fine */
    return result;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Vec3_normalize(linmath_Vec3 *self)
{
    PyObject *result = PyObject_CallObject((PyObject *)&linmath_Vec3Type, NULL);
    vec3_norm(((linmath_Vec3 *)result)->vector,
              ((linmath_Vec3 *)self)->vector);
    return result;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Vec3_cross_product(linmath_Vec3 *self,
                           PyObject     *other)
{
    vec3 *other_vec;
    if (PyTuple_Check(other))
    {
        vec3 tuple = {0.f, 0.f, 0.f};
        /* If tuple's length is lesser than 3, PyTuple_GetItem will raise
           an IndexError, so this function can safely return */
        if (!PyArg_ParseTuple(other,
                              "ff|f:cross_product",
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
        PyErr_SetString(PyExc_TypeError, UNSUPPORTED_TYPE_OTHER);
        return NULL;
    }

    /* Create result vector, calculate and then return result */
    PyObject *result = PyObject_CallObject((PyObject *)&linmath_Vec3Type, NULL);
    vec3_mul_cross(((linmath_Vec3 *)result)->vector,
                   ((linmath_Vec3 *)self)->vector,
                   *other_vec);
    return result;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Vec3_reflect(linmath_Vec3 *self,
                     PyObject     *other)
{
    vec3 *other_vec;
    if (PyTuple_Check(other))
    {
        vec3 tuple = {0.f, 0.f, 0.f};
        /* If tuple's length is lesser than 3, PyTuple_GetItem will raise
           an IndexError, so this function can safely return */
        if (!PyArg_ParseTuple(other,
                              "ff|f:reflect",
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
        PyErr_SetString(PyExc_TypeError, UNSUPPORTED_TYPE_OTHER);
        return NULL;
    }

    /* Create result vector, calculate and then return result */
    PyObject *result = PyObject_CallObject((PyObject *)&linmath_Vec3Type, NULL);
    vec3_reflect(((linmath_Vec3 *)result)->vector,
                 ((linmath_Vec3 *)self)->vector,
                 *other_vec);
    return result;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyGetSetDef linmath_Vec3_getsets[] = {
    {"length", (getter)linmath_Vec3_getlength,
               NULL,
               "Returns the length of the vector",
               NULL},
    {NULL, NULL, NULL, NULL, NULL}
};


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyMethodDef linmath_Vec3_methods[] = {
    {"from_line"     , (PyCFunction)linmath_Vec3_from_line,
                       /* BUG: Python/C API has this bug, if one wants to define
                               a static method which also accepts keyword arguments
                               one should use the:
                               `METH_VARARGS | METH_KEYWORDS | METH_STATIC`
                               ml_flags, otherwise, it will raise the following:
                               Bad call flags in PyCFunction_Call.
                               METH_OLDARGS is no longer supported! */
                       METH_VARARGS | METH_KEYWORDS | METH_STATIC,
                       "Creates a vector from a line"},
    {"normalize"    , (PyCFunction)linmath_Vec3_normalize,
                       METH_NOARGS,
                       "Return a new normalized vector"},
    {"cross_product",  (PyCFunction)linmath_Vec3_cross_product,
                       METH_O,
                       NULL}, /* TODO: Write documentation */
    {"reflect"      ,  (PyCFunction)linmath_Vec3_reflect,
                       METH_O,
                       NULL}, /* TODO: Write documentation */
    {NULL, NULL, 0, NULL}
};


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyMemberDef linmath_Vec3_members[] = {
    {"x", T_FLOAT,
          offsetof(linmath_Vec3, vector) + sizeof(float)*0,
          READONLY,
          "First value ('x') in the vector"},
    {"y", T_FLOAT,
          offsetof(linmath_Vec3, vector) + sizeof(float)*1,
          READONLY,
          "Second value ('y') in the vector"},
    {"z", T_FLOAT,
          offsetof(linmath_Vec3, vector) + sizeof(float)*2,
          READONLY,
          "Third value ('z') in the vector"},
    {NULL, 0, 0, 0, NULL}
};


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyNumberMethods linmath_Vec3_number_methods = {
    .nb_add                  = (binaryfunc)linmath_Vec3___add__,  // binaryfunc
    .nb_subtract             = (binaryfunc)linmath_Vec3___sub__,  // binaryfunc
    .nb_multiply             = (binaryfunc)linmath_Vec3___mul__,  // binaryfunc
    .nb_remainder            = 0,                                 // binaryfunc
    .nb_divmod               = 0,                                 // binaryfunc
    .nb_power                = 0,                                 // ternaryfunc
    .nb_negative             = 0,                                 // unaryfunc
    .nb_positive             = 0,                                 // unaryfunc
    .nb_absolute             = 0,                                 // unaryfunc
    .nb_bool                 = 0,                                 // inquiry
    .nb_invert               = 0,                                 // unaryfunc
    .nb_lshift               = 0,                                 // binaryfunc
    .nb_rshift               = 0,                                 // binaryfunc
    .nb_and                  = 0,                                 // binaryfunc
    .nb_xor                  = 0,                                 // binaryfunc
    .nb_or                   = 0,                                 // binaryfunc
    .nb_int                  = 0,                                 // unaryfunc
    .nb_reserved             = 0,                                 // void*
    .nb_float                = 0,                                 // unaryfunc
    .nb_inplace_add          = 0,                                 // binaryfunc
    .nb_inplace_subtract     = 0,                                 // binaryfunc
    .nb_inplace_multiply     = 0,                                 // binaryfunc
    .nb_inplace_remainder    = 0,                                 // binaryfunc
    .nb_inplace_power        = 0,                                 // ternaryfunc
    .nb_inplace_lshift       = 0,                                 // binaryfunc
    .nb_inplace_rshift       = 0,                                 // binaryfunc
    .nb_inplace_and          = 0,                                 // binaryfunc
    .nb_inplace_xor          = 0,                                 // binaryfunc
    .nb_inplace_or           = 0,                                 // binaryfunc
    .nb_floor_divide         = 0,                                 // binaryfunc
    .nb_true_divide          = 0,                                 // binaryfunc
    .nb_inplace_floor_divide = 0,                                 // binaryfunc
    .nb_inplace_true_divide  = 0,                                 // binaryfunc
    .nb_index                = 0,                                 // unaryfunc
};


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PySequenceMethods linmath_Vec3_sequence_methods = {
    .sq_length         = (lenfunc)linmath_Vec3___len__,           // lenfunc
    .sq_concat         = 0,                                       // binaryfunc
    .sq_repeat         = 0,                                       // ssizeargfunc
    .sq_item           = (ssizeargfunc)linmath_Vec3___getitem__,  // ssizeargfunc
    .sq_ass_item       = 0,                                       // ssizeobjargproc
    .sq_contains       = 0,                                       // objobjproc
    .sq_inplace_concat = 0,                                       // binaryfunc
    .sq_inplace_repeat = 0,                                       // ssizeargfunc
};



/*----------------------------------------------------------------------------*/
PyDoc_STRVAR(linmath_Vec3_doc,
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
    .tp_as_sequence    = &linmath_Vec3_sequence_methods,
    .tp_as_mapping     = 0,
    .tp_hash           = 0,
    .tp_call           = 0,
    .tp_str            = 0,
    .tp_getattro       = 0,
    .tp_setattro       = 0,
    .tp_as_buffer      = 0,
    .tp_flags          = Py_TPFLAGS_DEFAULT |
                         Py_TPFLAGS_BASETYPE, /* Can be subtyped */
    .tp_doc            = linmath_Vec3_doc,
    .tp_traverse       = 0,
    .tp_clear          = 0,
    .tp_richcompare    = 0,
    .tp_weaklistoffset = 0,
    .tp_iter           = 0,
    .tp_iternext       = 0,
    .tp_methods        = linmath_Vec3_methods,
    .tp_members        = linmath_Vec3_members,
    .tp_getset         = linmath_Vec3_getsets,
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
typedef struct
{
    PyObject_HEAD
    mat4x4 matrix;
} linmath_Mat4x4;

/* Forward declare Type */
static PyTypeObject linmath_Mat4x4Type;


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static int
linmath_Mat4x4_init(linmath_Mat4x4 *self,
                    PyObject *args,
                    PyObject *kwargs)
{
    UNUSED_PARAMETER(kwargs);

    /* Set default values */
    size_t i, j;
    for (i=0; i<4; i++)
        for (j=0; j<4; j++)
            self->matrix[i][j] = 0.f;

    /* Unpack and store arguments */
    if (!PyArg_ParseTuple(args,
                          "|(ffff)(ffff)(ffff)(ffff):__init__",
                          &self->matrix[0][0],
                          &self->matrix[0][1],
                          &self->matrix[0][2],
                          &self->matrix[0][3],
                          &self->matrix[1][0],
                          &self->matrix[1][1],
                          &self->matrix[1][2],
                          &self->matrix[1][3],
                          &self->matrix[2][0],
                          &self->matrix[2][1],
                          &self->matrix[2][2],
                          &self->matrix[2][3],
                          &self->matrix[3][0],
                          &self->matrix[3][1],
                          &self->matrix[3][2],
                          &self->matrix[3][3]))
        return PYTHON_RETURN_VALUE_FAILURE;
    /* If everything went fine */
    return PYTHON_RETURN_VALUE_SUCCESS;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static void
linmath_Mat4x4_dealloc(linmath_Mat4x4 *self)
{
    /* Free self as a python object */
    Py_TYPE(self)->tp_free((PyObject *)self);
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Mat4x4___repr__(linmath_Mat4x4 *self)
{
    /* Create buffer for each row, and the whole representation */
    char part_buffer[REPR_BUFFER_SIZE],
         repr_buffer[REPR_BUFFER_SIZE*4 + 1] = "Mat4x4(";

    /* Format the data of the matrix into a string */
    for (size_t i=0; i<4; i++)
    {
        if (i)
            strncat(repr_buffer, ", ", 2);

        snprintf(part_buffer,
                 REPR_BUFFER_SIZE,
                 "(%f, %f, %f, %f)",
                 self->matrix[i][0],
                 self->matrix[i][1],
                 self->matrix[i][2],
                 self->matrix[i][3]);

        strncat(repr_buffer,
                part_buffer,
                REPR_BUFFER_SIZE);
    }
    strncat(repr_buffer, ")", 1);
    /* Return newly cerated struing representation */
    return Py_BuildValue("s", repr_buffer);
}

/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static Py_ssize_t
linmath_Mat4x4___len__(linmath_Mat4x4 *self)
{
    UNUSED_PARAMETER(self);
    return MAT4X4_LENGTH;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Mat4x4___getitem__(linmath_Mat4x4 *self,
                           Py_ssize_t     index)
{
    if (index < MAT4X4_LENGTH)
        return Py_BuildValue("(ffff)",
                             ((linmath_Mat4x4 *)self)->matrix[index][0],
                             ((linmath_Mat4x4 *)self)->matrix[index][1],
                             ((linmath_Mat4x4 *)self)->matrix[index][2],
                             ((linmath_Mat4x4 *)self)->matrix[index][3]);
    PyErr_SetString(PyExc_IndexError, "Mat4x4 index out of range");
    return NULL;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Mat4x4___add__(linmath_Mat4x4 *self,
                       PyObject       *other)
{
    mat4x4 *other_mat;
    if (PyTuple_Check(other))
    {
        mat4x4 tuple = {{0.f, 0.f, 0.f, 0.f},
                        {0.f, 0.f, 0.f, 0.f},
                        {0.f, 0.f, 0.f, 0.f},
                        {0.f, 0.f, 0.f, 0.f}};
        /* If tuple's length is lesser than 3, PyTuple_GetItem will raise
           an IndexError, so this function can safely return */
        if (!PyArg_ParseTuple(other,
                              "|(ffff)(ffff)(ffff)(ffff):__add__",
                              &tuple[0][0],
                              &tuple[0][1],
                              &tuple[0][2],
                              &tuple[0][3],
                              &tuple[1][0],
                              &tuple[1][1],
                              &tuple[1][2],
                              &tuple[1][3],
                              &tuple[2][0],
                              &tuple[2][1],
                              &tuple[2][2],
                              &tuple[2][3],
                              &tuple[3][0],
                              &tuple[3][1],
                              &tuple[3][2],
                              &tuple[3][3]))
            return NULL;
        other_mat = &tuple;
    }
    else if (PyObject_IsInstance(other, (PyObject *)&linmath_Mat4x4Type))
        other_mat = &((linmath_Mat4x4 *)other)->matrix;
    else
    {
        PyErr_SetString(PyExc_TypeError, UNSUPPORTED_TYPE_OTHER);
        return NULL;
    }

    /* Create result vector, calculate and then return result */
    PyObject *result = PyObject_CallObject((PyObject *)&linmath_Mat4x4Type, NULL);
    mat4x4_add(((linmath_Mat4x4 *)result)->matrix,
               ((linmath_Mat4x4 *)self)->matrix,
               *other_mat);
    return result;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Mat4x4___sub__(linmath_Mat4x4 *self,
                       PyObject       *other)
{
    mat4x4 *other_mat;
    if (PyTuple_Check(other))
    {
        mat4x4 tuple = {{0.f, 0.f, 0.f, 0.f},
                        {0.f, 0.f, 0.f, 0.f},
                        {0.f, 0.f, 0.f, 0.f},
                        {0.f, 0.f, 0.f, 0.f}};
        /* If tuple's length is lesser than 3, PyTuple_GetItem will raise
           an IndexError, so this function can safely return */
        if (!PyArg_ParseTuple(other,
                              "|(ffff)(ffff)(ffff)(ffff):__sub__",
                              &tuple[0][0],
                              &tuple[0][1],
                              &tuple[0][2],
                              &tuple[0][3],
                              &tuple[1][0],
                              &tuple[1][1],
                              &tuple[1][2],
                              &tuple[1][3],
                              &tuple[2][0],
                              &tuple[2][1],
                              &tuple[2][2],
                              &tuple[2][3],
                              &tuple[3][0],
                              &tuple[3][1],
                              &tuple[3][2],
                              &tuple[3][3]))
            return NULL;
        other_mat = &tuple;
    }
    else if (PyObject_IsInstance(other, (PyObject *)&linmath_Mat4x4Type))
        other_mat = &((linmath_Mat4x4 *)other)->matrix;
    else
    {
        PyErr_SetString(PyExc_TypeError, UNSUPPORTED_TYPE_OTHER);
        return NULL;
    }

    /* Create result vector, calculate and then return result */
    PyObject *result = PyObject_CallObject((PyObject *)&linmath_Mat4x4Type, NULL);
    mat4x4_sub(((linmath_Mat4x4 *)result)->matrix,
               ((linmath_Mat4x4 *)self)->matrix,
               *other_mat);
    return result;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Mat4x4___mul__(linmath_Mat4x4 *self,
                       PyObject       *other)
{
    float scalar = 1.f;
    // vec3   *other_vec;
    mat4x4 *other_mat;
    PyObject *result;

    if (PyLong_Check(other))
    {
        scalar = (float)PyLong_AsLong(other);
        goto Scale_Matrix;
    }
    else if (PyFloat_Check(other))
    {
        scalar = (float)PyFloat_AsDouble(other);
        goto Scale_Matrix;
    }
    else if (PyTuple_Check(other))
    {
        // /* If the first argument is not a tuple */
        // if (!PyTuple_Check(PyTuple_GetItem(0)))
        // {
        //     vec3 vec_tuple = {0.f, 0.f, 0.f};
        //     if (!PyArg_ParseTuple(other,
        //                           "ff|f:__mul__",
        //                           vec_tuple + 0,
        //                           vec_tuple + 1,
        //                           vec_tuple + 2))
        //         return NULL;
        //     other_vec = &vec_tuple;
        //     goto Mul_With_Vector;
        // }

        /* If the first argument is a tuple */
        mat4x4 mat_tuple = {{0.f, 0.f, 0.f, 0.f},
                            {0.f, 0.f, 0.f, 0.f},
                            {0.f, 0.f, 0.f, 0.f},
                            {0.f, 0.f, 0.f, 0.f}};
        if (!PyArg_ParseTuple(other,
                              "|(ffff)(ffff)(ffff)(ffff):__mul__",
                              &mat_tuple[0][0],
                              &mat_tuple[0][1],
                              &mat_tuple[0][2],
                              &mat_tuple[0][3],
                              &mat_tuple[1][0],
                              &mat_tuple[1][1],
                              &mat_tuple[1][2],
                              &mat_tuple[1][3],
                              &mat_tuple[2][0],
                              &mat_tuple[2][1],
                              &mat_tuple[2][2],
                              &mat_tuple[2][3],
                              &mat_tuple[3][0],
                              &mat_tuple[3][1],
                              &mat_tuple[3][2],
                              &mat_tuple[3][3]))
            return NULL;
        other_mat = &mat_tuple;
        goto Multiply_Matrix;
    }
    // else if (PyObject_IsInstance(other, (PyObject *)&linmath_Vec3Type))
    // {
    //     other_vec = &((linmath_Vec3 *)other)->vector;
    //     goto Mul_With_Vector;
    // }
    else if (PyObject_IsInstance(other, (PyObject *)&linmath_Mat4x4Type))
    {
        other_mat = &((linmath_Mat4x4 *)other)->matrix;
        goto Multiply_Matrix;
    }
    else
    {
        PyErr_SetString(PyExc_TypeError, UNSUPPORTED_TYPE_OTHER);
        return NULL;
    }

    Multiply_Matrix:
        /* Create result vector, calculate and then return result */
        result = PyObject_CallObject((PyObject *)&linmath_Mat4x4Type, NULL);
        mat4x4_mul(((linmath_Mat4x4 *)result)->matrix,
                     ((linmath_Mat4x4 *)self)->matrix,
                     *other_mat);
        return result;
    Scale_Matrix:
        /* Create result vector, calculate and then return result */
        result = PyObject_CallObject((PyObject *)&linmath_Mat4x4Type, NULL);
        mat4x4_scale(((linmath_Mat4x4 *)result)->matrix,
                     ((linmath_Mat4x4 *)self)->matrix,
                     scalar);
        return result;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
linmath_Mat4x4_identity(linmath_Mat4x4 *self)
{
    UNUSED_PARAMETER(self);
    PyObject *result = PyObject_CallObject((PyObject *)&linmath_Mat4x4Type, NULL);
    mat4x4_identity(((linmath_Mat4x4 *)result)->matrix);
    return result;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyNumberMethods linmath_Mat4x4_number_methods = {
    .nb_add                  = (binaryfunc)linmath_Mat4x4___add__,  // binaryfunc
    .nb_subtract             = (binaryfunc)linmath_Mat4x4___sub__,  // binaryfunc
    .nb_multiply             = (binaryfunc)linmath_Mat4x4___mul__,  // binaryfunc
    .nb_remainder            = 0,                                   // binaryfunc
    .nb_divmod               = 0,                                   // binaryfunc
    .nb_power                = 0,                                   // ternaryfunc
    .nb_negative             = 0,                                   // unaryfunc
    .nb_positive             = 0,                                   // unaryfunc
    .nb_absolute             = 0,                                   // unaryfunc
    .nb_bool                 = 0,                                   // inquiry
    .nb_invert               = 0,                                   // unaryfunc
    .nb_lshift               = 0,                                   // binaryfunc
    .nb_rshift               = 0,                                   // binaryfunc
    .nb_and                  = 0,                                   // binaryfunc
    .nb_xor                  = 0,                                   // binaryfunc
    .nb_or                   = 0,                                   // binaryfunc
    .nb_int                  = 0,                                   // unaryfunc
    .nb_reserved             = 0,                                   // void*
    .nb_float                = 0,                                   // unaryfunc
    .nb_inplace_add          = 0,                                   // binaryfunc
    .nb_inplace_subtract     = 0,                                   // binaryfunc
    .nb_inplace_multiply     = 0,                                   // binaryfunc
    .nb_inplace_remainder    = 0,                                   // binaryfunc
    .nb_inplace_power        = 0,                                   // ternaryfunc
    .nb_inplace_lshift       = 0,                                   // binaryfunc
    .nb_inplace_rshift       = 0,                                   // binaryfunc
    .nb_inplace_and          = 0,                                   // binaryfunc
    .nb_inplace_xor          = 0,                                   // binaryfunc
    .nb_inplace_or           = 0,                                   // binaryfunc
    .nb_floor_divide         = 0,                                   // binaryfunc
    .nb_true_divide          = 0,                                   // binaryfunc
    .nb_inplace_floor_divide = 0,                                   // binaryfunc
    .nb_inplace_true_divide  = 0,                                   // binaryfunc
    .nb_index                = 0,                                   // unaryfunc
};


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PySequenceMethods linmath_Mat4x4_sequence_methods = {
    .sq_length         = (lenfunc)linmath_Mat4x4___len__,           // lenfunc
    .sq_concat         = 0,                                         // binaryfunc
    .sq_repeat         = 0,                                         // ssizeargfunc
    .sq_item           = (ssizeargfunc)linmath_Mat4x4___getitem__,  // ssizeargfunc
    .sq_ass_item       = 0,                                         // ssizeobjargproc
    .sq_contains       = 0,                                         // objobjproc
    .sq_inplace_concat = 0,                                         // binaryfunc
    .sq_inplace_repeat = 0,                                         // ssizeargfunc
};


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyMethodDef linmath_Mat4x4_methods[] = {
    {"identity", (PyCFunction)linmath_Mat4x4_identity,
                 METH_NOARGS | METH_STATIC,
                 "Return an Identity Matrix"},
    {NULL, NULL, 0, NULL}
};


/*----------------------------------------------------------------------------*/
PyDoc_STRVAR(linmath_Mat4x4_doc,
             "Represents a matrix of 4*4 floats");

static PyTypeObject linmath_Mat4x4Type = {
    PyObject_HEAD_INIT(NULL)
    .tp_name           = MODULE_NAME ".Mat4x4",
    .tp_basicsize      = sizeof(linmath_Mat4x4),
    .tp_itemsize       = 0,
    .tp_dealloc        = (destructor)linmath_Mat4x4_dealloc,
    .tp_print          = 0,
    .tp_getattr        = 0,
    .tp_setattr        = 0,
    .tp_reserved       = 0,
    .tp_repr           = (reprfunc)linmath_Mat4x4___repr__,
    .tp_as_number      = &linmath_Mat4x4_number_methods,
    .tp_as_sequence    = &linmath_Mat4x4_sequence_methods,
    .tp_as_mapping     = 0,
    .tp_hash           = 0,
    .tp_call           = 0,
    .tp_str            = 0,
    .tp_getattro       = 0,
    .tp_setattro       = 0,
    .tp_as_buffer      = 0,
    .tp_flags          = Py_TPFLAGS_DEFAULT |
                         Py_TPFLAGS_BASETYPE, /* Can be subtyped */
    .tp_doc            = linmath_Mat4x4_doc,
    .tp_traverse       = 0,
    .tp_clear          = 0,
    .tp_richcompare    = 0,
    .tp_weaklistoffset = 0,
    .tp_iter           = 0,
    .tp_iternext       = 0,
    .tp_methods        = linmath_Mat4x4_methods,
    .tp_members        = 0,//linmath_Mat4x4_members,
    .tp_getset         = 0,//linmath_Mat4x4_getsets,
    .tp_base           = 0,
    .tp_dict           = 0,
    .tp_descr_get      = 0,
    .tp_descr_set      = 0,
    .tp_dictoffset     = 0,
    .tp_init           = (initproc)linmath_Mat4x4_init,
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

    /* Finalise Mat4x4 class */
    if (PyType_Ready(&linmath_Mat4x4Type))
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

    /* Insert Vec3 class into module */
    Py_INCREF((PyObject *)&linmath_Mat4x4Type);
    if (!PyModule_AddObject(module,
                            "Mat4x4",
                            (PyObject *)&linmath_Mat4x4Type) < 0)
    {
        Py_XDECREF((PyObject *)&linmath_Mat4x4Type);
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
