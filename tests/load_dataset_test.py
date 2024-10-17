from scripts.script import download_file_from_google_drive
import os
download_file_from_google_drive(file_id=os.getenv("DATA_SET_PARAMS_ID"))
