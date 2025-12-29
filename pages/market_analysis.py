"""
Page d'analyse du marché immobilier avec données DVF
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.dvf_loader import (
    load_dvf_data, get_communes_list, get_commune_data,
    get_market_stats, calculate_market_evolution, get_top_communes
)
from utils.market_analysis import (
    analyze_price_trends, calculate_market_liquidity,
    compare_to_market, calculate_market_score,
    get_investment_recommendation
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


def show_market_analysis():
    """Affiche la page d'analyse du marché"""
    
    st.header("Analyse du Marché Immobilier")
    st.markdown("Explorez les données DVF (Demandes de Valeurs Foncières)")
    
    # Charger les données
    with st.spinner("Chargement des données DVF..."):
        df = load_dvf_data()
    
    if df.empty:
        st.error("Aucune donnée DVF disponible. Vérifiez que les fichiers sont présents dans le dossier /data")
        return
    
    st.success(f"{len(df):,} enregistrements chargés ({df['annee'].min():.0f}-{df['annee'].max():.0f})")
    
    # Tabs pour différentes analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "Recherche par Commune",
        "Tendances du Marché",
        "Top Communes",
        "Vue d'Ensemble"
    ])
    
    with tab1:
        show_commune_search(df)
    
    with tab2:
        show_market_trends(df)
    
    with tab3:
        show_top_communes(df)
    
    with tab4:
        show_market_overview(df)


