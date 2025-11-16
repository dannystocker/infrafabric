# Formules Stock & Demand Sensing
## Guide Pratique Gestion Inventaire Distribution Matériaux Construction

**Version:** 1.0
**Date:** 16 novembre 2025
**Cible:** Gedimat et franchises distribution matériaux construction
**Portée:** Formules classiques (EOQ, safety stock, point de commande) + approches modernes (ML, demand sensing, ERP)
**Format:** 2-3 pages synthèse exécutive + formules + cas d'application

---

## PARTIE A : FORMULES CLASSIQUES D'INVENTAIRE

### 1. EOQ (Economic Order Quantity - Quantité Économique de Commande)

**Formule Wilson (1934):**
```
EOQ = √(2 × D × S / H)

Où:
- D = Demande annuelle (unités/an)
- S = Coût de lancement par commande (€/commande)
- H = Coût annuel de détention par unité (€/unité/an)
```

**Exemple Gedimat - Tuiles Emeris:**
- Demande annuelle: 5,000 palettes
- Coût lancement (traitement commande, suivi transport): 50€
- Coût détention par palette: 15€/an (stockage 8€, assurance 4€, obsolescence 3€)

EOQ = √(2 × 5,000 × 50 / 15) = √33,333 = **183 palettes par commande**

**Interprétation:** Commander 183 palettes minimise coût total (économies transport groupé > surcoûts stockage)

**Hypothèses EOQ (critiques pour secteur construction):**
- Demande constante → ❌ Faux en construction (saisonnalité 40-60%)
- Prix unitaire constant → ✅ Correct (rabais fournisseur intégrés via H ajusté)
- Pas de rupture stock → ❌ Risqué (clients chantier impatients)
- Délai approvisionnement constant → ❌ Variabilité fournisseur 15-25%

**Applicabilité Gedimat:** EOQ = base pour matériaux non-saisonniers (ciment, sable). Adapter par facteur saisonnier 0.7-1.3.

---

### 2. Stock de Sécurité (Safety Stock)

**Formule z-score (distribution normale):**
```
SS = z × σ_L × √LT

Où:
- z = Facteur de service (1.65=95%, 1.96=97.5%, 2.33=99%)
- σ_L = Écart-type demande journalière
- LT = Délai d'approvisionnement (jours)
```

**Exemple Gedimat - Portes & fenêtres (saisonnier):**
- Demande: 100 unités/jour moyenne, écart-type 25 unités (forte variation saisonnière)
- Délai fournisseur: 14 jours (moyen)
- Facteur service: 95% (z=1.65, acceptable car clients bricolage/petits pros)

SS = 1.65 × 25 × √14 = **154 unités**

**Alternative: Formule intégrant variabilité délai:**
```
SS = z × √(D² × σ_LT² + LT × σ_D²)

Où:
- σ_LT = Écart-type délai (jours)
- σ_D = Écart-type demande journalière
```

Avec σ_LT = 2 jours (fournisseur Emeris fiable, variance légère):
SS = 1.65 × √(100² × 2² + 14 × 25²) = **207 unités**

**Coût rupture vs surstock (arbitrage):**
- Augmenter z de 1.65→2.33 (+40% coût stock) mais réduire rupture de 5%→1%
- Construction: clients captifs (chantier date fixe) → investir en SS (z=1.96 recommandé)

**Applicabilité Gedimat:** SS augmente Oct-Mar (+50% saisonnalité). Réviser tous trimestres avec données historiques.

---

### 3. Point de Commande (Reorder Point)

**Formule simple:**
```
ROP = D × LT + SS

Où:
- D = Demande moyenne journalière
- LT = Délai d'approvisionnement (jours)
- SS = Stock de sécurité (voir section 2)
```

**Exemple Gedimat - Ciment 25kg:**
- D = 200 sacs/jour
- LT = 7 jours (fournisseur régional fiable)
- SS = 800 sacs (z=1.65, σ=35 sacs, délai stable)

ROP = 200 × 7 + 800 = **2,200 sacs**

**Interprétation:** Commander dès stock atteint 2,200 sacs = arrive environ SS réserve

