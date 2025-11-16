# FORMULES VRP ET SEUILS DE DÉCISION DÉTAILLÉS - GEDIMAT
## Annexe Technique - Calculs d'Optimisation Logistics

**Complément à :** ANALYSE_VRP_CONSOLIDATION_GEDIMAT_2025.md
**Date :** Novembre 2025
**Public :** Équipe logistique + Encadrement opérationnel

---

## 1. SEUILS DE CONSOLIDATION - FORMULES PRÉCISES

### 1.1 Décision Binaire : Affrètement Isolé vs Consolidation

**Condition d'optimalité consolidation :**

$$
\text{Consolider} \Leftrightarrow \sum_i C_i^{\text{consolidé}} + C_{\text{coord}} < \sum_i C_i^{\text{isolé}}
$$

**Où :**
- $C_i^{\text{isolé}}$ = Coût affrètement commande $i$ seule (€)
- $C_i^{\text{consolidé}}$ = Coût proportionnel commande $i$ dans tournée groupée (€)
- $C_{\text{coord}}$ = Coût coordination logistique (€)

**Formules de coûts :**

$$
C_i^{\text{isolé}} = C_{\text{base}} + D_i \times 6,50 \text{ €/km} + S_{\text{petit volume}}
$$

**Détail :**
- $C_{\text{base}}$ = Frais administratifs Médiafret = 150€
- $D_i$ = Distance fournisseur → dépôt $i$ (km)
- $S_{\text{petit volume}}$ = Surtaxe si vol < 10t = +20-30% du tarif base

$$
C_i^{\text{consolidé}} = \frac{C_{\text{tournée}} \times q_i}{\sum_j q_j}
$$

**Détail :**
- $C_{\text{tournée}}$ = Coût total tournée multi-clients (€)
- $q_i$ = Tonnage commande $i$ (t)
- $\sum_j q_j$ = Tonnage total tournée (t)

**Allocation coûts tournée :**

$$
C_{\text{tournée}} = C_{\text{chauffeur}} + C_{\text{carburant}} + C_{\text{manut.}}
$$

$$
= (100€ + 24,20€/h \times T_{\text{tournée}}) + (0,30€/km \times D_{\text{tournée}}) + (25€ \times n_{\text{sites}})
$$

**Où :**
- $T_{\text{tournée}}$ = Durée tournée (heures)
- $D_{\text{tournée}}$ = Distance totale tournée (km)
- $n_{\text{sites}}$ = Nombre sites décharge

### 1.2 Seuils Quantitatifs (Calibrés Gedimat)

**Tableau seuils empiriques - Quand consolider est rentable ?**

#### Seuil 1 : Poids Total

$$
\text{Consolider SI} : \sum_i q_i \geq 10 \text{ tonnes}
$$

**Justification :** En dessous 10t, affrètement small-volume surtaxé (+30%) pas compensé par économies regroupement. Au-delà 10t, gains regroupement + navettes justifient coordination.

**Exemple :**
- Commande isolée 8t → Affrètement = 150€ + (50km × 6,50) + 30% surcharge = 150 + 325 + 112 = **587€**
- Commande isolée 12t → Affrètement = 150 + (50 × 6,50) = **475€** (pas surcharge petit volume)
- **Delta = 112€ → seuil 10t justifié**

#### Seuil 2 : Nombre de Dépôts Destinataires

$$
\text{Consolider SI} : n_{\text{dépôts}} \geq 2
$$

**Justification :** Avec 1 dépôt, pas de "multi-dépôt problem" → pas consolidation possible. 2+ dépôts = opportunité navette interne après livraison hub.

#### Seuil 3 : Délai Client

$$
\text{Consolider SI} : \text{délai\_client} \geq 48 \text{ heures}
$$

**Justification :** <48h = urgence, impossible attendre coordination 48h avant lancement. ≥48h = window de consolidation ouvert.

**Calcul délai minimum pour consolider :**

$$
\Delta t_{\text{min}} = \text{LT}_{\text{fournisseur}} + \text{délai\_coordination} + \text{délai\_transport}
$$

$$
= 12 \text{ jours} + 2 \text{ jours} + 1 \text{ jour} = 15 \text{ jours}
$$

Si délai client < 15j : pas consolidation, chauffeur direct ou navette urgence.

#### Seuil 4 : Distance Géographique Max

