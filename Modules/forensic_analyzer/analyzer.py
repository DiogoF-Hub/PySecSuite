from exiftool import ExifTool
from datetime import datetime
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
upload_dir = os.path.join(root_dir, "Uploads")


def check_exiftool_installed():
    try:
        with ExifTool() as et:
            return True
    except Exception as e:
        print(f"ExifTool is not installed or not found: {e}")
        return False


def compare_time_difference(time_difference: float):
    print(f"\nTime Difference: {time_difference} seconds")

    if time_difference < 0:
        print(
            "File modification time is earlier than creation time. No issue detected."
        )
    elif time_difference <= 120:
        print("Minor difference (likely due to file transfer or system copy).")
    else:
        print(
            "Warning: File was modified AFTER it was originally created (possible tampering)."
        )


def extract_all_metadata(file_path: str, file_name: str):
    try:
        with ExifTool() as et:
            # Step 1: Run ExifTool and get metadata list (usually 1 item)
            metadata_list = et.execute_json("-j", file_path)

            # Step 2: Check if list is not empty
            if metadata_list and isinstance(metadata_list, list):
                metadata = metadata_list[0]  # First file's metadata
            else:
                metadata = {}  # Fallback if something went wrong

            print(f"\nMetadata for: {file_name}\n")
            for tag, value in metadata.items():
                print(f"{tag}: {value}")
    except Exception as e:
        print(f"Failed to extract metadata: {e}")


def extract_metadata_all_timestamp(file_path: str, file_name: str):
    try:
        with ExifTool() as et:
            # Step 1: Run ExifTool and get metadata list (usually 1 item)
            metadata_list = et.execute_json("-j", file_path)

            # Step 2: Check if list is not empty
            if metadata_list and isinstance(metadata_list, list):
                metadata = metadata_list[0]  # First file's metadata
            else:
                metadata = {}  # Fallback if something went wrong

            # Filter and print timestamp-related tags
            timestamp_keywords = ["date", "time"]
            found_any = False
            print(f"\nTimestamps for: {file_name}\n")

            for tag, value in metadata.items():
                if any(keyword in tag.lower() for keyword in timestamp_keywords):
                    print(f"{tag}: {value}")
                    found_any = True

            if not found_any:
                print(f"No timestamp-related metadata found in {file_name}.")

    except Exception as e:
        print(f"Failed to extract timestamp: {e}")


def analyze_image_metadata(file_path: str, file_name: str):
    try:
        with ExifTool() as et:
            metadata_list = et.execute_json("-j", file_path)
            metadata = metadata_list[0] if metadata_list else {}

            file_modify_raw = metadata.get("File:FileModifyDate")
            exif_original_raw = metadata.get("EXIF:DateTimeOriginal")

            print(f"\nFile: {file_name}")
            print(f"File Modify Date      : {file_modify_raw}")
            print(f"EXIF DateTime Original: {exif_original_raw}")

            if file_modify_raw and exif_original_raw:
                # Remove time zone (+01:00) if present in FileModifyDate
                file_modify_clean = file_modify_raw.split("+")[0].strip()
                exif_original_clean = exif_original_raw.strip()

                # Convert to datetime objects
                file_modify_dt = datetime.strptime(
                    file_modify_clean, "%Y:%m:%d %H:%M:%S"
                )
                exif_original_dt = datetime.strptime(
                    exif_original_clean, "%Y:%m:%d %H:%M:%S"
                )

                # Compare timestamps
                time_difference = (file_modify_dt - exif_original_dt).total_seconds()

                compare_time_difference(time_difference)
            else:
                print("Not enough timestamp information to perform consistency check.")

    except Exception as e:
        print(f"Failed to check timestamps: {e}")


def analyze_pdf_metadata(file_path: str, file_name: str):
    # todo: Implement PDF metadata extraction and timestamp check
    return


def analyze_docx_metadata(file_path: str, file_name: str):
    # todo: Implement DOCX metadata extraction and timestamp check
    return


def analyze_file(file_name: str):
    file_path = os.path.join(upload_dir, file_name)

    if not check_exiftool_installed():
        print("ExifTool is not installed.")
        return

    if not os.path.isfile(file_path):
        return False

    file_ext = os.path.splitext(file_path)[1].lower()  # e.g. ".jpg"

    if file_ext in [".jpg", ".jpeg", ".png"]:
        # Call your image metadata + timestamp check
        analyze_image_metadata(file_path, file_name)

    elif file_ext == ".pdf":
        # Run PDF-specific analysis
        analyze_pdf_metadata(file_path, file_name)

    elif file_ext == ".docx":
        # Run DOCX-specific analysis
        analyze_docx_metadata(file_path, file_name)

    else:
        print(f"Unsupported file type: {file_ext}")
