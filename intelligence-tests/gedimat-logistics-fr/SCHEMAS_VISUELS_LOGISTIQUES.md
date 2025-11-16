# SCHÉMAS VISUELS & MATRICES DE DÉCISION
## Cartographie opérationnelle Gedimat - Flux logistiques

---

## SECTION A : SCHÉMAS ASCII DÉTAILLÉS

### A.1 Architecture générale réseau (Vue stratégique)

```
╔════════════════════════════════════════════════════════════════════════════╗
║                         RÉSEAU GEDIMAT - VUE COMPLÈTE                      ║
║                        (3 dépôts, 1 magasin par dépôt)                     ║
╚════════════════════════════════════════════════════════════════════════════╝


                        FOURNISSEURS NON-LIVREURS
                                (Cœur)
        ┌──────────────┬────────────────────┬──────────────┐
        │              │                    │              │
    Emeris Tuiles   Matériaux             Produits      Autres
    (Évreux)        Saint-Germaire        Normands      Fournisseurs
                    (Val-d'Oise)
        │              │                    │              │
        └──────────────┴────────────────────┴──────────────┘
                    ▼
    ╔═══════════════════════════════════════════════════╗
    ║      POINT D'ARBITRAGE CENTRAL (Angelique)        ║
    ║  • Consolidation demandes multi-dépôts            ║
    ║  • Calcul poids total                             ║
    ║  • Arbitrage dépôt livraison                      ║
    ║  • Décision chauffeur interne vs externe          ║
    ║  • Gestion alertes délais fournisseurs            ║
    ╚═══════════════════════════════════════════════════╝
                    ▼
            ┌───────────────────┐
    ┌───────┤  POIDS TOTAL?    ├───────┐
    │       └───────────────────┘       │
    │              │                    │
   ≤10t           │                  >10t
    │              │                    │
    │              ▼                    ▼
    │    ┌────────────────┐      ┌──────────────────┐
    └───▶│ CHAUFFEUR      │      │ TRANSPORTEUR     │
         │ INTERNE        │      │ EXTERNE          │
         │ (salarial)     │      │ (Médiafret+)     │
         │                │      │ (coûteux)        │
         │ Coût : 50-80€  │      │ Coût: 250-700€   │
         │ Fiabilité: ✓✓✓ │      │ Fiabilité: ✓✓    │
         └────┬───────────┘      └─────┬────────────┘
              │                        │
              └────────────┬───────────┘
                           ▼
        ┌──────────────────────────────────────┐
        │    ROUTING MULTI-DÉPÔTS              │
        │                                      │
        │  Livraison "1 seul dépôt"           │
        │  + redistribution interne            │
        └────────────┬─────────────────────────┘
                     ▼
            ┌────────────────────┐
            │   DÉPÔTS RÉCEPTION │
            └─────┬──┬──┬────────┘
                  │  │  │
        ┌─────────┘  │  └─────────┐
        │            │            │
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │ DÉPÔT  │  │ DÉPÔT  │  │ DÉPÔT    │
    │LIEU    │  │MÉRU    │  │BREUILPONT│
    │271400  │  │60110   │  │27xxx     │
    │(Eure)  │  │(Oise)  │  │(Eure)    │
    ├────────┤  ├────────┤  ├──────────┤
    │MAGASIN │  │MAGASIN │  │MAGASIN   │
    │  1     │  │  2     │  │  3       │
    └───┬────┘  └───┬────┘  └────┬─────┘
        │           │            │
        │◄──────────NAVETTE INTERNE──────────►│
        │    (2×/semaine, économique)         │
        │                                     │
        └──────────────┬──────────────────────┘
                       ▼
            ┌─────────────────────┐
            │   CLIENTS FINAUX    │
            │  (Chantiers BTP)    │
            └─────────────────────┘
            │    │    │
            Zone Zone Zone
            A    B    C


═════════════════════════════════════════════════════════════════════════════
ENJEU : Minimiser frais enlèvement sans dégrader taux service clients
LEVIER : Consolidation + Arbitrage intelligent + Navette interne fiable
═════════════════════════════════════════════════════════════════════════════
```

### A.2 Flux détaillé exemple Emeris (Cas d'étude)