$$
\text{Consolider SI} : \text{Max}(D_i, D_j, D_k) \leq 150 \text{ km}
$$

**Justification :** Au-delà 150km, distance tournée dépasse durée chauffeur 8h (vitesse 80km/h = 10,5h > 8h). Obligation split en 2 trajets = perte gains consolidation.

**Calcul distance tournée max :**

$$
D_{\text{tournée}} = \sum_i (\text{distance fournisseur} \to \text{dépôt}_i + \text{distance dépôt}_i \to \text{dépôt}_{i+1})
$$

**Exemple Émerge (Évreux) vers 2 dépôts :**
- Évreux → Lieu (20km) + Lieu → Méru (45km) + retour parc = **65 km total** ✓ Consolidable

### 1.3 Fonction d'Optimisation : Quand Consolider Économise Vraiment ?

**Calcul ROI consolidation :**

$$
\text{Gain Consolidation} = (C^{\text{isolé}} - C^{\text{consolidé}}) - C_{\text{coord}}
$$

**Application cas Émerge (exemple réel) :**

```
SCÉNARIO ISOLÉ (2 enlèvements séparés Médiafret)
──────────────────────────────────────────────────
Enlèvement 1 (Émerge → Méru, 15t, 80km) :
  C1_isolé = 150€ + (80 × 6,50) = 150 + 520 = 670€

Enlèvement 2 (Émerge → Gisors, 5t, 30km) :
  C2_isolé = 150€ + (30 × 6,50) + 30% surcharge petit vol
           = 150 + 195 + 104 = 449€

TOTAL C_isolé = 670 + 449 = 1 119€

SCÉNARIO CONSOLIDÉ (Chauffeur + navette interne)
──────────────────────────────────────────────────
Tournée chauffeur (Évreux → Lieu → Méru) :
  Durée : 3h transport + 1,5h décharge = 4,5h
  C_tournée = 100€ + (24,20 × 4,5) + (0,30 × 65km) + (25 × 2 sites)
            = 100€ + 109€ + 19,50€ + 50€ = 278€

Allocation proportionnelle :
  C1_consolidé = 278 × (15/20) = 208,50€
  C2_consolidé = 278 × (5/20) = 69,50€
  Total = 278€

Navette redistribution (Méru → Gisors, 5t, 50km) :
  Coût navette = 25€ (marginal)

TOTAL C_consolidé = 278 + 25 = 303€

COÛT COORDINATION (Angelique)
────────────────────────────
Temps 30 min (confirmer délai, planifier) = 30€

CALCUL GAIN
───────────
Gain = (1 119 - 303) - 30 = 816 - 30 = 786€ ✓ TRÈS RENTABLE

Ratio gain/coût coord = 786 / 30 = 26,2 > 2 → Consolider OUI
```

---

## 2. FORMULES SCORING DÉPÔT DÉTAILLÉES

### 2.1 Normalisation des Variables

**Variable U (Urgence basée délai client):**

$$
U = \begin{cases}
1,00 & \text{if délai} \leq 24h \\
0,98 - 0,02 \times \lceil \text{délai} / 6 \rceil & \text{if } 24h < \text{délai} \leq 120h \\
0,30 & \text{if délai} > 120h
\end{cases}
$$

**Interprétation :**
- Délai J+1 (24h) → U = 1,00 (urgence maximale)
- Délai J+2 (48h) → U = 0,94 (urgence élevée)
- Délai J+3 (72h) → U = 0,90 (urgence moyenne)
- Délai J+5 (120h) → U = 0,70 (urgence faible)

**Variable P (Pénalité client normalisée):**

$$
P = \min \left( \frac{\text{pénalité\_jour}}{2000}, 1,0 \right)
$$

**Justification :** Seuil 2000€/jour = max pénalité secteur BTP. Normalise 0-1.

**Variable V (Volume relatif):**

$$
V = \frac{q_{\text{dépôt}}}{\sum_i q_i}
$$

**Variable D (Distance inverse):**

$$
D = 1 - \frac{d_{\text{fournisseur} \to \text{dépôt}}}{d_{\text{max}}} = 1 - \frac{d}{\text{max distance fournisseur-dépôts}}
$$

### 2.2 Fonction Score Multicritères Pondérée

