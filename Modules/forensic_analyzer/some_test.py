from exiftool import ExifTool


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
