recipe_columns_description = {
    "Colonne": [
        "**nom**",
        "**identifiant**",
        "**minutes**",
        "**contributeur_id**",
        "**soumis**",
        "**balises**",
        "**nutrition**",
        "**n_étapes**",
        "**mesures**",
        "**description**"
    ],
    "Description": [
        "Nom de la recette",
        "ID de la recette",
        "Minutes pour préparer la recette",
        "ID utilisateur qui a soumis cette recette",
        "Date à laquelle la recette a été soumise",
        "Balises Food.com pour la recette",
        """Informations nutritionnelles sous la forme `[calories (#), matières grasses totales (PDV), sucre (PDV), sodium (PDV), protéines (PDV), graisses saturées (PDV), glucides (PDV)]` ; 
                    PDV signifie « pourcentage de la valeur quotidienne »""",
        "Nombre d'étapes dans la recette",
        "Texte pour les étapes de la recette, dans l'ordre",
        "Description de la recette"
    ]
}

mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']


submissions_data = {
    'submissions_per_year': {1999: 2054, 2000: 1038, 2001: 4682, 2002: 20056, 2003: 18000, 2004: 16601, 2005: 23865, 2006: 27260, 2007: 34299, 2008: 30745, 2009: 22547, 2010: 11902, 2011: 7573, 2012: 5187, 2013: 3792, 2014: 1049, 2015: 306, 2016: 204, 2017: 288, 2018: 189},
    'submissions_per_month': {1: 21856, 2: 18536, 3: 20571, 4: 20186, 5: 21684, 6: 18726, 7: 18584, 8: 18866, 9: 18631, 10: 19131, 11: 18771, 12: 16095},
    'submissions_per_weekday': {0: 48087, 1: 42757, 2: 37537, 3: 35823, 4: 29612, 5: 16624, 6: 21197}
}
