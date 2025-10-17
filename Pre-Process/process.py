import pandas as pd
import warnings
import glob
import os

# Suppress all warnings
warnings.filterwarnings('ignore')

# This function reads a data file (Excel or CSV), cleans it, and saves it as a CSV.
def read_and_clean_file(file_name, new_file_name, header_row=0):
    try:
        df = None
        # Check the file extension and use the correct pandas reader
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_name, header=header_row, low_memory=False)
        elif file_name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_name, header=header_row)
        else:
            print(f"⚠️  Warning: Unsupported file format for '{file_name}'. Skipping.")
            return

        # Handle multi-level headers by joining column names
        if isinstance(header_row, list):
            df.columns = [' '.join(str(col) for col in multi_col).strip() for multi_col in df.columns.values]
        
        # Drop fully empty columns and rows
        df.dropna(axis=1, how='all', inplace=True)
        df.dropna(axis=0, how='all', inplace=True)

        # Save the cleaned DataFrame to a new CSV file
        df.to_csv(new_file_name, index=False)
        print(f"✅ Successfully processed '{file_name}' and saved to '{new_file_name}'.")

    except FileNotFoundError:
        print(f"❌ Error: The file '{file_name}' was not found.")
    except Exception as e:
        print(f"❌ An error occurred while processing '{file_name}': {e}")

# --- Main Processing Logic ---

# 1. Define the files to process by keyword and their settings.
files_to_process = [
    {'keyword': 'population', 'new_file_name': 'population_cleaned.csv', 'header_row': 0},
    {'keyword': 'religion', 'new_file_name': 'religion_cleaned.csv', 'header_row': 0},
    {'keyword': 'education', 'new_file_name': 'education_cleaned.csv', 'header_row': 0},
    {'keyword': 'healthcare', 'new_file_name': 'healthcare_cleaned.csv', 'header_row': 0},
    {'keyword': 'language', 'new_file_name': 'language_cleaned.csv', 'header_row': 2},
    {'keyword': 'occupation', 'new_file_name': 'occupation_cleaned.csv', 'header_row': [4, 5]},
]

# 2. Get a list of all data files (CSV, XLS, XLSX) in the current directory.
file_patterns = ['*.csv', '*.xls', '*.xlsx']
all_data_files = []
for pattern in file_patterns:
    all_data_files.extend(glob.glob(pattern))

# 3. Loop through configurations, find matching files, and process them.
print("--- Starting Data Cleaning Process ---")
for config in files_to_process:
    found_file = None
    for file_path in all_data_files:
        if config['keyword'].lower() in os.path.basename(file_path).lower():
            found_file = file_path
            break
    
    if found_file:
        read_and_clean_file(
            file_name=found_file,
            new_file_name=config['new_file_name'],
            header_row=config['header_row']
        )
    else:
        print(f"⚠️  Warning: No data file found for keyword '{config['keyword']}'. Skipping.")

print("\n--- Process Complete ---")
print("Note: The 'Crops.pdf' file is a PDF and was not processed.")