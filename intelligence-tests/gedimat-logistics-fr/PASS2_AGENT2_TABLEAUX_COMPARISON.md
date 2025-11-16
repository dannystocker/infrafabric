# PASS 2 - AGENT 2: Tableaux Comparatifs Détaillés
## Matrices de Comparaison Coûts & Scénarios Transport

**Date:** 16 novembre 2025
**Audience:** Décideurs opérationnels, Angélique, Responsables dépôts
**Format:** Tableaux exploitables pour arbres de décision

---

## TABLE 1: COMPARAISON DIRECTE - TROIS MODES TRANSPORT

### Vue Synthétique Par Métrique

```
╔════════════════════════════════════════════════════════════════════════════════╗
║ MÉTRIQUE                    CHAUFFEURS INTERNES  AFFRÈTEMENT EXTERNE  NAVETTES  ║
╠════════════════════════════════════════════════════════════════════════════════╣
║ Coût €/tonne                €8-12 (salarial)     €15-25 (direct)     €15-18   ║
║                             €6-11 (marginal)                         (marginal)║
║                                                                                  ║
║ Coût €/km                   €0.40-0.60           €0.80-1.20          €0.82-1.00║
║                                                                                  ║
║ Coût €/tonne/km             €0.04-0.07           €0.06-0.12          €0.14-0.16║
║                                                                                  ║
║ Premium vs Interne          BASELINE             +40-70%             +60-90%   ║
║                                                                                  ║
║ Délai Livraison             1-2 jours            2-5 jours           2-5 jours ║
║                             (régional proche)    (consolidation)     (fixe)    ║
║                                                                                  ║
║ Flexibilité Urgence         EXCELLENTE           Bonne               Faible    ║
║                             (j+1 possible)       (express +30%)       (fixe     ║
║                                                                       2×/sem)   ║
║                                                                                  ║
║ Fiabilité                   Bonne                Moyenne             Bonne     ║
║ (respect delai)             (retards rares)      (retards Médiafret) (prévisib)║
║                                                                                  ║
║ Impact Dépôt                Efficace (1 arrêt)   EXCELLENT (direct)  Concentré ║
║ (consolidation)                                  (multi-arrêt OK)    (2 arrêts)║
║                                                                                  ║
║ Capacité Charge             6-8 tonnes           20-30 tonnes        5-8 tonnes║
║ (typique)                   (PL léger)           (semi-complet)      (circuit) ║
║                                                                                  ║
║ Distance Efficacité         <150 km optimal      >100 km optimal     50-200 km ║
║                                                                      fixe       ║
║                                                                                  ║
║ Coût Annuel Budget          €45-70k              €80-120k            €9-15k   ║
║ (Gedimat estimé)            (1-2 chauffeurs)     (Médiafret)         (2×/sem)  ║
║                                                                                  ║
║ Courbe Coûts vs Volume      ↗ LINÉAIRE            ↘ DÉGRESSIVE        → FIXE   ║
║ (augmente avec tonnes)      (salarial fixe)      (économies échelle) (navette) ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

---

## TABLE 2: MATRICE DE SÉLECTION - QUEL MODE POUR QUEL CAS?

### Arbre de Décision par Charge & Distance

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DÉCISION MODE TRANSPORT OPTIMAL                         │
└─────────────────────────────────────────────────────────────────────────────┘

CHARGE TONNAGE:
│
├─ < 5 TONNES
│  │
│  ├─ Distance fournisseur < 80 km ────→ CHAUFFEUR INTERNE
│  │                                      Coût: €30-50
│  │                                      Délai: 1-2 jours
│  │
│  └─ Distance > 80 km ────────────────→ AFFRÈTEMENT (mini-charge)
│                                         Coût: €80-120
│                                         Délai: 2-4 jours
│
├─ 5-10 TONNES
│  │
│  ├─ Distance < 100 km ───────────────→ CHAUFFEUR INTERNE
│  │                                      Coût: €40-70
│  │                                      Délai: 1-2 jours
│  │                                      Utilisation: OPTIMAL
│  │
│  └─ Distance > 100 km ───────────────→ Évaluer affrètement vs attendre
│                                         Si urgent: AFFRÈTEMENT (€100-150)
│                                         Si flexible: ATTENDRE consolidation
│
├─ 10-15 TONNES (SEUIL CRITIQUE)
│  │
│  ├─ Client tolère délai +1-3h ──────→ CONSOLIDER DYNAMIQUE
│  │                                      Regrouper 2 commandes <10t
│  │                                      Coût: €150-180 (vs €80-90 separate)
│  │  ⚠️ Attention: Peut coûter plus cher en transport
│  │     MAIS avantage dépôt (1 livraison) + satisfaction client
│  │
│  └─ Urgent (client J-1) ────────────→ AFFRÈTEMENT EXPRESS
│                                        Coût: €180-250 (+30% premium)
│                                        Délai: 1-2 jours
│
├─ 15-20 TONNES
│  │
│  ├─ Même région (Île-de-France) ────→ AFFRÈTEMENT standard
│  │                                      Coût: €150-200
│  │                                      Décomposition possible: 1-2 dépôts
│  │                                      Scoring: Proximité > Volume
│  │
│  └─ Multi-région ────────────────────→ CONSOLIDATION Médiafret
│                                         (si 2+ arrêts) Coût: €200-260
│                                         Économie: -€30-50 vs séparé
│
├─ 20-30 TONNES (SEMI-COMPLET NORMAL)
│  │
│  └─────────────────────────────────→ AFFRÈTEMENT CONSOLIDÉ
│                                        Coût: €250-350
│                                        Décomposition: 2-3 arrêts OK
│                                        RÈGLE: Livrer dépôt le plus proche
│                                              d'abord (coût marginal bas)
│
└─ > 30 TONNES
   │
   └─────────────────────────────────→ COMPLET + SURCHARGE OU Décomposition
                                        Vérifier contrats poids axle
                                        Possible: 2 chargements < 30t

───────────────────────────────────────────────────────────────────────────────

REDISTRIBUTION ENTRE DÉPÔTS:
│
└─ Par défaut ──────────────────────→ NAVETTE INTERNE (2×/semaine)
                                       Coût: €9-15k/an (salarial fixe)
                                       Délai: 1-4 jours selon cycle

                                       EXCEPTION (Urgent semaine):
                                       Affrètement intra-semaine
                                       (coût additionnel: €50-100)
```

