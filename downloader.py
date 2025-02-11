import os
import requests
import datetime
import time

# Constants
BASE_URL = "http://oasis.caiso.com/oasisapi/GroupZip"
GROUP_ID = "DAM_LMP_GRP"  # Grouped DAM LMP data (all nodes)
VERSION = "12"  # API version
RESULT_FORMAT = "6"  # CSV format
START_DATE = datetime.date(2022, 1, 1)  # Start date
END_DATE = datetime.date(2022, 12, 31)  # End date
OUTPUT_DIR = os.path.join(os.getcwd(), "dataset")  # Save in "dataset" folder

# Create the output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function to download LMP data
def download_lmp_data(start_date):
    """Downloads DAM LMP data for a given day in CSV format."""
    end_date = start_date + datetime.timedelta(days=1)  # Only one day allowed per request
    start_str = start_date.strftime("%Y%m%dT07:00-0000")
    end_str = end_date.strftime("%Y%m%dT07:00-0000")

    # Construct URL
    url = f"{BASE_URL}?groupid={GROUP_ID}&startdatetime={start_str}&enddatetime={end_str}&version={VERSION}&resultformat={RESULT_FORMAT}"

    # Filepath to save
    filename = os.path.join(OUTPUT_DIR, f"DAM_LMP_{start_date}.zip")

    print(f"📅 Downloading data for: {start_date} ...")

    # Make the request
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"✅ Saved: {filename}")
    else:
        print(f"❌ Failed to download {start_date}: HTTP {response.status_code}")

# Loop through each date and download
current_date = START_DATE
while current_date <= END_DATE:
    download_lmp_data(current_date)
    current_date += datetime.timedelta(days=1)  # Move to the next day
    print("⏳ Waiting 5 seconds before next request...")
    time.sleep(5)  # Wait 5 seconds to avoid rate limits

print("🎉 All downloads completed!")
