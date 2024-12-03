import streamlit as st

def load_css(path):
    """
    Charge et applique un fichier CSS personnalisé dans l'application Streamlit.

    Cette fonction lit le contenu d'un fichier CSS spécifié par le chemin fourni et l'applique
    à l'application Streamlit en injectant le CSS dans le HTML de la page. Si le fichier n'est pas
    trouvé, une erreur est affichée dans l'interface Streamlit.

    Args:
        path (str): Le chemin vers le fichier CSS à charger.

    Raises:
        FileNotFoundError: Si le fichier CSS spécifié n'est pas trouvé.
    """
    try:
        with open(path) as f:
            css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Le fichier CSS n'a pas été trouvé : {path}")
