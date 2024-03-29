import os
import logging
from datetime import datetime
import send2trash

def get_desktop_path():
    # Get the path to the user's Desktop folder.
    return os.path.join(os.path.expanduser('~'), 'Desktop')

def check_permission(directory):
    # Check if the user has permission to delete files and folders in specified directory.
    return os.access(directory, os.W_OK)

def delete_files(desktop_path):
    # Move files and folders to the recycle bin instead of permanently deleting them.
    if not os.path.isdir(desktop_path):
        logging.error("Desktop directory not found!")
        return

    log_file_path = "deleted_files.txt"

    number_of_files = 0
    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, 'a') as log_file:
                for root, dirs, files in os.walk(desktop_path, topdown=False):
                    for name in files:
                        file_path = os.path.join(root, name)
                        send2trash.send2trash(file_path)  # Move file to recycling bin
                        number_of_files += 1
                        log_text = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Moved file to recycling bin - {name} ({file_path})\n"
                        log_file.write(log_text)

                for name in dirs:
                    folder_path = os.path.join(root, name)
                    send2trash.send2trash(folder_path)  # Move folder to recycling bin
                    number_of_files += 1
                    log_text = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Moved folder to recycling bin - {name} ({folder_path})\n"
                    log_file.write(log_text)
        else:
            logging.error("Log file not found. Aborting deletion process.")
    except OSError as e:
        logging.error(f"Error scanning the desktop directory: {str(e)}")

    logging.info("Files and folders moved to recycling bin successfully!")
    logging.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Moved {number_of_files} items to the recycling bin on the desktop.")

    if log_file:
        log_file.close()

def get_confirmation(number_of_files):
    # Get user confirmation for the deletion process.
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
