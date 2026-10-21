#!/usr/bin/env python3
"""Diagnostic launcher for the compiled Cython extension.

A Cython extension imported as 'dump' does not execute code guarded by
if __name__ == '__main__'. Rebuild with an explicit safe entry point.
"""
import importlib.machinery
import importlib.util
from pathlib import Path
import platform
import sys
import traceback


def main():
    directory = Path(__file__).resolve().parent
    name = "dump"
    supported = importlib.machinery.EXTENSION_SUFFIXES
    extension = next(
        (directory / (name + suffix) for suffix in supported
         if (directory / (name + suffix)).is_file()),
        None,
    )
    if extension is None:
        available = [p.name for p in directory.glob("dump*.so")]
        raise RuntimeError(
            f"No compatible extension found for Python {sys.version.split()[0]} "
            f"on {platform.machine()}. Found: {available or 'none'}"
        )

    loader = importlib.machinery.ExtensionFileLoader(name, str(extension))
    spec = importlib.util.spec_from_file_location(name, extension, loader=loader)
    if spec is None:
        raise ImportError(f"Cannot load {extension.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise

    # Avoid calling arbitrary exported functions automatically.
    entry = getattr(module, "safe_main", None)
    if callable(entry):
        return entry()

    raise RuntimeError(
        f"{extension.name} imported, but has no safe_main() entry point. "
        "The original source puts its startup under "
        "if __name__ == '__main__', which is skipped during extension import. "
        "Recompile the source with an explicit safe_main() that starts "
        "the intended interactive application without background data export."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
