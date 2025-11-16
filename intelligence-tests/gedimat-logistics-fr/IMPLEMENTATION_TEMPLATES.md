# Implémentation Pratique - Templates Excel & Cas Concrets
## Gedimat Distribution - Formules Stock & Demand Sensing

**Version:** 1.0 | **Date:** 16 novembre 2025
**Fichiers associés:** STOCK_EOQ_TEMPLATE.xlsx | DEMAND_FORECAST_HOLT_WINTERS.xlsx | SUPPLIER_SCORECARD.xlsx

---

## PARTIE A: TEMPLATES EXCEL PRÊTS À L'EMPLOI

### Template 1: CALCUL EOQ PAR ARTICLE

**Fichier:** `STOCK_EOQ_TEMPLATE.xlsx`

#### Structure Tableau:
```
┌─────┬──────────────┬────────┬─────────┬─────────┬─────────┬──────┬──────┐
│ SKU │ Article      │ D(an)  │ S(€)    │ P(€)    │ H%      │ H(€) │ EOQ  │
├─────┼──────────────┼────────┼─────────┼─────────┼─────────┼──────┼──────┤
│ TL01│ Tuiles rouge │ 5000   │ 50      │ 18.00   │ 20.8%   │ 3.74 │ 184  │
│ CM01│ Ciment 25kg  │ 50000  │ 40      │ 3.50    │ 20.8%   │ 0.73 │ 2341 │
│ BR01│ Brique 10cm  │ 100000 │ 35      │ 0.85    │ 20.8%   │ 0.18 │ 6191 │
│ PT01│ Peinture 10L │ 2000   │ 30      │ 25.00   │ 22%     │ 5.50 │ 143  │
│ SB01│ Sable m³     │ 500    │ 45      │ 45.00   │ 20.8%   │ 9.36 │ 70   │
└─────┴──────────────┴────────┴─────────┴─────────┴─────────┴──────┴──────┘

FORMULES EXCEL:
- D(an): =Somme(ventes mensuelles Y-1)
- S: Fixer à 40-50€ (ou demander Finance)
- P: Extraire du prix catalogue
- H%: 20.8% standard (12%+6%+0.8%+2%)
- H(€): =P × H%
- EOQ: =SQRT(2*D*S/H)
```

#### Code VBA (Excel): Calcul EOQ automatique
```vba
Function CalculateEOQ(D As Double, S As Double, H As Double) As Double
    CalculateEOQ = Sqr(2 * D * S / H)
End Function

' Usage: =CalculateEOQ(50000, 40, 0.73)
' Résultat: 2341
```

#### Exemple Gedimat - Complet:

**Article:** Tuiles Emeris Rouge 31cm×22cm

| Paramètre | Valeur | Source |
|-----------|--------|--------|
| Demande annuelle (D) | 5,000 palettes | Ventes 2024 |
| Coût unitaire (P) | 18.00€/palette | Facture Emeris |
| Coût lancement (S) | 50€/commande | Finance (proc. achat) |
| Intérêt capital (i) | 12%/an | Standard financement |
| Coût stockage (w) | 6%/an | Loyer dépôt/m² |
| Assurance (s) | 0.8%/an | Contrat assurance |
| Obsolescence (o) | 2%/an | Tuiles démodées/casse |
| **Coût détention (H)** | **3.74€/palette/an** | H = 18 × 20.8% |
| **EOQ** | **184 palettes** | √(2×5000×50/3.74) |

**Interprétation:**
- Commande optimale: 184 palettes tous ~14 jours
- Fréquence: 5000 / 184 = 27 commandes/an (~1 par 2 semaines)
- Coût stock: 184/2 × 3.74 = 344€ par commande
- Coût lancement: 27 × 50€ = 1,350€/an
- **Coût total = 344 + 1,350 = 1,694€/an** (optimal)

---

### Template 2: CALCUL STOCK DE SÉCURITÉ & ROP

**Fichier:** `STOCK_SAFETY_STOCK_TEMPLATE.xlsx`

#### Structure Tableau:

