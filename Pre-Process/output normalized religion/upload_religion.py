import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

load_dotenv()

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
RELIGIONS_LOOKUP_FILE = "output_normalized/religions.csv"
RELIGION_STATS_FILE = "output_normalized/religion_stats.csv"

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

DB_CONNECTION_STRING = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

def enable_rls(table_name, engine):
    """Secures the table with RLS."""
    print(f"  🔒 Securing table '{table_name}'...")
    try:
        with engine.begin() as conn:
            conn.execute(text(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY;'))
            conn.execute(text(f'DROP POLICY IF EXISTS "Public Read Access" ON "{table_name}";'))
            conn.execute(text(f'CREATE POLICY "Public Read Access" ON "{table_name}" FOR SELECT USING (true);'))
        print(f"     ✅ Security applied.")
    except Exception as e:
        print(f"     ⚠️ Error applying security: {e}")

def upload_lookup_table(engine):
    """Uploads the religions lookup table."""
    if not os.path.exists(RELIGIONS_LOOKUP_FILE):
        print(f"❌ Error: {RELIGIONS_LOOKUP_FILE} not found. Run normalization first.")
        return False

    print(f"\n🚀 Uploading LOOKUP table: 'religions'...")
    df = pd.read_csv(RELIGIONS_LOOKUP_FILE)
    
    try:
        # 1. Upload
        df.to_sql('religions', engine, if_exists='replace', index=False)
        print(f"     ✅ Data uploaded ({len(df)} rows).")
        
        # 2. Set Primary Key
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE religions ADD PRIMARY KEY (id);"))
        print(f"     ✅ Primary Key enforced.")
        
        enable_rls('religions', engine)
        return True
    except Exception as e:
        print(f"     ❌ Error uploading lookup: {e}")
        return False

def upload_stats_table(engine):
    """Uploads stats and links to BOTH Regions and Religions."""
    if not os.path.exists(RELIGION_STATS_FILE):
        print(f"❌ Error: {RELIGION_STATS_FILE} not found.")
        return False

    print(f"\n🚀 Uploading DATA table: 'religion_stats'...")
    # Load data in chunks to prevent memory issues
    df_iter = pd.read_csv(RELIGION_STATS_FILE, chunksize=5000)
    
    try:
        # 1. Upload in Chunks
        first_chunk = True
        total_rows = 0
        for chunk in df_iter:
            mode = 'replace' if first_chunk else 'append'
            chunk.to_sql('religion_stats', engine, if_exists=mode, index=False)
            first_chunk = False
            total_rows += len(chunk)
            print(f"     ... uploaded {total_rows} rows")
            
        print(f"     ✅ Total uploaded: {total_rows} rows.")
        
        # 2. Add Foreign Keys (The 3-Table Link)
        with engine.begin() as conn:
            # Link to Regions (State)
            conn.execute(text("""
                ALTER TABLE religion_stats 
                ADD CONSTRAINT fk_regions_rel 
                FOREIGN KEY (state) REFERENCES regions(state);
            """))
            print(f"     ✅ Linked to 'regions' table.")

            # Link to Religions (Religion ID)
            conn.execute(text("""
                ALTER TABLE religion_stats 
                ADD CONSTRAINT fk_religions_lookup 
                FOREIGN KEY (religion_id) REFERENCES religions(id);
            """))
            print(f"     ✅ Linked to 'religions' table.")
        
        enable_rls('religion_stats', engine)
        return True
        
    except Exception as e:
        print(f"     ❌ Error uploading stats: {e}")
        return False

# ==========================================
# 🏁 MAIN
# ==========================================
if __name__ == "__main__":
    try:
        engine = create_engine(DB_CONNECTION_STRING, poolclass=NullPool)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connected to Supabase.")

        # Step 1: Upload Lookup
        if upload_lookup_table(engine):
            # Step 2: Upload Data & Link
            upload_stats_table(engine)
            
    except Exception as e:
        print(f"❌ Critical Error: {e}")