import os
import platform
from datetime import datetime
import shutil

# Deletes files and folders on the desktop and logs the deleted items in a log file.
def delete_files():
    desktop_paths = {
        'Windows': os.path.join(os.path.expanduser('~'), 'Desktop'),
        'Darwin': os.path.join(os.path.expanduser('~'), 'Desktop'),
        'Linux': os.path.join(os.path.expanduser('~'), 'Desktop')
    }

    desktop_path = desktop_paths.get(platform.system())

    if not desktop_path or not os.path.isdir(desktop_path):
        print("Desktop directory not found!")
        return

    # Open log file in append mode using with statement
    try:
        log_file_path = os.path.join(os.getcwd(), 'deleted_files.txt')
        with open(log_file_path, 'a') as log_file:
            # List all files and directories on the desktop
            files = os.listdir(desktop_path)

            if not get_confirmation(len(files)):
                print("Deletion cancelled.")
                return

            # Filter and delete files and folders
            for file in files:
                file_path = os.path.join(desktop_path, file)
                if os.path.isfile(file_path) or os.path.isdir(file_path):
                    # Determine whether it is a file or folder
                    item_type = 'file' if os.path.isfile(file_path) else 'folder'

                    # Delete files and folders
                    shutil.rmtree(file_path) if os.path.isdir(file_path) else os.remove(file_path)

                    # Log the time, file/folder name, and type
                    log_text = f"{datetime.now().strftime('%H:%M:%S')}: Deleted {item_type} - {file} ({file_path})\n"
                    log_file.write(log_text)

        print("Files and folders deleted successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Prompts the user for confirmation to delete files and folders.
def get_confirmation(num_files):
    while True:
        confirmation = input(f"Are you sure you want to delete {num_files} items from the desktop? (y/n): ")
        if confirmation.lower() in ["y", "n"]:
            return confirmation.lower() == "y"
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")

delete_files()
