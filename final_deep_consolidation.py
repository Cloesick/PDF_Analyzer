"""
Final Deep Consolidation
Consolidates remaining duplicate/similar files:
- Utility scripts (check_, debug_, verify_, test_ patterns)
- Component files (TSX/JSX)
- HTML demo files
- PowerShell/Batch scripts
- Remaining specialized scripts
"""

import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ARCHIVE_DIR = PROJECT_ROOT / "archive"


def consolidate_utility_scripts():
    """Archive check_, debug_, verify_, test_ scripts"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: Utility Scripts")
    print("="*80)
    
    patterns = {
        "check_scripts": list(PROJECT_ROOT.glob("check_*.py")),
        "debug_scripts": list(PROJECT_ROOT.glob("debug_*.py")),
        "verify_scripts": list(PROJECT_ROOT.glob("verify_*.py")),
        "test_scripts": list(PROJECT_ROOT.glob("test_*.py")),
        "inspect_scripts": list(PROJECT_ROOT.glob("inspect_*.py")),
        "diagnose_scripts": list(PROJECT_ROOT.glob("diagnose_*.py")),
        "show_scripts": list(PROJECT_ROOT.glob("show_*.py")),
    }
    
    archive_util = ARCHIVE_DIR / "utility_scripts"
    archive_util.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for category, files in patterns.items():
        if files:
            print(f"\n📁 {category.replace('_', ' ').title()}: {len(files)} files")
            for file in files:
                shutil.move(str(file), str(archive_util / file.name))
                print(f"   Archived: {file.name}")
                count += 1
    
    return count


def consolidate_specialized_scripts():
    """Archive specialized one-off scripts"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: Specialized Scripts")
    print("="*80)
    
    # Scripts that are catalog/task specific and not needed anymore
    specific_files = [
        # Extract specific
        "extract_aandrijf_images.py",
        "extract_aandrijf_specs.py",
        "extract_abs_from_tables.py",
        "extract_all_catalogs_dynamic.py",
        "extract_all_images_universal.py",
        "extract_missing_catalogs.py",
        "extract_missing_images.py",
        "extract_missing_tools.py",
        "extract_plat_oprolbare_correct.py",
        "extract_pomp_manual_parsing.py",
        "extract_pomp_specials_correct.py",
        "extract_pomp_specials_correct_v2.py",
        "extract_rvs_improved.py",
        "extract_rvs_properties.py",
        "extract_single_catalog.py",
        "extract_slangkoppelingen_correct.py",
        
        # Deploy specific
        "deploy_complete_bronpompen.py",
        "deploy_complete_pompentoebehoren.py",
        "deploy_complete_verzinkte_buizen.py",
        
        # Create specific
        "create_aandrijftechniek_report.py",
        "create_all_catalog_pages.py",
        "create_complete_aandrijftechniek_data.py",
        "create_final_summary.py",
        "create_grouped_from_products_feed.py",
        "create_pe_buizen_report.py",
        "create_plat_oprolbare_report.py",
        "create_products_grouped_data.py",
        
        # Fix/enhance specific
        "fix_aandrijftechniek_images.py",
        "fix_aandrijftechniek_images_v2.py",
        "fix_concatenated_tables.py",
        "fix_webshop_images.py",
        "enhance_properties_with_icons.py",
        "enhance_table_descriptions.py",
        
        # Link/map specific
        "link_images_to_grouped.py",
        "link_images_to_products.py",
        "link_makita_images.py",
        "link_makita_ultra_aggressive.py",
        "map_all_aandrijftechniek_images.py",
        
        # Rename/clean specific
        "rename_aandrijftechniek_images.py",
        "rename_all_aandrijftechniek_images.py",
        "rename_experiment_images.py",
        "clean_airpress_images.py",
        "clean_grouped_data.py",
        "cleanup_makita_images.py",
        
        # Merge specific
        "merge_comprehensive_to_webshop.py",
        "merge_makita_properties.py",
        "merge_makita_to_webshop.py",
        "merge_rvs_complete.py",
        
        # Other specialized
        "add_multilanguage_names.py",
        "batch_analyze_pdfs.py",
        "calculate_stats.py",
        "category_aware_extractor.py",
        "classify_images_with_gpt.py",
        "complete_aandrijftechniek_mapping.py",
        "convert_aandrijftechniek_to_grouped.py",
        "convert_to_webp.py",
        "copy_existing_images.py",
        "copy_to_webshop.py",
        "dynamic_table_extractor.py",
        "enhanced_table_extractor.py",
        "enrich_aandrijftechniek_with_properties.py",
        "enrich_all_grouped_catalogs.py",
        "enrich_all_jsons.py",
        "enrich_grouped_products.py",
        "enrich_jsons_with_image_paths.py",
        "filter_best_tool_images.py",
        "final_comprehensive_brand_analysis.py",
        "final_exhaustive_verification.py",
        "final_verification.py",
        "find_better_product_images.py",
        "find_missing_tool_images.py",
        "format_makita_batteries_table.py",
        "full_sync_images.py",
        "generate_catalog_data.py",
        "group_catalog_products.py",
        "group_table_products.py",
        "identify_incomplete_pdfs.py",
        "identify_unparsed_columns.py",
        "integrate_exhaustive_extraction.py",
        "keep_only_new_extraction.py",
        "parse_catalog_text_data.py",
        "prepare_for_webshop.py",
        "process_all_catalogs.py",
        "property_translation_config.py",
        "re_extract_with_smart_parsing.py",
        "regenerate_catalog_pages_exact.py",
        "regroup_by_table_and_image.py",
        "remove_all_non_tools.py",
        "replace_with_tools_only.py",
        "rewrite_media_urls.py",
        "run_catalog_extraction.py",
        "run_extraction_with_progress.py",
        "run_selective_extraction.py",
        "serve_catalog.py",
        "smart_property_extractor.py",
        "sync_images_and_rebuild.py",
        "sync_webp_to_webshop.py",
        "test_extraction_one_pdf.py",
        "ultimate_pdf_extractor.py",
        "validate_aandrijftechniek_system.py",
    ]
    
    archive_spec = ARCHIVE_DIR / "specialized_scripts"
    archive_spec.mkdir(parents=True, exist_ok=True)
    
    count = 0
    print(f"Found {len(specific_files)} specialized scripts to archive:")
    for filename in specific_files:
        file_path = PROJECT_ROOT / filename
        if file_path.exists():
            shutil.move(str(file_path), str(archive_spec / filename))
            if count < 10:  # Show first 10
                print(f"   Archived: {filename}")
            count += 1
    
    if count > 10:
        print(f"   ... and {count - 10} more")
    
    return count


