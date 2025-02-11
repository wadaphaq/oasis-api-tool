import os
import pandas as pd

# Define directories
INPUT_DIR = "unzip-dataset"
OUTPUT_FILE = "combined.csv"

# Get list of CSV files
csv_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".csv")]

# Initialize CSV writer
combined_df = pd.DataFrame()

# Read & concatenate files in chunks (efficient for large data)
for idx, file in enumerate(csv_files):
    file_path = os.path.join(INPUT_DIR, file)
    df = pd.read_csv(file_path, low_memory=False)  # Load CSV
    combined_df = pd.concat([combined_df, df], ignore_index=True)

    print(f"✅ Merged: {file} ({idx+1}/{len(csv_files)})")

# Save to a single CSV file
combined_df.to_csv(OUTPUT_FILE, index=False)

print(f"🎉 All CSV files combined into {OUTPUT_FILE}!")
