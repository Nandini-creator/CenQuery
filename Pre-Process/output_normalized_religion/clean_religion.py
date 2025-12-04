import pandas as pd
import re
import os

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_FILE = "input/religion.xlsx"
OUTPUT_DIR = "output_normalized_religion"
RELIGIONS_FILE = os.path.join(OUTPUT_DIR, "religions.csv")
TRU_FILE = os.path.join(OUTPUT_DIR, "tru.csv")
STATS_FILE = os.path.join(OUTPUT_DIR, "religion_stats.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_column_name(name):
    if not name: return "col"
    s = str(name).lower().strip()
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    return s[:60]

def process_religion_data():
    print(f"📖 Reading: {INPUT_FILE}")
    try:
        df = pd.read_csv(INPUT_FILE)
    except:
        try:
            df = pd.read_excel(INPUT_FILE)
        except Exception as e:
            print(f"❌ Error: {e}")
            return

    df.columns = [clean_column_name(c) for c in df.columns]
    
    # --- FIX: Standardize TRU ---
    print("   🆕 Creating Standardized TRU lookup...")
    tru_map = {
        "Total": 1,
        "Rural": 2,
        "Urban": 3
    }
    tru_df = pd.DataFrame(list(tru_map.items()), columns=['name', 'id'])
    tru_df = tru_df[['id', 'name']]
    tru_df.to_csv(TRU_FILE, index=False)
    
    df['tru_id'] = df['tru'].map(tru_map)

    # Handle Religion Lookup
    print("   ✂️  Extracting Religion Lookup...")
    unique_rel = df['religion'].unique()
    rel_df = pd.DataFrame({'id': range(1, len(unique_rel) + 1), 'religion_name': unique_rel})
    rel_df.to_csv(RELIGIONS_FILE, index=False)
    
    rel_map = dict(zip(rel_df['religion_name'], rel_df['id']))
    df['religion_id'] = df['religion'].map(rel_map)

    # Cleanup
    cols_to_drop = ['religion', 'tru', 'district', 'subdistt', 'townvillage', 'name']
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
    
    if 'state' in df.columns:
        df['state'] = df['state'].fillna(0).astype(int)

    # Reorder
    cols = list(df.columns)
    # Ensure state, tru_id, religion_id are first
    priority = ['state', 'tru_id', 'religion_id']
    for col in reversed(priority):
        if col in cols:
            cols.insert(0, cols.pop(cols.index(col)))
    df = df[cols]

    df.to_csv(STATS_FILE, index=False)
    print(f"✅ Created '{STATS_FILE}'")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        process_religion_data()
    else:
        print(f"❌ File not found: {INPUT_FILE}")