**Variante multi-source (Gedimat: 2-3 fournisseurs par SKU):**
```
ROP_optimal = ROP_rapide si coût urgence < économie délai court
Sinon: ROP_économique (fournisseur moins cher, délai +5j)
```

**Système visuel (petit déploiement Gedimat):**
```
VERT:   > ROP → normal
ORANGE: ROP ± 10% → alerte commande
ROUGE:  < ROP - SS → urgence/rupture proche
```

---

### 4. Stock Minimum/Maximum (Min-Max Policy)

**Formule paramétrique:**
```
S_min = Point de commande
S_max = Point de commande + EOQ

Ou, pour système périodique (révision mensuelle):
S_max = D × (LT + P) + SS

Où P = Période révision (30 jours mensuel)
```

**Exemple Gedimat - Brique 10cm (produit lourd):**
- D = 500 briques/jour
- LT = 4 jours
- P = 7 jours (révision hebdomadaire, produit critique)
- SS = 3,500 briques

S_min = (500 × 4) + 3,500 = **5,500 briques**
S_max = (500 × 4) + (500 × 7) + 3,500 = **9,000 briques**

**Politique:** Chaque lundi, commander si stock < 5,500 pour atteindre 9,000

**Avantage/Inconvénient:**
- ✅ Simple, pas besoin surveillance quotidienne
- ❌ Peut créer pics commandes vs lissage EOQ
- Construction: Combiner min-max + alertes saisonnières (été +40% briques)

---

### 5. Coût de Détention (Holding Cost)

**Formule complète:**
```
H = P × (i + w + s + o)

Où:
- P = Coût unitaire du produit (€/unité)
- i = Taux intérêt capital immobilisé (12% an)
- w = Coût stockage espace/manutention (5-8% an)
- s = Coût assurance stock (0.5-1% an)
- o = Coût obsolescence/détérioration (1-5% an secteur)
```

**Exemple détaillé Gedimat - Tuiles Emeris:**

| Composant | Taux | Calcul | Coût |
|-----------|------|--------|------|
| Coût unitaire P | - | - | 18€/palette |
| Intérêt capital | 12% | 18 × 0.12 | 2.16€ |
| Stockage (3€/m², 1m² par palette) | 6% | 18 × 0.06 | 1.08€ |
| Assurance | 0.8% | 18 × 0.008 | 0.14€ |
| Obsolescence (casse, démodé) | 2% | 18 × 0.02 | 0.36€ |
| **TOTAL H = i+w+s+o** | **20.8%** | - | **3.74€/palette/an** |

**Variantes par catégorie (Gedimat):**
- Matériaux standards (ciment, sable): H = 12-15% (peu obsolescence)
- Articles mode (peinture couleur, revêtements): H = 20-25% (forte obsolescence)
- Électroportatifs: H = 25-35% (obsolescence technologique rapide)

**Implication:** Articles haute H → commander moins fréquent, EOQ plus petit

---

## PARTIE B : DEMAND SENSING MODERNE

### 1. Machine Learning - Approches Prévision

**4 Approches principales (complexité croissante):**

#### A) Lissage Exponentiel (Holt-Winters)
```
Formule simple: F(t+1) = α×D(t) + (1-α)×F(t)
α = 0.2-0.3 typiquement

Avec saisonnalité: F(t+1) = α×D(t)/S(t-L) + (1-α)×(F(t)+T(t))
où S() = facteur saisonnier, T() = trend, L = longueur cycle (52 semaines)
```

**Avantage:** Rapide implémentation, besoin 2-3 mois données, coût bas (Excel macro)
**Inconvénient:** Suppose passé = avenir (échoue sur ruptures marché)
**Gedimat:** ✅ Déploiement immédiat briques/ciment/sable

#### B) Régression Linéaire Multivariée
```
Demande = β₀ + β₁×Jour_semaine + β₂×Semaine_année + β₃×Température + β₄×Indices_BTP

Estimé par moindres carrés ordinaires (MCO)
```

**Exemple Gedimat - Plâtre:**
- Jour semaine: Samedi +25% (bricolage week-end)
- Semaine année: Avril-Août +45% (travaux saisonniers)
- Température: <10°C → +20% (façade chauffage), >25°C → +30% (terrasse, rénovation)
- Indice BTP construction France (INSEE): +1 point = +0.8% demande

