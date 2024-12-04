import streamlit as st
from src.process.recommandation import AdvancedRecipeRecommender


def recommandation_page(recipe_df):
    # Chargement des données
    # Chargement des données
    recommender = AdvancedRecipeRecommender(recipes_df=recipe_df)

    # Sidebar de navigation
    st.sidebar.title("🍽️ Recipe Intelligence")
    menu = st.selectbox("Sélectionnez une page", [
        "Recommandations de Recettes",
        "Analyse de Clusters",
    ], key='selectbox_analyse_13')

    # Page de Recommandations
    if menu == "Recommandations de Recettes":
        st.title("🍲 Recommandations Personnalisées")

        # Sélection de recette
        selected_recipe_id = st.selectbox(
            "Choisissez une recette de base",
            recommender.recipes_df['id'].tolist()
        )

        # Afficher la recette sélectionnée
        selected_recipe = recommender.recipes_df[recommender.recipes_df['id']
                                                 == selected_recipe_id].iloc[0]
        st.subheader(f"Recette de Base : {selected_recipe['name']}")

        # Colonnes pour les détails
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Durée :** {selected_recipe['minutes']} minutes")
            st.write(f"**Nombre d'étapes :** {selected_recipe['n_steps']}")
        with col2:
            st.write("**Ingrédients :**")
            st.write(", ".join(eval(selected_recipe['ingredients'])))

        # Recommandations
        st.subheader("Recommandations Basées sur le Contenu")
        recommendations = recommender.content_based_recommendations(
            selected_recipe_id,
            top_n=3
        )

        # Afficher les recommandations
        for _, rec in recommendations.iterrows():
            with st.expander(rec['name']):
                st.write(f"**Durée :** {rec['minutes']} minutes")
                st.write(
                    f"**Ingrédients :** {', '.join(eval(rec['ingredients']))}")

    # Page d'Analyse de Clusters
    elif menu == "Analyse de Clusters":
        st.title("Analyse de Clusters")
