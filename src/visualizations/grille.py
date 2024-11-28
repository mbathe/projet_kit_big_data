import streamlit as st

class Grille:
    def __init__(self, nb_lignes, nb_colonnes, largeurs_colonnes):
        self.nb_lignes = nb_lignes
        self.nb_colonnes = nb_colonnes
        self.largeurs_colonnes = largeurs_colonnes  # Les poids relatifs des colonnes

    def afficher(self, graphiques):
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
                            if graphiques[idx_graphique]['titre'] : 
                                st.write(f"{graphiques[idx_graphique]['titre']}")
                            graphiques[idx_graphique]['graphique'].afficher()
                        # Ajouter une classe personnalisée au conteneur
                        container.markdown('<div class="graph-container"></div>', unsafe_allow_html=True)
                    idx_graphique += 1