$$
\text{Score}_{\text{dépôt}} = 0,40 \times U + 0,30 \times P + 0,20 \times V + 0,10 \times D
$$

**Poids justifiés :**
- U (40%) : Urgence = facteur dominant pour satisfaction client
- P (30%) : Pénalité = impact coûts direct très mesurable
- V (20%) : Volume = facteur économique transport
- D (10%) : Distance = "bruit", moins critique que 3 premiers

### 2.3 Règles de Décision Basées Score

**Interprétation Score :**

```
Score ≥ 0,75 : URGENCE CRITIQUE
├─ Livrer ce dépôt en direct
├─ Chauffeur interne si < 48h urgence
├─ Affrètement Médiafret si urgent absolu
└─ Autres dépôts → navette + hub relais

Score 0,50-0,75 : URGENCE MOYENNE
├─ Hub régional (transbordement acceptable)
├─ Navette redistribution J+2 acceptable
└─ Économies consolidation prioritaires

Score < 0,50 : PAS URGENCE
├─ Regroupement consolidé (J+2-3)
├─ Maximiser utilisation chauffeur (tournée multi-clients)
└─ Coûts minimaux (-70% vs affrètement direct)
```

**Exemple Score Comparatif (3 cas types):**

```
CAS A : Client Urgent (Chantier bloqué, pénalité 1 000€/jour)
──────────────────────────────────────────────────────────
U = 0,98 (délai 24h)
P = 0,50 (1000 / 2000)
V = 0,75 (15t / 20t)
D = 0,35 (distance fournisseur moyen)

Score_A = 0,40(0,98) + 0,30(0,50) + 0,20(0,75) + 0,10(0,35)
        = 0,392 + 0,15 + 0,15 + 0,035 = 0,727 ★★ MOYEN-HAUT

Action : Livrer en direct (score borderline, mais urgence + pénalité poussent)

CAS B : Client Standard (Inventaire renew, pas urgence)
─────────────────────────────────────────────────────
U = 0,60 (délai 72h)
P = 0,0 (pas pénalité)
V = 0,25 (5t / 20t)
D = 0,70 (distance fournisseur très proche)

Score_B = 0,40(0,60) + 0,30(0,0) + 0,20(0,25) + 0,10(0,70)
        = 0,24 + 0 + 0,05 + 0,07 = 0,36 ★ BAS

Action : Hub régional ou regroupement (pas urgence, coûts priori)

CAS C : Client Flexible (Pas urgence, volume moyen, distance courte)
────────────────────────────────────────────────────────────────────
U = 0,70 (délai 60h, medium)
P = 0,10 (pénalité 200€/jour)
V = 0,50 (10t / 20t)
D = 0,80 (très proche fournisseur)

Score_C = 0,40(0,70) + 0,30(0,10) + 0,20(0,50) + 0,10(0,80)
        = 0,28 + 0,03 + 0,10 + 0,08 = 0,49 ★ LIMITE BAS

Action : Navette interne prioritaire (distance très proche) ou regroupement
```

---

## 3. ALGORITHME VRP TOURNÉE - OPTIMISATION ITINÉRAIRE GEDIMAT

### 3.1 Problème VRP Appliqué Milkrun Île-de-France

**Données entrée :**
```
Fournisseurs :
├─ Émerge (Évreux) : 15t tuiles
├─ Saint-Germaire (Val-d'Oise) : 10t accessoires
├─ Leroy Merlin (Île-de-France) : 8t divers

Destinations dépôts :
├─ Lieu (271400) : 1 000m² distance
├─ Méru (60110) : 50km distance
├─ Breuilpont (27xxx) : 80km distance

Capacité véhicule : 25t (camion PL)
Contrainte temps : 480 min/jour (8 heures)
Fenêtre Départ : 8h00 (collecte fournisseurs)
Fenêtre Retour : 16h30 (fin travail chauffeur)
```

**Formule distance euclidienne (approximé) :**

$$
D_{\text{route}} = \sum_{i=0}^{n} \sqrt{(x_i - x_{i+1})^2 + (y_i - y_{i+1})^2}
$$

