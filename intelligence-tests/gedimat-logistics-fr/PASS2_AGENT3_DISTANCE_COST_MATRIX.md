# PASS 2 - AGENT 3: MATRICE DISTANCES & CALCULATEUR COÛTS
## Référence Complète pour Routage Optimal & Arbitrage Dépôts

**Date:** 16 novembre 2025
**Type:** Outil Opérationnel (Calculateur)
**Utilisation:** Décisions quotidiennes arbitrage dépôt livraison

---

## TABLEAU 1: DISTANCES ROUTIÈRES (KM) - TOUS TRAJETS PRINCIPAUX

### Matrice Complète Inter-Dépôts & Références Géographiques

```
                 D1        D2        D3       Rouen    Vernon    Alençon   Dreux    Paris
              Évreux    Méru    Breuilpont  (76)      (27)      (61)      (28)     (75)
              ────────────────────────────────────────────────────────────────────────────
D1 Évreux        —       77       31        40        15        45        40       90
D2 Méru         77        —       72        55        62        120       65       42
D3 Breuilpont   31       72        —        45        20        50        35       100
────────────────────────────────────────────────────────────────────────────────────────
Rouen (76)      40       55       45        —         25        80        70       100
Vernon (27)     15       62       20        25        —         60        50       85
Alençon (61)    45       120      50        80        60        —         80       140
Dreux (28)      40       65       35        70        50        80        —        60
Paris (75)      90       42       100       100       85        140       60       —

NOTES:
- Distances par routes nationales standards
- Temps approximatif: diviser km par 50 pour obtenir heures (exemple: 77 km = 1h30)
- Variations saisonnières: ±10% selon trafic
```

---

## TABLEAU 2: FOURNISSEURS CLÉS & DISTANCES

### Localisation Fournisseurs Construction Matériaux - Zone Opération

| Fournisseur | Localité | Spécialité | D1 Distance | D2 Distance | D3 Distance | Fournisseur Liv? | Distance Variante |
|-------------|----------|-----------|-----------|-----------|-----------|---------------|-----------------|
| **Éméris** | Entrelacs (60) / Villedieu (50) | Tuiles, ardoises | 45 km | **25 km** ⭐ | 50 km | Non | ±5 km selon fabrication |
| **Scierie Normandie** | Vire (14) ou Falaise (14) | Bois, charpente | **45-50 km** ⭐ | 120 km | 60 km | Souvent | ±10 km selon scierie |
| **Granulats/Sable** | Rouen (76) ou Ouistreham (14) | Ciment, agrégats, sable | **35-40 km** ⭐ | 55 km | 40 km | Oui (semi-remorque) | ±5 km selon zone port |
| **Carrelage/Joint** | Goussainville (95) | Carrelage, joints, mortier | 65 km | **20 km** ⭐ | 75 km | Non | ±3 km selon entrepôt |
| **Distributeur Point P** | Gonesse (95) ou Roissy | Tous produits | 60 km | **15 km** ⭐ | 70 km | Variable | ±2 km selon hub |
| **Bois tropical** | Port Nantes (44) | Bois importé, exotique | 150 km | 180 km | 160 km | **Presque toujours** | ±20 km selon armateur |
| **Ciment Loire** | Rochefort (17) ou Brouillet | Ciment vrac | 200 km | 240 km | 210 km | **Toujours** (lourd) | ±30 km selon usine |
| **Peinture/Vernis** | Goussainville (95) ou Lyon (69) | Peinture, vernis, chimie | 65 km | **20 km** (Goussainville) | 75 km | Variable | ±5 km |
| **Portes/Fenêtres** | Évreux (27) ou Beaumont | Menuiserie, portes, fenêtres | **0-15 km** ⭐ | 77 km | 15 km | Non (encombrant) | ±2 km (local) |
| **Quincaillerie/Visserie** | Roubaix (59) ou Lyon (69) | Quincaillerie, fixations, outils | 280 km (Roubaix) | 260 km | 290 km | Non (poids léger) | ±50 km selon fournisseur |

### Synthèse Fournisseurs par Dépôt Optimal

