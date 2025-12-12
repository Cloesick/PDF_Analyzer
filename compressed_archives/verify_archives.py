"""Quick verification script to test zip integrity"""
import zipfile
from pathlib import Path

compressed_dir = Path(__file__).parent

print("Testing zip file integrity...\n")
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

print(f"\nResult: {success} OK, {failed} failed")
