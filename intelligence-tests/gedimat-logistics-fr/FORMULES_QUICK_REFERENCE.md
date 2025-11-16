# Formules Stock & Demand Sensing - Feuille Rapide
## Quick Reference & Outils Pratiques Gedimat

**Version:** 1.0 | **Date:** 16 novembre 2025
**Usage:** Impression A3, affichage bureau coordination Gedimat

---

## 🔷 LES 5 FORMULES ESSENTIELLES

### 1️⃣ EOQ (Quantité Économique de Commande)

```
EOQ = √(2 × D × S / H)

ÉTAPES:
1. D = Demande annuelle (consulter ventes Y-1)
2. S = Coût lancement (demander finance: ~€40-60)
3. H = Coût détention annuel:
   P = coût unitaire
   H = P × (12% intérêt + 6% stockage + 0.8% assurance + 2% obsolescence)
4. Calculer racine carrée résultat

EXEMPLE RAPIDE (Ciment 25kg):
D=50,000 sacs/an | S=40€ | P=3.50€ | H=3.5×0.208=0.73€
EOQ = √(2×50,000×40/0.73) = √5,479,452 = 2,341 sacs

UTILISER POUR: Commandes planifiées, pas urgences
```

---

### 2️⃣ Stock de Sécurité (Safety Stock)

```
SS = z × σ_L × √LT

ÉTAPES:
1. z = Facteur de service (choix):
   z=1.28 → 90% service (rarement)
   z=1.65 → 95% service (standard Gedimat)
   z=1.96 → 97.5% service (articles critiques)
   z=2.33 → 99% service (rupture très coûteuse)

2. σ_L = Écart-type demande journalière
   (Excel: =STDEV sur 30 derniers jours)

3. LT = Délai approvisionnement (jours)

EXEMPLE RAPIDE (Tuiles Emeris):
z=1.65 (95%) | σ=15 tuiles/jour | LT=7 jours
SS = 1.65 × 15 × √7 = 65 palettes

TABLEAU RAPIDE (z=1.65):
LT=3j : SS = 1.65 × σ × 1.73
LT=7j : SS = 1.65 × σ × 2.65
LT=14j: SS = 1.65 × σ × 3.74
LT=30j: SS = 1.65 × σ × 5.48
```

---

### 3️⃣ Point de Commande (Reorder Point)

```
ROP = (D × LT) + SS

ÉTAPES:
1. D = Demande moyenne/jour (consulter moyenne 30j)
2. LT = Délai fournisseur (jours)
3. SS = Voir formule 2️⃣

EXEMPLE:
D=200 briques/jour | LT=4j | SS=800
ROP = (200 × 4) + 800 = 1,600 briques

⚠️ COMMANDER DÈS QUE STOCK ATTEINT ROP

SYSTÈME ALERTE:
🟢 VERT:   Stock > ROP → Normal
🟡 ORANGE: ROP-200 < Stock < ROP → Alerte
🔴 ROUGE:  Stock < ROP-200 → Urgence/Rupture
```

---

### 4️⃣ Stock Min-Max

```
S_min = ROP
S_max = ROP + EOQ

OU (pour révision périodique/7j):
S_max = (D × (LT + P)) + SS
        P = période révision (7j)

EXEMPLE (Sable bac):
ROP = 5,000 m³ | EOQ = 3,000 m³
→ S_min = 5,000 | S_max = 8,000

PROCÉDURE:
Chaque LUNDI: Si stock < 5,000 m³
           → Commander pour atteindre 8,000 m³
```

---

### 5️⃣ Coût de Détention (Holding Cost)

```
H = P × (i + w + s + o)
où i=12%, w=6%, s=0.8%, o=2%
H_total = P × 0.208 ≈ P × 21%

TABLEAU RAPIDE (coût annuel par unité):
P=€5   → H≈€1.04/an  → EOQ réduction 20%
P=€10  → H≈€2.08/an  → EOQ réduction 14%
P=€20  → H≈€4.16/an  → EOQ réduction 10%
P=€50  → H≈€10.4/an  → EOQ réduction 6%

📌 Articles chers (P>€30) → plus petites commandes
📌 Articles bons marché (P<€10) → commandes groupées
```

---

## 🔷 DEMAND SENSING - 4 APPROCHES CLASSÉES

| Approche | Formule | Données | Délai | Coût | Gedimat |
|----------|---------|---------|-------|------|---------|
| **Holt-Winters** | F=α×D+(1-α)×F | 8 semaines | 1 semaine | €0-5K | ✅ IMMÉDIAT |
| **Régression** | D=β₀+β₁×jour+β₂×saison+... | 6 mois | 2 semaines | €10-20K | ✅ Q1 2025 |
| **ARIMA** | p,d,q lags | 24 mois | 4 semaines | €30-50K | 🟡 2025 |
| **LSTM/IA** | Neural networks | 24+ mois | Continu | €100K+ | ❌ Trop cher |

