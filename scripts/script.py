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
        logging.FileHandler("script.log"),
        logging.StreamHandler()
    ]
)

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


def download_dataset_from_kaggle():
    print("Downloading dataset...")
    path = kagglehub.dataset_download(
        "shuyangli94/food-com-recipes-and-user-interactions")
    return path

def deplacer_fichiers(chemin_source, chemin_destination):
    """
    Déplace tous les fichiers du dossier chemin_source vers chemin_destination.
    Si chemin_destination n'existe pas, il est créé.
    """
    try:
        # Vérifie si le chemin de destination existe, sinon le crée
        if not os.path.exists(chemin_destination):
            os.makedirs(chemin_destination)
            print(f"Le dossier de destination '{chemin_destination}' a été créé.")

        # Liste tous les fichiers dans le dossier source
        for fichier in os.listdir(chemin_source):
            chemin_fichier = os.path.join(chemin_source, fichier)

            # Vérifie que c'est un fichier avant de le déplacer
            if os.path.isfile(chemin_fichier):
                shutil.move(chemin_fichier, chemin_destination)
                print(f"Le fichier '{fichier}' a été déplacé vers '{chemin_destination}'.")
    except Exception as e:
        logging.error(f"Une erreur s'est produite : {e}")

def download_dataset():
    path_to_data = os.path.join('data')
    if os.path.exists(path_to_data) : 
        logging.error(f"Deja chargé")
    else : 
        path = download_dataset_from_kaggle()
        deplacer_fichiers(path, path_to_data)
        os.rmdir(path) # Supprimer un dossier vide

if __name__ == "__main__":
    download_dataset()
    

