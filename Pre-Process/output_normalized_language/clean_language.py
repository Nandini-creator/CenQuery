import pandas as pd
import re
import os

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_FILE = "input/Language.xlsx"
OUTPUT_DIR = "output_normalized_language"

# Dimension Files (Lookups)
LANGUAGES_FILE = os.path.join(OUTPUT_DIR, "languages.csv")
REGIONS_FILE = os.path.join(OUTPUT_DIR, "regions.csv")
TRU_FILE = os.path.join(OUTPUT_DIR, "tru.csv")

# Fact File (Data)
LANGUAGE_STATS_FILE = os.path.join(OUTPUT_DIR, "language_stats.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_area_name(text):
    if not isinstance(text, str): return text
    text = str(text).replace('State - ', '')
    text = re.sub(r'\s*\(\d+\)', '', text)
    return text.strip()

def clean_language_name(text):
    if not isinstance(text, str): return text
    text = re.sub(r'^\d+\s+', '', text)
    return text.strip().title()

def process_language_data():
    print(f"📖 Reading: {INPUT_FILE}")
    
    column_names = [
        "table_code", "state_code", "district_code", "sub_district_code", "area_name",
        "language_code", "language_name",
        "tot_p", "tot_m", "tot_f",   
        "rur_p", "rur_m", "rur_f",   
        "urb_p", "urb_m", "urb_f"    
    ]

    try:
        df = pd.read_excel(
            INPUT_FILE, 
            skiprows=6,  
            header=None, 
            names=column_names,
            dtype={'state_code': str, 'district_code': str, 'language_code': str}
        )
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return

    df = df.dropna(subset=['state_code'])
    df['area_name'] = df['area_name'].apply(clean_area_name)
    df['language_name_clean'] = df['language_name'].apply(clean_language_name)

    print("✂️  Extracting Languages Lookup...")
    languages_df = df[['language_code', 'language_name_clean']].drop_duplicates()
    languages_df.rename(columns={'language_name_clean': 'name', 'language_code': 'id'}, inplace=True)
    languages_df.to_csv(LANGUAGES_FILE, index=False)
    print(f"   ✅ Created '{LANGUAGES_FILE}'")

    print("✂️  Extracting Regions Lookup...")
    regions_df = df[['state_code', 'area_name']].drop_duplicates()
    regions_df.to_csv(REGIONS_FILE, index=False)
    print(f"   ✅ Created '{REGIONS_FILE}'")

    # Standardize TRU
    tru_data = [{'id': 1, 'name': 'Total'}, {'id': 2, 'name': 'Rural'}, {'id': 3, 'name': 'Urban'}]
    pd.DataFrame(tru_data).to_csv(TRU_FILE, index=False)
    print(f"   ✅ Created '{TRU_FILE}'")

    print("🔄 Unpivoting Data (Wide -> Long)...")
    normalized_rows = []
    
    for _, row in df.iterrows():
        base_info = {
            'state': row['state_code'],  # FIX: Renamed directly to 'state'
            'language_id': row['language_code']
        }
        
        # 1. Total Rows (TRU=1)
        row_tot = base_info.copy()
        row_tot.update({'tru_id': 1, 'person': row['tot_p'], 'male': row['tot_m'], 'female': row['tot_f']})
        normalized_rows.append(row_tot)
        
        # 2. Rural Rows (TRU=2)
        row_rur = base_info.copy()
        row_rur.update({'tru_id': 2, 'person': row['rur_p'], 'male': row['rur_m'], 'female': row['rur_f']})
        normalized_rows.append(row_rur)
        
        # 3. Urban Rows (TRU=3)
        row_urb = base_info.copy()
        row_urb.update({'tru_id': 3, 'person': row['urb_p'], 'male': row['urb_m'], 'female': row['urb_f']})
        normalized_rows.append(row_urb)

    df_norm = pd.DataFrame(normalized_rows)
    
    for c in ['person', 'male', 'female']:
        df_norm[c] = pd.to_numeric(df_norm[c], errors='coerce').fillna(0).astype(int)

    df_norm.to_csv(LANGUAGE_STATS_FILE, index=False)
    print(f"   ✅ Created '{LANGUAGE_STATS_FILE}' (Fact Table)")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        process_language_data()
    else:
        print(f"❌ File not found: {INPUT_FILE}")