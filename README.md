# Création d'une webapp Streamlit d'analyse de données

## Objectif du projet
L'objectif de ce projet est de mettre en pratique les concepts et les compétences que nous avons appris en cours sur le développement Python pour la production, en créant et déployant une application web incluant une partie analyse de données.

## Fonctionnalités
- **Statistiques détaillées des recettes**
    - 📈 Analyses nutritionnelles avancées
    - 🌍 Exploration des tendances culinaires
    - ⭐ Système de recommandation personnalisé

- **Interaction des utilisateurs**
    - 📈 Analyses avancées des contributions
    - 🌍 Exploration des distributions des contributions

## Prérequis

Avant d'exécuter le code, assurez-vous que les éléments suivants sont installés et configurés :

Les variables d'environnement se trouvent dans le fichier `.env`

- Python 3.11 ou supérieur
- **Poetry** pour la gestion des dépendances. [Installer Poetry](https://python-poetry.org/docs/#installation)
- **Docker** (optionnel, pour le déploiement local) : [Installer Docker](https://docs.docker.com/engine/install/)
- **Compte MongoDB Atlas ou base de données MongoDB** : [Installer MongoDB](https://www.mongodb.com/docs/manual/installation/)

## 1. Déploiement de l'application en local en mode développement

### Étape 1 : Cloner le dépôt
```bash
git clone https://github.com/mbathe/tp_bgdia700.git
cd tp_bgdia700
```

### Étape 2 : Installer les dépendances
```bash
poetry install
```

### Étape 3 : Télécharger le dataset
Exécutez l'instruction suivante à la racine du projet pour télécharger le dataset et l'enregistrer à l'emplacement par défaut `./data/dataset/` (défini par la variable d'environnement **DIR_DATASET**). Vous pouvez modifier cet emplacement en modifiant la valeur de cette variable.

```bash
python script.py
```

### Étape 4 : Lancer l'application
À la racine du répertoire du projet, exécutez la commande suivante :
```bash
streamlit run src/👨‍🍳Recettes.py
```

## 2. Déploiement de l'application en local avec Docker

### Étape 1 : Cloner le dépôt
```bash
git clone https://github.com/mbathe/tp_bgdia700.git
cd tp_bgdia700
```

### Étape 2 : Construire l'image Docker
```bash
docker build -t projet_kig_big_data .
```

### Étape 3 : Lancer l'application
À la racine du répertoire du projet, exécutez la commande suivante :
```bash
docker run -d --name projet_big_data1 --memory="2g" -p 8501:8501 projet_kig_big_data
```

## 3. Déploiement de l'application avec une base de données MongoDB (local ou Atlas)

### Étape 1 : Cloner le dépôt
```bash
git clone https://github.com/mbathe/tp_bgdia700.git
cd tp_bgdia700
```

### Étape 2 : Modifier les variables d'environnement
Avant de déployer l'application, modifiez les variables d'environnement suivantes :
```
# CHAÎNE DE CONNEXION À LA BASE DE DONNÉES MONGODB POUR UN DÉPLOIEMENT EN LIGNE
CONNECTION_STRING = 

# NOM DE LA BASE DE DONNÉES À UTILISER
DATABASE_NAME = tp_big_data

# NOM DE LA COLLECTION POUR SAUVEGARDER LES RECETTES DANS MONGODB
COLLECTION_RECIPES_NAME = recipes

# NOM DE LA COLLECTION POUR SAUVEGARDER LES INTERACTIONS DANS MONGODB
COLLECTION_RAW_INTERACTIONS = raw_interaction
```

### Étape 3 : Charger les données depuis les fichiers CSV vers la base de données
```bash
python scripts/mongo_data.py
```

### Étape 4 : Lancer l'application
À la racine du répertoire du projet, exécutez la commande suivante :
```bash
streamlit run src/👨‍🍳Recettes.py
```

## Déploiement en ligne
- **Streamlit Cloud** : [Lien à ajouter]
- **VPS local** : [Lien à ajouter]
