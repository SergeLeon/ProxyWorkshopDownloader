import os
from pathlib import Path

mods_path = Path(os.getcwd()) / "mods"
mods_path.mkdir(parents=True, exist_ok=True)