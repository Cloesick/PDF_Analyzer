"""
Compress Archive Folders
Creates zip archives of all archived content to save disk space.
The original folders are kept for safety, but can be deleted after verification.
"""

import zipfile
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
ARCHIVE_ROOT = PROJECT_ROOT / "archive"
OUTPUT_ARCHIVE = PROJECT_ROOT / "output" / "archive"


def get_folder_size(folder: Path) -> int:
    """Calculate total size of folder in bytes"""
    total = 0
    try:
        for item in folder.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
    except Exception:
        pass
    return total


def compress_folder(folder: Path, zip_path: Path) -> tuple[int, int]:
    """
    Compress a folder to zip file.
    Returns (original_size, compressed_size)
    """
    original_size = get_folder_size(folder)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for file in folder.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(folder.parent)
                zipf.write(file, arcname)
    
    compressed_size = zip_path.stat().st_size
    return original_size, compressed_size


def main():
    """Compress all archive folders"""
    
    print("="*80)
    print("ARCHIVE COMPRESSION")
    print("="*80)
    print("Compressing archived files to save disk space\n")
    
    # Find all archive folders
    archive_folders = []
    
    # Root archive folders
    if ARCHIVE_ROOT.exists():
        for folder in ARCHIVE_ROOT.iterdir():
            if folder.is_dir():
                archive_folders.append(("root", folder))
    
    # Output archive folders
    if OUTPUT_ARCHIVE.exists():
        for folder in OUTPUT_ARCHIVE.iterdir():
            if folder.is_dir():
                archive_folders.append(("output", folder))
    
    if not archive_folders:
        print("❌ No archive folders found")
        return
    
    print(f"📂 Found {len(archive_folders)} archive folders to compress\n")
    
    # Create compressed_archives directory
    compressed_dir = PROJECT_ROOT / "compressed_archives"
    compressed_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    total_original = 0
    total_compressed = 0
    compression_results = []
    
    for location, folder in archive_folders:
        folder_name = folder.name
        file_count = sum(1 for _ in folder.rglob("*") if _.is_file())
        
        print(f"📦 Compressing: {folder_name}")
        print(f"   Location: {location}")
        print(f"   Files: {file_count}")
        
        # Create zip file
        if location == "root":
            zip_name = f"archive_{folder_name}_{timestamp}.zip"
        else:
            zip_name = f"output_archive_{folder_name}_{timestamp}.zip"
        
        zip_path = compressed_dir / zip_name
        
        try:
            original_size, compressed_size = compress_folder(folder, zip_path)
            
            total_original += original_size
            total_compressed += compressed_size
            
            ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            print(f"   Original:   {original_size / 1024 / 1024:.2f} MB")
            print(f"   Compressed: {compressed_size / 1024 / 1024:.2f} MB")
            print(f"   Saved:      {ratio:.1f}%")
            print(f"   ✓ Created: {zip_name}\n")
            
            compression_results.append({
                "folder": folder_name,
                "location": location,
                "files": file_count,
                "original_mb": original_size / 1024 / 1024,
                "compressed_mb": compressed_size / 1024 / 1024,
                "ratio": ratio,
                "zip_file": zip_name,
                "folder_path": folder
            })
            
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    # Summary
    print("="*80)
    print("COMPRESSION COMPLETE")
    print("="*80)
    
    total_ratio = (1 - total_compressed / total_original) * 100 if total_original > 0 else 0
    
    print(f"\n📊 Summary:")
    print(f"   Archive folders:    {len(compression_results)}")
    print(f"   Total files:        {sum(r['files'] for r in compression_results)}")
    print(f"   Original size:      {total_original / 1024 / 1024:.2f} MB")
    print(f"   Compressed size:    {total_compressed / 1024 / 1024:.2f} MB")
    print(f"   Space saved:        {(total_original - total_compressed) / 1024 / 1024:.2f} MB ({total_ratio:.1f}%)")
    
    print(f"\n📁 Compressed archives saved to:")
    print(f"   {compressed_dir}")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Verify zip files can be extracted")
    print(f"   2. If verified, you can safely delete original archive folders:")
    
    for result in compression_results:
        print(f"      • {result['folder_path']}")
    
    print(f"\n⚠️  Original folders are kept for safety. Delete manually after verification.")
    print("="*80)
    
    # Create verification script
    verify_script = compressed_dir / "verify_archives.py"
    with verify_script.open("w", encoding="utf-8") as f:
        f.write('''"""Quick verification script to test zip integrity"""
import zipfile
from pathlib import Path

compressed_dir = Path(__file__).parent

print("Testing zip file integrity...\\n")
success = 0
failed = 0

for zip_file in compressed_dir.glob("*.zip"):
    try:
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            bad = zipf.testzip()
            if bad is None:
                print(f"✓ {zip_file.name}")
                success += 1
            else:
                print(f"✗ {zip_file.name} - corrupt file: {bad}")
                failed += 1
    except Exception as e:
        print(f"✗ {zip_file.name} - error: {e}")
        failed += 1

print(f"\\nResult: {success} OK, {failed} failed")
''')
    
    print(f"\n📝 Created verification script: {verify_script.name}")
    print(f"   Run: python {verify_script}")


if __name__ == "__main__":
    main()
