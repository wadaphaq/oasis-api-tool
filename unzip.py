import os
import zipfile

# Define directories
INPUT_DIR = "dataset"
OUTPUT_DIR = "unzip-dataset"

# Create output directory if not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Iterate over ZIP files and extract them
for file in os.listdir(INPUT_DIR):
    if file.endswith(".zip"):
        file_path = os.path.join(INPUT_DIR, file)
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(OUTPUT_DIR)
        print(f"✅ Extracted: {file}")

print("🎉 All files extracted into 'unzip-dataset'!")