**Pour Gedimat (coordonnées approx):**
```
Évreux      (x=0, y=0)
Val-d'Oise  (x=30, y=20)
Île-de-France (x=50, y=30)
Lieu        (x=-20, y=-10)
Méru        (x=15, y=50)
Breuilpont  (x=-5, y=-30)

Distance Évreux-Val-d'Oise = √((30-0)² + (20-0)²) = √(900+400) = 36 km
Distance Val-d'Oise-IDF = √((50-30)² + (30-20)²) = √(400+100) = 22 km
Distance IDF-Lieu = √((-20-50)² + (-10-30)²) = √(4900+1600) = 80 km
Distance Lieu-Méru = √((15-(-20))² + (50-(-10))²) = √(1225+3600) = 69 km
Distance Méru-Breuilpont = √((-5-15)² + (-30-50)²) = √(400+6400) = 82 km
Distance Breuilpont-Évreux (retour) = √((0-(-5))² + (0-(-30))²) = √(25+900) = 30 km
```

### 3.2 Séquençage Optimal (Nearest Neighbor Heuristique)

**Algorithme glouton (nearest neighbor) :**

```
Départ Évreux (08h00)
│
├─ Voiture vers fournisseur PLUS PROCHE : Val-d'Oise (36 km)
│  Collecte Saint-Germaire (10t) : 25 min
│  Cumul : 36 km, 25 min, 10 tonnes
│
├─ Vers fournisseur PLUS PROCHE restant : Île-de-France (22 km de Val-d'Oise)
│  Collecte Leroy Merlin (8t) : 20 min
│  Cumul : 58 km, 45 min, 18 tonnes
│
├─ Retour vers Évreux pour Émerge (Impossible, autres fournisseurs = "ancrage")
│  Alternative : Collecte in-situ
│  Distance Île-de-France → Évreux : ~50 km
│  ✗ Total trajet = 108 km > 100 km max pour timing
│
REROUTE : Collecte Émerge AVANT Val-d'Oise
─────────────────────────────────────────────
Départ Évreux (08h00)
├─ Collecte Émerge (15t) : 30 min
├─ Route Évreux → Val-d'Oise (36 km) : 45 min
├─ Collecte Saint-Germaire (10t) : 25 min
├─ Route Val-d'Oise → Île-de-France (22 km) : 25 min
├─ Collecte Leroy Merlin (8t) : 20 min
├─ TOTAL = 33t (>25t capacité) → SURCHARGE !
```

**Optimal = 2 véhicules ou split 2 tournées :**

```
TOURNÉE 1 (Chauffeur 1) : Émerge + Saint-Germaire
──────────────────────────────────────────────
Départ 08h00
├─ Évreux → Collecte Émerge (15t) : 30 min
├─ Route Évreux → Val-d'Oise (36 km) : 45 min
├─ Collecte Saint-Germaire (10t) : 25 min
├─ Total poids : 25t (capacité max) ✓
├─ Route Val-d'Oise → Dépôts Gedimat
│   - Arrivée Lieu (80 km de Val-d'Oise) : 1h20
│   - Décharge 25t : 1h30
├─ Retour Parc : 16h30
├─ TOTAL DURÉE : 8h30 (acceptable, <9h max)
└─ TOTAL DISTANCE : ~150 km

TOURNÉE 2 (Chauffeur 2) : Leroy Merlin + redistribution
────────────────────────────────────────────────
Départ 09h00 (offset pour éviter congestion)
├─ Île-de-France → Collecte Leroy Merlin (8t) : 20 min
├─ Dépôt Lieu (80 km) : 1h20
├─ Décharge 8t : 30 min
├─ Navette Lieu → Méru (45 km) : 1h [optional, peut être navette régulière]
├─ Retour Parc : 15h30
├─ TOTAL DURÉE : 7h (confortable)
└─ TOTAL DISTANCE : ~170 km

OU ALTERNATIVE : Regrouper 1 chauffeur + assistance décharge
───────────────────────────────────────────────────────────
1 chauffeur + 1 assistant décharge (coût +40€)
Tournée unique Émerge + Saint-Germaire + Leroy Merlin (2 trajets)
Coût supplémentaire assistance : 40€
Gain consolidation : +200€
NET : +160€ économies
```

---

## 4. COMPARAISON COÛTS : FORMULES DÉTAILLÉES

### 4.1 Formule Coût Affrètement Médiafret (Baseline)

$$
C_{\text{affrètement}} = C_{\text{base}} + C_{\text{distance}} + C_{\text{surcharge volume}} + C_{\text{manutention}}
$$

