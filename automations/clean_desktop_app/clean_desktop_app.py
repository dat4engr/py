import os
import platform
from datetime import datetime

def delete_files():
    desktop_path = ''
    
    # Get desktop path according to the operating system
    if platform.system() == 'Windows':
        desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    elif platform.system() == 'Darwin':  # macOS
        desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    elif platform.system() == 'Linux':
        desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    
    if os.path.isdir(desktop_path):
        # Open log file in append mode
        log_file = open('deleted_files_log.txt', 'a')
    
        # List all files and directories on the desktop
        files = os.listdir(desktop_path)
        
        # Filter and delete files and folders
        for file in files:
            file_path = os.path.join(desktop_path, file)
            if os.path.isfile(file_path) or os.path.isdir(file_path):
                # Delete files and directories
                os.remove(file_path) if os.path.isfile(file_path) else os.rmdir(file_path)
                
                # Log the time and file/folder name
                log_text = f"{datetime.now().strftime('%H:%M:%S')}: Deleted {'file' if os.path.isfile(file_path) else 'folder'} - {file}\n"
                log_file.write(log_text)
                
        log_file.close()
        print("Files and folders deleted successfully!")
    else:
        print("Desktop directory not found!")

delete_files()
