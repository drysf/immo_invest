import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Simulateur Investissement Immobilier",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
    <style>
    /* Fond noir partout */
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
    
    /* Sidebar avec bordure bleue */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 3px solid #3498db !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #000000 !important;
    }
    
    /* Onglets en noir */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #000000 !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background-color: #000000 !important;
    }
    
    /* Métriques */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def calculer_investissement(prix_bien, surface, apport, taux_credit, duree_credit, 
                           loyer_mensuel, charges_copro, travaux, frais_notaire_pct,
                           taxe_fonciere, assurance_pgl, vacance_locative,
                           appreciation_annuelle, augmentation_loyer):
    """Calcule tous les indicateurs de l'investissement"""
    
    # Calculs initiaux
    prix_total = prix_bien + travaux
    frais_notaire = prix_bien * frais_notaire_pct
    cout_total = prix_total + frais_notaire
    montant_emprunte = cout_total - apport
    
    # Mensualités du crédit
    if taux_credit > 0 and duree_credit > 0:
        taux_mensuel = taux_credit / 100 / 12
        nb_mois = duree_credit * 12
        mensualite_credit = montant_emprunte * (taux_mensuel * (1 + taux_mensuel)**nb_mois) / ((1 + taux_mensuel)**nb_mois - 1)
        cout_total_credit = mensualite_credit * nb_mois
        interets_total = cout_total_credit - montant_emprunte
    else:
        mensualite_credit = 0
        cout_total_credit = 0
        interets_total = 0
    
    # Revenus et charges mensuels
    revenus_bruts_mensuel = loyer_mensuel * (1 - vacance_locative/100)
    charges_mensuelles = charges_copro + assurance_pgl + (taxe_fonciere / 12)
    charges_totales = charges_mensuelles + mensualite_credit
    
    # Cashflow mensuel
    cashflow_mensuel = revenus_bruts_mensuel - charges_totales
    cashflow_annuel = cashflow_mensuel * 12
    
    # Rentabilité brute
    loyers_annuels = loyer_mensuel * 12
    rentabilite_brute = (loyers_annuels / prix_total) * 100
    
    # Rentabilité nette
    charges_annuelles = charges_mensuelles * 12
    revenus_nets = loyers_annuels * (1 - vacance_locative/100) - charges_annuelles
    rentabilite_nette = (revenus_nets / cout_total) * 100
    
    # ROI (Return on Investment sur apport)
    if apport > 0:
        roi = (revenus_nets / apport) * 100
    else:
        roi = 0
    
    # Simulation sur 20 ans
    projection = []
    valeur_bien = prix_bien
    loyer_actuel = loyer_mensuel
    capital_restant = montant_emprunte
    
    for annee in range(1, 21):
        # Appréciation du bien
        valeur_bien *= (1 + appreciation_annuelle/100)
        
        # Augmentation du loyer
        if annee > 1:
            loyer_actuel *= (1 + augmentation_loyer/100)
        
        # Revenus de l'année
        revenus_annee = loyer_actuel * 12 * (1 - vacance_locative/100)
        charges_annee = (charges_copro + assurance_pgl) * 12 + taxe_fonciere
        
        # Remboursement du crédit
        if annee <= duree_credit:
            remb_annuel = mensualite_credit * 12
            # Calcul simplifié du capital remboursé
            capital_rembourse = remb_annuel - (capital_restant * taux_credit / 100)
            capital_restant -= capital_rembourse
        else:
            remb_annuel = 0
            capital_rembourse = 0
            capital_restant = 0
        
        cashflow_annee = revenus_annee - charges_annee - remb_annuel
        
        # Plus-value latente
        plus_value = valeur_bien - prix_bien
        
        projection.append({
            'Année': annee,
            'Valeur Bien': valeur_bien,
            'Loyer Mensuel': loyer_actuel,
            'Revenus Annuels': revenus_annee,
            'Charges Annuelles': charges_annee,
            'Remboursement': remb_annuel,
            'Cashflow': cashflow_annee,
            'Capital Restant': max(0, capital_restant),
            'Plus-value': plus_value,
            'Patrimoine Net': valeur_bien - max(0, capital_restant)
        })
    
    return {
        'cout_total': cout_total,
        'montant_emprunte': montant_emprunte,
        'mensualite_credit': mensualite_credit,
        'interets_total': interets_total,
        'revenus_bruts_mensuel': revenus_bruts_mensuel,
        'charges_mensuelles': charges_mensuelles,
        'cashflow_mensuel': cashflow_mensuel,
        'cashflow_annuel': cashflow_annuel,
        'rentabilite_brute': rentabilite_brute,
        'rentabilite_nette': rentabilite_nette,
        'roi': roi,
        'projection': projection
    }

