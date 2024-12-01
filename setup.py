from scripts.script import download_dataset_from_drive
from dotenv import load_dotenv
import os
load_dotenv()


if __name__ == "__main__":
    file_id = os.getenv("DATA_SET_PARAMS_ID")
    output_dir = os.getenv("DIR_DATASET_DOCKER")
    downloaded_file = download_dataset_from_drive(file_id, output_dir)
