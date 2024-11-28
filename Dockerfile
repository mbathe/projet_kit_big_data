# Utiliser l'image officielle de Python 3.12
FROM python:3.12-slim

# Installer les dépendances système nécessaires
RUN apt-get update && \
    apt-get install -y graphviz nano libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Installer Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Vérifier que Poetry est installé
RUN poetry --version

# Ajouter Poetry au PATH
ENV PATH="/root/.local/bin:$PATH"


# Exposer le port par défaut pour Streamlit
EXPOSE 8501

# Créer le répertoire de l'application
WORKDIR /streamlit-docker

# Copier les fichiers de configuration de Poetry
COPY pyproject.toml poetry.lock ./

# Installer les dépendances avec Poetry
RUN poetry install --no-root

# Copier tous les fichiers de l'application
COPY . .

ENV PYTHONPATH="/streamlit-docker/src:$PYTHONPATH"

# Commande pour lancer l'application lorsque le conteneur est exécuté
CMD ["sh", "-c", "poetry run streamlit run ./src/main.py"]

# Configurer les commandes spécifiques à Streamlit
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
    [general]\n\
    email = \"\"\n\
    " > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
    [server]\n\
    enableCORS = false\n\
    " > /root/.streamlit/config.toml'