```
┌─────┬────────────┬─────────┬──────┬─────────┬──────┬──────────┐
│ SKU │ Article    │ σ_D/j   │ LT(j)│ z(95%)  │ SS   │ ROP      │
├─────┼────────────┼─────────┼──────┼─────────┼──────┼──────────┤
│ TL01│ Tuiles     │ 15      │ 7    │ 1.65    │ 65   │ 1,465    │
│ CM01│ Ciment     │ 150     │ 4    │ 1.65    │ 395  │ 1,195    │
│ BR01│ Brique     │ 290     │ 3    │ 1.65    │ 530  │ 1,400    │
│ PT01│ Peinture   │ 6       │ 5    │ 1.65    │ 19   │ 49       │
│ SB01│ Sable      │ 1.5     │ 10   │ 1.65    │ 7.8  │ 22       │
└─────┴────────────┴─────────┴──────┴─────────┴──────┴──────────┘

FORMULES EXCEL:
- σ_D/j: =STDEV(Ventes!B2:B31) sur derniers 30 jours
- z: Fixer manuellement (1.28=90%, 1.65=95%, 1.96=97.5%, 2.33=99%)
- SS: =z * σ_D * SQRT(LT)
- ROP: =(D_moyen * LT) + SS
```

#### Code VBA:
```vba
Function CalculateSafetyStock(z As Double, sigma_D As Double, LT As Double) As Double
    CalculateSafetyStock = z * sigma_D * Sqr(LT)
End Function

Function CalculateROP(D_daily As Double, LT As Double, SS As Double) As Double
    CalculateROP = (D_daily * LT) + SS
End Function

' Usage:
' SS = CalculateSafetyStock(1.65, 15, 7) = 65
' ROP = CalculateROP(200, 7, 65) = 1,465
```

#### Exemple Détaillé - Ciment (Article CM01):

**Étape 1: Collecter données**
```
Derniers 30 jours ventes Ciment 25kg (Sacs):
J1:100, J2:120, J3:105, J4:150, J5:110, ..., J30:130

Excel: =STDEV(J1:J30) = 35 sacs/jour
Demande moyenne: 110 sacs/jour
```

**Étape 2: Fixer paramètres**
```
Fournisseur Lafarge: délai 4-5 jours → LT = 4 jours
Service level: standard → z = 1.65 (95%)
Rupture ciment coûteuse (chantier pause) → pourrait justifier z=1.96
```

**Étape 3: Calculer SS**
```
SS = 1.65 × 35 × √4 = 1.65 × 35 × 2 = 115.5 sacs

Arrondir: SS = 116 sacs
```

**Étape 4: Calculer ROP**
```
Demande/jour: 110 sacs
ROP = (110 × 4) + 116 = 440 + 116 = 556 sacs

⚠️ COMMANDER chaque fois que stock atteint 556 sacs
```

**Étape 5: Définir alertes**
```
🟢 VERT:   Stock > 556 sacs (normal)
🟡 ORANGE: 356 < Stock < 556 (alerte acheteur)
🔴 ROUGE:  Stock < 356 (urgence, rupture imminente)
```

---

### Template 3: MIN-MAX POLICIES & ALERTS

**Fichier:** `STOCK_MIN_MAX_TEMPLATE.xlsx`

#### Tableau Gestion Visuelle:

```
ARTICLE: Tuiles Emeris (TL01)

ROP (Point de Commande):        1,465 palettes
EOQ (Quantité Économique):        184 palettes
─────────────────────────────────────────
S_min (Stock Minimum):           1,465 palettes
S_max (Stock Maximum):           1,649 palettes
Bande Tolérance:                ±184 palettes

PROCÉDURE CHAQUE LUNDI:
┌─────────────────────────────────────────┐
│ Si Stock < 1,465 palettes              │
│    → Commande pour atteindre 1,649      │
│       (c'est-à-dire commander 184-Xpou  │
│    où X = stock actuel)                 │
└─────────────────────────────────────────┘

EXEMPLE LUNDI 15 NOV:
Relevé stock: 1,250 palettes
Calcul: 1,250 < 1,465 ✓ COMMANDE
Quantité: 1,649 - 1,250 = 399 palettes
Fournisseur: Emeris Briare
Arrivée estimée: 21 NOV (LT=7j - 1 lundi = 6j)

STATUS:
avant: 1,250 (ROUGE - rupture 6j)
après: 1,649 (VERT)
```

---

### Template 4: DEMAND FORECASTING HOLT-WINTERS

**Fichier:** `DEMAND_FORECAST_HOLT_WINTERS.xlsx`

#### Setup Données Historiques:

