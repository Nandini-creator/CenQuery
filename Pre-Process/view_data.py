import pandas as pd
import glob
import os

# --- Script to Display the First 5 Rows of Cleaned CSVs ---

print("--- Displaying First 5 Entries of each Cleaned CSV ---\n")

# 1. Find all files in the current directory that end with '_cleaned.csv'
cleaned_files = glob.glob('*_cleaned.csv')

# 2. Check if any cleaned files were found
if not cleaned_files:
    print("❌ No cleaned CSV files found.")
    print("Please run the 'process.py' script first to generate the cleaned files.")
else:
    # 3. If files are found, loop through each one
    for file_path in cleaned_files:
        try:
            # Print a header for each file for clarity
            print("======================================================")
            print(f"📄 DataFrame from: {os.path.basename(file_path)}")
            print("======================================================")
            
            # Read the cleaned CSV into a pandas DataFrame
            df = pd.read_csv(file_path)
            
            # Display the first 5 rows of the DataFrame
            # .head() is a pandas function that returns the top n rows (default is 5)
            print(df.head())
            print("\n") # Add a newline for better spacing

        except Exception as e:
            # Handle any errors that might occur during file reading
            print(f"❌ Error reading '{file_path}': {e}\n")

print("--- End of Report ---")