$$
= 150€ + (D_{\text{km}} \times 6,50€/km) + \begin{cases}
0,30 \times \text{base} & \text{if } q < 10t \\
0 & \text{if } q \geq 10t
\end{cases} + 150€
$$

**Exemple 10 cas Gedimat :**

| Tonnage | Distance | Coût Affrètement | Coût/tonne |
|---------|----------|---|---|
| 5t | 30km | 150 + 195 + 104 + 150 = **599€** | 119€/t |
| 10t | 30km | 150 + 195 + 0 + 150 = **495€** | 49,5€/t |
| 15t | 80km | 150 + 520 + 0 + 150 = **820€** | 54,6€/t |
| 20t | 50km | 150 + 325 + 0 + 150 = **625€** | 31,2€/t |

### 4.2 Formule Coût Chauffeur Interne (Direct ou Navette)

$$
C_{\text{chauffeur}} = C_{\text{fixe}} + C_{\text{variable\_km}} + C_{\text{manutention}}
$$

$$
= 100€ + (0,30€/km \times D_{\text{km}}) + (24,20€/h \times T_{\text{décharge}})
$$

**Ou version marginal (navette):**

$$
C_{\text{navette}} = C_{\text{variable\_km}} + C_{\text{manutention marginal}}
$$

$$
= (0,50€/km \times D_{\text{km}}) + (4,20€/h \times T_{\text{redistribution}})
$$

