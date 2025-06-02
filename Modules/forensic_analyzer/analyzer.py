from exiftool import ExifTool
from datetime import datetime
import zipfile
import os
import filetype

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
upload_dir = os.path.join(root_dir, "Uploads")


def check_exiftool_installed():
    try:
        with ExifTool() as et:
            return True
    except Exception as e:
        print(f"ExifTool is not installed or not found: {e}")
        return False


def validate_file_extension(file_path: str):
    kind = filetype.guess(file_path)
    declared_ext = os.path.splitext(file_path)[1].lower()

    if not kind:
        print("Could not determine actual file type (possibly unknown or corrupted).")
        return True  # Proceed with analysis anyway

    actual_ext = f".{kind.extension}"

    print(f"Declared extension: {declared_ext}")
    print(f"Actual file type  : {actual_ext} ({kind.mime})")

    if actual_ext != declared_ext:
        print("WARNING: File extension does not match actual file type!")
        return False  # Skip analysis if extensions do not match

    return True


def compare_time_difference(time_difference: float):
    # Convert seconds into hours, minutes, and seconds
    minutes = int(time_difference // 60)
    hours = int(minutes // 60)
    seconds = int(time_difference % 60)

    # Format as human-readable string
    if hours > 0:
        print(f"\nTime Difference: {hours}h {minutes % 60}m {seconds}s")
    elif minutes > 0:
        print(f"\nTime Difference: {minutes}m {seconds}s")
    else:
        print(f"\nTime Difference: {int(time_difference)} seconds")

    if time_difference < 0:
        print(
            "\nFile modification time is earlier than creation time. No issue detected."
        )
    elif 0 < time_difference <= 120:
        print(
            f"\nMinor difference ({int(time_difference)}s). Likely due to file transfer or system copy."
        )

    elif time_difference == 0:
        print("\nTimestamps are exactly the same. No difference.")
    else:
        print(
            "\nWarning: File was modified AFTER it was originally created (possible tampering)."
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
    print(f"\nAnalyzing PDF: {file_name}")

    try:
        with ExifTool() as et:
            metadata_list = et.execute_json("-j", file_path)
            metadata = metadata_list[0] if metadata_list else {}

            # ---------- Timestamp Check ----------
            pdf_create = metadata.get("PDF:CreateDate")
            pdf_modify = metadata.get("PDF:ModifyDate")

            print(f"PDF Creation Date     : {pdf_create}")
            print(f"PDF Last Modified Date: {pdf_modify}")

            if pdf_create and pdf_modify:
                create_clean = pdf_create.split("+")[0].strip()
                modify_clean = pdf_modify.split("+")[0].strip()

                create_dt = datetime.strptime(create_clean, "%Y:%m:%d %H:%M:%S")
                modify_dt = datetime.strptime(modify_clean, "%Y:%m:%d %H:%M:%S")

                time_difference = (modify_dt - create_dt).total_seconds()
                compare_time_difference(time_difference)
            else:
                print("Not enough timestamp information to perform consistency check.")

            # ---------- Embedded Object Check ----------
            has_javascript = metadata.get("PDF:JavaScript", "").lower() == "yes"
            has_embedded_files = (
                metadata.get("PDF:HasEmbeddedFiles", "").lower() == "yes"
            )
            has_xfa = metadata.get("PDF:HasXFA", "").lower() == "yes"

            if has_javascript:
                print("JavaScript detected in the PDF.")
            else:
                print("No JavaScript detected in the PDF.")

            if has_embedded_files:
                print("Embedded files detected in the PDF.")
            else:
                print("No embedded files detected in the PDF.")

            if has_xfa:
                print("Interactive XFA forms detected in the PDF.")
            else:
                print("No interactive XFA forms detected in the PDF.")

        # ---------- Suspicious Pattern Check ----------
        suspicious_keywords = [
            "powershell",
            "cmd",
            "base64",
            "http://",
            "https://",
            "ftp://",
            "curl",
            "wget",
        ]
        try:
            with open(file_path, "rb") as f:
                content = f.read().decode(errors="ignore").lower()

            hits = [kw for kw in suspicious_keywords if kw in content]

            if hits:
                print("\nSuspicious patterns detected in raw PDF content:")
                for kw in hits:
                    print(f" - Keyword '{kw}' found")
            else:
                print("\nNo suspicious patterns found in raw content.")

        except Exception as e:
            print(f"Error scanning PDF for patterns: {e}")

    except Exception as e:
        print(f"Failed to analyze PDF metadata: {e}")


def analyze_docx_metadata(file_path: str, file_name: str):
    print(f"\nAnalyzing DOCX file: {file_name}")

    # --------- Metadata Check (using ExifTool) ---------
    try:
        with ExifTool() as et:
            metadata_list = et.execute_json("-j", file_path)
            metadata = metadata_list[0] if metadata_list else {}

            create_raw = metadata.get("Document:CreateDate") or metadata.get(
                "File:FileCreateDate"
            )
            modify_raw = metadata.get("Document:ModifyDate") or metadata.get(
                "File:FileModifyDate"
            )

            print(f"Create Date : {create_raw}")
            print(f"Modify Date : {modify_raw}")

            if create_raw and modify_raw:
                create_clean = create_raw.split("+")[0].strip()
                modify_clean = modify_raw.split("+")[0].strip()

                create_dt = datetime.strptime(create_clean, "%Y:%m:%d %H:%M:%S")
                modify_dt = datetime.strptime(modify_clean, "%Y:%m:%d %H:%M:%S")

                time_difference = (modify_dt - create_dt).total_seconds()
                compare_time_difference(time_difference)
            else:
                print("Not enough timestamp information to perform consistency check.")

    except Exception as e:
        print(f"Failed to extract metadata: {e}")

    # --------- Macro, Embedded Object, and Suspicious Pattern Check ---------
    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            file_list = zip_ref.namelist()

            has_macros = False
            embedded_objects = []
            suspicious_keywords = [
                "powershell",
                "cmd",
                "base64",
                "http://",
                "https://",
                "ftp://",
                "curl",
                "wget",
            ]
            suspicious_hits = []

            for inner_file in file_list:
                lower_name = inner_file.lower()

                if "vbaproject.bin" in lower_name:
                    has_macros = True

                if "embeddings/" in lower_name:
                    embedded_objects.append(inner_file)

                # Suspicious pattern detection inside files
                try:
                    with zip_ref.open(inner_file) as f:
                        content = f.read().decode(errors="ignore").lower()
                        for keyword in suspicious_keywords:
                            if keyword in content:
                                suspicious_hits.append((inner_file, keyword))
                except:
                    continue  # skip unreadable files

            # Print macro detection
            if has_macros:
                print("Macros detected in the document.")
            else:
                print("No macros detected in the document.")

            # Print embedded objects
            if embedded_objects:
                print("Embedded objects found:")
                for item in embedded_objects:
                    print(f" - {item}")
            else:
                print("No embedded objects found.")

            # Print suspicious keywords
            if suspicious_hits:
                print("\nSuspicious patterns detected:")
                for fname, keyword in suspicious_hits:
                    print(f" - Keyword '{keyword}' found in {fname}")
            else:
                print("\nNo suspicious patterns found.")

    except Exception as e:
        print(f"Failed to analyze DOCX for embedded content: {e}")


def analyze_file(file_name: str):
    file_path = os.path.join(upload_dir, file_name)

    if not check_exiftool_installed():
        print("ExifTool is not installed.")
        return False

    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return False

    if not validate_file_extension(file_path):
        print("Analysis skipped due to mismatched file type.")
        return False

    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext in [".jpg", ".jpeg", ".png"]:
        analyze_image_metadata(file_path, file_name)

    elif file_ext == ".pdf":
        analyze_pdf_metadata(file_path, file_name)

    elif file_ext in [".docx", ".docm"]:
        analyze_docx_metadata(file_path, file_name)

    else:
        print(f"Unsupported file type: {file_ext}")
