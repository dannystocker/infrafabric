# CARTOGRAPHIE VISUELLE DÉTAILLÉE
## Flux Logistique Gedimat - Diagrammes Complets

**Document Complémentaire:** PASS 2 Analysis
**Date:** 16 novembre 2025

---

## 1. STRUCTURE GÉOGRAPHIQUE & DÉPÔTS

```
RÉGION ÎLE-DE-FRANCE / NORD FRANCE
════════════════════════════════════════════════════════════

                    FOURNISSEURS MAJEURS
                    ═════════════════════

        Éméris (Tuiles)          Édiliens (Ciment)
        ├─ Location: Nord Oise   ├─ Location: Loire-Atlantique
        ├─ Type: Non-livreur     └─ Type: Non-livreur
        └─ Flux: ~15-20t/livraison


DÉPÔTS GEDIMAT
══════════════

        ┌─────────────────────────────────────────────────┐
        │                                                 │
   DÉPÔT ÉVREUX              DÉPÔT MÉRU           DÉPÔT GISORS
   (27140, Eure)             (60110, Oise)        (27xxx, Eure)
        │                         │                   │
   Magasin                    Magasin             Magasin
   Gedimat                    Gedimat             Gedimat
        │                         │                   │
        │                         │                   │
        └─────────────────────────┼─────────────────┘
                                  │
                        ZONES CLIENTS (Rayon 50-80km)
                        ═════════════════════════════
                        ├─ Petits clients (0-2t)
                        ├─ Moyens clients (2-10t)
                        └─ Gros clients (10-30t, souvent enlèvement)

DISTANCES APPROXIMATIVES:
════════════════════════
  Évreux ↔ Méru: ~40km (via Pontoise)
  Évreux ↔ Gisors: ~60km (via Magny-en-Vexin)
  Méru ↔ Gisors: ~30km (plus proche)

  (À valider avec coordonnées GPS exactes)
```

---

## 2. FLUX APPROVISIONNEMENT DÉTAILLÉ (Par Type Fournisseur)

### Scénario A: Fournisseur Non-Livreur, Commande <10 tonnes (Simple)

```
FOURNISSEUR (ex: Petit distributeur local, 8 tonnes)
│
├─ DÉCISION 1: Poids?
│  ├─ Réponse: 8 tonnes < 10 tonnes
│  └─ ACTION: Chauffeur interne OK
│
├─ DÉPÔT OPTIMAL?
│  ├─ Calculer: Distance fournisseur → chaque dépôt
│  ├─ Évreux: 30km
│  ├─ Méru: 15km ← PIVOT (plus proche)
│  └─ Gisors: 25km
│
└─ EXÉCUTION:
   │
   ├─ Chauffeur Gedimat PL (≤10t)
   │  │
   │  └─ Va directement chez fournisseur
   │     │
   │     ├─ Enlève 8 tonnes
   │     │
   │     └─ Livre DÉPÔT MÉRU (plus proche, 15km)
   │        │
   │        └─ Marchandise en stock 1-2h après arrivée
   │
   ├─ COÛT TRANSPORT:
   │  ├─ Salaire chauffeur: ~60€/jour (fixe)
   │  ├─ Carburant: ~3-5€/100km = ~3-8€ (négligeable)
   │  └─ TOTAL: ~65€ (presque gratuit vs externe)
   │
   └─ DÉLAI:
      ├─ Matin: départ fournisseur 8h
      ├─ Arrivée dépôt Méru: ~10h
      └─ Disponibilité client: même jour 14h-15h si enlèvement possible

═══════════════════════════════════════════════════════════════
```

### Scénario B: Fournisseur Non-Livreur, Commande 10-20 tonnes (Critique)

