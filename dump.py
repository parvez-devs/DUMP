import importlib.util
import sys
from pathlib import Path


def _load_dump_module():
    module_path = Path(__file__).resolve().with_name(
        "dump.cpython-314-aarch64-linux-android.so"
    )

    if not module_path.exists():
        raise FileNotFoundError(f"Missing native module: {module_path}")

    spec = importlib.util.spec_from_file_location("dump_native", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create import spec for {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules["dump_native"] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    try:
        module = _load_dump_module()
        menu = getattr(module, "menu", None)
        if menu is None:
            raise AttributeError("dump module does not expose a menu() function")
        menu()
    except Exception as exc:
        raise SystemExit(str(exc))
