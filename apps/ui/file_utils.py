"""
File and folder management utilities.
"""
import os
import shutil
from typing import List, Dict, Optional
from pathlib import Path


def list_folder_files(folder_path: str) -> List[Dict[str, any]]:
    """
    List all files in a folder with their metadata.
    
    Args:
        folder_path: Path to the folder
        
    Returns:
        List of dictionaries containing file information
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")
    
    files = []
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        
        if os.path.isfile(item_path):
            stat = os.stat(item_path)
            files.append({
                'name': item,
                'path': item_path,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'extension': os.path.splitext(item)[1]
            })
    
    return files


def delete_file(file_path: str) -> bool:
    """
    Delete a single file.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not os.path.isfile(file_path):
            raise IsADirectoryError(f"Path is a directory, not a file: {file_path}")
        
        os.remove(file_path)
        return True
    except Exception as e:
        raise Exception(f"Failed to delete file: {str(e)}")


def delete_multiple_files(file_paths: List[str]) -> Dict[str, any]:
    """
    Delete multiple files.
    
    Args:
        file_paths: List of file paths to delete
        
    Returns:
        Dictionary with success/failure counts and details
    """
    results = {
        'success': [],
        'failed': [],
        'success_count': 0,
        'failed_count': 0
    }
    
    for file_path in file_paths:
        try:
            delete_file(file_path)
            results['success'].append(file_path)
            results['success_count'] += 1
        except Exception as e:
            results['failed'].append({
                'path': file_path,
                'error': str(e)
            })
            results['failed_count'] += 1
    
    return results


def delete_folder(folder_path: str, force: bool = False) -> bool:
    """
    Delete a folder and all its contents.
    
    Args:
        folder_path: Path to the folder to delete
        force: If True, delete even if folder is not empty
        
    Returns:
        True if successful
    """
    try:
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"Path is not a directory: {folder_path}")
        
        # Check if folder is empty
        if not force and os.listdir(folder_path):
            raise ValueError(f"Folder is not empty. Use force=True to delete non-empty folders.")
        
        # Delete folder and all contents
        shutil.rmtree(folder_path)
        return True
    except Exception as e:
        raise Exception(f"Failed to delete folder: {str(e)}")


def get_folder_size(folder_path: str) -> int:
    """
    Calculate total size of all files in a folder.
    
    Args:
        folder_path: Path to the folder
        
    Returns:
        Total size in bytes
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    
    return total_size


def clear_folder_contents(folder_path: str) -> Dict[str, any]:
    """
    Delete all files and subfolders within a folder, but keep the folder itself.
    
    Args:
        folder_path: Path to the folder to clear
        
    Returns:
        Dictionary with deletion statistics
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")
    
    results = {
        'files_deleted': 0,
        'folders_deleted': 0,
        'errors': []
    }
    
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                results['files_deleted'] += 1
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                results['folders_deleted'] += 1
        except Exception as e:
            results['errors'].append({
                'path': item_path,
                'error': str(e)
            })
    
    return results


def safe_delete_file(file_path: str, backup_dir: Optional[str] = None) -> bool:
    """
    Safely delete a file with optional backup.
    
    Args:
        file_path: Path to the file to delete
        backup_dir: Optional directory to move file to instead of deleting
        
    Returns:
        True if successful
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if backup_dir:
        # Move to backup instead of deleting
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, os.path.basename(file_path))
        
        # Handle duplicate names
        counter = 1
        while os.path.exists(backup_path):
            name, ext = os.path.splitext(os.path.basename(file_path))
            backup_path = os.path.join(backup_dir, f"{name}_{counter}{ext}")
            counter += 1
        
        shutil.move(file_path, backup_path)
    else:
        # Direct deletion
        os.remove(file_path)
    
    return True