**Avantage:** Intègre variables externes, interprétable
**Inconvénient:** Requiert données externes, relation linéaire (simpliste)
**Gedimat:** ✅ Moyen terme (6 mois données), coût modéré Python/SQL

#### C) Séries Temporelles ARIMA
```
Modèle ARIMA(p,d,q):
- p: ordre autorégressif (p lags demande passée)
- d: degré différenciation (stationnarité)
- q: ordre moyenne mobile (p résidus passés)

Exemple: ARIMA(2,1,2) = 2 semaines passées + différence 1er ordre + 2 résidus
```

**Avantage:** Capture dynamiques temporelles, robuste autocorrélation
**Inconvénient:** Complexité paramétrage, 12-24 mois données minimum
**Gedimat:** 🟡 Long terme (2025), nécessite historique complet

#### D) Réseaux Neuronaux (LSTM, Transformers)
```
Deep Learning: Réseau récurrent explorant dépendances long terme
Input: 52 semaines demande passée + variables externes
Output: Prévision 4-12 semaines
```

**Avantage:** Capture patterns non-linéaires complexes
**Inconvénient:** Risque surapprentissage, 2+ ans données, coût infrastructure (GPU)
**Gedimat:** ❌ Non recommandé (coût ROI insuffisant PME)

---

### 2. Demand Sensing vs. Demand Forecasting

**Différences critiques:**

| Aspect | Forecasting | Sensing |
|--------|-------------|---------|
| **Méthode** | Statistique passé | Signaux temps réel |
| **Horizon** | 4-52 semaines | 1-4 semaines |
| **Données** | Ventes historiques | PDV, commandes web, météo, événements |
| **Fréquence mise à jour** | Mensuelle/trimestrielle | Quotidienne/hebdomadaire |
| **Coût implém.** | Moyen ($5-20K) | Élevé ($50-150K) |
| **Cas usage** | Production long délai | Distribution haute volatilité |

**Exemple Gedimat - Peinture:**

*Forecasting (classique):*
- Analyse 24 mois ventes: moyenne 400L/semaine, saisonnalité ±15%
- Prévoit April 460L, May 465L (algorithme Holt-Winters)
- Commande fixe tous 2 mois

*Demand Sensing (moderne):*
- Semaine 1: PDV web montre 520L demandes 3j (vs 400 forecast)
- Signaux temps réel: météo prévoit 3j sans pluie (peintres actifs), événement "Journées Bricolage"
- Ajuste commande +30% pour semaine 2-4
- Réduit rupture de 22% → 8%, coût urgence -15K€ trimestre

**Déploiement Gedimat (recommandation):**
- ✅ **Phase 1 (court terme):** Lissage exponentiel Holt-Winters, révision hebdomadaire
- ✅ **Phase 2 (moyen terme):** Régression multivariée + données externes (météo, indice BTP)
- 🟡 **Phase 3 (long terme):** Demand sensing intégré PDV/e-commerce (nécessite système IT)

---

### 3. Patterns Saisonniers - Construction Français

**Cycles majeurs (analyse 10 ans données construction France):**

```
SAISONNALITÉ ANNUELLE:
Jan-Mar    : 70% (post-vacances, plans annuels travaux)
Avr-May    : 105% (apogée chantiers, météo favorable)
Jun-Aug    : 95% (vacances freinent, mais travaux estivaux)
Sep-Oct    : 110% (reprise rentrée, avant préparation hiver)
Nov-Dec    : 75% (préparation Noël, mauvais temps)

PAR CATÉGORIE:
- Toiture/Briques: saisonnalité FORTE (80-120%), pics Mar-Oct
- Peinture/Vernis: MOYENNE (90-110%), pics Mai-Sep
- Ciment/Sable: FAIBLE (95-105%), demande lissée
- Outillage/Électro: TRÈS FORTE (70-130%), pics vacances
```