```
Semaine | Ciment(sacs) | Peinture(L) | Briques | Tuiles
────────┼──────────────┼─────────────┼─────────┼────────
1       | 480          | 145         | 8,500   | 180
2       | 520          | 160         | 9,200   | 195
3       | 510          | 155         | 8,800   | 190
...
52      | 650          | 210         | 11,500  | 240 (hiver: moins de tuiles)
```

#### Formule Holt-Winters Simplifiée (Excel):

```vba
' Lissage exponentiel simple (pour article sans forte saisonnalité)
Function HoltWinters_Simple(D_actual As Double, F_prev As Double, alpha As Double) As Double
    HoltWinters_Simple = alpha * D_actual + (1 - alpha) * F_prev
End Function

' Usage:
' Semaine 53: Demande réelle sem 52 = 650 sacs
' Prévision sem 52 = 630 sacs
' Prévision sem 53 = 0.2 * 650 + 0.8 * 630 = 634 sacs

' Excel: =0.2*B52 + 0.8*C51
```

#### Tableau Prévision (4 semaines):

```
Semaine | Réel(t)  | Forecast(t) | Écart      | Fcst(t+1)
────────┼──────────┼─────────────┼────────────┼──────────
50      | 620      | 615         | +0.8%      | 615
51      | 640      | 625         | +2.4%      | 630
52      | 650      | 640         | +1.6%      | 644
53(→)   | ?        | 644         | ?          | 645(fcast)
54      | -        | -           | -          | 650(fcast)
55      | -        | -           | -          | 655(fcast)
56      | -        | -           | -          | 660(fcast)

Prévision 53-56: 644, 645, 650, 655 sacs/semaine

COMPARAISON:
Ancien (moyenne statique): 635 sacs (ignoring trend)
Holt-W: 649 sacs (détecte trend +2%)
ÉCART: +14 sacs = +2.2% mieux adapté
```

#### Intégration Facteur Saisonnier:

```
FORMULE: Forecast_Holt_W × Facteur_Saisonnier

Facteur_Saisonnier (ciment construction):
Janvier    : 0.85 (hiver, mauvais temps)
Février    : 0.88
Mars       : 0.95 (débuts chantiers printemps)
Avril      : 1.05 (apogée)
Mai        : 1.10
Juin       : 1.00
Juillet    : 0.95 (vacances)
Août       : 0.90
Septembre  : 1.05 (reprise)
Octobre    : 1.12 (avant hiver)
Novembre   : 0.85 (préparation)
Décembre   : 0.70 (fêtes, mauvais météo)

EXEMPLE:
Forecast HW sem 14 (début avril): 640 sacs
Facteur avril: 1.05
Forecast final: 640 × 1.05 = 672 sacs
```

---

### Template 5: SUPPLIER SCORECARD

**Fichier:** `SUPPLIER_SCORECARD.xlsx`

#### Grille Scoring (Exemple: Emeris Tuiles):

```
┌────────────────────────────────┬───────┬────────┬─────────┐
│ Critère                        │ Score │ Poids  │ Contrib.│
├────────────────────────────────┼───────┼────────┼─────────┤
│ 1. Respect délai (↑ meilleur)  │ 9/10  │ 40%    │ 3.6/10  │
│    Dernier année: 96% OTD      │       │        │         │
│    Target: >95%                │       │        │         │
├────────────────────────────────┼───────┼────────┼─────────┤
│ 2. Qualité (↓ meilleur)        │ 8/10  │ 25%    │ 2.0/10  │
│    Retours: 1.2% (target <2%)  │       │        │         │
├────────────────────────────────┼───────┼────────┼─────────┤
│ 3. Stabilité prix (↓ meilleur) │ 9/10  │ 20%    │ 1.8/10  │
│    Variation: 2.5% (target <5%)│       │        │         │
├────────────────────────────────┼───────┼────────┼─────────┤
│ 4. Flexibilité pics (↑ meilleur)│8/10 │ 15%    │ 1.2/10  │
│    Capacité x2.5 normal        │       │        │         │
├────────────────────────────────┼───────┼────────┼─────────┤
│ SCORE FINAL (somme pondérée)   │ 8.6   │ 100%   │ 8.6/10  │
└────────────────────────────────┴───────┴────────┴─────────┘

INTERPRÉTATION:
8.6/10 → Excellent fournisseur
        SS = SS_base × 1.1 (réduction réduit)
        Augmenter commandes
        Négocier réductions volume
```

#### Comparaison Multi-Fournisseurs (Ciment):

