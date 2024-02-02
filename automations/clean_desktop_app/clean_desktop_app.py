import os
import platform
from datetime import datetime

def delete_files():
    # Deletes files and folders on the desktop and logs the deleted items in a log file.
    desktop_path = ''

    # Get desktop path according to the operating system (Windows, MacOS, or Linux)
    if platform.system() == 'Windows':
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    elif platform.system() == 'Darwin':
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    elif platform.system() == 'Linux':
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    if os.path.isdir(desktop_path):
        try:
            # Open log file in append mode using with statement
            log_file_path = os.path.join(os.getcwd(), 'deleted_files.txt')
            with open(log_file_path, 'a') as log_file:
                # List all files and directories on the desktop
                files = os.listdir(desktop_path)
                
                # Prompt user for confirmation before deleting
                confirmation = input(f"Are you sure you want to delete {len(files)} items from the desktop? (y/n): ")
                if confirmation.lower() != "y":
                    print("Deletion cancelled.")
                    return
                
                # Filter and delete files and folders
                for file in files:
                    file_path = os.path.join(desktop_path, file)
                    if os.path.isfile(file_path) or os.path.isdir(file_path):
                        # Determine whether it is a file or folder
                        item_type = 'file' if os.path.isfile(file_path) else 'folder'

                        # Delete files and directories
                        os.remove(file_path) if os.path.isfile(file_path) else os.rmdir(file_path)

                        # Log the time, file/folder name, and type
                        log_text = f"{datetime.now().strftime('%H:%M:%S')}: Deleted {item_type} - {file} ({file_path})\n"
                        log_file.write(log_text)

            print("Files and folders deleted successfully!")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    else:
        print("Desktop directory not found!")

delete_files()