---

## TABLE 3: COÛTS PAR SCÉNARIO - CAS D'USAGE RÉELS

### Scenario A: Petit Fournisseur Régional (<80km)

```
╔═══════════════════════════════════════════════════════════════════════════╗
║ SCENARIO: Fournisseur X (matériaux divers) à Évreux, Commande 8 tonnes   ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║ MODE 1: CHAUFFEUR INTERNE (Optimal pour ce cas)                          ║
║ ──────────────────────────────────────────────────────────────────────────║
║  Coûts:
║    - Salaire allocation: €25-35 (4-5 heures à ~€7-8/h marginal)
║    - Carburant: €8-10 (170 km × €0.06/km diesel)
║    - Entretien allocation: €5-10
║    - Total Salarial/Marginal: €38-55
║
║  Délai: 1-2 jours (opération semaine)
║  Satisfaction client: Excellente (livraison directe dépôt)
║
║ MODE 2: AFFRÈTEMENT EXTERNE (Coûteux pour cette charge)
║ ──────────────────────────────────────────────────────────────────────────║
║  Coûts:
║    - Médiafret 8 tonnes, 80 km: €100-140 (€12-17/tonne)
║    - Total: €100-140
║
║  Délai: 2-3 jours (consolidation possible avec autres)
║  Avantage: Zéro ressource interne utilisée
║
║ DÉCISION: ✓ CHAUFFEUR INTERNE
║ Économie: €50-100 vs affrètement
║ Note: Cas d'école - chauffeur interne presque toujours optimal < 10t régional
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Scenario B: Cas Émeris - 20 Tonnes Vers 2 Dépôts

```
╔═══════════════════════════════════════════════════════════════════════════╗
║ SCENARIO: Émeris (tuiles) → 15t Méru + 5t Gisors (80 km éloignement)     ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║ OPTION 1: "DÉFENSE TERRITORIALE" - Livrer Méru d'abord (actuel)          ║
║ ──────────────────────────────────────────────────────────────────────────║
║  Étape 1: Enlèvement 20t chez Émeris
║    - Médiafret: €200-250 (standard tarif)
║    - Livre Méru (15t = prioritaire volume)
║
║  Étape 2: Redistribution 5t Gisors
║    - Attendre navette (2-4 jours): €0 transport + attente client
║    - OU affrètement intra-semaine: €50-80 urgent
║
║  Coût Total: €200-330 (dépend urgence)
║  Délai: 3-7 jours (2 livraisons, délai redistribution)
║  Satisf. Client: RISQUÉE (Gisors attend 4j si navette)
║
║
║ OPTION 2: "SCORING INTELLIGENT" - Livrer Gisors d'abord (optimisé)       ║
║ ──────────────────────────────────────────────────────────────────────────║
║  Étape 1: Enlèvement 20t chez Émeris
║    - Médiafret route optimisée: Émeris → Gisors (5t) → Méru (15t)
║    - Coût: €200-250 (peut -€20 si consolidation multi-arrêt reconnue)
║    - Arrêt 1: Gisors (5t) - Client 1 satisfait
║    - Arrêt 2: Méru (15t) - Client 2 satisfait
║
║  Étape 2: Pas de redistribution (déjà livré Méru direct)
║    - Coûts évités: €0
║
║  Coût Total: €180-230
║  Délai: 3-4 jours (1 livraison optimisée)
║  Satisf. Client: EXCELLENTE (livraisons directes, pas redéploiement)
║  Économie: €20-100 vs Option 1
║
║ DÉCISION: ✓ OPTION 2 (SCORING INTELLIGENT)
║ Économies estimées: €30-50 ce cas
║ Fréquence annuelle: 10-15 cas similaires = €300-750/an gain réel
║ + Amélioration satisfaction client (pas redistribution)
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Scenario C: Consolidation Dynamique - Deux Commandes Partielles

