# tp_bgdia700-develop/docs/source/conf.py

import os
import sys
import sphinx_rtd_theme

# Obtenir le chemin absolu du dossier contenant conf.py
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../src/pages')))
current_dir = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, os.path.abspath('../../src'))
# Chemin vers le répertoire racine du projet
project_dir = os.path.abspath(os.path.join(current_dir, '../..'))

# Ajouter le chemin racine du projet à sys.path
# sys.path.insert(0, os.path.abspath('../'))  # ou './' selon la structure de votre projet


project = "DOCUMENTATION DE L'APPLICATION KIT BIG DATA"
copyright = '2024, Paul, Alexandre, Alexandre, Julian'
author = 'Mbathe Mekontchou Paul, Alexandre Desgrées du Loû, Alexandre Movsessian, Julian Sliva'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'fr'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
autodoc_member_order = 'bysource'
autoclass_content = 'both'
