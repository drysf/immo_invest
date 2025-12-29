"""
Page de simulation fiscale avancée
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.financial_calculator import (
    calculate_tax_lmnp, calculate_tax_pinel,
    calculate_income_tax, calculate_social_charges,
    calculate_wealth_tax
)

# CSS pour fond noir
st.markdown("""
    <style>
    .stApp {
        background: #000000 !important;
    }
    .main {
        background-color: #000000 !important;
    }
    .block-container {
        background-color: #000000 !important;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #000000 !important;
    }
    [data-testid="stHeader"] {
        background-color: #000000 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 3px solid #3498db !important;
    }
    </style>
""", unsafe_allow_html=True)


def show_tax_simulation():
    """Affiche la page de simulation fiscale"""
    
    st.header("Simulation Fiscale Avancée")
    st.markdown("Optimisez votre investissement avec différents dispositifs fiscaux")
    
    # Choix du régime
    regime = st.radio(
        "Choisissez votre régime fiscal",
        ["Location Nue (Revenus Fonciers)", "LMNP (Location Meublée)", "Loi Pinel"],
        horizontal=True
    )
    
    if regime == "Location Nue (Revenus Fonciers)":
        show_revenus_fonciers()
    elif regime == "LMNP (Location Meublée)":
        show_lmnp()
    else:
        show_pinel()


def show_revenus_fonciers():
    """Simulation revenus fonciers classiques"""
    st.subheader("Location Nue - Revenus Fonciers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Revenus")
        loyers_annuels = st.number_input(
            "Loyers annuels bruts (€)",
            min_value=0,
            max_value=500000,
            value=12000,
            step=1000
        )
    
    with col2:
        st.markdown("### Charges Déductibles")
        
        interets = st.number_input(
            "Intérêts d'emprunt (€/an)",
            min_value=0,
            max_value=100000,
            value=3000,
            step=500
        )
        
        charges_copro = st.number_input(
            "Charges de copropriété (€/an)",
            min_value=0,
            max_value=20000,
            value=1200,
            step=100
        )
        
        taxe_fonciere = st.number_input(
            "Taxe foncière (€/an)",
            min_value=0,
            max_value=10000,
            value=800,
            step=100
        )
        
        assurance = st.number_input(
            "Assurance PNO (€/an)",
            min_value=0,
            max_value=2000,
            value=200,
            step=50
        )
        
        travaux = st.number_input(
            "Travaux (€/an)",
            min_value=0,
            max_value=50000,
            value=1000,
            step=500,
            help="Travaux d'entretien et de réparation"
        )
        
        autres = st.number_input(
            "Autres charges (€/an)",
            min_value=0,
            max_value=20000,
            value=500,
            step=100
        )
    
    # Paramètres fiscaux
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        tranche_marginale = st.slider(
            "Tranche Marginale d'Imposition (%)",
            0, 45, 30,
            help="Votre tranche d'imposition sur le revenu"
        )
    
    with col2:
        regime_fiscal = st.radio(
            "Régime Fiscal",
            ["Micro-Foncier", "Réel"],
            help="Micro-foncier: abattement de 30% (plafonné à 15 000€ de loyers)"
        )
    
    # Calculs
    charges_totales = interets + charges_copro + taxe_fonciere + assurance + travaux + autres
    
    # Micro-Foncier
    if regime_fiscal == "Micro-Foncier" and loyers_annuels <= 15000:
        abattement = loyers_annuels * 0.3
        revenus_imposables_micro = loyers_annuels - abattement
        impot_micro = revenus_imposables_micro * (tranche_marginale / 100)
        prelevements_sociaux_micro = revenus_imposables_micro * 0.172
        impot_total_micro = impot_micro + prelevements_sociaux_micro
    else:
        revenus_imposables_micro = 0
        impot_total_micro = 0
    
    # Régime Réel
    revenus_imposables_reel = max(0, loyers_annuels - charges_totales)
    impot_reel = revenus_imposables_reel * (tranche_marginale / 100)
    prelevements_sociaux_reel = revenus_imposables_reel * 0.172
    impot_total_reel = impot_reel + prelevements_sociaux_reel
    
    # Déficit foncier
    deficit = max(0, charges_totales - loyers_annuels)
    economie_deficit = deficit * (tranche_marginale / 100)
    
    # Résultats
    st.markdown("---")
    st.header("Résultats de la Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Revenus**")
        st.metric("Loyers Annuels", f"{loyers_annuels:,.0f} €")
        st.metric("Charges Totales", f"{charges_totales:,.0f} €")
    
    with col2:
        if regime_fiscal == "Micro-Foncier" and loyers_annuels <= 15000:
            st.success("**Micro-Foncier**")
            st.metric("Revenus Imposables", f"{revenus_imposables_micro:,.0f} €")
            st.metric("Impôt Total", f"{impot_total_micro:,.0f} €")
        else:
            st.warning("Micro-Foncier non applicable")
    
    with col3:
        st.success("**Régime Réel**")
        st.metric("Revenus Imposables", f"{revenus_imposables_reel:,.0f} €")
        st.metric("Impôt Total", f"{impot_total_reel:,.0f} €")
    
    # Comparaison
    st.markdown("---")
    st.subheader("Comparaison des Régimes")
    
    if loyers_annuels <= 15000:
        economie = impot_total_micro - impot_total_reel
        if economie > 0:
            st.success(f"Le régime réel vous fait économiser {economie:,.0f} € par an")
        elif economie < 0:
            st.info(f"Le micro-foncier vous fait économiser {-economie:,.0f} € par an")
        else:
            st.info("Les deux régimes sont équivalents")
    
    # Déficit foncier
    if deficit > 0:
        st.markdown("---")
        st.warning(f"**Déficit Foncier: {deficit:,.0f} €**")
        st.caption(f"Économie d'impôt potentielle: {economie_deficit:,.0f} € (imputable sur votre revenu global dans la limite de 10 700€)")
    
    # Graphique détail charges
    st.markdown("---")
    st.subheader("Répartition des Charges Déductibles")
    
    charges_data = pd.DataFrame({
        'Charge': ['Intérêts', 'Charges Copro', 'Taxe Foncière', 'Assurance', 'Travaux', 'Autres'],
        'Montant': [interets, charges_copro, taxe_fonciere, assurance, travaux, autres]
    })
    
    fig = go.Figure(data=[go.Pie(
        labels=charges_data['Charge'],
        values=charges_data['Montant'],
        hole=0.4
    )])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def show_lmnp():
    """Simulation LMNP"""
    st.subheader("LMNP - Location Meublée Non Professionnelle")
    
    st.info("Le statut LMNP permet de déduire vos charges ET d'amortir votre bien")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Investissement")
        
        prix_bien = st.number_input(
            "Prix du bien (€)",
            min_value=0,
            max_value=2000000,
            value=150000,
            step=10000
        )
        
        mobilier = st.number_input(
            "Valeur du mobilier (€)",
            min_value=0,
            max_value=50000,
            value=5000,
            step=500
        )
        
        loyers_annuels = st.number_input(
            "Loyers annuels (€)",
            min_value=0,
            max_value=500000,
            value=15000,
            step=1000
        )
    
    with col2:
        st.markdown("### Charges Annuelles")
        
        interets = st.number_input(
            "Intérêts d'emprunt (€)",
            min_value=0,
            max_value=100000,
            value=4000,
            step=500,
            key="lmnp_interets"
        )
        
        charges = st.number_input(
            "Autres charges (€)",
            min_value=0,
            max_value=50000,
            value=3000,
            step=500,
            key="lmnp_charges"
        )
    
    # Amortissement
    st.markdown("---")
    st.subheader("Amortissement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duree_amort_bien = st.slider(
            "Durée d'amortissement du bien (années)",
            10, 50, 30,
            help="Généralement 25-30 ans pour l'immobilier"
        )
    
    with col2:
        duree_amort_mobilier = st.slider(
            "Durée d'amortissement du mobilier (années)",
            3, 15, 7
        )
    
    # Calcul amortissement
    # On amortit 80% du prix (le terrain n'est pas amortissable)
    amort_bien = (prix_bien * 0.8) / duree_amort_bien
    amort_mobilier = mobilier / duree_amort_mobilier
    amortissement_total = amort_bien + amort_mobilier
    
    # Choix du régime
    regime = st.radio(
        "Régime Fiscal",
        ["Micro-BIC", "Réel Simplifié"],
        help="Micro-BIC: abattement de 50% (plafonné à 77 700€). Réel: déduction des charges et amortissement"
    )
    
    # Calculs
    charges_totales = interets + charges
    
    # Micro-BIC
    if regime == "Micro-BIC" and loyers_annuels <= 77700:
        abattement = loyers_annuels * 0.5
        revenus_micro = loyers_annuels - abattement
    else:
        revenus_micro = 0
    
    # Réel
    result_lmnp = calculate_tax_lmnp(loyers_annuels, charges_totales, amortissement_total)
    
    # Résultats
    st.markdown("---")
    st.header("Résultats de la Simulation LMNP")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Loyers Annuels", f"{loyers_annuels:,.0f} €")
        st.metric("Charges", f"{charges_totales:,.0f} €")
    
    with col2:
        st.metric("Amortissement Bien", f"{amort_bien:,.0f} €")
        st.metric("Amortissement Mobilier", f"{amort_mobilier:,.0f} €")
    
    with col3:
        if revenus_micro > 0:
            st.info("**Micro-BIC**")
            st.metric("Revenus Imposables", f"{revenus_micro:,.0f} €")
        else:
            st.warning("Micro-BIC\nnon éligible")
    
    with col4:
        st.success("**Réel Simplifié**")
        st.metric("Revenus Imposables", f"{result_lmnp['revenus_imposables_reel']:,.0f} €")
    
    # Avantages
    st.markdown("---")
    
    if revenus_micro > 0:
        economie = result_lmnp['economie_reel_vs_micro']
        if economie > 0:
            st.success(f"Le régime réel vous fait économiser l'impôt sur {economie:,.0f} € par an grâce à l'amortissement")
        else:
            st.info("Le micro-BIC est plus avantageux dans votre situation")
    
    # Graphique amortissement
    st.markdown("---")
    st.subheader("Détail de l'Amortissement")
    
    fig = go.Figure(data=[go.Pie(
        labels=['Bien Immobilier', 'Mobilier'],
        values=[amort_bien, amort_mobilier],
        hole=0.4,
        marker_colors=['#3498db', '#e74c3c']
    )])
    fig.update_layout(
        title=f"Amortissement Annuel: {amortissement_total:,.0f} €",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Projection sur 10 ans
    st.markdown("---")
    st.subheader("Projection sur 10 ans")
    
    projection = []
    for annee in range(1, 11):
        revenus_imp = max(0, loyers_annuels - charges_totales - amortissement_total)
        cashflow_net = loyers_annuels - charges_totales
        projection.append({
            'Année': annee,
            'Loyers': loyers_annuels,
            'Charges': -charges_totales,
            'Amortissement': -amortissement_total,
            'Revenus Imposables': revenus_imp,
            'Cashflow Net': cashflow_net
        })
    
    df_proj = pd.DataFrame(projection)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_proj['Année'],
        y=df_proj['Cashflow Net'],
        name='Cashflow Net',
        marker_color='#2ecc71'
    ))
    fig.add_trace(go.Scatter(
        x=df_proj['Année'],
        y=df_proj['Revenus Imposables'],
        name='Revenus Imposables',
        line=dict(color='#e74c3c', width=3)
    ))
    fig.update_layout(
        title="Cashflow vs Revenus Imposables",
        xaxis_title="Année",
        yaxis_title="Montant (€)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def show_pinel():
    """Simulation Loi Pinel"""
    st.subheader("Loi Pinel - Investissement Locatif Défiscalisé")
    
    st.info("La loi Pinel permet de réduire vos impôts en échange d'un engagement de location")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Bien Immobilier")
        
        prix_acquisition = st.number_input(
            "Prix d'acquisition (€)",
            min_value=0,
            max_value=500000,
            value=200000,
            step=10000,
            help="Plafonné à 300 000€ pour le Pinel"
        )
        
        surface = st.number_input(
            "Surface (m²)",
            min_value=10,
            max_value=200,
            value=50,
            step=5
        )
        
        zone = st.selectbox(
            "Zone Pinel",
            ["A bis", "A", "B1"],
            help="Paris/Région Parisienne = A bis, Grandes métropoles = A, Autres villes = B1"
        )
    
    with col2:
        st.markdown("### Engagement")
        
        duree = st.select_slider(
            "Durée d'engagement (années)",
            options=[6, 9, 12],
            value=9,
            help="Plus la durée est longue, plus la réduction est importante"
        )
        
        loyer_mensuel = st.number_input(
            "Loyer mensuel envisagé (€)",
            min_value=0,
            max_value=10000,
            value=800,
            step=50
        )
    
    # Calculer Pinel
    result_pinel = calculate_tax_pinel(prix_acquisition, zone, duree)
    plafond_loyer = result_pinel['plafond_loyer']
    loyer_max = plafond_loyer * surface
    
    # Vérifier respect des plafonds
    st.markdown("---")
    st.subheader("Vérification des Conditions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if prix_acquisition <= 300000:
            st.success(f"Prix conforme\n({prix_acquisition:,.0f} € ≤ 300 000 €)")
        else:
            st.error(f"Prix trop élevé\nPlafond Pinel: 300 000 €")
    
    with col2:
        st.info(f"**Plafond de loyer**\n{plafond_loyer:.2f} €/m²")
        st.caption(f"Loyer max: {loyer_max:,.0f} €/mois")
    
    with col3:
        if loyer_mensuel <= loyer_max:
            st.success(f"Loyer conforme\n({loyer_mensuel:,.0f} € ≤ {loyer_max:,.0f} €)")
        else:
            st.warning(f"Loyer trop élevé\nRamenez à {loyer_max:,.0f} €/mois")
    
    # Résultats
    st.markdown("---")
    st.header("Avantage Fiscal Pinel")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Réduction Totale",
            f"{result_pinel['reduction_totale']:,.0f} €",
            help=f"Sur {duree} ans"
        )
    
    with col2:
        st.metric(
            "Réduction Annuelle",
            f"{result_pinel['reduction_annuelle']:,.0f} €",
            help="Montant déduit de vos impôts chaque année"
        )
    
    with col3:
        taux_reduc = (result_pinel['reduction_totale'] / prix_acquisition) * 100
        st.metric(
            "Taux de Réduction",
            f"{taux_reduc:.1f}%",
            help="Pourcentage du prix d'acquisition"
        )
    
    # Calcul de rentabilité
    st.markdown("---")
    st.subheader("Analyse de Rentabilité")
    
    # Utiliser le loyer plafonné si nécessaire
    loyer_applique = min(loyer_mensuel, loyer_max)
    loyers_annuels = loyer_applique * 12
    
    col1, col2 = st.columns(2)
    
    with col1:
        charges_annuelles = st.number_input(
            "Charges annuelles estimées (€)",
            min_value=0,
            max_value=50000,
            value=3000,
            step=500
        )
        
        mensualite_credit = st.number_input(
            "Mensualité de crédit (€)",
            min_value=0,
            max_value=5000,
            value=900,
            step=50
        )
    
    with col2:
        # Calculs
        cashflow_mensuel = loyer_applique - mensualite_credit
        cashflow_annuel = loyers_annuels - (mensualite_credit * 12) - charges_annuelles
        
        # Avec avantage Pinel
        cashflow_avec_pinel = cashflow_annuel + result_pinel['reduction_annuelle']
        
        st.metric("Cashflow Annuel (sans Pinel)", f"{cashflow_annuel:,.0f} €")
        st.metric("Cashflow Annuel (avec Pinel)", f"{cashflow_avec_pinel:,.0f} €",
                 delta=f"+{result_pinel['reduction_annuelle']:,.0f} €")
    
    # Graphique évolution réduction
    st.markdown("---")
    st.subheader(f"Évolution sur {duree} ans")
    
    projection = []
    for annee in range(1, duree + 1):
        projection.append({
            'Année': annee,
            'Réduction Fiscale': result_pinel['reduction_annuelle'],
            'Réduction Cumulée': result_pinel['reduction_annuelle'] * annee,
            'Cashflow avec Pinel': cashflow_avec_pinel,
            'Cashflow sans Pinel': cashflow_annuel
        })
    
    df_proj = pd.DataFrame(projection)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_proj['Année'],
        y=df_proj['Réduction Fiscale'],
        name='Réduction Annuelle',
        marker_color='#2ecc71'
    ))
    fig.add_trace(go.Scatter(
        x=df_proj['Année'],
        y=df_proj['Réduction Cumulée'],
        name='Réduction Cumulée',
        line=dict(color='#3498db', width=3),
        yaxis='y2'
    ))
    fig.update_layout(
        title="Avantage Fiscal Pinel",
        xaxis_title="Année",
        yaxis_title="Réduction Annuelle (€)",
        yaxis2=dict(title="Réduction Cumulée (€)", overlaying='y', side='right'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparaison cashflows
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_proj['Année'],
        y=df_proj['Cashflow sans Pinel'],
        name='Sans Pinel',
        marker_color='#e74c3c'
    ))
    fig2.add_trace(go.Bar(
        x=df_proj['Année'],
        y=df_proj['Cashflow avec Pinel'],
        name='Avec Pinel',
        marker_color='#2ecc71'
    ))
    fig2.update_layout(
        title="Comparaison des Cashflows",
        xaxis_title="Année",
        yaxis_title="Cashflow Annuel (€)",
        barmode='group',
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)


if __name__ == "__main__":
    show_tax_simulation()