# Titre principal
st.title("Simulateur d'Investissement Immobilier")
st.markdown("### Analysez la rentabilité de votre projet immobilier")

# Sidebar pour les paramètres
with st.sidebar:
    st.header("Paramètres du Bien")
    
    st.subheader("Prix du Bien")
    
    surface = st.number_input("Surface (m²)", min_value=10, max_value=500, value=50, step=5)
    prix_m2 = st.number_input("Prix au m² (€)", min_value=1000, max_value=20000, 
                               value=4000, step=100)
    prix_bien = surface * prix_m2
    st.info(f"**Prix du bien: {prix_bien:,.0f} €**")
    
    travaux = st.number_input("Montant des travaux (€)", min_value=0, max_value=500000, 
                              value=5000, step=1000)
    
    st.markdown("---")
    st.subheader("Financement")
    
    apport = st.number_input("Apport personnel (€)", min_value=0, max_value=prix_bien, 
                            value=int(prix_bien * 0.1), step=5000)
    
    pct_apport = (apport / prix_bien * 100) if prix_bien > 0 else 0
    st.caption(f"Apport: {pct_apport:.1f}% du prix")
    
    taux_credit = st.slider("Taux d'intérêt crédit (%)", min_value=0.0, max_value=5.0, 
                            value=3.8, step=0.1)
    
    duree_credit = st.slider("Durée du crédit (années)", min_value=5, max_value=30, 
                            value=20, step=1)
    
    frais_notaire_pct = st.slider("Frais de notaire (%)", min_value=2.0, max_value=10.0, 
                                   value=7.5, step=0.5) / 100

# Onglets principaux
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Analyse", 
    "Revenus & Charges", 
    "Projection 20 ans", 
    "Marché DVF",
    "Comparaison", 
    "Fiscalité"
])

with tab1:
    st.header("Analyse de Rentabilité")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenus Locatifs")
        loyer_m2 = st.number_input("Loyer mensuel au m² (€)", min_value=5.0, max_value=100.0, 
                                    value=13.0, step=0.5)
        loyer_mensuel = surface * loyer_m2
        st.success(f"**Loyer mensuel estimé: {loyer_mensuel:,.0f} €**")
        
        vacance_locative = st.slider("Vacance locative (%)", min_value=0, max_value=20, 
                                     value=5, step=1)
    
    with col2:
        st.subheader("Charges")
        charges_copro = st.number_input("Charges copropriété (€/mois)", min_value=0, 
                                       max_value=500, value=30, step=10)
        
        taxe_fonciere = st.number_input("Taxe foncière annuelle (€)", min_value=0, 
                                        max_value=10000, 
                                        value=800, 
                                        step=100)
        
        assurance_pgl = st.number_input("Assurance PNO/GLI (€/mois)", min_value=0, 
                                        max_value=200, value=30, step=5)
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Hypothèses d'évolution")
        appreciation_annuelle = st.slider("Appréciation du bien (%/an)", 
                                         min_value=-2.0, max_value=10.0, 
                                         value=2.0, step=0.1,
                                         help="Moyenne historique France: 1.5-2.5%/an")
    
    with col4:
        st.subheader("Augmentation du loyer")
        augmentation_loyer = st.slider("Augmentation loyer (%/an)", 
                                       min_value=0.0, max_value=5.0, 
                                       value=1.5, step=0.1,
                                       help="IRL moyen 2024: +1.5%")
    
    # Calcul
    resultats = calculer_investissement(
        prix_bien, surface, apport, taux_credit, duree_credit,
        loyer_mensuel, charges_copro, travaux, frais_notaire_pct,
        taxe_fonciere, assurance_pgl, vacance_locative,
        appreciation_annuelle, augmentation_loyer
    )
    
    st.markdown("---")
    st.header("Résultats de l'Analyse")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Coût Total", f"{resultats['cout_total']:,.0f} €")
        st.metric("Montant Emprunté", f"{resultats['montant_emprunte']:,.0f} €")
    
    with col2:
        st.metric("Mensualité Crédit", f"{resultats['mensualite_credit']:,.0f} €")
        st.metric("Intérêts Total", f"{resultats['interets_total']:,.0f} €")
    
    with col3:
        couleur_cashflow = "normal" if resultats['cashflow_mensuel'] >= 0 else "inverse"
        st.metric("Cashflow Mensuel", f"{resultats['cashflow_mensuel']:,.0f} €",
                 delta=None, delta_color=couleur_cashflow)
        st.metric("Cashflow Annuel", f"{resultats['cashflow_annuel']:,.0f} €")
    
    with col4:
        st.metric("Rentabilité Brute", f"{resultats['rentabilite_brute']:.2f}%")
        st.metric("Rentabilité Nette", f"{resultats['rentabilite_nette']:.2f}%")
    
    # ROI
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.metric("ROI (sur apport)", f"{resultats['roi']:.2f}%", 
                 help="Return on Investment calculé sur votre apport personnel")

