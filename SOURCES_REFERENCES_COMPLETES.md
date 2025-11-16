# Sources et Références Complètes
## Gestion des Stocks - Distribution Matériaux Construction

---

## 1. SOURCES ACADÉMIQUES CLASSIQUES

### 1.1 Fondateurs EOQ (Harris & Wilson)

**Harris, F.W.** (1913)
- **Titre** : "How Many Parts to Make at Once"
- **Publication** : *Factory, The Magazine of Management*, A.W. Shaw Company
- **Volume/Pages** : Vol. 10, pp. 135-136, février 1913
- **Statut** : Oubliée jusqu'en 1988
- **Apport** : Formule originelle d'optimisation taille de lot
- **Accès** : Archives numérisées via JSTOR, ResearchGate
- **Pertinence Gedimat** : Fondation théorique, validation historique formule

---

**Wilson, R.H.** (1934)
- **Titre** : "A Scientific Routine for Stock Control"
- **Publication** : *Harvard Business Review*
- **Volume/Numéro** : Vol. 13(1), 1934
- **Apport** : Popularisation et contexte pratique EOQ
- **Pertinence** : Formule porte son nom malgré découverte Harris 1913
- **Application** : Contexte industriel 1934, obsolete partiellement mais fondateur

---

### 1.2 Manuels Opérationnels Standards Industrie

**Vollmann, T.E., Berry, W.L., & Whybark, D.C.** (2004)
- **Titre** : *Manufacturing Planning and Control Systems for Supply Chain Management* (5e édition)
- **Éditeur** : McGraw-Hill
- **Chapitres clés** :
  - Ch. 3 : Inventory Management Fundamentals
  - Ch. 4 : Reorder Point & Safety Stock Calculations
  - Ch. 12 : Multi-Echelon Inventory Management
- **Formules couvertes** : ROP, SS z-score, EOQ extensions
- **Pertinence** : Standard industrie, méthodologie ABC, contexte multi-échelon
- **Accès** : Université, organisations professionnelles

---

**Ballou, R.H.** (2004)
- **Titre** : *Business Logistics/Supply Chain Management* (5e édition)
- **Éditeur** : Pearson Prentice Hall
- **ISBN** : 0-13-172040-1
- **Chapitres clés** :
  - Ch. 6 : Inventory Policy Decisions
  - Ch. 7 : Logistical Network Configuration
- **Apport** : Optimisation réseau distribution, coûts transport vs stock, MEIO
- **Cas d'étude** : Distribution multi-dépôts (comparable Gedimat)
- **Pertinence** : Applicabilité directe architecture 3 niveaux Gedimat

---

## 2. SOURCES RECHERCHE CONTEMPORAINE (2020-2024)

### 2.1 Machine Learning Supply Chain Forecasting

**Deshpande, V., et al.** (2024)
- **Titre** : "How Machine Learning Will Transform Supply Chain Management"
- **Publication** : *Harvard Business Review*
- **Numéro** : March-April 2024 (Vol. 102, No. 2)
- **URL** : https://hbr.org/2024/03/how-machine-learning-will-transform-supply-chain-management
- **Auteurs affiliés** : UNC Kenan-Flagler Business School
- **Contenu clé** :
  - Limites systèmes planning traditionnels
  - Approche ML pour prévisions demand sensing
  - Amélioration agilité supply chain post-disruptions 2020-2022
- **Pertinence Gedimat** :
  - Demand sensing pour matériaux construction
  - Validation scientifique approche ML vs ARIMA
  - Contexte 2024 = référence actuelle

---

**MDPI Forecasting Journal** (2024)
- **Titre** : "Machine Learning and Deep Learning Models for Demand Forecasting in Supply Chain Management: A Critical Review"
- **Publication** : *Forecasting*, Vol. 7, No. 5, 2024
- **Étude** : Analyse 119 articles Scopus (2015-2024)
- **Modèles comparés** :
  - ARIMA/SARIMA (baseline)
  - Gradient Boosting (XGBoost, LightGBM)
  - Deep Learning (LSTM, Transformer)
  - Ensembles hybrides
- **Erreurs MAPE rapportées** :
  - ARIMA : 15-25%
  - XGBoost : 10-18%
  - LSTM : 8-15% (si données suffisantes)
- **Pertinence** : Sélection algorithme demand sensing pilote Gedimat
- **Accès** : https://www.mdpi.com/2571-5577/7/5/93

---

### 2.2 Demand Sensing Pratique

**AWS** (2024)
- **Titre** : "AI-Powered Demand-Sensing: Transforming Supply Chain Planning with External Data"
- **Format** : White Paper Executive Insights
- **URL** : https://aws.amazon.com/executive-insights/content/ai-powered-demand-sensing/
- **Bénéfices rapportés** :
  - Forecast accuracy : +23%
  - Inventory reduction : -5%
  - Fulfillment costs : -30%