```
FOURNISSEUR (ex: Éméris tuiles, 20 tonnes groupées)
│
├─ COMMANDES GROUPÉES:
│  ├─ Dépôt MÉRU: 15 tonnes
│  └─ Dépôt GISORS: 5 tonnes
│  └─ TOTAL: 20 tonnes
│
├─ DÉCISION 1: Poids total?
│  ├─ Réponse: 20 tonnes > 10 tonnes
│  └─ ACTION: Affrètement externe OBLIGATOIRE
│
├─ DÉCISION 2: DÉPÔT PIVOT? (CRITIQUE - 3 CRITÈRES)
│
│  ┌──────────────────────────────────────────────────────┐
│  │ OPTION A: PRIORITÉ VOLUME (Défense territoriale)    │
│  ├──────────────────────────────────────────────────────┤
│  │ Méru demande: "J'ai 15t (75%), je veux direct"      │
│  │ Trajet: Éméris → Méru (40km)                        │
│  │ Coût: Médiafret ~900€ (base tarif)                  │
│  │ Redistribution: Méru → Gisors navette J+1           │
│  │ Coût navette: ~40€ + 2h tempo attente               │
│  │ TOTAL COÛT: ~940€, DÉLAI: Gisors J+1               │
│  │ PROBLÈME: Inefficace (distance loin, coût haut)     │
│  └──────────────────────────────────────────────────────┘
│
│  ┌──────────────────────────────────────────────────────┐
│  │ OPTION B: PRIORITÉ DISTANCE (Optimisation logistique)│
│  ├──────────────────────────────────────────────────────┤
│  │ Gisors est plus proche Éméris (30km vs 40km Méru)   │
│  │ Trajet optimal: Éméris → GISORS (30km)              │
│  │ Coût: Médiafret ~850€ (3% moins cher, 30km < 40km)  │
│  │ Redistribution: Gisors → Méru navette J+1 (15t)     │
│  │ Coût navette: ~50€ + 2h tempo attente               │
│  │ TOTAL COÛT: ~900€, DÉLAI: Méru J+1                 │
│  │ GAIN: ~40€, Méru attend 1 jour = ACCEPTABLE?        │
│  │ SCORE: Efficace IF clients Méru pas urgents         │
│  └──────────────────────────────────────────────────────┘
│
│  ┌──────────────────────────────────────────────────────┐
│  │ OPTION C: PRIORITÉ URGENCE CLIENT (Satisfaction)     │
│  ├──────────────────────────────────────────────────────┤
│  │ Client chantier Méru: "Besoin J+1 (chantier J+2)"    │
│  │ Trajet: Éméris → MÉRU direct (accepter surcoût)      │
│  │ Coût: Médiafret ~900€ (chantier = urgent premium?)   │
│  │ Redistribution: AUCUNE, Méru reçoit J1 17h           │
│  │ Coût supplémentaire vs Option B: ~40-50€             │
│  │ BÉNÉFICE: Client satisfait, pas annulation           │
│  │ CALCUL: Surcoût 40€ << Perte commande (LTV ~500€)    │
│  │ SCORE: Justifié si client = important/urgent         │
│  └──────────────────────────────────────────────────────┘
│
└─ DÉCISION FINALE (MATRICE):
   │
   │ IF Urgence client Méru élevée (Chantier J+2)
   │    → OPTION C (Méru direct, +40€, client heureux)
   │
   │ ELSE IF Distance Gisors << Distance Méru
   │    → OPTION B (Gisors pivot, -40€, Méru J+1)
   │
   │ ELSE (Tout égal/conflictueux)
   │    → Scoring multi-critère: 35% distance + 35% urgence + 30% volume
   │       → Calculer score Méru vs Gisors
   │       → Appliquer règle formalisée

═══════════════════════════════════════════════════════════════
```

### Scénario C: Fournisseur Non-Livreur, Commande >20 tonnes (Semi-Complet)

```
FOURNISSEUR (ex: Édiliens ciment, 28 tonnes, semi-complet)
│
├─ COMMANDES GROUPÉES:
│  ├─ Dépôt ÉVREUX: 10 tonnes
│  ├─ Dépôt MÉRU: 12 tonnes
│  ├─ Dépôt GISORS: 6 tonnes
│  └─ TOTAL: 28 tonnes (charge semi-complete)
│
├─ DÉCISION 1: >10 tonnes?
│  └─ OUI → Affrètement externe
│
├─ DÉCISION 2: CONSOLIDATION POSSIBLE?
│  │
│  ├─ OPTION A: Un seul pivot (classique)
│  │  └─ Choisir dépôt optimal (distance/urgence)
│  │  └─ Exemple: Évreux (est centre géographique)
│  │  └─ Tous dépôts reçoivent J+1 navette
│  │
│  └─ OPTION B: Multi-livraison (rare, si surcoûts justifiés)
│     ├─ Éverez: Direct (10t)
│     ├─ Méru: Navette depuis Évreux
│     └─ Gisors: Navette depuis Évreux
│
└─ EXÉCUTION STANDARD:
   │
   ├─ Semi-complet 28t
   │  └─ Seul 1 dépôt reçoit livraison directe (pivot)
   │  └─ Exemple: ÉVREUX (est central)
   │
   ├─ JOUR 1 (Livraison Évreux):
   │  ├─ 10t → Magasin Évreux (récupérées direct)
   │  ├─ 12t → Stockées temp Évreux (destin Méru)
   │  └─ 6t → Stockées temp Évreux (destin Gisors)
   │
   ├─ JOUR 2 (Navette 1):
   │  ├─ Navette matin: Évreux → Méru (12t)
   │  ├─ Arrivée Méru: 10h
   │  └─ Disponibilité: 11h-12h
   │
   ├─ JOUR 3 (Navette 2):
   │  ├─ Navette matin: Évreux → Gisors (6t)
   │  ├─ Arrivée Gisors: 11h
   │  └─ Disponibilité: 12h-13h
   │
   └─ COÛTS ESTIMÉS:
      ├─ Affrètement externe (Évreux): ~1100€
      ├─ Navette 1 (Évreux→Méru): ~50€
      ├─ Navette 2 (Évreux→Gisors): ~45€
      └─ TOTAL: ~1195€ pour 28t (équivalent ~42€/tonne)

═══════════════════════════════════════════════════════════════
```

