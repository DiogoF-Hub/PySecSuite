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
    try:
        with ExifTool() as et:
            metadata_list = et.execute_json("-j", file_path)
            metadata = metadata_list[0] if metadata_list else {}

            # Get relevant timestamps
            pdf_create = metadata.get("PDF:CreateDate")
            pdf_modify = metadata.get("PDF:ModifyDate")

            print(f"\nAnalyzing PDF: {file_name}")
            print(f"PDF Creation Date     : {pdf_create}")
            print(f"PDF Last Modified Date: {pdf_modify}")

            if pdf_create and pdf_modify:
                # Clean date strings (remove timezone, just like in images)
                create_clean = pdf_create.split("+")[0].strip()
                modify_clean = pdf_modify.split("+")[0].strip()

                # Convert to datetime objects
                create_dt = datetime.strptime(create_clean, "%Y:%m:%d %H:%M:%S")
                modify_dt = datetime.strptime(modify_clean, "%Y:%m:%d %H:%M:%S")

                # Compare
                time_difference = (modify_dt - create_dt).total_seconds()
                compare_time_difference(time_difference)

            else:
                print("Not enough timestamp information to perform consistency check.")

    except Exception as e:
        print(f"Failed to analyze PDF metadata: {e}")


def analyze_docx_metadata(file_path: str, file_name: str):
    try:
        with ExifTool() as et:
            metadata_list = et.execute_json("-j", file_path)
            metadata = metadata_list[0] if metadata_list else {}

            # Try to get creation and modification dates
            create_raw = metadata.get("Document:CreateDate")
            modify_raw = metadata.get("Document:ModifyDate")

            print(f"\nAnalyzing DOCX: {file_name}")
            print(f"Create Date : {create_raw}")
            print(f"Modify Date : {modify_raw}")

            if create_raw and modify_raw:
                # Clean the strings (no timezone expected but be safe)
                create_clean = create_raw.split("+")[0].strip()
                modify_clean = modify_raw.split("+")[0].strip()

                # Convert to datetime objects
                create_dt = datetime.strptime(create_clean, "%Y:%m:%d %H:%M:%S")
                modify_dt = datetime.strptime(modify_clean, "%Y:%m:%d %H:%M:%S")

                time_difference = (modify_dt - create_dt).total_seconds()
                compare_time_difference(time_difference)
            else:
                print("Not enough timestamp information to perform consistency check.")

    except Exception as e:
        print(f"Failed to analyze DOCX metadata: {e}")


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
