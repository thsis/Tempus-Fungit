from src.utilities import take_photo, CONFIG, get_abs_path

if __name__ == "__main__":
    photo_path = get_abs_path("figures", CONFIG.get("GENERAL", "photo_file_name"))
    take_photo(photo_path)