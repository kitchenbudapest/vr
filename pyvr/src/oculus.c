/* INFO ************************************************************************
**                                                                            **
**                                  kibu-vr                                   **
**                                  =======                                   **
**                                                                            **
**        Oculus Rift + Leap Motion + Python 3 + Blender + Arch Linux         **
**                       Version: 0.1.0.270 (20150412)                        **
**                          File: pyvr/src/oculus.c                           **
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
            PyExc_Exception
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


/* Include standard library's objects */
/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
#include <stddef.h> /*
    macro : offsetof
*/

#include <stdio.h> /*
    const : stderr
    func  : printf
            fprintf
*/

#include <stdlib.h> /*
    const : NULL
            EXIT_FAILURE
            EXIT_SUCCESS
*/

#include <stdbool.h> /*
    type  : bool
    const : true
            false
*/

#include <string.h> /*
    func  : strncat
*/


/* Include Oculus' C API */
/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
#include <OVR_CAPI.h> /*
    type  : ovrHmd
            ovrTrackingState
            ovrPosef
    enum  : ovrTrackingCap_Orientation
            ovrTrackingCap_MagYawCorrection
            ovrTrackingCap_Position
    func  : ovr_Initialize
            ovr_Shutdown
            ovr_Detect
            ovrHmd_Create
            ovrHmd_Destroy
            ovrHmd_GetLastError
            ovrHmd_ConfigureTracking
            ovrHmd_GetTrackingState
*/


/* Module level constants */
/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
#define PYTHON_RETURN_VALUE_SUCCESS             0
#define PYTHON_RETURN_VALUE_FAILURE            -1
#define PYTHON_MODULE_CAN_BE_REINITIALISED      1
#define PYTHON_MODULE_CAN_NOT_BE_REINITIALISED -1
#define ERROR_BUFFER_SIZE                       1024
#define MODULE_NAME                             "oculus"


/* Module level variables */
/*----------------------------------------------------------------------------*/
/* Is LibOVR initialised? */
static bool   IS_INITIALISED   = false;
/* Number of controller instances using the insitialised LibOVR */
static size_t CONTROLLER_COUNT = 0;


/*----------------------------------------------------------------------------*/
static PyObject *oculus_InitialisationError;
static PyObject *oculus_TrackingError;


/*----------------------------------------------------------------------------*/
typedef struct
{
    PyObject_HEAD
    PyObject *position;
    PyObject *orientation;
} oculus_OculusRiftDK2Frame;


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static int
oculus_OculusRiftDK2Frame_init(oculus_OculusRiftDK2Frame *self,
                               PyObject *args,
                               PyObject *kwargs)
{
    static char *kwlist[] = {"position", "orientation", NULL};
    /* Unpack and store arguments */
    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "OO:__init__",
                                     kwlist,
                                     &self->position,
                                     &self->orientation))
        return PYTHON_RETURN_VALUE_FAILURE;

    /* Increase ref-count of the objects */
    Py_INCREF(self->position);
    Py_INCREF(self->orientation);
    return PYTHON_RETURN_VALUE_SUCCESS;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static void
