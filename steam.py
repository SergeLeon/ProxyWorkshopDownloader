from pysteamcmdwrapper import SteamCMD, SteamCMDException
from contextlib import suppress
import subprocess
import os
from pathlib import Path

steam_path = Path(f"{os.getcwd()}") / "steamcmd"
steam_path.mkdir(exist_ok=True)
steam = SteamCMD(steam_path)

with suppress(SteamCMDException):
    steam.install()


def create_junction(in_path: Path, out_path: Path):
    # TODO: Add mklink analog for linux
    if in_path.exists():
        in_path.rmdir()
    Path(in_path).parents[0].mkdir(parents=True, exist_ok=True)
    subprocess.call(['mklink', "/j", in_path, out_path], shell=True)


def workshop_download(app_id, workshop_id, install_dir, validate=True):
    workshop_download_path = Path(steam.installation_path) / "steamapps" / "workshop" / "content" / str(app_id)
    create_junction(workshop_download_path, install_dir)
    steam.workshop_update(app_id=app_id, workshop_id=workshop_id,
                          install_dir=steam.installation_path,
                          validate=validate)


if __name__ == "__main__":
    mods_folder = Path(os.getcwd()) / "mods"
    mods_folder.mkdir(parents=True, exist_ok=True)
    workshop_download(app_id=294100, workshop_id=2881790485,
                      install_dir=mods_folder, validate=True)
