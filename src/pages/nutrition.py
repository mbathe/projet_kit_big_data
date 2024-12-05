import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
import pandas as pd
import ast
import matplotlib.pyplot as plt
from pathlib import Path
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
cwd = str(Path.cwd())

st.set_page_config(
    page_title="INTERACTIONS_PAGE",
    layout="wide"
)


@st.cache_data
def load_data():
    df_RAW_recipes = pd.read_csv(cwd + '\\data\\RAW_recipes.csv')
    df_RAW_interactions = pd.read_csv(
        cwd + '\\data\\RAW_interactions.csv')

    # On ne garde que la moyenne des notes de la recette
    df_mean_rating = df_RAW_interactions[[
        'recipe_id', 'rating']].groupby(['recipe_id']).mean().round(2)
    # On ne garde que le nombre de notes de la recette
    df_count_rating = df_RAW_interactions[[
        'recipe_id', 'rating']].groupby(['recipe_id']).count()

    df_nutrition = df_RAW_recipes[['id', 'name', 'nutrition']]

    merged_df = df_nutrition.merge(df_mean_rating, left_on='id', right_on='recipe_id').merge(
        df_count_rating, left_on='id', right_on='recipe_id')

    merged_df.rename(columns={'rating_x': 'Moyenne des notes',
                              'rating_y': 'Nombre de notes'}, inplace=True)

    # Convertir les chaînes de caractères en listes
    merged_df['nutrition'] = merged_df['nutrition'].apply(ast.literal_eval)

    # Convertir la colonne de listes en plusieurs colonnes
    valeurs_df = pd.DataFrame(
        merged_df['nutrition'].tolist(), index=merged_df.index)

    # Renommer les colonnes si nécessaire
    valeurs_df.columns = ['Calories', 'Graisses', 'Sucre', 'Sodium',
                          'Protéines', 'Graisse_saturées', 'Glucides']

    # Joindre le DataFrame original avec le nouveau DataFrame
    nutrition_df = merged_df.drop(columns=['nutrition', 'id']).join(valeurs_df)

    nutrition_df[['Calories', 'Graisses', 'Sucre', 'Sodium',
                  'Protéines', 'Graisse_saturées', 'Glucides']].apply(pd.to_numeric)

    return nutrition_df


@st.cache_data
def clean_data(df):

    df = df[(df['Nombre de notes'] >= 5)]
    df = df.drop(df[df.Calories > 800].index)
    df = df.drop(df[df.Graisses > 100].index)
    df = df.drop(df[df.Graisse_saturées > 100].index)
    df = df.drop(df[df.Sucre > 100].index)
    df = df.drop(df[df.Sodium > 100].index)
    df = df.drop(df[df.Protéines > 100].index)
    df = df.drop(df[df.Glucides > 100].index)

    return df


nutrition_df = load_data()
clean_nutrition_df = clean_data(nutrition_df)

tabs = st.tabs(
    ["Accueil", "Analyse des valeurs nutritionnelles", "Choisir son régime"])

