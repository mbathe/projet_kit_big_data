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


### DOWNLOAD FROM KAGGLE ###
def download_dataset_from_kaggle() -> str:
    """
    Télécharge un dataset spécifique depuis Kaggle.

    Cette fonction utilise `kagglehub` pour télécharger le dataset identifié par 
    "shuyangli94/food-com-recipes-and-user-interactions". Elle affiche un message indiquant 
    le début du téléchargement et retourne le chemin vers le fichier téléchargé.

    Args:
        None

    Returns:
        str: Chemin vers le fichier téléchargé.

    Raises:
        Exception: Si le téléchargement échoue pour une raison quelconque.

    Logs :
        INFO: Indique le début du téléchargement du dataset.
        INFO: Indique la fin du téléchargement avec le chemin du fichier.
        ERROR: Indique une erreur survenue lors du téléchargement.
    """
    logging.info("Downloading dataset...")
    try:
        path = kagglehub.dataset_download("shuyangli94/food-com-recipes-and-user-interactions")
        logging.info(f"Dataset téléchargé et sauvegardé à : {path}")
        return path
    except Exception as e:
        logging.error(f"Erreur lors du téléchargement du dataset : {e}")
        raise

def deplacer_fichiers(chemin_source: str, chemin_destination: str):
    """
    Déplace tous les fichiers du dossier `chemin_source` vers `chemin_destination`.

    Cette fonction vérifie si le chemin de destination existe. Si ce n'est pas le cas, elle crée 
    le dossier de destination. Ensuite, elle déplace tous les fichiers du dossier source 
    vers le dossier de destination. En cas d'erreur lors du déplacement, un message d'erreur 
    est enregistré dans les logs.

    Args:
        chemin_source (str): Chemin du dossier source contenant les fichiers à déplacer.
        chemin_destination (str): Chemin du dossier de destination où les fichiers seront déplacés.

    Returns:
        None

    Raises:
        Exception: Si une erreur survient lors du déplacement des fichiers.

    Logs :
        INFO: Indique la création du dossier de destination s'il n'existe pas.
        INFO: Indique le déplacement réussi de chaque fichier.
        ERROR: Indique une erreur survenue lors du déplacement des fichiers.
    """
    try:
        # Vérifie si le chemin de destination existe, sinon le crée
        if not os.path.exists(chemin_destination):
            os.makedirs(chemin_destination)
            logging.info(f"Le dossier de destination '{chemin_destination}' a été créé.")

        # Liste tous les fichiers dans le dossier source
        for fichier in os.listdir(chemin_source):
            chemin_fichier = os.path.join(chemin_source, fichier)

            # Vérifie que c'est un fichier avant de le déplacer
            if os.path.isfile(chemin_fichier):
                shutil.move(chemin_fichier, chemin_destination)
                logging.info(f"Le fichier '{fichier}' a été déplacé vers '{chemin_destination}'.")
    except Exception as e:
        logging.error(f"Une erreur s'est produite lors du déplacement des fichiers : {e}")
        raise

def download_dataset():
    """
    Télécharge le dataset depuis Kaggle et déplace les fichiers vers le répertoire de destination.

    Cette fonction vérifie d'abord si le répertoire de destination existe déjà. Si c'est le cas,
    elle enregistre une erreur indiquant que le dataset a déjà été chargé. Sinon, elle télécharge
    le dataset, déplace les fichiers vers le répertoire de destination, et supprime le dossier
    temporaire utilisé pour le téléchargement.

    Args:
        None

    Returns:
        None

    Raises:
        Exception: Si une erreur survient lors du téléchargement ou du déplacement des fichiers.

    Logs :
        ERROR: Indique que le dataset est déjà chargé.
        INFO: Indique le début du processus de téléchargement et de déplacement.
        ERROR: Indique une erreur survenue lors du téléchargement ou du déplacement.
        INFO: Indique la suppression réussie du dossier temporaire.
    """
    path_to_data = os.path.join('data')
    if os.path.exists(path_to_data):
        logging.error(f"Le dataset est déjà chargé dans '{path_to_data}'.")
    else:
        try:
            logging.info("Début du téléchargement du dataset.")
            # Télécharger le dataset depuis Kaggle
            path = download_dataset_from_kaggle()
            
            # Déplacer les fichiers téléchargés vers le répertoire de destination
            deplacer_fichiers(path, path_to_data)
            
            # Supprimer le dossier temporaire de téléchargement s'il est vide
            if os.path.isdir(path) and not os.listdir(path):
                os.rmdir(path)
                logging.info(f"Le dossier temporaire '{path}' a été supprimé.")
        except Exception as e:
            logging.error(f"Une erreur s'est produite lors du téléchargement du dataset : {e}")
            raise


if __name__ == "__main__":
    download_dataset()
    