```
╔═══════════════════════════════════════════════════════════════════════════╗
║ SCENARIO: Jour donné, 2 commandes arrivent dépôt Méru                    ║
║           14h00: 7t matériaux | 14h30: 6t ciment = 13t total             ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║ OPTION 1: "2 ENLÈVEMENTS SÉPARÉS" (Actuel si processus pas changé)       ║
║ ──────────────────────────────────────────────────────────────────────────║
║  Commande 14h00 (7t):
║    - Chauffeur interne enlève seul: €25-40
║
║  Commande 14h30 (6t):
║    - Chauffeur interne enlève seul: €20-30
║
║  Coût Total: €45-70
║  Délai: Chacun next working day
║  Frais: 2 trajets fournisseur, 2 enlèvements dépôt (moins efficient)
║
║
║ OPTION 2: "CONSOLIDATION DYNAMIQUE" - Attendre 45 min, enlever ensemble  ║
║ ──────────────────────────────────────────────────────────────────────────║
║  14h45 - Décision: Combiner 13t
║    - Médiafret enlèvement 13t: €150-180 (€11-14/tonne)
║    - 1 livraison dépôt (efficient: uncharger une fois)
║
║  Coût Total: €150-180
║  Délai: +45 min attente (acceptable si client pas urgent)
║  Avantage: 1 enlèvement, 1 livraison dépôt plus efficient
║
║
║ ANALYSE DÉCISION:
║ ───────────────────────────────────────────────────────────────────────────
║
║  Coût transport direct: €45-70 (2 chauffeurs) vs €150-180 (1 affrètement)
║                          → Option 1 MOINS CHER en transport ✗
║
║  MAIS:
║  - Dépôt: 1 livraison (Option 2) vs 2 livraisons (Option 1)
║    → Option 2 MEILLEUR pour dépôt (uncharger 1 fois vs 2 fois)
║
║  - Satisfaction: Client tolère délai +45 min?
║    → Si OUI: Option 2 = meilleur satisfaction
║    → Si NON: Option 1 = respecter urgence
║
║  - Coûts marginaux:
║    Si chauffeur "libre" pour autre transport: coûts internes €50-70
║    Si chauffeur sinon inactif: coûts salarial seuls ≈ allocation
║
║ CONCLUSION: CONSOLIDATION utile si:
║  ✓ Client tolère délai 45 min
║  ✓ Dépôt bénéficie (moins uncharger) ≈ €10-20 économie dépôt
║  ✓ Alors total impact = -€50 transport + €10 dépôt = net -€40
║
║ RECOMMANDATION: Implémenter si clients régionaux (Méru, Gisors)
║                 Moins pertinent pour urgences (Île-de-France)
║
║ Potentiel annuel: 5-10 cas/mois × €40 gain = €2.4-4.8k/an
╚═══════════════════════════════════════════════════════════════════════════╝
```