with tabs[0]:

    left, middle, right = st.columns((2, 10, 2))
    with middle:
        st.title('Contexte')
        st.write("Dans cette partie, nous allons nous concentrer sur les valeurs nutritionnelles des recttes. Nous chercherons en particulier à déterminer l'influence des différentes valeurs nutritionnelles sur la popularité d'une recette.")

        st.title('Description du jeu de données global')
        st.write('Notre jeu de données fusionne la table des valeurs nutritionnelles des recettes avec celle des notes attribuées par les utilisateurs :')

        desc_df = nutrition_df.describe()

        nan_count = nutrition_df.isna().sum()
        desc_df.loc['NaN Count'] = nan_count

        st.dataframe(desc_df, use_container_width=True)
        st.write("Nous avons deux moyens de déterminer la popularité d'une recette : le nombre de note et la moyenne des notes.")
        st.write("""Nous avons sept valeurs nutritionneles différentes : les calories, et six différents apports journaliers en %PDV. """)

        st.write("""Le %PDV indique quel pourcentage de la valeur quotidienne recommandée d'un nutriment est fourni par une portion d'un aliment spécifique. Par exemple, si un aliment contient 15% du PDV pour les graisses totales, cela signifie qu'une portion de cet aliment fournit 15% de la quantité de graisses recommandée pour une alimentation de 2000 calories.""")

        """ Comment se calcule le PDV ?

        PDV=(Quantité du nutriment dans la portion/Quantité recommandée quotidienne pour ce nutriment)×100"""

        columns = ['Calories', 'Graisses', 'Sucre', 'Sodium',
                   'Protéines', 'Graisse_saturées', 'Glucides']

        fig, axes = plt.subplots(nrows=1, ncols=7, figsize=(20, 10))

        axes = axes.flatten()

        for i, col in enumerate(columns):
            sns.boxplot(data=nutrition_df, y=col, ax=axes[i])
            axes[i].set_title(f'Boxplot de {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Value')

        plt.suptitle(
            'Distribution des valeurs nutritionnelles par recette', fontsize=16)

        plt.tight_layout()
        plt.subplots_adjust(top=0.9)

        st.pyplot(fig)
        st.write('Notre dataset ne possède pas de valeurs nulles (NaN), cependant il possède énormément de valeurs extrêmes.')
        st.write("Notamment, certaines recettes n'ont aucun sens avec plus de 400 000 calories et plus de 360 000% des apports journaliers en sucre.")

        st.dataframe(nutrition_df[nutrition_df.Calories > 400000],
                     use_container_width=True, hide_index=True)

        ma_liste = ["Les recettes qui ont été notées moins de 5 fois. On ignore ainsi les recettes les moins populaires.",
                    "Les recettes qui font plus de 800 calories. On se concentre uniquement sur les recettes de repas.",
                    "Les recettes dont les apports journaliers en nutrition sont supérieurs à 100%. On ignore ainsi la plupart des recettes avec des valeurs extrêmes."]

        # Afficher la liste avec des puces (bullets points)
        st.markdown(
            "### Dans la suite de notre étude, pour nettoyer notre jeu de données, nous allons ignorer :")
        for entree in ma_liste:
            st.markdown(f"- {entree}")

        # Jeu de données nettoyé

        st.title('Description du jeu de données nettoyé')

        st.dataframe(clean_nutrition_df.describe(), use_container_width=True)

        columns = ['Calories', 'Graisses', 'Sucre', 'Sodium',
                   'Protéines', 'Graisse_saturées', 'Glucides']

        fig, axes = plt.subplots(nrows=1, ncols=7, figsize=(20, 10))

        axes = axes.flatten()

        for i, col in enumerate(columns):
            sns.boxplot(data=clean_nutrition_df, y=col, ax=axes[i])
            axes[i].set_title(f'Boxplot de {col}')
            axes[i].set_xlabel(col)
            axes[i].set_ylabel('Value')

        plt.suptitle(
            'Distribution des valeurs nutritionnelles par recette', fontsize=16)

        plt.tight_layout()
        plt.subplots_adjust(top=0.9)

        st.pyplot(fig)


