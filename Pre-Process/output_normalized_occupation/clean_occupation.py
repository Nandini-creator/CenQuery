import pandas as pd
import re
import os

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_FILE = "input/Occupation.xls"
OUTPUT_DIR = "output_normalized_occupation"

# Dimension Files (Lookups)
TRU_FILE = os.path.join(OUTPUT_DIR, "tru.csv")
REGIONS_FILE = os.path.join(OUTPUT_DIR, "regions.csv")
AGE_GROUPS_FILE = os.path.join(OUTPUT_DIR, "age_groups.csv")

# Fact File (Data)
OCCUPATION_STATS_FILE = os.path.join(OUTPUT_DIR, "occupation_stats.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_text(text):
    if not isinstance(text, str): return text
    text = str(text).replace('State - ', '')
    text = re.sub(r'\s*\(\d+\)', '', text)
    return text.strip()

def process_occupation_data():
    print(f"📖 Reading: {INPUT_FILE}")
    
    column_names = [
        "table_code", "state_code", "district_code", "area_name", "tru", "age_group",
        "population_total", "population_male", "population_female",
        "main_workers_total", "main_workers_male", "main_workers_female",
        "marginal_workers_total", "marginal_workers_male", "marginal_workers_female",
        "marg_3_6mo_total", "marg_3_6mo_male", "marg_3_6mo_female",
        "marg_less_3mo_total", "marg_less_3mo_male", "marg_less_3mo_female",
        "non_workers_total", "non_workers_male", "non_workers_female",
        "seeking_work_total", "seeking_work_male", "seeking_work_female"
    ]

    try:
        df = pd.read_excel(
            INPUT_FILE, 
            skiprows=9, 
            header=None, 
            names=column_names,
            dtype={'state_code': str, 'district_code': str} 
        )
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return

    df = df.dropna(subset=['state_code'])
    df['area_name'] = df['area_name'].apply(clean_text)
    df['age_group'] = df['age_group'].replace('Total', 'All Ages')
    
    # --- FIX 1: Standardize TRU ---
    print("✂️  Extracting TRU Lookup...")
    tru_map = {
        "Total": 1,
        "Rural": 2,
        "Urban": 3
    }
    tru_df = pd.DataFrame(list(tru_map.items()), columns=['name', 'id'])
    tru_df = tru_df[['id', 'name']]
    tru_df.to_csv(TRU_FILE, index=False)
    print(f"   ✅ Created '{TRU_FILE}'")

    df['tru_id'] = df['tru'].map(tru_map)

    # Extract Regions (preserving state_code for now, will rename later)
    print("✂️  Extracting Regions Lookup...")
    regions_df = df[['state_code', 'district_code', 'area_name']].drop_duplicates()
    regions_df.to_csv(REGIONS_FILE, index=False)
    print(f"   ✅ Created '{REGIONS_FILE}'")

    # Extract Age Groups
    print("✂️  Extracting Age Group Lookup...")
    unique_ages = df['age_group'].unique()
    age_df = pd.DataFrame({'id': range(1, len(unique_ages) + 1), 'name': unique_ages})
    age_df.to_csv(AGE_GROUPS_FILE, index=False)
    print(f"   ✅ Created '{AGE_GROUPS_FILE}'")

    df['age_group_id'] = df['age_group'].map(dict(zip(age_df['name'], age_df['id'])))

    # Cleanup columns
    cols_to_drop = ['area_name', 'tru', 'age_group', 'district_code', 'table_code']
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)

    # --- FIX 2: Rename state_code to state ---
    df.rename(columns={'state_code': 'state'}, inplace=True)

    # Ensure numeric
    numeric_cols = [c for c in df.columns if 'total' in c or 'male' in c or 'female' in c or c == 'state']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # Reorder columns
    keys = ['state', 'tru_id', 'age_group_id'] # 'state' is the new name
    metrics = [c for c in df.columns if c not in keys]
    df = df[keys + metrics]

    df.to_csv(OCCUPATION_STATS_FILE, index=False)
    print(f"   ✅ Created '{OCCUPATION_STATS_FILE}' (Fact Table)")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        process_occupation_data()
    else:
        print(f"❌ File not found: {INPUT_FILE}")