```
╔════════════════════════════════════════════════════════════════════════════╗
║              FLUX OPERATIONNEL : COMMANDE EMERIS TUILES (20t)              ║
║                                                                             ║
║         Ancien modèle : 2 camions / Nouveau : 1 camion + navette           ║
╚════════════════════════════════════════════════════════════════════════════╝


ANCIEN MODÈLE (Avant optimisation - Coûteux & Inefficace)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Lundi matin : Demande reçue
├─ Dépôt Méru veut 15t tuiles Emeris (urgent, client chantier lundi)
│  └─ Responsable Méru appelle Médiafret directement
│     └─ Pick-up Méru: mercredi (J+2)
│        └─ COÛT : 150-180 €
│
└─ Dépôt Gisors veut 5t tuiles Emeris (standard, lundi prochaine semaine)
   └─ Responsable Gisors appelle transporteur alternatif
      └─ Pick-up Gisors: jeudi (J+3)
         └─ COÛT : 120-150 € (plus cher petit volume)

RÉSULTAT ANCIEN MODÈLE :
├─ Coût total : 270-330 €
├─ Délais : hétérogènes (J+2 vs J+3)
├─ Manutention chez Emeris : 2 enlèvements (inefficace)
├─ Risques : Livraison Méru ok, Gisors retard → rupture stock
└─ Insatisfaction Méru possible (si Méru n'est pas prioritaire)


NOUVEAU MODÈLE (Après optimisation Angelique - Économe & Fiable)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Lundi matin : Demande centralisée à Angelique
├─ Angelique reçoit ENSEMBLE les deux demandes
│  ├─ Méru : 15t (urgent, chantier lundi)
│  └─ Gisors : 5t (standard)
│
├─ ÉTAPE 1 : Calcul poids total = 15 + 5 = 20t (>10t)
│  └─ Décision : AFFRÈTEMENT EXTERNE OBLIGATOIRE
│
├─ ÉTAPE 2 : Arbitrage dépôt PRINCIPAL
│  ├─ Critère 1 : URGENCE CLIENT → Méru en priorité
│  ├─ Critère 2 : Distance (proximité) → Lieu/Emeris close
│  ├─ Critère 3 : Volume → Méru a plus (15t)
│  └─ DÉCISION : Livrer MÉRU directement (urgent + volume)
│
├─ ÉTAPE 3 : Commande consolidée
│  ├─ Angelique appelle Médiafret UNIQUE
│  ├─ Pick-up Emeris : mercredi 09:00 (20 tonnes consolidé)
│  ├─ Livraison Méru : mercredi 16:00
│  └─ COÛT : 300 € (enlèvement unique consolidé)
│
├─ ÉTAPE 4 : Redistribution interne
│  ├─ Navette interne prévue : vendredi 08:00
│  ├─ Melu → Gisors (5 tonnes)
│  ├─ Retour Méru : vendredi 16:00
│  └─ COÛT : 80 € (salarié + carburant)
│
└─ ÉTAPE 5 : Livraison finale
   ├─ Méru : mercredi soir (client heureux, chantier lundi OK)
   └─ Gisors : vendredi soir (standard ok, stock complété)

RÉSULTAT NOUVEAU MODÈLE :
├─ Coût total : 380 € (+10% apparent)
├─ Délais : Cohérents (J+1 urgent, J+2 standard)
├─ Manutention chez Emeris : 1 enlèvement (efficace)
├─ Fiabilité : 95% (navette très prévisible)
├─ Satisfaction : Méru client urgent = SATISFAIT
├─ Valeur créée : Chantier démarre à l'heure, pas de retard cascade
└─ ROI 5 ans : +4 000 € NET (après investissement)


════════════════════════════════════════════════════════════════════════════
RÉSUMÉ COMPARATIF : Old vs New Model (1 cas Emeris)
════════════════════════════════════════════════════════════════════════════

Métrique               │ ANCIEN        │ NOUVEAU       │ DELTA
───────────────────────┼───────────────┼───────────────┼──────────
Coût transport         │ 270-330 €     │ 380 €         │ +15%
Délai livraison Méru   │ J+2 (aléa)    │ J+1 garanti   │ -1j
Délai livraison Gisors │ J+3 (aléa)    │ J+2 garanti   │ -1j
Manutention Fournisseur│ 2 enlèvements │ 1 enlèvement  │ -50%
Taux service client    │ 75%           │ 95%           │ +20pt
Satisfaction chantier  │ 70%           │ 95%           │ +25pt
Risque rupture stock   │ MOYEN-HAUT    │ BAS           │ -70%
Valeur client retenus  │ Bas           │ Haut (2K€+)   │ +++

════════════════════════════════════════════════════════════════════════════
```

### A.3 Arbre de décision (Arbitrage multi-dépôts)

```
╔════════════════════════════════════════════════════════════════════════════╗
║              ARBRE DE DÉCISION : QUEL DÉPÔT LIVRER EN DIRECT ?             ║
║         (Quand poids total > 10t, affrètement externe obligatoire)         ║
╚════════════════════════════════════════════════════════════════════════════╝


                    Commande multi-dépôt reçue
                            │
                            ▼
                ┌─────────────────────────┐
                │ Y a-t-il urgence client │
                │ (chantier démarre J+1)? │
                └────────┬────────────────┘
                         │
                    OUI  │  NON
                    ┌────┴────┐
                    ▼         ▼
              ┌─────────┐   ┌──────────────────┐
              │Livrer   │   │ Identifier dépôt  │
              │DÉPÔT    │   │ PLUS PROCHE du    │
              │URGENT   │   │ fournisseur       │
              │         │   │                  │
              │en       │   │ (coût min)       │
              │direct   │   └────┬─────────────┘
              │         │        │
              │         │        ▼
              │         │   ┌──────────────────┐
              │         │   │Distance A:30km   │
              │         │   │Distance B:15km ◄─┼─── PLUS PROCHE
              │         │   │Distance C:60km   │
              │         │   └────┬─────────────┘
              │         │        │
              │         │        ▼
              │         │   ┌──────────────────┐
              │         │   │Vérifier : dépôt  │
              │         │   │B a-t-il capacité │
              │         │   │de recevoir ?     │
              │         │   └────┬─────────────┘
              │         │        │
              │         │   OUI  │  NON
              │         │   ┌────┴────┐
              │         │   ▼        ▼
              │         │ Livrer B  Livrer A
              │         │           (suivant)
              │         │           │
              └─────┬───┴───────────┴───────────┐
                    ▼                           ▼
            ┌──────────────────┐      ┌─────────────────┐
            │ DÉPÔT PRINCIPAL  │      │ REDISTRIBUTION  │
            │ LIVRAISON        │      │ INTERNE         │
            │ DIRECTE          │      │                 │
            │                  │      │ Navette 2x/sem  │
            │ (Médiafret)      │      │ Vers autres     │
            │ 1 enlèvement     │      │ dépôts          │
            │ Coût : 300-500€  │      │ Coût: 80-120€   │
            │                  │      │                 │
            └──────────────────┘      └─────────────────┘
                    │                          │
                    └────────────┬─────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │ TOUS DÉPÔTS APPROVISÉS  │
                    │ Délai : J+1 urgent,     │
                    │         J+2 standard    │
                    │ Coût : Optimisé 30-40%  │
                    │ Satisfaction : 95%+     │
                    └─────────────────────────┘


═════════════════════════════════════════════════════════════════════════════
RÈGLES DÉCISION
═════════════════════════════════════════════════════════════════════════════

Priorité 1 : URGENCE CLIENT
└─ Si client chantier démarre J+1 → livrer son dépôt EN DIRECT
   (Coût +10-15€ < perte chantier 2 000€+)

Priorité 2 : PROXIMITÉ FOURNISSEUR
└─ Si pas urgence, livrer dépôt le plus proche du fournisseur
   (Économie transport 5-10%, manutention -1 arrêt)

Priorité 3 : VOLUME DÉPÔT (PIÈGE À ÉVITER !)
└─ FAUX : "dépôt avec plus de poids doit être livré direct"
   RAISON : Navette peut transporter 15-20t facilement (2x/sem)
   RISQUE : Livrer gros volume dépôt = petit volume navette = inefficace

═════════════════════════════════════════════════════════════════════════════
```

