import gdown
import zipfile
import os
from dotenv import load_dotenv
from googledriver import download
load_dotenv()
def download_datase(url):
    output_zip = 'dataset.zip'
    gdown.download(url, output_zip, quiet=False)
    with zipfile.ZipFile(output_zip, 'r') as zip_ref:
        zip_ref.extractall(os.getenv('DATA_DIR'))


def download_file_from_google_drive(file_id, destination="mon_fichier_test.zip"):
    URL = 'https://drive.google.com/file/d/1a2JonFLnOCvtML2ZQWFCtpniWwmmCUuo/view?usp=share_link'
    download(URL, '../data', cached_filename="mon_fichier_test.zip")
    """
    # URL = "https://docs.google.com/uc?export=download&confirm=t"
    session = requests.Session()
    response = session.get(URL, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)
    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)
 """


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
