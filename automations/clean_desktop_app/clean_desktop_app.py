import os
import logging
from datetime import datetime

def get_desktop_path():
    # Get the path to the user's Desktop folder.
    return os.path.join(os.path.expanduser('~'), 'Desktop')

def delete_files(desktop_path):
    # Delete files and folders from the specified directory.
    if not os.path.isdir(desktop_path):
        logging.error("Desktop directory not found!")
        return

    log_file_path = "deleted_files.txt"

    number_of_files = 0
    try:
        with open(log_file_path, 'a') as log_file:
            for entry in os.scandir(desktop_path):
                item_type = "file" if os.path.isfile(os.path.join(desktop_path, entry.name)) else "folder"
                file_path = os.path.join(desktop_path, entry.name)

                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)

                number_of_files += 1
                log_text = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Deleted {item_type} - {entry.name} ({file_path})\n"
                log_file.write(log_text)
    except OSError as e:
        logging.error(f"Error scanning the desktop directory: {str(e)}")

    logging.info("Files and folders deleted successfully!")
    logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Deleted {number_of_files} items from the desktop.")

    if log_file:
        log_file.close()

def get_confirmation(number_of_files):
    # Get user confirmation for the deletion process.
    while True:
        confirmation = input(f"Are you sure you want to delete {number_of_files} items from the desktop? (y/n): ")
        if confirmation.lower() in ["y", "n"]:
            return confirmation.lower() == "y"
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    logging.basicConfig(filename="deleted_files.log", level=logging.INFO)
    desktop_path = get_desktop_path()

    if os.path.exists(desktop_path):
        confirmation = get_confirmation(10)
        if confirmation:
            delete_files(desktop_path)
        else:
            logging.info("Deletion process cancelled by user.")
    else:
        logging.error("Desktop directory not found. Deletion process aborted.")
