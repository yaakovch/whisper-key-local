import os
import sys
import ctypes

if sys.platform == "win32":
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass and os.path.isdir(meipass):
        os.add_dll_directory(meipass)
        os.environ["PATH"] = meipass + ";" + os.environ.get("PATH", "")

        for dll_name in ("cublas64_12.dll", "cublasLt64_12.dll"):
            dll_path = os.path.join(meipass, dll_name)
            if os.path.isfile(dll_path):
                try:
                    ctypes.WinDLL(dll_path)
                except OSError:
                    pass
