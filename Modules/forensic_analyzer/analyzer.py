from exiftool import ExifTool
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
upload_dir = os.path.join(root_dir, "Uploads")

if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)


def check_exiftool_installed():
    try:
        with ExifTool() as et:
            return True
    except Exception as e:
        print(f"ExifTool is not installed or not found: {e}")
        return False


def check_file_exists(file_path: str):
    if not os.path.isfile(file_path):
        return False
    else:
        return True


def extract_metadata(file_name: str):
    file_path = os.path.join(upload_dir, file_name)

    if not check_exiftool_installed():
        print("ExifTool is not installed. Please install it to use this feature.")
        return

    if not check_file_exists(file_path):
        print(f"File does not exist: {file_path}")
        return

    try:
        with ExifTool() as et:
            metadata_list = et.execute_json("-j", file_path)
            metadata = metadata_list[0] if metadata_list else {}

            print(f"\nMetadata for: {file_path}\n")
            for tag, value in metadata.items():
                print(f"{tag}: {value}")
    except Exception as e:
        print(f"Failed to extract metadata: {e}")
