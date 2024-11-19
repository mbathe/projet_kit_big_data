import kagglehub
import os
import shutil


def download_dataset():
    print("Downloading dataset...")
    path = kagglehub.dataset_download(
        "shuyangli94/food-com-recipes-and-user-interactions")
    print("Path to dataset files:", path)
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
            print(f"Le dossier de destination '{
                  chemin_destination}' a été créé.")

        # Liste tous les fichiers dans le dossier source
        for fichier in os.listdir(chemin_source):
            chemin_fichier = os.path.join(chemin_source, fichier)

            # Vérifie que c'est un fichier avant de le déplacer
            if os.path.isfile(chemin_fichier):
                shutil.move(chemin_fichier, chemin_destination)
                print(f"Le fichier '{fichier}' a été déplacé vers '{
                      chemin_destination}'.")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")


if __name__ == "__main__":
    path = download_dataset()
    chemin_destination = 'data'
    deplacer_fichiers(path, chemin_destination)