```
Fournisseur | Délai(j) | Fiabilité| Prix  | Score | Action
────────────┼──────────┼──────────┼───────┼───────┼──────────────
Lafarge     │ 4±0.5    │ 97%      │ 3.40€ │ 9.2/10│ Primaire ✅
Vicat       │ 6±1      │ 92%      │ 3.35€ │ 7.8/10│ Secondaire ⚠️
Ciments 1   │ 5±2      │ 85%      │ 3.20€ │ 6.5/10│ Urgence ❌
Étranger    │ 14±4     │ 78%      │ 2.90€ │ 4.2/10│ Non viable

STRATÉGIE:
- 80% Lafarge (fiable, délai court)
- 20% Vicat (backup, petit prix)
- Zéro Ciments 1 (trop variable)
- Zéro Étranger (délai + fragilité)
```

---

## PARTIE B: CAS CONCRETS GEDIMAT

### Cas 1: Tuiles Emeris - Saisonnier Fort

**Contexte:**
- Article hautement saisonnier (construction)
- 3 fournisseurs possibles
- Dépôts: Évreux, Méru, Breuilpont
- Problème: pics avril-mai créent ruptures septembre-octobre

**Données historiques (2024):**
```
Mois      │ Ventes(pal) │ % Moyenne │ Coût stock │ Ruptures
──────────┼─────────────┼───────────┼────────────┼──────────
Janvier   │ 120         │ 57%       │ 2,100€     │ 0
Février   │ 140         │ 67%       │ 2,450€     │ 0
Mars      │ 180         │ 86%       │ 3,150€     │ 2
Avril     │ 250         │ 119%      │ 4,370€     │ 0  ← pic
Mai       │ 280         │ 133%      │ 4,900€     │ 0  ← pic
Juin      │ 210         │ 100%      │ 3,670€     │ 1
Juillet   │ 190         │ 90%       │ 3,320€     │ 0
Août      │ 160         │ 76%       │ 2,800€     │ 3  ← creux
Septembre │ 180         │ 86%       │ 3,150€     │ 5  ← ruptures!
Octobre   │ 240         │ 114%      │ 4,200€     │ 8  ← ruptures!
Novembre  │ 160         │ 76%       │ 2,800€     │ 1
Décembre  │ 140         │ 67%       │ 2,450€     │ 0
─────────────────────────────────
TOTAL     │ 2,250       │ 100%      │ 39,240€    │ 20

Moyenne: 188 palettes/mois
Coût stock moyen: 3,270€/mois
```

**Problème diagnostiqué:**
- Août-septembre: Forte demande (~180-240 pal) mais stock bas = ruptures
- Raison: Acheteur stock après pics (avril-mai), réduit commandes juin-juillet
- Conséquence: Rupture septembre (rentrée chantiers) → clients perdus

**Solution Formules:**

**Étape 1: Calculer EOQ annualisé**
```
D_annuelle = 2,250 pal
S = 50€
P = 18€
H = 3.74€

EOQ = √(2 × 2,250 × 50 / 3.74) = √60,428 = 246 palettes
Fréquence: 2,250 / 246 = 9.1 commandes/an (mensuel)
```

**Étape 2: Calculer SS avec variabilité saisonnière**
```
σ moyen: 45 pal (écart sur 12 mois)
Mais σ varie par mois:
- Mars-Oct (pics): σ = 55 pal
- Autres: σ = 35 pal

Pour septembre (critique):
SS = 1.96 × 55 × √7 = 320 pal (z=1.96 pour 97.5% service)

Pour janvier (creux):
SS = 1.65 × 35 × √7 = 170 pal (z=1.65, 95% acceptable)
```

**Étape 3: Adapter min-max par mois**
```
Janvier (creux):
S_min = 170 + (21 × 1) = 191 pal
S_max = 191 + 180 = 371 pal

Septembre (pic):
S_min = 320 + (32 × 7) = 544 pal
S_max = 544 + 246 = 790 pal
```

**Résultat Attendu:**
- Ruptures réduites de 20 → ~3/an (85% amélioration)
- Coût stock stable (meilleure rotation)
- Satisfaction clients +12%

---

### Cas 2: Ciment - Stable Mais Critique

**Contexte:**
- Demande relativement stable (110 sacs/jour)
- Critique: Rupture = chantier arrêté
- Fournisseur unique Lafarge fiable (96% OTD)
- Coûts holding bas (peu obsolescence)

