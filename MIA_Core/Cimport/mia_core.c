
//╔═══════════════════════════════════════════════════════════════╗
//║  Project: MIA Core                                            ║
//║  Link: t.me/FrontendVSCode                                    ║
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
//║  lang: C                                                      ║
//║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
//║  build: 3.10.15                                               ║
//║  files: mia_core.c                                            ║
//╚═══════════════════════════════════════════════════════════════╝

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <Python.h>

// ============================================
// MIA FUNCTIONS IMPLEMENTATION
// ============================================

// Функция для проверки vbmeta
static int mia_verify_vbmeta_impl(const char* path) {
    FILE* fp = fopen(path, "rb");
    if (!fp) return 0;
    
    // Проверка магии MIA
    uint8_t magic[4];
    fread(magic, 1, 4, fp);
    fclose(fp);
    
    // "MIA0" магия
    return (magic[0] == 'A' && magic[1] == 'V' && 
            magic[2] == 'B' && magic[3] == '0');
}

// Функция для получения информации
static int mia_get_info_impl(const char* path, uint64_t* rollback_index) {
    FILE* fp = fopen(path, "rb");
    if (!fp) return 0;
    
    // Пропускаем магию (4 байта) + версию (8 байт) + заголовок
    fseek(fp, 64, SEEK_SET);
    
    // Читаем rollback_index (8 байт)
    fread(rollback_index, sizeof(uint64_t), 1, fp);
    
    fclose(fp);
    return 1;
}

// ============================================
// PYTHON C-API WRAPPER (ЭКСПОРТИРУЕМЫЕ ФУНКЦИИ)
// ============================================

static PyObject* py_verify_vbmeta(PyObject* self, PyObject* args) {
    const char* path;
    
    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;
    
    int result = mia_verify_vbmeta_impl(path);
    
    if (result)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static PyObject* py_get_vbmeta_info(PyObject* self, PyObject* args) {
    const char* path;
    
    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;
    
    uint64_t rollback_index = 0;
    int result = mia_get_info_impl(path, &rollback_index);
    
    if (!result) {
        Py_RETURN_NONE;
    }
    
    return Py_BuildValue("{s:K,s:i}",
                         "rollback_index", rollback_index,
                         "verified", 1);
}

static PyObject* py_verify_chain(PyObject* self, PyObject* args) {
    const char* vbmeta_path;
    const char* boot_path;
    
    if (!PyArg_ParseTuple(args, "ss", &vbmeta_path, &boot_path))
        return NULL;
    
    int vbmeta_ok = mia_verify_vbmeta_impl(vbmeta_path);
    int boot_ok = mia_verify_vbmeta_impl(boot_path);
    
    if (vbmeta_ok && boot_ok)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

// ============================================
// МЕТОДЫ МОДУЛЯ
// ============================================

static PyMethodDef AvbCoreMethods[] = {
    {"verify_vbmeta", py_verify_vbmeta, METH_VARARGS, "Проверить vbmeta подпись"},
    {"get_vbmeta_info", py_get_vbmeta_info, METH_VARARGS, "Получить информацию из vbmeta"},
    {"verify_chain", py_verify_chain, METH_VARARGS, "Проверить цепочку vbmeta -> boot"},
    {NULL, NULL, 0, NULL}
};

// ============================================
// ОПРЕДЕЛЕНИЕ МОДУЛЯ
// ============================================

static struct PyModuleDef mia_core_module = {
    PyModuleDef_HEAD_INIT,
    "mia_core_native",           // Имя модуля
    "MIA Core native module",    // Описание
    -1,
    AvbCoreMethods
};

// ============================================
// ИНИЦИАЛИЗАЦИЯ МОДУЛЯ (ГЛАВНАЯ ФУНКЦИЯ)
// ============================================

PyMODINIT_FUNC PyInit_mia_core_native(void) {
    return PyModule_Create(&mia_core_module);
}