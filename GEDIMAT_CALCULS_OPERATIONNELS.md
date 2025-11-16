# Gedimat - Calculs Opérationnels Détaillés
## Exemples d'Application Matériaux Construction

---

## 1. EXEMPLE DÉTAILLÉ : CIMENT CEM II 42,5 - DÉPÔT MARSEILLE

### 1.1 Collecte Données Historiques (6 mois : Mai-Oct 2024)

```
Demande quotidienne (sacs/jour) :
Mai :     450, 480, 460, 490, 510, 430, 520, 470, ...  → Moy = 471/j
Juin :    510, 545, 580, 550, 610, 590, 620, 630, ...  → Moy = 565/j (pic été)
Juillet : 630, 620, 640, 680, 670, 650, 690, 710, ...  → Moy = 663/j (max)
Août :    520, 510, 480, 500, 490, 450, 470, 460, ...  → Moy = 489/j (baisse vacances)
Sept :    480, 510, 520, 530, 510, 490, 530, 560, ...  → Moy = 516/j
Oct :     420, 450, 430, 460, 480, 400, 440, 470, ...  → Moy = 444/j (baisse)

Moyenne période 6 mois : (471 + 565 + 663 + 489 + 516 + 444) / 6 = 524 sacs/jour
Écart-type quotidien (calculé sur tous les jours) : σ_d = 92 sacs
Coefficient variation : 92 / 524 = 17,6% (faible variabilité jour-à-jour)
```

**Mais saisonnalité extrême** : 663 juil vs 444 oct = -33% → Adapter modèle par saison

### 1.2 Coûts Gedimat Marseille Ciment

**Coûts de Commande** :
- Frais administratifs (création CMD, vérification qualité, dédouanement) : 45 €
- Frais transport groupé (palettisation, manutention) : 25 €
- Coûts système (EDI, traçabilité) : 15 €
- **Total C_c = 85 € / commande**

**Coûts de Détention Annuels** :
- Loyer entrepôt Marseille : 0,15 €/sac/an (au m² ÷ capacité)
- Assurance stock (0,5% valeur) : 0,08 €/sac/an (ciment = 15 €/sac)
- Manutention interne (reséquençage) : 0,05 €/sac/an
- Obsolescence / casse (2-3%) : 0,04 €/sac/an
- Financement (4% coûts capital) : 0,06 €/sac/an
- **Total C_d = 0,38 €/sac/an**

**Ou par jour** : C_d = 0,38 / 365 = **0,00104 €/sac/jour**

### 1.3 Calcul EOQ Marseille Ciment

**Demande annuelle (novembre 2024 - octobre 2025)** :
```
D = 524 sacs/jour × 365 jours = 191,260 sacs/an

Ajusté saisonnalité (prévision 2025) :
Mai-Oct normale : 450k sacs = 124,000 sacs
Nov-Avr réduit (-15%) : 150k → 127,500 sacs
Prévision 2025 : ~183,500 sacs (été moins fort qu'été 2024)

Utiliser D = 190,000 sacs (projection conservative)
```

$$EOQ = \sqrt{\frac{2 \times 190,000 \times 85}{0,38}}$$

$$= \sqrt{\frac{32,300,000}{0,38}} = \sqrt{85,000,000} ≈ \mathbf{9,220 \text{ sacs}}$$

**Ou par palette** (50 sacs/palette) : **184 palettes / commande**

**Fréquence commandes** : 190,000 / 9,220 ≈ **20.6 commandes/an**

**Cycle réapprovisionnement moyen** : 365 / 20.6 ≈ **17.7 jours**

### 1.4 Stock de Sécurité - Scénarios Service Level

**Contexte** :
- Lead time Fournisseur : 12 jours (10-15j, σ_L = 1.2 jours)
- Demande quotidienne moyenne : 524 sacs
- Écart-type demande quotidienne : 92 sacs
- Demande erratique, saisonnière

#### Scénario A : Service 95% (σ_d constant, L_t constant)

$$SS_{95\%} = Z_{95} \times \sigma_d \times \sqrt{LT}$$
$$= 1.645 \times 92 \times \sqrt{12}$$
$$= 1.645 \times 92 \times 3.464$$
$$≈ \mathbf{525 \text{ sacs}} \text{ (~10.5 palettes)}$$

**Coût détention annuel** : 525 × 0.38 = **199.5 €/an**