with tab2:
    st.header("Détail Revenus & Charges")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenus")
        revenus_data = pd.DataFrame({
            'Type': ['Loyers bruts mensuels', 'Vacance locative', 'Revenus nets mensuels'],
            'Montant (€)': [
                loyer_mensuel,
                -loyer_mensuel * (vacance_locative/100),
                resultats['revenus_bruts_mensuel']
            ]
        })
        
        fig_revenus = go.Figure(data=[
            go.Bar(x=revenus_data['Type'], y=revenus_data['Montant (€)'],
                  marker_color=['#2ecc71', '#e74c3c', '#3498db'])
        ])
        fig_revenus.update_layout(title="Revenus Mensuels", height=400)
        st.plotly_chart(fig_revenus, use_container_width=True)
    
    with col2:
        st.subheader("Charges")
        charges_data = pd.DataFrame({
            'Type': ['Charges copro', 'Taxe foncière', 'Assurance', 'Crédit'],
            'Montant (€)': [
                charges_copro,
                taxe_fonciere / 12,
                assurance_pgl,
                resultats['mensualite_credit']
            ]
        })
        
        fig_charges = go.Figure(data=[
            go.Pie(labels=charges_data['Type'], values=charges_data['Montant (€)'],
                  hole=0.4)
        ])
        fig_charges.update_layout(title="Répartition des Charges Mensuelles", height=400)
        st.plotly_chart(fig_charges, use_container_width=True)
    
    # Tableau détaillé
    st.markdown("---")
    st.subheader("Tableau Récapitulatif Mensuel")
    
    recap_data = pd.DataFrame({
        'Catégorie': ['REVENUS', 'CHARGES', 'CHARGES', 'CHARGES', 'CHARGES', 'CHARGES', 'RÉSULTAT'],
        'Détail': [
            'Loyers (après vacance)',
            'Charges copropriété',
            'Taxe foncière',
            'Assurance PNO/GLI',
            'Mensualité crédit',
            'Total charges',
            'Cashflow mensuel'
        ],
        'Montant (€)': [
            resultats['revenus_bruts_mensuel'],
            -charges_copro,
            -taxe_fonciere / 12,
            -assurance_pgl,
            -resultats['mensualite_credit'],
            -resultats['charges_mensuelles'] - resultats['mensualite_credit'],
            resultats['cashflow_mensuel']
        ]
    })
    
    # Formater les montants
    recap_data['Montant Formaté'] = recap_data['Montant (€)'].apply(lambda x: f"{x:,.2f} €")
    st.dataframe(recap_data[['Catégorie', 'Détail', 'Montant Formaté']], use_container_width=True, hide_index=True)