with tabs[1]:

    st.title('Analyse des valeurs nutritionnelles')

    correlation_matrix = clean_nutrition_df[['Moyenne des notes', 'Nombre de notes', 'Calories', 'Graisses',
                                            'Protéines', 'Glucides', 'Sucre', 'Sodium']].corr()

    left, middle, right = st.columns((2, 5, 2))
    with middle:
        # Créer la heatmap
        plt.figure(figsize=(7, 7))
        sns.heatmap(correlation_matrix, annot=True,
                    cmap='coolwarm', fmt='.2f', linewidths=0.5)

        # Ajouter un titre
        plt.title("Matrice des Corrélations")

        # Afficher le graphique
        plt.tight_layout()

        st.pyplot(plt)

    # Analyse monovariée

    fig, axs = plt.subplots(1, 4, figsize=(20, 5))

    # Plot the first scatter plot (Graisses vs Moyenne des notes)
    scatter1 = axs[0].scatter(clean_nutrition_df['Graisses'],
                              clean_nutrition_df['Moyenne des notes'])
    axs[0].set_title('Graisses vs Moyenne des notes')
    axs[0].set_xlabel('Graisses (g)')
    axs[0].set_ylabel('Moyenne des notes')
    axs[0].grid(True)

    # Plot the second scatter plot (Calories vs Moyenne des notes)
    scatter2 = axs[1].scatter(clean_nutrition_df['Calories'],
                              clean_nutrition_df['Moyenne des notes'])
    axs[1].set_title('Calories vs Moyenne des notes')
    axs[1].set_xlabel('Calories')
    axs[1].set_ylabel('Moyenne des notes')
    axs[1].grid(True)

    # Plot the third scatter plot (Sodium vs Moyenne des notes)
    scatter3 = axs[2].scatter(clean_nutrition_df['Sodium'],
                              clean_nutrition_df['Moyenne des notes'])
    axs[2].set_title('Sodium vs Moyenne des notes')
    axs[2].set_xlabel('Sodium (mg)')
    axs[2].set_ylabel('Moyenne des notes')
    axs[2].grid(True)

    # Plot the third scatter plot (Graisses vs Sucre)
    scatter4 = axs[3].scatter(clean_nutrition_df['Glucides'],
                              clean_nutrition_df['Moyenne des notes'])
    axs[3].set_title('Glucides vs Moyenne des notes')
    axs[3].set_xlabel('Glucides (g)')
    axs[3].set_ylabel('Moyenne des notes')
    axs[3].grid(True)

    # Adjust the layout for better spacing
    plt.tight_layout()

    # Display the plot
    st.pyplot(plt)

    fig, axs = plt.subplots(1, 4, figsize=(20, 5))

    # Plot the first scatter plot (Graisses vs Moyenne des notes)
    scatter1 = axs[0].scatter(clean_nutrition_df['Graisses'],
                              clean_nutrition_df['Nombre de notes'])
    axs[0].set_title('Graisses vs Nombre de notes')
    axs[0].set_xlabel('Graisses (g)')
    axs[0].set_ylabel('Nombre de notes')
    axs[0].grid(True)

    # Plot the second scatter plot (Calories vs Moyenne des notes)
    scatter2 = axs[1].scatter(clean_nutrition_df['Calories'],
                              clean_nutrition_df['Nombre de notes'])
    axs[1].set_title('Calories vs Nombre de notes')
    axs[1].set_xlabel('Calories')
    axs[1].set_ylabel('Nombre de notes')
    axs[1].grid(True)

    # Plot the third scatter plot (Sodium vs Moyenne des notes)
    scatter3 = axs[2].scatter(clean_nutrition_df['Sodium'],
                              clean_nutrition_df['Nombre de notes'])
    axs[2].set_title('Sodium vs Nombre de notes')
    axs[2].set_xlabel('Sodium (mg)')
    axs[2].set_ylabel('Nombre de notes')
    axs[2].grid(True)

    # Plot the third scatter plot (Graisses vs Sucre)
    scatter4 = axs[3].scatter(clean_nutrition_df['Glucides'],
                              clean_nutrition_df['Nombre de notes'])
    axs[3].set_title('Glucides vs Nombre de notes')
    axs[3].set_xlabel('Glucides (g)')
    axs[3].set_ylabel('Nombre de notes')
    axs[3].grid(True)

    # Adjust the layout for better spacing
    plt.tight_layout()

    # Display the plot
    st.pyplot(plt)

