import os
import shutil

def delete_folders(folder_path):
    # Iterate through all the items in the folder
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        # Check if the item is a directory
        if os.path.isdir(item_path):
            # Delete the directory and all its contents
            shutil.rmtree(item_path)
            print(f"Deleted directory: {item_path}")

# Path to the Desktop folder
desktop_folder = '/Add/your/Desktop'

# Call the function to delete all folders
delete_folders(desktop_folder)