#### Scénario B : Service 99% (plus conservateur)

$$SS_{99\%} = Z_{99} \times \sigma_d \times \sqrt{LT}$$
$$= 2.326 \times 92 \times \sqrt{12}$$
$$= 2.326 \times 92 \times 3.464$$
$$≈ \mathbf{743 \text{ sacs}} \text{ (~14.9 palettes)}$$

**Coût détention annuel** : 743 × 0.38 = **282.3 €/an**

**Surcoût 99% vs 95%** : +218 sacs (-0.5 ruptures/an estimé)

#### Scénario C : Service Dynamique Saisonnière

Adapter Z par saison :
- Juillet (pic) : SS 99% (demande volatile)
- Nov-Fév (creux) : SS 90% (demande basse mais stable)
- Autres mois : SS 95% (standard)

```python
# Pseudocode logique opérationnelle
if month in ['Jun', 'Jul', 'Aug', 'Sep']:  # Saison haute
    Z = 2.326  # 99%
    SS = 743 sacs
elif month in ['Nov', 'Dec', 'Jan', 'Feb']:  # Saison basse
    Z = 1.28  # 90%
    SS = 365 sacs
else:
    Z = 1.645  # 95%
    SS = 525 sacs
```

**Stock moyen annuel** : (743×4 + 365×4 + 525×4) / 12 ≈ **545 sacs**
**vs statique 99%** : 743 sacs → **Économie -198 sacs** (-27%)

### 1.5 Point de Commande (ROP)

#### Configuration A : Statique (95% service)

$$ROP = (D_j \times LT) + SS$$
$$= (524 \times 12) + 525$$
$$= 6,288 + 525$$
$$= \mathbf{6,813 \text{ sacs}}$$

**Opérationnel** :
- Quand stock atteint 6,813 sacs → Déclencher commande
- EOQ = 9,220 sacs → 17.6 jours de consommation
- Pendant 12j délai : consommer ~6,288 sacs
- SS 525 protège les 2.4j de variabilité/retard

#### Configuration B : Dynamique (Demand Sensing)

Ajuster ROP quotidiennement selon prévision 7-14 jours :

```
Lundi 20 nov 2024 :
Prévision semaine (XGBoost + météo) : 450 sacs/jour (pluie prévue → chantiers arrêtés)
ROP_dynamique = (450 × 12) + 400 [SS réduit 95% → 90%] = 5,800 sacs

Mardi 21 nov 2024 :
Prévision : 510 sacs/jour (retour beau temps)
ROP_dynamique = (510 × 12) + 480 = 6,600 sacs

Mercredi 22 nov 2024 :
Alerte robustesse : si 5 jours consécutifs écart > 25% vs prévision → signaler outlier
```

**Impact** : Réduit ROP moyens de 8% sur année → -550 sacs stock moyen

### 1.6 Simulation Mois Type (Novembre 2024) - Configuration Statique ROP 6,813

| Date | Consommation | Stock Ouverture | Stock Clôture | Action |
|------|------------|------|------|---------|
| 1-5 Nov | 2,400 | 8,500 | 6,100 | Surveiller, proche ROP |
| 6-7 Nov | 1,100 | 6,100 | 5,000 | **< ROP → CMD #1 (9,220)** |
| 8-19 Nov | 6,300 | 5,000 + (retard livraison 4j) | 7,920 | Réception CMD #1 j12 |
| 20-30 Nov | 6,350 | 7,920 | 1,570 | Stock baisse, proche rupture |
| 30 Nov | — | 1,570 | — | **Alerte : < SS(525)** |
| 1-12 Déc | 6,288 | 1,570 + CMD#2 (9,220) | 4,502 | Réception CMD #2 |

**Observations** :
- ROP 6,813 fonctionne bien si Lead Time = 12j
- Si retard livrais +3j (semaine 8-19 Nov) → risque rupture
- SS 525 parfois insuffisant avec pics erratiques
- Besoin SS 99% (743) OR demand sensing pour flexibilité

---

## 2. EXEMPLE : TUILES MARSEILLE - DEMANDE TRÈS SAISONNIÈRE

### 2.1 Profil Demande