---

## TABLE 4: STRUCTURE COÛTS ANNUELS DÉTAILLÉE

### Budget Transport Estimé (Tous Modes)

```
┌──────────────────────────────────────────────────────────────────────────┐
│         BUDGETS TRANSPORT ANNUELS GEDIMAT - DÉCOMPOSITION DÉTAILLÉE       │
└──────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════╗
║ 1. CHAUFFEURS INTERNES (1-2 FTE estimé)                                 ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Salaires + charges sociales:                                    €28-42k  ║
║    - SMIC brut + primes risque: ~€20-25k/an
║    - Charges sociales (42%): +€8.4-10.5k
║    - Avantages (essence, repas): +€2-3k
║    - Heures supp/congés spéciaux: +€1-3.5k
║                                                                            ║
║  Carburant (diesel allocation):                                  €3-5k   ║
║    - 33,000 km/an × €0.09-0.15/km: €3-5k
║    - Inclus dans "utilisation" (pas encore décomposé)
║                                                                            ║
║  Maintenance & entretien:                                        €1-2k   ║
║    - Révision, filtres, pneus, réparation courante
║    - Durée de vie 5-7 ans (amortissement)
║                                                                            ║
║  Assurance responsabilité civile:                                €0.8-1.2k ║
║                                                                            ║
║  Amortissement véhicule (Renault Master, 5 ans):                €2-3k   ║
║                                                                            ║
║  Frais divers (péage minimal, parking, hygiene):                €0.5-1k  ║
║                                                                            ║
║  ────────────────────────────────────────────────────────────────────────║
║  TOTAL CHAUFFEURS INTERNES:                           €36-55k (1 FTE)   ║
║                             ×2 si 2 chauffeurs      €72-110k (2 FTE)   ║
║                                                                            ║
║  Hypothèse Gedimat: 1-2 chauffeurs ≈ €45-75k/an                         ║
║  Confidence: Moyen (±€10k) - nécessite données paie réelles              ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════╗
║ 2. AFFRÈTEMENT EXTERNE (Médiafret) - >10 TONNES                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Volume moyen estimé: 150-200 enlèvements/an                             ║
║  Tonnage moyen par enlèvement: 15-18 tonnes                              ║
║  Tonnage annuel géré: 2,250-3,600 tonnes >10t                            ║
║                                                                            ║
║  Tarif moyen Médiafret:                                          €12-16/t ║
║  → Basé sur mix (10-20t standard, semi-complet économies d'échelle)      ║
║                                                                            ║
║  Coût annual = 2,500-3,200 tonnes × €12-16/tonne             €30-51k    ║
║                                                                            ║
║  Éléments additionnels:                                                   ║
║    - Enlèvements urgents (premium +30%): ~€5-10k/an                      ║
║    - Retards/réclamations Médiafret: ~€2-5k/an                          ║
║    - Surcharges (zone, nuit, W-E): ~€3-8k/an                            ║
║    - Sous-traitants (si Médiafret délègue): ~€10-20k/an                 ║
║                                                                            ║
║  ────────────────────────────────────────────────────────────────────────║
║  TOTAL AFFRÈTEMENT ESTIMÉ:                             €50-94k/an        ║
║                                                                            ║
║  Hypothèse Gedimat: €80-120k/an (facteur marges possibles)               ║
║  Confidence: Faible (±€30k) - MANQUE factures réelles Médiafret          ║
║  ACTION CRITIQUE: Demander 6 mois factures pour validation                ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════╗
║ 3. NAVETTES INTERNES (2×/SEMAINE, 3 DÉPÔTS)                             ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Modèle: Chauffeur dédié ou allocation polyvalent                        ║
║                                                                            ║
║  Scenario A (Chauffeur dédié 20% temps):                                 ║
║    - Allocation salaire: €5.6-8.4k/an (20% × €28-42k)
║    - Carburant (100 tournées × 110 km): €1-1.5k
║    - Maintenance allocation: €200-300
║    - Subtotal: €7-10k
║                                                                            ║
║  Scenario B (Chauffeur polyvalent 50% temps):                            ║
║    - Allocation salaire: €14-21k
║    - Carburant: €1.2-1.5k
║    - Maintenance: €200-300
║    - Subtotal: €15.4-22.8k
║                                                                            ║
║  ────────────────────────────────────────────────────────────────────────║
║  HYPOTHÈSE GEDIMAT: Navettes = coûts marginaux faibles                   ║
║                     (chauffeur ne ferait rien sinon)                      ║
║                     Estimation: €9-15k/an                                 ║
║  Confidence: Moyen (±€5k) - dépend allocation réelle                      ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════╗
║ 4. COÛTS CACHÉS - COORDINATION & PERTE COMMANDES                        ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  A. Temps Angélique non budgété:                                         ║
║     Estimation: 11-18 h/semaine × €20-25/h (coût moyen) × 50 semaines   ║
║     = €11-22.5k/an CACHÉ (non alloué transport)                          ║
║                                                                            ║
║  B. Pertes commandes clients (Émeris-like incidents):                    ║
║     - Fréquence: 2-4 incidents/an (à valider avec CRM)
║     - Coût par incident: €800-1.2k (transport payé + marge perdue)
║     - Total: €1.6-4.8k/an
║                                                                            ║
║  C. Tensions inter-dépôts (inefficacité arbitrage):                      ║
║     - Surcoûts débats, délais décision: ~€1-2k/an
║     - Urgences intra-semaine (vs navette): ~€0.6-1.2k/an
║                                                                            ║
║  D. Surstock défensif (immobilisation):                                  ║
║     - Surstock estimé: €8-12k immobilisé
║     - Coûts intérêt/usure (3-5%): €240-600/an
║                                                                            ║
║  ────────────────────────────────────────────────────────────────────────║
║  TOTAL COÛTS CACHÉS:                                 €14.3-30.6k/an     ║
║  Confidence: Très faible (±50%) - données manquantes                      ║
║  ACTIONS: Audit CRM pertes, timesheet Angélique, WMS stock               ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════╗
║ RÉSUMÉ GLOBAL BUDGET TRANSPORT GEDIMAT ESTIMÉ                           ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  Chauffeurs internes:                              €45-75k (Confiance: M) ║
║  Affrètement Médiafret:                            €80-120k (Confiance: F) ║
║  Navettes inter-dépôts:                            €9-15k (Confiance: M)  ║
║  Carburant marginal/entretien:                     €4-8k (Confiance: M)   ║
║  Coûts cachés (coordination, pertes):              €14-31k (Confiance: F)  ║
║  ────────────────────────────────────────────────────────────────────────║
║  TOTAL ANNUEL ESTIMÉ:                    €152-249k                        ║
║  ────────────────────────────────────────────────────────────────────────║
║  PLAGE RÉALISTE (±25%):                    €114-311k                      ║
║  ────────────────────────────────────────────────────────────────────────║
║                                                                            ║
║  ⚠️  ÉCART CONFIANCE: ±30-40%                                            ║
║      Raison: Manque données Médiafret, données chauffeurs, CRM pertes    ║
║                                                                            ║
║  PRIORISER VALIDATION:                                                    ║
║    1️⃣  Factures Médiafret 6 mois (aff. 40% budget)                      ║
║    2️⃣  Données paie chauffeurs (internes 20% budget)                     ║
║    3️⃣  Audit CRM réclamations (coûts cachés)                             ║
║                                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## TABLE 5: OPPORTUNITÉS ÉCONOMIES - MATRICE IMPACT × EFFORT

### Priorités d'Optimisation

```
┌────────────────────────────────────────────────────────────────────────┐
│           OPPORTUNITÉS DE RÉDUCTION COÛTS - IMPACT VS EFFORT            │
└────────────────────────────────────────────────────────────────────────┘

