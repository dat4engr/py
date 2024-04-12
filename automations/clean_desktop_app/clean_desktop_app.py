import os
import logging
import send2trash
from datetime import datetime

# Update the logging configuration to capture additional log messages
logging.basicConfig(filename="deleted_files.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def move_file_to_recycle_bin(file_path, log_file):
    # Move a file to the recycling bin with confirmation prompt.
    try:
        confirmation = input(f"Are you sure you want to move the file {os.path.basename(file_path)} to the recycling bin? (y/n): ")
        
        if confirmation.lower() == 'y':
            send2trash.send2trash(file_path)  # Move file to recycling bin
            log_text = log_action("Moved file to recycling bin", os.path.basename(file_path), file_path)
            log_file.write(log_text + "\n")
            return 1
        elif confirmation.lower() == 'n':
            return 0
        else:
            logging.error("Invalid input. Skipping file deletion.")
            return 0
    except OSError as e:
        logging.error(f"Error moving file to recycling bin: {str(e)}")
        return 0

def move_folder_to_recycle_bin(folder_path, log_file):
    # Move a folder to the recycling bin with confirmation prompt.
    try:
        confirmation = input(f"Are you sure you want to move the folder {os.path.basename(folder_path)} to the recycling bin? (y/n): ")
        
        if confirmation.lower() == 'y':
            send2trash.send2trash(folder_path)  # Move folder to recycling bin
            log_text = log_action("Moved folder to recycling bin", os.path.basename(folder_path), folder_path)
            log_file.write(log_text + "\n")
            return 1
        elif confirmation.lower() == 'n':
            return 0
        else:
            logging.error("Invalid input. Skipping folder deletion.")
            return 0
    except OSError as error:
        logging.error(f"Error moving folder to recycling bin: {str(error)}")
        return 0

def delete_files(desktop_path, max_file_size=None, file_type=None, days_since_modified=None):
    # Delete files based on specified criteria from the Desktop directory and move them to the recycling bin.
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
                        if os.path.isfile(file_path):
                            if (max_file_size is None or os.path.getsize(file_path) <= max_file_size) and \
                               (file_type is None or file_path.endswith(file_type)) and \
                               (days_since_modified is None or (datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))).days <= days_since_modified):
                                number_of_files += move_file_to_recycle_bin(file_path, log_file)

                for root, dirs, _ in os.walk(desktop_path, topdown=False):
                    for name in dirs:
                        folder_path = os.path.join(root, name)
                        number_of_files += move_folder_to_recycle_bin(folder_path, log_file)

        else:
            logging.error("Log file not found. Aborting deletion process.")
    except OSError as error:
        logging.error(f"Error scanning the desktop directory: {str(error)}")

    logging.info("Files and folders moved to recycling bin successfully!")
    logging.info(f"Moved {number_of_files} items to the recycling bin on the desktop.")

def get_confirmation(number_of_files):
    # Get user confirmation for moving files and folders to the recycling bin.
    while True:
        confirmation = input(f"Are you sure you want to move {number_of_files} items to the recycling bin on the desktop? (y/n): ")
        if confirmation.lower() in ["y", "n"]:
            return confirmation.lower() == "y"
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")

if __name__ == "__main__":
    desktop_path = get_desktop_path()

    try:
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
    except Exception as error:
        logging.error(f"An error occurred: {str(error)}")