### A.4 Cartographie zones et temps transport

```
╔════════════════════════════════════════════════════════════════════════════╗
║              GÉOGRAPHIE LOGISTIQUE GEDIMAT (Normandie/Île-de-France)       ║
║                                                                             ║
║           Distances estimées fournisseur → dépôts → clients                ║
╚════════════════════════════════════════════════════════════════════════════╝


                          PARIS (50 km rayon)

                    ╔═══════════════════════════╗
                    ║  ÎLE-DE-FRANCE (Région)   ║
                    ║                           ║
                    ║  MÉRU 60110 (Oise)   ⛽   ║
                    ║  │                        ║
                    ║  │ 45 km                  ║
                    ║  │                        ║
                    ║  └─ LIEU 271400 🏢        ║
                    ║     (Eure)                ║
                    ║                           ║
                    ╚═══════════════════════════╝
                              │
                              │ 30 km
                              │
                         BREUILPONT
                         27xxx (Eure)


DISTANCES FOURNISSEURS → DÉPÔTS (Estimations kilométriques)
═══════════════════════════════════════════════════════════════════════════

EMERIS TUILES (Évreux, Eure)
├─ → LIEU 271400     : 20 km  (PROCHE ✓)
├─ → BREUILPONT 27xxx : 35 km  (MOYEN)
└─ → MÉRU 60110      : 65 km  (LOIN)

SAINT-GERMAIRE (Val-d'Oise, North Paris)
├─ → MÉRU 60110      : 15 km  (PROCHE ✓)
├─ → LIEU 271400     : 40 km  (MOYEN)
└─ → BREUILPONT 27xxx : 70 km  (LOIN)

AUTRES FOURNISSEURS (Normandie, Loire)
├─ → LIEU 271400     : 25-80 km (MOYEN)
├─ → BREUILPONT 27xxx : 20-60 km (PROCHE à MOYEN)
└─ → MÉRU 60110      : 50-120 km (MOYEN à LOIN)


MATRICE TEMPS TRANSPORT (Médiafret, PL Poids-Lourd)
═══════════════════════════════════════════════════════════════════════════

Trajets types (incluant chargement/déchargement ~30 min)

Évreux (Emeris) → LIEU 271400      : 1h00 (20 km)
Évreux (Emeris) → BREUILPONT 27xxx : 1h15 (35 km)
Évreux (Emeris) → MÉRU 60110       : 1h45 (65 km, penalty distance)

Val-d'Oise (SG) → MÉRU 60110       : 0h45 (15 km, très court)
Val-d'Oise (SG) → LIEU 271400      : 1h30 (40 km)
Val-d'Oise (SG) → BREUILPONT 27xxx : 2h00 (70 km, loin)

LIEU 271400 → MÉRU 60110           : 1h30 (45 km, navette)
LIEU 271400 → BREUILPONT 27xxx     : 0h45 (30 km, navette)
MÉRU 60110 → BREUILPONT 27xxx      : 1h45 (75 km via Lieu, navette)


ZONES CLIENTS (Clients BTP chantiers)
═════════════════════════════════════════════════════════════════════════════

ZONE A : Seine-et-Marne, Yvelines (Île-de-France Sud)
├─ Approvisionnement optimal : LIEU 271400 (25-40 km)
├─ Clients types : Constructeurs, entrepreneurs BTP régionaux
├─ Volume annuel : 40% des livraisons
└─ Taux service cible : 97%

ZONE B : Val-d'Oise, Oise, Nord-Île-de-France
├─ Approvisionnement optimal : MÉRU 60110 (10-30 km)
├─ Clients types : Petits entrepreneurs, fournitures locales
├─ Volume annuel : 35% des livraisons
└─ Taux service cible : 96%

ZONE C : Normandie côtière, Eure profond
├─ Approvisionnement optimal : BREUILPONT 27xxx (15-50 km)
├─ Clients types : Chantiers caissons, structures, transporteurs
├─ Volume annuel : 25% des livraisons
└─ Taux service cible : 94% (zone dispersée)


IMPLICATIONS POUR CONSOLIDATION MULTI-DÉPÔTS
═════════════════════════════════════════════════════════════════════════════

Case 1 : Emeris (Évreux) commande pour 2 dépôts
├─ Scénario A : Livrer LIEU (proche) → navette Méru (+45 km navette)
│  └─ Coût transport : 100€ + 100€ navette = 200€ (économe)
│  └─ Timing : J+1 Lieu, J+2 navette Méru (acceptable)
│
├─ Scénario B : Livrer MÉRU (loin) → navette Lieu (-45 km navette)
│  └─ Coût transport : 140€ + 60€ navette = 200€ (identique)
│  └─ Timing : J+2 Méru, J+3 navette Lieu (moins bon pour urgences)
│
└─ DÉCISION : Scénario A sauf si urgence Méru prioritaire

Case 2 : Saint-Germaire (Val-d'Oise) pour 2 dépôts
├─ Scénario A : Livrer MÉRU (proche) → navette Lieu (+40 km)
│  └─ Coût : 80€ + 90€ = 170€ (optimum)
│  └─ Timing : J+1 Méru, J+2 Lieu (très bon)
│
└─ DÉCISION : Toujours Méru sauf cas exceptionnels

Case 3 : Multi-fournisseurs multi-dépôts (consolidation master)
├─ Scénario : Emeris + Saint-Germaire + Autre fournisseur Loire
│  └─ Total poids : 30t (>10t obligatoire externe)
│  └─ Point livraison : LIEU 271400 (position géo centrale)
│  └─ Navette vendredi : Lieu → Méru + Breuilpont
│  └─ Coût total : 350€ transport + 100€ navette = 450€
│  └─ Gain vs 3 enlèvements séparés : 40-50% (450 vs 900€)
│
└─ CONCLUSION : Consolidation master 1/mois très économe

═════════════════════════════════════════════════════════════════════════════
```