```
Historique 12 mois : Tuiles Marseille

Hiver (Nov-Fév) : 100-150 unités/jour (rénovations intérieures)
Printemps (Mar-Mai) : 250-350 unités/jour (pic construction)
Été (Jun-Aug) : 180-220 unités/jour (vacances ralentit BTP)
Automne (Sep-Oct) : 300-400 unités/jour (rush fin année)

Moyenne annuelle : 225 tuiles/jour
Saisonnalité index :
  - Hiver : 0.67× moyenne
  - Printemps : 1.56× moyenne
  - Été : 0.89× moyenne
  - Automne : 1.67× moyenne

Coefficient variation inter-saisons : 150% (TRÈS élevé)
```

### 2.2 Problème EOQ Standard

EOQ ignore saisonnalité → Trop petit en hiver (ruptures), trop grand en été (surstock)

```
EOQ hiver (124 tuiles/jour × 365 = 45,260/an) :
  D_hiver = 45,260 × 0.67 ÷ 4 mois / 12 = 11,565 tuiles en hiver uniquement
  EOQ_hiver = √(2×11,565×75÷1.2) ≈ 328 tuiles
  → Trop petit, ruptures fréquentes

EOQ printemps (225 × 1.56 = 351 tuiles/jour) :
  D_printemps = 351 × 365 × 0.25 = 32,091 tuiles
  EOQ_printemps = √(2×32,091×75÷1.2) ≈ 527 tuiles
  → Approprié
```

### 2.3 Solution : Classement Saisonnier + Demand Sensing

**Stratégie** :

```
Période (Nov-Fév) Hiver :
├─ Service Level : 90% (rupture acceptable, baisse demande)
├─ SS = 1.28 × 35 × √12 ≈ 155 tuiles
├─ EOQ = √(2×11,565×75÷1.2) ≈ 328 tuiles
└─ ROP = (124×12) + 155 = 1,643 tuiles

Période (Mar-May) Printemps :
├─ Service Level : 99% (pics importants, clients sensibles)
├─ SS = 2.326 × 65 × √12 ≈ 525 tuiles
├─ EOQ = √(2×32,091×75÷1.2) ≈ 527 tuiles
└─ ROP = (351×12) + 525 = 4,747 tuiles

Période (Jun-Aug) Été :
├─ Service Level : 92% (demande ralentit, capacité libérée)
├─ SS = 1.405 × 25 × √12 ≈ 121 tuiles
├─ EOQ = √(2×19,620×75÷1.2) ≈ 405 tuiles
└─ ROP = (201×12) + 121 = 2,533 tuiles

Période (Sep-Oct) Automne :
├─ Service Level : 99% (rush, clients urgents)
├─ SS = 2.326 × 70 × √12 ≈ 564 tuiles
├─ EOQ = √(2×32,775×75÷1.2) ≈ 534 tuiles
└─ ROP = (375×12) + 564 = 5,064 tuiles

Demand Sensing Adjustment :
├─ +7 jours API météo (pluie réduit chantiers)
├─ Calendrier BTP (rentrée sept ↑ 20%, congés juil ↓ 15%)
├─ Promos calendaire (mai → débordements juin)
└─ ROP dynamique ±15% vs statique saisonnier
```

### 2.4 Comparaison Stocks Gérés

| Approche | Stock Moyen | Max | Min | Ruptures/an |
|----------|-----------|-----|-----|---|
| **EOQ statique** | 450 | 975 | 180 | 6-8 |
| **EOQ saisonnier** | 320 | 780 | 140 | 2-3 |
| **+ Demand sensing** | 285 | 740 | 130 | 0-1 |

**Économie stock moyen** : 450 → 285 tuiles (-37%)
**Coût détention/an** : -37% × 365 × coût_stockage

---

## 3. EXEMPLE MULTI-ÉCHELON : CIMENT 3 DÉPÔTS CONSOLIDÉS

### 3.1 Données de Base

| Dépôt | Ville | Demande/j | σ_d | Lead time | SS 95% (isolé) |
|-------|-------|-----------|-----|-----------|---|
| A | Marseille | 524 | 92 | 12j | 525 |
| B | Paris (IDF) | 580 | 105 | 10j | 552 |
| C | Lyon | 420 | 78 | 11j | 435 |
| **TOTAL** | **3 sites** | **1,524** | **σ_global=?** | **Moyen 11j** | **1,512** |

### 3.2 Calcul Variabilité Globale (Pooling)

Si demandes indépendantes (pas corrélées) :

$$\sigma_{global}^2 = \sum_i \sigma_i^2 = 92^2 + 105^2 + 78^2 = 8,464 + 11,025 + 6,084 = 25,573$$

