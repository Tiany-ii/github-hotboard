# -*- coding: utf-8 -*-
"""
Build GitHub Hotboard.exe
--------------------------
Usage:  double-click build.bat, or run `python build.py`

Outputs dist/GitHub Hotboard.exe (single file, no Python needed on the target machine).

Note for maintainers: the WebView2 .NET assemblies MUST land in the root of the
PyInstaller archive. If they end up in a subfolder the window shows a blank page.
"""
import os
import sys
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

EXE_NAME = "GitHub Hotboard"


def fail(msg):
    print("[error] " + msg)
    return 1


def main():
    if not os.path.isfile("github-hot.html"):
        return fail("github-hot.html not found next to build.py")
    if not os.path.isfile("app.py"):
        return fail("app.py not found next to build.py")

    try:
        import webview
    except ImportError:
        return fail("pywebview is missing. Run: python -m pip install -r requirements.txt")
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        return fail("pyinstaller is missing. Run: python -m pip install -r requirements.txt")

    lib = os.path.join(os.path.dirname(os.path.abspath(webview.__file__)), "lib")
    if not os.path.isdir(lib):
        return fail("cannot find pywebview lib directory: %s" % lib)

    args = [sys.executable, "-m", "PyInstaller",
            "--noconfirm", "--clean", "--onefile", "--windowed",
            "--name", EXE_NAME,
            "--add-data", "github-hot.html" + os.pathsep + ".",
            "--collect-all", "webview",
            "--collect-all", "pythonnet",
            "--collect-all", "clr_loader"]

    if os.path.isfile("app.ico"):
        args += ["--icon", "app.ico"]

    # WebView2 .NET assemblies must sit at the archive root
    for name in ("Microsoft.Web.WebView2.Core.dll",
                 "Microsoft.Web.WebView2.WinForms.dll",
                 "WebBrowserInterop.x64.dll"):
        src = os.path.join(lib, name)
        if os.path.isfile(src):
            args += ["--add-binary", src + os.pathsep + "."]

    # WebView2Loader.dll is per-architecture
    for arch in ("win-x64", "win-x86", "win-arm64"):
        src = os.path.join(lib, "runtimes", arch, "native", "WebView2Loader.dll")
        if os.path.isfile(src):
            args += ["--add-binary", src + os.pathsep + arch]

    args.append("app.py")

    print("[build] starting, about 40 seconds ...")
    if subprocess.call(args) != 0:
        return fail("PyInstaller exited with a non-zero code")

    exe = os.path.join(HERE, "dist", EXE_NAME + ".exe")
    if not os.path.isfile(exe):
        return fail("expected artifact not found: %s" % exe)
    print("[done] %s  (%.1f MB)" % (exe, os.path.getsize(exe) / 1024 / 1024))

    # Keep dist/ (that is the artifact) but drop the intermediates
    for junk in ("build", EXE_NAME + ".spec"):
        path = os.path.join(HERE, junk)
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        elif os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
    print("[clean] removed build/ and %s.spec" % EXE_NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main())
