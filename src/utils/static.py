import pandas as pd
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


constribution_data = {
    'total_contributors': 27926,
    'contributions_per_user': {
        'mean': 8.29,
        'median': 1.0,
        'max': 3118
    },
    'top_contributors': {
        89831: 3118,
        37779: 2553,
        37449: 2493,
        1533: 1595,
        58104: 1522,
        169430: 1378,
        4470: 1125,
        80353: 1104,
        283251: 1004,
        21752: 971
    }
}


expected_data_complexity = {'steps_stats': {'mean': 9.7654994668382, 'median': 9.0, 'min': 0, 'max': 145, 'distribution': {0: 1, 1: 2442, 2: 6982, 3: 11461, 4: 14753, 5: 18047, 6: 19927, 7: 20785, 8: 19980, 9: 18265, 10: 16272, 11: 14131, 12: 11940, 13: 10137, 14: 8297, 15: 6759, 16: 5522, 17: 4640, 18: 3621, 19: 3184, 20: 2468, 21: 2005, 22: 1683, 23: 1334, 24: 1128, 25: 926, 26: 791, 27: 654, 28: 545, 29: 428, 30: 364, 31: 298, 32: 244, 33: 233, 34: 182, 35: 149, 36: 139, 37: 107, 38: 100, 39: 85, 40: 80, 41: 74, 42: 50, 43: 40, 44: 45, 45: 42, 46: 28,
                                                                                                                           47: 30, 48: 27, 49: 30, 50: 15, 51: 14, 52: 9, 53: 15, 54: 9, 55: 19, 56: 9, 57: 9, 58: 6, 59: 5, 60: 5, 61: 5, 62: 6, 63: 6, 64: 4, 65: 3, 66: 3, 67: 2, 68: 1, 69: 2, 70: 4, 71: 1, 72: 1, 73: 2, 75: 1, 76: 3, 77: 1, 79: 1, 80: 1, 81: 3, 82: 3, 85: 1, 86: 1, 87: 1, 88: 2, 90: 1, 93: 1, 97: 1, 98: 1, 100: 1, 108: 1, 110: 1, 113: 1, 145: 1}}, 'time_stats': {'mean_minutes': 9398.546009488984, 'median_minutes': 40.0, 'min_minutes': 0, 'max_minutes': 2147483647, 'time_ranges': {'30-60min': 70077, '15-30min': 55131, '0-15min': 42828, '1-2h': 36683, '>2h': 25824}}}


expected_data_temporal_distribution = {
    'date_min': pd.Timestamp('1999-08-06 00:00:00'),
    'date_max': pd.Timestamp('2018-12-04 00:00:00'),
    'total_days': 7060,
    'submissions_per_year': {
        1999: 2054,
        2000: 1038,
        2001: 4682,
        2002: 20056,
        2003: 18000,
        2004: 16601,
        2005: 23865,
        2006: 27260,
        2007: 34299,
        2008: 30745,
        2009: 22547,
        2010: 11902,
        2011: 7573,
        2012: 5187,
        2013: 3792,
        2014: 1049,
        2015: 306,
        2016: 204,
        2017: 288,
        2018: 189
    },
    'submissions_per_month': {
        1: 21856,
        2: 18536,
        3: 20571,
        4: 20186,
        5: 21684,
        6: 18726,
        7: 18584,
        8: 18866,
        9: 18631,
        10: 19131,
        11: 18771,
        12: 16095
    },
    'submissions_per_weekday': {
        0: 48087,
        1: 42757,
        2: 37537,
        3: 35823,
        4: 29612,
        5: 16624,
        6: 21197
    }
}

expected_tags_data = {'total_unique_tags': 545, 'most_common_tags': {'preparation': 215092, 'time-to-make': 210244, 'course': 203750, 'main-ingredient': 158748, 'dietary': 154295, 'easy': 120799, 'occasion': 105986, 'cuisine': 83885, 'low-in-something': 80928, 'main-dish': 65893, '60-minutes-or-less': 65528,
                                                                     'equipment': 65090, 'number-of-servings': 54779, '30-minutes-or-less': 52811, 'meat': 51612, 'vegetables': 50004, 'taste-mood': 48848, 'north-american': 44725, '4-hours-or-less': 44145, '3-steps-or-less': 43324}, 'tags_per_recipe': {'mean': 17.8970418036202, 'median': 17.0, 'min': 1, 'max': 73}}


expected_nutrition_data = {'calories': {'mean': 447.1033141772491, 'median': 299.1, 'min': 0.0, 'max': 434360.2, 'quartiles': {0.25: 167.3, 0.5: 299.1, 0.75: 492.8}}, 'total_fat': {'mean': 34.11962363243608, 'median': 19.0, 'min': 0.0, 'max': 17183.0, 'quartiles': {0.25: 8.0, 0.5: 19.0, 0.75: 39.0}}, 'sugar': {'mean': 81.80831688471997, 'median': 24.0, 'min': 0.0, 'max': 362729.0, 'quartiles': {0.25: 9.0, 0.5: 24.0, 0.75: 66.0}}, 'sodium': {'mean': 27.370085066988068, 'median': 13.0,
                                                                                                                                                                                                                                                                                                                                                                                                                                                             'min': 0.0, 'max': 14664.0, 'quartiles': {0.25: 4.0, 0.5: 13.0, 0.75: 31.0}}, 'protein': {'mean': 31.406551497260505, 'median': 17.0, 'min': 0.0, 'max': 6552.0, 'quartiles': {0.25: 6.0, 0.5: 17.0, 0.75: 47.0}}, 'saturated_fat': {'mean': 43.05071413183345, 'median': 21.0, 'min': 0.0, 'max': 10395.0, 'quartiles': {0.25: 6.0, 0.5: 21.0, 0.75: 50.0}}, 'carbohydrates': {'mean': 14.87129906199235, 'median': 8.0, 'min': 0.0, 'max': 36098.0, 'quartiles': {0.25: 4.0, 0.5: 8.0, 0.75: 16.0}}}
