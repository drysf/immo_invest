"""
Module de calculs financiers avancés pour l'investissement immobilier
"""
import numpy as np
from typing import Dict, List, Tuple
import pandas as pd


def calculate_loan_schedule(principal: float, annual_rate: float, 
                            years: int) -> pd.DataFrame:
    """
    Calcule le tableau d'amortissement du prêt
    
    Args:
        principal: Montant emprunté
        annual_rate: Taux annuel (en %)
        years: Durée en années
    
    Returns:
        DataFrame avec le détail mois par mois
    """
    if annual_rate == 0 or years == 0:
        return pd.DataFrame()
    
    monthly_rate = annual_rate / 100 / 12
    n_payments = years * 12
    
    # Calcul de la mensualité
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**n_payments) / \
                     ((1 + monthly_rate)**n_payments - 1)
    
    schedule = []
    remaining_balance = principal
    
    for month in range(1, n_payments + 1):
        interest = remaining_balance * monthly_rate
        principal_payment = monthly_payment - interest
        remaining_balance -= principal_payment
        
        schedule.append({
            'Mois': month,
            'Mensualité': monthly_payment,
            'Intérêts': interest,
            'Capital': principal_payment,
            'Capital Restant': max(0, remaining_balance)
        })
    
    return pd.DataFrame(schedule)


def calculate_irr(cashflows: List[float]) -> float:
    """
    Calcule le Taux de Rendement Interne (TRI/IRR)
    
    Args:
        cashflows: Liste des flux de trésorerie (investissement initial négatif)
    
    Returns:
        TRI en pourcentage
    """
    try:
        irr = np.irr(cashflows)
        return irr * 100
    except:
        return 0.0


def calculate_npv(cashflows: List[float], discount_rate: float) -> float:
    """
    Calcule la Valeur Actuelle Nette (VAN/NPV)
    
    Args:
        cashflows: Liste des flux de trésorerie
        discount_rate: Taux d'actualisation (en %)
    
    Returns:
        VAN
    """
    rate = discount_rate / 100
    npv = sum(cf / (1 + rate)**i for i, cf in enumerate(cashflows))
    return npv


def calculate_tax_lmnp(revenus_locatifs: float, charges_deductibles: float,
                       amortissement: float = 0) -> Dict:
    """
    Calcule l'imposition en régime LMNP (Location Meublée Non Professionnelle)
    
    Args:
        revenus_locatifs: Revenus locatifs annuels
        charges_deductibles: Charges déductibles (intérêts, travaux, etc.)
        amortissement: Montant de l'amortissement annuel
    
    Returns:
        Dictionnaire avec les détails fiscaux
    """
    # Régime réel simplifié
    revenus_imposables = revenus_locatifs - charges_deductibles - amortissement
    revenus_imposables = max(0, revenus_imposables)
    
    # Abattement micro-BIC (50% avec plafond de 77 700€)
    abattement_micro = min(revenus_locatifs * 0.5, 77700 * 0.5)
    revenus_micro = max(0, revenus_locatifs - abattement_micro)
    
    return {
        'revenus_locatifs': revenus_locatifs,
        'charges_deductibles': charges_deductibles,
        'amortissement': amortissement,
        'revenus_imposables_reel': revenus_imposables,
        'revenus_imposables_micro': revenus_micro,
        'economie_reel_vs_micro': revenus_micro - revenus_imposables
    }


def calculate_tax_pinel(prix_acquisition: float, zone: str, duree: int = 6) -> Dict:
    """
    Calcule la réduction d'impôt Pinel
    
    Args:
        prix_acquisition: Prix d'acquisition du bien
        zone: Zone Pinel ('A', 'A bis', 'B1')
        duree: Durée de l'engagement (6, 9 ou 12 ans)
    
    Returns:
        Dictionnaire avec les réductions fiscales
    """
    # Plafond de prix et de surface
    plafond = 300000  # €
    prix_retenu = min(prix_acquisition, plafond)
    
    # Taux de réduction selon la durée
    if duree == 6:
        taux = 0.12  # 12% sur 6 ans (2% par an)
    elif duree == 9:
        taux = 0.18  # 18% sur 9 ans (2% pendant 6 ans + 1% pendant 3 ans)
    elif duree == 12:
        taux = 0.21  # 21% sur 12 ans (2% pendant 6 ans + 1% pendant 6 ans)
    else:
        taux = 0.12
    
    reduction_totale = prix_retenu * taux
    reduction_annuelle = reduction_totale / duree
    
    return {
        'prix_acquisition': prix_acquisition,
        'prix_retenu': prix_retenu,
        'zone': zone,
        'duree': duree,
        'reduction_totale': reduction_totale,
        'reduction_annuelle': reduction_annuelle,
        'plafond_loyer': get_plafond_loyer_pinel(zone)
    }