---

## 3. FLUX REDISTRIBUTION INTERNE (Navette)

```
APRÈS LIVRAISON DÉPÔT PIVOT
════════════════════════════════

Jour 1 (Livraison Éméris 20 tonnes à Gisors)
═══════════════════════════════════════════════
 9h  ├─ Médiafret arrive Gisors avec 20 tonnes
     │  ├─ 5 tonnes déchargées (destination Gisors) ← REÇU
     │  └─ 15 tonnes en attente redistribution (destination Méru)
     │
14h  └─ Fin déchargement, début classement/tri


Jour 2 (Navette Gisors → Méru)
═════════════════════════════════
 7h  ├─ Chauffeur interne arrive Gisors
     │  └─ Charge 15 tonnes (4-5 palettes tuiles Éméris)
     │
 8h  ├─ Départ Gisors
     │  └─ Route Gisors → Méru (30km, ~40 min)
     │
10h ├─ Arrivée Méru
    │  └─ Déchargement 15 tonnes
    │
12h └─ Disponibilité Méru pour clients (même jour ou J+1 si urgent)


ALTERNATIVE: NAVETTE 2x/SEMAINE (ACTUEL)
═════════════════════════════════════════

Hypothèse: Navettes fixes mardi + vendredi

Lundi      Livraison Gisors 20t
           ├─ Gisors reçoit 5t (direct, enlèvement possible J+1)
           └─ 15t en stockage attente redistribution

Mardi      NAVETTE #1 (matin)
 8h-10h    Gisors → Méru (15t)
           ├─ Arrivée 10h, Méru peut servir clients midi
           └─ Clients Méru: Enlèvement L+1 après livraison

Jeudi      Clients Gisors enlèvent excédent si nécessaire
           (mais généralement 5t suffit pour 2-3 jours)

Vendredi   NAVETTE #2 (matin, si surplus depuis lundi)
 8h-10h    Gisors/Méru → Évreux (si volume accumulé)
           └─ Rarement utilisée pour Éméris

════════════════════════════════════════════════════════════════

PROBLÈME: Fréquence 2x/semaine vs Demande Client 1-2j
───────────────────────────────────────────────────────
  • Si livraison = lundi soir, client besoin = mardi matin
    → Dépôt peut servir direct si stock suffisant
    → Sinon attendre navette mardi (délai OK)

  • Si livraison = jeudi, client besoin = lundi suivant
    → Attendre navette vendredi + week-end = délai LONG
    → Alternative: Cliente enlève samedi? Impossible (fermé)
    → Ou livraison directe lundi = coûteux

OPTIMISATION FUTURE: Fréquence navette flexible (à la demande)
```

---

## 4. ARBRE DE DÉCISION DÉPÔT PIVOT (Multicritère)