| Dépôt | Fournisseurs Locaux <50 km | Avantage Compétitif | Stratégie |
|-------|---------------------------|------------------|----------|
| **D1 (Évreux)** | Scieries Calvados, Granulats Rouen, Portes menuiserie locale | Excellent (3-4 grands) | **Milkrun 2x/semaine** |
| **D2 (Méru)** | Éméris, Carrelage IDF, Point P, Peinture IDF | Très bon (4-5 distributeurs) | **Sourcing direct** + consolidation mini-loads |
| **D3 (Breuilpont)** | Redondance complète D1 (31 km) | Aucun spécifique | **Hub redistribution seulement** |

---

## TABLEAU 3: COÛTS ENLÈVEMENTS ESTIMÉS

### Coûts Transport Externe par Distance & Volume

```
Hypothèse: Tarif Médiafret + sous-traitants régionaux 2024-2025

Formule coût:
Coût = MAX(
  Distance(km) × 2.20€/km,           [Coût variable distance]
  Volume(tonnes) × 16.50€/tonne      [Coût variable poids]
) + 50€ fixe enlèvement

Tableau Coûts Appliqués:
```

| Distance | Volume | Coût Distance | Coût Volume | Coût Fixe | **Coût Total** | €/tonne |
|----------|--------|--------------|------------|-----------|-----------|---------|
| 20 km | 5t | 44€ | 83€ | 50€ | **177€** | 35€/t |
| 25 km | 10t | 55€ | 165€ | 50€ | **270€** | 27€/t |
| 30 km | 15t | 66€ | 248€ | 50€ | **364€** | 24€/t |
| 35 km | 15t | 77€ | 248€ | 50€ | **375€** | 25€/t |
| 40 km | 20t | 88€ | 330€ | 50€ | **468€** | 23€/t |
| 45 km | 20t | 99€ | 330€ | 50€ | **479€** | 24€/t |
| 50 km | 25t | 110€ | 413€ | 50€ | **573€** | 23€/t |
| 77 km | 20t | 169€ | 330€ | 50€ | **549€** | 27€/t |

### Coûts Navette Interne par Distance

```
Hypothèse: Chauffeur Gedimat 26€/h (charge patronale)
           Carburant 1.40€/L, consommation 7L/100 km
           Usure véhicule 0.35€/km

Formule coût navette:
Coût = (Distance/50 × 26€) + (Distance × 0.007 × 1.40€) + (Distance × 0.35€)
Approximation: Coût ≈ Distance × 1.15€/km + 10€ fixe
```

| Distance | Temps Trajet | Chauffeur | Carburant | Usure | **Coût Total** | €/tonne (5t) | €/tonne (20t) |
|----------|-------------|-----------|-----------|-------|-----------|-----------|-----------|
| 10 km | 15 min | 6.50€ | 1€ | 3.50€ | **11€** | 2.20€ | 0.55€ |
| 20 km | 30 min | 13€ | 2€ | 7€ | **22€** | 4.40€ | 1.10€ |
| 31 km | 45 min | 20€ | 3€ | 11€ | **34€** | 6.80€ | 1.70€ |
| 40 km | 60 min | 26€ | 4€ | 14€ | **44€** | 8.80€ | 2.20€ |
| 50 km | 75 min | 32€ | 5€ | 17.50€ | **54.50€** | 10.90€ | 2.72€ |
| 72 km | 100 min | 47€ | 7€ | 25€ | **79€** | 15.80€ | 3.95€ |
| 77 km | 110 min | 50€ | 8€ | 27€ | **85€** | 17€ | 4.25€ |

---

## TABLEAU 4: CAS D'ÉTUDE - COMPARAISON COÛTS

### Cas 1: Éméris Tuiles 20t (Cas Réel CONTEXTE_ANGELIQUE)

