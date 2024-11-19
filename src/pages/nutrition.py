import seaborn as sns
import streamlit as st
import pandas as pd
import ast
import matplotlib.pyplot as plt
from pathlib import Path
import os

st.set_page_config(
    page_title="INTERACTIONS_PAGE",
    layout="wide"
)

st.subheader("NUTRITION")

df_RAW_recipes = pd.read_csv(os.path.join('data','RAW_recipes.csv'))
df_RAW_interactions = pd.read_csv(os.path.join('data','RAW_interactions.csv'))

# On ne garde que la moyenne des notes de la recette
df_mean_rating = df_RAW_interactions[[
    'recipe_id', 'rating']].groupby(['recipe_id']).mean()
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
valeurs_df.columns = ['calories', 'total_fat', 'sugar', 'sodium',
                      'protein', 'saturated_fat', 'carbohydrates']


# Joindre le DataFrame original avec le nouveau DataFrame
final_df = merged_df.drop(columns=['nutrition', 'id']).join(valeurs_df)

final_df[['calories', 'total_fat', 'sugar', 'sodium',
         'protein', 'saturated_fat', 'carbohydrates']].apply(pd.to_numeric)


# Preprocessing

final_df = final_df[(final_df['Nombre de notes'] >= 1)]
final_df = final_df.drop(final_df[final_df.calories > 3000].index)
final_df = final_df.drop(final_df[final_df.total_fat > 100].index)
final_df = final_df.drop(final_df[final_df.saturated_fat > 100].index)
final_df = final_df.drop(final_df[final_df.sugar > 100].index)
final_df = final_df.drop(final_df[final_df.sodium > 100].index)
final_df = final_df.drop(final_df[final_df.protein > 100].index)
final_df = final_df.drop(final_df[final_df.carbohydrates > 100].index)

final_df_nutrition = final_df[['calories', 'total_fat', 'sugar', 'sodium',
                              'protein', 'saturated_fat', 'carbohydrates']]


st.title('Description du dataset')

st.dataframe(final_df.describe())

# Sélectionner la recette


st.title('Analyse recette par recette')

selected_value = st.selectbox(
    "Sélectionnez la recette",
    final_df['name'],
    index=None,
    placeholder="Sélectionnez la recette ...",
)

st.text(f'Recette notée {final_df[[
        'Nombre de notes']].loc[final_df["name"] == selected_value].iloc[0]['Nombre de notes']} fois')
st.text(f'Avec une moyenne de {final_df[[
    'Moyenne des notes']].loc[final_df["name"] == selected_value].iloc[0]['Moyenne des notes']} sur 5')

fig, axs = plt.subplots(1, 2, figsize=(20, 5))


calories_line = final_df[['total_fat', 'protein',
                          'carbohydrates']].loc[final_df["name"] == selected_value].iloc[0]

# Tracer le premier diagramme circulaire
axs[0].pie(calories_line, labels=calories_line.index,
           autopct='%1.1f%%', startangle=90)
axs[0].set_title("Diagramme de composition des calories")

full_line = final_df[['saturated_fat', 'total_fat',
                      'protein', 'carbohydrates', 'sugar', 'sodium',]].loc[final_df["name"] == selected_value].iloc[0]

# Tracer le troisième diagramme circulaire
axs[1].bar(full_line.index, full_line, color=[
    'orange', 'blue', 'green', 'red', 'purple', 'brown', 'cyan'])
axs[1].axhline(100, color='red', linestyle='dashed',
               linewidth=2, label='Apport journalier requis')
axs[1].legend(loc='right')
axs[1].set_title("Diagramme de composition global")

plt.tight_layout()

st.pyplot(plt)

st.title('Analyse globale')

# Création d'une figure avec des sous-graphiques
fig, axes = plt.subplots(1, len(final_df_nutrition.columns), figsize=(15, 5))

# Tracer un boxplot pour chaque colonne
for i, col in enumerate(final_df_nutrition.columns):
    # Tracer le boxplot pour chaque colonne
    axes[i].boxplot(final_df_nutrition[col])
    axes[i].set_title(f'Boxplot de {col}')
    axes[i].set_xticklabels([col])  # Nommer l'axe X (nom de la colonne)
    axes[i].set_ylabel('Valeur')  # Optionnel: étiquette pour l'axe Y

# Ajuster l'espacement pour que les graphes ne se chevauchent pas
plt.tight_layout()

st.pyplot(plt)


correlation_matrix = final_df[['Moyenne des notes', 'total_fat',
                               'protein', 'carbohydrates', 'sugar', 'sodium']].corr()

# Créer la heatmap
plt.figure(figsize=(5, 5))
sns.heatmap(correlation_matrix, annot=True,
            cmap='coolwarm', fmt='.2f', linewidths=0.5)

# Ajouter un titre
plt.title("Matrice des Corrélations")

# Afficher le graphique
plt.tight_layout()

st.pyplot(plt)
