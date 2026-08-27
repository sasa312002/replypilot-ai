from pathlib import Path
from zipfile import ZipFile

import requests


# Kaggle public dataset download URL
DATASET_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/"
    "thoughtvector/customer-support-on-twitter"
)

# Output locations
output_directory = Path("data/raw")
output_directory.mkdir(parents=True, exist_ok=True)

zip_file_path = output_directory / "customer-support-on-twitter.zip"


print("Downloading the Customer Support on Twitter dataset...")


with requests.get(
    DATASET_URL,
    stream=True,
    timeout=300
) as response:

    response.raise_for_status()

    downloaded_bytes = 0
    next_progress_report = 25 * 1024 * 1024

    with zip_file_path.open("wb") as output_file:

        for chunk in response.iter_content(
            chunk_size=1024 * 1024
        ):
            if chunk:
                output_file.write(chunk)
                downloaded_bytes += len(chunk)

                if downloaded_bytes >= next_progress_report:
                    downloaded_mb = downloaded_bytes / (1024 * 1024)
                    print(f"Downloaded approximately {downloaded_mb:.0f} MB...")
                    next_progress_report += 25 * 1024 * 1024


print("Download completed!")
print("Extracting the dataset...")


with ZipFile(zip_file_path, "r") as zip_file:
    zip_file.extractall(output_directory)


csv_files = list(output_directory.rglob("twcs.csv"))

if csv_files:
    print("Dataset extracted successfully!")
    print(f"CSV location: {csv_files[0]}")
else:
    print("The ZIP file was downloaded, but twcs.csv was not found.")