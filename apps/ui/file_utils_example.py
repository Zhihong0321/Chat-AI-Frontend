"""
Example usage of file_utils module.
"""
from file_utils import (
    list_folder_files,
    delete_file,
    delete_multiple_files,
    delete_folder,
    get_folder_size,
    clear_folder_contents,
    safe_delete_file
)


def example_list_files():
    """Example: List all files in a folder."""
    try:
        files = list_folder_files("./uploads")
        print(f"Found {len(files)} files:")
        for file in files:
            print(f"  - {file['name']} ({file['size']} bytes)")
    except Exception as e:
        print(f"Error: {e}")


def example_delete_single_file():
    """Example: Delete a single file."""
    try:
        success = delete_file("./uploads/test.txt")
        if success:
            print("File deleted successfully")
    except Exception as e:
        print(f"Error: {e}")


def example_delete_multiple_files():
    """Example: Delete multiple files."""
    files_to_delete = [
        "./uploads/file1.txt",
        "./uploads/file2.txt",
        "./uploads/file3.txt"
    ]
    
    results = delete_multiple_files(files_to_delete)
    print(f"Deleted {results['success_count']} files")
    print(f"Failed to delete {results['failed_count']} files")
    
    if results['failed']:
        print("Failed files:")
        for failed in results['failed']:
            print(f"  - {failed['path']}: {failed['error']}")


def example_delete_folder():
    """Example: Delete an entire folder."""
    try:
        # Delete empty folder
        delete_folder("./temp_folder")
        print("Empty folder deleted")
        
        # Delete folder with contents (force=True)
        delete_folder("./old_uploads", force=True)
        print("Folder with contents deleted")
    except Exception as e:
        print(f"Error: {e}")


def example_get_folder_size():
    """Example: Get total size of folder."""
    try:
        size_bytes = get_folder_size("./uploads")
        size_mb = size_bytes / (1024 * 1024)
        print(f"Folder size: {size_mb:.2f} MB")
    except Exception as e:
        print(f"Error: {e}")


def example_clear_folder():
    """Example: Clear all contents from a folder."""
    try:
        results = clear_folder_contents("./temp")
        print(f"Cleared folder:")
        print(f"  - Files deleted: {results['files_deleted']}")
        print(f"  - Folders deleted: {results['folders_deleted']}")
        
        if results['errors']:
            print(f"  - Errors: {len(results['errors'])}")
    except Exception as e:
        print(f"Error: {e}")


def example_safe_delete():
    """Example: Safely delete with backup."""
    try:
        # Delete with backup
        safe_delete_file("./important.txt", backup_dir="./backups")
        print("File moved to backup")
        
        # Delete without backup
        safe_delete_file("./temp.txt")
        print("File deleted permanently")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("File Utils Examples")
    print("=" * 50)
    
    # Uncomment the examples you want to run:
    # example_list_files()
    # example_delete_single_file()
    # example_delete_multiple_files()
    # example_delete_folder()
    # example_get_folder_size()
    # example_clear_folder()
    # example_safe_delete()