with tab3:
    st.header("Projection sur 20 ans")
    
    df_projection = pd.DataFrame(resultats['projection'])
    
    # Graphique patrimoine net
    fig_patrimoine = go.Figure()
    fig_patrimoine.add_trace(go.Scatter(
        x=df_projection['Année'], 
        y=df_projection['Patrimoine Net'],
        mode='lines+markers',
        name='Patrimoine Net',
        line=dict(color='#2ecc71', width=3),
        fill='tozeroy'
    ))
    fig_patrimoine.add_trace(go.Scatter(
        x=df_projection['Année'], 
        y=df_projection['Valeur Bien'],
        mode='lines',
        name='Valeur du Bien',
        line=dict(color='#3498db', width=2, dash='dash')
    ))
    fig_patrimoine.update_layout(
        title="Évolution du Patrimoine Net",
        xaxis_title="Année",
        yaxis_title="Montant (€)",
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig_patrimoine, use_container_width=True)
    
    # Graphique cashflow cumulé
    df_projection['Cashflow Cumulé'] = df_projection['Cashflow'].cumsum()
    
    fig_cashflow = go.Figure()
    fig_cashflow.add_trace(go.Bar(
        x=df_projection['Année'], 
        y=df_projection['Cashflow'],
        name='Cashflow Annuel',
        marker_color='#9b59b6'
    ))
    fig_cashflow.add_trace(go.Scatter(
        x=df_projection['Année'], 
        y=df_projection['Cashflow Cumulé'],
        mode='lines+markers',
        name='Cashflow Cumulé',
        line=dict(color='#e74c3c', width=3),
        yaxis='y2'
    ))
    fig_cashflow.update_layout(
        title="Évolution du Cashflow",
        xaxis_title="Année",
        yaxis_title="Cashflow Annuel (€)",
        yaxis2=dict(title="Cashflow Cumulé (€)", overlaying='y', side='right'),
        height=500,
        hovermode='x unified'
    )
    st.plotly_chart(fig_cashflow, use_container_width=True)
    
    # Tableau détaillé
    st.markdown("---")
    st.subheader("Données Détaillées")
    
    # Formater le dataframe pour l'affichage
    df_display = df_projection.copy()
    for col in df_display.columns:
        if col != 'Année':
            df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f} €")
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)

