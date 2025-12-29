"""
Module de chargement et normalisation des données DVF (Demandes de Valeurs Foncières)
"""
import pandas as pd
import os
from typing import Optional, List, Dict
import streamlit as st

@st.cache_data
def load_dvf_data(years: Optional[List[int]] = None) -> pd.DataFrame:
    """
    Charge les données DVF pour les années spécifiées
    
    Args:
        years: Liste des années à charger (ex: [2022, 2023, 2024])
              Si None, charge toutes les années disponibles
    
    Returns:
        DataFrame avec les données DVF normalisées
    """
    data_dir = "data"
    all_data = []
    
    if years is None:
        years = [2017, 2022, 2023, 2024]
    
    for year in years:
        file_path = os.path.join(data_dir, f"dvf{year}.csv")
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                
                # Normaliser les noms de colonnes
                df.columns = df.columns.str.lower().str.strip()
                
                # Mapper les anciennes colonnes vers les nouvelles
                column_mapping = {
                    'annee': 'annee',
                    'année': 'annee',
                    'insee_com': 'insee_com',
                    'nb_mutations': 'nb_mutations',
                    'nbmaisons': 'nb_maisons',
                    'nbapparts': 'nb_apparts',
                    'propmaison': 'prop_maison',
                    'propappart': 'prop_appart',
                    'prixmoyen': 'prix_moyen',
                    'prixm2moyen': 'prix_m2_moyen',
                    'surfacemoy': 'surface_moy'
                }
                
                df = df.rename(columns=column_mapping)
                
                # Assurer que la colonne année existe
                if 'annee' not in df.columns:
                    df['annee'] = year
                
                all_data.append(df)
            except Exception as e:
                st.warning(f"Erreur lors du chargement de {file_path}: {e}")
    
    if not all_data:
        return pd.DataFrame()
    
    # Combiner toutes les données
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Nettoyer et convertir les types
    numeric_cols = ['nb_mutations', 'nb_maisons', 'nb_apparts', 
                    'prop_maison', 'prop_appart', 'prix_moyen', 
                    'prix_m2_moyen', 'surface_moy']
    
    for col in numeric_cols:
        if col in combined_df.columns:
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
    
    return combined_df


@st.cache_data
def get_communes_list(df: pd.DataFrame) -> List[str]:
    """Retourne la liste des codes INSEE des communes disponibles"""
    if 'insee_com' in df.columns:
        return sorted(df['insee_com'].dropna().unique().astype(str).tolist())
    return []


def get_commune_data(df: pd.DataFrame, insee_code: str) -> pd.DataFrame:
    """
    Récupère les données d'une commune spécifique
    
    Args:
        df: DataFrame DVF complet
        insee_code: Code INSEE de la commune
    
    Returns:
        DataFrame filtré pour la commune
    """
    return df[df['insee_com'].astype(str) == str(insee_code)].copy()


def get_market_stats(df: pd.DataFrame, commune: Optional[str] = None, 
                     property_type: str = 'all') -> Dict:
    """
    Calcule les statistiques du marché immobilier
    
    Args:
        df: DataFrame DVF
        commune: Code INSEE de la commune (None = toutes)
        property_type: 'all', 'maisons', 'appartements'
    
    Returns:
        Dictionnaire avec les statistiques
    """
    if commune:
        df = get_commune_data(df, commune)
    
    if df.empty:
        return {}
    
    # Filtrer par type de bien
    if property_type == 'maisons' and 'nb_maisons' in df.columns:
        df = df[df['nb_maisons'] > 0]
    elif property_type == 'appartements' and 'nb_apparts' in df.columns:
        df = df[df['nb_apparts'] > 0]
    
    stats = {}
    
    if 'prix_moyen' in df.columns:
        stats['prix_moyen'] = df['prix_moyen'].mean()
        stats['prix_median'] = df['prix_moyen'].median()
        stats['prix_min'] = df['prix_moyen'].min()
        stats['prix_max'] = df['prix_moyen'].max()
    
    if 'prix_m2_moyen' in df.columns:
        stats['prix_m2_moyen'] = df['prix_m2_moyen'].mean()
        stats['prix_m2_median'] = df['prix_m2_moyen'].median()
        stats['prix_m2_min'] = df['prix_m2_moyen'].min()
        stats['prix_m2_max'] = df['prix_m2_moyen'].max()
    
    if 'surface_moy' in df.columns:
        stats['surface_moyenne'] = df['surface_moy'].mean()
        stats['surface_mediane'] = df['surface_moy'].median()
    
    if 'nb_mutations' in df.columns:
        stats['total_mutations'] = df['nb_mutations'].sum()
    
    return stats


def calculate_market_evolution(df: pd.DataFrame, commune: Optional[str] = None) -> pd.DataFrame:
    """
    Calcule l'évolution du marché année par année
    
    Args:
        df: DataFrame DVF
        commune: Code INSEE de la commune (None = toutes)
    
    Returns:
        DataFrame avec l'évolution annuelle
    """
    if commune:
        df = get_commune_data(df, commune)
    
    if df.empty or 'annee' not in df.columns:
        return pd.DataFrame()
    
    evolution = df.groupby('annee').agg({
        'prix_moyen': 'mean',
        'prix_m2_moyen': 'mean',
        'surface_moy': 'mean',
        'nb_mutations': 'sum'
    }).reset_index()
    
    # Calculer les variations annuelles
    evolution['variation_prix'] = evolution['prix_moyen'].pct_change() * 100
    evolution['variation_prix_m2'] = evolution['prix_m2_moyen'].pct_change() * 100
    
    return evolution


@st.cache_data
def get_departement_data(df: pd.DataFrame, dept_code: str) -> pd.DataFrame:
    """
    Récupère les données d'un département
    
    Args:
        df: DataFrame DVF
        dept_code: Code du département (ex: '75', '69')
    
    Returns:
        DataFrame filtré pour le département
    """
    if 'insee_com' in df.columns:
        # Extraire les 2 ou 3 premiers caractères selon le département
        mask = df['insee_com'].astype(str).str.startswith(dept_code)
        return df[mask].copy()
    return pd.DataFrame()


def get_top_communes(df: pd.DataFrame, metric: str = 'prix_m2_moyen', 
                     top_n: int = 10, ascending: bool = False) -> pd.DataFrame:
    """
    Récupère le top N des communes selon une métrique
    
    Args:
        df: DataFrame DVF
        metric: Métrique à utiliser pour le classement
        top_n: Nombre de communes à retourner
        ascending: Ordre croissant (True) ou décroissant (False)
    
    Returns:
        DataFrame avec le classement
    """
    if metric not in df.columns or 'insee_com' not in df.columns:
        return pd.DataFrame()
    
    # Grouper par commune et calculer la moyenne
    top = df.groupby('insee_com').agg({
        metric: 'mean',
        'nb_mutations': 'sum'
    }).reset_index()
    
    # Trier et prendre le top N
    top = top.nlargest(top_n, metric) if not ascending else top.nsmallest(top_n, metric)
    
    return top