def get_plafond_loyer_pinel(zone: str) -> float:
    """Retourne le plafond de loyer au m² pour la zone Pinel"""
    plafonds = {
        'A bis': 18.25,
        'A': 13.56,
        'B1': 10.93,
        'B2': 9.50
    }
    return plafonds.get(zone, 10.93)


def calculate_wealth_tax(patrimoine_net: float) -> float:
    """
    Calcule l'IFI (Impôt sur la Fortune Immobilière)
    
    Args:
        patrimoine_net: Patrimoine immobilier net
    
    Returns:
        Montant de l'IFI
    """
    if patrimoine_net < 1300000:
        return 0
    
    # Barème IFI 2024
    tranches = [
        (800000, 0.0),
        (510000, 0.005),  # 1 300 000 à 1 810 000
        (540000, 0.007),  # 1 810 000 à 2 350 000
        (650000, 0.010),  # 2 350 000 à 3 000 000
        (1000000, 0.0125), # 3 000 000 à 4 000 000
        (6000000, 0.015),  # 4 000 000 à 10 000 000
        (float('inf'), 0.0175)  # > 10 000 000
    ]
    
    ifi = 0
    base = patrimoine_net - 800000  # Abattement de 800 000€
    cumul = 0
    
    for montant_tranche, taux in tranches:
        tranche_imposable = min(base - cumul, montant_tranche)
        if tranche_imposable <= 0:
            break
        ifi += tranche_imposable * taux
        cumul += montant_tranche
    
    return ifi


def calculate_income_tax(revenus_imposables: float, parts: float = 1.0) -> float:
    """
    Calcule l'impôt sur le revenu (approximatif)
    
    Args:
        revenus_imposables: Revenus imposables annuels
        parts: Nombre de parts fiscales
    
    Returns:
        Montant de l'impôt
    """
    quotient = revenus_imposables / parts
    
    # Barème 2024
    tranches = [
        (11294, 0.0),
        (17524, 0.11),
        (37133, 0.30),
        (88970, 0.41),
        (float('inf'), 0.45)
    ]
    
    impot = 0
    cumul = 0
    
    for limite, taux in tranches:
        tranche_imposable = min(quotient - cumul, limite)
        if tranche_imposable <= 0:
            break
        impot += tranche_imposable * taux
        cumul += limite
    
    return impot * parts


def calculate_social_charges(revenus_fonciers: float) -> float:
    """
    Calcule les prélèvements sociaux sur revenus fonciers
    
    Args:
        revenus_fonciers: Revenus fonciers nets
    
    Returns:
        Montant des prélèvements sociaux (17.2% en 2024)
    """
    return revenus_fonciers * 0.172


def calculate_profitability_ratios(prix_acquisition: float, loyers_annuels: float,
                                   charges_annuelles: float, apport: float,
                                   cashflow_annuel: float) -> Dict:
    """
    Calcule les ratios de rentabilité
    
    Args:
        prix_acquisition: Prix d'acquisition total
        loyers_annuels: Loyers annuels bruts
        charges_annuelles: Charges annuelles
        apport: Apport personnel
        cashflow_annuel: Cashflow annuel
    
    Returns:
        Dictionnaire avec tous les ratios
    """
    rentabilite_brute = (loyers_annuels / prix_acquisition) * 100
    revenus_nets = loyers_annuels - charges_annuelles
    rentabilite_nette = (revenus_nets / prix_acquisition) * 100
    
    roi = (revenus_nets / apport * 100) if apport > 0 else 0
    cash_on_cash = (cashflow_annuel / apport * 100) if apport > 0 else 0
    
    # Taux de couverture de la dette (DCR - Debt Coverage Ratio)
    # NOI / Service de la dette
    
    return {
        'rentabilite_brute': rentabilite_brute,
        'rentabilite_nette': rentabilite_nette,
        'roi': roi,
        'cash_on_cash': cash_on_cash,
        'cap_rate': rentabilite_nette  # Équivalent à rentabilité nette
    }


def calculate_break_even_point(charges_fixes_mensuelles: float, 
                               loyer_mensuel: float,
                               prix_bien: float) -> Dict:
    """
    Calcule le point mort (break-even) de l'investissement
    
    Args:
        charges_fixes_mensuelles: Charges mensuelles fixes
        loyer_mensuel: Loyer mensuel
        prix_bien: Prix du bien
    
    Returns:
        Dictionnaire avec analyses du point mort
    """
    if loyer_mensuel <= 0:
        return {}
    
    taux_occupation_min = (charges_fixes_mensuelles / loyer_mensuel) * 100
    
    return {
        'taux_occupation_minimum': taux_occupation_min,
        'jours_location_minimum': taux_occupation_min * 365 / 100,
        'marge_securite': 100 - taux_occupation_min
    }
