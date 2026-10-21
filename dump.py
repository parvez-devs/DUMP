#!/usr/bin/env python3
"""Launch the compiled Cython dump extension from this directory."""
import importlib.machinery
import importlib.util
import pathlib
import platform
import sys
import traceback


def main():
    root = pathlib.Path(__file__).resolve().parent
    name = "dump"
    candidates = [
        root / (name + suffix)
        for suffix in importlib.machinery.EXTENSION_SUFFIXES
    ]
    extension = next((path for path in candidates if path.is_file()), None)
    if extension is None:
        available = ", ".join(p.name for p in root.glob("dump*.so")) or "none"
        raise RuntimeError(
            f"No compatible Cython extension found. Python={sys.version.split()[0]}, "
            f"architecture={platform.machine()}, available={available}. "
            "Install the Python/architecture version used to build the extension."
        )

    loader = importlib.machinery.ExtensionFileLoader(name, str(extension))
    spec = importlib.util.spec_from_file_location(name, extension, loader=loader)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {extension.name}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise

    # Cython modules execute their top-level statements during initialization.
    # Call an explicit entry point only when the module exports one.
    for entry in ("main", "run"):
        function = getattr(module, entry, None)
        if callable(function):
            return function()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