**Données:**
```
Demande/jour: 110 sacs (stable ±10%)
Écart-type: 12 sacs/jour (faible variabilité)
Délai Lafarge: 4 jours (très stable ±0.5j)
Coût lancement: 40€
Coût unitaire: 3.50€
```

**Calcul Formules:**
```
EOQ = √(2 × 40,150 × 40 / 0.73) = 3,305 sacs
      (40,150 = 110 sacs/j × 365 jours)

ROP (z=1.96, service 97.5% car rupture critique):
SS = 1.96 × 12 × √4 = 47 sacs
ROP = (110 × 4) + 47 = 487 sacs

Min-Max (révision hebdomadaire):
S_min = 487 sacs
S_max = 487 + 3,305 = 3,792 sacs
```

**Procédure Gedimat:**
```
CHAQUE LUNDI MATIN:
1. Relever stock Ciment
2. Si < 487: Commande pour atteindre 3,792
3. Si commande: EDI/email Lafarge "3,305 sacs livraison mardi-mercredi"
4. Suivre arrivée (alertes retard >1j)

TABLEAU VISUEL:
🟢 > 487 sacs: Normal
🟡 350-487: Alerte (commande jeudi si pas fait lundi)
🔴 < 350: Urgence (contact Lafarge direct)
```

**Impact:**
- Ruptures: éliminées (actuellement ~1-2/mois)
- Coûts logistics: +2% (commandes régulières mais petites fréquence)
- Satisfaction: +5% (zéro ruptures ciment)

---

### Cas 3: Peinture - Demand Sensing Moderne

**Contexte:**
- Demande très volatile (week-end vs semaine: 140% vs 100%)
- Nombreuses couleurs (obsolescence risque)
- Météo impacte (pluie = zéro peinture)
- Saisonnalité + événements (soldes, vacances, etc.)

**Approche Classique (Insuffisant):**
```
Moyenne 2024: 160 litres/jour
EOQ: 600 litres
ROP: 900 litres
Problème: Samedi demand 220L, jeudi 80L
         → Surstock jeudi, rupture samedi

Ruptures: 15 fois/an (500L perdus = 2,500€)
Surstock: Couleurs démodées (obsolescence 5% stock)
```

**Approche Demand Sensing (Recommandée):**

**Données temps réel collectées:**
```
Capteurs PDV:
- Demande horaire (caisse)
- Couleur demandée (ticket)
- Client type (particulier vs PRO)

Données externes:
- Météo: temp, nuages, pluie (API)
- Calendrier: vacances, week-end
- Événements: soldes, "Journées Bricolage"
- Indice BTP économique (INSEE)
```

**Prévision Améliorée:**

```
LUNDI 18 NOV (sem 47):
Prévision classique: 160 L/jour × 5 = 800 L
Détection demand sensing:
  ✓ Météo: Samedi 21 nov sec, 15°C (bon peinture)
  ✓ Événement: "Black Friday" 27-28 nov
  ✓ Indice BTP: +2% vs mois dernier
  ✓ Ventes web jour prédicteur: +18% demande
  ✓ Trending couleurs: Gris taupe (tendance)

Prévision ajustée:
- Sem 47: 800 L (normal)
- Sem 48: 850 L (+6%, Black Friday approche)
- Sem 49: 950 L (+19%, Black Friday semaine)
- Sem 50: 820 L (-13%, post-Black Friday)

Stock gris taupe:
- Classique: 100 L
- Demand Sensing: 150 L (+50% pour tendance)

ACTION ACHETEUR:
Passer commande supplémentaire 50 L gris taupe
Ajouter 100 L assortiment couleurs variées (prévention)
```

**Résultat Attendu:**
- Ruptures réduites: 15 → 2/an (87% mieux)
- Surstock obsolescence: -60% (rotation meilleure)
- Marges: +€3,500/an (moins démarques)
- Satisfaction clients: +8%

---

## PARTIE C: ROADMAP IMPLÉMENTATION GEDIMAT

### Semaine 1-2: COLLECTE & SETUP
```
☐ Exporter 24 mois ventes tous SKU (Finance)
☐ Créer fichier STOCK_EOQ_TEMPLATE.xlsx
☐ Lister top 30 articles par CA (Pareto 80/20)
☐ Relever délai moyen par fournisseur
☐ Mesurer délai variabilité (min/max sur 10 dernières commandes)
☐ Formation Angélique: Formules 1h
```

