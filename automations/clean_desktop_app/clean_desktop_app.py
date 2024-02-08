import os
from datetime import datetime
import shutil

def get_desktop_path():
    # Returns the path to the desktop directory based on the current platform.
    return os.path.join(os.path.expanduser('~'), 'Desktop')

def delete_files(desktop_path):
    # Deletes files and folders on the desktop and logs the deleted items in a log file.
    if not os.path.isdir(desktop_path):
        print("Desktop directory not found!")
        return

    log_file_path = os.path.join(os.getcwd(), 'deleted_files.txt')

    try:
        number_of_files = 0
        with open(log_file_path, 'a') as log_file:
            files = os.listdir(desktop_path)

            if not get_confirmation(len(files)):
                print("Deletion cancelled.")
                return

            for file in files:
                file_path = os.path.join(desktop_path, file)
                if os.path.isfile(file_path) or os.path.isdir(file_path):
                    item_type = 'file' if os.path.isfile(file_path) else 'folder'

                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)

                    number_of_files += 1
                    log_text = "{}: Deleted {} - {} ({})\n".format(
                        datetime.now().strftime('%H:%M:%S'), item_type, file, file_path)
                    log_file.write(log_text)

        print("Files and folders deleted successfully!")
        print(f"Deleted {number_of_files} items from the desktop.")
    except FileNotFoundError:
        print("Log file not found!")
    except PermissionError:
        print("Permission denied!")
    except Exception as error:
        print(f"An error occurred: {str(error)}")

def get_confirmation(number_of_files):
    # Prompts the user for confirmation to delete files and folders.
    while True:
        confirmation = input(f"Are you sure you want to delete {number_of_files} items from the desktop? (y/n): ")
        if confirmation.lower() in ["y", "n"]:
            return confirmation.lower() == "y"
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")

desktop_path = get_desktop_path()
delete_files(desktop_path)