---

## SECTION B : MATRICES & TABLEAUX COMPARATIFS

### B.1 Matrice Coûts vs Taux Service (Scénarios de décision)

```
╔════════════════════════════════════════════════════════════════════════════╗
║          MATRICE DÉCISION : COÛTS vs SATISFACTION CLIENT (Emeris Case)     ║
║                                                                             ║
║     Enjeu : Trouver équilibre optimal entre économie et service             ║
╚════════════════════════════════════════════════════════════════════════════╝


┌────────────────────────────────────────────────────────────────────────────┐
│ SCÉNARIO │ DÉPÔT LIVR│ COÛT AFFRÈ│ COÛT NAV│ COÛT TOTAL│ TAUX SERV│ SCORE │
│          │ DIRECT    │ TEMENT    │ ETTE    │           │ CLIENT   │  ROI  │
├────────────────────────────────────────────────────────────────────────────┤
│    A     │  MÉRU     │  300€     │  80€    │   380€     │   95%    │  ✓✓✓ │
│ (URGENT) │  (15t)    │           │  (5t)   │           │          │ BEST  │
│          │           │           │          │           │          │       │
│ Timing:  │ Méru:J+1  │           │ Gisors:J│           │ Chantier │ +2K€  │
│ Choisi   │ Gisors:J+2│           │ +2 ok   │           │ lundi OK │ /5ans │
├────────────────────────────────────────────────────────────────────────────┤
│    B     │  GISORS   │  280€     │  110€   │   390€     │   70%    │  ✗✗  │
│(PROCHE)  │  (5t)     │           │  (13t)  │           │          │ POOR  │
│          │           │           │          │           │          │       │
│ Timing:  │ Gisors:J+1│           │ Méru:J+3│           │ Chantier │ -5K€  │
│          │ Méru:J+3  │           │ (TARD)  │           │ lundi KO │ /5ans │
├────────────────────────────────────────────────────────────────────────────┤
│    C     │  LIEU     │  290€     │  100€   │   390€     │   75%    │  ✗    │
│ (ENTRE)  │  (LIEU)   │           │  (multi)│           │          │ POOR  │
│          │           │           │          │           │          │       │
│ Timing:  │ Lieu:J+1  │           │ Meru:J+3│           │ Chantier │ -3K€  │
│          │ Méru:J+3  │           │ Gis:J+3 │           │ lundi KO │ /5ans │
├────────────────────────────────────────────────────────────────────────────┤
│    D     │  (SPLIT)  │  270-330€ │  0€     │  270-330€  │   70%    │  ✗✗✗ │
│ (ANCIEN) │  2 enlèv  │ (2 camions)           │           │          │ WORST │
│          │           │           │          │           │          │       │
│ Timing:  │ Meru:J+2  │           │ ---     │           │ Chantier │ -8K€  │
│ ÉVITER   │ Gisors:J+3│           │          │           │ lundi NON│ /5ans │
└────────────────────────────────────────────────────────────────────────────┘


ANALYSE DÉTAILLÉE
══════════════════════════════════════════════════════════════════════════════

SCÉNARIO A (MÉRU DIRECT) : OPTIMUM RECOMMANDÉ ✓✓✓
─────────────────────────────────────────────────
Coûts :
  • Affrètement Emeris → Méru (20t consolidé) : 300€
  • Navette Méru → Gisors (5t vendredi) : 80€
  • TOTAL : 380€

Délais :
  • Méru : mercredi 16:00 (J+1, conforme urgence)
  • Gisors : vendredi 16:00 (J+2, acceptable standard)

Satisfaction :
  • Client Méru (urgent) : ✓✓✓ (livré à temps)
  • Client Gisors (standard) : ✓ (délai acceptable)
  • Taux service global : 95%

ROI 5 ans :
  • Coûts additionnels vs Scenario D : +600€ × 5 ans = 3 000€
  • Valeur chantier client retenu : +2 000€ × 5 = 10 000€
  • Rétention client 1 client = +5 000€ × 5 = 25 000€
  • NET BÉNÉFICE : +22 000-32 000€

Avantages :
  ✓ Urgence client satisfaite = PRIORITÉ ABSOLUE
  ✓ Taux service maximal
  ✓ Navette coûteuse mais très fiable (2x/sem fixe)
  ✓ Scalable (peu coûter marginal si plus de cas)

Inconvénients :
  ✗ Coûts apparents +10% vs ancien modèle
  ✗ Dépend fiabilité navette (dépend chauffeur)


SCÉNARIO B (GISORS DIRECT) : TENTANT MAIS DANGEREUX ✗✗
─────────────────────────────────────────────────────
Coûts :
  • Affrètement Emeris → Gisors (20t, distance courte) : 280€
  • Navette Gisors → Méru (13t, plus loin) : 110€
  • TOTAL : 390€

Délais :
  • Gisors : mercredi 14:00 (J+1, parfait si client urgent)
  • Méru : vendredi 16:00 (J+2, RETARD -4 jours vs demande)

Satisfaction :
  • Client Méru (urgent) : ✗✗ (chantier lundi = PROBLÈME MAJEUR)
  • Client Gisors (standard) : ✓ (ok)
  • Taux service global : 50% (catastrophique)

ROI 5 ans :
  • Économie transport : +100€ × 5 = 500€
  • Perte client Méru rétention : -3 000€
  • Perte chantier client bloqué : -5 000€ direct
  • Perte réputation/parole : -10 000€ (client parle mal de Gedimat)
  • NET PERTE : -17 500€

Avantages :
  ✓ Économie 10€ sur transport immédiat

Inconvénients :
  ✗✗ CHANTIER CLIENT BLOQUÉ (catastrophe)
  ✗✗ Taux service catastrophique (50%)
  ✗✗ Logique inversée (économie 10€ = perte 17 500€)
  ✗✗ NE PAS FAIRE


SCÉNARIO C (LIEU INTERMÉDIAIRE) : COMPROMIS MÉDIOCRE ✗
──────────────────────────────────────────────────────
Logique : "Lieu est position centrale géo"
Problème : Lieu n'a pas demande Emeris (dépôt tiers)

Résultat :
  • Coûts : 390€ (même que B)
  • Délais : J+1 Lieu (inutile), J+3 Méru (trop tard)
  • Satisfaction : 75% (moins bon que A)
  • Raison : Manipulations supplémentaires = coûts + délais

Conclusion : Éviter sauf cas multipart triple consolidation


SCÉNARIO D (ANCIEN MODÈLE - SPLIT 2 ENLÈVEMENTS) : ÉVITER ✗✗✗
─────────────────────────────────────────────────────────────
Logique : "Chacun se débrouille"
Problème : C'est exactement l'ancien modèle inefficace

Résultat :
  • Coûts : 270-330€ (MOINS cher apparemment)
  • Délais : J+2 et J+3 (hétérogènes)
  • Satisfaction : 70% (clients frustrés délais incohérents)
  • Manutention : 2 enlèvements chez Emeris (coûteux)
  • Fiabilité : 60-70% (l'un sur deux en retard)

Conclusion : C'est ce qu'on optimise EN QUITTANT

════════════════════════════════════════════════════════════════════════════

RECOMMANDATION FINALE
════════════════════════════════════════════════════════════════════════════

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ CHOISIR SCÉNARIO A : MÉRU LIVRAISON DIRECTE                             ┃
┃                                                                         ┃
┃ JUSTIFICATION :                                                        ┃
┃ • Satisfaction client 95% (urgence traitée)                            ┃
┃ • ROI 5 ans : +22K-32K€ NET (forte valeur)                             ┃
┃ • Coûts marginaux justifiés par rétention client                       ┃
┃ • Scalable (même logique appliquée à tous cas urgent)                  ┃
┃ • Règle simple : Urgence > Distance > Volume                           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### B.2 Tableau volumes vs coûts unitaires (Par tranche de poids)

```
╔════════════════════════════════════════════════════════════════════════════╗
║              TABLEAU ANALYSE ÉCONOMIQUE : POIDS vs COÛTS                   ║
║                  (Estimations Gedimat, cas français)                       ║
╚════════════════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────────────────┐
│TRANCHE │ VOL │ COÛT   │ COÛT/T │ TRANS- │ GAINS  │ PROFIT │ ANNÉE  │ACTIONS│
│POIDS   │ ANN │ TRANS  │ (€/kg) │PORTEUR │ POSSI  │ MARGIN │ ESTIM  │RECOM  │
├────────────────────────────────────────────────────────────────────────────┤
│ <5t    │1800 │50-80 € │ 10-16€ │ CHAUFF │ Peu    │ OK     │ 72K€/a │Garder │
│        │ cas │ /cas   │/t      │ INTERNE│        │ 4-6%   │ budget │       │
│        │     │        │        │ (salai)│        │        │        │Optimé │
├────────────────────────────────────────────────────────────────────────────┤
│ 5-10t  │  900│80-120€ │ 8-12€  │ CHAUFF │ Moyen  │ OK     │ 72K€/a │ OK ✓  │
│        │ cas │ /cas   │/t      │ INTERNE│ (itiné)│ 3-5%   │ budget │       │
│        │     │        │        │ (salai)│        │        │        │       │
├────────────────────────────────────────────────────────────────────────────┤
│10-20t  │  400│250-400│ 12-20€ │ MÉDIA  │ TRÈS   │ ✗ CRIT │120K€/a│ LEVER │
│        │ cas │  €/cas│/t      │ FRET   │ ÉLEVÉ  │ -2-4%  │ budget │Principal│
│        │     │ (COÛT │        │(extern)│(LEVIER)│ PROB   │        │ POINT  │
│        │     │ MAXI) │        │        │        │        │        │        │
├────────────────────────────────────────────────────────────────────────────┤
│20-30t  │  150│400-700│ 14-23€ │ SEMI-  │ Énorme │ ✗ CRIT │ 60K€/a │ LEVER  │
│        │ cas │  €/cas│/t      │COMPLET │ (LEVIER│ -5-8%  │ budget │ AGRESS │
│        │     │       │        │        │ MAJEUR)│ PROB   │        │ IF POS │
├────────────────────────────────────────────────────────────────────────────┤
│ >30t   │  20 │700-120│ 18-35€ │ CHARG  │ MAXI   │ ✗ CRIT │ 15K€/a │ CONTRAT│
│        │ cas │  0€   │/t      │COMPLET │ (LEVIER│ -8-12% │ spécial│ANNUEL │
│        │     │       │        │        │ EXTRÊME│ PROB   │        │        │
└────────────────────────────────────────────────────────────────────────────┘


ANALYSE DÉTAILLÉE PAR SEGMENT
════════════════════════════════════════════════════════════════════════════

SEGMENT 1 : <5 tonnes (CHAUFFEUR INTERNE)
──────────────────────────────────────────
Volume annuel : ~1 800 cas (35% du trafic)
Coût unitaire : 50-80€ (chauffeur salarié)
Coût/tonne : 10-16€ par tonne (TRÈS BON)
Transporteur : Chauffeur Gedimat interne (PL)

Profit margin : 4-6% (acceptable pour petit volume)
Budget annuel : 72 000€ (1 800 cas × 40€ moy)

Statut : ✓ OPTIMAL - MAINTENIR
  • Chauffeur interne = flexible, rapide, fiable
  • Coûts bas (salaire fixe amorti sur volume)
  • Permet consolidation facile avec petits volumes
  • Pas de point de levier économique

Actions :
  • Optimiser itinéraires (regrouper <5t par dépôt)
  • Utiliser chauffeurs comme "flex" pour urgences
  • Monitorer taux utilisation camion (target: 80%+)


SEGMENT 2 : 5-10 tonnes (CHAUFFEUR INTERNE)
────────────────────────────────────────────
Volume annuel : ~900 cas (25% du trafic)
Coût unitaire : 80-120€ (chauffeur salarié + temps)
Coût/tonne : 8-12€ par tonne (BON)
Transporteur : Chauffeur Gedimat interne (PL)

Profit margin : 3-5% (acceptable)
Budget annuel : 72 000€ (900 cas × 80€ moy)

Statut : ✓ BON - À CONSERVER AVEC SUIVI
  • Encore économique comparé external
  • Flexibilité excellente
  • Consolidation 2-3 cas = <10t très facile
  • Peu de marge = attention aux surcoûts

Actions :
  • Consolidation obligatoire si poids → 10t (interne jusqu'au seuil)
  • Alert si dépasse 10t : bascule externe
  • Itinéraire optimisé (économiser 20-30 min = -10€)


SEGMENT 3 : 10-20 tonnes (AFFRÈTEMENT EXTERNE) ⚠ CRITIQUE
──────────────────────────────────────────────────────────
Volume annuel : ~400 cas (20% trafic)
Coût unitaire : 250-400€ (Médiafret, coûteux)
Coût/tonne : 12-20€ par tonne (moyen-élevé)
Transporteur : Médiafret + sous-traitants

Profit margin : -2% à -4% (NÉGATIF OU TRÈS FAIBLE = PROB)
Budget annuel : 120 000€ (400 cas × 300€ moy) ← MAJEUR !

Statut : ✗ CRITIQUE - POINT DE LEVIER PRINCIPAL
  • PLUS COÛTEUX QUE CHAUFFEUR INTERNE (12-20€/t vs 8-12€/t)
  • Représente 50% du budget logistique externe
  • Marges réduites ou négatives = pas rentable
  • Consolidation multi-dépôt = levier économique majeur

Problèmes :
  • Pas consolidation actuellement = 2-3 enlèvements séparés
  • Perte économie regroupement (poids insuffisant par enlèvement)
  • Délais hétérogènes (chacun son calendrier)

Actions IMMÉDIATES :
  ✓ PRIORITÉ 1 : Consolidation obligatoire
     └─ Regrouper 2-3 demandes dépôt même fournisseur
     └─ Gain : -20-25% coût (300€ vs 450€ pour 2 enlèv)

  ✓ PRIORITÉ 2 : Arbitrage intelligent dépôt
     └─ Livrer dépôt urgent ou close au fournisseur
     └─ Navette interne économe (80€) vs 2e enlèvement (250€)
     └─ Gain : -15% coût (330€ vs 400€)

  ✓ PRIORITÉ 3 : Alertes fournisseur
     └─ Éviter surcoûts urgence (+30%)
     └─ Gain : -10-15% (réduire 30% urgences)

  RÉSULTAT ESPÉRÉ : 120K€ → 90-100K€ (-15-20%)
  ← ÉCONOMIE 20-30K€/AN SUR SEGMENT CRITIQUE


SEGMENT 4 : 20-30 tonnes (SEMI-COMPLET) ⚠ TRÈS CRITIQUE
─────────────────────────────────────────────────────────
Volume annuel : ~150 cas (10% trafic)
Coût unitaire : 400-700€ (semi-chargement, très coûteux)
Coût/tonne : 14-23€ par tonne (ÉLEVÉ)
Transporteur : Médiafret, transporteurs spécialisés semi

Profit margin : -5% à -8% (FORTEMENT NÉGATIF)
Budget annuel : 60 000€ (150 cas × 400€ moy) ← TRÈS LOURD !

Statut : ✗ TRÈS CRITIQUE - LEVIER AGRESSIF REQUIS
  • PLUS COÛTEUX QUE TOUS les autres segments
  • Marges TRÈS négatives = business model endommagé
  • Semi-complet = sous-utilisé généralement
  • Consolidation master ou contrats spéciaux = seule sortie

Problèmes CRITIQUES :
  • Un seul enlèvement chez fournisseur = pas flexible
  • Poids élevé = peu de marge pour ajustement
  • Coûts fixes semi-remorque = très cher si sous-chargé

Actions IMMÉDIATES :
  ✓ PRIORITÉ 1 : Master consolidation
     └─ Regrouper 2-3 fournisseurs en 1 semi-complet
     └─ Au lieu : 2-3 semi à 50% utilisation
     └─ Gain : -30-40% coût (600€ vs 1000€)

  ✓ PRIORITÉ 2 : Contrats annuels fournisseurs
     └─ Engagements volumes semaine 1-4 mois N
     └─ Pouvoir négocier tarifs réduits (-15-20%)
     └─ Meilleure prédictibilité

  ✓ PRIORITÉ 3 : Reconsidérer modèle approvisionnement
     └─ Passer de "dépôt-centrique" à "client-centrique"
     └─ Livrer directement clients gros volumes (live-drop)
     └─ Éliminer entreposage intermédiaire en certains cas

  RÉSULTAT ESPÉRÉ : 60K€ → 42-45K€ (-25-30%)
  ← ÉCONOMIE 15-18K€/AN SUR SEGMENT TRÈS CRITIQUE


SEGMENT 5 : >30 tonnes (CHARGEMENT COMPLET)
────────────────────────────────────────────
Volume annuel : ~20 cas (5% trafic, rare)
Coût unitaire : 700-1 200€ (chargement complet lourd)
Coût/tonne : 18-35€ par tonne (TRÈ ÉLEVÉ)
Transporteur : Chargement complet, contrats spéciaux

Profit margin : -8% à -12% (TRÈS NÉGATIF)
Budget annuel : 15 000€ (20 cas × 750€ moy, mais rare)

Statut : ✗ ACCEPTABLE si rare et contrats spéciaux
  • Rare (20 cas/an) = peu d'impact budget global
  • Généralement chargement saisonnier ou spécial
  • Contrats annuels négociés = coûts acceptables

Actions :
  • Négocier contrats annuels saisonniers (octobre, mars)
  • Consolidation avec partenaires (partage semi) possible
  • Monitorer : ne pas laisser devenir habituel

═════════════════════════════════════════════════════════════════════════════

SYNTHÈSE ÉCONOMIQUE GLOBALE
════════════════════════════════════════════════════════════════════════════

Segment          │ Budget   │ Coût/t  │ Margin │ Priorité │ Gain Potentiel
──────────────────┼──────────┼─────────┼────────┼──────────┼───────────────
<5t  (interne)   │ 72K€     │ 10-16€  │ 4-6%   │ Bas      │ 5-10% = 3-7K€
5-10t (interne)  │ 72K€     │ 8-12€   │ 3-5%   │ Bas      │ 3-5% = 2-4K€
─────────────────┼──────────┼─────────┼────────┼──────────┼───────────────
10-20t (EXTERNE) │ 120K€    │ 12-20€  │ ✗-2%  │ CRITIQUE │ 20-25% = 20-30K€
20-30t (EXTERNE) │ 60K€     │ 14-23€  │ ✗-5%  │ CRITIQUE │ 25-30% = 15-18K€
─────────────────┼──────────┼─────────┼────────┼──────────┼───────────────
>30t (EXTERNAL)  │ 15K€     │ 18-35€  │ ✗-8%  │ Bas      │ 10-15% = 1-2K€
─────────────────┼──────────┼─────────┼────────┼──────────┼───────────────
TOTAL ANNUEL     │ 339K€    │ 11€ moy │ 0%     │          │ 45-65K€ (13-19%)

════════════════════════════════════════════════════════════════════════════

RECOMMANDATIONS PRIORITAIRES
════════════════════════════════════════════════════════════════════════════

1. SEGMENT 10-20t : Gain potentiel 20-30K€
   └─ Action : Consolidation + alertes fournisseur
   └─ Timing : Immédiat (3-4 semaines)
   └─ Effort : Modéré (processus Angelique + outils)

2. SEGMENT 20-30t : Gain potentiel 15-18K€
   └─ Action : Master consolidation + contrats annuels
   └─ Timing : 6 semaines (négociation)
   └─ Effort : Moyen-lourd (restructuration approvisionnement)

3. SEGMENTS Interne : Gain 5-11K€
   └─ Action : Optimisation itinéraires, consolidation <10t
   └─ Timing : Continu (amélioration incrémentale)
   └─ Effort : Faible

TOTAL GAIN POTENTIEL : 40-60K€/AN
PAYBACK INVESTISSEMENT OUTILS : < 2 mois
════════════════════════════════════════════════════════════════════════════
```

---

## SECTION C : INDICATEURS DE SUIVI (KPIs)

### C.1 Tableau de bord logistique recommandé

```
╔════════════════════════════════════════════════════════════════════════════╗
║            TABLEAU DE BORD : KPIs LOGISTIQUES GEDIMAT                      ║
║                   (Suivi mensuel & actions correctives)                    ║
╚════════════════════════════════════════════════════════════════════════════╝

NIVEAU 1 : COÛTS (Tracking mensuel)
─────────────────────────────────────────────────────────────────────────────

Métrique                          │ Cible    │ Formule                │ Fréq
──────────────────────────────────┼──────────┼─────────────────────────┼─────
Coût moyen enlèvement (<10t)       │ 60-90€   │ Total coût / nb cas     │ Mois
Coût moyen enlèvement (10-20t)     │ 250-300€ │ Total coût / nb cas     │ Mois
Coût moyen enlèvement (20-30t)     │ 350-450€ │ Total coût / nb cas     │ Mois
Coût/tonne moyen transporté        │ 10-12€   │ Total coût / t tonnées  │ Mois
% Coûts vs chiffre affaires        │ <3%      │ Coûts logistique / CA   │ Mois
Taux utilisation chauffeur interne │ 75-85%   │ Heures facturées / h    │ Sem
Coûts affrètement externe vs budget│ <105%    │ Costs réels / forecast  │ Mois
Nombre enlèvements consolidés      │ +20%/an  │ % cas multi-dépôts      │ Mois


NIVEAU 2 : DÉLAIS & FIABILITÉ
─────────────────────────────────────────────────────────────────────────────

Métrique                          │ Cible    │ Formule                │ Fréq
──────────────────────────────────┼──────────┼─────────────────────────┼─────
Taux livraison on-time (J prévu)   │ >95%     │ Liv. à temps / Total    │ Mois
Taux livraison <24h retard         │ >98%     │ Liv. ≤24h / Total       │ Mois
Délai moyen livraison (J)          │ 2-3j     │ Somme délais / nb cas   │ Sem
Incidents retard fournisseur       │ <10/mois │ Nb retards signalés     │ Mois
Alertes fournisseur décenchées     │ >30/mois │ Nb alertes prévention   │ Mois
Temps moyen prise alerte           │ <24h     │ Temps detect / action   │ Mois
% Cas urgence satisfaits           │ >95%     │ Urgent livré J+1 / tot  │ Mois


NIVEAU 3 : SATISFACTION CLIENT
─────────────────────────────────────────────────────────────────────────────

Métrique                          │ Cible    │ Formule                │ Fréq
──────────────────────────────────┼──────────┼─────────────────────────┼─────
Score satisfaction client (0-10)   │ >8.5     │ Moyenne sondage         │ Trim
Taux rétention clients 1 an        │ >92%     │ Clients mêmes / année   │ Ann
NPS (Net Promoter Score)           │ >60      │ Promoteurs - détractors │ Trim
Nombre plaintes logistique/mois    │ <3       │ Incidents graves        │ Mois
% Clients "très satisfaits" délai  │ >80%     │ Note ≥9 sur délais      │ Trim
Délai moyen réaction client plainte│ <24h     │ Temps contact client    │ Mois


NIVEAU 4 : OPÉRATIONS (Tracking continu)
─────────────────────────────────────────────────────────────────────────────

Métrique                          │ Cible    │ Formule                │ Fréq
──────────────────────────────────┼──────────┼─────────────────────────┼─────
Nombre transporteurs utilisés      │ <5 actifs│ Nb transporteurs actifs │ Mois
Concentration top-1 transporteur   │ <70%     │ % volume top 1 / total  │ Mois
Qualité fournisseurs (score)       │ >8/10    │ Avg délai & qualité     │ Mois
Nombre de dépôts impliqués/enlèv   │ 1.5 moy  │ Dépôts moyens/cas       │ Mois
Nombre navettes/semaine            │ 2-3      │ Navettes prévues/réalis │ Sem
Taux utilisation navette (poids)   │ >70%     │ Poids réel / capacité   │ Sem


════════════════════════════════════════════════════════════════════════════

TABLEAU DE BORD MENSUEL (Modèle Excel à remplir)
────────────────────────────────────────────────────────────────────────────

Mois : ________         Responsable : Angelique         Signer : _______

┌──────────────────────────────────────────────────────────────────────────┐
│ COÛTS                                                                    │
├──────────────────────────────────┬─────────┬──────┬──────┬─────────────┤
│ Indicateur                       │ Actuel  │Cible │Delta │ Analyse     │
├──────────────────────────────────┼─────────┼──────┼──────┼─────────────┤
│ Coût enlèvement moy (<10t)       │   €     │ 75€  │  │ OK / À revoir│
│ Coût enlèvement moy (10-20t)     │   €     │280€  │  │ OK / À revoir│
│ Coût enlèvement moy (20-30t)     │   €     │400€  │  │ OK / À revoir│
│ Coût/tonne moyen                 │   €/t   │ 11€  │  │ OK / À revoir│
│ % Cases consolidées 2+ dépôts    │   %     │ 30%  │  │ OK / À revoir│
└──────────────────────────────────┴─────────┴──────┴──────┴─────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ DÉLAIS                                                                   │
├──────────────────────────────────┬─────────┬──────┬──────┬─────────────┤
│ % On-time (jour promis)          │   %     │ 95%  │  │ OK / À revoir│
│ Délai moyen livraison (jours)    │   j     │  2.5 │  │ OK / À revoir│
│ Retards fournisseur signalés     │   #     │  <5  │  │ OK / À revoir│
│ Alertes préventives fournisseur  │   #     │  >20 │  │ OK / À revoir│
└──────────────────────────────────┴─────────┴──────┴──────┴─────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ SATISFACTION CLIENT                                                      │
├──────────────────────────────────┬─────────┬──────┬──────┬─────────────┤
│ Score satisfaction (0-10)        │ /10     │ 8.5  │  │ OK / À revoir│
│ NPS (Promoters - Detractors)     │  pts    │  60  │  │ OK / À revoir│
│ Plaintes logistique              │   #     │ <2   │  │ OK / À revoir│
│ Temps réaction plainte client    │   h     │ <24  │  │ OK / À revoir│
└──────────────────────────────────┴─────────┴──────┴──────┴─────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ ACTIONS CORRECTIVES (Si delta négatif)                                  │
├──────────────────────────────────────────────────────────────────────────┤
│ 1. Métrique écart :                                                      │
│    Action corrective :                                                   │
│    Deadline :                                                            │
├──────────────────────────────────────────────────────────────────────────┤
│ 2. Métrique écart :                                                      │
│    Action corrective :                                                   │
│    Deadline :                                                            │
└──────────────────────────────────────────────────────────────────────────┘


════════════════════════════════════════════════════════════════════════════
```

---

*Document de schémas visuels & matrices de décision - Diagnostic logistique complet Gedimat, français, terminologie opérationnelle.*