ZONE 1: GAINS RAPIDES (EFFORT BAS, IMPACT MOYEN)
═════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│ 1A. ALERTES RETARDS FOURNISSEURS                                        │
├─────────────────────────────────────────────────────────────────────────┤
│ Description:  Automatiser détection retards (ARC date dépassée)         │
│ Effort:       2 jours dev Excel + formations                            │
│ Coût:         0€ (interne)                                              │
│ Bénéfice:     Angélique gagne 2-3h/semaine, moins urgences intra-sem   │
│ Gain estimé:  €3-5k/an (libération temps)                               │
│ Timeline:     Semaine 1                                                 │
│ Risque:       Bas (alertes non critiques)                               │
│ PRIORITY:     ⭐⭐⭐⭐⭐ IMMÉDIAT                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 1B. SCORING DÉPÔT OPTIMISÉ (Proximité × Volume × Urgence)              │
├─────────────────────────────────────────────────────────────────────────┤
│ Description:  Excel macro scoring (40% dist, 30% vol, 30% urgence)     │
│ Effort:       1-2 jours dev + 5 jours test                             │
│ Coût:         1-2k€ (consultant logistique)                             │
│ Bénéfice:     Arbitrage systématique vs "défense territo", economie €  │
│ Gain estimé:  €4-12k/an (5-10% affrètement optimisé)                   │
│ Timeline:     Semaine 2-3                                              │
│ Risque:       Faible (Excel, pas IT critique)                          │
│ PRIORITY:     ⭐⭐⭐⭐⭐ PHASE 1                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 1C. CONSOLIDATION MANUELLE (Regrouper <10t dans créneau 2-3h)          │
├─────────────────────────────────────────────────────────────────────────┤
│ Description:  Angélique examine quotidien: "2 commandes mêmes 2h?"     │
│ Effort:       1 jour processus + 1 jour Excel alertes                   │
│ Coût:         0€ (processus)                                            │
│ Bénéfice:     Économies consolidation + 1 livraison dépôt vs 2         │
│ Gain estimé:  €8-20k/an (30-50% economies si 50-100 consolidations)   │
│ Timeline:     Semaine 4                                                 │
│ Risque:       Moyen (client tolère délai +1-3h?)                        │
│ PRIORITY:     ⭐⭐⭐⭐ PHASE 1 (post-alertes)                           │
└─────────────────────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════════════════════╗
║ SOUS-TOTAL ZONE 1 (Quick Wins):                          €8-37k potentiel║
║ Effort total:              2-3 semaines + 1-2k€ consultant             ║
║ ROI:                       8:1 à 37:1 (excellent)                      ║
╚═════════════════════════════════════════════════════════════════════════╝


