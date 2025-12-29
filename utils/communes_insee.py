"""
Module pour charger et gérer les données INSEE des communes
"""
import pandas as pd
import streamlit as st
from typing import Dict, Tuple, List, Optional


@st.cache_data
def load_communes_insee() -> pd.DataFrame:
    """
    Charge le fichier des communes INSEE
    
    Returns:
        DataFrame avec les communes françaises
    """
    try:
        df = pd.read_csv('insee/v_commune_2025.csv', encoding='utf-8', dtype=str)
        # Nettoyer les noms de colonnes
        df.columns = df.columns.str.strip()
        return df
    except UnicodeDecodeError:
        # Essayer avec latin-1 si utf-8 échoue
        try:
            df = pd.read_csv('insee/v_commune_2025.csv', encoding='latin-1', dtype=str)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Erreur de chargement du fichier communes: {e}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur: {e}")
        return pd.DataFrame()


def create_commune_search_dict(df_insee: pd.DataFrame) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Crée des dictionnaires pour la recherche de communes
    
    Args:
        df_insee: DataFrame INSEE des communes
    
    Returns:
        Tuple (code_to_name, name_to_code)
    """
    if df_insee.empty or 'COM' not in df_insee.columns or 'LIBELLE' not in df_insee.columns:
        return {}, {}
    
    # Filtrer uniquement les communes (TYPECOM = 'COM')
    df_communes = df_insee[df_insee['TYPECOM'] == 'COM'].copy()
    
    # Créer les dictionnaires
    code_to_name = {}
    name_to_code = {}
    
    for _, row in df_communes.iterrows():
        code = row['COM']
        libelle = row['LIBELLE']
        
        if pd.notna(code) and pd.notna(libelle):
            code_to_name[code] = libelle
            # Normaliser le nom pour la recherche
            name_normalized = libelle.lower().strip()
            name_to_code[name_normalized] = code
    
    return code_to_name, name_to_code


def search_communes(search_term: str, code_to_name: Dict[str, str], 
                    available_codes: List[str], max_results: int = 50) -> List[Tuple[str, str]]:
    """
    Recherche des communes par code INSEE ou nom
    
    Args:
        search_term: Terme de recherche
        code_to_name: Dictionnaire code INSEE -> nom
        available_codes: Liste des codes disponibles dans les données DVF
        max_results: Nombre maximum de résultats
    
    Returns:
        Liste de tuples (code, nom)
    """
    if not search_term:
        return []
    
    search_lower = search_term.lower().strip()
    results = []
    
    # Filtrer uniquement les communes disponibles dans les données DVF
    available_codes_set = set(available_codes)
    
    for code, nom in code_to_name.items():
        if code not in available_codes_set:
            continue
        
        # Recherche par code
        if search_lower in code.lower():
            results.append((code, nom))
        # Recherche par nom
        elif search_lower in nom.lower():
            results.append((code, nom))
        
        if len(results) >= max_results:
            break
    
    return sorted(results, key=lambda x: x[1])  # Trier par nom


def format_commune_option(code: str, nom: str) -> str:
    """
    Formate une option de commune pour l'affichage
    
    Args:
        code: Code INSEE
        nom: Nom de la commune
    
    Returns:
        Chaîne formatée
    """
    return f"{nom} ({code})"


def get_code_from_formatted(formatted: str) -> Optional[str]:
    """
    Extrait le code INSEE d'une option formatée
    
    Args:
        formatted: Chaîne formatée "Nom (code)"
    
    Returns:
        Code INSEE ou None
    """
    if not formatted or '(' not in formatted:
        return None
    
    try:
        return formatted.split('(')[-1].rstrip(')')
    except:
        return None
