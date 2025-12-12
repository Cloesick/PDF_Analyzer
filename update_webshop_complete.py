"""
Complete Webshop Update from Product_pdfs
==========================================
Runs all necessary scripts to update the webshop with Product_pdfs data:
1. Rebuild products feed
2. Generate grouped catalog files
3. Setup catalog metadata and PDFs
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def run_script(script_name: str, description: str) -> bool:
    """Run a Python script and return success status"""
    
    print(f"\n{'='*80}")
    print(f"🔄 {description}")
    print("="*80)
    
    script_path = PROJECT_ROOT / script_name
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=PROJECT_ROOT,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - Complete")
            return True
        else:
            print(f"❌ {description} - Failed (exit code: {result.returncode})")
            return False
    
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False


def main():
    """Main entry point"""
    
    print("="*80)
    print("🚀 COMPLETE WEBSHOP UPDATE FROM PRODUCT_PDFS")
    print("="*80)
    print("\nThis will run all necessary steps to update the webshop:")
    print("  1. Rebuild products feed (products_for_shop.json)")
    print("  2. Generate grouped catalog files (*_grouped.json)")
    print("  3. Setup catalog metadata and copy PDFs")
    print()
    
    # Track success
    steps = [
        ("rebuild_webshop_from_product_pdfs.py", "Step 1: Rebuild Products Feed"),
        ("generate_grouped_catalogs.py", "Step 2: Generate Grouped Catalogs"),
        ("setup_webshop_from_product_pdfs.py", "Step 3: Setup Catalog Metadata"),
    ]
    
    results = []
    
    for script, description in steps:
        success = run_script(script, description)
        results.append((description, success))
    
    # Final summary
    print(f"\n{'='*80}")
    print("📊 UPDATE SUMMARY")
    print("="*80)
    
    all_success = True
    for description, success in results:
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {status} - {description}")
        if not success:
            all_success = False
    
    print("="*80)
    
    if all_success:
        print("\n🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
        print("\n💡 Next steps:")
        print("  1. Start/restart your webshop:")
        print("     cd C:\\Users\\prova\\Documents\\Projects\\DemaWebshop\\dema-webshop")
        print("     npm run dev")
        print()
        print("  2. Test these pages:")
        print("     http://localhost:3000/products")
        print("     http://localhost:3000/catalogs")
        print("     http://localhost:3000/catalog/slangkoppelingen-grouped")
        print()
    else:
        print("\n⚠️  Some steps failed. Review the output above for details.")
    
    print("="*80)


if __name__ == "__main__":
    main()