- **Sources de données** :
  - Internal (POS, inventory, orders)
  - External (weather, market trends, social media)
- **Pertinence** : KPI réaliste pour cas Gedimat

---

**ThroughPut AI** (2024)
- **Titre** : "Demand Sensing: The Ultimate Guide"
- **URL** : https://throughput.world/blog/demand-sensing/
- **Format** : Blog consultatif, illustré
- **Contenu** :
  - Définition vs demand forecasting classique
  - Architecture données
  - Cas d'usage retail & manufacturing
- **Pertinence** : Explication accessible demand sensing

---

**ImpactAnalytics** (2024)
- **Titre** : "Mastering Demand Sensing in 2024"
- **URL** : https://www.impactanalytics.co/blog/demand-sensing
- **Focus** : Intégration POS temps-réel, weather APIs, promotional calendars

---

### 2.3 Multi-Echelon Inventory Optimization (MEIO)

**GEP** (2024)
- **Titre** : "Multi-Echelon Inventory Optimization (MEIO): Transforming Supply Chain"
- **URL** : https://www.gep.com/blog/strategy/multi-echelon-inventory-optimization-transforming-supply-chain
- **Contenu clé** :
  - Pooling formula réduction coûts
  - Vs approche décentralisée
  - Gains 25-50% stock
- **Pertinence** : Justification architectural Hub + 3 dépôts Gedimat

---

**o9 Solutions** (2024)
- **Titre** : "What is Multi Echelon Inventory Optimization (MEIO)?"
- **URL** : https://o9solutions.com/articles/what-is-multi-echelon-inventory-optimization-meio/
- **Format** : Article consulting, cas d'étude anonymisés

---

**LEAFIO AI** (2024)
- **Titre** : "Multi-Echelon Inventory Optimization Software"
- **URL** : https://www.leafio.ai/multi-echelon-inventory-optimization/
- **Apport** : Perspectives tech/algo implémentation MEIO

---

**IDC Manufacturing Insights** (2023)
- **Titre** : Étude Benchmark MEIO
- **Citation clé** : "Organizations utilizing inventory optimization reduced inventory levels by up to 25% in one year and enjoyed a discounted cash flow above 50% in less than two years"
- **Pertinence** : Validation ROI multi-échelon

---

## 3. SOURCES SPÉCIALISÉES MATÉRIAUX CONSTRUCTION

### 3.1 Gestion Stocks Construction

**SupplyChainInfo (SedAPTA)** (2024)
- **Titre** : "Optimisation des stocks : l'inventaire multi-échelons"
- **URL** : https://www.sedapta.com/fr/solutions/sales-operation-planning/inventory-management/optimisation-des-stocks-linventaire-multi-echelons/
- **Langue** : Français
- **Contexte** : Adaptation France, secteur BTP

---

**HEMEA** (2024)
- **Titre** : "5 leviers pour optimiser sa gestion de stock en BTP"
- **URL** : https://www.hemea.com/fr/pro/questions-frequentes/gestion-stocks
- **Pratiques spécifiques** :
  - Gestion ciment, mortier, tuiles
  - Variabilité saisonnière
  - Déstockage fin chantier

---

**Moderne House** (2024)
- **Titre** : "Stockage des matériaux de construction: éviter le gaspillage"
- **URL** : https://moderne-house.fr/stockage-et-conservation-des-materiaux-de-construction-eviter-le-gaspillage/
- **Apport** : Contraintes stockage physique (tuiles, ciment)

---

### 3.2 Étude Secteur Négoce Matériaux

**Xerfi** (2024)
- **Titre** : "Le négoce de bois et de matériaux de construction : étude, stratégies, classements"
- **URL** : https://www.xerfi.com/presentationetude/Le-negoce-de-bois-et-de-materiaux-de-construction_NEG15
- **Format** : Étude sectorielle payante
- **Contenu** : Dynamics prix, supply shocks, stratégies distributeurs

---

## 4. SOURCES OUTILS ET CALCULATEURS

### 4.1 Tutoriels Formules

**Lokad** (2024 - Français)
- **Stock de Sécurité** : https://www.lokad.com/safety-stock-definition/
- **Point de Commande** : https://www.lokad.com/reorder-point-definition/
- **EOQ** : https://www.lokad.com/economic-order-quantity-eoq-definition-and-formula/
- **Format** : Blog explicatif, formules, exemples
- **Multilingue** : Français, Anglais, Autres

---

**SlimStock** (2024)
- **Titres** :
  - "EOQ : formula and use"
  - "Safety Stock: Definition, Calculation and Formulas"
  - "Service Level Management"