oculus_OculusRiftDK2Frame_dealloc(oculus_OculusRiftDK2Frame *self)
{
    /* Decrease python object references */
    Py_XDECREF(self->position);
    Py_XDECREF(self->orientation);
    /* Free self as a python object */
    Py_TYPE(self)->tp_free((PyObject *)self);
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyMemberDef oculus_OculusRiftDK2Frame_members[] = {
    {"position"  ,  T_OBJECT,
                    offsetof(oculus_OculusRiftDK2Frame, position),
                    READONLY,
                    "Position vector (tuple of three floats: x, y, z)"},
    {"orientation", T_OBJECT,
                    offsetof(oculus_OculusRiftDK2Frame, orientation),
                    READONLY,
                    "Orientation quaternion (tuple of 4 floats: w, x, y, z)"},
    {NULL, 0, 0, 0, NULL}
};


/*----------------------------------------------------------------------------*/
PyDoc_STRVAR(ordk2frame_doc,
             "OculusRiftDK2Frame class represents all the available data and "
             "information of the device at a given time (which is the current "
             "time)");

static PyTypeObject oculus_OculusRiftDK2FrameType = {
    PyObject_HEAD_INIT(NULL)
    .tp_name           = MODULE_NAME ".OculusRiftDK2Frame",
    .tp_basicsize      = sizeof(oculus_OculusRiftDK2Frame),
    .tp_itemsize       = 0,
    .tp_dealloc        = (destructor)oculus_OculusRiftDK2Frame_dealloc,
    .tp_print          = 0,
    .tp_getattr        = 0,
    .tp_setattr        = 0,
    .tp_reserved       = 0,
    .tp_repr           = 0,
    .tp_as_number      = 0,
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
    .tp_doc            = ordk2frame_doc,
    .tp_traverse       = 0,
    .tp_clear          = 0,
    .tp_richcompare    = 0,
    .tp_weaklistoffset = 0,
    .tp_iter           = 0,
    .tp_iternext       = 0,
    .tp_methods        = 0,
    .tp_members        = oculus_OculusRiftDK2Frame_members,
    .tp_getset         = 0,
    .tp_base           = 0,
    .tp_dict           = 0,
    .tp_descr_get      = 0,
    .tp_descr_set      = 0,
    .tp_dictoffset     = 0,
    .tp_init           = (initproc)oculus_OculusRiftDK2Frame_init,
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
    ovrHmd device;
    float head_factor;
    float head_shift[3];
} oculus_OculusRiftDK2;


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static void
_oculus_raise_python_exception(ovrHmd device,
                               PyObject *exception,
                               const char *prefix,
                               const char *suffix)
{
    /* Create string buffer for error messages */
    char error_buffer[ERROR_BUFFER_SIZE];
    strncpy(error_buffer, prefix, ERROR_BUFFER_SIZE);
    strncat(error_buffer, ovrHmd_GetLastError(device), ERROR_BUFFER_SIZE);
    strncat(error_buffer, suffix, ERROR_BUFFER_SIZE);
    PyErr_SetString(exception, error_buffer);
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static int
oculus_OculusRiftDK2_init(oculus_OculusRiftDK2 *self,
                          PyObject *args,
                          PyObject *kwargs)
{
    /* If LibOVR has not been initialised yet */
    if (!IS_INITIALISED)
    {
        /* Initialise Oculus */
        if (!ovr_Initialize(0))
            goto Init_Error;
        IS_INITIALISED = true;
    }

    /* Increase instance counter, which is using the initialised LibOVR */
    ++CONTROLLER_COUNT;

    /* Check if there are any HMDs available */
    if (!ovrHmd_Detect())
        goto Init_No_Devices_Error;

    /* Check global error */
    // if (error = ovrHmd_GetLastError(NULL))
    //     fprintf(stderr, "Error (init): '%s'\n", error);


    /* TODO: make index optional !!! */

    /* Set default values */
    int device_index    = 0;
    self->head_shift[0] = 0.f;
    self->head_shift[1] = 0.f;
    self->head_shift[2] = 0.f;
    self->head_factor   = 1.f;

    /* Unpack arguments */
    static char *kwlist[] = {"device_index",
                             "head_factor",
                             "head_shift_x",
                             "head_shift_y",
                             "head_shift_z",
                             NULL};
    if (!PyArg_ParseTupleAndKeywords(args,
                                     kwargs,
                                     "|iffff:__init__",
                                     kwlist,
                                     &device_index,
                                     &self->head_factor,
                                     self->head_shift + 0,
                                     self->head_shift + 1,
                                     self->head_shift + 2))
        goto Init_Error_Python;

    /* Get the device */
    ovrHmd device = ovrHmd_Create(device_index);
    if (!device)
        goto Init_HMD_Error;

    /* Check global error */
    // if (error = ovrHmd_GetLastError(NULL))
    //     fprintf(stderr, "Error (init): '%s'\n", error);
    /* Check for device specific error */
    // if (error = ovrHmd_GetLastError(device))
    //     fprintf(stderr, "Error (init): '%s'\n", error);

    /* Configure tracking */
    ovrHmd_ConfigureTracking(device, ovrTrackingCap_Orientation |
                                     ovrTrackingCap_MagYawCorrection |
                                     ovrTrackingCap_Position, 0);

    /* Check global error */
    // if (error = ovrHmd_GetLastError(NULL))
    //     fprintf(stderr, "Error (init): '%s'\n", error);
    /* Check for device specific error */
    // if (error = ovrHmd_GetLastError(device))
    //     fprintf(stderr, "Error (init): '%s'\n", error);

    /* If everything went fine */
    self->device = device;
    return PYTHON_RETURN_VALUE_SUCCESS;

    /* If there was a problem */
    Init_HMD_Error:
        _oculus_raise_python_exception(device,
                                       oculus_InitialisationError,
                                       "Cannot initialise Oculus device",
                                       NULL);
    Init_No_Devices_Error:
        _oculus_raise_python_exception(NULL,
                                       oculus_InitialisationError,
                                       "Cannot initialise Oculus device (No device found)",
                                       NULL);
    Init_Error:
        _oculus_raise_python_exception(NULL,
                                       oculus_InitialisationError,
                                       "Cannot initialise Oculus SDK: '",
                                       "'\n(HINT: Is oculusd/ovrd running?)");
    Init_Error_Python:
        self->device = NULL;
        return PYTHON_RETURN_VALUE_FAILURE;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static void
oculus_OculusRiftDK2_dealloc(oculus_OculusRiftDK2 *self)
{
    /* Close oculus session */
    if (self->device)
        ovrHmd_Destroy(self->device);

    /* If this instance was the last one, which used the initialised LibOVR */
    if (!--CONTROLLER_COUNT)
    {
        IS_INITIALISED = false;
        ovr_Shutdown();
    }

    /* Free self as a python object */
    Py_TYPE(self)->tp_free((PyObject *)self);
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyObject *
oculus_OculusRiftDK2_frame(oculus_OculusRiftDK2 *self)
{
    if (!self->device)
    {
        PyErr_SetString(oculus_TrackingError, "No device found");
        return NULL;
    }

    /* Check if there is an error stored in the HMD */
    // const char *error = ovrHmd_GetLastError(self->device);
    // if (error)
    //     fprintf(stderr, "Error (frame): '%s'\n", error);

    /* Get the most current (0.0) tracking state of the HMD */
    ovrTrackingState state = ovrHmd_GetTrackingState(self->device, 0.0);
    ovrPosef head   = state.HeadPose.ThePose;
    // ovrPosef camera = state.CameraPose;

    /* Create python tuples and fill them with values and place them into
       another tuple, which will be the argument for the frame-object */
    PyObject *position    = Py_BuildValue("(fff)",
                                          head.Position.x*self->head_factor + self->head_shift[0],
                                          head.Position.y*self->head_factor + self->head_shift[1],
                                          head.Position.z*self->head_factor + self->head_shift[2]),
             *orientation = Py_BuildValue("(ffff)", head.Orientation.w,
                                                    head.Orientation.x,
                                                    head.Orientation.y,
                                                    head.Orientation.z),
             *args = Py_BuildValue("(OO)", position, orientation);

    /* Create a new frame-object and pass the previously constructed argument tuple */
    PyObject *frame = PyObject_CallObject((PyObject *)&oculus_OculusRiftDK2FrameType, args);

    /* Clean up */
    Py_XDECREF(args);
    Py_XDECREF(position);
    Py_XDECREF(orientation);

    /* Return the new frame-object */
    return frame;
}


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
static PyMethodDef oculus_OculusRiftDK2_methods[] = {
    {"frame", (PyCFunction)oculus_OculusRiftDK2_frame,
              METH_NOARGS,
              "Returns a new OculusRiftDK2Frame object"},
    {NULL, NULL, 0, NULL}
};


/*----------------------------------------------------------------------------*/
PyDoc_STRVAR(ordk2_doc,
             "OculusRiftDK2 class represents the controller of an Oculus device "
             "connected to the computer, represented by the given index");

static PyTypeObject oculus_OculusRiftDK2Type = {
    PyObject_HEAD_INIT(NULL)
    .tp_name           = MODULE_NAME ".OculusRiftDK2",
    .tp_basicsize      = sizeof(oculus_OculusRiftDK2),
    .tp_itemsize       = 0,
    .tp_dealloc        = (destructor)oculus_OculusRiftDK2_dealloc,
    .tp_print          = 0,
    .tp_getattr        = 0,
    .tp_setattr        = 0,
    .tp_reserved       = 0,
    .tp_repr           = 0,
    .tp_as_number      = 0,
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
    .tp_doc            = ordk2_doc,
    .tp_traverse       = 0,
    .tp_clear          = 0,
    .tp_richcompare    = 0,
    .tp_weaklistoffset = 0,
    .tp_iter           = 0,
    .tp_iternext       = 0,
    .tp_methods        = oculus_OculusRiftDK2_methods,
    .tp_members        = 0,
    .tp_getset         = 0,
    .tp_base           = 0,
    .tp_dict           = 0,
    .tp_descr_get      = 0,
    .tp_descr_set      = 0,
    .tp_dictoffset     = 0,
    .tp_init           = (initproc)oculus_OculusRiftDK2_init,
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
PyDoc_STRVAR(oculus_module_doc,
             "oculus module contains convenient classes to interact with the "
             "OculusRift DK2 device");

static struct PyModuleDef oculus_module = {
    PyModuleDef_HEAD_INIT,
    .m_name     = MODULE_NAME,
    .m_doc      = oculus_module_doc,
    .m_size     = PYTHON_MODULE_CAN_BE_REINITIALISED,
    .m_methods  = NULL,
    .m_reload   = NULL,
    .m_traverse = NULL,
    .m_clear    = NULL,
    .m_free     = NULL,
};


/*- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - */
PyMODINIT_FUNC
PyInit_oculus(void)
{
    /* Create module */
    PyObject *module = PyModule_Create(&oculus_module);
    if (!module)
        goto Module_Init_Error;

    /* Create and add errors to module */
    oculus_InitialisationError = PyErr_NewException(MODULE_NAME ".InitialisationError",
                                                    NULL,
                                                    NULL);
    PyModule_AddObject(module, "InitialisationError", oculus_InitialisationError);

    oculus_TrackingError = PyErr_NewException(MODULE_NAME ".TrackingError",
                                                    NULL,
                                                    NULL);
    PyModule_AddObject(module, "TrackingError", oculus_TrackingError);

    /* Finalize frame-class */
    if (PyType_Ready(&oculus_OculusRiftDK2FrameType))
        goto Module_Make_Object_Ready_Error;

    /* Finalize controller-object */
    if (PyType_Ready(&oculus_OculusRiftDK2Type))
        goto Module_Make_Object_Ready_Error;

    /* Insert frame-class into module */
    Py_INCREF((PyObject *)&oculus_OculusRiftDK2FrameType);
    if (PyModule_AddObject(module,
                           "OculusRiftDK2Frame",
                           (PyObject *)&oculus_OculusRiftDK2FrameType) < 0)
    {
        Py_XDECREF((PyObject *)&oculus_OculusRiftDK2FrameType);
        goto Module_Add_Object_Error;
    }

    /* Insert controller-class into module */
    Py_INCREF((PyObject *)&oculus_OculusRiftDK2Type);
    if (PyModule_AddObject(module,
                           "OculusRiftDK2",
                           (PyObject *)&oculus_OculusRiftDK2Type) < 0)
    {
        Py_XDECREF((PyObject *)&oculus_OculusRiftDK2Type);
        goto Module_Add_Object_Error;
    }


    /* If everything went fine */
    return module;

    /* IF there was a problem */
    Module_Add_Object_Error:
    Module_Make_Object_Ready_Error:
        Py_XDECREF(module);
    Module_Init_Error:
        return NULL;
}