---

## 🔷 FACTEURS SAISONNIERS CONSTRUCTION FRANCE

### Par Mois (Gedimat)
```
Jan: 70%    Avr: 105%   Juil: 95%    Oct: 110%
Fév: 75%    Mai: 110%   Aoû: 90%    Nov: 75%
Mar: 85%    Juin: 100%  Sep: 105%   Déc: 65%

UTILISER: EOQ_mois = EOQ_base × Facteur_mois

Exemple (Tuiles):
EOQ_base = 200 palettes
EOQ_avril = 200 × 1.05 = 210 palettes ✅
EOQ_décembre = 200 × 0.65 = 130 palettes ✅
```

### Par Jour Semaine
```
Lun-Ven: 100% (pros)
Samedi: 140% (bricolage)
Dimanche: 30% (fermé plupart)
Jours fériés: 20%

AUGMENTER SS samedi +40%
RÉDUIRE SS dimanche -60%
```

---

## 🔷 SCORING FIABILITÉ FOURNISSEUR

### Grille Notation (0-10)
```
┌─────────────────────────────────┬──────┬────────┐
│ Critère                         │ Note │ Poids  │
├─────────────────────────────────┼──────┼────────┤
│ Respect délai % / (% souhaité)  │ /10  │ 40%    │
│ Qualité: retours <% / (tol 2%)  │ /10  │ 25%    │
│ Prix stable: var% / (tol 5%)    │ /10  │ 20%    │
│ Flexibilité pics (x? volume)    │ /10  │ 15%    │
├─────────────────────────────────┼──────┼────────┤
│ SCORE FINAL                     │ /10  │ 100%   │
└─────────────────────────────────┴──────┴────────┘

INTERPRÉTATION:
9-10  : Excellent (SS ×1.1)
7-8   : Acceptable (SS ×1.3)
5-6   : Faible (SS ×1.7)
<5    : Chercher alternative
```

---

## 🔷 TABLEAU LEADS VARIABILITÉ FOURNISSEUR

```
Formule: SS_ajusté = SS_base × (1 + Variabilité%)

EXEMPLES:
Fournisseur fiable (5-7j): var=25% → SS ×1.25
Fournisseur moyen (5-12j): var=75% → SS ×1.75
Fournisseur risqué (5-20j): var=150% → SS ×2.50

EXEMPLE CONCRET (Emeris tuiles):
- Délai moyen: 7 jours
- Plage: 5-9 jours (variabilité 28%)
- SS base: 100 palettes
- SS ajusté = 100 × 1.28 = 128 palettes
```

---

## ✅ CHECKLIST IMPLÉMENTATION GEDIMAT

### PHASE 1 (1-3 MOIS) - RAPIDE

- [ ] **Semaine 1-2: Collecte données**
  - [ ] Extraire 24 mois ventes par SKU (Excel)
  - [ ] Calculer D (demande annuelle/jour)
  - [ ] Mesurer délai moyen fournisseur par article
  - [ ] Estimer P (coût unitaire) × catégorie

- [ ] **Semaine 3-4: EOQ par SKU**
  - [ ] Lister top 20 articles par CA (80/20)
  - [ ] Calculer S (coût lancement) avec finance
  - [ ] Calculer H (coût détention) = P × 0.208
  - [ ] Calculer EOQ pour top 20
  - [ ] Documenter résultat Excel

- [ ] **Semaine 5-6: Safety Stock & ROP**
  - [ ] Calculer σ (écart-type 30 derniers jours) par article
  - [ ] Fixer z=1.65 pour la plupart (95% service)
  - [ ] Calculer SS = z × σ × √LT
  - [ ] Calculer ROP = (D × LT) + SS
  - [ ] Mettre en place alertes visuelles (vert/orange/rouge)

- [ ] **Semaine 7-8: Min-Max & Tests**
  - [ ] Définir S_min = ROP, S_max = ROP + EOQ
  - [ ] Tester 2 semaines avec coordinatrice Angélique
  - [ ] Ajuster z si trop/trop peu ruptures
  - [ ] Afficher formules bureau (poster A3)

- [ ] **Semaine 9: Formation & Go**
  - [ ] Former Angélique (usage formules + alerte)
  - [ ] Documents: Mode opératoire (1 page)
  - [ ] Lancer en production sur top 20 articles
  - [ ] Suivre KPI semaine 1 (ruptures, surstock)

### PHASE 2 (4-9 MOIS) - MOYEN TERME

- [ ] **Données externes**
  - [ ] API météo France (temperature)
  - [ ] INSEE indice BTP (tendance économique)
  - [ ] Calendrier événements (vacances, fêtes)
  - [ ] Google Trends construction/bricolage

