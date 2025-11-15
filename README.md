# Application Web d'Analyse de Recettes avec Streamlit

## Objectif du Projet

Ce projet vise à développer une application web interactive utilisant Streamlit pour l'analyse approfondie de données culinaires. L'application met en pratique les compétences avancées en développement Python, analyse de données, et développement web.


## Fonctionnalités Principales

### Analyse de Recettes
- Statistiques nutritionnelles détaillées
- Visualisation des tendances culinaires
- Analyse comparative des ingrédients
- Système de recommandation personnalisé basé sur les préférences

### Interactions Utilisateurs
- Analyse des contributions des utilisateurs
- Exploration des distributions des interactions
- Visualisations interactives des données


## Prérequis

Avant d'exécuter le code, assurez-vous que les éléments suivants sont installés et configurés :

Les variables d'environnement se trouvent dans le fichier `.env`

- **Python 3.11** ou supérieur
- **Poetry** pour la gestion des dépendances. [Installer Poetry](https://python-poetry.org/docs/#installation)
- **Docker** (optionnel, pour le déploiement local) : [Installer Docker](https://docs.docker.com/engine/install/)
- **Compte MongoDB Atlas ou base de données MongoDB**(optionnel, pour ligne ou en local à partie de mongodb) : [Installer MongoDB](https://www.mongodb.com/docs/manual/installation/)


## Modes de Déploiement

### 1. Déploiement Local (Développement)

#### Étape 1 : Cloner le dépôt
```bash
git clone https://github.com/mbathe/projet_kit_big_data.git
cd projet_kit_big_data
```

#### Étape 2 : Installer les dépendances
```bash
poetry install
```
#### Étape 3 : Activer l'environnement
```bash
poetry shell
```

#### Étape 4 : Télécharger le dataset
Exécutez l'instruction suivante à la racine du projet pour télécharger le dataset et l'enregistrer à l'emplacement par défaut `./data/dataset/` (défini par la variable d'environnement **DOCKER_DOWNLOAD_DATASET_DIR**). Vous pouvez modifier cet emplacement en modifiant la valeur de cette variable.

```bash
poetry run python script.py
```

#### Étape 5 : Lancer l'application
À la racine du répertoire du projet, exécutez la commande suivante :
```bash
streamlit run src/Recettes.py
```

### 2. Déploiement Local (Docker)

#### Étape 1 : Cloner le dépôt
```bash
git clone https://github.com/mbathe/projet_kit_big_data.git
cd projet_kit_big_data
```

#### Étape 2 : Construire l'image Docker
```bash
docker build -t projet_kig_big_data .
```

#### Étape 3 : Lancer l'application
À la racine du répertoire du projet, exécutez la commande suivante :
```bash
docker run -d --name projet_big_data1 --memory="2g" -p 8501:8501 projet_kig_big_data
```

### 3. Déploiement de l'application avec une base de données MongoDB (local ou Atlas)

#### Étape 1 : Cloner le dépôt
```bash
git clone https://github.com/mbathe/projet_kit_big_data.git
cd projet_kit_big_data
```

#### Étape 2 : Installer les dépendances
```bash
poetry install
```

#### Étape 3 : Modifier les variables d'environnement
Avant de déployer l'application, donnez des valeurs aux variables d'environnement suivantes du fichier `.env` :
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


#### Étape 4 : Charger les données depuis les fichiers CSV vers la base de données
```bash
python scripts/mongo_data.py
```

#### Étape 5 : Lancer l'application
À la racine du répertoire du projet, exécutez la commande suivante :
```bash
streamlit run src/Recettes.py
```


##  Déploiement en Ligne

### Plateformes
- **Streamlit Cloud** : [Lien de l'application](https://tpbgdia700-w9z9mmtuyekqgmkmtkctxq.streamlit.app/)
- **VPS Local** : [http://158.178.192.72:8501/](http://158.178.192.72:8501/)

### Documentation
- **Documentation de l'application** : [https://documentation-projet-kit-big-data.readthedocs.io/en/latest/](https://documentation-projet-kit-big-data.readthedocs.io/en/latest/)


## Contributeurs

### Équipe de Développement

| Nom                       | Rôle           | Contact                            |
| ------------------------- | -------------- | ---------------------------------- |
| MBATHE MEKONTCHOU PAUL    | Data Scientist | [https://github.com/mbathe]        |
| Alexandre Desgrées du Loû | Data Scientist | [https://github.com/Alexandre-ddl] |
| Alexandre Movsessian      | Data Scientist | [https://github.com/AlexMovsess]   |
| Julian Sliva              | Data Scientist | [https://github.com/JuJuFR78]      |

