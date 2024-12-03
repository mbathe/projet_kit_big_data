import streamlit as st

class Grille:
    """
    Classe pour organiser et afficher des graphiques dans une grille à l'aide de Streamlit.

    Cette classe permet de disposer plusieurs graphiques dans une grille structurée selon
    le nombre de lignes et de colonnes spécifié, avec des largeurs de colonnes personnalisées.

    Args:
        nb_lignes (int): Le nombre de lignes dans la grille.
        nb_colonnes (int): Le nombre de colonnes dans la grille.
        largeurs_colonnes (List[int]): Les poids relatifs des colonnes.

    Attributes:
        nb_lignes (int): Le nombre de lignes dans la grille.
        nb_colonnes (int): Le nombre de colonnes dans la grille.
        largeurs_colonnes (List[int]): Les poids relatifs des colonnes.

    """

    def __init__(self, nb_lignes, nb_colonnes, largeurs_colonnes):
        """
        Initialise une grille pour l'affichage des graphiques.

        Args:
            nb_lignes (int): Le nombre de lignes dans la grille.
            nb_colonnes (int): Le nombre de colonnes dans la grille.
            largeurs_colonnes (List[int]): Les poids relatifs des colonnes.
        """
        self.nb_lignes = nb_lignes
        self.nb_colonnes = nb_colonnes
        self.largeurs_colonnes = largeurs_colonnes  # Les poids relatifs des colonnes

    def afficher(self, graphiques):
        """
        Affiche une liste de graphiques dans la grille.

        Cette méthode organise les graphiques fournis dans une grille structurée selon
        le nombre de lignes et de colonnes définies lors de l'initialisation.

        Args:
            graphiques (List[Dict]): Liste de dictionnaires contenant les graphiques et leurs titres à afficher.

        Raises:
            AssertionError: Si le nombre de graphiques dépasse le nombre de cellules disponibles dans la grille.
        """
        assert len(graphiques) <= self.nb_lignes * self.nb_colonnes, "Pas assez de cellules pour afficher tous les graphiques."
        idx_graphique = 0
        for ligne in range(self.nb_lignes):
            colonnes = st.columns(self.largeurs_colonnes)
            for col in range(self.nb_colonnes):
                if idx_graphique < len(graphiques):
                    with colonnes[col]:
                        # Conteneur pour le style personnalisé
                        container = st.container()
                        with container:
                            if graphiques[idx_graphique]['titre']:
                                st.write(f"{graphiques[idx_graphique]['titre']}")
                            graphiques[idx_graphique]['graphique'].afficher()
                        # Ajouter une classe personnalisée au conteneur
                        container.markdown('<div class="graph-container"></div>', unsafe_allow_html=True)
                    idx_graphique += 1
