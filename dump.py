#!/usr/bin/env python3
import importlib.machinery
import importlib.util
import pathlib
import sys

def main():
    root = pathlib.Path(__file__).resolve().parent

    for suffix in importlib.machinery.EXTENSION_SUFFIXES:
        module_file = root / f"dump{suffix}"

        if module_file.is_file():
            spec = importlib.util.spec_from_file_location(
                "dump", module_file
            )

            if spec is None or spec.loader is None:
                raise ImportError("Cannot load Cython module")

            module = importlib.util.module_from_spec(spec)
            sys.modules["dump"] = module
            spec.loader.exec_module(module)
            return

    raise RuntimeError(
        "Compatible dump Cython module not found. "
        f"Python: {sys.version.split()[0]}"
    )

if __name__ == "__main__":
    main()
