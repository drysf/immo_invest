"""
Module d'analyse du marché immobilier avec données DVF
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import streamlit as st


def analyze_price_trends(df: pd.DataFrame, commune: Optional[str] = None) -> Dict:
    """
    Analyse les tendances de prix sur plusieurs années
    
    Args:
        df: DataFrame DVF
        commune: Code INSEE de la commune (None = toutes)
    
    Returns:
        Dictionnaire avec les tendances
    """
    if commune:
        from utils.dvf_loader import get_commune_data
        df = get_commune_data(df, commune)
    
    if df.empty or 'annee' not in df.columns:
        return {}
    
    # Calculer les moyennes par année
    yearly_avg = df.groupby('annee').agg({
        'prix_moyen': 'mean',
        'prix_m2_moyen': 'mean',
        'nb_mutations': 'sum'
    }).reset_index()
    
    if len(yearly_avg) < 2:
        return {'tendance': 'Données insuffisantes'}
    
    # Calculer les variations
    variation_prix = yearly_avg['prix_moyen'].pct_change().mean() * 100
    variation_prix_m2 = yearly_avg['prix_m2_moyen'].pct_change().mean() * 100
    
    # Tendance générale (régression linéaire simple)
    if 'prix_m2_moyen' in yearly_avg.columns:
        years = yearly_avg['annee'].values
        prices = yearly_avg['prix_m2_moyen'].values
        
        # Régression linéaire
        z = np.polyfit(years, prices, 1)
        tendance_slope = z[0]
        
        if tendance_slope > 50:
            tendance = "Forte hausse"
        elif tendance_slope > 0:
            tendance = "Hausse modérée"
        elif tendance_slope > -50:
            tendance = "Baisse modérée"
        else:
            tendance = "Forte baisse"
    else:
        tendance = "Indéterminée"
    
    return {
        'variation_prix_annuelle': variation_prix,
        'variation_prix_m2_annuelle': variation_prix_m2,
        'tendance': tendance,
        'nombre_annees': len(yearly_avg),
        'evolution': yearly_avg
    }


def calculate_market_liquidity(df: pd.DataFrame, commune: Optional[str] = None) -> Dict:
    """
    Calcule des indicateurs de liquidité du marché
    
    Args:
        df: DataFrame DVF
        commune: Code INSEE de la commune
    
    Returns:
        Dictionnaire avec indicateurs de liquidité
    """
    if commune:
        from utils.dvf_loader import get_commune_data
        df = get_commune_data(df, commune)
    
    if df.empty:
        return {}
    
    # Nombre de transactions
    total_transactions = df['nb_mutations'].sum() if 'nb_mutations' in df.columns else 0
    
    # Transactions par année
    if 'annee' in df.columns:
        annees_uniques = df['annee'].nunique()
        transactions_par_an = total_transactions / annees_uniques if annees_uniques > 0 else 0
    else:
        transactions_par_an = 0
    
    # Volume du marché
    if 'prix_moyen' in df.columns and 'nb_mutations' in df.columns:
        volume_total = (df['prix_moyen'] * df['nb_mutations']).sum()
    else:
        volume_total = 0
    
    # Évaluer la liquidité
    if transactions_par_an > 100:
        liquidite = "Très liquide"
    elif transactions_par_an > 50:
        liquidite = "Liquide"
    elif transactions_par_an > 20:
        liquidite = "Moyennement liquide"
    else:
        liquidite = "Peu liquide"
    
    return {
        'total_transactions': total_transactions,
        'transactions_par_an': transactions_par_an,
        'volume_total': volume_total,
        'evaluation_liquidite': liquidite
    }


def compare_to_market(prix_m2: float, df: pd.DataFrame, 
                     commune: Optional[str] = None) -> Dict:
    """
    Compare un prix au m² avec le marché
    
    Args:
        prix_m2: Prix au m² à comparer
        df: DataFrame DVF
        commune: Code INSEE de la commune
    
    Returns:
        Dictionnaire avec la comparaison
    """
    if commune:
        from utils.dvf_loader import get_commune_data
        df = get_commune_data(df, commune)
    
    if df.empty or 'prix_m2_moyen' not in df.columns:
        return {'statut': 'Données insuffisantes'}
    
    # Statistiques du marché
    prix_m2_marche = df['prix_m2_moyen'].mean()
    prix_m2_median = df['prix_m2_moyen'].median()
    prix_m2_std = df['prix_m2_moyen'].std()
    
    # Écart par rapport à la moyenne
    ecart_pct = ((prix_m2 - prix_m2_marche) / prix_m2_marche) * 100
    
    # Positionnement
    if prix_m2 < prix_m2_median * 0.8:
        positionnement = "Bien en dessous du marché"
        evaluation = "Excellent prix"
    elif prix_m2 < prix_m2_median:
        positionnement = "En dessous du marché"
        evaluation = "Bon prix"
    elif prix_m2 < prix_m2_median * 1.2:
        positionnement = "Dans la moyenne du marché"
        evaluation = "Prix correct"
    else:
        positionnement = "Au-dessus du marché"
        evaluation = "Prix élevé"
    
    return {
        'prix_m2_analyse': prix_m2,
        'prix_m2_marche': prix_m2_marche,
        'prix_m2_median': prix_m2_median,
        'ecart_pourcentage': ecart_pct,
        'positionnement': positionnement,
        'evaluation': evaluation
    }


def find_similar_properties(surface: float, df: pd.DataFrame,
                           commune: Optional[str] = None,
                           tolerance: float = 0.2) -> pd.DataFrame:
    """
    Trouve les biens similaires dans la base DVF
    
    Args:
        surface: Surface du bien
        df: DataFrame DVF
        commune: Code INSEE de la commune
        tolerance: Tolérance de surface (20% par défaut)
    
    Returns:
        DataFrame avec les biens similaires
    """
    if commune:
        from utils.dvf_loader import get_commune_data
        df = get_commune_data(df, commune)
    
    if df.empty or 'surface_moy' not in df.columns:
        return pd.DataFrame()
    
    # Filtrer par surface similaire
    surface_min = surface * (1 - tolerance)
    surface_max = surface * (1 + tolerance)
    
    similar = df[
        (df['surface_moy'] >= surface_min) & 
        (df['surface_moy'] <= surface_max)
    ].copy()
    
    return similar


def calculate_market_score(df: pd.DataFrame, commune: str) -> Dict:
    """
    Calcule un score global du marché pour une commune
    
    Args:
        df: DataFrame DVF
        commune: Code INSEE de la commune
    
    Returns:
        Dictionnaire avec le score et ses composantes
    """
    from utils.dvf_loader import get_commune_data
    df_commune = get_commune_data(df, commune)
    
    if df_commune.empty:
        return {'score': 0, 'appreciation': 'Données insuffisantes'}
    
    score = 0
    details = {}
    
    # 1. Liquidité (0-25 points)
    liquidite = calculate_market_liquidity(df, commune)
    if liquidite.get('transactions_par_an', 0) > 100:
        score += 25
        details['liquidite'] = 'Excellent'
    elif liquidite.get('transactions_par_an', 0) > 50:
        score += 20
        details['liquidite'] = 'Bon'
    elif liquidite.get('transactions_par_an', 0) > 20:
        score += 15
        details['liquidite'] = 'Moyen'
    else:
        score += 10
        details['liquidite'] = 'Faible'
    
    # 2. Tendance des prix (0-35 points)
    trends = analyze_price_trends(df, commune)
    variation = trends.get('variation_prix_m2_annuelle', 0)
    if variation > 5:
        score += 35
        details['tendance'] = 'Forte croissance'
    elif variation > 2:
        score += 30
        details['tendance'] = 'Croissance'
    elif variation > 0:
        score += 25
        details['tendance'] = 'Stable positif'
    elif variation > -2:
        score += 15
        details['tendance'] = 'Stable'
    else:
        score += 5
        details['tendance'] = 'Baisse'
    
    # 3. Volume du marché (0-20 points)
    volume = liquidite.get('volume_total', 0)
    if volume > 10000000:  # > 10M€
        score += 20
        details['volume'] = 'Très important'
    elif volume > 5000000:
        score += 15
        details['volume'] = 'Important'
    elif volume > 1000000:
        score += 10
        details['volume'] = 'Moyen'
    else:
        score += 5
        details['volume'] = 'Faible'
    
    # 4. Stabilité (0-20 points)
    if 'prix_m2_moyen' in df_commune.columns:
        std = df_commune['prix_m2_moyen'].std()
        mean = df_commune['prix_m2_moyen'].mean()
        cv = (std / mean * 100) if mean > 0 else 100
        
        if cv < 10:
            score += 20
            details['stabilite'] = 'Très stable'
        elif cv < 20:
            score += 15
            details['stabilite'] = 'Stable'
        elif cv < 30:
            score += 10
            details['stabilite'] = 'Variable'
        else:
            score += 5
            details['stabilite'] = 'Très variable'
    
    # Appréciation globale
    if score >= 85:
        appreciation = "Excellent marché"
    elif score >= 70:
        appreciation = "Bon marché"
    elif score >= 55:
        appreciation = "Marché correct"
    elif score >= 40:
        appreciation = "Marché moyen"
    else:
        appreciation = "Marché difficile"
    
    return {
        'score': score,
        'score_max': 100,
        'appreciation': appreciation,
        'details': details
    }


def get_investment_recommendation(df: pd.DataFrame, commune: str,
                                 prix_m2: float, surface: float) -> Dict:
    """
    Génère une recommandation d'investissement basée sur les données du marché
    
    Args:
        df: DataFrame DVF
        commune: Code INSEE de la commune
        prix_m2: Prix au m² envisagé
        surface: Surface du bien
    
    Returns:
        Dictionnaire avec la recommandation
    """
    # Analyser le marché
    market_score = calculate_market_score(df, commune)
    comparison = compare_to_market(prix_m2, df, commune)
    trends = analyze_price_trends(df, commune)
    
    # Score global de recommandation
    score = market_score.get('score', 50)
    
    # Ajuster selon le prix
    ecart = comparison.get('ecart_pourcentage', 0)
    if ecart < -20:
        score += 10  # Bonus pour prix très avantageux
    elif ecart > 20:
        score -= 10  # Malus pour prix élevé
    
    # Recommandation
    if score >= 80:
        recommandation = "Fortement recommandé"
        couleur = "success"
    elif score >= 65:
        recommandation = "Recommandé"
        couleur = "success"
    elif score >= 50:
        recommandation = "À considérer"
        couleur = "warning"
    elif score >= 35:
        recommandation = "Prudence requise"
        couleur = "warning"
    else:
        recommandation = "Non recommandé"
        couleur = "error"
    
    return {
        'recommandation': recommandation,
        'score': score,
        'couleur': couleur,
        'market_score': market_score,
        'price_comparison': comparison,
        'trends': trends
    }
