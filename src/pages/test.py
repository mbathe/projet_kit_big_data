import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Analyse des Soumissions", layout="wide")

# Données
submissions_per_year = {1999: 2054, 2000: 1038, 2001: 4682, 2002: 20056, 2003: 18000,
                        2004: 16601, 2005: 23865, 2006: 27260, 2007: 34299, 2008: 30745,
                        2009: 22547, 2010: 11902, 2011: 7573, 2012: 5187, 2013: 3792,
                        2014: 1049, 2015: 306, 2016: 204, 2017: 288, 2018: 189}

submissions_per_month = {1: 21856, 2: 18536, 3: 20571, 4: 20186, 5: 21684, 6: 18726,
                         7: 18584, 8: 18866, 9: 18631, 10: 19131, 11: 18771, 12: 16095}

submissions_per_weekday = {0: 48087, 1: 42757,
                           2: 37537, 3: 35823, 4: 29612, 5: 16624, 6: 21197}

# Conversion en DataFrames
df_year = pd.DataFrame(list(submissions_per_year.items()),
                       columns=['Année', 'Soumissions'])
df_month = pd.DataFrame(list(submissions_per_month.items()), columns=[
                        'Mois', 'Soumissions'])
df_weekday = pd.DataFrame(list(submissions_per_weekday.items()), columns=[
                          'Jour', 'Soumissions'])

# Ajout des noms des jours
jours = ['Lundi', 'Mardi', 'Mercredi',
         'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
df_weekday['Nom du Jour'] = df_weekday['Jour'].map(lambda x: jours[x])

# Ajout des noms des mois
mois = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
df_month['Nom du Mois'] = df_month['Mois'].map(lambda x: mois[x-1])

# Titre de l'application
st.title("📊 Analyse des Soumissions")

# Informations générales
st.header("📅 Période d'analyse")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Date de début", "6 août 1999")
with col2:
    st.metric("Date de fin", "4 décembre 2018")
with col3:
    st.metric("Nombre total de jours", "7060")

# Création des onglets
tab1, tab2, tab3 = st.tabs(
    ["📈 Par Année", "📅 Par Mois", "📆 Par Jour de la Semaine"])

with tab1:
    st.subheader("Distribution des soumissions par année")

    # Graphique des soumissions par année
    fig_year = px.line(df_year, x='Année', y='Soumissions',
                       title='Évolution des soumissions par année',
                       markers=True)
    st.plotly_chart(fig_year, use_container_width=True)

    # Tableau des données par année
    st.dataframe(df_year.style.highlight_max(subset=['Soumissions'], color='lightgreen')
                 .highlight_min(subset=['Soumissions'], color='lightpink'),
                 hide_index=True)

with tab2:
    st.subheader("Distribution des soumissions par mois")

    # Graphique des soumissions par mois
    fig_month = px.bar(df_month, x='Nom du Mois', y='Soumissions',
                       title='Distribution des soumissions par mois')
    st.plotly_chart(fig_month, use_container_width=True)

    # Tableau des données par mois
    st.dataframe(df_month[['Nom du Mois', 'Soumissions']]
                 .style.highlight_max(subset=['Soumissions'], color='lightgreen')
                 .highlight_min(subset=['Soumissions'], color='lightpink'),
                 hide_index=True)

with tab3:
    st.subheader("Distribution des soumissions par jour de la semaine")

    # Graphique des soumissions par jour de la semaine
    fig_weekday = px.bar(df_weekday, x='Nom du Jour', y='Soumissions',
                         title='Distribution des soumissions par jour de la semaine')
    st.plotly_chart(fig_weekday, use_container_width=True)

    # Tableau des données par jour
    st.dataframe(df_weekday[['Nom du Jour', 'Soumissions']]
                 .style.highlight_max(subset=['Soumissions'], color='lightgreen')
                 .highlight_min(subset=['Soumissions'], color='lightpink'),
                 hide_index=True)
