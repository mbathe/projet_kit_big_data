<<<<<<< HEAD
""" import json
=======
import json
>>>>>>> 601a7a15331ce1944996c25ea542c6a25da39240
import ast
from tqdm import tqdm

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Float, Text, JSON, text ,  Boolean, ARRAY
)
from sqlalchemy.orm import sessionmaker , relationship , declarative_base
from sqlalchemy.sql import func


Base = declarative_base()

class IngrMap(Base):
    __tablename__ = 'ingr_map'
    
    id_add_for_unicity = Column(Integer, primary_key=True, autoincrement=True)

    # Identifiant unique de l'ingrédient
    id = Column(Integer, nullable=False)
    
    # Texte brut de l'ingrédient tel qu'il apparaît dans les recettes
    raw_ingr = Column(String, nullable=False)
    
    # Nombre de mots dans le texte brut de l'ingrédient
    raw_words = Column(Integer, nullable=True)
    
    # Version traitée du texte de l'ingrédient (par exemple, mise en minuscule, suppression de la ponctuation)
    processed = Column(String, nullable=True)
    
    # Longueur du texte traité
    len_proc = Column(Integer, nullable=True)
    
    # Nom standardisé de l'ingrédient après traitement
    replaced = Column(String, nullable=True)
    
    # Nombre d'occurrences de cet ingrédient dans l'ensemble de données
    count = Column(Integer, nullable=True)

class User(Base):
    __tablename__ = 'users'
    
    # Indice interne de l'utilisateur (clé primaire)
    u = Column(Integer, primary_key=True, nullable=False)

    # user_id =  Column(Integer,unique=True, nullable=False)
    
    # Liste des techniques associées à l'utilisateur (stockée sous forme de texte JSON)
    techniques = Column(Text, nullable=True)
    
    # Liste des indices des recettes avec lesquelles l'utilisateur a interagi (id dans Recipe)
    items = Column(Text, nullable=True)
    
    # Nombre d'items avec lesquels l'utilisateur a interagi
    n_items = Column(Integer, nullable=True)
    
    # Liste des notes données par l'utilisateur
    ratings = Column(Text, nullable=True)
    
    # Nombre de notes données
    n_ratings = Column(Integer, nullable=True)
    
    # Relations
    interactions = relationship('Interaction', back_populates='user', foreign_keys='Interaction.u')
    recipes_contributed = relationship('Recipe', back_populates='contributor', foreign_keys='Recipe.contributor_id')

class Recipe(Base):
    __tablename__ = 'recipes'
    
    # Identifiant unique de la recette (clé primaire)
    id = Column(Integer, primary_key=True, nullable=False)
    
    # Indice interne de la recette
    i = Column(Integer, unique=True, nullable=True)
    
    # Nom de la recette
    name = Column(String, nullable=True)
    
    # Tokens du nom de la recette (stockés sous forme de texte JSON)
    name_tokens = Column(Text, nullable=True)
    
    # Tokens des ingrédients
    ingredient_tokens = Column(Text, nullable=True)
    
    # Tokens des étapes de la recette
    steps_tokens = Column(Text, nullable=True)
    
    # Liste des techniques culinaires utilisées
    techniques = Column(Text, nullable=True)
    
    # Niveau calorique de la recette
    calorie_level = Column(Integer, nullable=True)
    
    # Liste des IDs des ingrédients utilisés
    ingredient_ids = Column(Text, nullable=True)
    
    # Temps total en minutes pour préparer la recette
    minutes = Column(Integer, nullable=True)
    
    # ID de l'utilisateur qui a contribué la recette
    contributor_id = Column(Integer, ForeignKey('users.u'), nullable=True)
    
    # Date de soumission de la recette
    submitted = Column(DateTime, nullable=True)
    
    # Tags associés à la recette
    tags = Column(Text, nullable=True)
    
    # Informations nutritionnelles
    nutrition = Column(Text, nullable=True)
    
    # Nombre d'étapes dans la recette
    n_steps = Column(Integer, nullable=True)
    
    # Liste des étapes de la recette
    steps = Column(Text, nullable=True)
    
    # Description de la recette
    description = Column(Text, nullable=True)
    
    # Liste des ingrédients utilisés dans la recette
    ingredients = Column(Text, nullable=True)
    
    # Nombre d'ingrédients
    n_ingredients = Column(Integer, nullable=True)
    
    # Relations
    interactions = relationship('Interaction', back_populates='recipe', foreign_keys='Interaction.recipe_id')
    contributor = relationship('User', back_populates='recipes_contributed', foreign_keys=[contributor_id])

class Interaction(Base):
    __tablename__ = 'interactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ID de l'utilisateur qui a interagi avec la recette
    user_id = Column(Integer, nullable=False)
    
    # ID de la recette avec laquelle l'utilisateur a interagi
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
    
    # Date de l'interaction
    date = Column(DateTime, nullable=True)
    
    # Note donnée par l'utilisateur
    rating = Column(Float, nullable=True)
    
    # Avis écrit par l'utilisateur
    review = Column(Text, nullable=True)
    
    # Indice interne de l'utilisateur
    u = Column(Integer , ForeignKey('users.u'),nullable=False )
    
    # Indice interne de la recette
    i = Column(Integer, nullable=True)
    
    # Relations
    user = relationship('User', back_populates='interactions', foreign_keys=[u])
    recipe = relationship('Recipe', back_populates='interactions', foreign_keys=[recipe_id])


class DatabaseManagement:
    def __init__(self, db_name: str, recreate: bool, USER: str, PASSWORD: str, HOST:str ,PORT: str):
        self.engine = create_engine(
            f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{db_name}"
        )
        self.db_name = db_name
        if recreate:
            if database_exists(self.engine.url):
                drop_database(self.engine.url)
                print(f"Base de données '{db_name}' supprimée.")
        
        if not database_exists(self.engine.url):
            self.create_db()
        
        # Créer un SessionLocal pour gérer les sessions
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_db(self):
        """Crée la base de données et les tables."""
        create_database(self.engine.url)
        Base.metadata.create_all(self.engine)
        print(f"Base de données '{self.db_name}' créée avec succès.")
    
    def query(self, sql_query: str):
        """Exécute une requête SQL et retourne les résultats."""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_query))  # Utilise text() pour envelopper la requête
            return result.fetchall()
    
    def initialize_IngrMap(self):
        session = self.SessionLocal()
        try:

            ingr_map_df = pd.read_pickle('ingr_map.pkl')
            
            # Insérer les données dans la table IngrMap
            print("Insertion des données dans IngrMap...")
            ingr_map_records = []
            for index, row in ingr_map_df.iterrows():
                ingr = IngrMap(
                    id=int(row['id']),
                    raw_ingr=row['raw_ingr'],
                    raw_words=int(row['raw_words']),
                    processed=row['processed'],
                    len_proc=int(row['len_proc']),
                    replaced=row['replaced'],
                    count=int(row['count'])
                )
                ingr_map_records.append(ingr)
            session.bulk_save_objects(ingr_map_records)
            session.commit()
            print("Données insérées dans IngrMap.")
        except Exception as e:
            print("Une erreur s'est produite:", e)
            session.rollback()
        finally:
            session.close()

    def initialize_PP_User(self):
        session = self.SessionLocal()
        try:

            pp_users_df = pd.read_csv('PP_users.csv')
            if pp_users_df['u'].is_unique:
                print("Les IDs dans PP_users sont uniques.")
            else:
                print("Attention: IDs du PP_users ne sont pas uniques.")
                pp_users_df = pp_users_df.drop_duplicates(subset='u')
                print("Doublons supprimés dans PP_users.")

            # Insérer les données dans la table User
            print("Insertion des données dans User...")
            pp_users_records = []
            for index, row in pp_users_df.iterrows():
                # Convertir les chaînes JSON en listes
                techniques = json.loads(row['techniques'])
                items = json.loads(row['items'])
                ratings = json.loads(row['ratings'])

                user = User(
                    u=int(row['u']),
                    techniques=json.dumps(techniques),  # Stocker en format JSON
                    items=json.dumps(items),
                    n_items=int(row['n_items']),
                    ratings=json.dumps(ratings),
                    n_ratings=int(row['n_ratings'])
                )
                pp_users_records.append(user)
            session.bulk_save_objects(pp_users_records)
            session.commit()
            print("Données insérées dans User.")

        except Exception as e:
            print("Une erreur s'est produite:", e)
            session.rollback()
        finally:
            session.close()

    def initialize_PP_recipes(self):
        session = self.SessionLocal()
        try:
            pp_recipes_df = pd.read_csv('PP_recipes.csv')
            if pp_recipes_df['id'].is_unique:
                print("Les IDs dans PP_recipes sont uniques.")
            else:
                print("Attention: IDs du PP_recipes ne sont pas uniques.")
                pp_recipes_df = pp_recipes_df.drop_duplicates(subset='id')
                print("Doublons supprimés dans PP_recipes.")

            # Insérer les données dans la table Recipe
            print("Insertion des données dans Recipe...")
            pp_recipes_records = []
            for index, row in pp_recipes_df.iterrows():
                # Convertir les chaînes JSON en listes
                name_tokens = json.loads(row['name_tokens'])
                ingredient_tokens = json.loads(row['ingredient_tokens'])
                steps_tokens = json.loads(row['steps_tokens'])
                techniques = json.loads(row['techniques'])
                ingredient_ids = json.loads(row['ingredient_ids'])

                recipe = Recipe(
                    id=int(row['id']),
                    i=int(row['i']),
                    name_tokens=json.dumps(name_tokens),
                    ingredient_tokens=json.dumps(ingredient_tokens),
                    steps_tokens=json.dumps(steps_tokens),
                    techniques=json.dumps(techniques),
                    calorie_level=int(row['calorie_level']),
                    ingredient_ids=json.dumps(ingredient_ids)
                )
                pp_recipes_records.append(recipe)
            session.bulk_save_objects(pp_recipes_records)
            session.commit()
            print("Données insérées dans Recipe.")

        except Exception as e:
            print("Une erreur s'est produite:", e)
            session.rollback()
        finally:
            session.close()

    def initialize_interaction(self , file_name):

        session = self.SessionLocal()
        try:            
                interactions_df = pd.read_csv(file_name)
                print(f"Insertion des interactions depuis {file_name}...")
                interactions_records = []
                for index, row in tqdm(list(interactions_df.iterrows())):
                    user_id = int(row['user_id'])
                    recipe_id = int(row['recipe_id'])


                    interaction = Interaction(
                        user_id=user_id,
                        recipe_id=recipe_id,
                        date=pd.to_datetime(row['date'], errors='coerce'),
                        rating=float(row['rating']),
                        u=int(row['u']),
                        i=int(row['i'])
                    )
                    interactions_records.append(interaction)
                session.bulk_save_objects(interactions_records)
                session.commit()
                print(f"Interactions insérées depuis {file_name}.")


        except Exception as e:
            print("Une erreur s'est produite:", e)
            session.rollback()
        finally:
            session.close()

    def initialize_RAW_recipes(self,user_id_to_u):
        try: 
            session = self.SessionLocal()
            raw_recipes_df = pd.read_csv('RAW_recipes.csv')
            # Mettre à jour les recettes avec les informations supplémentaires
            print("Mise à jour des recettes avec les données brutes...")
            for index, row in tqdm(raw_recipes_df.iterrows()):
                    recipe_id = int(row['id'])
                    user_id = int(row['contributor_id'])
                    try :
                        contributor_id = user_id_to_u[user_id]
                    except : 
                        contributor_id = user_id
                    
                    user = session.query(User).filter_by(u=contributor_id).first()
                    if not user:
                        user = User(u=user_id)
                        session.add(user)
                        session.commit()

                    # Vérifier si la recette existe déjà
                    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
                    if recipe:
                        # Mettre à jour les champs de la recette existante
                        recipe.name = row['name']
                        recipe.minutes = int(row['minutes'])
                        recipe.contributor_id = contributor_id  # Assurez-vous que contributor_id existe maintenant
                        recipe.submitted = pd.to_datetime(row['submitted'], errors='coerce')
                        recipe.tags = json.dumps(ast.literal_eval(row['tags']))
                        recipe.nutrition = json.dumps(ast.literal_eval(row['nutrition']))
                        recipe.n_steps = int(row['n_steps'])
                        recipe.steps = json.dumps(ast.literal_eval(row['steps']))
                        recipe.description = row['description']
                        recipe.ingredients = json.dumps(ast.literal_eval(row['ingredients']))
                        recipe.n_ingredients = int(row['n_ingredients'])
                    else:
                        # Créer une nouvelle recette
                        recipe = Recipe(
                            id=recipe_id,
                            name=row['name'],
                            minutes=int(row['minutes']),
                            contributor_id=contributor_id,
                            submitted=pd.to_datetime(row['submitted'], errors='coerce'),
                            tags=json.dumps(ast.literal_eval(row['tags'])),
                            nutrition=json.dumps(ast.literal_eval(row['nutrition'])),
                            n_steps=int(row['n_steps']),
                            steps=json.dumps(ast.literal_eval(row['steps'])),
                            description=row['description'],
                            ingredients=json.dumps(ast.literal_eval(row['ingredients'])),
                            n_ingredients=int(row['n_ingredients'])
                        )
                        session.add(recipe)
            session.commit()
            print("Recettes mises à jour avec les données brutes.")
        # except Exception as e:
        #     print("Une erreur s'est produite:", e)
            
        finally:
            session.rollback()
            session.close()
    
    def initialize_RAW_interactions(self) : 
            session = self.SessionLocal()
            try : 
                raw_interactions_df = pd.read_csv('RAW_interactions.csv')
                print("Insertion des interactions depuis RAW_interactions.csv...")
                raw_interactions_records = []
                for index, row in raw_interactions_df.iterrows():
                    user_id = int(row['user_id'])
                    recipe_id = int(row['recipe_id'])

                    # Vérifier si l'utilisateur existe, sinon le créer
                    user = session.query(User).filter_by(u=user_id).first()
                    if not user:
                        user = User(u=user_id)
                        session.add(user)
                        session.commit()

                    # Vérifier si la recette existe, sinon la créer
                    recipe = session.query(Recipe).filter_by(id=recipe_id).first()
                    if not recipe:
                        recipe = Recipe(id=recipe_id)
                        session.add(recipe)
                        session.commit()

                    interaction = Interaction(
                        user_id=user.u,
                        recipe_id=recipe.id,
                        date=pd.to_datetime(row['date'], errors='coerce'),
                        rating=float(row['rating']),
                        review=row['review']
                    )
                    raw_interactions_records.append(interaction)
                session.bulk_save_objects(raw_interactions_records)
                session.commit()
                print("Interactions insérées depuis RAW_interactions.csv.")

    

            
                # Commit final
                session.commit()
                print("Données insérées avec succès dans la base de données.")
            
            except Exception as e:
                print("Une erreur s'est produite:", e)
                session.rollback()
            finally:
                session.close()

    def initialize_database(self):
        """Initialise la base de données en créant les tables et en y insérant les données."""
        
        # Créer les tables dans la base de données
        Base.metadata.create_all(self.engine)

        # Créer une session pour les transactions
        # session = self.SessionLocal()

        try:
            # Charger les données des fichiers
            print("Chargement des données...")

    # 1. Charger ingr_map.pkl
            self.initialize_IngrMap()

    # 2. Charger PP_users.csv
            self.initialize_PP_User()

    # 3. Charger PP_recipes.csv
            self.initialize_PP_recipes()
        
    # 4. Charger interactions.csv
            self.initialize_interaction('interactions_test.csv')
            self.initialize_interaction('interactions_train.csv')
            self.initialize_interaction('interactions_validation.csv')

            session = self.SessionLocal()
            user_id_to_u ={user_id : u for (user_id,u) in  set(session.query(Interaction.user_id, Interaction.u).all())}
            session.close()

    # 5. Charger RAW_recipes.csv
            self.initialize_RAW_recipes(user_id_to_u)

    # 6. Charger RAW_interactions.csv



        except Exception as e:
            print("Une erreur s'est produite:", e)
            session.rollback()
        finally:
            session.close()
<<<<<<< HEAD
 """
=======
>>>>>>> 601a7a15331ce1944996c25ea542c6a25da39240
