import streamlit as st
import base64
import time  # Simuler un délai pour le chargement des données.


class Welcome:
    def __init__(self):
        pass

    @staticmethod
    def get_img_as_base64(file_path):
        """Convertit une image en base64"""
        try:
            with open(file_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception as e:
            st.error(f"Erreur de chargement de l'image : {e}")
            return None

    @staticmethod
    def display_welcome_screen():
        """Affiche l'écran de bienvenue"""
        # Charger l'image en base64 (remplacez par le chemin de votre image)
        img_path = "path/to/your/cooking_image.jpg"
        img_base64 = Welcome.get_img_as_base64(img_path)

        # Style CSS personnalisé
        st.markdown(f"""
        {'' if img_base64 else ''}

        👨‍🍳 Food.com Recipes Explorer
        🍽️ Analyse Approfondie des Recettes
        """, unsafe_allow_html=True)

        # Message informatif
        st.markdown("""
        ### 📊 Chargement des Données Culinaires
        *Votre voyage gastronomique commence...*
        
        #### 🔍 Ce que vous allez découvrir :
        
        - 🥗 **Statistiques détaillées des recettes**
        - 📈 Analyses nutritionnelles avancées
        - 🌍 Exploration des tendances culinaires
        - ⭐ Système de recommandation personnalisé
        """)

    @staticmethod
    def load_data():
        """Chargement des données avec spinner et progression"""
        with st.spinner("Chargement des données en cours..."):
            # Simuler un temps de chargement (ajustez selon vos besoins)
            # Remplacez par votre logique de chargement de données réelle.
            time.sleep(5)

        # Lorsque le spinner est terminé, vous pouvez afficher un message ou afficher la nouvelle version de l'application.
        st.success("Données chargées avec succès !")

    @staticmethod
    def show_welcom():
        """Méthode principale pour exécuter l'application"""

        # Créez un espace vide pour le contenu initial
        welcome_placeholder = st.empty()

        # Affiche l'écran de bienvenue
        welcome_placeholder.markdown("""
        👨‍🍳 Food.com Recipes Explorer
        🍽️ Analyse Approfondie des Recettes
        ### 📊 Chargement des Données Culinaires
        
        *Votre voyage gastronomique commence...*

        #### 🔍 Ce que vous allez découvrir :
        - 🥗 **Statistiques détaillées des recettes**
        - 📈 Analyses nutritionnelles avancées
        - 🌍 Exploration des tendances culinaires
        - ⭐ Système de recommandation personnalisé
        """)

        # Démarre le chargement des données et affiche un spinner
        Welcome.load_data()

        # Après le spinner, videz le conteneur d'écran de bienvenue
        welcome_placeholder.empty()

        # Affiche le contenu suivant (par exemple les données ou autres éléments après le chargement)
        st.markdown(
            "### 🎉 Voici le contenu suivant de l'application après le chargement des données !")
        # Affichez ici les autres éléments de votre application, comme les graphiques ou les analyses.
        # Par exemple :
        st.write("Les données sont maintenant prêtes à être analysées.")


if __name__ == "__main__":
    try:
        Welcome.show_welcom()
    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")
