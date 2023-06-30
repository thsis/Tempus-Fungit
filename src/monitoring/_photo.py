import subprocess
from src.utilities import CONFIG, get_abs_path


def take_photo(photo_name):
    cmd = f"libcamera-jpeg -o {photo_name} -v 0"
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    photo_path = get_abs_path("figures", CONFIG.get("GENERAL", "photo_file_name"))
    take_photo(photo_path)
