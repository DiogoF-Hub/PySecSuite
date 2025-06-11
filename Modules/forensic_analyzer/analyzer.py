from exiftool import ExifTool
from datetime import datetime
import zipfile
import os
import filetype

# Define root and upload directories
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
upload_dir = os.path.join(root_dir, "Uploads")


# Check if ExifTool is installed and functional
def check_exiftool_installed():
    try:
        with ExifTool() as et:
            return True
    except Exception:
        return False


# Validate file extension by checking the actual file type
def validate_file_extension(file_path: str):
    kind = filetype.guess(file_path)
    declared_ext = os.path.splitext(file_path)[1].lower()
    if declared_ext == ".docm":
        return True  # DOCM files are allowed to have macros, so we analyze them anyway
    if not kind:
        return True  # Proceed with analysis anyway if filetype can't be guessed
    actual_ext = f".{kind.extension}"
    return actual_ext == declared_ext


# Compare creation and modification times and return human-readable messages
def compare_time_difference(time_difference: float):
    messages = []
    minutes = int(time_difference // 60)
    hours = int(minutes // 60)
    seconds = int(time_difference % 60)

    if hours > 0:
        messages.append(f"⏱️ Time Difference: {hours}h {minutes % 60}m {seconds}s")
    elif minutes > 0:
        messages.append(f"⏱️ Time Difference: {minutes}m {seconds}s")
    else:
        messages.append(f"⏱️ Time Difference: {int(time_difference)} seconds")

    if time_difference < 0:
        messages.append(
            "✅ File modification time is earlier than creation time. No issue detected."
        )
    elif 0 < time_difference <= 120:
        messages.append(
            "⚠️ Minor difference. Likely due to file transfer or system copy."
        )
    elif time_difference == 0:
        messages.append("✅ Timestamps are exactly the same. No difference.")
    else:
        messages.append(
            "❗ Warning: File was modified AFTER it was originally created (possible tampering)."
        )
    return messages


# Analyze image metadata and check timestamp consistency
def analyze_image_metadata(file_path: str, file_name: str):
    results = [f"**🖼️ File:** {file_name}"]
    try:
        with ExifTool() as et:
            metadata_list = et.execute_json("-j", file_path)
            metadata = metadata_list[0] if metadata_list else {}

            file_modify_raw = metadata.get("File:FileModifyDate")
            exif_original_raw = metadata.get("EXIF:DateTimeOriginal")

            results.append(f"🗓️ File Modify Date      : {file_modify_raw}")
            results.append(f"📷 EXIF DateTime Original: {exif_original_raw}")

            if file_modify_raw and exif_original_raw:
                file_modify_clean = file_modify_raw.split("+")[0].strip()
                exif_original_clean = exif_original_raw.strip()
                file_modify_dt = datetime.strptime(
                    file_modify_clean, "%Y:%m:%d %H:%M:%S"
                )
                exif_original_dt = datetime.strptime(
                    exif_original_clean, "%Y:%m:%d %H:%M:%S"
                )
                time_difference = (file_modify_dt - exif_original_dt).total_seconds()
                results.extend(compare_time_difference(time_difference))
            else:
                results.append(
                    "⚠️ Not enough timestamp information to perform consistency check."
                )
    except Exception as e:
        results.append(f"❌ Failed to check timestamps: {e}")
    return results


# Analyze PDF metadata and search for suspicious content
def analyze_pdf_metadata(file_path: str, file_name: str):
    results = [f"**📄 Analyzing PDF:** {file_name}"]
    try:
        with ExifTool() as et:
            metadata_list = et.execute_json("-j", file_path)
            metadata = metadata_list[0] if metadata_list else {}

            pdf_create = metadata.get("PDF:CreateDate")
            pdf_modify = metadata.get("PDF:ModifyDate")

            results.append(f"📅 PDF Creation Date     : {pdf_create}")
            results.append(f"📝 PDF Last Modified Date: {pdf_modify}")

            if pdf_create and pdf_modify:
                create_clean = pdf_create.split("+")[0].strip()
                modify_clean = pdf_modify.split("+")[0].strip()
                create_dt = datetime.strptime(create_clean, "%Y:%m:%d %H:%M:%S")
                modify_dt = datetime.strptime(modify_clean, "%Y:%m:%d %H:%M:%S")
                time_difference = (modify_dt - create_dt).total_seconds()
                results.extend(compare_time_difference(time_difference))
            else:
                results.append(
                    "⚠️ Not enough timestamp information to perform consistency check."
                )

            # Check for embedded scripts and files
            results.append(
                "🧠 JavaScript detected in the PDF."
                if metadata.get("PDF:JavaScript", "").lower() == "yes"
                else "✔️ No JavaScript detected in the PDF."
            )
            results.append(
                "📎 Embedded files detected in the PDF."
                if metadata.get("PDF:HasEmbeddedFiles", "").lower() == "yes"
                else "✔️ No embedded files detected in the PDF."
            )
            results.append(
                "🧾 Interactive XFA forms detected in the PDF."
                if metadata.get("PDF:HasXFA", "").lower() == "yes"
                else "✔️ No interactive XFA forms detected in the PDF."
            )

        # Check raw PDF for suspicious keywords
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
                results.append("🚨 Suspicious patterns detected in raw PDF content:")
                for kw in hits:
                    results.append(f" - Keyword '{kw}' found")
            else:
                results.append("✅ No suspicious patterns found in raw content.")
        except Exception as e:
            results.append(f"⚠️ Error scanning PDF for patterns: {e}")
    except Exception as e:
        results.append(f"❌ Failed to analyze PDF metadata: {e}")
    return results


# Analyze DOCX metadata and search for embedded content
def analyze_docx_metadata(file_path: str, file_name: str):
    results = [f"**📄 Analyzing DOCX file:** {file_name}"]
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

            results.append(f"🕒 Create Date : {create_raw}")
            results.append(f"🕓 Modify Date : {modify_raw}")

            if create_raw and modify_raw:
                create_clean = create_raw.split("+")[0].strip()
                modify_clean = modify_raw.split("+")[0].strip()
                create_dt = datetime.strptime(create_clean, "%Y:%m:%d %H:%M:%S")
                modify_dt = datetime.strptime(modify_clean, "%Y:%m:%d %H:%M:%S")
                time_difference = (modify_dt - create_dt).total_seconds()
                results.extend(compare_time_difference(time_difference))
            else:
                results.append(
                    "⚠️ Not enough timestamp information to perform consistency check."
                )
    except Exception as e:
        results.append(f"❌ Failed to extract metadata: {e}")

    # Inspect the DOCX zip structure for macros, embedded files, and suspicious strings
    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            file_list = zip_ref.namelist()

            has_macros = any("vbaproject.bin" in f.lower() for f in file_list)
            embedded_objects = [f for f in file_list if "embeddings/" in f.lower()]

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
                try:
                    with zip_ref.open(inner_file) as f:
                        content = f.read().decode(errors="ignore").lower()
                        for keyword in suspicious_keywords:
                            if keyword in content:
                                suspicious_hits.append((inner_file, keyword))
                except:
                    continue

            results.append(
                "🧬 Macros detected in the document."
                if has_macros
                else "✔️ No macros detected in the document."
            )
            if embedded_objects:
                results.append("📎 Embedded objects found:")
                results.extend([f" - {item}" for item in embedded_objects])
            else:
                results.append("✔️ No embedded objects found.")

            if suspicious_hits:
                results.append("🚨 Suspicious patterns detected:")
                results.extend(
                    [
                        f" - Keyword '{kw}' found in {fname}"
                        for fname, kw in suspicious_hits
                    ]
                )
            else:
                results.append("✅ No suspicious patterns found.")
    except Exception as e:
        results.append(f"❌ Failed to analyze DOCX for embedded content: {e}")
    return results


# Convert a duration in seconds into a human-readable string
def format_duration(seconds_str):
    try:
        # Convert the input string to a float
        total_seconds = float(seconds_str)

        # Handle very short durations
        # .2f is used to format seconds with two decimal places
        if total_seconds < 1:
            return f"{total_seconds:.2f} seconds"

        # Convert to hours, minutes, and seconds
        # divmod is used to get the quotient (result) and remainder
        minutes, seconds = divmod(int(total_seconds), 60)
        hours, minutes = divmod(minutes, 60)

        # Build the readable string
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"

    except Exception:
        # If input couldn't be parsed
        return f"{seconds_str} (unreadable)"


# Analyze audio/video files using multiple metadata tags
def analyze_media_metadata(file_path: str, file_name: str):
    kind = filetype.guess(file_path)
    media_label = kind.mime if kind else "Unknown Media"
    results = [f"**📁 Analyzing {media_label}:** {file_name}"]

    try:
        with ExifTool() as et:
            metadata_list = et.execute_json("-j", file_path)
            metadata = metadata_list[0] if metadata_list else {}

            creation_raw = (
                metadata.get("QuickTime:CreateDate")
                or metadata.get("Track:CreateDate")
                or metadata.get("EXIF:CreateDate")
                or metadata.get("ID3:Date")
                or metadata.get("File:FileCreateDate")
            )
            modify_raw = (
                metadata.get("QuickTime:ModifyDate")
                or metadata.get("Track:ModifyDate")
                or metadata.get("File:FileModifyDate")
            )

            results.append(f"🕒 Creation Date : {creation_raw}")
            results.append(f"🕓 Modify Date   : {modify_raw}")

            now = datetime.now()
            if creation_raw and modify_raw:
                creation_clean = creation_raw.split("+")[0].strip()
                modify_clean = modify_raw.split("+")[0].strip()
                creation_dt = datetime.strptime(creation_clean, "%Y:%m:%d %H:%M:%S")
                modify_dt = datetime.strptime(modify_clean, "%Y:%m:%d %H:%M:%S")
                time_difference = (modify_dt - creation_dt).total_seconds()
                results.extend(compare_time_difference(time_difference))
                if creation_dt > now:
                    results.append("⚠️ Suspicious: Creation time is in the future.")
                if modify_dt > now:
                    results.append("⚠️ Suspicious: Modification time is in the future.")
            else:
                results.append(
                    "⚠️ Not enough timestamp information to perform consistency check."
                )

            duration_showed = False
            duration_sec = metadata.get("Track:Duration") or metadata.get(
                "QuickTime:Duration"
            )
            if duration_sec:
                duration_showed = True
                readable = format_duration(duration_sec)
                results.append(f"⏳ Duration: {readable}")
                try:
                    if float(duration_sec) < 1.0:
                        results.append(
                            "⚠️ Very short duration — possibly incomplete or suspicious."
                        )
                except:
                    pass

            for tag in [
                "Format",
                "Duration",
                "AudioCodec",
                "VideoCodec",
                "Title",
                "Artist",
                "Album",
            ]:
                for key in metadata:
                    if key.lower().endswith(tag.lower()):
                        if tag == "Duration" and not duration_showed:
                            results.append(
                                f"⏳ {tag}: {format_duration(metadata[key])}"
                            )
                            continue
                        results.append(f"🎧 {tag}: {metadata[key]}")
                        break
    except Exception as e:
        results.append(f"❌ Failed to analyze {media_label} metadata: {e}")
    return results


# Main dispatcher for analyzing any supported file type
def analyze_file(file_name: str):
    file_path = os.path.join(upload_dir, file_name)

    if not check_exiftool_installed():
        return [
            "❌ ExifTool is not installed. Check the github repository for installation instructions."
        ]

    if not os.path.isfile(file_path):
        return [f"❌ File not found: {file_path}"]

    if not validate_file_extension(file_path):
        return ["⚠️ Analysis skipped due to mismatched file type."]

    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext in [".jpg", ".jpeg", ".png"]:
        return analyze_image_metadata(file_path, file_name)
    elif file_ext == ".pdf":
        return analyze_pdf_metadata(file_path, file_name)
    elif file_ext in [".docx", ".docm"]:
        return analyze_docx_metadata(file_path, file_name)
    elif file_ext in [".mp4", ".mkv", ".m4a", ".mp3", ".wav", ".flac", ".aac"]:
        return analyze_media_metadata(file_path, file_name)
    else:
        return [f"❌ Unsupported file type: {file_ext}"]