ZONE 2: MOYEN TERME (EFFORT MOYEN, IMPACT ÉLEVÉ)
═════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│ 2A. TABLEAU DE BORD + SATISFACTION CLIENT                              │
├─────────────────────────────────────────────────────────────────────────┤
│ Description:  Dashboard KPI (taux service, coût €/t, NPS, % consol.)  │
│ Effort:       1-2 semaines dev Excel/PowerBI                           │
│ Coût:         2-3k€ (consultant)                                        │
│ Bénéfice:     Baseline mesure, visibilité réelle coûts vs estimations │
│ Gain estimé:  €0 direct, MAIS révèle opportunités €10-30k additionels │
│ Timeline:     Mois 2                                                    │
│ Risque:       Bas (data visualization)                                 │
│ PRIORITY:     ⭐⭐⭐⭐ VALIDATION Phase 1                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 2B. AUDIT COÛTS CACHÉS - Angélique & Pertes Commandes                  │
├─────────────────────────────────────────────────────────────────────────┤
│ Description:  Analyse CRM pertes, timesheet Angélique, WMS surstock   │
│ Effort:       3-5 jours analyse                                         │
│ Coût:         1-2k€ (consultant)                                        │
│ Bénéfice:     Quantifier coûts cachés ~€14-31k estimés = révéler $    │
│ Gain estimé:  €3-9k (libération temps Angélique via automation)        │
│ Timeline:     Mois 1-2                                                  │
│ Risque:       Bas (audit analytique)                                   │
│ PRIORITY:     ⭐⭐⭐⭐ VALIDATION baseline                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 2C. RÉOPTIMISATION NAVETTES (Fréquence, "appels à vide")               │
├─────────────────────────────────────────────────────────────────────────┤
│ Description:  Ajuster 2×/sem → selon volumes + créer "urgence navette" │
│ Effort:       1-2 semaines processus + training                        │
│ Coût:         0€ (processus)                                            │
│ Bénéfice:     Moins urgences intra-semaine, meilleure utilisation cap │
│ Gain estimé:  €2-5k/an (15-30% réduction navettes)                    │
│ Timeline:     Mois 3                                                    │
│ Risque:       Moyen (dépôts résistent changement)                      │
│ PRIORITY:     ⭐⭐⭐ MOYEN TERME                                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 2D. CONTRATS FOURNISSEURS - SLA Délais, Pénalités                      │
├─────────────────────────────────────────────────────────────────────────┤
│ Description:  Négocier avec 5-10 top fournisseurs: délais, pénalités  │
│ Effort:       4-6 semaines négociation + legal review                  │
│ Coût:         2-5k€ (avocat si contrats complexes)                     │
│ Bénéfice:     Réduire imprévu retards, clarifier responsabilités      │
│ Gain estimé:  €2-5k/an (moins incidents, pénalités appliquées)        │
│ Timeline:     Mois 4-6                                                  │
│ Risque:       Moyen (négociation fournisseurs peut être sensible)      │
│ PRIORITY:     ⭐⭐⭐ POST-Quick Wins                                   │
└─────────────────────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════════════════════╗
║ SOUS-TOTAL ZONE 2 (Medium Term):                   €7-28k potentiel     ║
║ Effort total:              4-8 semaines                                ║
║ ROI:                       3:1 à 14:1                                  ║
╚═════════════════════════════════════════════════════════════════════════╝


