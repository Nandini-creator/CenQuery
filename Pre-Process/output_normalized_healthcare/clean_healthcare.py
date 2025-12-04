import pandas as pd
import re
import os

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_FILE = "input/Healthcare.xls"
OUTPUT_DIR = "output_normalized_healthcare"

# Master Files
REGIONS_FILE = os.path.join(OUTPUT_DIR, "regions.csv")
TRU_FILE = os.path.join(OUTPUT_DIR, "tru.csv")

# Output for this specific dataset
STATS_FILE = os.path.join(OUTPUT_DIR, "healthcare_stats.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ... (Keep your existing clean_column_name function here) ...
def clean_column_name(name):
    """Shortens verbose healthcare column names."""
    if not name: return "col"
    s = str(name).lower().strip()
    replacements = {
        'per 1,000 live births': '',
        'per 100,000 live births': '',
        'percentage': 'pct',
        'population': 'pop',
        'households': 'hh',
        'children under age 5 years': 'child_u5',
        'women age 15-49 years': 'women_15_49',
        'men age 15-54 years': 'men_15_54',
        'literate': 'lit',
        'attended school': 'school',
        'sex ratio': 'sex_ratio',
        'births': 'births',
        'deaths': 'deaths'
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    return s[:60]

def process_healthcare_data():
    print(f"📖 Reading: {INPUT_FILE}")
    try:
        df = pd.read_excel(INPUT_FILE, header=1)
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # 1. Clean Columns
    df.columns = [clean_column_name(c) for c in df.columns]
    
    # 2. Process Regions (States)
    print("🗺️  Processing Regions (States)...")
    # Load existing regions if available, else create
    # (Assuming standard State IDs 0-35 exist, we map them)
    # For healthcare, we often have names like "India", "North", etc.
    # Here we assume a mapping logic exists or we perform a merge.
    # For simplicity in this fix, we ensure the column is named 'state'
    
    # ... (Your existing Region extraction logic fits here) ...
    # Ensuring the final dataframe has a 'state' column with IDs is key.
    # If your original script did this via name mapping, keep it.
    
    # 3. Process TRU (Standardized)
    print("🏙️  Processing TRU (Area)...")
    tru_map = {
        "Total": 1,
        "Rural": 2,
        "Urban": 3
    }
    
    # Create standardized lookup file
    tru_df = pd.DataFrame(list(tru_map.items()), columns=['name', 'id'])
    tru_df = tru_df[['id', 'name']]
    tru_df.to_csv(TRU_FILE, index=False)
    
    # Map TRU IDs
    # Healthcare file likely has 'Area' or similar column
    if 'area' in df.columns:
        df['tru_id'] = df['area'].map(tru_map)
    
    # 4. Final Polish & Save
    # Drop text columns if IDs exist
    cols_to_drop = ['states_uts', 'area', 'clean_state']
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True, errors='ignore')
    
    df.to_csv(STATS_FILE, index=False)
    print(f"✅ Created '{STATS_FILE}'")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        process_healthcare_data()
    else:
        print(f"❌ File not found: {INPUT_FILE}")