- [ ] **Modèle Holt-Winters avancé**
  - [ ] Implémenter en Python ou Excel VBA
  - [ ] Intégrer facteurs saisonniers mensuels
  - [ ] Réviser prévisions chaque lundi (hebdo)
  - [ ] Comparer vs reality 4 semaines

- [ ] **Scoring fournisseurs systématique**
  - [ ] Grille notation pour tous fournisseurs principaux
  - [ ] Réunion mensuelle achat/coordination
  - [ ] Ajuster SS selon score fournisseur
  - [ ] Documenter Actions (<7 fournisseurs: audits)

- [ ] **Dashboard KPI (Tableau/Excel)**
  - [ ] Taux service (cible 97%)
  - [ ] Coût moyen stock (cible <3% CA)
  - [ ] Taux rupture (cible <1%)
  - [ ] Délai moyen approvisionnement (cible <8j)

### PHASE 3 (10-24 MOIS) - EXCELLENCE

- [ ] **Migration ERP (Odoo recommandé)**
  - [ ] Module Stock + Purchase + MRP
  - [ ] Sync PDV temps réel
  - [ ] EDI fournisseurs automatisé
  - [ ] Budget: €50-80K + formation

- [ ] **Demand Sensing temps réel**
  - [ ] API PDV → ERP (quotidien)
  - [ ] Détection écarts forecasting (>15%)
  - [ ] Alertes acheteur automatisées
  - [ ] Dashboard prévision/réel

- [ ] **Optimisation multi-site**
  - [ ] Algo VRP/TSP (distribution 3 dépôts)
  - [ ] Consolidation commandes cross-dock
  - [ ] Navettes inter-dépôts optimales
  - [ ] Coûts transport -20%

- [ ] **Predictive analytics**
  - [ ] ARIMA ou LSTM si données 24+ mois
  - [ ] Prédire ruptures avant qu'elles surviennent
  - [ ] Planifier capacité fournisseur
  - [ ] Satisfactions clients +5%

---

## 📊 KPI SUIVI (GEDIMAT)

### Chaque SEMAINE:
```
☐ Taux Service = Nb articles en stock / Nb articles
  Cible: >97% | Seuil alerte: <95%

☐ Taux Rupture = Nb ruptures / Nb demandes
  Cible: <1% | Seuil alerte: >2%

☐ Délai Approvisionnement Moyen
  Cible: <8j | Seuil alerte: >10j
```

### Chaque MOIS:
```
☐ Coût Stock Moyen = Valeur stock / (CA/12)
  Cible: <3% CA | Benchmark: 3-5%

☐ Taux Rotation = CA/12 / Valeur stock moyenne
  Cible: >4x/an | Benchmark: 2-4x

☐ Stock Excédentaire = Nb articles <30j vente
  Cible: <5% SKU | Seuil alerte: >10%

☐ Supplier Performance Score
  Cible: >8/10 | Actions: <6/10
```

---

## 🛠️ OUTILS RECOMMANDÉS

### Excel Natif (Gratuit):
```
- STDEV() = Écart-type (pour σ)
- SQRT() = Racine carrée (pour √LT)
- IF() = Conditions min-max
- VLOOKUP() = Facteurs saisonniers
Fichier template: STOCK_EOQ_TEMPLATE.xlsx
```

### Python Simple (Gratuit):
```python
# Holt-Winters lissage exponentiel
from statsmodels.tsa.holtwinters import ExponentialSmoothing
model = ExponentialSmoothing(data, trend='add', seasonal='add', seasonal_periods=52)
forecast = model.fit().fittedvalues
```

### Cloud (Payant):
```
- Odoo Stock Module (€3-8K/an)
- Tableau Online (€70/user/mois)
- Google Sheets + Apps Script (gratuit)
```

---

## 📚 GLOSSAIRE RAPIDE

| Terme | Définition | Exemple |
|-------|-----------|---------|
| **EOQ** | Quantité optimale commande | 250 palettes |
| **ROP** | Niveau alerte commande | 1,500 briques |
| **SS** | Stock réserve rupture | 300 unités |
| **LT** | Délai fournisseur | 7 jours |
| **D** | Demande/période | 200/jour |
| **H** | Coût détention/an | €0.73/sac |
| **S** | Coût lancement commande | €50 |
| **σ** | Écart-type demande | ±25 units |
| **z** | Facteur service | 1.65=95% |

---

## ☎️ SUPPORT GEDIMAT

**Questions formules?**
- Angélique (Coordinatrice): coordination@gedimat.fr
- Directeur: direction@gedimat.fr

**Problème données?**
- Finance: extraction@gedimat.fr
- IT/ERP: support@gedimat.fr

**Feedback implémentation?**
- Slack #logistics-optimization
- Réunion mensuelle (1er jeudi)

---

**Document:** Formules Stock & Demand Sensing - Quick Reference
**Mise à jour:** 16 novembre 2025
**À imprimer:** Format A3 affichage bureau coordination
**Révision:** Tous les trimestres avec KPI réels