ZONE 3: LONG TERME (EFFORT ÉLEVÉ, IMPACT STRUCTUREL)
═════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│ 3A. SYSTÈME OPTIMISATION INTÉGRÉ (Google OR-Tools / Jsprit)             │
├─────────────────────────────────────────────────────────────────────────┤
│ Description:  Plateforme MDVRP auto-optimise dépôt + routing          │
│ Effort:       8-12 semaines dev + intégration                          │
│ Coût:         20-40k€ (dev full-time ou consultant spécialisé)       │
│ Bénéfice:     Optimisation multi-critère automatique, suggestions      │
│ Gain estimé:  €10-25k/an (addition Zone 1+2 + meilleur routage)      │
│ Timeline:     Mois 9-12                                                │
│ Risque:       Moyen (déploiement IT, formation)                        │
│ GATING:       SEULEMENT si Zone 1-2 ROI >10k validé                   │
│ PRIORITY:     ⭐⭐⭐ PHASE 2 conditionnel                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 3B. PARTENARIATS POOLING FRET (Shared Transport Non-Concurrents)       │
├─────────────────────────────────────────────────────────────────────────┤
│ Description:  Négocier partage capacité avec Brico Dépôt, Weldom      │
│ Effort:       6-12 semaines négociation + setup                        │
│ Coût:         5-10k€ (legal, platform setup)                           │
│ Bénéfice:     Économies 25-30% transport consolidé, partage risques   │
│ Gain estimé:  €15-25k/an (IF volumes documentation 6 mois)           │
│ Timeline:     Mois 6-12                                                │
│ Risque:       Élevé (partenaire alignment, confidentialité)           │
│ GATING:       Nécessite signature accord avant développement           │
│ PRIORITY:     ⭐⭐ LONG TERME                                         │
└─────────────────────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════════════════════╗
║ SOUS-TOTAL ZONE 3 (Long Term):                     €25-50k potentiel    ║
║ Effort total:              4-6 mois + €25-50k investment               ║
║ ROI:                       0.5:1 à 2:1 (LT only IF all quick wins work)║
╚═════════════════════════════════════════════════════════════════════════╝

═════════════════════════════════════════════════════════════════════════════

RÉSUMÉ SCÉNARIOS CUMUL:
─────────────────────

