import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.subheader("RECIPES")


data = {'minutes': [1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 5, 6]}
df = pd.DataFrame(data)

# Calculer la fréquence des minutes
frequence_minutes = df['minutes'].value_counts().sort_index()
taille_groupe = 100
nombre_total_minutes = frequence_minutes.shape[0]

# Exemple de DataFrame (remplacez ceci par votre DataFrame)
data = {'minutes': [1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 5, 6]}
df = pd.DataFrame(data)

# Calculer la fréquence des minutes
frequence_minutes = df['minutes'].value_counts().sort_index()

# Interface utilisateur pour choisir la plage de minutes
st.title("Fréquence des valeurs dans la colonne 'minutes'")

# Sélectionner la plage de minutes
min_value = int(frequence_minutes.index.min())
max_value = int(frequence_minutes.index.max())
selected_range = st.slider("Sélectionnez la plage de minutes",
                           min_value=min_value,
                           max_value=max_value,
                           value=(min_value, max_value))

# Filtrer les données selon la plage sélectionnée
filtered_frequence = frequence_minutes.loc[selected_range[0]:selected_range[1]]

# Améliorer l'apparence des graphiques
# plt.style.use('seaborn-darkgrid')  # Utiliser un style de Matplotlib

# Afficher le graphique
plt.figure(figsize=(12, 6))
bars = plt.bar(filtered_frequence.index, filtered_frequence.values,
               color='skyblue', edgecolor='black')

# Ajout de labels et de titres
plt.xticks(rotation=45, ha='right')
plt.xlabel('Minutes', fontsize=12)
plt.ylabel('Fréquence', fontsize=12)
plt.title(f'Fréquence des valeurs de {selected_range[0]} à {
          selected_range[1]} dans la colonne "minutes"', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Ajouter des annotations sur les barres
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval,
             int(yval), ha='center', va='bottom', fontsize=10)

plt.tight_layout()

# Afficher le plot dans Streamlit
st.pyplot(plt)
