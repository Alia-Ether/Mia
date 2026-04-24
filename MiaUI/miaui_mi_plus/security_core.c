//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: security_core.h                          ║    
//╚═════════════════════════════╝       

#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>
#include <Python.h>

bool file_exists(const char *path) {
    FILE *fp = fopen(path, "r");
    if (fp) {
        fclose(fp);
        return true;
    }
    return false;
}

bool is_being_debugged() {
    FILE *fp;
    char line[256];
    fp = fopen("/proc/self/status", "r");
    if (fp == NULL) return false;

    while (fgets(line, sizeof(line), fp)) {
        if (strncmp(line, "TracerPid:", 10) == 0) {
            int tracer_pid = atoi(line + 10);
            fclose(fp);
            return tracer_pid > 0;
        }
    }
    fclose(fp);
    return false;
}

bool detect_known_malware() {
    if (file_exists("/data/local/tmp/xmrig") || file_exists("/system/bin/rat_daemon")) {
        return true;
    }
    return false;
}

static PyObject* is_being_debugged_py(PyObject* self, PyObject* args) {
    if (is_being_debugged()) Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

static PyObject* detect_known_malware_py(PyObject* self, PyObject* args) {
    if (detect_known_malware()) Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

static PyMethodDef SecurityMethods[] = {
    {"debug_check", is_being_debugged_py, METH_NOARGS, NULL},
    {"malware_scan", detect_known_malware_py, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef security_module = {
    PyModuleDef_HEAD_INIT,
    "miaui_mi.security_core",
    NULL,
    -1,
    SecurityMethods
};

PyMODINIT_FUNC PyInit_security_core(void) {
    return PyModule_Create(&security_module);
}