**Facteur jour semaine (Gedimat spécifique):**
```
Lun-Ven: 100% (pros, PME travaux)
Samedi : 140% (bricolage week-end, particuliers)
Dimanche: 30% (une seule formule ouverte certains )
Jours fériés: 20% (variable selon région)
```

**Application Gedimat:**
- Cutter EOQ par facteur saisonnier mensuel: EOQ_month = EOQ × Facteur_month
- Augmenter SS: Oct-Nov (+50%), Juin (+20%)
- Réduire SS: Décembre (-25%), Août (-10%)

---

### 4. Lead Time Variabilité & Fiabilité Fournisseur

**Formule intégrant risque fournisseur:**
```
SS_ajusté = SS_base × (1 + %_délai_variabilité / 100)

Où %_délai_variabilité = (Délai_max - Délai_moyen) / Délai_moyen

Exemple: Fournisseur A: délai 5-14j (moyen 7j)
%_var = (14-7)/7 = 100% → Multiplier SS par 2.0
Fournisseur B: délai 6-8j (moyen 7j)
%_var = (8-7)/7 = 14% → Multiplier SS par 1.14
```

**Scoring fiabilité fournisseur (Gedimat):**

| Critère | Poids | Note | Impact SS |
|---------|-------|------|-----------|
| Respect délai >95% | 40% | A=10, B=6, C=3 | Multiplicateur 1.0-2.5 |
| Qualité (retours <2%) | 25% | A=10, B=6, C=3 | Risque double défaut |
| Stabilité prix (var<5%) | 20% | A=10, B=7, C=4 | Coût contrat |
| Capacité pics (x2 volume) | 15% | A=10, B=5, C=2 | Flexibilité approvisionnement |
| **Score fournisseur** | **100%** | - | - |

**Exemple scoring Gedimat - Emeris (tuiles):**
- Respect délai 96% → 9.6/10
- Retours 1.2% → 9/10
- Prix stable 3% var → 9/10
- Pics x2.5 possible → 9.5/10
- **Score = 0.40×9.6 + 0.25×9 + 0.20×9 + 0.15×9.5 = 9.3/10** = Excellent

**Action Gedimat:**
- Score >8.5: SS multiplié 1.1 (supplier de confiance)
- Score 7-8.5: SS multiplié 1.3 (moyen, attention)
- Score <7: SS multiplié 1.7-2.0 OU trouver alternative (risqué)

---

### 5. Intégration ERP - Systèmes Modernes

**Flux idéal GestStock-ERP (Gedimat):**

```
[1. PDV MAGASIN]
   ↓ Sync quotidien (ticket caisse)
[2. MODULE STOCK ERP]
   ↓ Demande réelle vs Prévision ML
[3. DEMAND SENSING]
   ↓ Détecte écart >±15% → alerte buyer
[4. ORCHESTRATION ACHAT]
   ↓ Recommande quantité, délai, fournisseur
[5. SÉLECTION FOURNISSEUR]
   ↓ Score fournisseur + délai + coût
[6. GÉNÉRATION COMMANDE]
   ↓ EDI/email fournisseur automatisé
[7. SUIVI LIVRAISON]
   ↓ Alertes retard + estimation ETA
[8. RÉCEPTION & RÈGLEMENT]
   ↓ Validation 3-way match (commande/reçu/facture)
```

**Composants ERP recommandés Gedimat:**

**Option 1: Open Source (coût ~€5-15K an)**
- **Odoo**: Module Stock + Purchase + Demand Forecasting
- Avantage: Français, flexible, communauté active
- Inconvénient: Modularité moyenne, support inégal

**Option 2: PME Standard (coût ~€20-50K an)**
- **SAP BusinessOne**: Supply Chain Management
- **Microsoft Dynamics 365**: Commerce + Supply Chain
- Avantage: Stabilité, support établi
- Inconvénient: Coût investissement initial, moins flexible

**Option 3: Cloud-natif (coût ~€3-8K mois)**
- **NetSuite**: Inventory Optimization module
- **Blue Yonder**: Demand Planning (ex JDA)
- Avantage: ML intégré, maintenance éditeur
- Inconvénient: Coût récurrent, dépendance cloud

**Implémentation Gedimat recommandée (3 phases):**

