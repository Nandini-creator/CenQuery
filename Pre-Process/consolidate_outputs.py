import os
import shutil
import pandas as pd

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "unified_outputs")

# Mapping of source folders to the files we want to grab
# We deliberately pick 'regions.csv' from healthcare because it was the most complete (had Ladakh & Telangana)
SOURCES = {
    "output normalized healthcare": [
        "regions.csv",          # MASTER COPY: Contains 39 states (incl. Telangana/Ladakh)
        "healthcare_stats.csv",
        "tru.csv"               # MASTER COPY
    ],
    "output normalized population": [
        # "population.csv",
        "population_stats.csv",
        # Skipping regions.csv here (it was older/less clean)
    ],
    "output normalized education": [
        "pca_stats.csv"
        # Skipping tru.csv (duplicate)
    ],
    "output normalized religion": [
        "religion_stats.csv",
        "religions.csv"
        # Skipping tru.csv (duplicate)
    ],
    "output normalized occupation": [
        "occupation_stats.csv",
        "age_groups.csv"
        # Skipping regions.csv & tru.csv (duplicates)
    ],
    "output normalized language": [
        "language_stats.csv",
        "languages.csv"
        # Skipping regions.csv & tru.csv (duplicates)
    ],
    "output crop": [
        "crops.csv"
    ]
}

def consolidate():
    # 1. Create the unified folder
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Created directory: {OUTPUT_DIR}")
    else:
        print(f"📁 Directory exists: {OUTPUT_DIR}")

    print("-" * 40)

    # 2. Iterate and Copy
    copied_count = 0
    for folder, files in SOURCES.items():
        src_folder_path = os.path.join(BASE_DIR, folder)
        
        if not os.path.exists(src_folder_path):
            print(f"⚠️  Warning: Source folder not found: {folder}")
            continue

        for filename in files:
            src_file = os.path.join(src_folder_path, filename)
            dst_file = os.path.join(OUTPUT_DIR, filename)

            if os.path.exists(src_file):
                shutil.copy2(src_file, dst_file)
                print(f"✅ Copied: {filename:<25} (from {folder})")
                copied_count += 1
            else:
                print(f"❌ Missing: {filename:<25} (in {folder})")

    # 3. Create a README to document the schema
    readme_path = os.path.join(OUTPUT_DIR, "README.txt")
    with open(readme_path, "w") as f:
        f.write("UNIFIED CENSUS DATA STAGING AREA\n")
        f.write("================================\n\n")
        f.write("Master Tables:\n")
        f.write("- regions.csv  (Source: Healthcare, includes 39 states/UTs)\n")
        f.write("- tru.csv      (Source: Healthcare, Total/Rural/Urban mapping)\n\n")
        f.write("Data Tables:\n")
        f.write("- population_stats.csv\n")
        f.write("- healthcare_stats.csv\n")
        f.write("- pca_stats.csv (Education)\n")
        f.write("- religion_stats.csv\n")
        f.write("- occupation_stats.csv\n")
        f.write("- crops.csv\n")
        f.write("- language_stats.csv\n")
    
    print("-" * 40)
    print(f"🎉 Success! {copied_count} files consolidated into 'unified_outputs/'.")

if __name__ == "__main__":
    consolidate()