**Justification "coût marginal" navette :**
- Chauffeur salaire = fixe (payé quoiqu'il advienne)
- Carburant supplémentaire = seul coût additionnel
- À 80km/h sur 50km, consommation supp. = 0,50€/km × 50km = 25€ ✓

---

## 5. TABLEAUX SEUILS OPÉRATIONNELS (POCHE PLASTIFIÉE)

### 5.1 Matrice Décision Rapide Chauffeur vs Navette vs Regroupement

```
╔════════════════════════════════════════════════════════════════════╗
║                  SEUILS VRP GEDIMAT 2025                          ║
║              (Plastifier et garder dans véhicule)                 ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  DISTANCE  TONNAGE  DÉLAI   NB DÉPÔTS  → DÉCISION  COÛT/T         ║
║  ──────────────────────────────────────────────────────────────  ║
║                                                                    ║
║  < 20km    any      any     any        → NAVETTE   1-3 €/t ✓✓✓   ║
║                                                                    ║
║  > 20km    > 14t    < 48h   any        → CHAUFFEUR 10-12 €/t ✓✓   ║
║                                        direct urgent              ║
║                                                                    ║
║  > 20km    > 14t    ≥ 48h   1          → CHAUFFEUR 12-18 €/t ✓✓   ║
║                                        direct optimisé            ║
║                                                                    ║
║  > 20km    10-14t   ≥ 48h   2+         → REGROUPEM 6-10 €/t ✓✓✓   ║
║                                        consolidé                  ║
║                                                                    ║
║  > 20km    < 10t    ≥ 48h   any        → HUB REG.  10-15 €/t ✓✓   ║
║                                        + navette                  ║
║                                                                    ║
║  > 20km    any      < 48h   any        → AFFRÈTM   40-70 €/t ✗    ║
║                              + urgence externe (dernier recours)  ║
║                                                                    ║
║  Clé : Priorité URGENCE > VOLUME > PROXIMITÉ                      ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
```

### 5.2 Calcul Coût 30 Secondes (Formules Simplifiées)

```
┌─────────────────────────────────────────────────────────────────┐
│            FORMULES RAPIDES ESTIMATION COÛTS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  NAVETTE : (25€ + 0,50€/km × distance) ÷ tonnage                │
│  Exemple : (25 + 0,50 × 50) ÷ 15t = 37,50 ÷ 15 = 2,50 €/t      │
│                                                                   │
│  CHAUFFEUR DIRECT : (100€ + 0,30€/km × distance) ÷ tonnage      │
│  Exemple : (100 + 0,30 × 80) ÷ 15t = 124 ÷ 15 = 8,27 €/t       │
│                                                                   │
│  HUB RÉGIONAL : (CHAUFFEUR vers hub + navette retour) ÷ tonnage │
│  Exemple : [(100 + 0,30×30) + (25€ nav)] ÷ 20t = 159 ÷ 20 = 7,95€/t
│                                                                   │
│  REGROUPEMENT (tournée multi-clients) :                         │
│  [(200€ chauffeur + 0,30€/km × 150km) ÷ nb_clients] ÷ vol_moy   │
│  Exemple 3 clients, 38t total : (245€ ÷ 3) ÷ 12,67t = 6,45€/t   │
│                                                                   │
│  AFFRÈTEMENT MÉDIAFRET (À ÉVITER) :                             │
│  (150€ + 6,50€/km × distance + surcharge volume) ÷ tonnage      │
│  Exemple 15t, 80km : (150 + 520) ÷ 15 = 44,67 €/t              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. ÉTUDE CAS : GEDIMAT CONSOLIDATION 1 SEMAINE RÉELLE

### 6.1 Simulation Semaine Type (15 commandes fournisseurs)

**Données entrée semaine N :**

```
CMD #1 : Émerge Tuiles (15t Méru + 5t Gisors) - Urgence 8/10
CMD #2 : Saint-Germaire (10t Méru) - Urgence 4/10
CMD #3 : BigMat (12t Lieu) - Urgence 5/10
CMD #4 : Leroy Merlin (8t Breuilpont) - Urgence 3/10
CMD #5 : Ciments Lafarge (25t Lieu) - Urgence 6/10
...
Total 15 commandes = 127t fournisseurs
```

**Application scoring + regroupement :**

```
REGROUPEMENT 1 : Émerge + Saint-Germaire (Île-de-France triangle)
──────────────────────────────────────────────────────────────
Tonnage : 30t (15 Émerge + 5 Gisors + 10 Saint-Germaire)
Délai : J+2 flexible
Coût regroupement : 310€ chauffeur + 60€ navette = 370€
Coûts isolés : 1 400€ (3 enlèvements affrètement)
ÉCONOMIE : 1 030€ (-73,6%)

REGROUPEMENT 2 : BigMat + Leroy Merlin (décentrés, petit vol)
──────────────────────────────────────────────────────────────
Tonnage : 20t (12 Lieu + 8 Breuilpont)
Délai : J+3 flexible
Coût regroupement : 280€ chauffeur + 40€ navette = 320€
Coûts isolés : 900€ (2 enlèvements)
ÉCONOMIE : 580€ (-64%)

COMMANDES ISOLÉES : Lafarge 25t (volume, urgence)
───────────────────────────────────────────────
Tonnage : 25t
Urgence score : 0,68 (médium, priorité Lieu)
Décision : Chauffeur interne direct (si disponible) sinon affrètement
Coût chauffeur : 150€ + (100 km × 0,30) = 180€
Coût affrètement : 800€
→ Chauffeur choisi (économie 620€)

TOTAL SEMAINE 7 COMMANDES
──────────────────────────
Coûts sans optimisation (7 affrètements isolés) : 4 800€
Coûts optimisé (3 regroupements + 1 chauffeur) : 870€
ÉCONOMIE SEMAINE : 3 930€

ANNUEL (52 semaines) : 3 930 × 52 = **204 360€ économie potentielle**

(Note : conservateur, réalité ~50-100k€ dû à cas non-optimisables)
```

---

## CONCLUSION - GUIDE D'UTILISATION OPÉRATIONNELLE

### Procédure Quotidienne Angelique & Planificateurs

```
À CHAQUE NOUVELLE COMMANDE > 5 tonnes :

1. COLLECTER DONNÉES (1 min)
   └─ Poids, dépôts, fournisseur, délai client, pénalité jour

2. CALCULER SCORE DÉPÔT (3 min, Excel)
   └─ Score = 0,40×U + 0,30×P + 0,20×V + 0,10×D

3. DÉCIDER TRANSPORT (2 min)
   └─ IF score > 0,75 → Livrer ce dépôt direct
   └─ ELSE IF 0,50-0,75 → Hub régional
   └─ ELSE → Regroupement consolidé

4. EXÉCUTER & TRACER (1 min)
   └─ Émettre commande transporteur
   └─ Logger coût + délai réel pour suivie mensuel

TOTAL : 7 minutes par commande vs 15 min ad-hoc (−53% temps)
COÛTS TRANSPORT : -35% à -70% selon applicabilité
```

---

**Fin d'annexe technique VRP – Document confidentiel Gedimat**