Scénario CONSERVATEUR (Zone 1 seulement):    €8-37k économies, 2-3 sem, 1-2k€
Scénario AMBITIEUX (Zone 1 + 2):            €15-65k économies, 3-4 mois, 5-12k€
Scénario TRANSFORMATION (Zone 1+2+3):       €40-115k économies, 9-12 mois, 30-70k€

RECOMMANDATION: Commencer Zone 1 IMMÉDIATEMENT
               Valider ROI, puis décider Zone 2-3 basé sur résultats réels
```

---

## TABLE 6: DONNÉES REQUISES - CHECKLIST VALIDATION

### Priorité Critique (Obtenir Avant Mois 2)

```
CHECKLIST VALIDATION COÛTS
══════════════════════════════════════════════════════════════════════════

☐ FACTURES MÉDIAFRET (6 mois minimum, si possible 12 mois)
  └─ Détail par enlèvement: date, tonnage, origine, destination, coût
  └─ Identifier tarifs, surcharges (zone, urgent, retard)
  └─ Évaluer: Sont-il pénalités retard appliquées?
  └─ Demander à: Comptabilité générale ou Dir. Logistique

☐ DONNÉES CHAUFFEURS INTERNES
  └─ Salaires annuels réels (brut, charges, avantages)
  └─ Heures travail (RTT, congés réels vs théorique)
  └─ Kilométrage réel (tachygraphe ou GPS si disponible)
  └─ Allocation temps par fonction (fournisseur? client? inactif?)
  └─ Demander à: Responsable RH ou Paie

☐ VOLUMES TRANSPORT MENSUEL
  └─ Distribution: nombre enlèvements <10t vs >10t par mois
  └─ Tonnage total: <10t interne vs >10t Médiafret
  └─ Saisonnalité: varie hiver vs été?
  └─ Demander à: WMS / Logiciel gestion ou Angélique

☐ HISTORIQUE INCIDENTS CLIENTS
  └─ Réclamations 6 derniers mois (nombre, motif, impact €)
  └─ Commandes annulées / déplacées chez concurrent
  └─ Retards fournisseur vs transport vs coordination (proportion)
  └─ Demander à: CRM ou Manager commercial

☐ LOCALISATION FOURNISSEURS PRINCIPAUX
  └─ Adresses GPS des 10-15 top fournisseurs (par volume)
  └─ Distance réelle Fournisseur ↔ Chaque dépôt
  └─ Horaires d'enlèvement (fenêtres d'accès)
  └─ Demander à: Responsable achats ou Angélique

DATE LIMITE COLLECTE: 31 Novembre 2025 (FIN MOIS 2)
RESPONSABLE: Direction générale / Sponsor IT
```

---

## TABLE 7: FEUILLE DE ROUTE NEXT STEPS

### Planning Exécution Recommandé

```
SEMAINE 1-2 (IMMÉDIATE):
─────────────────────────
❑ Réunion lancement avec PDG + Angélique
❑ Demander factures Médiafret (6 mois)
❑ Demander données paie chauffeurs
❑ Formation Angélique scoring multicritère (2h)
❑ Mise en place alertes retards (Excel, démarrage)

SEMAINE 3-4:
────────────
❑ Dev Excel scoring dépôt (1.5j consultant)
❑ Tests scoring avec 20 cas réels
❑ Formation Angélique utilisation quotidienne
❑ Mise en place consolidation manuelle (processus)

MOIS 2 (Semaines 5-8):
──────────────────────
❑ Tableau de bord initial (coûts, KPI)
❑ Sondage satisfaction 50 clients pilotes
❑ Audit interne: temps Angélique, WMS surstock
❑ Compilation résultats Phase 1

MOIS 3 (Semaines 9-12):
───────────────────────
❑ Réunion bilan PDG avec résultats réels
❑ Décision: Go Zone 2 (medium term) Y/N
❑ Si OUI: Lancer scoring fournisseurs + SLA negos

Validation budget vs réel:
  Phase 1 coût: 1-2k€
  Phase 1 gain potentiel: 8-37k€
  → Si gains <5k€: analyser pourquoi, corriger
  → Si gains >20k€: accélérer Phase 2
```

---

**Fin Tableaux Comparatifs - Pass 2**
*Prêt intégration Dossier Final*