```
COMMANDE GROUPÉE MULTI-DÉPÔT
│
└─ DÉCISION ARBORESCENTE
   │
   ├─ [1] POIDS TOTAL?
   │  ├─ ≤10 tonnes
   │  │  └─ Chauffeur interne → Dépôt DISTANCE MINI → FIN
   │  │
   │  └─ >10 tonnes
   │     │
   │     └─ [2] URGENCE DÉTECTÉE?
   │        │
   │        ├─ OUI (Client chantier date fixe, J+1 demandé)
   │        │  │
   │        │  └─ [2a] Coût surcoût <10% vs perte client?
   │        │     ├─ OUI → Livrer DÉPÔT URGENT direct
   │        │     │         └─ Justification: LTV > surcoût
   │        │     │
   │        │     └─ NON → Aller à [3] DISTANCE
   │        │
   │        └─ NON (Commande régulière, pas urgence)
   │           │
   │           └─ [3] CALCULER SCORE MULTI-CRITÈRE
   │              │
   │              ├─ Critère 1: DISTANCE (Poids: 35%)
   │              │  ├─ Distance Évreux-Fournisseur = X km
   │              │  ├─ Distance Méru-Fournisseur = Y km
   │              │  ├─ Distance Gisors-Fournisseur = Z km
   │              │  └─ Score = (Min distance / Max distance) * 35
   │              │
   │              ├─ Critère 2: VOLUME LOCAL (Poids: 30%)
   │              │  ├─ Tonnage destiné Évreux = A tonnes
   │              │  ├─ Tonnage destiné Méru = B tonnes
   │              │  ├─ Tonnage destiné Gisors = C tonnes
   │              │  └─ Score = (Max tonnage / Total) * 30
   │              │
   │              ├─ Critère 3: CHARGE DÉPÔT ACTUELLE (Poids: 20%)
   │              │  ├─ Capacité restante Évreux = A%
   │              │  ├─ Capacité restante Méru = B%
   │              │  ├─ Capacité restante Gisors = C%
   │              │  └─ Score = (Max capacité / 100) * 20
   │              │
   │              ├─ Critère 4: FIABILITÉ FOURNISSEUR (Poids: 15%)
   │              │  ├─ Historique Évreux (% livraisons à temps)
   │              │  ├─ Historique Méru (% livraisons à temps)
   │              │  ├─ Historique Gisors (% livraisons à temps)
   │              │  └─ Score = (% fiabilité) * 15
   │              │
   │              └─ TOTAL SCORE
   │                 ├─ Évreux: 10 + 8 + 5 + 14 = 37/100
   │                 ├─ Méru: 12 + 12 + 4 + 12 = 40/100 ← GAGNANT
   │                 └─ Gisors: 12 + 9 + 6 + 13 = 40/100
   │                    └─ En cas égalité: Desempate par distance = GISORS
   │
   │
   └─ [4] VÉRIFICATION CAPACITÉ PIVOT?
      │
      ├─ Dépôt optimal peut recevoir 20 tonnes?
      │  ├─ Oui → Procéder livraison pivot
      │  └─ Non → Récalculer sans dépôt saturé, vérifier 2e choix
      │
      └─ [5] NOTIFICATION & LIVRAISON
         │
         ├─ Médiafret reçoit instruction: "Livrer Méru le 15/11 avant 17h"
         ├─ Navigatione 2 jours: Gisors reçoit SMS "Marchandise Éméris arrive, prévoir stockage"
         └─ ...

════════════════════════════════════════════════════════════════
```

---

## 5. MATRICE INEFFICACITÉS vs FLUX POINT-CLÉS

```
MAPPING INEFFICACITÉS → FLUX OPÉRATIONNEL
═════════════════════════════════════════════════

Flux Opérationnel          Inefficacité Associée              Impact               Localisation
─────────────────────────  ───────────────────────────────   ───────────────────  ─────────────
COMMANDE REÇUE             Pas d'alerte urgence auto         Arbitrage urgent     Étape 1
 ↓                         (détection manuelle)              retardé (~30-60 min)

GROUPEMENT FOURNISSEUR     Défense territoriale              Arbitrage coûteux    Étape 2
 ↓                         (chaque dépôt défend intérêt)     (+20-30% transport)

DÉCISION DÉPÔT PIVOT       Pas de règle multi-critère        Inconistance, conflit Étape 3
 ↓                         (Angélique décide ad-hoc)         (dépôt vs dépôt)

SUIVI FOURNISSEUR          Pas d'alertes automatiques        Retard détecté J+2   Étape 4-5
 ↓                         (suivi manuel)                     au lieu J+1

DEMANDE TRANSPORT          Logiciel insuffisant              Pas de coûts visibles Étape 6
 ↓                         (pas de stats, scoring)           (bloque transparence)

LIVRAISON DÉPÔT PIVOT      Navette non-optimisée             Attente 1-3 jours    Étape 7
 ↓                         (fréquence fixe 2x/semaine)       (variance délai)

CLIENT ATTEND              Pas d'alerte retard proactive     Incertitude client   Étape 8
 ↓                         (information réactive)            (panique si retard)

FEEDBACK CLIENT            Mesure satisfaction négative      Aveugle satisfaction Étape 9
                           uniquement (réclamations)         (arbitrage coûts vs
                                                              satisfaction flou)

════════════════════════════════════════════════════════════════
```

---

## 6. FLUX OPTIMAL (PROPOSITION PASS 3)

```
[Réservé pour Pass 3 - Recommandations Optimales]

Comparaison:
  Flux ACTUEL (PASS 2 diagnostic)
  vs
  Flux PROPOSÉ (PASS 3 recommandations)

Éléments à optimiser:
  • Alertes automatiques → Détection J+0 vs J+2
  • Scoring multicritère → Règle transparente vs ad-hoc
  • Dashboard → Coûts visibles vs opaques
  • Communication client → Proactive vs réactive
  • Navette → Fréquence flexible vs fixe 2x/semaine
```

---

**Document finalisé:** Cartographie Visuelle PASS 2
**Prochaines étapes:** PASS 3 (Recommandations) + PASS 4 (Cross-Domain Expertise)
