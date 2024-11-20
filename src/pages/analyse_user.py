from src.visualizations.graphiques import LineChart , Histogramme
from src.visualizations import Grille, load_css

from pathlib import Path

import streamlit as st
import pandas as pd


if __name__ == "__main__":
    # Configuration de la page pour une largeur maximale
    st.set_page_config(layout="wide")

############################
############################
####  fonctions de base ####
############################
############################

@st.cache_data
def load_large_csv(file_path):
    return pd.read_csv(file_path)



#####################
#####################
####  Load CSS  #####
#####################
#####################

path_to_css = 'src/css_pages/analyse_user.css'
load_css(path_to_css)


######################################
###################################### 
####  Chargement d'un dataframe  #####
######################################
######################################

st.title("Chargement d'un dataframe")

# Liste des fichiers disponibles dans le dossier "data"
data_dir = Path("data")
csv_files = list(data_dir.glob("*.csv"))

if csv_files:
    file_selected = st.selectbox("Sélectionnez un fichier CSV à analyser :", csv_files)
    if file_selected:
        st.write(f"Chargement du fichier : `{file_selected}`")

        # Charger le fichier sélectionné
        data = load_large_csv(file_selected)

        # Afficher un échantillon des données
        st.write("Aperçu des données :", data.head())

        # traitement de data :
        if 'date' in data.columns :
            data['date'] = pd.to_datetime(data['date'])
            data['year'] = data['date'].dt.year.astype(str)
        
        if 'rating' in data.columns :
            unique_ratings = data['rating'].unique()
else:
    st.warning("Aucun fichier CSV trouvé dans le dossier `data`.")


#########################################
#########################################
##  Analyse des notes par utilisateur  ##
#########################################
#########################################

st.title("Analyse des notes par utilisateur")

if 'user_id' in data.columns:
    # Sélection d'un utilisateur pour l'analyse
    user_id = st.number_input("Entrez l'ID utilisateur à analyser :", min_value=0)

    user_data = data[data['user_id'] == user_id]

    if not user_data.empty:
        st.success(f"Données trouvées pour l'utilisateur {user_id} !")
        
        if 'date' in user_data.columns and 'rating' in user_data.columns:
            user_data.loc[:, 'year_month'] = user_data['date'].dt.to_period('M')
            monthly_avg = user_data.groupby('year_month')['rating'].mean()
            monthly_avg.index = monthly_avg.index.astype(str) 

            # Conversion du DataFrame pour LineChart
            chart_data = monthly_avg.reset_index()
            chart_data.columns = ['Mois', 'Note moyenne']

            st.subheader("Aperçu des notes utilisateur au fil du temps")
            line_chart = LineChart(data=chart_data, x='Mois', y='Note moyenne', height=400, line_color='rgb(26, 28, 35)')
            graphiques = [{
                "titre": f"",
                "graphique": line_chart,
            }]

            grille = Grille(nb_lignes= 1, nb_colonnes= 1, largeurs_colonnes= [1])
            grille.afficher(graphiques)
        else:
            st.warning("Les colonnes nécessaires ('date', 'rating') sont absentes du fichier.")
    else:
        st.error(f"Aucune donnée trouvée pour l'utilisateur {user_id}.")
else:
    st.error("La colonne 'user_id' est absente du fichier.")


##############################################
##############################################
##  Analyse sur les note moyenne mensuelle  ##
##############################################
##############################################


# Interface principale Streamlit
st.title("Analyse notes moyennes mensuelle")

 # Vérification des colonnes nécessaires
if ('date' in data.columns) and ('rating' in data.columns):
    
    # Calcul de la moyenne mensuelle des notes
    monthly_average_rating = data.set_index('date').resample('ME')['rating'].mean().reset_index()

    # Préparation des données pour LineChart
    monthly_average_rating.columns = ['Mois', 'Note moyenne']

    st.subheader("Notation moyenne hebdomadaire au fil du temps")
    line_chart = LineChart(data=monthly_average_rating, x='Mois', y='Note moyenne', height=400,line_color='rgb(26, 28, 35)')
    graphiques = [{
        "titre": f"",
        "graphique": line_chart,
    }]

    grille = Grille(nb_lignes= 1, nb_colonnes= 1, largeurs_colonnes= [1])
    grille.afficher(graphiques)   
