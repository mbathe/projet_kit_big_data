import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
from process.nutrition_preprocess import load_data, clean_data
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from sklearn.cluster import KMeans
import logging
from typing import Tuple, Optional
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class NutritionPage:
    """
    Classe représentant une page d'analyse nutritionnelle d'un jeu de données sur les recettes. 
    Elle inclut des méthodes pour charger, nettoyer, analyser et afficher des informations sur les recettes.
    """

    def __init__(self, data_directory: str):
        """
        Initialise la classe NutritionPage avec le répertoire des données.

        Parameters:
            data_directory (str): Le chemin vers le répertoire contenant les données à charger.
        """
        self.data_directory = data_directory
        self.nutrition_df = None
        self.clean_nutrition_df = None

    def load_and_clean_data(self) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Charge et nettoie les données nutritionnelles. 
        Utilise les fonctions `load_data` et `clean_data` pour charger et nettoyer les données respectivement.

        Returns:
            Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]: Un tuple contenant les données brutes et nettoyées.
        """
        self.nutrition_df = load_data()
        self.clean_nutrition_df = clean_data(self.nutrition_df)
        return self.nutrition_df, self.clean_nutrition_df

    def display_context(self) -> None:
        """
        Affiche le contexte et la description du jeu de données ainsi que la distribution des valeurs nutritionnelles.
        Présente également des informations sur le nettoyage du jeu de données et les valeurs extrêmes à ignorer.
        """

        st.title("Contexte")
        st.write("Dans cette partie, nous allons nous concentrer sur les valeurs nutritionnelles des recettes. Nous chercherons en particulier à déterminer l'influence des différentes valeurs nutritionnelles sur la popularité d'une recette.")

        st.title('Description du jeu de données global')
        st.write('Notre jeu de données fusionne la table des valeurs nutritionnelles des recettes avec celle des notes attribuées par les utilisateurs :')

        desc_df = self.nutrition_df.describe()
        nan_count = self.nutrition_df.isna().sum()
        desc_df.loc['NaN Count'] = nan_count

        st.dataframe(desc_df, use_container_width=True)
        st.write("Nous avons deux moyens de déterminer la popularité d'une recette : le nombre de notes et la moyenne des notes.")
        st.write("Nous avons sept valeurs nutritionnelles différentes : les calories (en calories) et six différents apports journaliers (en %PDV).")

        st.write("""Le %PDV indique quel pourcentage de la valeur quotidienne recommandée d'un nutriment est fourni par une portion d'un aliment spécifique.""")
        st.write(
            """Par exemple Sodium 30%PDV indique que la recette fournit 30% des apports journaliers en sel.""")

        columns = ['Calories', 'Graisses', 'Sucre', 'Sodium',
                   'Protéines', 'Graisse_saturées', 'Glucides']

        fig, axes = plt.subplots(nrows=1, ncols=7, figsize=(20, 10))
        axes = axes.flatten()

        for i, col in enumerate(columns):
            sns.boxplot(data=self.nutrition_df, y=col, ax=axes[i])
            axes[i].set_title(f'Boxplot de {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Value')

        plt.suptitle(
            'Distribution des valeurs nutritionnelles par recette', fontsize=16)
        plt.subplots_adjust(top=0.9)
        plt.tight_layout()
        st.pyplot(fig)
        st.write('Notre dataset ne possède pas de valeurs nulles (NaN), cependant il possède énormément de valeurs extrêmes.')
        st.write("Notamment, certaines recettes n'ont aucun sens avec plus de 400 000 calories et plus de 360 000% des apports journaliers en sucre.")
        st.dataframe(self.nutrition_df[self.nutrition_df.Calories >
                     400000], use_container_width=True, hide_index=True)

        st.markdown(
            "### Dans la suite de notre étude, pour nettoyer notre jeu de données, nous allons ignorer :")
        ma_liste = [
            "Les recettes qui ont été notées moins de 5 fois. On évite ainsi le biais de notation des recettes notées une seule fois.",
            "Les recettes qui font plus de 800 calories. On ne notera pas les alcools et les recettes aberrantes.",
            "Les recettes dont les apports journaliers en nutrition sont supérieurs à 100%."
        ]
        for entree in ma_liste:
            st.markdown(f"- {entree}")

        st.title('Description du jeu de données nettoyé')
        st.dataframe(self.clean_nutrition_df.describe(),
                     use_container_width=True)

        fig, axes = plt.subplots(nrows=1, ncols=7, figsize=(20, 10))
        axes = axes.flatten()

        for i, col in enumerate(columns):
            sns.boxplot(data=self.clean_nutrition_df, y=col, ax=axes[i])
            axes[i].set_title(f'Boxplot de {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Value')

        plt.suptitle(
            'Distribution des valeurs nutritionnelles par recette', fontsize=16)
        plt.subplots_adjust(top=0.9)
        plt.tight_layout()
        st.pyplot(fig)

        st.write('Nous avons ignoré beaucoup de données lors du nettoyage de notre jeu de données mais nous avons obtenu une répartition utilisable des données.')

    def display_nutrition_analysis(self) -> None:
        """
        Affiche une analyse des valeurs nutritionnelles dans les données nettoyées.
        Cela comprend des histogrammes des différentes valeurs nutritionnelles, une matrice des corrélations et des scatterplots par rapport aux notes.
        """
        st.title('Analyse des valeurs nutritionnelles')

        st.subheader('Première approche')

        st.write(
            'Commençons par observer la façon dont les données sont réparties dans nos différentes catégories :')

        # Histogrammes des valeurs nutritionnelles

        fig, axes = plt.subplots(2, 4, figsize=(20, 10))

        sns.histplot(
            self.clean_nutrition_df['Calories'], kde=True, ax=axes[0, 0])
        sns.histplot(
            self.clean_nutrition_df['Graisses'], kde=True, ax=axes[0, 1])
        sns.histplot(
            self.clean_nutrition_df['Sodium'], kde=True, ax=axes[0, 2])
        sns.histplot(
            self.clean_nutrition_df['Glucides'], kde=True, ax=axes[0, 3])

        sns.histplot(
            self.clean_nutrition_df['Protéines'], kde=True, ax=axes[1, 0])
        sns.histplot(self.clean_nutrition_df['Sucre'], kde=True, ax=axes[1, 1])
        sns.histplot(
            self.clean_nutrition_df['Graisse_saturées'], kde=True, ax=axes[1, 2])
        axes[1, 3].axis('off')  # Cache le dernier subplot

        st.pyplot(plt)

        st.write(
            """On observe que les calories suivent quasiment une distribution normale, avec un léger décalage à droite. 
            En revanche les autres catégories semblent plutôt suivre une distribution exponentielle, 
            ce qui s'explique par le fait que ce sont des pourcentages.""")

        # Matrice des corrélations

        st.subheader('Première approche')

        correlation_matrix = self.clean_nutrition_df[['Moyenne des notes', 'Nombre de notes', 'Calories', 'Graisses',
                                                      'Protéines', 'Glucides', 'Sucre', 'Sodium']].corr()

        left, middle, right = st.columns((2, 5, 2))
        with middle:
            plt.figure(figsize=(7, 7))
            sns.heatmap(correlation_matrix, annot=True,
                        cmap='coolwarm', fmt='.2f', linewidths=0.5)
            plt.title("Matrice des Corrélations")
            st.pyplot(plt)

        st.write(
            """La matrice des corrélations nous indique clairement qu'aucune des valeurs nutritionnelle n'est corrélée avec le nombre de notes reçues ou avec la moyenne des notes reçues.""")

        st.write(
            """Cependant cette matrice analyse uniquement les corrélations linéaires entre les différentes données.""")

        st.write(
            """A noter que certaines valeurs nutritionnelles sont fortement corrélées entre elles, ce qui est normal car elles résultent les une des autres. Par example les calories sont la somme des protéines, des graisses et des glucides.""")

        # Scatterplot des valeurs nutritionnelles en fonction de la valeur des notes

        st.subheader('Analyse des nutriments par rapport au nombre de notes')

        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        axes = axes.flatten()

        sns.scatterplot(x='Graisses', y='Moyenne des notes',
                        data=self.clean_nutrition_df, ax=axes[0])
        axes[0].set_title('Graisses vs Nombre de notes')

        sns.scatterplot(x='Calories', y='Moyenne des notes',
                        data=self.clean_nutrition_df, ax=axes[1])
        axes[1].set_title('Calories vs Nombre de notes')

        sns.scatterplot(x='Sodium', y='Moyenne des notes',
                        data=self.clean_nutrition_df, ax=axes[2])
        axes[2].set_title('Sodium vs Nombre de notes')

        sns.scatterplot(x='Glucides', y='Moyenne des notes',
                        data=self.clean_nutrition_df, ax=axes[3])
        axes[3].set_title('Glucides vs Nombre de notes')

        sns.scatterplot(x='Protéines', y='Moyenne des notes',
                        data=self.clean_nutrition_df, ax=axes[4])
        axes[4].set_title('Protéines vs Nombre de notes')

        sns.scatterplot(x='Sucre', y='Moyenne des notes',
                        data=self.clean_nutrition_df, ax=axes[5])
        axes[5].set_title('Sucre vs Nombre de notes')

        sns.scatterplot(x='Graisse_saturées', y='Moyenne des notes',
                        data=self.clean_nutrition_df, ax=axes[6])
        axes[6].set_title('Graisse saturées vs Nombre de notes')

        axes[7].axis('off')  # Cache le dernier subplot
        plt.tight_layout()
        st.pyplot(fig)

        st.write(
            """Malgré les résultats de la matrice précédente, on observe une certaine corrélation entre les différentes valeurs nutritionnelles et la note moyenne des recettes.""")

        st.write(
            """Notamment, les recettes fortes en graisse, en sodium et en glucides sont en général mieux notées.""")

        st.subheader('Analyse en clustering')

        st.write(
            """Nous allons essayer de déterminer si il existe des clusters de données dépendant de la moyenne des notes.
            """)

        left, middle, right = st.columns((2, 5, 2))
        with left:
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write(
                """Le graphique montre la méthode du "coude", où nous cherchons le nombre de clusters à partir du point où l'inertie cesse de baisser rapidement.
            Le "coude" est souvent un bon indicateur du nombre optimal de clusters.
            """)
        with middle:
            st.subheader(
                'Méthode du coude pour déterminer le nombre de clusters')

            # Sélectionner les colonnes pour le clustering
            features = ['Moyenne des notes', 'Calories', 'Graisses', 'Protéines',
                        'Glucides', 'Sucre', 'Sodium', 'Graisse_saturées']
            df_clustering = self.clean_nutrition_df[features]

            # Calculer l'inertie pour différents nombres de clusters
            inertias = []
            max_clusters = 10
            for k in range(1, max_clusters + 1):
                kmeans = KMeans(n_clusters=k, random_state=42)
                kmeans.fit(df_clustering)
                inertias.append(kmeans.inertia_)

            # Tracer le graphique du "coudé"
            plt.figure(figsize=(8, 6))
            plt.plot(range(1, max_clusters + 1),
                     inertias, marker='o', linestyle='--')
            plt.title('Méthode du coude')
            plt.xlabel('Nombre de clusters')
            plt.ylabel('Inertie (WSS)')
            plt.xticks(range(1, max_clusters + 1))
            plt.grid(True)
            st.pyplot(plt)
        with right:
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write(
                """On observe sur le graphique adjacent que le nombre optimal de clusters pour notre jeu de données est de 3.""")
            st.write("""Vous pouvez cependant sélectionner une autre valeur pour déterminer par vous même l'impact de la sélection du nombre de clusters.""")

        cluster_value = st.slider(
            "Choisissez un nombre de clusters :", 2, 10, 3)

        # Sélectionner les colonnes pour le clustering

        features = ['Moyenne des notes', 'Graisses', 'Protéines',
                    'Glucides', 'Sucre', 'Sodium', 'Graisse_saturées', 'Calories']
        df_clustering = self.clean_nutrition_df[features]

        # Appliquer K-Means
        kmeans = KMeans(n_clusters=cluster_value, random_state=42)
        self.clean_nutrition_df['Cluster'] = kmeans.fit_predict(df_clustering)

        # Affichage des résultats du clustering
        st.write(f"Nombre de clusters créés : {
                 len(self.clean_nutrition_df['Cluster'].unique())}")

        # Visualisation des clusters en 2D

        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        axes = axes.flatten()

        sns.scatterplot(x='Graisses', y='Moyenne des notes', hue='Cluster',
                        palette='viridis',
                        data=self.clean_nutrition_df, ax=axes[0])
        axes[0].set_title('Graisses vs Nombre de notes')

        sns.scatterplot(x='Calories', y='Moyenne des notes', hue='Cluster',
                        palette='viridis',
                        data=self.clean_nutrition_df, ax=axes[1])
        axes[1].set_title('Calories vs Nombre de notes')

        sns.scatterplot(x='Sodium', y='Moyenne des notes', hue='Cluster',
                        palette='viridis',
                        data=self.clean_nutrition_df, ax=axes[2])
        axes[2].set_title('Sodium vs Nombre de notes')

        sns.scatterplot(x='Glucides', y='Moyenne des notes', hue='Cluster',
                        palette='viridis',
                        data=self.clean_nutrition_df, ax=axes[3])
        axes[3].set_title('Glucides vs Nombre de notes')

        sns.scatterplot(x='Protéines', y='Moyenne des notes', hue='Cluster',
                        palette='viridis',
                        data=self.clean_nutrition_df, ax=axes[4])
        axes[4].set_title('Protéines vs Nombre de notes')

        sns.scatterplot(x='Sucre', y='Moyenne des notes', hue='Cluster',
                        palette='viridis',
                        data=self.clean_nutrition_df, ax=axes[5])
        axes[5].set_title('Sucre vs Nombre de notes')

        sns.scatterplot(x='Graisse_saturées', y='Moyenne des notes', hue='Cluster',
                        palette='viridis',
                        data=self.clean_nutrition_df, ax=axes[6])
        axes[6].set_title('Graisse saturées vs Nombre de notes')

        axes[7].axis('off')  # Cache le dernier subplot
        plt.tight_layout()
        st.pyplot(fig)

        st.write(
            """Les clusters montrent comment les recettes se regroupent selon des valeurs nutritionnelles similaires. 
            On observe que nos clusters dépendent énormément de la catégorie calories. En effet, cette catégorie est celle qui est la plus corrélée aux autres, en étant la somme des valeurs de graisses, protéines et glucides.""")
        st.write(
            """De même, on observe bien que certaines valeurs nutritionnelles montrent des semblants de clusters, même si ils sont moins marqués que ceux de la catégorie calorie.""")
        st.write(
            """En revanche, les clusters ne dépendent pas du tout de la valeur de la moyenne des notes, et ce quelque soit le nombre de clusters choisit.""")
        st.write(
            """On en conclut que la valeur des notes des recettes n'est définitivement pas corrélée aux valeurs nutritionnelles.""")

    def display_filtered_recipes(self) -> None:
        """
        Affiche un tableau de recettes filtrées en fonction du régime alimentaire sélectionné et permet d'explorer les détails des recettes.

        Cette fonction permet à l'utilisateur de choisir un régime alimentaire parmi trois options : "Low-Carb", "High-Protein" et "Low-Fat". 
        En fonction du régime sélectionné, elle filtre les recettes et affiche un espace interactif avec des informations sur chaque recette, telles que les notes, 
        les valeurs nutritionnelles, etc. L'utilisateur peut également sélectionner une recette pour en afficher les détails, y compris des graphiques sur la composition des calories 
        et des nutriments."""

        st.title("Recherche de recette par régime alimentaire.")
        st.subheader("Cette partie vous offre l'occasion de rechercher vous même des recettes qui pourraient vous intéresser en fonction du régime que vous souhaitez suivre.")

        # Logging du début de la fonction
        logger.info(
            "Affichage de la recherche de recettes par régime alimentaire")

        regimes = ["Low-Carb", "High-Protein", "Low-Fat"]
        selected_regime = st.selectbox("Choisissez un régime", regimes)

        logger.info(f"Régime sélectionné : {selected_regime}")

        # Ajouter des descriptions pour chaque régime
        regime_descriptions = {
            "Low-Carb": "Le régime Low-Carb limite la consommation de glucides, ce qui pousse le corps à utiliser les graisses comme source principale d'énergie.",
            "High-Protein": "Le régime High-Protein se concentre sur un apport élevé en protéines, favorisant la construction musculaire et la perte de poids.",
            "Low-Fat": "Le régime Low-Fat réduit la consommation de graisses, ce qui peut aider à la gestion du poids et à la santé cardiovasculaire."
        }

        # Afficher la description du régime sélectionné
        st.write(f"### Description du régime **{selected_regime}**:")
        st.write(regime_descriptions[selected_regime])

        def filter_recipes(regime) -> None:
            logger.info(f"Filtrage des recettes pour le régime {regime}")
            if regime == "Low-Carb":
                return self.clean_nutrition_df[self.clean_nutrition_df['Glucides'] <= 3]
            elif regime == "High-Protein":
                return self.clean_nutrition_df[self.clean_nutrition_df['Protéines'] >= 75]
            elif regime == "Low-Fat":
                return self.clean_nutrition_df[self.clean_nutrition_df['Graisses'] <= 3]
            else:
                return self.clean_nutrition_df

        filtered_df = filter_recipes(selected_regime)

        # Vérification si des recettes ont été trouvées
        if not filtered_df.empty:
            st.write(
                f"Recettes correspondant au régime **{selected_regime}**:")
            logger.info(f"{len(filtered_df)} recettes trouvées pour le régime {
                        selected_regime}")

            # Configuration de la grille pour afficher les recettes
            grid_options = GridOptionsBuilder.from_dataframe(filtered_df[['name', 'Moyenne des notes', 'Nombre de notes', 'Calories',
                                                                          'Graisse_saturées', 'Graisses', 'Protéines', 'Glucides', 'Sucre', 'Sodium']])
            grid_options.configure_selection('single', use_checkbox=True)
            grid_options.configure_pagination(paginationPageSize=10)
            grid_options.configure_column(
                'name', headerCheckboxSelection=True, autoSizeColumns=True)

            # Affichage de la grille avec les recettes filtrées
            grid_response = AgGrid(
                filtered_df, gridOptions=grid_options.build(), enable_enterprise_modules=True)

            try:
                recette_info = grid_response['selected_rows'].iloc[0]
                logger.info(f"Recette sélectionnée : {recette_info['name']}")
            except AttributeError:
                st.write(
                    "Sélectionnez une recette pour en afficher les caractéristiques.")
                logger.warning("Aucune recette sélectionnée")
                return

            st.write(f"### Détails pour la recette : {recette_info['name']}")
            st.text(f"""Recette notée {recette_info['Nombre de notes']} fois avec une moyenne de {
                    recette_info['Moyenne des notes']} sur 5""")

            # Diagramme circulaire pour la composition des calories
            Calories_line = recette_info[['Graisses', 'Protéines', 'Glucides']]
            fig1 = go.Figure(data=[go.Pie(labels=Calories_line.index, values=Calories_line,
                                          hoverinfo='label+percent', textinfo='label+percent', hole=0.3)])

            fig1.update_layout(title=f"Diagramme de composition des calories : {
                               recette_info['Calories']} calories totales", title_x=0.25)

            # Diagramme en barres pour la composition des nutriments
            full_line = recette_info[[
                'Graisse_saturées', 'Graisses', 'Protéines', 'Glucides', 'Sucre', 'Sodium']]
            fig2 = go.Figure(data=[go.Bar(x=full_line.index, y=full_line,
                                          marker=dict(color=['orange', 'blue', 'green', 'red', 'purple', 'brown', 'cyan']))])

            fig2.add_shape(type="line", x0=0, y0=100, x1=6,
                           y1=100, line=dict(color="Red", width=2))
            fig2.update_layout(title=f"Composition des nutriments pour {
                               recette_info['name']}", title_x=0.1)

            # Affichage des deux graphiques côte à côte
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig1)
            with col2:
                st.plotly_chart(fig2)

        else:
            st.write(
                f"Aucune recette trouvée pour le régime **{selected_regime}**.")
            logger.info(f"Aucune recette trouvée pour le régime {
                        selected_regime}")

    def run(self) -> None:
        """
        Affiche l'interface utilisateur avec plusieurs onglets permettant de naviguer entre différentes sections de l'application.

        Cette fonction crée un interface utilisateur basée sur Streamlit avec trois onglets :
        1. **Accueil** : Affiche le contexte de l'application via la fonction `display_context`.
        2. **Analyse statistique de la popularité des différentes valeurs nutritionnelles** : Affiche une analyse des données nutritionnelles via la fonction `display_nutrition_analysis`.
        3. **Choisir la recette adaptée à son régime** : Permet à l'utilisateur de rechercher des recettes en fonction du régime alimentaire via la fonction `display_filtered_recipes`.

        Chaque onglet est associé à une fonction qui gère l'affichage de l'interface et l'interaction avec l'utilisateur. Les onglets sont présentés sous forme de navigation pour une utilisation fluide et structurée de l'application.

        La fonction ne renvoie aucune valeur et est responsable de l'organisation de l'interface utilisateur de l'application Streamlit, facilitant l'interaction avec l'utilisateur.

        Returns:
            None: Cette fonction ne retourne aucune valeur. Elle sert uniquement à organiser et afficher les différentes sections de l'application.
        """
        tabs = st.tabs(
            ["Accueil", "Analyse statistique de la popularité des différentes valeurs nutritionnelles", "Choisir la recette adaptée à son régime"])
        with tabs[0]:
            self.display_context()
        with tabs[1]:
            self.display_nutrition_analysis()
        with tabs[2]:
            self.display_filtered_recipes()


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    nutrition_page = NutritionPage(data_directory='./data')
    nutrition_page.load_and_clean_data()
    nutrition_page.run()