with tabs[2]:
    # Affichage du titre de l'application
    st.title("Filtrer des recettes par régime alimentaire")

    # Options de régimes
    regimes = ["Low-Carb", "High-Protein", "Low-Fat"]
    selected_regime = st.selectbox("Choisissez un régime", regimes)

    # Fonction pour filtrer les recettes en fonction du régime

    def filter_recipes(regime):
        if regime == "Low-Carb":
            # Filtre les recettes avec moins de 10g de glucides
            return clean_nutrition_df[clean_nutrition_df['Glucides'] <= 3]
        elif regime == "High-Protein":
            # Filtre les recettes avec plus de 20g de protéines
            return clean_nutrition_df[clean_nutrition_df['Protéines'] >= 75]
        elif regime == "Low-Fat":
            # Filtre les recettes avec moins de 10g de graisses
            return clean_nutrition_df[clean_nutrition_df['Graisses'] <= 3]
        else:
            return clean_nutrition_df

    # Appliquer le filtre
    filtered_df = filter_recipes(selected_regime)

    # Affichage des recettes filtrées
    if not filtered_df.empty:
        st.write(f"Recettes correspondant au régime **{selected_regime}**:")
        grid_options = GridOptionsBuilder.from_dataframe(filtered_df)
        grid_options.configure_selection('single', use_checkbox=True)
        grid_options.configure_pagination(paginationPageSize=10)
        grid_options.configure_column('name', headerCheckboxSelection=True)

        grid_response = AgGrid(
            filtered_df, gridOptions=grid_options.build(), enable_enterprise_modules=True)

        if grid_response['selected_rows'] is not None:
            recette_info = grid_response['selected_rows'].iloc[0]

    else:
        st.write(
            f"Aucune recette ne correspond au régime **{selected_regime}**.")

    try:
        assert (recette_info.any())
    except NameError:
        st.write("Sélectionnez une recette pour en afficher les caractéristiques.")
    else:
        st.write(f"### Détails pour la recette : {recette_info['name']}")

        st.text(f'Recette notée {recette_info['Nombre de notes']} fois avec une moyenne de {
                recette_info['Moyenne des notes']} sur 5')

        # Données pour la première figure (diagramme circulaire)
        Calories_line = recette_info[['Graisses', 'Protéines', 'Glucides']]

        # Diagramme circulaire pour la composition des Calories
        fig1 = go.Figure(data=[go.Pie(labels=Calories_line.index, values=Calories_line,
                                      hoverinfo='label+percent',
                                      textinfo='label+percent',
                                      hole=0.3)])

        fig1.update_layout(
            title=f"Diagramme de composition des calories : {
                recette_info['Calories']} calories totales",
            title_x=0.25,  # Centrer le titre
        )

        # Données pour la deuxième figure (bar chart)
        full_line = recette_info[['Graisse_saturées', 'Graisses', 'Protéines', 'Glucides',
                                  'Sucre', 'Sodium']]

        # Diagramme en barres pour la composition globale
        fig2 = go.Figure(data=[go.Bar(x=full_line.index, y=full_line,
                                      marker=dict(color=['orange', 'blue', 'green', 'red', 'purple', 'brown', 'cyan']))])

        # Ajouter une ligne pour l'apport journalier recommandé
        fig2.add_shape(type="line", x0=0, x1=len(full_line)-1, y0=100,
                       y1=100, line=dict(color="red", dash="dash"))

        # Ajouter un titre et une légende
        fig2.update_layout(
            title="Diagramme de composition global",
            title_x=0.4,
            showlegend=False,
            xaxis_title="Nutriments",
            yaxis_title="Quantité",
            plot_bgcolor='white',  # Fond blanc
            shapes=[dict(type="line", x0=0, x1=len(full_line)-1, y0=100,
                         y1=100, line=dict(color="red", dash="dash"))],
            annotations=[dict(x=0.5, y=100, xref="paper", yref="y",
                              text="Apport journalier requis", showarrow=True, arrowhead=3, ax=0, ay=-30, font=dict(
                                  size=12,       # Taille de la police
                                  # Couleur du texte foncé (gris foncé ou une autre couleur)
                                  color="rgb(50, 50, 50)"
                              ),)]
        )

        # Affichage des deux graphiques côte à côte dans Streamlit
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(fig1)

        with col2:
            st.plotly_chart(fig2)
