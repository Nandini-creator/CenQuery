from dotenv import load_dotenv
import pandas as pd
import re
import os
import pdfplumber
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine, text

# ==========================================
# 🔧 CONFIGURATION
# ==========================================
INPUT_FOLDER = 'input'  # Place all your XLS/PDF files here
OUTPUT_FOLDER = 'output_3'  # Cleaned CSVs and SQL definitions will be saved here
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct the SQLAlchemy connection string
DB_CONNECTION_STRING = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"


# ==========================================
# 🧠 SMART HEURISTICS (Header Detection and Cleaning)
# ==========================================
def is_mostly_strings(series):
    """Checks if a row is predominantly text/non-numeric."""
    # Note: Using .astype(str) for safety before checking if it's numeric
    non_numeric = sum(1 for item in series if not isinstance(item, (int, float)))
    return non_numeric / len(series) > 0.8

def find_header_row(df_preview):
    """Finds the row index that looks most like a header based on heuristics."""
    candidates = {}
    for i in range(len(df_preview)):
        row = df_preview.iloc[i].dropna()
        if len(row) == 0: continue
        
        score = 0
        
        # Rule 1: Text row followed by numeric row
        if i + 1 < len(df_preview):
            next_row = df_preview.iloc[i+1].dropna()
            numeric_next = sum(1 for x in next_row if isinstance(x, (int, float)) or str(x).replace('.','',1).isdigit())
            if is_mostly_strings(row) and numeric_next > len(next_row) / 2:
                score += 5
        
        # Rule 2: Keywords
        row_text = " ".join(row.astype(str).str.lower())
        if any(x in row_text for x in ['code', 'district', 'total', 'population', 'name']):
            score += 3
            
        candidates[i] = score

    # --- FIX IS BELOW ---
    if not candidates:
        return 0
    
    # We find the item (key, value) with the highest value (score), then return the key (row index)
    best_row_index, best_score = max(candidates.items(), key=lambda item: item[1])
    return best_row_index

def clean_column_names(df):
    """Standardizes column names, truncates to 63 chars, and handles duplicates."""
    cleaned = []
    seen = set()
    
    for col in df.columns:
        # 1. Standardize: lowercase, no spaces, no special chars
        c = re.sub(r'\s+', '_', str(col).strip().lower())
        c = re.sub(r'[^a-z0-9_]', '', c)
        
        # 2. Handle Empty
        if not c:
            c = f"col_{len(cleaned)}"

        # 3. Truncate to 60 characters to leave room for potential suffixes
        # Postgres limit is 63. We use 60 to be safe.
        c = c[:60]
        
        # 4. Handle Duplicates (Collision Resolution)
        original_c = c
        counter = 1
        while c in seen:
            # Create a suffix, e.g., "_1", "_2"
            suffix = f"_{counter}"
            # Ensure we don't exceed 63 chars even with suffix
            # We cut the original string shorter to fit the suffix
            c = original_c[:(63 - len(suffix))] + suffix
            counter += 1
        
        seen.add(c)
        cleaned.append(c)
        
    df.columns = cleaned
    return df

# ==========================================
# 📂 FILE PROCESSORS (The File Router)
# ==========================================
def process_excel(filepath):
    """Reads, intelligently cleans, and returns a DataFrame from an Excel file."""
    try:
        preview = pd.read_excel(filepath, nrows=20, header=None)
        header_idx = find_header_row(preview)
        
        # Read full file using the determined header
        df = pd.read_excel(filepath, header=header_idx)
        df = clean_column_names(df)
        df.dropna(how='all', inplace=True)
        return df
    except Exception as e:
        print(f"     ❌ Error processing Excel: {e}")
        return None

def process_pdf(filepath):
    """Extracts tables from a PDF file (best effort) and returns a DataFrame."""
    all_tables = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        # Assume first row of the extracted table is the header
                        df = pd.DataFrame(table[1:], columns=table[0])
                        all_tables.append(df)
        
        if not all_tables: return None
        full_df = pd.concat(all_tables, ignore_index=True)
        full_df = clean_column_names(full_df)
        return full_df
    except Exception as e:
        print(f"     ❌ Error processing PDF: {e}")
        return None

