import os
import sys
import shutil
import logging
import json
import datetime
from pathlib import Path

ALL_LANGUAGES = {
    "zh": "Chinese",
    "es": "Spanish",
    "en": "English",
    "hi": "Hindi",
    "ar": "Arabic",
    "bn": "Bengali",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "de": "German"
}

def load_config(config_file: str) -> dict:
    """
    Loads configuration from a JSON file.

    :param config_file: Path to the JSON configuration file.
    :return: Configuration dictionary.
    """
    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise ValueError(f"Configuration file '{config_file}' not found.")
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON in the configuration file '{config_file}'.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error while loading configuration: {e}")
        sys.exit(1)

def scan_directory(target_directory, extensions, excluded_dirs):
    """
    Scans a directory for files, skipping excluded directories.
    """
    for root, dirs, files in os.walk(target_directory):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in excluded_dirs]
        for file in files:
            yield root, file

def generate_directory_tree(base_path: str, indent: str = "") -> str:
    """
    Generates a directory tree in text format for a given base path,
    showing only directories.

    Args:
        base_path (str): The root directory path to start creating the tree.
        indent (str): The indentation for the current level (used internally).

    Returns:
        str: A directory tree as a formatted string.
    """
    if not os.path.isdir(base_path):
        raise ValueError(f"Invalid directory path: {base_path}")

    tree = []
    # Get a sorted list of directories (excluding hidden ones and files)
    entries = sorted(
        [entry for entry in os.listdir(base_path) if
         not entry.startswith(".") and os.path.isdir(os.path.join(base_path, entry))],
        key=lambda s: s.lower()
    )

    for i, entry in enumerate(entries):
        entry_path = os.path.join(base_path, entry)
        connector = "└── " if i == len(entries) - 1 else "├── "
        tree.append(f"{indent}{connector}{entry}")

        # Recursively process subdirectories
        subtree = generate_directory_tree(entry_path, indent + ("    " if i == len(entries) - 1 else "│   "))
        if subtree.strip():  # Only append non-empty results
            tree.append(subtree)

    # Join lines, filtering out any accidental empty lines
    return "\n".join([line for line in tree if line.strip()])

def remove_extension(filename):
    """
    Takes a filename as a string, checks if it has an extension,
    and removes the extension if it exists.

    :param filename: str - The input filename
    :return: str - Filename without the extension
    """
    # Use os.path.splitext to split the filename into name and extension
    name, extension = os.path.splitext(filename)

    # Check if an extension exists
    if extension:
        return name
    return filename

def move_file(current_location: Path, new_location: str, new_document_filename: str) -> None:
    """
    Moves a file from the current location to the new location,
    creating any required directories along the path.

    Args:
        current_location (str): The current file path.
        new_location (str): The new file path, including the new name.
        new_document_filename (str): The new file name.

    Raises:
        FileNotFoundError: If the current_location does not exist.
        PermissionError: If the user lacks required permissions.
        Exception: For all other errors during the file operation.
    """
    # Validate current file exists
    if not os.path.isfile(current_location):
        raise FileNotFoundError(f"The file '{current_location}' does not exist.")

    # Create the target directory path if it doesn't exist
    if not os.path.exists(new_location):
        os.makedirs(new_location)
        logging.info(f"Creating directory {new_location}.")
        new_dir_tree = True
    else:
        logging.info(f"Directory {new_location} exist.")
        new_dir_tree = False

    # Move the file
    shutil.move(current_location, new_location + '/' + new_document_filename)
    print(f"""File moved successfully: "{new_location}" """)

    return new_dir_tree


def get_file_creation_time(file_path):
    """
    Get the creation timestamp of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The creation timestamp in human-readable format.
    """
    try:
        # Get file metadata
        stats = os.stat(file_path)
        # Retrieve the creation time (st_birthtime) in seconds since epoch
        creation_time = stats.st_birthtime
        # Convert the timestamp to a readable datetime format
        return datetime.datetime.fromtimestamp(creation_time)
    except AttributeError:
        # AttributeError occurs if st_birthtime is not available
        raise OSError("st_birthtime is not supported on this platform or file system.")
    except FileNotFoundError:
        return f"File not found: {file_path}"