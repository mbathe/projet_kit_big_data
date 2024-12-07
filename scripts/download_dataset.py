import kagglehub
import os
import shutil
import gdown
import zipfile
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("../script.log"),
        logging.StreamHandler()
    ]
)

### DOWNLOAD FROM GOOGLE DRIVE ###

def download_dataset_from_drive(file_id, output_directory):
    """
    Télécharge un fichier ZIP depuis Google Drive et le décompresse.
    
    Args:
        file_id (str): L'ID du fichier Google Drive
        output_directory (str): Répertoire de destination pour le téléchargement et la décompression
    
    Returns:
        str: Chemin du fichier ZIP téléchargé
    """
    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_directory, exist_ok=True)

    # Construire l'URL de téléchargement
    url = f'https://drive.google.com/uc?id={file_id}'

    # Chemin de sortie pour le fichier ZIP
    output_zip = os.path.join(output_directory, 'dataset.zip')

    try:
        # Télécharger le fichier
        logging.info(f"Téléchargement du fichier depuis : {url}")
        gdown.download(url, output_zip, quiet=False)

        # Décompresser le fichier
        logging.info(f"Décompression du fichier dans : {output_directory}")
        with zipfile.ZipFile(output_zip, 'r') as zip_ref:
            zip_ref.extractall(output_directory)

        # Supprimer le fichier ZIP après décompression (optionnel)
        os.remove(output_zip)

        logging.info("Téléchargement et décompression terminés avec succès.")
        return output_zip

    except Exception as e:
        logging.error(
            f"Erreur lors du téléchargement ou de la décompression : {e}")
        return None