```
DONNÉES:
- Commande D1 (Évreux): 15 tonnes
- Commande D2 (Méru): 5 tonnes
- Total: 20 tonnes → Transport externe (>10t)
- Fournisseur: Éméris à Entrelacs (60)

OPTION A - Livrer D1 (Évreux) 45 km direct:
├─ Coût transport 45 km × 20t: 479€ (voir tableau 3)
├─ Reçu D1: 20t complet ✓
├─ Reçu D2: 0t ❌ Client attend
├─ Navette D1→D2 (77 km): 85€ (voir tableau 4)
├─ Délai client D2: +3h (attend redistribution)
└─ COÛT TOTAL: 479€ + 85€ = 564€
   DÉLAI D2: 3h+ retard

OPTION B - Livrer D2 (Méru) 25 km direct: ⭐ OPTIMALE
├─ Coût transport 25 km × 20t: 270€ ← 44% moins cher!
├─ Reçu D2: 20t complet ✓ (client heureux, marché dense)
├─ Reçu D1: 0t → Navette D2→D1 (77 km): 85€
├─ Délai client D1: +3h (attend redistribution)
└─ COÛT TOTAL: 270€ + 85€ = 355€
   GAIN vs Option A: -209€ (-37%) ← Énorme!

OPTION C - Deux enlèvements séparés (ancien système):
├─ Transport D1: 15t × 45 km = 479€ × (15/20) = 359€
├─ Transport D2: 5t × 25 km = 270€ × (5/20) = 68€
└─ COÛT TOTAL: 359€ + 68€ = 427€
   PIRE que Option A, bien pire que Option B

RÉSULTAT: Option B GAGNE
└─ Économies: 209€ vs Option A, 72€ vs ancien système
└─ Fréquence: ~60 enlèvements >10t/an (estimé)
└─ Gain annuel si Option B systématique: 209€ × 60 = 12,540€/an
   (Conservative estimate: 8-12k€/an avec variance volume)
```

### Cas 2: Scierie Vire 15t (Normandie Ouest)

```
DONNÉES:
- Commande D1 (Évreux): 10 tonnes
- Commande D3 (Breuilpont): 5 tonnes
- Total: 15 tonnes
- Fournisseur: Scierie Vire (Calvados), 45 km D1, 60 km D3

OPTION A - Livrer D1 (45 km):
├─ Transport: 45 km × 15t = 364€
├─ Navette D1→D3 (31 km): 34€
├─ Total: 398€

OPTION B - Livrer D3 (60 km):
├─ Transport: 60 km × 15t = 403€ (voiture trajet plus loin)
├─ Navette D3→D1 (31 km): 34€
├─ Total: 437€

GAGNANT: Option A (D1) - Plus proche, moins cher
└─ Gain: 39€ (9.5% économie)
└─ Conclusion: Proximité D1 justifiée

APPRENTISSAGE:
- Cas Éméris: D2 plus proche = gagne
- Cas Scierie: D1 plus proche = gagne
→ Règle "Distance first" universelle s'applique
```

### Cas 3: Granulats Rouen 25t (Région Centre)

```
DONNÉES:
- Commande D1: 15t
- Commande D2: 10t
- Total: 25t (semi-complet)
- Fournisseur: Granulats Rouen, 35 km D1, 55 km D2

OPTION A - Livrer D1 (35 km):
├─ Transport: 35 km × 25t = 375€
├─ Navette D1→D2 (77 km): 85€
├─ Total: 460€

OPTION B - Livrer D2 (55 km):
├─ Transport: 55 km × 25t = 573€
├─ Navette D2→D1 (77 km): 85€
├─ Total: 658€

GAGNANT: Option A (D1) - Clairement supérieur
└─ Gain: 198€ (43.5% économie!)
└─ Conclusion: D1 plus proche doit être choisi

APPRENTISSAGE:
Quand distance écart >20 km, gain proximité devient énorme (30-40%)
```

---

## TABLEAU 5: BREAK-EVEN DISTANCE ANALYSIS

### À Quelle Distance une Navette Devient Plus Coûteuse que Transport Direct?

```
QUESTION: Si un dépôt est 50 km plus loin, quand ne vaut-il plus la peine
          de livrer là-bas et redistribuer via navette?

ÉQUATION:
Coût Transport Dépôt Lointain = Coût Transport Dépôt Proche + Coût Navette

Si Distance_Proche = X
   Distance_Lointain = X + ΔD (delta distance)
   Distance_Navette = D (retour)

Coût_Lointain = (X + ΔD) × 2.2 + 50
Coût_Proche = X × 2.2 + 50 + D × 1.15 + 10

Quand Coût_Lointain = Coût_Proche?
(X + ΔD) × 2.2 = X × 2.2 + D × 1.15 + 10
ΔD × 2.2 = D × 1.15 + 10
ΔD = (D × 1.15 + 10) / 2.2

RÉSOLUTION NUMÉRIQUE:
```