with tab4:
    st.header("Analyse de Marché DVF")
    
    st.info("Comparez votre projet aux données réelles du marché immobilier français")
    
    # Import des modules
    try:
        from utils.dvf_loader import load_dvf_data, get_communes_list
        from utils.market_analysis import compare_to_market, get_investment_recommendation
        
        # Charger les données DVF
        with st.spinner("Chargement des données DVF..."):
            df_dvf = load_dvf_data()
        
        if not df_dvf.empty:
            st.success(f"{len(df_dvf):,} enregistrements chargés")
            
            # Charger les données INSEE des communes
            try:
                from utils.communes_insee import (
                    load_communes_insee, create_commune_search_dict, 
                    search_communes, format_commune_option, get_code_from_formatted
                )
                from utils.dvf_loader import get_communes_list
                
                df_insee = load_communes_insee()
                code_to_name, name_to_code = create_commune_search_dict(df_insee)
                available_codes = get_communes_list(df_dvf)
                
                # Interface de recherche
                st.markdown("---")
                st.subheader("Sélection de la Commune")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    search_input = st.text_input(
                        "Rechercher par nom de commune ou code INSEE",
                        placeholder="Ex: Paris, Lyon, 75015...",
                        help="Tapez au moins 2 caractères pour lancer la recherche"
                    )
                
                commune_select = None
                
                if search_input and len(search_input) >= 2:
                    # Rechercher les communes
                    results = search_communes(search_input, code_to_name, available_codes, max_results=30)
                    
                    if results:
                        with col2:
                            st.write(f"{len(results)} résultat(s) trouvé(s)")
                        
                        # Créer les options formatées
                        options = [format_commune_option(code, nom) for code, nom in results]
                        
                        selected = st.selectbox(
                            "Sélectionnez la commune dans les résultats",
                            [""] + options,
                            key="commune_selector"
                        )
                        
                        if selected:
                            commune_select = get_code_from_formatted(selected)
                    else:
                        st.warning("Aucune commune trouvée avec ce critère")
                elif search_input and len(search_input) < 2:
                    st.info("Tapez au moins 2 caractères pour rechercher")
            
            except Exception as e:
                st.error(f"Erreur lors du chargement des données communes: {e}")
                # Fallback vers l'ancienne méthode
                from utils.dvf_loader import get_communes_list
                communes = get_communes_list(df_dvf)
                if communes:
                    commune_select = st.text_input(
                        "Code INSEE de la commune",
                        placeholder="Ex: 75015",
                        help="Entrez le code INSEE à 5 chiffres"
                    )
                    if commune_select not in communes:
                        commune_select = None
            
            with col2:
                if commune_select:
                    st.metric("Commune sélectionnée", commune_select)
            
            # Analyse comparative
            if commune_select:
                st.markdown("---")
                st.subheader("Comparaison avec le Marché")
                
                # Comparer le prix
                comparison = compare_to_market(prix_m2, df_dvf, commune_select)
                
                if comparison.get('statut') != 'Données insuffisantes':
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Votre Prix/m²", f"{prix_m2:,.0f} €")
                    
                    with col2:
                        st.metric("Prix/m² Marché", 
                                 f"{comparison.get('prix_m2_marche', 0):,.0f} €")
                    
                    with col3:
                        ecart = comparison.get('ecart_pourcentage', 0)
                        st.metric("Écart", f"{ecart:+.1f}%",
                                 delta_color="inverse")
                    
                    # Évaluation
                    st.markdown("---")
                    positionnement = comparison.get('positionnement', '')
                    evaluation = comparison.get('evaluation', '')
                    
                    if 'dessous' in positionnement.lower():
                        st.success(f"**{positionnement}** - {evaluation}")
                    elif 'moyenne' in positionnement.lower():
                        st.info(f"**{positionnement}** - {evaluation}")
                    else:
                        st.warning(f"**{positionnement}** - {evaluation}")
                    
                    # Recommandation d'investissement
                    st.markdown("---")
                    st.subheader("Recommandation d'Investissement")
                    
                    reco = get_investment_recommendation(df_dvf, commune_select, 
                                                        prix_m2, surface)
                    
                    score = reco.get('score', 0)
                    recommandation = reco.get('recommandation', '')
                    
                    # Jauge de score
                    import plotly.graph_objects as go
                    
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Score d'Investissement"},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 35], 'color': "#e74c3c"},
                                {'range': [35, 50], 'color': "#f39c12"},
                                {'range': [50, 65], 'color': "#f1c40f"},
                                {'range': [65, 80], 'color': "#2ecc71"},
                                {'range': [80, 100], 'color': "#27ae60"}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.75,
                                'value': 70
                            }
                        }
                    ))
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    if reco.get('couleur') == 'success':
                        st.success(f"**{recommandation}**")
                    elif reco.get('couleur') == 'warning':
                        st.warning(f"**{recommandation}**")
                    else:
                        st.error(f"**{recommandation}**")
                else:
                    st.warning("Données insuffisantes pour cette commune")
            else:
                st.info("Utilisez la recherche ci-dessus pour sélectionner une commune")
        else:
            st.warning("Aucune donnée DVF disponible")
    
    except ImportError:
        st.error("Modules d'analyse DVF non disponibles")
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")