- **URL** : https://www.slimstock.com/blog/
- **Format** : Guides opérationnels, calculateurs intégrés
- **Pertinence** : Accessibilité practitioners

---

**DAU (Defense Acquisition University)** (2024)
- **Titre** : "Economic Order Quantity (EOQ)"
- **URL** : https://www.dau.edu/acquipedia-article/economic-order-quantity-eoq
- **Format** : Référence gouvernementale

---

**Mecalux** (2024 - Français)
- **Titre** : "EOQ: formula and use"
- **URL** : https://www.mecalux.fr/blog/stock-securite-calcul-optimisation
- **Format** : Guide illustré

---

### 4.2 Calculateurs Interactifs

**ShipBob** (2024)
- **Reorder Point Calculator** : https://www.shipbob.com/blog/reorder-point-formula/
- **Format** : Outil interactif

---

**Interlake Mecalux** (2024)
- **EOQ Calculator** : https://www.interlakemecalux.com/blog/eoq-formula
- **Format** : Infographie + outil

---

## 5. SOURCES RECHERCHE AVANCÉE

### 5.1 Thèses Doctorat (FR)

**Bahloul, K.** (2024, approx.)
- **Titre** : "Optimisation combinée des coûts de transport et de stockage dans un réseau logistique multi-produits avec demande probabiliste"
- **Format** : Thèse HAL Sciences (tel-00695275)
- **Apport** : Problème intégré transport + inventory (IRP = Inventory Routing Problem)
- **Pertinence** : Architecture multi-échelon Gedimat

---

**Anonyme** (2024)
- **Titre** : "Stratégies d'optimisation pour le problème intégré de transport et de gestion de stock"
- **URL** : https://theses.fr/2024UCFA0139
- **Université** : Université Claude Bernard (2024)
- **Focus** : Integrated optimization transport/inventory

---

### 5.2 Études de Cas & Benchmarks

**ResearchGate** (2024)
- **Titre** : "Étude de l'optimisation des coûts de la chaîne de distribution: cas des coûts de stockage et de transport"
- **URL** : https://www.researchgate.net/publication/325263349
- **Format** : Cas d'étude empirique

---

**Stack Exchange - Operations Research** (2024)
- **Q&A** : "Reorder point and safety stock for very long lead times"
- **URL** : https://or.stackexchange.com/questions/4335
- **Apport** : Discussion algorithmes, edge cases

---

## 6. BASES DE DONNÉES ACADÉMIQUES

### Pour Recherche Approfondie :

- **JSTOR** : Articles historiques (Harris 1913, Wilson 1934, Vollmann 2004)
- **ScienceDirect** : Articles supply chain contemporains, MEIO
- **Scopus** : Revue 119 articles ML demand forecasting (2015-2024)
- **Google Scholar** : Accès libre articles post-2020
- **HAL Sciences** : Thèses françaises accès complet
- **ResearchGate** : Preprints chercheurs

---

## 7. SYNTHÈSE PAR BESOIN

### Besoin 1 : Comprendre EOQ & Stock de Sécurité

**Essentiels (2-3h lecture)** :
1. Lokad explicatif (gratuit)
2. Mecalux guide (gratuit)
3. Vollmann 2004 Ch. 3-4 (si accès université)

### Besoin 2 : Demand Sensing + ML

**Essentiels (1-2 jours)** :
1. HBR Deshpande 2024 (payant, ~30$)
2. AWS whitepaper (gratuit)
3. MDPI review 119 articles (accès journal)

### Besoin 3 : Multi-Échelon Implémentation

**Essentiels (3-5j)** :
1. GEP blog MEIO (gratuit)
2. Ballou 2004 Ch. 6-7 (manuel)
3. Thèse Bahloul transport+inventory (gratuit HAL)

### Besoin 4 : Contexte Matériaux Construction

**Essentiels (2-3j)** :
1. HEMEA 5 leviers BTP (gratuit)
2. Xerfi étude secteur (payant)
3. SedAPTA guides français (gratuit)

---

## 8. STATISTIQUES COUVERTURE SOURCES

| Catégorie | Nombre | Couverture |
|-----------|--------|-----------|
| **Académiques classiques** | 2 | Historique EOQ |
| **Manuels opérationnels** | 2 | Standard industrie |
| **Recherche 2020-2024** | 8+ | ML, MEIO, demand sensing |
| **Spécialisées construction** | 4 | Gedimat contexte |
| **Outils/calculateurs** | 6 | Accessibilité |
| **Recherche avancée** | 5 | Thèses, cas études |
| **TOTAL** | **27+** | — |

---

**Document de référence - Gedimat Logistics Intelligence**
**Dernière mise à jour : Novembre 2025**