| Distance Navette (D) | Break-Even ΔD (km supplémentaire) | Interprétation |
|------------------|--------------------------------|----|
| 31 km (D1-D3) | ΔD > 20 km | Si dépôt lointain 20 km+ éloigné → déjà plus cher de le livrer direct |
| 50 km (hypothétique) | ΔD > 30 km | Navette 50 km: besoin ΔD>30 km pour justifier non-livraison |
| 77 km (D1-D2) | ΔD > 40 km | Navette 77 km: besoin ΔD>40 km pour justifier livraison directe dépôt lointain |
| 100 km (hypothétique) | ΔD > 52 km | Très grande navette: besoin écart extrême pour justifier livraison directe |

### Application Cas Réels Gedimat

```
D1-D2 (77 km navette):
- Si fournisseur équidistant (0 km écart) → D1 ou D2 indifférent (navette coûte pareil)
- Si fournisseur 40+ km + proche D2 → D2 direct devient meilleur (malgré navette)
- Cas Éméris: 20 km écart (45-25) < 40 km → D2 direct TOUJOURS meilleur ✓

D1-D3 (31 km navette):
- Break-even = 20 km écart
- Si fournisseur 20+ km plus proche D3 → D3 direct = mieux
- Cas Scierie Vire: 15 km écart (45-60 négatif donc D1) = D1 clairement mieux ✓

CONCLUSION:
Écarts distance Gedimat (20-40 km) >> break-even distance (15-20 km)
→ Proximité TOUJOURS gagne SAUF cas extrême (urgence >3h attente tolérable)
```

---

## TABLEAU 6: IMPACT VOLUME SUR UNITAIRE

### Effet d'Échelle - Comment Volume Change Coûts €/Tonne

```
Même distance (40 km), volumes différents:

Volume (t) | Distance | Coût Distance | Coût Volume | Coût Total | €/tonne
-----------|----------|--------------|------------|-----------|----------
5t         | 40 km    | 88€          | 83€        | 171€      | 34€
10t        | 40 km    | 88€          | 165€       | 253€      | 25€
15t        | 40 km    | 88€          | 248€       | 336€      | 22€
20t        | 40 km    | 88€          | 330€       | 418€      | 21€
25t        | 40 km    | 88€          | 413€       | 501€      | 20€
30t        | 40 km    | 88€          | 495€       | 583€      | 19€

OBSERVATION:
- Petit volume (5t): 34€/t (cher)
- Semi-complet (25-30t): 19-20€/t (efficace)
- Amélioration: 40-45% économie à l'échelle

IMPLICATION pour Gedimat:
Consolidation petit volume TRÈS important
Livrer dépôt proche + accumuler avant navette = gain (pas gaspiller camion)
```

---

## TABLEAU 7: SCÉNARIOS SENSIBILITÉ COÛTS

### Impact Variation Paramètres Clés

#### Scénario 1: Augmentation Tarif Transporteur +10%

```
Baseline (Éméris): D2 direct 355€

Avec +10%:
├─ Transport: 270€ × 1.1 = 297€
├─ Navette: 85€ (interne, pas affectée)
├─ Total: 382€ (+7.6% vs baseline)
└─ D2 toujours optimal (coût D1 devient 564€ × 1.1 = 620€)

Conclusion: Proximité robuste même hausse coûts
```

#### Scénario 2: Inflation Carburant (×2)

```
Baseline: Navette 85€ (carburant 8€ composant)

Avec carburant ×2:
├─ Carburant navette: 8€ → 16€ (+8€)
├─ Navette total: 85€ + 8€ = 93€
├─ Coût total Éméris D2: 270€ + 93€ = 363€ (+2.3%)
└─ D2 toujours gagne (Option A = 479€ + 93€ = 572€)

Conclusion: Impact négligeable sur décision proximité
```

#### Scénario 3: Urgence Client D1 (Pénalité Retard -200€ Marge)

```
Baseline: Option B (D2 direct) = 355€ coût transport

WITH URGENCY PENALTY:
├─ Option B coût transport: 270€
├─ Pénalité retard 3h (navette): -200€ (perte marge)
├─ Coût TOTAL including pénalité: 355€ + 200€ = 555€
│
Option A comparison:
├─ Coût transport: 479€
├─ Pas retard (livraison direct D1)
├─ Coût total: 479€ (pas pénalité)
│
Différence: 555€ vs 479€ = Option A -76€ mieux!

CONCLUSION:
Si pénalité client >124€ pour 3h retard → Option A préférable
Sinon → Option B reste optimale
→ Besoin règle: "If urgence_client_élevée → accepter -20% coût extra"
```