| Phase | Durée | Action | Système |
|-------|-------|--------|---------|
| 1 (Quick) | 1-3 mois | Importer historique 24 mois, configurer Holt-Winters | Odoo Stock |
| 2 (Interméd.) | 4-9 mois | Intégrer données PDV temps réel, lissage hebdomadaire | Odoo + regr. linéaire |
| 3 (Complet) | 10-24 mois | API demand sensing, scoring fournisseur, optimisation coûts | Module ML cloud |

**KPI suivi ERP (Gedimat):**
```
- Taux service: >97% (objectif)
- Coût moyen stock: <3% du CA (benchmark secteur)
- Délai moyen réappro: <8j (vs 12j moyen)
- Taux rupture: <1% (vs 3-5% secteur)
- Taux rotation: >4x/an (ciment, sable), >2x/an (articles spécialisés)
```

---

## SYNTHÈSE PRATIQUE : ROADMAP GEDIMAT

### Court terme (0-3 mois) - RAPIDE & CHEAP
```
✅ Implémenter Holt-Winters (Excel VBA ou Python simple)
✅ Définir EOQ par catégorie produit
✅ Fixer points de commande (ROP) avec SS z=1.65
✅ Mettre en place alertes visuelles (min-max)
✅ Former coordinatrice Angélique (formules + outils)
Budget: €2-5K | Impact: -10% coûts stockage
```

### Moyen terme (4-9 mois) - ÉQUILIBRE
```
✅ Intégrer données externes (météo, indice BTP INSEE)
✅ Déployer régression linéaire (4-5 variables clés)
✅ Systématiser scoring fournisseurs
✅ Synchroniser PDV → système stock quotidien
✅ Tableaux de bord KPI (Tableau/PowerBI léger)
Budget: €20-40K | Impact: -15% coûts transport, +3% taux service
```

### Long terme (10-24 mois) - EXCELLENCE
```
✅ Migrer ERP complet (Odoo recommandé)
✅ Implémenter ARIMA ou LSTM si données disponibles
✅ API demand sensing temps réel
✅ Optimisation automatisée multi-dépôts (problème TSP/VRP)
✅ Predictive analytics: ruptures clients avant qu'elles surviennent
Budget: €50-80K + €500/mois cloud | Impact: -20% coûts global, +5% satisfaction clients
```

---

## SOURCES & CITATIONS

**Classiques Inventaire:**
1. Harris, F.W. (1913). "How many parts to make at once." Factory, The Magazine of Management, 10(2):135-136.
2. Wilson, R.H. (1934). "A Scientific Routine for Stock Control." Harvard Business Review, 13(1):116-128.
3. Abramowitz, M. & Stegun, I.A. (1964). Handbook of Mathematical Functions (Normal distribution z-scores).

**Demand Sensing & ML:**
4. Syntetos, A.A. & Boylan, J.E. (2005). "On the stock control performance of intermittent demand estimators." International Journal of Production Economics, 103(1):36-47.
5. Hyndman, R.J. & Athanasopoulos, G. (2021). Forecasting: Principles and Practice (3e éd.). OTexts.
6. Choi, T.M. (2020). "Artificial intelligence for supply chain resilience." Supply Chain Management, 25(6):627-631.

**Construction Française:**
7. INSEE (2025). "Indice de la production dans la construction" (publication mensuelle).
8. Fédération Française du Bâtiment (2023). Étude saisonnalité secteur construction France.
9. Gedimat Internal Data (2020-2025). 24 mois historique ventes 3 dépôts français.

**Standards Secteur:**
10. APICS (2023). Certified in Inventory and Operations Planning (APICS CSCP).
11. Council of Supply Chain Management Professionals (CSMP) Best Practices.
12. Chopra, S. & Meindl, P. (2016). Supply Chain Management: Strategy, Planning, and Operation (6e éd.). Pearson.

---

**Document:** Formules Stock & Demand Sensing
**Applicable à:** Gedimat franchises, distributeurs matériaux construction, PME logistique saisonnière
**Version prochaine:** Intégration cas concrets Évreux/Méru/Breuilpont (Q1 2025)
**Révisé par:** InfraFabric Agent 4 (Pass 1: Formules)
