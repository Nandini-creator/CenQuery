import pandas as pd
import re
import os

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_FILE = "input/religion.xlsx"
OUTPUT_DIR = "output_normalized"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_column_name(name):
    if not name: return "col"
    s = str(name).lower().strip()
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    return s[:60]

def normalize_religion_data():
    print(f"📖 Reading: {INPUT_FILE}")
    try:
        df = pd.read_csv(INPUT_FILE)
    except:
        try:
            df = pd.read_excel(INPUT_FILE)
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return

    # 1. Clean Columns
    df.columns = [clean_column_name(c) for c in df.columns]
    
    # 2. Extract Unique Religions (Create Lookup)
    print("✂️  Extracting Religion Lookup Table...")
    unique_religions = df['religion'].unique()
    
    # Create DataFrame: ID | Religion Name
    religions_lookup = pd.DataFrame({
        'id': range(1, len(unique_religions) + 1),
        'religion_name': unique_religions
    })
    
    # Save Lookup
    lookup_path = os.path.join(OUTPUT_DIR, "religions.csv")
    religions_lookup.to_csv(lookup_path, index=False)
    print(f"   ✅ Created '{lookup_path}' ({len(religions_lookup)} rows)")

    # 3. Replace Text with IDs in Main Data
    print("🔗 Linking Data to Lookup...")
    # Create a map: {'Hindu': 1, 'Muslim': 2 ...}
    rel_map = dict(zip(religions_lookup['religion_name'], religions_lookup['id']))
    
    # Apply map
    df['religion_id'] = df['religion'].map(rel_map)
    
    # 4. Final Cleanup for Stats Table
    # Drop columns that are now in lookups or redundant
    cols_to_drop = ['religion', 'district', 'subdistt', 'townvillage', 'name']
    df.drop(columns=[c for c in cols_to_drop if c in df.columns], inplace=True)
    
    # Move religion_id to the front for readability (optional)
    cols = list(df.columns)
    cols.insert(1, cols.pop(cols.index('religion_id')))
    df = df[cols]

    # Save Stats
    stats_path = os.path.join(OUTPUT_DIR, "religion_stats.csv")
    df.to_csv(stats_path, index=False)
    print(f"   ✅ Created '{stats_path}' ({len(df)} rows)")
    
    # 5. SQL Schema Tip
    print("\n💡 SQL for Lookup Table:")
    print("CREATE TABLE religions (id SERIAL PRIMARY KEY, religion_name TEXT UNIQUE);")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        normalize_religion_data()
    else:
        print(f"❌ File not found: {INPUT_FILE}")