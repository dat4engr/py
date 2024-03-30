import os
import logging
import send2trash
from datetime import datetime

def get_desktop_path():
    # Get the path of the Desktop directory.
    return os.path.join(os.path.expanduser('~'), 'Desktop')

def check_permission(directory):
    # Check if the user has write permissions for a given directory.
    return os.access(directory, os.W_OK)

def log_action(action, name, path):
    # Create a log message for an action taken on a file or folder.
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"{timestamp}: {action} - {name} ({path})"

def delete_files(desktop_path):
    # Delete files and folders from the Desktop directory and move them to the recycling bin.
    if not os.path.isdir(desktop_path):
        logging.error("Desktop directory not found!")
        return

    log_file_path = "deleted_files.txt"

    number_of_files = 0
    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, 'a') as log_file:
                for root, _, files in os.walk(desktop_path, topdown=False):
                    for name in files:
                        file_path = os.path.join(root, name)
                        try:
                            send2trash.send2trash(file_path)  # Move file to recycling bin
                            number_of_files += 1
                            log_text = log_action("Moved file to recycling bin", name, file_path)
                            log_file.write(log_text + "\n")
                        except OSError as e:
                            logging.error(f"Error moving file to recycling bin: {str(e)}")

                for _, dirs, _ in os.walk(desktop_path, topdown=False):
                    for name in dirs:
                        folder_path = os.path.join(root, name)
                        try:
                            send2trash.send2trash(folder_path)  # Move folder to recycling bin
                            number_of_files += 1
                            log_text = log_action("Moved folder to recycling bin", name, folder_path)
                            log_file.write(log_text + "\n")
                        except OSError as e:
                            logging.error(f"Error moving folder to recycling bin: {str(e)}")
        else:
            logging.error("Log file not found. Aborting deletion process.")
    except OSError as e:
        logging.error(f"Error scanning the desktop directory: {str(e)}")

    logging.info("Files and folders moved to recycling bin successfully!")
    logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Moved {number_of_files} items to the recycling bin on the desktop.")

def get_confirmation(number_of_files):
    # Get user confirmation for moving files and folders to the recycling bin.
    while True:
        confirmation = input(f"Are you sure you want to move {number_of_files} items to the recycling bin on the desktop? (y/n): ")
        if confirmation.lower() in ["y", "n"]:
            return confirmation.lower() == "y"
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    logging.basicConfig(filename="deleted_files.log", level=logging.INFO)
    desktop_path = get_desktop_path()

    if os.path.exists(desktop_path):
        if check_permission(desktop_path):
            confirmation = get_confirmation(10)
            if confirmation:
                delete_files(desktop_path)
            else:
                logging.info("Deletion process cancelled by user.")
        else:
            logging.error("User does not have permission to delete files and folders in the desktop directory.")
    else:
        logging.error("Desktop directory not found. Deletion process aborted.")
