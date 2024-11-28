import os
from src.visualizations.graphiques import LineChart , Histogramme
from src.visualizations import Grille, load_css

from pathlib import Path
import streamlit as st
import pandas as pd

from dotenv import load_dotenv
load_dotenv()



class DataLoader:
    """Class responsible for loading data."""
    @staticmethod
    @st.cache_data
    def load_large_csv(file_path):
        return pd.read_csv(file_path)


class CSSLoader:
    """Class responsible for loading CSS."""
    @staticmethod
    def load(path_to_css):
        load_css(path_to_css)


class DataAnalyzer:
    """Class for analyzing the data."""
    def __init__(self, data):
        self.data = data

    def preprocess(self):
        if 'date' in self.data.columns:
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data['year'] = self.data['date'].dt.year.astype(str)
        return self.data

    def analyze_user(self, user_id):
        user_data = self.data[self.data['user_id'] == user_id]
        if not user_data.empty:
            user_data['year_month'] = user_data['date'].dt.to_period('M')
            monthly_avg = user_data.groupby('year_month')['rating'].mean()
            monthly_avg.index = monthly_avg.index.astype(str)  # Convert PeriodIndex to string
            monthly_avg = monthly_avg.reset_index()  # Convert to DataFrame
            monthly_avg.columns = ['Mois', 'Note moyenne']
            return monthly_avg
        return None

    def analyze_monthly_ratings(self):
        monthly_average_rating = self.data.set_index('date').resample('ME')['rating'].mean().reset_index()
        monthly_average_rating.columns = ['Mois', 'Note moyenne']
        return monthly_average_rating

    def analyze_ratings_frequencies(self):
        unique_ratings = self.data['rating'].unique()
        frequency_data = []
        for rating in sorted(unique_ratings):
            rating_data = self.data[self.data['rating'] == rating]
            frequency_data.append((rating, rating_data))
        return frequency_data

    def analyze_user_ratings_frequencies(self, user_id):
        user_data = self.data[self.data['user_id'] == user_id]
        if not user_data.empty:
            unique_ratings_user = user_data['rating'].unique()
            frequency_data = []
            for rating in sorted(unique_ratings_user):
                rating_data = user_data[user_data['rating'] == rating]
                frequency_data.append((rating, rating_data))
            return frequency_data
        return None


class VisualizationManager:
    """Class for managing visualizations."""
    @staticmethod
    def display_line_chart(data, x, y, title):
        st.subheader(title)
        line_chart = LineChart(data=data, x=x, y=y, height=400, line_color='rgb(26, 28, 35)')
        graphiques = [{"titre": "", "graphique": line_chart}]
        grille = Grille(nb_lignes=1, nb_colonnes=1, largeurs_colonnes=[1])
        grille.afficher(graphiques)

    @staticmethod
    def display_histogram(data, x, title, bin_size=1):
        st.subheader(title)
        histogram = Histogramme(data=data, x=x, bin_size=bin_size, height=400, bar_color='rgb(26, 28, 35)')
        graphiques = [{"titre": "", "graphique": histogram}]
        grille = Grille(nb_lignes=1, nb_colonnes=1, largeurs_colonnes=[1])
        grille.afficher(graphiques)

    @staticmethod
    def display_ratings_frequencies(frequency_data, x, title):
        st.subheader(title)
        graphiques = []
        for rating, rating_data in frequency_data:
            histogram = Histogramme(
                data=rating_data,
                bin_size=1,
                x=x,
                height=300,
                bar_color='rgb(26, 28, 35)',
                line_color='rgb(8,48,107)'
            )
            graphiques.append({
                "titre": f"Fréquence de la note {int(rating)}",
                "graphique": histogram,
            })
        grille = Grille(nb_lignes=2, nb_colonnes=3, largeurs_colonnes=[1, 1, 1])
        grille.afficher(graphiques)


class StreamlitPage:
    def __init__(self):
        self.data = None

    def load_css(self):
        path_to_css = 'src/css_pages/analyse_user.css'
        CSSLoader.load(path_to_css)




    def load_data(self):
        st.title("Chargement d'un dataframe")
        data_dir = Path(os.getenv("DIR_DATASET_2"))
        csv_files = list(data_dir.glob("*.csv"))

        if csv_files:
            file_selected = st.selectbox("Sélectionnez un fichier CSV à analyser :", csv_files)
            if file_selected:
                st.write(f"Chargement du fichier : `{file_selected}`")
                self.data = DataLoader.load_large_csv(file_selected)
                st.write("Aperçu des données :", self.data.head())
        else:
            st.warning("Aucun fichier CSV trouvé dans le dossier `data`.")

    def run_analysis(self):
        if self.data is not None:
            analyzer = DataAnalyzer(self.data)
            self.data = analyzer.preprocess()

            # Ratings frequencies
            st.title("Analyse de Fréquences")
            if 'rating' in self.data.columns:
                VisualizationManager.display_histogram(self.data, 'rating', "Fréquence globale des notes")
            else:
                st.warning("La colonne 'rating' est absente du fichier.")
            
            # Frequencies over time
            st.title("Fréquence des notes au fil du temps")
            if 'date' in self.data.columns and 'rating' in self.data.columns:
                frequency_data = analyzer.analyze_ratings_frequencies()
                VisualizationManager.display_ratings_frequencies(frequency_data, x='year', title="Fréquence des Notes au fil du temps")
            

            # Monthly average ratings
            st.title("Analyse des notes moyennes mensuelles")
            if 'rating' in self.data.columns and 'date' in self.data.columns:
                monthly_ratings = analyzer.analyze_monthly_ratings()
                VisualizationManager.display_line_chart(monthly_ratings, 'Mois', 'Note moyenne',
                                                        "Notation moyenne hebdomadaire au fil du temps")

            # User frequencies
            st.title("Fréquence des Notes par utilisateur au fil du temps")
            if 'user_id' in self.data.columns:
                user_id = st.number_input("Entrez l'ID utilisateur à analyser :", min_value=0, key=2)
                user_frequency_data = analyzer.analyze_user_ratings_frequencies(user_id)
                if user_frequency_data:
                    VisualizationManager.display_ratings_frequencies(user_frequency_data, x='year', title=f"Fréquence des Notes pour l'utilisateur {user_id}")
                else:
                    st.error(f"Aucune donnée trouvée pour l'utilisateur {user_id}.")

            # User analysis
            st.title("Analyse des notes par utilisateur")
            if 'user_id' in self.data.columns:
                user_id = st.number_input("Entrez l'ID utilisateur à analyser :", min_value=0)
                user_analysis = analyzer.analyze_user(user_id)
                if user_analysis is not None:
                    VisualizationManager.display_line_chart(user_analysis, 'Mois', 'Note moyenne',
                                                            "Aperçu des notes utilisateur au fil du temps")
                else:
                    st.error(f"Aucune donnée trouvée pour l'utilisateur {user_id}.")
            else:
                st.error("La colonne 'user_id' est absente du fichier.")


    def run(self):
        st.set_page_config(layout="wide")
        self.load_css()
        self.load_data()
        if self.data is not None:
            self.run_analysis()


if __name__ == "__main__":
    page_analyse_user = StreamlitPage()
    page_analyse_user.run()
