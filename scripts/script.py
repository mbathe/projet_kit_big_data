from dotenv import dotenv_values
import os
import kagglehub
from dotenv import load_dotenv

load_dotenv()


def download_dataset():
    print("Downloading dataset...")
    path = kagglehub.dataset_download(
        "shuyangli94/food-com-recipes-and-user-interactions")
    print("Path to dataset files:", path)


download_dataset()
