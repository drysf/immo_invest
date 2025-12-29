# Documentation des Données DVF

## Source des Données

Les données DVF (Demandes de Valeurs Foncières) sont issues de la base de données publique de l'administration fiscale française. Elles recensent l'ensemble des ventes immobilières réalisées en France.

## Structure des Fichiers CSV

### Colonnes disponibles

| Colonne | Type | Description |
|---------|------|-------------|
| `INSEE_COM` | String | Code INSEE de la commune (5 caractères) |
| `annee` | Integer | Année de la transaction |
| `nb_mutations` | Integer | Nombre total de mutations (ventes) |
| `NbMaisons` | Integer | Nombre de maisons vendues |
| `NbApparts` | Integer | Nombre d'appartements vendus |
| `PropMaison` | Float | Proportion de maisons (%) |
| `PropAppart` | Float | Proportion d'appartements (%) |
| `PrixMoyen` | Float | Prix moyen de vente (€) |
| `Prixm2Moyen` | Float | Prix moyen au m² (€) |
| `SurfaceMoy` | Float | Surface moyenne (m²) |

### Exemple de données

```csv
INSEE_COM,annee,nb_mutations,NbMaisons,NbApparts,PropMaison,PropAppart,PrixMoyen,Prixm2Moyen,SurfaceMoy
75101,2024,450,0,450,0,100,520000,9800,53
75102,2024,380,0,380,0,100,680000,11200,61
69001,2024,320,25,295,8,92,285000,4500,63
```

## Années Disponibles

- **dvf2017.csv** : Données de l'année 2017
- **dvf2022.csv** : Données de l'année 2022
- **dvf2023.csv** : Données de l'année 2023
- **dvf2024.csv** : Données de l'année 2024

## Codes INSEE

### Exemples de codes INSEE par département

#### Île-de-France
- **75xxx** : Paris (75001 à 75120)
- **92xxx** : Hauts-de-Seine
- **93xxx** : Seine-Saint-Denis
- **94xxx** : Val-de-Marne
- **77xxx** : Seine-et-Marne
- **78xxx** : Yvelines
- **91xxx** : Essonne
- **95xxx** : Val-d'Oise

#### Grandes Métropoles
- **69xxx** : Rhône (Lyon)
- **13xxx** : Bouches-du-Rhône (Marseille)
- **31xxx** : Haute-Garonne (Toulouse)
- **33xxx** : Gironde (Bordeaux)
- **59xxx** : Nord (Lille)
- **44xxx** : Loire-Atlantique (Nantes)

#### Autres villes importantes
- **67xxx** : Bas-Rhin (Strasbourg)
- **34xxx** : Hérault (Montpellier)
- **35xxx** : Ille-et-Vilaine (Rennes)
- **06xxx** : Alpes-Maritimes (Nice)

## Utilisation dans l'Application

### Chargement des données

```python
from utils.dvf_loader import load_dvf_data

# Charger toutes les années
df = load_dvf_data()

# Charger des années spécifiques
df = load_dvf_data(years=[2022, 2023, 2024])
```

### Recherche par commune

```python
from utils.dvf_loader import get_commune_data

# Récupérer les données pour Paris 15ème
df_paris15 = get_commune_data(df, "75115")
```

### Statistiques de marché

```python
from utils.dvf_loader import get_market_stats

# Statistiques globales pour une commune
stats = get_market_stats(df, commune="75115", property_type="appartements")

print(f"Prix moyen: {stats['prix_moyen']:,.0f} €")
print(f"Prix/m² moyen: {stats['prix_m2_moyen']:,.0f} €")
print(f"Surface moyenne: {stats['surface_moyenne']:.0f} m²")
```

## Limites et Précautions

### Données manquantes
- Certaines petites communes peuvent avoir peu ou pas de données
- Les transactions peuvent être agrégées annuellement
- Certaines années peuvent manquer pour certaines communes

### Interprétation
- Les prix sont des **moyennes** : ils peuvent masquer une grande variabilité
- Les données ne distinguent pas l'état du bien (neuf, ancien, rénové)
- Elles ne prennent pas en compte les spécificités individuelles (vue, étage, etc.)

### Confidentialité
- Les données sont agrégées pour préserver l'anonymat
- Elles ne permettent pas d'identifier des transactions individuelles

## Sources Officielles

- **data.gouv.fr** : Portail open data du gouvernement français
- **DVF Explorer** : Outil de visualisation officiel
- **API DVF** : Accès programmatique aux données

## Mise à Jour des Données

Pour mettre à jour les fichiers DVF :

1. Téléchargez les nouvelles données depuis data.gouv.fr
2. Placez les fichiers CSV dans le dossier `/data`
3. Nommez-les selon le format : `dvfYYYY.csv`
4. Relancez l'application

## Format Alternatif

Si vous disposez de données DVF dans un format différent, le module `dvf_loader.py` peut être adapté en modifiant la fonction `load_dvf_data()`.

## Calculs Dérivés

L'application calcule automatiquement :

- **Évolution temporelle** : Variation annuelle des prix
- **Tendances** : Régression linéaire sur les prix
- **Liquidité** : Volume de transactions
- **Volatilité** : Écart-type des prix
- **Score de marché** : Évaluation globale (0-100)

## Exemple Complet

```python
from utils.dvf_loader import load_dvf_data, get_commune_data
from utils.market_analysis import (
    analyze_price_trends,
    calculate_market_score,
    get_investment_recommendation
)

# 1. Charger les données
df = load_dvf_data()

# 2. Analyser une commune
commune = "75115"  # Paris 15ème
trends = analyze_price_trends(df, commune)
score = calculate_market_score(df, commune)

# 3. Obtenir une recommandation
reco = get_investment_recommendation(
    df=df,
    commune=commune,
    prix_m2=8500,
    surface=45
)

print(f"Tendance: {trends['tendance']}")
print(f"Score: {score['score']}/100 - {score['appreciation']}")
print(f"Recommandation: {reco['recommandation']}")
```

## Support

Pour toute question sur les données DVF, consultez :
- La documentation officielle sur data.gouv.fr
- Les forums de discussion sur l'open data français
- Le code source dans `utils/dvf_loader.py`
