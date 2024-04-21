import os
import logging
import send2trash
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Update the logging configuration to capture additional log messages
logging.basicConfig(filename="deleted_files.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_desktop_path():
    # Get the path of the Desktop directory.
    return os.path.join(os.path.expanduser('~'), 'Desktop')

def check_permission(directory):
    # Check if the user has write permissions for a given directory.
    return os.access(directory, os.W_OK)

def log_action(action, name, path, result):
    # Create a log message for an action taken on a file or folder including the result.
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"{timestamp}: {action} - {name} ({path}) - Result: {result}"

def move_to_recycle_bin(item_path, log_file, is_file=True):
    # Move an item to the recycling bin with confirmation prompt.
    try:
        confirmation = input(f"Are you sure you want to move the {'file' if is_file else 'folder'} {os.path.basename(item_path)} to the recycling bin? (y/n): ")
        
        if confirmation.lower() == 'y':
            send2trash.send2trash(item_path)  # Move item to recycling bin with confirmation
            log_text = log_action(f"Moved {'file' if is_file else 'folder'} to recycling bin", os.path.basename(item_path), item_path, "Success")
            log_file.write(log_text + "\n")
            return 1
        elif confirmation.lower() == 'n':
            return 0
        else:
            logging.error(f"Invalid input. Skipping {'file' if is_file else 'folder'} deletion.")
            return 0
    except OSError as error:
        logging.error(f"Error moving {'file' if is_file else 'folder'} to recycling bin: {str(error)}")
        return 0

def delete_items(item_path, log_file, is_file=True):
    # Delete items based on specified criteria and move them to the recycling bin.
    if (is_file and os.path.isfile(item_path)) or (not is_file and os.path.isdir(item_path)):
        return move_to_recycle_bin(item_path, log_file, is_file)
    return 0

def delete_files(desktop_path, max_file_size=None, file_type=None, days_since_modified=None):
    # Delete files and folders based on specified criteria from the Desktop directory and move them to the recycling bin.
    if not os.path.isdir(desktop_path):
        logging.error("Desktop directory not found!")
        return

    log_file_path = "deleted_files.txt"

    number_of_items_deleted = 0
    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, 'a') as log_file:
                with ThreadPoolExecutor() as executor:
                    for item in os.scandir(desktop_path):
                        if item.is_file():
                            if (max_file_size is None or item.stat().st_size <= max_file_size) and \
                               (file_type is None or item.name.endswith(file_type)) and \
                               (days_since_modified is None or (datetime.now() - datetime.fromtimestamp(item.stat().st_mtime)).days <= days_since_modified):
                                number_of_items_deleted += executor.submit(delete_items, item.path, log_file, is_file=True).result()
                        elif item.is_dir():
                            number_of_items_deleted += executor.submit(delete_items, item.path, log_file, is_file=False).result()

        else:
            logging.error("Log file not found. Aborting deletion process.")
    except OSError as error:
        logging.error(f"Error scanning the desktop directory: {str(error)}")

    logging.info("Files and folders moved to the recycling bin successfully!")
    logging.info(f"Moved {number_of_items_deleted} items to the recycling bin on the desktop.")

if __name__ == "__main__":
    desktop_path = get_desktop_path()

    try:
        if os.path.exists(desktop_path):
            if check_permission(desktop_path):
                delete_files(desktop_path)
            else:
                logging.error("User does not have permission to delete files and folders in the desktop directory.")
        else:
            logging.error("Desktop directory not found. Deletion process aborted.")
    except Exception as error:
        logging.error(f"An error occurred: {str(error)}")
