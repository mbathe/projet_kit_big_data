from scripts.download_dataset import download_dataset_from_drive
from dotenv import load_dotenv
import os
load_dotenv()

if __name__ == "__main__":
    file_id = os.getenv("DATASET_DRIVE_ID")
    output_dir = os.getenv("DIR_DATASET")
    downloaded_file = download_dataset_from_drive(file_id, output_dir)
