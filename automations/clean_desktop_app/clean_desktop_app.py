import os
import shutil
import logging
from datetime import datetime
from pathlib import Path

def get_desktop_path():
    # Returns the path to the desktop directory.
    return Path.home() / "Desktop"

def delete_files(desktop_path):
    # Deletes files and folders from the desktop.
    if not desktop_path.is_dir():
        logging.error("Desktop directory not found!")
        return

    log_file_path = Path.cwd() / "deleted_files.txt"

    try:
        number_of_files = 0
        with log_file_path.open('a') as log_file:
            files = [file for file in desktop_path.iterdir() if file.is_file() or file.is_dir()]

            if not get_confirmation(len(files)):
                logging.info("Deletion cancelled.")
                return

            for file in files:
                item_type = "file" if file.is_file() else "folder"
                file_path = desktop_path / file

                if file.is_dir():
                    shutil.rmtree(file_path)
                else:
                    file.unlink()

                number_of_files += 1
                log_text = f"{datetime.now().strftime('%H:%M:%S')}: Deleted {item_type} - {file} ({file_path})\n"
                log_file.write(log_text)

        logging.info("Files and folders deleted successfully!")
        logging.info(f"Deleted {number_of_files} items from the desktop.")
    except FileNotFoundError:
        logging.error("Log file not found!")
    except PermissionError:
        logging.error("Permission denied!")
    except Exception as error:
        logging.error(f"An error occurred: {str(error)}")

def get_confirmation(number_of_files):
    # Asks for confirmation to delete files and folders.
    while True:
        confirmation = input(f"Are you sure you want to delete {number_of_files} items from the desktop? (y/n): ")
        if confirmation.lower() in ["y", "n"]:
            return confirmation.lower() == "y"
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    logging.basicConfig(filename="delete_files.log", level=logging.INFO)
    desktop_path = get_desktop_path()
    delete_files(desktop_path)
