# 🚀 Guide de Démarrage Rapide

## Installation Express (5 minutes)

### 1️⃣ Vérifier Python

```bash
python --version
```

Vous devez avoir Python 3.8 ou supérieur. Sinon, téléchargez-le depuis [python.org](https://www.python.org/).

### 2️⃣ Installer les Dépendances

```bash
pip install -r requirements.txt
```

### 3️⃣ Lancer l'Application

**Windows :**
```bash
start.bat
```
ou
```bash
streamlit run simulateur_immobilier.py
```

**Mac/Linux :**
```bash
chmod +x start.sh
./start.sh
```
ou
```bash
streamlit run simulateur_immobilier.py
```

### 4️⃣ Accéder à l'Application

Ouvrez votre navigateur à l'adresse : **http://localhost:8501**

## 📚 Utilisation Rapide

### Scénario 1 : Première Simulation

1. **Dans la barre latérale**, entrez :
   - Surface : 50 m²
   - Prix au m² : 4 000 €
   - Apport : 20 000 €

2. **Configurez le crédit** :
   - Taux : 3,8%
   - Durée : 20 ans

3. **Définissez les revenus** :
   - Loyer au m² : 13 €

4. **Consultez** l'onglet "💰 Analyse" pour voir :
   - Rentabilité brute et nette
   - Cashflow mensuel
   - ROI

### Scénario 2 : Analyse de Marché

1. **Allez dans l'onglet** "🏘️ Marché DVF"

2. **Sélectionnez** le code INSEE de votre commune
   - Paris 15ème : 75115
   - Lyon 6ème : 69386
   - Marseille 8ème : 13208

3. **Comparez** votre projet aux données réelles

4. **Obtenez** un score et une recommandation

### Scénario 3 : Optimisation Fiscale

1. **Accédez** à l'onglet "💼 Fiscalité"

2. **Choisissez** votre régime :
   - Location nue classique
   - LMNP avec amortissement
   - Loi Pinel

3. **Comparez** les avantages fiscaux

4. **Visualisez** l'impact sur votre cashflow

### Scénario 4 : Comparaison de Projets

1. **Dans l'onglet** "⚖️ Comparaison"

2. **Configurez** votre premier projet

3. **Cliquez** sur "Ajouter le scénario actuel"

4. **Modifiez** les paramètres pour un second projet

5. **Ajoutez-le** et comparez les résultats

## 🎯 Cas d'Usage Fréquents

### 🏢 Investissement Locatif Classique

**Objectif** : Générer des revenus complémentaires

**Configuration recommandée** :
- Bien ancien à rénover (meilleur prix)
- Financement à 80-90%
- Loyer légèrement sous le marché (bonne occupation)
- Régime fiscal : Réel (déduction des travaux)

**Indicateurs à surveiller** :
- ✅ Rentabilité nette > 4%
- ✅ Cashflow positif après 2-3 ans
- ✅ ROI > 8%

### 💰 Création de Patrimoine

**Objectif** : Valoriser son épargne à long terme

**Configuration recommandée** :
- Bien de qualité en bon emplacement
- Financement long (25-30 ans)
- Focus sur la plus-value future
- Régime fiscal : LMNP (amortissement)

**Indicateurs à surveiller** :
- ✅ Prix/m² sous la médiane du marché
- ✅ Tendance de marché positive
- ✅ Score d'investissement > 70

### 🎁 Réduction d'Impôts

**Objectif** : Optimiser sa fiscalité

**Configuration recommandée** :
- Bien neuf éligible Pinel
- Zone A, A bis ou B1
- Loyer au plafond autorisé
- Engagement 9 ans minimum

**Indicateurs à surveiller** :
- ✅ Réduction fiscale > 15% du prix
- ✅ Loyer proche du marché
- ✅ Cashflow neutre ou positif avec Pinel

### 📈 Spéculation Court Terme

**Objectif** : Revendre avec plus-value rapide

**Configuration recommandée** :
- Bien à rénover
- Marché en forte croissance
- Financement court ou cash
- Pas de location (travaux immédiats)

**Indicateurs à surveiller** :
- ✅ Variation prix/m² > 5%/an
- ✅ Volume de transactions élevé
- ✅ Prix d'achat < médiane -20%

## 🔍 Trouver le Code INSEE de sa Commune

### Méthode 1 : Site Officiel

Visitez : [insee.fr/geographie](https://www.insee.fr/fr/recherche/recherche-geographique)

### Méthode 2 : Dans l'Application

1. Allez dans "🏘️ Marché DVF"
2. Ouvrez le menu déroulant "Code INSEE"
3. Tapez le nom de votre ville
4. Les codes correspondants s'affichent

### Codes des Principales Villes

| Ville | Code INSEE |
|-------|-----------|
| Paris 1er | 75101 |
| Paris 15ème | 75115 |
| Lyon 1er | 69381 |
| Lyon 6ème | 69386 |
| Marseille 1er | 13201 |
| Marseille 8ème | 13208 |
| Toulouse | 31555 |
| Nice | 06088 |
| Nantes | 44109 |
| Bordeaux | 33063 |
| Lille | 59350 |
| Strasbourg | 67482 |

## ❓ FAQ Rapide

**Q : Les données DVF ne chargent pas ?**
R : Vérifiez que les fichiers CSV sont bien dans le dossier `/data`

**Q : Comment exporter mes résultats ?**
R : Utilisez la fonction "Print" de votre navigateur ou faites des captures d'écran

**Q : Puis-je modifier les hypothèses d'évolution ?**
R : Oui, dans l'onglet principal, ajustez "Appréciation du bien" et "Augmentation loyer"

**Q : Les calculs fiscaux sont-ils exacts ?**
R : Ils sont indicatifs. Consultez un expert-comptable pour votre situation personnelle.

**Q : Puis-je utiliser cette app sur mobile ?**
R : Oui, mais l'expérience est optimisée pour ordinateur

## 🆘 Support

**Problème technique ?**
1. Vérifiez que toutes les dépendances sont installées
2. Consultez les messages d'erreur dans le terminal
3. Vérifiez les logs Streamlit

**Question sur les calculs ?**
- Consultez le README.md pour les formules détaillées
- Référez-vous aux tooltips (?) dans l'application

**Suggestion d'amélioration ?**
- Créez une issue sur GitHub
- Contactez l'équipe de développement

## 📊 Prochaines Étapes

Après avoir maîtrisé les bases :

1. ✅ Explorez tous les onglets
2. ✅ Comparez plusieurs communes
3. ✅ Testez différents régimes fiscaux
4. ✅ Créez des scénarios de comparaison
5. ✅ Consultez la documentation complète (README.md)

## 🎓 Ressources Complémentaires

### Dans le Projet
- **README.md** : Documentation complète
- **RELEASE_NOTES.md** : Toutes les fonctionnalités
- **data/README_DVF.md** : Guide des données DVF

### Externes
- [data.gouv.fr](https://data.gouv.fr) : Données DVF officielles
- [service-public.fr](https://service-public.fr) : Informations fiscales
- [anil.org](https://anil.org) : Informations juridiques immobilières

---

**Bon investissement ! 🏠💰📈**