with tab5:
    st.header("Comparaison de Scénarios")
    
    st.info("Créez et comparez plusieurs scénarios d'investissement")
    
    # Initialiser session state pour les scénarios
    if 'scenarios' not in st.session_state:
        st.session_state.scenarios = []
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Ajouter un Scénario")
        scenario_nom = st.text_input("Nom du scénario", placeholder="Ex: Paris 50m²")
    
    with col2:
        st.write("")
        st.write("")
        if st.button("Ajouter le scénario actuel", use_container_width=True):
            if scenario_nom:
                scenario = {
                    'nom': scenario_nom,
                    'surface': surface,
                    'prix_m2': prix_m2,
                    'prix_bien': prix_bien,
                    'loyer_mensuel': loyer_mensuel,
                    'resultats': resultats
                }
                st.session_state.scenarios.append(scenario)
                st.success(f"Scénario '{scenario_nom}' ajouté!")
            else:
                st.error("Veuillez donner un nom au scénario")
    
    if st.button("Effacer tous les scénarios"):
        st.session_state.scenarios = []
        st.rerun()
    
    if len(st.session_state.scenarios) < 2:
        st.warning("Ajoutez au moins 2 scénarios pour voir la comparaison")
    else:
        st.markdown("---")
        st.subheader(f"Comparaison de {len(st.session_state.scenarios)} Scénarios")
        
        # Créer le dataframe de comparaison
        comparaison_data = []
        for scenario in st.session_state.scenarios:
            comparaison_data.append({
                'Scénario': scenario['nom'],
                'Surface (m²)': scenario['surface'],
                'Prix Bien': scenario['prix_bien'],
                'Loyer Mensuel': scenario['loyer_mensuel'],
                'Rentabilité Brute': scenario['resultats']['rentabilite_brute'],
                'Rentabilité Nette': scenario['resultats']['rentabilite_nette'],
                'Cashflow Mensuel': scenario['resultats']['cashflow_mensuel'],
                'ROI': scenario['resultats']['roi']
            })
        
        df_comp = pd.DataFrame(comparaison_data)
        
        # Graphique comparatif rentabilité
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            x=df_comp['Scénario'],
            y=df_comp['Rentabilité Brute'],
            name='Rentabilité Brute',
            marker_color='#3498db'
        ))
        fig_comp.add_trace(go.Bar(
            x=df_comp['Scénario'],
            y=df_comp['Rentabilité Nette'],
            name='Rentabilité Nette',
            marker_color='#2ecc71'
        ))
        fig_comp.update_layout(
            title="Comparaison des Rentabilités",
            xaxis_title="Scénario",
            yaxis_title="Rentabilité (%)",
            barmode='group',
            height=500
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Graphique cashflow
        fig_cashflow = go.Figure()
        fig_cashflow.add_trace(go.Bar(
            x=df_comp['Scénario'],
            y=df_comp['Cashflow Mensuel'],
            marker_color='#9b59b6'
        ))
        fig_cashflow.update_layout(
            title="Comparaison du Cashflow Mensuel",
            xaxis_title="Scénario",
            yaxis_title="Cashflow (€)",
            height=400
        )
        st.plotly_chart(fig_cashflow, use_container_width=True)
        
        # Tableau comparatif
        st.markdown("---")
        st.subheader("Tableau Comparatif")
        
        # Formater le dataframe
        df_comp_display = df_comp.copy()
        df_comp_display['Prix Bien'] = df_comp_display['Prix Bien'].apply(lambda x: f"{x:,.0f} €")
        df_comp_display['Loyer Mensuel'] = df_comp_display['Loyer Mensuel'].apply(lambda x: f"{x:,.0f} €")
        df_comp_display['Cashflow Mensuel'] = df_comp_display['Cashflow Mensuel'].apply(lambda x: f"{x:,.0f} €")
        df_comp_display['Rentabilité Brute'] = df_comp_display['Rentabilité Brute'].apply(lambda x: f"{x:.2f}%")
        df_comp_display['Rentabilité Nette'] = df_comp_display['Rentabilité Nette'].apply(lambda x: f"{x:.2f}%")
        df_comp_display['ROI'] = df_comp_display['ROI'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(df_comp_display, use_container_width=True, hide_index=True)
        
        # Meilleurs scénarios
        st.markdown("---")
        st.subheader("Meilleurs Scénarios")
        
        col1, col2, col3 = st.columns(3)
        
        best_rentabilite = df_comp.nlargest(1, 'Rentabilité Nette').iloc[0]
        with col1:
            st.info("**Meilleure Rentabilité Nette**")
            st.write(f"{best_rentabilite['Scénario']}")
            st.metric("", f"{best_rentabilite['Rentabilité Nette']:.2f}%")
        
        best_cashflow = df_comp.nlargest(1, 'Cashflow Mensuel').iloc[0]
        with col2:
            st.success("**Meilleur Cashflow**")
            st.write(f"{best_cashflow['Scénario']}")
            st.metric("", f"{best_cashflow['Cashflow Mensuel']:,.0f} €")
        
        best_roi = df_comp.nlargest(1, 'ROI').iloc[0]
        with col3:
            st.warning("**Meilleur ROI**")
            st.write(f"{best_roi['Scénario']}")
            st.metric("", f"{best_roi['ROI']:.2f}%")

with tab6:
    st.header("Simulation Fiscale")
    
    st.info("Optimisez votre investissement avec différents régimes fiscaux")
    
    # Import du module fiscal
    try:
        from utils.financial_calculator import (
            calculate_tax_lmnp, calculate_tax_pinel,
            calculate_social_charges
        )
        
        # Choix du régime
        regime_fiscal = st.selectbox(
            "Régime Fiscal",
            [
                "Location Nue - Micro-Foncier",
                "Location Nue - Réel",
                "LMNP - Micro-BIC",
                "LMNP - Réel Simplifié",
                "Loi Pinel"
            ],
            help="Choisissez le régime fiscal adapté à votre projet"
        )
        
        st.markdown("---")
        
        # Location Nue
        if "Location Nue" in regime_fiscal:
            st.subheader("Location Nue - Revenus Fonciers")
            
            col1, col2 = st.columns(2)
            
            with col1:
                loyers_annuels_fiscal = loyer_mensuel * 12
                st.metric("Loyers Annuels", f"{loyers_annuels_fiscal:,.0f} €")
                
                tranche_marginale = st.slider(
                    "Tranche Marginale d'Imposition (%)",
                    0, 45, 30
                )
            
            with col2:
                # Charges déductibles
                charges_deductibles = (
                    (resultats['mensualite_credit'] - 
                     (resultats['montant_emprunte'] * taux_credit / 100 / 12)) * 12 +  # Intérêts
                    charges_copro * 12 +
                    taxe_fonciere +
                    assurance_pgl * 12
                )
                
                st.metric("Charges Déductibles", f"{charges_deductibles:,.0f} €")
            
            # Calculs fiscaux
            if "Micro-Foncier" in regime_fiscal:
                if loyers_annuels_fiscal <= 15000:
                    abattement = loyers_annuels_fiscal * 0.3
                    revenus_imposables = loyers_annuels_fiscal - abattement
                    st.success(f"Éligible au Micro-Foncier (abattement de 30%)")
                else:
                    st.warning(f"Non éligible au Micro-Foncier (loyers > 15 000€)")
                    revenus_imposables = max(0, loyers_annuels_fiscal - charges_deductibles)
            else:
                revenus_imposables = max(0, loyers_annuels_fiscal - charges_deductibles)
            
            impot_revenu = revenus_imposables * (tranche_marginale / 100)
            prelevements_sociaux = calculate_social_charges(revenus_imposables)
            impot_total = impot_revenu + prelevements_sociaux
            
            st.markdown("---")
            st.subheader("Résultats Fiscaux")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Revenus Imposables", f"{revenus_imposables:,.0f} €")
            
            with col2:
                st.metric("Impôt sur le Revenu", f"{impot_revenu:,.0f} €")
            
            with col3:
                st.metric("Prélèvements Sociaux", f"{prelevements_sociaux:,.0f} €")
            
            with col4:
                st.metric("Impôt Total", f"{impot_total:,.0f} €")
            
            # Cashflow après impôts
            cashflow_apres_impots = resultats['cashflow_annuel'] - impot_total
            
            st.markdown("---")
            st.metric("Cashflow Après Impôts", f"{cashflow_apres_impots:,.0f} €",
                     delta=f"{-impot_total:,.0f} €", delta_color="inverse")
        
        # LMNP
        elif "LMNP" in regime_fiscal:
            st.subheader("LMNP - Location Meublée Non Professionnelle")
            
            col1, col2 = st.columns(2)
            
            with col1:
                loyers_annuels_fiscal = loyer_mensuel * 12
                st.metric("Loyers Annuels", f"{loyers_annuels_fiscal:,.0f} €")
                
                valeur_mobilier = st.number_input(
                    "Valeur du mobilier (€)",
                    min_value=0,
                    max_value=50000,
                    value=5000,
                    step=500
                )
            
            with col2:
                duree_amort = st.slider(
                    "Durée d'amortissement (années)",
                    10, 40, 25
                )
                
                # Calcul amortissement
                amort_bien = (prix_bien * 0.8) / duree_amort
                amort_mobilier = valeur_mobilier / 7
                amortissement_total = amort_bien + amort_mobilier
                
                st.metric("Amortissement Annuel", f"{amortissement_total:,.0f} €")
            
            # Charges déductibles
            charges_deductibles = (
                resultats['mensualite_credit'] * 12 * 0.3 +  # Portion intérêts estimée
                charges_copro * 12 +
                taxe_fonciere +
                assurance_pgl * 12
            )
            
            # Calculs LMNP
            result_lmnp = calculate_tax_lmnp(
                loyers_annuels_fiscal,
                charges_deductibles,
                amortissement_total
            )
            
            st.markdown("---")
            st.subheader("Résultats LMNP")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if "Micro-BIC" in regime_fiscal and loyers_annuels_fiscal <= 77700:
                    revenus_micro = result_lmnp['revenus_imposables_micro']
                    st.success(f"**Micro-BIC**\nRevenus imposables: {revenus_micro:,.0f} €")
                else:
                    st.warning("Micro-BIC\nNon éligible")
            
            with col2:
                revenus_reel = result_lmnp['revenus_imposables_reel']
                st.success(f"**Réel Simplifié**\nRevenus imposables: {revenus_reel:,.0f} €")
            
            with col3:
                economie = result_lmnp['economie_reel_vs_micro']
                if economie > 0:
                    st.metric("Économie (Réel)", f"{economie:,.0f} €", 
                             help="Grâce à l'amortissement")
            
            # Avantage fiscal
            if revenus_reel == 0:
                st.success("Aucun impôt à payer grâce à l'amortissement!")
            
        # Pinel
        elif "Pinel" in regime_fiscal:
            st.subheader("Loi Pinel - Investissement Défiscalisé")
            
            col1, col2 = st.columns(2)
            
            with col1:
                zone_pinel = st.selectbox(
                    "Zone Pinel",
                    ["A bis", "A", "B1"],
                    help="Zone géographique du bien"
                )
            
            with col2:
                duree_pinel = st.select_slider(
                    "Durée d'engagement",
                    options=[6, 9, 12],
                    value=9
                )
            
            # Calcul Pinel
            result_pinel = calculate_tax_pinel(prix_bien, zone_pinel, duree_pinel)
            
            st.markdown("---")
            st.subheader("Avantage Fiscal Pinel")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Réduction Totale", 
                         f"{result_pinel['reduction_totale']:,.0f} €",
                         help=f"Sur {duree_pinel} ans")
            
            with col2:
                st.metric("Réduction Annuelle", 
                         f"{result_pinel['reduction_annuelle']:,.0f} €")
            
            with col3:
                taux_reduc = (result_pinel['reduction_totale'] / prix_bien) * 100
                st.metric("Taux de Réduction", f"{taux_reduc:.1f}%")
            
            # Plafond de loyer
            plafond = result_pinel['plafond_loyer'] * surface
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Plafond de loyer Pinel**\n{result_pinel['plafond_loyer']:.2f} €/m²")
            
            with col2:
                if loyer_mensuel <= plafond:
                    st.success(f"Loyer conforme ({loyer_mensuel:,.0f} € ≤ {plafond:,.0f} €)")
                else:
                    st.warning(f"Loyer trop élevé (max: {plafond:,.0f} €)")
            
            # Impact sur le cashflow
            cashflow_avec_pinel = resultats['cashflow_annuel'] + result_pinel['reduction_annuelle']
            
            st.markdown("---")
            st.subheader("Impact sur le Cashflow")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Cashflow Sans Pinel", f"{resultats['cashflow_annuel']:,.0f} €")
            
            with col2:
                st.metric("Cashflow Avec Pinel", f"{cashflow_avec_pinel:,.0f} €",
                         delta=f"+{result_pinel['reduction_annuelle']:,.0f} €")
        
        # Lien vers page complète
        st.markdown("---")
        st.info("Pour une simulation fiscale complète, consultez la page dédiée dans le menu")
    
    except ImportError:
        st.error("Module de calculs fiscaux non disponible")
    except Exception as e:
        st.error(f"Erreur: {e}")

# Footer avec informations
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 20px;'>
    <p><strong>Simulateur d'Investissement Immobilier</strong></p>
    <p>Données DVF - Analyses de marché - Simulations fiscales</p>
    <p style='font-size: 0.9em;'>Les simulations sont fournies à titre indicatif. 
    Consultez un professionnel pour des conseils personnalisés.</p>
</div>
""", unsafe_allow_html=True)
