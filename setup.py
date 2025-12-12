import sys
from cx_Freeze import setup, Executable

# 运行指令: python setup.py build
build_exe_options = {
    "packages": [
        "os", "tkinter", "random", "re", "requests", "bs4",
        "nlc_isbn", "formatting", "pyperclip", "webbrowser",
        "bookmarkget", "ttkbootstrap"
    ],
    "excludes": ["tkinter.test", "numpy", "scipy", "pandas"],
    "include_files": ["logo.ico"]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="EbookDataGeter",
    version="1.2.0",
    description="EbookDataGeter现代版",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="logo.ico")]
)