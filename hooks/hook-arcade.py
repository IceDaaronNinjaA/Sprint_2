"""PyInstaller hook for Arcade's runtime resources."""

from importlib.util import find_spec
from pathlib import Path

from PyInstaller.utils.hooks import collect_dynamic_libs


arcade_spec = find_spec("arcade")
if arcade_spec is None or arcade_spec.origin is None:
    raise ImportError("Arcade is not installed")

arcade_dir = Path(arcade_spec.origin).parent

hiddenimports = ["arcade.gl.backends.opengl.provider", "arcade.gl.backends.opengl"]
datas = [
    (str(arcade_dir / "resources" / "system"), "arcade/resources/system"),
    (str(arcade_dir / "VERSION"), "arcade"),
]
binaries = collect_dynamic_libs("pymunk")
