from setuptools import setup, Extension, find_packages
import sysconfig
import platform
import os

python_inc = sysconfig.get_paths()["include"]
extra_args = ["-O3", "-Wall", "-fPIC"]
if platform.system().lower() == "linux":
    extra_args.append("-D_MIA_LINUX")
if "ANDROID_ROOT" in os.environ:
    extra_args.append("-D_MIA_ANDROID")

extensions = [
    Extension(
        name="miaui_mi.core",
        sources=["MiaUI/miaui_mi_plus/system_info.c"],
        include_dirs=[python_inc],
        extra_compile_args=extra_args,
    ),
    Extension(
        name="miaui_mi.security_core",
        sources=["MiaUI/miaui_mi_plus/security_core.c"],
        include_dirs=[python_inc],
        extra_compile_args=extra_args,
    ),
    Extension(
        name="mia_core_native",
        sources=["MIA_Core/Cimport/mia_core.c"],
        include_dirs=[python_inc],
        extra_compile_args=extra_args,
    ),
]

all_install_requires = []

setup(
    name="Mia",
    version="3.10.15",
    author="Alia Ether 𖤍",
    author_email="alia.vscode@gmail.com",
    description="EUL Unified Intelligence Engine & Development Toolkit for Android/Linux",
    long_description="""
EUL Unified Intelligence Engine & Development Toolkit for Android/Linux.
Integrates MiaUI core with MIA_Core low-level firmware tools.

Единая экосистема EUL системного интеллекта и инструментов разработки для Android/Linux.
Объединяет движок MiaUI и низкоуровневые инструменты MIA_Core.
    """,
    long_description_content_type="text/markdown",
    url="https://github.com/Alia-Ether/Mia",
    license="ETHERIUM USAGE LICENSE (EUL)",

    package_dir={
        "": "MiaUI",
        "MIA_Core": "MIA_Core",
        "bash": "bash",
    },
    packages=(
        find_packages(where="MiaUI", include=["miaui_mi", "miaui_mi.*", "miaui_mi_pro", "miaui_mi_plus", "games", "games.*", "report"]) +
        ["MIA_Core"] + [f"MIA_Core.{pkg}" for pkg in find_packages(where="MIA_Core", include=["bridge", "bridge.*", "plugin", "plugin.*", "Cimport", "Cpython", "Cpython.*"])] +
        ["bash"]
    ),

    install_requires=all_install_requires,

    entry_points={
        "console_scripts": [
            "mia=miaui_mi.cli:main",
            "mia-core=MIA_Core.Cpython.main:main",
            # mia-term убран — не нужен
        ],
    },

    ext_modules=extensions,
    include_package_data=True,
    
    package_data={
        "miaui_mi.security.pypass": [
            "Makefile",
            "src/**/*",
            "include/**/*",
            "src/*.c",
            "include/*.h",
            "*.txt",
            "*.json",
        ],
        "miaui_mi": [
            "help/*.txt",
            "help/*.json",
        ],
        "miaui_mi_pro": [
            "*.txt",
        ],
        "games": [
            "telegram/*.py",
            "data/*.py",
        ],
        "MIA_Core": [
            "plugin/**/*.py",
        ],
 },    
    zip_safe=False,
    python_requires=">=3.8",
)
