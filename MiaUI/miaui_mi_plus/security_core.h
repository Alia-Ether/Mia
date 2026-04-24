//╔═════════════════════════════╗                       
//║  Link: t.me/FrontendVSCode                       ║                         
//║  Author: Frontend & LED (𝙰𝚕𝚒𝚊 𝙴𝚝𝚑𝚎𝚛 𖤍) 🌷       ║    
//║  lang: C                                         ║                     
//║  [VS-HASH-01] ΞΩ77Λβ99PPHD8A71                   ║                      
//║  build:3.10.15                                   ║
//║  files: security_core.h                          ║    
//╚═════════════════════════════╝       




#ifndef VORTEXUI_SECURITY_CORE_H
#define VORTEXUI_SECURITY_CORE_H

#include <stdbool.h>
#include <Python.h> // Include Python API for wrapper function declarations

// ============================================
// HELPER UTILITIES DECLARATIONS
// ============================================

/**
 * @brief Checks if a file exists at the given path.
 * @param path The file path.
 * @return True if the file exists, false otherwise.
 */
bool file_exists(const char *path);

// ============================================
// ANTI-DEBUGGING CHECK DECLARATIONS
// ============================================

/**
 * @brief Scans procfs to detect if the current process is being debugged.
 * @return True if a debugger (TracerPid > 0) is attached, false otherwise.
 */
bool is_being_debugged();

// ============================================
// MALWARE SIGNATURE DETECTION DECLARATIONS
// ============================================

/**
 * @brief Checks for known malware signatures (simplified example).
 * @return True if suspicious files are found, false otherwise.
 */
bool detect_known_malware();

// ============================================
// PYTHON C-API WRAPPER DECLARATIONS (BRIDGES)
// ============================================

/**
 * @brief Python wrapper for is_being_debugged() function.
 */
static PyObject* is_being_debugged_py(PyObject* self, PyObject* args);

/**
 * @brief Python wrapper for detect_known_malware() function.
 */
static PyObject* detect_known_malware_py(PyObject* self, PyObject* args);


#endif // VORTEXUI_SECURITY_CORE_H
