# Dockerfile pour le déploiement dans un conteneur 
## Utiliser une version officielle de Python comme image parente
FROM python:3.7-slim
## Définir le répertoire de travail dans le conteneur sur /app
WORKDIR /app
## Ajouter le contenu du répertoire courant dans le conteneur à /app
ADD . /app
## Installer les packages nécessaires spécifiés dans requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
## Rendre le port 80 accessible au monde extérieur à ce conteneur
EXPOSE 80
## Exécuter app.py lorsque le conteneur est lancé
CMD streamlit run --server.port 80 app.py