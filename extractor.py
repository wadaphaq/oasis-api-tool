import pandas as pd
import json

# Load the XLS file
file_path = "LMPLocations_vs_FullList.xls"
xls = pd.ExcelFile(file_path)

# Extract the sheet names
print("Available sheets:", xls.sheet_names)

# Load the first sheet (you can change this if needed)
df = xls.parse(xls.sheet_names[0])

# Assuming the node names are in a column named 'Node Name' or similar
# Adjust the column name based on your file's structure
column_name = 'name'  # Change this if necessary
if column_name not in df.columns:
    print("Column name not found. Available columns:", df.columns)
    exit()

# Extract node names
node_names = df[column_name].dropna().unique().tolist()

# Save as JSON
json_file = "nodes.json"
with open(json_file, "w") as f:
    json.dump(node_names, f, indent=4)

# Save as CSV
csv_file = "nodes.csv"
pd.DataFrame(node_names, columns=["Node Name"]).to_csv(csv_file, index=False)

print(f"Node names extracted and saved to {json_file} and {csv_file}")
