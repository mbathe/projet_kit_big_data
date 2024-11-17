""" import os

from src.utils.streamlit import st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
from src.zone_sacha.db_mapping import DatabaseManagement, IngrMap, Recipe, Interaction
from sqlalchemy import func


USER = os.getenv('USER')
PASSWORD = ""
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')


db_name = "PROJET_FOOD_MSIA"
recreate_db = False

db = DatabaseManagement(db_name, recreate_db,USER,PASSWORD,HOST,PORT)

session = db.SessionLocal()
produits = set(session.query(IngrMap.replaced,IngrMap.id).all())
id_to_produits = {id_ : ele for (ele,id_) in produits }

# Recipes = set(session.query(Recipe.name,Recipe.ingredient_ids).all())
Recipes = session.query(
    Recipe.id,
    Recipe.name,
    Recipe.ingredient_ids,
    func.avg(Interaction.rating).label('average_rating')
    
).join(
    Interaction, Interaction.recipe_id == Recipe.id
).group_by(
    Recipe.id,
    Recipe.name
).all()
Recipe_dict = {name : ([id_to_produits[int(id_)] for id_ in produits[1:-1].split(',')],rate)  for (_,name,produits,rate) in Recipes if produits}



produits_df = pd.DataFrame({
    'nom_produit': [ ele[0] for ele in produits]
})
recettes_df = pd.DataFrame({
    'nom_recette' : [recip for recip in Recipe_dict],
    'ingredients': [Recipe_dict[recip][0] for recip in Recipe_dict],
    'notation' : [Recipe_dict[recip][1] for recip in Recipe_dict]

})

# Conversion des ingrédients en listes si nécessaire


def convert_ingredients(x):
    if isinstance(x, str):
        return ast.literal_eval(x)
    return x


recettes_df['ingredients'] = recettes_df['ingredients'].apply(
    convert_ingredients)

st.title("Recherche de Recettes")

# Initialisation de la liste des ingrédients sélectionnés
if 'selected_ingredients' not in st.session_state:
    st.session_state.selected_ingredients = []

# Barre de recherche
search_query = st.text_input("Rechercher un ingrédient")

if search_query:
    produits_filtres = produits_df[produits_df['nom_produit'].str.contains(
        search_query, case=False, na=False)]
    if not produits_filtres.empty:
        selected = st.selectbox(
            "Sélectionnez un ingrédient", produits_filtres['nom_produit'].tolist())
        if st.button("Ajouter"):
            if selected not in st.session_state.selected_ingredients:
                st.session_state.selected_ingredients.append(selected)
                st.success(f"{selected} ajouté à la liste.")
    else:
        st.warning("Aucun produit trouvé.")

# Affichage des ingrédients sélectionnés
st.subheader("Ingrédients Sélectionnés")
for ingr in st.session_state.selected_ingredients:
    st.write(f"- {ingr}")

# Bouton de recherche des recettes
if st.button("Rechercher des Recettes"):
    if st.session_state.selected_ingredients:
        # Calcul de la similarité
        recettes_df['ingredients_str'] = recettes_df['ingredients'].apply(
            lambda x: ' '.join(x))

        vectorizer = TfidfVectorizer().fit(recettes_df['ingredients_str'])
        recettes_vectors = vectorizer.transform(recettes_df['ingredients_str'])

        # Vectorisation des ingrédients sélectionnés
        selected_str = ' '.join(st.session_state.selected_ingredients)
        selected_vector = vectorizer.transform([selected_str])

        # Calcul de la similarité cosine
        cosine_sim = cosine_similarity(
            selected_vector, recettes_vectors).flatten()
        recettes_df['similarity'] = cosine_sim

        # Tri des recettes par similarité décroissante
        recettes_similaires = recettes_df.sort_values(
            by='similarity', ascending=False).head(10)

        # Affichage des recettes
        st.subheader("Recettes Similaires")
        for index, row in recettes_similaires.iterrows():
            with st.expander(row['nom_recette']):
                st.write("**Ingrédients :**")
                st.write(", ".join(row['ingredients']))
                # Affichage des étoiles
                full_stars = int(row['notation'])
                empty_stars = 5 - full_stars
                stars = '⭐' * full_stars + '☆' * empty_stars
                st.write("**Notation :**")
                st.write(stars)
    else:
        st.warning("Veuillez ajouter au moins un ingrédient à la liste.")
 """
