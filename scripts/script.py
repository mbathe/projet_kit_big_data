import kagglehub
import os
from dotenv import load_dotenv
load_dotenv()
def download_dataset():
    print("Downloading dataset...")
    path = kagglehub.dataset_download(
        "shuyangli94/food-com-recipes-and-user-interactions", path=os.getenv('DATA_DIR'))
    print("Path to dataset files:", path)