else :
    st.warning("Les colonnes 'date' et 'rating' sont nécessaires pour cette analyse.")
    


######################################
###################################### 
####     Analyse de Frequences   #####
######################################
######################################

st.title("Analyse de Fréquences")

##-------------------------------------------
# Frequence globale des notes 
##-------------------------------------------

# Interface principale Streamlit
st.subheader("Fréquence globale des notes")

if 'rating' in data.columns:
    histogram = Histogramme(
        data=data,
        x='rating',
        bin_size=1,
        height=400,
        bar_color='rgb(26, 28, 35)',
    )

    graphiques = [{
        "titre": f"",
        "graphique": histogram,
    }]

    grille = Grille(nb_lignes= 1, nb_colonnes= 1, largeurs_colonnes= [1])
    grille.afficher(graphiques)
else:
    st.warning("La colonne 'rating' est absente du fichier.")

##-------------------------------------------
# Frequence des notes au fil du temps
##-------------------------------------------

st.subheader("Frequence des Notes au fil du temps")

if ('date' in data.columns) and ('rating' in data.columns):

    graphiques = []
    for idx, rating in enumerate(sorted(unique_ratings)):

        rating_data = data[data['rating'] == rating]

        # Création du graphique pour cette note
        histogram = Histogramme(
            data=rating_data,
            bin_size = 1,
            x='year',
            height=300,
            bar_color='rgb(26, 28, 35)',
            line_color='rgb(8,48,107)'
        )
        graphiques.append({
            "titre": f"Fréquence de la note {int(rating)}",
            "graphique": histogram,
        })

    grille = Grille(nb_lignes = 2, nb_colonnes = 3, largeurs_colonnes = [1,1,1]) # largeurs_colonnes = [1] * nb_colonnes  
    grille.afficher(graphiques)
else :
    st.warning("Les colonnes 'date' et 'rating' sont nécessaires pour cette analyse.")

##-------------------------------------------
# Frequence des notes par users
##-------------------------------------------

st.subheader("Fréquence des Notes par User au fil du temps")

if 'user_id' in data.columns:
    # Sélection d'un utilisateur pour l'analyse
    user_id_ = st.number_input("Entrez l'ID utilisateur à analyser :", min_value=0, key=2)

    user_data = data[data['user_id'] == user_id_]

    if not user_data.empty:
        st.success(f"Données trouvées pour l'utilisateur {user_id_} !")
        
        # Analyse des données utilisateur (par exemple, moyenne des notes mensuelles)
        if 'date' in user_data.columns and 'rating' in user_data.columns:

            graphiques = []
            unique_ratings_user = user_data['rating'].unique()
            for idx, rating in enumerate(sorted(unique_ratings_user)):

                rating_data = user_data[data['rating'] == rating]

                histogram = Histogramme(
                    data=rating_data,
                    bin_size = 1,
                    x='year',
                    height=300,
                    bar_color='rgb(26, 28, 35)',
                    line_color='rgb(8,48,107)'
                )
                graphiques.append({
                    "titre": f"Fréquence de la note {int(rating)}",
                    "graphique": histogram,
                })

            grille = Grille(nb_lignes = 2, nb_colonnes = 3, largeurs_colonnes = [1,1,1])
            grille.afficher(graphiques)
                    
        else:
            st.warning("Les colonnes nécessaires ('date', 'rating') sont absentes du fichier.")
    else:
        st.error(f"Aucune donnée trouvée pour l'utilisateur {user_id_}.")
else:
    st.error("La colonne 'user_id' est absente du fichier.")

