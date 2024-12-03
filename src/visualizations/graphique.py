class Graphique:
    """
    Classe de base pour les graphiques.

    Cette classe sert de base pour différents types de graphiques. Elle stocke les données nécessaires
    et définit une méthode abstraite pour l'affichage, qui doit être implémentée par les classes dérivées.

    Args:
        data (Any): Les données à afficher dans le graphique.

    Attributes:
        data (Any): Les données à afficher dans le graphique.

    """

    def __init__(self, data):
        """
        Initialise un objet Graphique.

        Args:
            data (Any): Les données à afficher dans le graphique.
        """
        self.data = data

    def afficher(self):
        """
        Méthode abstraite pour afficher le graphique.

        Doit être implémentée par les classes dérivées.
        """
        pass