# ==========================================
# 🚀 UPLOADER
# ==========================================
def upload_to_db(df, table_name, engine):
    """Uploads DataFrame to PostgreSQL with chunking."""
    print(f"  🚀 Uploading {len(df)} rows to table '{table_name}'...")
    try:
        # Using if_exists='replace' creates the table if it doesn't exist 
        # or overwrites it if it does.
        # chunksize prevents huge transactions from timing out on Supabase.
        df.to_sql(table_name, engine, if_exists='replace', index=False, chunksize=1000)
        print(f"     ✅ Success! Table '{table_name}' created/replaced.")
        enable_rls(table_name, engine)
    except Exception as e:
        print(f"     ❌ Database Error during upload: {e}")

def enable_rls(table_name, engine):
    """Enables RLS and creates a policy allowing public read access."""
    print(f"  🔒 Securing table '{table_name}'...")
    try:
        # We use a transaction to ensure all security settings apply together
        with engine.begin() as conn:
            # 1. Enable Row Level Security (Removes "Unrestricted" warning)
            conn.execute(text(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY;'))
            
            # 2. Clean up old policies if they exist (to prevent errors on re-runs)
            conn.execute(text(f'DROP POLICY IF EXISTS "Public Read Access" ON "{table_name}";'))
            
            # 3. Create a policy that allows anyone (anon) to SELECT (read) data
            conn.execute(text(f'CREATE POLICY "Public Read Access" ON "{table_name}" FOR SELECT USING (true);'))
            
        print(f"     ✅ Security applied: Public Read / Admin Write.")
    except Exception as e:
        print(f"     ⚠️ Error applying security: {e}")

def save_sql_schema(df, table_name, engine, output_folder):
    """Generates the CREATE TABLE SQL statement and saves it to a file."""
    try:
        # Pandas can generate the CREATE TABLE statement for us!
        schema_sql = pd.io.sql.get_schema(df, table_name, con=engine)
        
        # Save it to a .sql file
        output_filename = f"{table_name}.sql"
        output_path = os.path.join(output_folder, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(schema_sql + ";")
            
        print(f"  📜 Saved SQL definition to '{output_path}'")
    except Exception as e:
        print(f"  ❌ Error saving SQL definition: {e}")

# ==========================================
# 🏁 MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    
    # 1. Setup Folders
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"Created input folder '{INPUT_FOLDER}'. Please place your files there and run again.")
        exit()
    
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"Created output folder '{OUTPUT_FOLDER}' for local backups.")

    # 2. Setup DB Engine
    try:
        engine = create_engine(DB_CONNECTION_STRING,  poolclass=NullPool)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connected to Supabase successfully.\n")
    except Exception as e:
        print(f"❌ FATAL: Could not connect to Supabase. Check connection string.\nError: {e}")
        exit()

    # 3. Process and Upload Files
    for filename in os.listdir(INPUT_FOLDER):
        filepath = os.path.join(INPUT_FOLDER, filename)
        if os.path.isdir(filepath) or filename.startswith('.'): continue

        print(f"Processing File: {filename}")
        
        # Generate a SQL-friendly table name and local CSV filename
        base_name = os.path.splitext(filename)[0]
        table_name = re.sub(r'[^a-z0-9]', '_', base_name.lower())
        output_filename = table_name + '.csv'
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        df = None
        
        # File Router
        if filename.lower().endswith(('.xls', '.xlsx')):
            df = process_excel(filepath)
        elif filename.lower().endswith('.pdf'):
            df = process_pdf(filepath)
        else:
            print(f"  ⚠️ Skipping unsupported file type: {filename}")

        if df is not None and not df.empty:
            
            # --- LOCAL SAVE ---
            try:
                df.to_csv(output_path, index=False)
                print(f"  💾 Saved clean file locally to '{output_path}'")
            except Exception as e:
                print(f"  ❌ Error saving local CSV: {e}")
            
            save_sql_schema(df, table_name, engine, OUTPUT_FOLDER)

            # --- DATABASE UPLOAD ---
            # upload_to_db(df, table_name, engine)
        
        elif df is not None and df.empty:
            print(f"  ⚠️ Skipping upload: DataFrame for {filename} is empty after cleaning.")
        
        print("-" * 30)