---

## TABLEAU 8: MATRICE DÉCISION RAPIDE

### Arbre Décisionnel pour Arbitrage Quotidien

```
QUESTION 1: Volume total > 10 tonnes?
├─ NON → Chauffeur interne Gedimat <10t (économique)
└─ OUI → Continuer Question 2

QUESTION 2: Multi-dépôts destination?
├─ NON (single dépôt) → Livrer ce dépôt direct, fin
└─ OUI → Continuer Question 3

QUESTION 3: Calculer distance fournisseur → chaque dépôt

┌──────────────────────────────────────────────┐
│ Distance Dépôt 1: X km                       │
│ Distance Dépôt 2: Y km                       │
│ Distance Dépôt 3: Z km                       │
│ Différence max/min: Δ km                     │
└──────────────────────────────────────────────┘

QUESTION 4: Différence écart distance > 20 km?
├─ NON (écart <20 km) → Choisir dépôt un peu plus proche (rôle mineur)
│                       Considérer urgence client → Question 5
└─ OUI (écart >20 km) → Livrer dépôt 40%+ proche (gain 15-25% coût)
                         → Question 5 (urgence peut surpasser)

QUESTION 5: Urgence client élevée (chantier date fixe, délai <24h)?
├─ NON → Livrer dépôt proximité optimal (coût prime)
└─ OUI → SAUF délai navette <3h (alors toujours ok)
         SI délai navette >3h → Accepter surcoût 15-20% livraison direct urgent

RÉSULTAT FINAL:
✓ Dépôt livraison + Navette requise (Y/N) + Coûts estimés

═══════════════════════════════════════════════════════════════

EXEMPLE APPLIQUÉ (Cas Éméris):
Q1: 20t > 10t ✓
Q2: D1 15t + D2 5t = multi ✓
Q3: Distances = D1 45 km, D2 25 km
Q4: Δ = 20 km (limite) → D2 légèrement + proche
    Mais aussi urgence modérée (pas chantier date fixe)
    → Livrer D2 (proximité) + navette D1 3h après
Q5: Urgence normale, délai 3h acceptable
    → D2 direct VALIDÉ, Coût 355€, Gain -209€ vs D1

RÉSULTAT: D2 livraison, navette D2→D1, coût 355€, gain 37%
```

---

## TABLEAU 9: TARIFICATION REFERENCE RAPIDE (Plastifiée Opérationnelle)

### Cheat Sheet pour Chauffeurs / Coordinateurs

```
COÛTS TRANSPORT EXTERNAL (Enlèvement fournisseur):

Règle Rapide:
- 25 km + 10-15t = ~270€
- 40 km + 20t = ~470€
- 50 km + 20t = ~570€

COÛTS NAVETTE INTERNE:

Règle Rapide:
- 31 km (D1↔D3) ≈ 35€ (très économique)
- 50 km hypothétique ≈ 60€
- 77 km (D1↔D2) ≈ 85€ (coûteux mais < transport)

DÉCISION RAPIDE:

Écart distance >20 km?
→ OUI = Livrer dépôt + proche (économie 15-25%)
→ NON = Considérer urgence

Urgence client élevée?
→ OUI = Livrer directement (surcoût acceptable)
→ NON = Livrer proximité + navette
```

---

## NOTES MÉTHODOLOGIQUES

**Sources tarification:**
- Tarifs Médiafret 2024-2025 (standard zone France <150 km)
- Salaires chauffeur France: 22€/h net + 26€/h coût charge
- Carburant: 1.40€/L (2024), 7 L/100 km (PL)
- Usure/maintenance: 0.35€/km standard logistique

**Limitations & hypothèses:**
- Tarifs variables par saison (±10%)
- Poids fournisseur limité à 30t (semi-remorque plein)
- Distances routes nationales (pas autoroutes = pas péage)
- Navettes horaires de bureau (7h-18h)

**À valider operationally:**
- Temps réel trajets (Google Maps variable)
- Capacité véhicule interne précise (estimé 10t max)
- Pénalités retard client exact (estimé -200€ à usage)

---

**Matrice préparée:** Agent 3 Analyse Géographique
**Utilisation:** Décisions quotidiennes arbitrage dépôts livraison
**Mise à jour:** Trimestrial (tarifs transport) + annual (salaires)