def show_commune_search(df: pd.DataFrame):
    """Affiche la recherche par commune"""
    st.subheader("Recherche par Commune")
    
    # Charger les données INSEE
    try:
        from utils.communes_insee import (
            load_communes_insee, create_commune_search_dict, 
            search_communes, format_commune_option, get_code_from_formatted
        )
        from utils.dvf_loader import get_communes_list
        
        df_insee = load_communes_insee()
        code_to_name, name_to_code = create_commune_search_dict(df_insee)
        available_codes = get_communes_list(df)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_input = st.text_input(
                "Rechercher par nom de commune ou code INSEE",
                placeholder="Ex: Paris, Lyon, Marseille, 75015...",
                help="Tapez au moins 2 caractères pour lancer la recherche"
            )
        
        commune = None
        
        if search_input and len(search_input) >= 2:
            # Rechercher les communes
            results = search_communes(search_input, code_to_name, available_codes, max_results=30)
            
            if results:
                # Créer les options formatées
                options = [format_commune_option(code, nom) for code, nom in results]
                
                with col2:
                    property_type = st.selectbox(
                        "Type de bien",
                        ["Tous", "Maisons", "Appartements"]
                    )
                
                selected = st.selectbox(
                    f"{len(results)} résultat(s) - Sélectionnez la commune",
                    [""] + options,
                    key="market_commune_selector"
                )
                
                if selected:
                    commune = get_code_from_formatted(selected)
            else:
                st.warning("Aucune commune trouvée avec ce critère")
                return
        elif search_input and len(search_input) < 2:
            st.info("Tapez au moins 2 caractères pour rechercher")
            return
        else:
            st.info("Utilisez la recherche ci-dessus pour sélectionner une commune")
            return
    
    except Exception as e:
        st.error(f"Erreur: {e}")
        # Fallback
        communes = get_communes_list(df)
        if not communes:
            st.warning("Aucune commune disponible")
            return
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            commune = st.text_input(
                "Code INSEE de la commune",
                placeholder="Ex: 75015",
                help="Entrez le code INSEE à 5 chiffres"
            )
            if commune not in communes:
                st.warning("Code INSEE non trouvé dans les données")
                return
        
        with col2:
            property_type = st.selectbox(
                "Type de bien",
                ["Tous", "Maisons", "Appartements"]
            )
    
    if not commune:
        return
    
    # Récupérer les données de la commune
    df_commune = get_commune_data(df, commune)
    
    if df_commune.empty:
        st.warning(f"Aucune donnée pour la commune {commune}")
        return
    
    # Statistiques globales
    st.markdown("---")
    st.subheader(f"Statistiques pour {commune}")
    
    # Calculer les stats
    prop_type = 'all' if property_type == "Tous" else property_type.lower()
    stats = get_market_stats(df, commune, prop_type)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Prix Moyen", f"{stats.get('prix_moyen', 0):,.0f} €")
    
    with col2:
        st.metric("Prix/m² Moyen", f"{stats.get('prix_m2_moyen', 0):,.0f} €")
    
    with col3:
        st.metric("Surface Moyenne", f"{stats.get('surface_moyenne', 0):.0f} m²")
    
    with col4:
        st.metric("Total Mutations", f"{stats.get('total_mutations', 0):.0f}")
    
    # Évolution dans le temps
    st.markdown("---")
    st.subheader("Évolution des Prix")
    
    evolution = calculate_market_evolution(df, commune)
    
    if not evolution.empty:
        # Graphique évolution prix/m²
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=evolution['annee'],
            y=evolution['prix_m2_moyen'],
            mode='lines+markers',
            name='Prix/m²',
            line=dict(color='#3498db', width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Évolution du Prix au m²",
            xaxis_title="Année",
            yaxis_title="Prix/m² (€)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Graphique variation annuelle
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(
            x=evolution['annee'][1:],
            y=evolution['variation_prix_m2'][1:],
            marker_color=['#2ecc71' if v > 0 else '#e74c3c' 
                         for v in evolution['variation_prix_m2'][1:]],
            name='Variation %'
        ))
        
        fig2.update_layout(
            title="Variation Annuelle du Prix/m²",
            xaxis_title="Année",
            yaxis_title="Variation (%)",
            height=350
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Analyse des tendances
        st.markdown("---")
        st.subheader("Analyse du Marché")
        
        trends = analyze_price_trends(df, commune)
        liquidity = calculate_market_liquidity(df, commune)
        market_score = calculate_market_score(df, commune)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**Tendance**")
            st.write(trends.get('tendance', 'Indéterminée'))
            st.caption(f"Variation moyenne: {trends.get('variation_prix_m2_annuelle', 0):.2f}%/an")
        
        with col2:
            st.info("**Liquidité**")
            st.write(liquidity.get('evaluation_liquidite', 'Indéterminée'))
            st.caption(f"{liquidity.get('transactions_par_an', 0):.0f} transactions/an")
        
        with col3:
            st.info("**Score Global**")
            st.write(f"{market_score.get('score', 0):.0f}/100")
            st.caption(market_score.get('appreciation', ''))
        
        # Tableau détaillé
        st.markdown("---")
        st.subheader("Données Détaillées")
        st.dataframe(evolution, use_container_width=True, hide_index=True)


def show_market_trends(df: pd.DataFrame):
    """Affiche les tendances du marché"""
    st.subheader("Tendances Globales du Marché")
    
    # Sélection de la période
    years_available = sorted(df['annee'].unique())
    
    col1, col2 = st.columns(2)
    with col1:
        year_start = st.selectbox("Année de début", years_available, index=0)
    with col2:
        year_end = st.selectbox("Année de fin", years_available, 
                               index=len(years_available)-1)
    
    # Filtrer par période
    df_period = df[(df['annee'] >= year_start) & (df['annee'] <= year_end)]
    
    # Évolution nationale
    evolution_nationale = df_period.groupby('annee').agg({
        'prix_moyen': 'mean',
        'prix_m2_moyen': 'mean',
        'surface_moy': 'mean',
        'nb_mutations': 'sum'
    }).reset_index()
    
    # Graphique prix moyen
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=evolution_nationale['annee'],
            y=evolution_nationale['prix_moyen'],
            mode='lines+markers',
            line=dict(color='#3498db', width=3),
            fill='tozeroy'
        ))
        fig1.update_layout(
            title="Prix Moyen des Transactions",
            xaxis_title="Année",
            yaxis_title="Prix Moyen (€)",
            height=350
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=evolution_nationale['annee'],
            y=evolution_nationale['prix_m2_moyen'],
            mode='lines+markers',
            line=dict(color='#2ecc71', width=3),
            fill='tozeroy'
        ))
        fig2.update_layout(
            title="Prix au m² Moyen",
            xaxis_title="Année",
            yaxis_title="Prix/m² (€)",
            height=350
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Volume des transactions
    st.markdown("---")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=evolution_nationale['annee'],
        y=evolution_nationale['nb_mutations'],
        marker_color='#9b59b6'
    ))
    fig3.update_layout(
        title="Volume des Transactions",
        xaxis_title="Année",
        yaxis_title="Nombre de Mutations",
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Statistiques de la période
    st.markdown("---")
    st.subheader("Statistiques de la Période")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        variation = ((evolution_nationale['prix_m2_moyen'].iloc[-1] / 
                     evolution_nationale['prix_m2_moyen'].iloc[0] - 1) * 100)
        st.metric("Variation Prix/m²", f"{variation:+.2f}%")
    
    with col2:
        total_mutations = evolution_nationale['nb_mutations'].sum()
        st.metric("Total Mutations", f"{total_mutations:,.0f}")
    
    with col3:
        avg_surface = evolution_nationale['surface_moy'].mean()
        st.metric("Surface Moyenne", f"{avg_surface:.0f} m²")


def show_top_communes(df: pd.DataFrame):
    """Affiche le classement des communes"""
    st.subheader("Classement des Communes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric = st.selectbox(
            "Critère de classement",
            ["prix_m2_moyen", "prix_moyen", "nb_mutations", "surface_moy"],
            format_func=lambda x: {
                "prix_m2_moyen": "Prix/m²",
                "prix_moyen": "Prix Moyen",
                "nb_mutations": "Nombre de Mutations",
                "surface_moy": "Surface Moyenne"
            }[x]
        )
    
    with col2:
        top_n = st.slider("Nombre de communes", 5, 50, 20)
    
    with col3:
        order = st.radio("Ordre", ["Plus élevé", "Plus faible"])
    
    # Récupérer le top communes
    ascending = (order == "Plus faible")
    top = get_top_communes(df, metric, top_n, ascending)
    
    if not top.empty:
        # Graphique
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=top['insee_com'].astype(str),
            y=top[metric],
            marker_color='#3498db',
            text=top[metric].round(0),
            textposition='outside'
        ))
        
        metric_name = {
            "prix_m2_moyen": "Prix/m² (€)",
            "prix_moyen": "Prix Moyen (€)",
            "nb_mutations": "Nombre de Mutations",
            "surface_moy": "Surface Moyenne (m²)"
        }[metric]
        
        fig.update_layout(
            title=f"Top {top_n} - {metric_name}",
            xaxis_title="Code INSEE",
            yaxis_title=metric_name,
            height=500,
            xaxis={'categoryorder': 'total ascending' if ascending else 'total descending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau
        st.markdown("---")
        st.subheader("Tableau Détaillé")
        
        top_display = top.copy()
        top_display[metric] = top_display[metric].apply(lambda x: f"{x:,.0f}")
        top_display['nb_mutations'] = top_display['nb_mutations'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(top_display, use_container_width=True, hide_index=True)


def show_market_overview(df: pd.DataFrame):
    """Affiche une vue d'ensemble du marché"""
    st.subheader("Vue d'Ensemble du Marché")
    
    # Statistiques globales
    stats = get_market_stats(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Prix Moyen National", f"{stats.get('prix_moyen', 0):,.0f} €")
    
    with col2:
        st.metric("Prix/m² Moyen", f"{stats.get('prix_m2_moyen', 0):,.0f} €")
    
    with col3:
        st.metric("Surface Moyenne", f"{stats.get('surface_moyenne', 0):.0f} m²")
    
    with col4:
        st.metric("Total Mutations", f"{stats.get('total_mutations', 0):,.0f}")
    
    # Distribution des prix
    st.markdown("---")
    st.subheader("Distribution des Prix au m²")
    
    if 'prix_m2_moyen' in df.columns:
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df['prix_m2_moyen'],
            nbinsx=50,
            marker_color='#3498db'
        ))
        fig.update_layout(
            title="Répartition des Prix au m²",
            xaxis_title="Prix/m² (€)",
            yaxis_title="Nombre de Communes",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Répartition Maisons vs Appartements
    st.markdown("---")
    st.subheader("Répartition Maisons vs Appartements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'nb_maisons' in df.columns and 'nb_apparts' in df.columns:
            total_maisons = df['nb_maisons'].sum()
            total_apparts = df['nb_apparts'].sum()
            
            fig = go.Figure(data=[go.Pie(
                labels=['Maisons', 'Appartements'],
                values=[total_maisons, total_apparts],
                hole=0.4,
                marker_colors=['#3498db', '#e74c3c']
            )])
            fig.update_layout(title="Répartition des Biens", height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Prix moyen par type
        if 'prop_maison' in df.columns and 'prix_m2_moyen' in df.columns:
            df_maisons = df[df['prop_maison'] > 80]
            df_apparts = df[df['prop_appart'] > 80]
            
            prix_maisons = df_maisons['prix_m2_moyen'].mean() if not df_maisons.empty else 0
            prix_apparts = df_apparts['prix_m2_moyen'].mean() if not df_apparts.empty else 0
            
            fig = go.Figure(data=[go.Bar(
                x=['Maisons', 'Appartements'],
                y=[prix_maisons, prix_apparts],
                marker_color=['#3498db', '#e74c3c'],
                text=[f"{prix_maisons:,.0f} €", f"{prix_apparts:,.0f} €"],
                textposition='outside'
            )])
            fig.update_layout(
                title="Prix/m² Moyen par Type",
                yaxis_title="Prix/m² (€)",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    show_market_analysis()
