//╔═══════════════════════════════════════════════════════════════╗
//║  Project: MIA Core                                            ║
//║  Link: t.me/FrontendVSCode                                    ║
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷                  ║
//║  lang: C                                                      ║
//║  [MIA-HASH-01] ΞΩ77Λβ99PPHD8A71                               ║
//║  build: 3.10.15                                               ║
//║  files: mia_core.h, mia_core.c                                ║
//╚═══════════════════════════════════════════════════════════════╝

#ifndef MIA_CORE_H
#define MIA_CORE_H

#include <stdbool.h>
#include <stdint.h>
#include <Python.h>

// ============================================
// MIA STRUCTURES (из libmia)
// ============================================

typedef struct {
    uint64_t rollback_index;
    uint32_t flags;
    uint32_t rollback_index_location;
} AvbVBMetaHeader;

// ============================================
// MIA FUNCTIONS DECLARATIONS
// ============================================

/**
 * @brief Проверить vbmeta образ
 * @param path Путь к vbmeta файлу
 * @return 1 если подпись верна, 0 если нет
 */
int mia_verify_vbmeta(const char* path);

/**
 * @brief Получить информацию из vbmeta
 * @param path Путь к файлу
 * @param header Указатель на структуру для заполнения
 * @return 1 если успешно, 0 если ошибка
 */
int mia_get_vbmeta_info(const char* path, AvbVBMetaHeader* header);

/**
 * @brief Проверить цепочку доверия MIA
 * @param vbmeta_path Путь к vbmeta
 * @param boot_path Путь к boot.img
 * @return 1 если верификация пройдена
 */
int mia_verify_chain(const char* vbmeta_path, const char* boot_path);

// ============================================
// PYTHON C-API WRAPPER DECLARATIONS
// ============================================

static PyObject* py_mia_verify_vbmeta(PyObject* self, PyObject* args);
static PyObject* py_mia_get_vbmeta_info(PyObject* self, PyObject* args);
static PyObject* py_mia_verify_chain(PyObject* self, PyObject* args);

#endif // MIA_CORE_H