def consolidate_components():
    """Archive component files"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: Component Files")
    print("="*80)
    
    components = [
        "ProductCard.jsx",
        "ProductCardEnhanced.tsx",
        "ProductGroupWithVariants.tsx",
        "ProductSpecsWithIcons.tsx",
        "PropertyBadges.tsx",
        "StatsBanner.tsx",
        "example_components_for_webshop.tsx",
    ]
    
    archive_comp = ARCHIVE_DIR / "example_components"
    archive_comp.mkdir(parents=True, exist_ok=True)
    
    count = 0
    print(f"Found {len(components)} component files:")
    for filename in components:
        file_path = PROJECT_ROOT / filename
        if file_path.exists():
            shutil.move(str(file_path), str(archive_comp / filename))
            print(f"   Archived: {filename}")
            count += 1
    
    return count


def consolidate_html_demos():
    """Archive HTML demo files"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: HTML Demo Files")
    print("="*80)
    
    html_files = [
        "makita_products_demo.html",
        "print_catalog.html",
        "product_catalog.html",
        "product_group_demo.html",
    ]
    
    archive_html = ARCHIVE_DIR / "html_demos"
    archive_html.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for filename in html_files:
        file_path = PROJECT_ROOT / filename
        if file_path.exists():
            shutil.move(str(file_path), str(archive_html / filename))
            print(f"   Archived: {filename}")
            count += 1
    
    return count


def consolidate_scripts_and_batch():
    """Archive PowerShell and batch files"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: Shell Scripts")
    print("="*80)
    
    scripts = [
        "backup_aandrijftechniek_mappings.ps1",
        "backup_mappings.ps1",
        "copy_all_images_to_webshop.ps1",
        "update_webshop_data.ps1",
        "run_image_linking.bat",
        "sync_to_webshop.bat",
    ]
    
    archive_shell = ARCHIVE_DIR / "shell_scripts"
    archive_shell.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for filename in scripts:
        file_path = PROJECT_ROOT / filename
        if file_path.exists():
            shutil.move(str(file_path), str(archive_shell / filename))
            print(f"   Archived: {filename}")
            count += 1
    
    return count


def consolidate_json_files():
    """Archive remaining JSON files in root"""
    
    print("\n" + "="*80)
    print("CONSOLIDATING: Root JSON Files")
    print("="*80)
    
    json_files = [
        "makita_image_analysis_report.json",
        "debug_table_p2_t4.json",
    ]
    
    archive_json = ARCHIVE_DIR / "misc_json"
    archive_json.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for filename in json_files:
        file_path = PROJECT_ROOT / filename
        if file_path.exists():
            shutil.move(str(file_path), str(archive_json / filename))
            print(f"   Archived: {filename}")
            count += 1
    
    return count


def main():
    """Run final deep consolidation"""
    
    print("="*80)
    print("FINAL DEEP CONSOLIDATION")
    print("="*80)
    print("Consolidating all remaining duplicate/specialized files\n")
    
    counts = {}
    
    counts["utility"] = consolidate_utility_scripts()
    counts["specialized"] = consolidate_specialized_scripts()
    counts["components"] = consolidate_components()
    counts["html"] = consolidate_html_demos()
    counts["shell"] = consolidate_scripts_and_batch()
    counts["json"] = consolidate_json_files()
    
    total = sum(counts.values())
    
    print("\n" + "="*80)
    print("FINAL CONSOLIDATION COMPLETE")
    print("="*80)
    print(f"Total files archived: {total}\n")
    
    for category, count in counts.items():
        if count > 0:
            print(f"   {category.title():20} {count:3} files")
    
    print(f"\n✅ Project is now maximally consolidated!")
    print(f"   Essential files remain in root")
    print(f"   All others archived to archive/")
    print("="*80)


if __name__ == "__main__":
    main()