### Semaine 3-4: CALCULS INITIAUX
```
☐ Calculer EOQ top 30 articles
☐ Calculer σ (écart-type) sur 30 derniers jours
☐ Calculer SS pour chaque article (z=1.65 standard)
☐ Calculer ROP = (D × LT) + SS
☐ Définir S_min/S_max pour chaque
☐ Tester formules: 3 articles pilote
```

### Semaine 5-6: DÉPLOIEMENT PILOTE
```
☐ Affichage alertes visuelles 3 dépôts
☐ Former équipes dépôts (coordinateurs, responsables)
☐ Procédure écrite: "Comment lire l'alerte min-max"
☐ Test lancement: 1 semaine production
☐ Suivi ruptures/surstock (KPI heure)
☐ Ajustements z si trop/trop peu ruptures
```

### Semaine 7-8: SCALING + DEMAND SENSING
```
☐ Déployer tous 200+ SKU (scaling EOQ)
☐ Implémenter Holt-Winters (Excel VBA ou Python)
☐ Intégrer facteur saisonnier par mois
☐ Tester prévision 4 semaines
☐ Comparer réel vs prévision (MAPE%)
☐ Former acheteurs: lecture forecasts
```

### Semaine 9-12: STABILISATION
```
☐ Scoring fournisseur systématique (tous fournisseurs)
☐ Ajuster SS par score fournisseur
☐ Dashboard KPI temps réel (Tableau/Excel)
☐ Réunion mensuelle: révision forecasts + KPI
☐ Documentation: "Mode opératoire Stock Gedimat"
☐ Budget dépensé: €5-10K | Impact attendu: -10% coûts
```

---

## FICHIERS EXCEL À TÉLÉCHARGER/ADAPTER

1. **STOCK_EOQ_TEMPLATE.xlsx**
   - Colonnes: SKU, Article, D(an), S, P, H, EOQ
   - Formules VBA: CalculateEOQ()
   - Exemple rempli: Tuiles, Ciment, Briques, Peinture, Sable

2. **STOCK_SAFETY_STOCK_TEMPLATE.xlsx**
   - Colonnes: SKU, Article, σ_D/j, LT, z, SS, ROP
   - Formules: STDEV(), CalculateSafetyStock(), CalculateROP()
   - Tableau alertes: Min-Max-Orange/Rouge

3. **DEMAND_FORECAST_HOLT_WINTERS.xlsx**
   - 52 semaines données historiques
   - Lissage exponentiel (α=0.2)
   - Facteur saisonnier par mois
   - Prévision 4-12 semaines

4. **SUPPLIER_SCORECARD.xlsx**
   - Grille scoring multi-critères
   - 4-5 fournisseurs par catégorie
   - Calcul automatique score pondéré
   - Recommandation SS par score

5. **STOCK_MIN_MAX_TEMPLATE.xlsx**
   - Min-max par article
   - Alerte visuelle automatisée
   - Tableau d'action (commande/qtée/fournisseur/ETA)
   - Historique commandes

---

## KPI À SUIVRE (Tableau de Bord)

### HEBDOMADAIRE
```
- Taux Service: (Articles en stock) / (Articles demandés) → Cible >97%
- Taux Rupture: (Nb ruptures) / (Nb demandes) → Cible <1%
- Délai Appro Moyen: (Somme délais) / (Nb commandes) → Cible <8j
```

### MENSUEL
```
- Coût Stock Moyen: Valeur stock / (CA/12) → Cible <3% CA
- Taux Rotation: (CA/12) / Valeur stock → Cible 3-6x/an
- Forecast Accuracy: 100% - MAPE → Cible >90%
- Supplier Performance: Score moyen → Cible >8/10
```

### TRIMESTRIEL
```
- Économie Holding: Différence EOQ vs ancien → Cible €5-15K
- Réduction Ruptures: Comparaison Y1 vs Y0 → Cible -60%
- Satisfaction Clients: NPS → Cible +3 points
- ROI Outils: (Économies) / (Coût implementation) → Cible >2x
```

---

**Document:** Implémentation Pratique - Templates Excel & Cas Concrets
**Dernière mise à jour:** 16 novembre 2025
**Format:** Markdown + Excel téléchargeables
**Responsable:** Angélique (Coordinatrice) + Directeur Gedimat
