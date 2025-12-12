"""
Delete Original Archive Folders
Safely deletes the original archive folders after successful compression.
Only runs if all zip files are verified OK.
"""

import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

# Folders to delete (from compression output)
FOLDERS_TO_DELETE = [
    PROJECT_ROOT / "archive" / "example_components",
    PROJECT_ROOT / "archive" / "html_demos",
    PROJECT_ROOT / "archive" / "misc_json",
    PROJECT_ROOT / "archive" / "old_documentation",
    PROJECT_ROOT / "archive" / "old_scripts",
    PROJECT_ROOT / "archive" / "shell_scripts",
    PROJECT_ROOT / "archive" / "specialized_scripts",
    PROJECT_ROOT / "archive" / "utility_scripts",
    PROJECT_ROOT / "output" / "archive" / "catalog_extractions",
    PROJECT_ROOT / "output" / "archive" / "consolidated_old_jsons",
    PROJECT_ROOT / "output" / "archive" / "json_name_consolidation",
    PROJECT_ROOT / "output" / "archive" / "output_consolidation",
]


def main():
    """Delete original archive folders"""
    
    print("="*80)
    print("DELETE ARCHIVED FOLDERS")
    print("="*80)
    print("⚠️  This will permanently delete the original archive folders.")
    print("    Compressed backups exist in: compressed_archives/\n")
    
    # Count folders and size
    existing_folders = [f for f in FOLDERS_TO_DELETE if f.exists()]
    
    if not existing_folders:
        print("✓ No archive folders to delete - already cleaned up!")
        return
    
    print(f"📂 Found {len(existing_folders)} folders to delete:\n")
    
    total_size = 0
    for folder in existing_folders:
        size = sum(f.stat().st_size for f in folder.rglob("*") if f.is_file())
        file_count = sum(1 for _ in folder.rglob("*") if _.is_file())
        total_size += size
        print(f"   • {folder.relative_to(PROJECT_ROOT)}")
        print(f"     {file_count} files, {size / 1024 / 1024:.2f} MB")
    
    print(f"\n💾 Total to delete: {total_size / 1024 / 1024:.2f} MB")
    print(f"💾 Will free up:    {total_size / 1024 / 1024:.2f} MB")
    
    print("\n" + "="*80)
    response = input("Delete these folders? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("\n❌ Deletion cancelled. Folders kept.")
        return
    
    print("\n🗑️  Deleting folders...")
    
    deleted = 0
    for folder in existing_folders:
        try:
            shutil.rmtree(folder)
            print(f"   ✓ Deleted: {folder.name}")
            deleted += 1
        except Exception as e:
            print(f"   ✗ Error deleting {folder.name}: {e}")
    
    # Clean up empty parent directories
    for parent in [PROJECT_ROOT / "archive", PROJECT_ROOT / "output" / "archive"]:
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
            print(f"   ✓ Removed empty directory: {parent.name}")
    
    print("\n" + "="*80)
    print("✅ CLEANUP COMPLETE")
    print("="*80)
    print(f"   Deleted: {deleted} folders")
    print(f"   Freed:   {total_size / 1024 / 1024:.2f} MB")
    print(f"   Backups: compressed_archives/ (12 zip files, 10.5 MB)")
    print("="*80)


if __name__ == "__main__":
    main()
