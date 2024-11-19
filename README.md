### Analyse des DataFrames et mapping vers des tables SQL

#### 1. `ingr_map.pkl`

**Description**: Ce DataFrame contient une correspondance entre les ID des ingrédients et leurs noms, ainsi que des informations supplémentaires sur chaque ingrédient.

**Colonnes**:

- `id` (int): Identifiant unique de l'ingrédient (clé primaire).
- `raw_ingr` (str): Texte brut de l'ingrédient tel qu'il apparaît dans les recettes.
- `raw_words` (int): Nombre de mots dans le texte brut de l'ingrédient.
- `processed` (str): Version traitée du texte de l'ingrédient (par exemple, mise en minuscule, suppression de la ponctuation).
- `len_proc` (int): Longueur du texte traité.
- `replaced` (str): Nom standardisé de l'ingrédient après traitement.
- `count` (int): Nombre d'occurrences de cet ingrédient dans l'ensemble de données.

**Mapping vers la base de données**:

- Créer une table `ingr_map` avec les colonnes ci-dessus.
- Utiliser `id` comme clé primaire.

#### 2. `interactions_test.csv`, `interactions_train.csv`, `interactions_validation.csv`

**Description**: Ces DataFrames contiennent les interactions des utilisateurs avec les recettes, y compris les évaluations.

**Colonnes**:

- `user_id` (int): Identifiant de l'utilisateur qui a interagi avec la recette.
- `recipe_id` (int): Identifiant de la recette.
- `date` (str): Date de l'interaction.
- `rating` (float): Note donnée par l'utilisateur à la recette.
- `u` (int): Indice interne de l'utilisateur utilisé dans le prétraitement.
- `i` (int): Indice interne de la recette utilisé dans le prétraitement.

**Mapping vers la base de données**:

- Créer une table `interactions` avec les colonnes correspondantes.
- Les colonnes `user_id` et `recipe_id` seront des clés étrangères vers les tables `users` et `recipes`.
- Inclure `u` et `i` si nécessaire pour le mapping interne.

#### 3. `PP_recipes.csv`

**Description**: Ce DataFrame contient des recettes prétraitées, y compris les tokens du nom, des ingrédients et des étapes, ainsi que des métadonnées supplémentaires.

**Colonnes**:

- `id` (int): Identifiant unique de la recette (clé primaire).
- `i` (int): Indice interne de la recette.
- `name_tokens` (str): Tokens du nom de la recette.
- `ingredient_tokens` (str): Tokens des ingrédients.
- `steps_tokens` (str): Tokens des étapes de la recette.
- `techniques` (str): Liste des techniques culinaires utilisées.
- `calorie_level` (int): Niveau calorique de la recette.
- `ingredient_ids` (str): Liste des IDs des ingrédients utilisés.

**Mapping vers la base de données**:

- Étendre la table `recipes` pour inclure ces colonnes.
- Stocker les listes et les tokens sous forme de texte ou de types appropriés (par exemple, JSON).

#### 4. `PP_users.csv`

**Description**: Ce DataFrame contient des données prétraitées sur les utilisateurs, y compris les techniques connues et les items (recettes) avec lesquels ils ont interagi.

**Colonnes**:

- `u` (int): Indice interne de l'utilisateur (clé primaire).
- `techniques` (str): Liste des techniques associées à l'utilisateur.
- `items` (str): Liste des indices des recettes avec lesquelles l'utilisateur a interagi.
- `n_items` (int): Nombre d'items avec lesquels l'utilisateur a interagi.
- `ratings` (str): Liste des notes données par l'utilisateur.
- `n_ratings` (int): Nombre de notes données.

**Mapping vers la base de données**:

- Créer une table `users` avec les colonnes correspondantes.
- Utiliser `u` comme clé primaire.

#### 5. `RAW_interactions.csv`

**Description**: Ce DataFrame contient les interactions brutes des utilisateurs avec les recettes, y compris les avis.

**Colonnes**:

- `user_id` (int): Identifiant de l'utilisateur.
- `recipe_id` (int): Identifiant de la recette.
- `date` (str): Date de l'interaction.
- `rating` (int): Note donnée par l'utilisateur.
- `review` (str): Avis écrit par l'utilisateur.

**Mapping vers la base de données**:

- Étendre la table `interactions` pour inclure la colonne `review`.
- Convertir `date` en type `DateTime`.

#### 6. `RAW_recipes.csv`

**Description**: Ce DataFrame contient les données brutes des recettes.

**Colonnes**:

- `id` (int): Identifiant unique de la recette (clé primaire).
- `name` (str): Nom de la recette.
- `minutes` (int): Temps total en minutes pour préparer la recette.
- `contributor_id` (int): Identifiant de l'utilisateur qui a contribué la recette.
- `submitted` (str): Date de soumission de la recette.
- `tags` (str): Liste des tags associés à la recette.
- `nutrition` (str): Informations nutritionnelles.
- `n_steps` (int): Nombre d'étapes dans la recette.
- `steps` (str): Liste des étapes de la recette.
- `description` (str): Description de la recette.
- `ingredients` (str): Liste des ingrédients utilisés.
- `n_ingredients` (int): Nombre d'ingrédients.

**Mapping vers la base de données**:

- Étendre la table `recipes` pour inclure ces colonnes.
- Mapper `contributor_id` vers la table `users`.
** Idées de thèmes 
- Faire de la recherche documentaire en sélectionnant le meilleur nom de recette parmi les noms disponibles à partir d'une liste d'ingrédients.
- Faire du NLP pour prédire le meilleur nom de recette à partir d'une liste d'ingrédients.
- Faire de l'IA générative pour générer le nom d'une recette en se basant sur les ingrédients.

Utiliser Streamlit Cloud pour partager sur internet, pas besoin de serveurs.


