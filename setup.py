import sys
from cx_Freeze import setup, Executable

# 运行指令: python setup.py build
build_exe_options = {
    "packages": [
        "os", "tkinter", "random", "re", "urllib.request", "bs4",
        "nlc_isbn", "formatting", "pyperclip", "webbrowser"
    ],
    "excludes": ["tkinter.test", "numpy", "scipy", "pandas"],
    "include_files": ["logo.ico"]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="EbookDataGeter",
    version="1.0.2",
    description="EbookDataGeter自由开源",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="logo.ico")]
)