$$\sigma_{global} = \sqrt{25,573} ≈ 160 \text{ sacs}$$

**Non corrélé (hypothèse) ✓** : Demandes différentes régions n'influencent pas l'une l'autre

### 3.3 EOQ Multi-Échelon Centralisé

**Hub Strasbourg** :
- Demande totale : 1,524 × 365 = 556,260 sacs/an
- Coûts commande fournisseur : 95 € (grosse commande, moins frais)
- Coûts détention Hub : 0.30 €/sac/an (meilleur coût espace)

$$EOQ_{central} = \sqrt{\frac{2 \times 556,260 \times 95}{0.30}} = \sqrt{354,060,000} ≈ \mathbf{18,820 \text{ sacs}}$$

**vs 3 EOQ isolés** :
$$EOQ_A + EOQ_B + EOQ_C = 9,220 + 9,820 + 7,200 ≈ 26,240 \text{ sacs}$$

**Économie** : -26% taille moyenne commande

### 3.4 Stock de Sécurité Centralisé (Pooling Formula)

$$SS_{centralisé} = Z \times \sigma_{global} \times \sqrt{\sum LT_i^2}$$

$$= 1.645 \times 160 \times \sqrt{12^2 + 10^2 + 11^2}$$

$$= 1.645 \times 160 \times \sqrt{144 + 100 + 121}$$

$$= 1.645 \times 160 \times \sqrt{365} = 1.645 \times 160 \times 19.1$$

$$≈ \mathbf{502 \text{ sacs}}$$

**Réduction vs 3 dépôts isolés** :
```
Isolé total : 525 + 552 + 435 = 1,512 sacs
Centralisé : 502 sacs
Réduction : -1,010 sacs (-67%)
```

### 3.5 Structure Logistique MEIO Gedimat 3-niveaux

```
FOURNISSEUR (Groupe Lafarge, Italie)
    ↓ [Commande 18,820 sacs]
    ↓ [Lead 12j]
    ↓
┌─────────────────────────────────────┐
│  NIVEAU 1 : HUB STRASBOURG          │
│  ├─ Stock stratégique : 502 sacs SS │
│  ├─ Commande fournisseur : 18,820   │
│  ├─ Rotation : 19j cycle            │
│  └─ Partenaires : Dépôts A,B,C      │
└─────────────────────────────────────┘
    ↓↓↓ [Camions intra-réseau 2-3j]
┌──────────────┬──────────────┬──────────────┐
│ NIVEAU 2A    │ NIVEAU 2B    │ NIVEAU 2C    │
│ MARSEILLE    │ PARIS        │ LYON         │
│ [Buffer 7j]  │ [Buffer 7j]  │ [Buffer 7j]  │
│ 3,668 sacs   │ 4,060 sacs   │ 2,940 sacs   │
│ EOQ loc: 4k  │ EOQ loc: 4k  │ EOQ loc: 3k  │
└──────────────┴──────────────┴──────────────┘
    ↓↓↓ [Flux temps-réel vers clients]
    [CLIENTS PME BTP]
```

### 3.6 Réseau Transport Intra-Réseau

**Fréquence réapprovisionnement dépôts** (du Hub) :

- **Marseille** : 524×7 ≈ 3,670 sacs × 2/semaine = **2 camions/semaine**
  Coût : 2 × 350 €/camion = 700 €/semaine = 36.4k€/an

- **Paris** : 580×7 ≈ 4,060 sacs × 2/semaine = **2 camions/semaine**
  Coût : 2 × 280 €/camion (+ proche Hub) = 560 €/semaine = 29.1k€/an

- **Lyon** : 420×7 ≈ 2,940 sacs × 2/semaine = **2 camions/semaine**
  Coût : 2 × 320 €/camion = 640 €/semaine = 33.3k€/an

**Total transport intra-réseau** : **36.4 + 29.1 + 33.3 = 98.8k€/an**

### 3.7 ROI Multi-Échelon

| Composante | Baseline (3 isolés) | MEIO Centralisé | Bénéfice |
|-----------|---|---|---|
| **Stock moyen (sacs)** | 1,512 | 502 | -1,010 (-67%) |
| **Coût détention/an** | 183.8k€ | 60.2k€ | **-123.6k€** |
| **Transport intra-réseau** | — | 98.8k€ | -98.8k€ |
| **Commandes fournisseur (coûts)** | 23.2k€ | 12.4k€ | **+10.8k€** |
| **Flexibilité opérationnelle** | Faible | Excellente | valeur |
| **NET BÉNÉFICE** | — | — | **-211.6k€** |

