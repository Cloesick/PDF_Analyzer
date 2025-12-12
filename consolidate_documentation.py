"""
Documentation Consolidation
Consolidates 55+ markdown files into organized documentation structure.

Many files are historical completion reports and summaries that can be archived.
Keeps only essential guides and current documentation.
"""

import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
ARCHIVE_DIR = PROJECT_ROOT / "archive" / "old_documentation"


def consolidate_docs():
    """Consolidate markdown documentation files"""
    
    # Keep these essential files
    keep_files = {
        # Current consolidation docs
        "CONSOLIDATION_GUIDE.md",
        "CONSOLIDATION_RESULTS.md",
        "JSON_CONSOLIDATION_COMPLETE.md",
        "OUTPUT_FOLDER_CONSOLIDATED.md",
        "QUICK_REFERENCE_CONSOLIDATED.md",
        
        # Essential guides
        "README.md",
        "PROJECT_STRUCTURE.md",
        "QUICK_REFERENCE.md",
        "WORKFLOW_GUIDE.md",
        
        # Specific technical guides (still relevant)
        "HOW_SKU_IMAGE_MAPPING_WORKS.md",
        "CATALOG_EXTRACTION_GUIDE.md",
        "FRONTEND_INTEGRATION_GUIDE.md",
        "PRODUCT_GROUPS_IMPLEMENTATION_GUIDE.md",
        "WEBSHOP_INTEGRATION_GUIDE.md",
    }
    
    # Archive these categories
    archive_categories = {
        "completion_reports": [
            "AUTOMATION_SUCCESS_SUMMARY.md",
            "AUTONOMOUS_COMPLETION_SUMMARY.md",
            "CLEANUP_COMPLETE.md",
            "COMPLETE_DEPLOYMENT_SUCCESS.md",
            "DEPLOYMENT_COMPLETE.md",
            "EXECUTION_SUMMARY.md",
            "EXTRACTION_IMPROVEMENTS_COMPLETE.md",
            "FINAL_COMPLETE_SUMMARY.md",
            "IMPLEMENTATION_COMPLETE.md",
            "INTEGRATION_COMPLETE_SUMMARY.md",
            "MASTER_PROJECT_COMPLETE.md",
            "SECURITY_COMPLETE.md",
            "SMART_TABLE_EXTRACTION_COMPLETE.md",
        ],
        "makita_specific": [
            "MAKITA_99_PERCENT_ACHIEVED.md",
            "MAKITA_BATTERY_PRODUCTS.md",
            "MAKITA_CLEANUP_AND_TUINFOLDER.md",
            "MAKITA_EXTRACTION_IMPROVED.md",
            "MAKITA_FINAL_RESULTS.md",
            "MAKITA_FRONTEND_GUIDE.md",
            "MAKITA_IMPROVEMENTS_COMPLETE.md",
            "MAKITA_IMPROVEMENT_PLAN.md",
            "MAKITA_NAMING_UPDATE.md",
            "MAKITA_PRICING_SUMMARY.md",
            "MAKITA_RESULTS_SUMMARY.md",
            "MAKITA_TABLE_EXTRACTION_COMPLETE.md",
            "MAKITA_TOOLS_ONLY_COMPLETE.md",
        ],
        "catalog_specific": [
            "AANDRIJFTECHNIEK_COMPLETE_MAPPING.md",
            "AANDRIJFTECHNIEK_IMAGE_FIX.md",
            "AANDRIJFTECHNIEK_IMAGE_NAMING_GUIDE.md",
            "ABSBU_EXAMPLE.md",
            "BRONPOMPEN_POMPENTOEBEHOREN_DEPLOYMENT.md",
            "RVS_IMPROVEMENT_SUMMARY.md",
        ],
        "old_summaries": [
            "CLEANUP_SUMMARY.md",
            "OUTPUT_CLEANUP_ANALYSIS.md",
            "TODAYS_ACHIEVEMENTS.md",
            "UPDATE_WEBSHOP_DATA.md",
            "WHERE_TO_SEE_UPDATES.md",
        ],
        "deployment_specific": [
            "BATTERY_FRONTEND_INTEGRATION.md",
            "BUGFIX_SEO_SLUG.md",
            "FIXES_AND_NEXT_STEPS.md",
            "FRONTEND_UPDATED_COMPLETE.md",
            "FRONTEND_UPDATED_COMPLETE_FINAL.md",
            "GITHUB_PUSH_INSTRUCTIONS.md",
            "MISSING_TOOLS_FOUND.md",
            "SKU_DETECTION_IMPROVED.md",
            "TABLE_EXTRACTION_FIX.md",
            "TROUBLESHOOTING_PAGE_NOT_LOADING.md",
            "WEBSHOP_DEPLOYMENT_GUIDE.md",
            "WEBSHOP_READY_FINAL.md",
        ],
        "guides_superseded": [
            "CATALOG_EXTRACTION_MAP.md",
            "CATALOG_README.md",
            "COVERAGE_IMPROVEMENT_GUIDE.md",
            "EXHAUSTIVE_EXTRACTION_GUIDE.md",
            "EXPANSION_PLAN.md",
            "PDF_ANALYZER_STATUS.md",
            "PRODUCT_DATA_ISSUES.md",
            "PRODUCT_STRUCTURE_COMPARISON.md",
            "README_EXPANSION.md",
            "README_IMAGE_EXTRACTION.md",
            "README_IMAGE_LINKING.md",
            "README_STATS_BANNER.md",
            "STATS_BANNER_USAGE.md",
            "TABLE_PRODUCTS_GUIDE.md",
            "ULTIMATE_EXTRACTOR_README.md",
            "SYSTEM_SECURITY_CHECKLIST.md",
        ],
    }
    
    # Create archive directory
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("DOCUMENTATION CONSOLIDATION")
    print("="*80)
    
    # Count files
    total_to_archive = sum(len(files) for files in archive_categories.values())
    print(f"\nFound {total_to_archive} documentation files to archive")
    print(f"Keeping {len(keep_files)} essential files\n")
    
    # Archive by category
    archived_count = 0
    for category, files in archive_categories.items():
        if not files:
            continue
        
        print(f"\n📁 {category.replace('_', ' ').title()}: {len(files)} files")
        
        for filename in files:
            file_path = PROJECT_ROOT / filename
            if file_path.exists():
                target = ARCHIVE_DIR / filename
                shutil.move(str(file_path), str(target))
                print(f"   Archived: {filename}")
                archived_count += 1
            else:
                print(f"   Not found: {filename}")
    
    # Summary
    print(f"\n{'='*80}")
    print("CONSOLIDATION COMPLETE")
    print("="*80)
    print(f"Files archived:     {archived_count}")
    print(f"Files kept:         {len(keep_files)}")
    print(f"Archive location:   {ARCHIVE_DIR}")
    print()
    print("✅ Documentation is now organized:")
    print("   • Essential guides in root")
    print("   • Historical docs archived")
    print("   • Clear structure")
    print("="*80)


if __name__ == "__main__":
    consolidate_docs()