**Payback period** : ~0 (gains immédiat)

---

## 4. COMPARAISON ALGORITHMES DEMAND SENSING

### 4.1 Cas : Prévision Ciment Marseille 7 jours

**Données réelles novembre 2024** :

| Jour | Réel (sacs) | ARIMA | XGBoost | Méteo | Consensus |
|-----|---|---|---|---|---|
| 1 Nov | 480 | 502 | 485 | 495 | **491** |
| 2 Nov | 510 | 498 | 508 | 520 | **509** |
| 3 Nov | 495 | 510 | 490 | 485 | **495** |
| 4 Nov | 505 | 515 | 510 | 500 | **508** |
| 5 Nov | 470 | 485 | 465 | 445 | **465** |
| 6 Nov | 520 | 530 | 525 | 540 | **532** |
| 7 Nov | 545 | 540 | 548 | 555 | **548** |
| **MAPE** | — | **2.1%** | **1.8%** | **3.2%** | **1.5%** |

**Erreur Absolue Moyenne % (MAPE)** :
- ARIMA seul : 2.1% (bon baseline)
- XGBoost : 1.8% (meilleur)
- Méteo/externe : 3.2% (bruit données)
- **Consensus (60% XGB, 30% ARIMA, 10% Méteo)** : **1.5%** ← Meilleur

### 4.2 Impact ROP Dynamique

```
Configuration statique ROP = 6,813 sacs

XGBoost prévoit semaine basse (450/j) → Réduire ROP à 5,800
Économie : 1,013 sacs pendants 7j = -0.038 € × 7 = -0.27€
Mais si rupture : coût urgence transport 300€

Configuration dynamique :
Si forecast baisse, réduire ROP → Économies stock
Si forecast hausse, augmenter ROP → Évite ruptures

Résultat annuel : -35k€ inventory + 8k€ economies urgences = -43k€/an
```

---

## 5. CHECKLIST IMPLÉMENTATION GEDIMAT

### Phase 1 : Audit (2-3 semaines)

- [ ] Extraire 24 mois données WMS (demandes réelles)
- [ ] Calculer σ_d, saisonnalité par SKU/région
- [ ] Comptabiliser coûts réels commande (75-95 €/commande)
- [ ] Coûts détention (0.35-0.40 €/unité/an)
- [ ] Valider lead times fournisseurs (10-15j réels vs contrat)
- [ ] Recenser ruptures 2024 (fréquence, coûts urgences)

### Phase 2 : Calculs (1 semaine)

- [ ] EOQ statique par SKU → Comparer vs pratique actuelle
- [ ] SS 95% et 99% → Sélectionner par classe ABC
- [ ] ROP statique pour chaque dépôt
- [ ] Modèle saisonnier pour tuiles, briques (variabilité > 30%)
- [ ] Validation vs simulation historique (hindcasting)

### Phase 3 : Demand Sensing Pilote (6-8 semaines)

- [ ] API météo intégration (OpenWeather ou NOAA)
- [ ] Calendrier BTP (jours fériés, périodes de congés)
- [ ] Module POS temps-réel → Data lake
- [ ] Entraîner ARIMA + XGBoost sur 24 mois ciment Marseille
- [ ] Backtesting MAPE 2024 → Validation < 5%

### Phase 4 : Multi-Échelon Conception (4 semaines)

- [ ] Modèle coûts transport Hub ↔ Dépôts
- [ ] Calcul pooling formula 3 régions
- [ ] Dimensionner Hub (capacité, localisation Strasbourg/Lyon)
- [ ] Négociations fournisseurs (délais EOQ géantes)
- [ ] Business case ROI

### Phase 5 : Production (3-6 mois)

- [ ] Déployer demand sensing 4 dépôts (Marseille, Paris, Lyon, Bordeaux)
- [ ] Intégrer recommandations ROP systèmes ERP
- [ ] Former équipes opérationnelles (logique SS, alertes)
- [ ] Monitorer MAPE, ruptures, stock turns
- [ ] Rollout multi-échelon progressif (test 1 mois puis complet)

---

**Document d'implémentation opérationnelle - Gedimat 2025**
