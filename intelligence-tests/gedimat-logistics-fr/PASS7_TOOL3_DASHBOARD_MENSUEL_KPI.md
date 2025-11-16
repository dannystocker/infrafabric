# PASS 7 - TOOL 3: DASHBOARD MENSUEL KPI GEDIMAT LOGISTIQUE
## Spécification Complète - Audience Dirigeants & Opérations

**Date:** 16 novembre 2025
**Auteur:** Pass 7 Deep Dive Agent 3
**Périmètre:** Gedimat 3 dépôts (Évreux, Méru, Gisors)
**Confiance:** 75% (post-Pass 4 KPI validation)
**Langue:** Français (norme executive)

---

## SECTION 1: AUDIENCE & FRÉQUENCE RÉUNIONS

### 1.1 Profils Utilisateurs & Besoins

| Rôle | Temps Revue | Fréquence | Focus Metrics | Format Préféré |
|---|---|---|---|---|
| **Angélique (Coordinatrice Logistique)** | 15 min | Hebdomadaire (jeudi) | Incidents retard, consolidation réalisée, chauffeur dispo | Tableau alertes + tendance coûts |
| **PDG (Direction Générale)** | 30 min | Mensuel (1er lundi) | ROI optimisation, coûts vs budget, KPI satisfaction client | Résumé exécutif + 3 graphes clés |
| **Direction Franchise** | 120 min | Trimestriel (fin trimestre) | Tendances 3 mois, comparaison vs benchmarks, recommandations | Présentation complets + données détaillées |
| **Finance (Responsable)** | 20 min | Mensuel + hebdo coûts | Coûts €/tonne, variance budget, évaluation Médiafret | Détail lignes budget + graphes variance |
| **IT/Support** | Administratif | À la demande | Logs erreurs formules, performance Excel | Rapports techniques |

### 1.2 Calendrier Réunions

```
HEBDOMADAIRE (Jeudi 16h30, 15 min, Coordinatrice Angélique):
├─ Revue alertes critiques (retards >5%, incidents)
├─ Validation données saisies semaine
├─ Ajustement consolidation pour semaine N+1
└─ Escalade PDG si exception détectée

MENSUEL (1er lundi 10h, 30 min, PDG + Finance + Logistique):
├─ KPI synthétique (18 indicateurs)
├─ Variance vs budget & targets
├─ Comparaison mois N-1 (tendance)
├─ Décisions arbitrage si KPI rouge
└─ Actions plan pour mois N+1

TRIMESTRIEL (Fin trimestre mercredi, 120 min, Direction + PDG + all stakeholders):
├─ Analyse tendances 3 mois (données historiques 24 mois)
├─ Comparaison benchmarks secteur
├─ Lessons learned (cas edge exception)
├─ Recommandations calibrage scoring (si bias détecté)
└─ Plan actions Q+1
```

---

## SECTION 2: ARCHITECTURE DASHBOARD - 3 SECTIONS THÉMATIQUES

### 2.1 SECTION A: COÛTS TRANSPORT (6 KPIs)

**Cible Audience:** PDG (stratégie coûts), Finance (budget), Logistique (optimisation)
**Visualisation Principale:** Trend lines 12 mois + Feux tricolores (vert/jaune/rouge vs targets)

#### KPI A.1: COÛT UNITAIRE €/TONNE TRANSPORT

**Définition:**
```
€/tonne = (Coûts totaux transport / Tonnes livrées ce mois)

Coûts totaux = Chauffeur interne (allocation) + Carburant + Affrètement Médiafret
               + Navettes inter-dépôts + Péages

Exemple: Octobre 2025
  Coûts totaux: €16,500 (€3.5k interne + €11k Médiafret + €1.8k navettes + €0.2k péages)
  Tonnes: 55t
  Résultat: €16,500 / 55 = €300/tonne = €0.30/t ✓ VERT (vs target €0.30)
```

**Baseline Actuel:** €0.35-0.45/t
**Target Gedimat (Post-Pass 6):** €0.25-0.30/t
**Benchmark Secteur:** PME €0.40-0.50, Best-in-class €0.25-0.30
**Fréquence Collecte:** Mensuel (données comptables M+5)
**Propriétaire:** Finance

**Formule Excel:**
```
=SOMME(Coûts_Chauffeur_Interne + Coûts_Carburant + Coûts_Affrètement
       + Coûts_Navettes + Coûts_Péages) / Tonnes_Livrées
```

**Interprétation Feu:**
- 🟢 VERT: ≤€0.30/t (cible atteinte, optimisation continue)
- 🟡 JAUNE: €0.30-€0.38/t (acceptable, monitoring serré)
- 🔴 ROUGE: >€0.38/t (dégradation, action corrective)

**Alertes Automatiques:**
- IF €/t >€0.35 THEN Email "Dépassement cible transport - Analyser Médiafret"
- IF variation mois/mois >+8% THEN Email "Variance coût détectée"

---

#### KPI A.2: COÛT UNITAIRE €/KM TRANSPORT

**Définition:**
```
€/km = Coûts totaux transport / Kilomètres parcourus (ce mois)

Exemple: Octobre 2025
  Coûts totaux: €16,500
  KM parcourus: 8,250 (chauffeurs internes + Médiafret estimé)
  Résultat: €16,500 / 8,250 = €2.00/km ✓ VERT (vs target €2.00)
```

**Baseline Actuel:** €2.20-2.40/km
**Target Gedimat:** €2.00/km (post-optimisation proximité & consolidation)
**Fréquence Collecte:** Mensuel (tachygraphe + factures Médiafret)
**Propriétaire:** Logistique

**Formule Excel:**
```
=SOMME(Coûts_Totaux_Transport) / KM_Total_Mois

Où KM_Total = KM_Chauffeur_Interne (tachygraphe)
             + KM_Médiafret_Estimé (tonnage × distance moyenne)
```

**Interprétation Feu:**
- 🟢 VERT: €2.00/km ou moins (excellente efficience)
- 🟡 JAUNE: €2.00-€2.20/km (normal, amélioration possible)
- 🔴 ROUGE: >€2.20/km (inefficacité détectée)

**Insight:** Utilisé pour détecter "dead miles" (trajets à vide), routes non-optimisées.

---

#### KPI A.3: TAUX REMPLISSAGE MOYEN CAMIONS (%)

**Définition:**
```
Taux_remplissage = Tonnage réel transporté / Capacité théorique camions

Exemple (Mois d'octobre):
  ├─ Trajet 1: 18t sur 30t disponible = 60%
  ├─ Trajet 2: 22t sur 30t disponible = 73%
  ├─ Trajet 3: 25t sur 30t disponible = 83%
  └─ Moyenne: (60 + 73 + 83) / 3 = 72% ✓ JAUNE (vs target 75%)
```

**Baseline Actuel:** ~67% (benchmark France moyen)
**Target Gedimat:** 75%+ (post-consolidation & Milkrun)
**Benchmark Best-in-class:** 78-85% (Leroy Merlin niveau)
**Fréquence Collecte:** Hebdomadaire (bordereau Médiafret)
**Propriétaire:** Logistique

**Formule Excel:**
```
=MOYENNE(Taux_remplissage_par_trajet)

Où Taux_remplissage_trajet = Tonnes_Chargement / Capacité_Théorique_30t
(Collecte: Médiafret bordereau + chauffeurs internes questionnaire)
```

**Interprétation Feu:**
- 🟢 VERT: ≥75% (consolidation efficace)
- 🟡 JAUNE: 70-75% (acceptable, mais amélioration possible)
- 🔴 ROUGE: <70% (surcoût par tonne, consolidation insuffisante)

**Cas d'Usage:** Si rouge détecté → Analyser "Pourquoi camion demi-plein?"
  - Fournisseur indisponible?
  - Client urgence qui a forcé départ partiel?
  - Consolidation non-réalisée (audit)?

---

#### KPI A.4: COÛT MOYEN PAR COMMANDE (€)

**Définition:**
```
€/commande = Coûts transport attribuables / Nombre commandes livrées

Exemple: Octobre 2025
  Coûts transport total: €16,500
  Commandes livrées: 140 (mix <10t interne + >10t Médiafret)
  Résultat: €16,500 / 140 = €118/commande ✓ VERT (vs target €120)
```

**Baseline Actuel:** ~€180 (affrètement moyen)
**Target Gedimat:** €120 (post-optimisation)
**Fréquence Collecte:** Mensuel (CRM + factures transport)
**Propriétaire:** Finance

**Formule Excel:**
```
=Coûts_Transport_Total / Nombre_Commandes_Livrées

(Nota: "Commandes" = transactions clients, pas tonnes)
```

**Interprétation Feu:**
- 🟢 VERT: ≤€120 (efficience bonne)
- 🟡 JAUNE: €120-€150 (normal, marges normales)
- 🔴 ROUGE: >€150 (erosion marges, impact rentabilité)

**Insight:** Complément à €/t et €/km. Permet vue "par transation client" (plus lisible commercialement).

---

#### KPI A.5: TAUX CONSOLIDATION (% cas)

**Définition:**
```
Taux_consolidation = Nombre commandes consolidées / Total commandes ×100%

Consolidation = Regroupement 2+ commandes même client/région en 1 trajet
                (au lieu de 2+ trajets séparés)

Exemple: Octobre 2025
  Cas consolidation détectés: 35 (Émeris + Fournisseur B même route, etc.)
  Total commandes: 140
  Taux: (35 / 140) × 100 = 25% ⚠️ JAUNE (vs target 35%)
```

**Baseline Actuel:** ~0% (aucune consolidation systématique)
**Target Gedimat:** 35%+ (post-implémentation Milkrun + consolidation)
**Économie Estimée par Consolidation:** €50-100 par cas (évite 2 trajets séparés)
**Fréquence Collecte:** Hebdomadaire (Angélique manual tracking)
**Propriétaire:** Logistique (Angélique)

**Formule Excel:**
```
=Nombre_Cas_Consolidation_Réalisée / Nombre_Total_Commandes × 100

Cas consolidation = SI (même client OU même région ET délai <48h)
                    ALORS regrouper routes
```

**Interprétation Feu:**
- 🟢 VERT: ≥35% (règle consolidation appliquée régulièrement)
- 🟡 JAUNE: 20-35% (consolidation partielle, amélioration possible)
- 🔴 ROUGE: <20% (opportunités non-saisies, audit Angélique process)

**Alert Automation:** IF Taux <20% THEN "Cible consolidation non atteinte - Analyser blocages"

**Cas Édge:** Urgence J+0 exempt consolidation (client ne peut pas attendre 48h).

---

#### KPI A.6: VARIANCE COÛTS vs BUDGET MENSUEL (%)

**Définition:**
```
Variance = [(Coûts Actuels - Budget Prévu) / Budget Prévu] × 100%

Exemple: Octobre 2025
  Budget prévu: €18,000
  Coûts réels: €16,500
  Variance: [(16,500 - 18,000) / 18,000] × 100 = -8.3% ✓ VERT (économie)
```

**Baseline Actuel:** Inconnu (pas de suivi budget détaillé actuel)
**Target Gedimat:** Variance ±5% (tolérance normale)
**Fréquence Collecte:** Mensuel (M+3 ou M+5 selon comptabilité)
**Propriétaire:** Finance (Contrôleur de gestion)

**Formule Excel:**
```
=((Coûts_Réels - Budget_Prévu) / Budget_Prévu) × 100%

Classification Variance:
  - Positive = Coûts < Budget (bonne nouvelle, mais pas toujours)
  - Négative = Coûts > Budget (problème, nécessite analyse)
```

**Interprétation Feu:**
- 🟢 VERT: -5% à +5% (dans envelope budgétaire, contrôle bon)
- 🟡 JAUNE: ±5% à ±10% (sortie budget modérée, action corrective semaine N+1)
- 🔴 ROUGE: >±10% (déviation importante, investigation immédiate)

**Sous-Analyses Variance:**
- Variance "Chauffeur Interne" (heures supplémentaires? absence?)
- Variance "Carburant" (prix +20%?)
- Variance "Médiafret" (utilisation externe > prévu?)
- Variance "Consolidation" (taux <target?)

---

### 2.2 SECTION B: SERVICE CLIENT (7 KPIs)

**Cible Audience:** PDG (satisfaction/rétention), Logistique (délai), Commercial (NPS)
**Visualisation Principale:** Évolution NPS (trend 12 mois), Jauge ponctualité (speedometer)

#### KPI B.1: DÉLAI MOYEN LIVRAISON (JOURS)

**Définition:**
```
Délai_moyen = MOYENNE(Date_Livraison_Réelle - Date_Commande_Client)

Exemple: Octobre 2025
  Livraisons: 140 commandes
  Délais individuels: J+2, J+3, J+4, J+5, J+4, ... (mix de valeurs)
  Délai moyen: 4.2 jours ✓ VERT (vs target 3-4j)
```

**Baseline Actuel:** ~4-5 jours (estimé Pass 3)
**Target Gedimat:** 2-3 jours (post-optimisation proximité)
**Benchmark PME:** 4-6 jours, Best-in-class: 2-3 jours
**Fréquence Collecte:** Mensuel (CRM historique livraisons)
**Propriétaire:** Logistique

**Formule Excel:**
```
=MOYENNE(Jours_Depuis_Commande_Jusquà_Livraison)

Données par commande:
  ├─ Numéro Commande
  ├─ Date Commande Client
  ├─ Date Livraison Réelle
  ├─ Écart en jours = Livraison - Commande
  └─ Comptabiliser en MOYENNE
```

**Interprétation Feu:**
- 🟢 VERT: ≤3 jours (excellent, satisfy clients rapides)
- 🟡 JAUNE: 3-5 jours (acceptable, standard secteur)
- 🔴 ROUGE: >5 jours (slow, risk churn client)

**Drivers Analyse:** Si ROUGE détecté:
  - Fournisseur retard? (dépôt reçoit tard)
  - Transport interne ralentit? (saturation chauffeurs?)
  - Client attente consolidation? (volontaire)

---

#### KPI B.2: TAUX PONCTUALITÉ (% "À TEMPS")

**Définition:**
```
Ponctualité = (Commandes Livrées À Temps / Commandes Totales) × 100%

"À Temps" = Livraison avant/égal Date Promise au client (SLA client)

Exemple: Octobre 2025
  Commandes livrées: 140
  Livrées À Temps: 126 (dont 14 retard >0j)
  Ponctualité: (126 / 140) × 100 = 90% ⚠️ JAUNE (vs target 95%)
```

**Baseline Actuel:** ~80% (estimé Pass 3)
**Target Gedimat:** 95%+ (post-scoring & optimisation)
**Benchmark PME:** 75-85%, Best-in-class: 95%+
**Fréquence Collecte:** Mensuel (CRM livraisons vs promesse)
**Propriétaire:** Logistique/Service Client

**Formule Excel:**
```
=Commandes_À_Temps / Commandes_Totales × 100%

Logique:
  IF (Date_Livraison_Réelle ≤ Date_Promise_SLA)
  THEN Compter = À Temps (oui)
  ELSE Compter = Retard (non)
```

**Interprétation Feu:**
- 🟢 VERT: ≥95% (excellent respect SLA)
- 🟡 JAUNE: 85-95% (acceptable, amélioration nécessaire)
- 🔴 ROUGE: <85% (service dégradé, risk churn 50%+ Pass 3 estimé)

**Note Important:** Distinction "à temps" vs "retard". Cas spéciaux:
  - Retard client demandé (consenti, ne compte pas)
  - Retard force majeure (livraison 24h tardif but client accepte)

---

#### KPI B.3: % RETARDS >48H (INDICATEUR CRITIQUE)

**Définition:**
```
Retard_critique = (Commandes Retard >2j / Commandes Totales) × 100%

"Retard >48h" = Livraison au-delà de date promise de PLUS de 2 jours

Exemple: Octobre 2025
  Commandes totales: 140
  Retards >48h détectés: 14 (exemple: promis J+3, livré J+6)
  Pourcentage: (14 / 140) × 100 = 10% 🔴 ROUGE (vs target <3%)
```

**Baseline Actuel:** ~12-15% (Pass 3 estimé)
**Target Gedimat:** <3% (post-optimisation)
**Impact Commercial:** Chaque retard >48h = risque churn 30-50% (estimé)
**Fréquence Collecte:** Mensuel (détection automatique CRM)
**Propriétaire:** Logistique/Commercial (escalade)

**Formule Excel:**
```
=COMPTE.SI(Retard_Jours > 2) / Nombre_Commandes_Total × 100%

Retard_Jours = IF (Date_Livraison_Réelle > Date_Promise_SLA)
               THEN DateDiff(Promise, Réelle)
               ELSE 0
```

**Interprétation Feu:**
- 🟢 VERT: <3% (incident isolé, acceptable)
- 🟡 JAUNE: 3-8% (pattern détecté, action corrective)
- 🔴 ROUGE: >8% (systémique, risk majeur clients)

**Alert & Escalade Automatique:**
- IF >10% THEN Email PDG "Service dégradé - retards >48h détectés"
- IF >15% THEN Email PDG + Direction Ops "Crise service - intervention urgente"

**Root Cause Analysis (Automatisé):**
```
IF Retard_Critique THEN Investiguer:
  - Fournisseur cause? (date enlèvement retard)
  - Transport cause? (chauffeur indisponible, route bloquée)
  - Dépôt cause? (stock manquant, erreur traitement)
  - Client change? (date promise annoncée tard)
```

---

#### KPI B.4: NET PROMOTER SCORE - NPS (−100 à +100)

**Définition:**
```
NPS = (% Promoteurs − % Détracteurs)

Enquête client trimestrielle: "Recommanderiez-vous Gedimat à un tiers?"
  ├─ Promoteurs (9-10) = "Oui, excellent service"
  ├─ Passifs (7-8) = "Neutre, normal"
  └─ Détracteurs (0-6) = "Non, problèmes logistiques"

Exemple Q3 2025:
  Enquête 30 clients
  └─ Promoteurs: 12 (40%)
  └─ Détracteurs: 6 (20%)
  └─ NPS: 40% − 20% = +20 ✓ JAUNE (vs target +35)
```

**Baseline Actuel:** Non mesuré (à établir)
**Target Gedimat:** +35-40 (secteur BTP matériaux)
**Benchmark PME:** +15-25, Best-in-class: +45-60
**Fréquence Collecte:** Trimestriel (30-50 clients sample)
**Propriétaire:** Commercial/Service Client

**Méthodologie Enquête:**
```
Timing: Fin trimestre (ex: fin septembre pour Q3)
Audience: Mix 30-50 clients (grandes comptes + PME)
Question: "Sur échelle 0-10, recommanderiez-vous Gedimat?"
Timing réponse: 2 semaines
Suivi: Relance si <40% réponse
Analyse: Segmenter par dépôt (Évreux vs Méru vs Gisors)
```

**Interprétation Feu:**
- 🟢 VERT: NPS ≥+35 (bonne santé, croissance possible)
- 🟡 JAUNE: NPS +15 à +35 (acceptable, amélioration urgente)
- 🔴 ROUGE: NPS <+15 (danger, risk churn, reputation)

**Correlation Analysis:**
- NPS vs Ponctualité (if ponctual ↑ then NPS ↑)
- NPS vs Retards >48h (strong inverse)
- NPS par dépôt (isolation problème?)

**Action Plan If ROUGE:**
  - Détracteur interviews (20% base: "Qu'avons-nous mal fait?")
  - Focus corrective sur top 3 complaints
  - Retest NPS 6 semaines post-action

---

#### KPI B.5: TAUX SATISFACTION CLIENT - CSAT (%)

**Définition:**
```
CSAT = Moyenne satisfaction clients enquête (1-5 étoiles ou %)

Question type: "Satisfait des délais livraison?" (Oui/Non) OU
               "Rating satisfaction générale 1-5 étoiles"

Exemple Q3 2025:
  Enquête 40 clients
  Satisfaction moyenne: 4.1/5 étoiles
  Pourcentage "Satisfait" (≥4/5): 32/40 = 80%
```

**Baseline Actuel:** Non mesuré (à établir)
**Target Gedimat:** ≥85% ("Satisfait")
**Fréquence Collecte:** Trimestriel (post-livraison ou fin trimestre)
**Propriétaire:** Service Client

**Méthodologie:**
```
Post-Livraison (Option 1):
  - SMS/Email automatique 24h après livraison
  - Question 1: "Livraison à l'heure?" (Oui/Non)
  - Question 2: "Rating général 1-5 étoiles"
  - Collecte: Intégrer à CRM

Fin Trimestre (Option 2):
  - Appel client managers
  - Discussion satisfaction période
  - Rating 1-5
```

**Interprétation Feu:**
- 🟢 VERT: ≥85% (bonne satisfaction, retention OK)
- 🟡 JAUNE: 75-85% (acceptable, monitoring)
- 🔴 ROUGE: <75% (insatisfaction détectable, action)

**Correlation:** CSAT vs Retards >48h (strong inverse). Si CSAT ↓ alors chercher retards.

---

#### KPI B.6: INCIDENTS PAR 100 LIVRAISONS (TAUX)

**Définition:**
```
Taux_Incident = (Nombre Incidents Logistiques / Livraisons Totales) × 100

Incident = Casse, Perte, Non-livraison, Erreur adresse, Réclamation client

Exemple: Octobre 2025
  Livraisons: 140
  Incidents: 3 (1× casse, 1× erreur adresse, 1× retard mal communiqué)
  Taux: (3 / 140) × 100 = 2.1 incidents/100 liv
```

**Baseline Actuel:** ~20-30/an estimé (Pass 3) = ~2-3/100 liv
**Target Gedimat:** <1.5/100 liv (post-formation & process)
**Fréquence Collecte:** Mensuel (CRM incidents log)
**Propriétaire:** Logistique/Service Client

**Catégories Incidents à Tracker:**
```
├─ Casse produit (ciment sac rompu, tuiles cassées)
├─ Perte (non-livraison, marchandise disparue)
├─ Erreur adresse (livré mauvais client)
├─ Retard >48h (incident logistique)
├─ Réclamation client (qualité service)
└─ Autres (à spécifier)
```

**Formule Excel:**
```
=COMPTE.SI(Type_Incident ≠ "Aucun") / Livraisons_Totales × 100

Par catégorie:
  ├─ Taux_Casse = Nombre_Casse / Livraisons × 100
  ├─ Taux_Perte = Nombre_Perte / Livraisons × 100
  ├─ Etc.
```

**Interprétation Feu:**
- 🟢 VERT: <1.5/100 liv (très bon, seulement incidents résiduels)
- 🟡 JAUNE: 1.5-2.5/100 liv (acceptable, improvement possible)
- 🔴 ROUGE: >2.5/100 liv (trop nombreux, root cause analysis)

**Alert:** IF Taux >2/100 AND Incident_Type = "Casse"
  THEN "Casse produit élevée - Vérifier emballage & formation chauffeur"

---

#### KPI B.7: CHURN RATE CLIENT (% ANNUEL)

**Définition:**
```
Churn_Rate = (Clients Perdus dans Période / Clients Début Période) × 100%

Client = Perdu si aucune commande >6 mois (comparé période précédente)

Exemple: Octobre 2025 (Q3 vs Q2)
  Clients Q3: 150
  Clients Q2: 160
  Clients perdus: 10 (décision non-commande / changement fournisseur)
  Churn: (10 / 160) × 100 = 6.25%
```

**Baseline Actuel:** Estimé 5-8% (Pass 3)
**Target Gedimat:** <3% (post-optimisation service + NPS)
**Impact Financier:** Chaque client perdu = €2-8k revenu annuel manqué
**Fréquence Collecte:** Trimestriel (CRM analysis commandes)
**Propriétaire:** Commercial (prevention)

**Root Cause Analysis (If Churn Élevée):**
```
Interroger clients perdus (focus groupe):
├─ "Quand avez-vous changé fournisseur?" (trigger date)
├─ "Pourquoi Gedimat?" (raison churn)
│  ├─ Retards logistiques?
│  ├─ Prix trop élevé?
│  ├─ Service client insufficient?
│  └─ Concurrent meilleur?
└─ Action corrective basée sur pattern (ex: si retards = fix prioritaire)
```

**Formule Excel:**
```
=Clients_Perdus / Clients_Début_Période × 100%

Clients_Perdus = SI (Pas commande derniers 6 mois
                      AND Avait commande période antérieure)
                 THEN Compter perte
```

**Interprétation Feu:**
- 🟢 VERT: <3% (churn normal, client loyalty OK)
- 🟡 JAUNE: 3-5% (watch, some attrition)
- 🔴 ROUGE: >5% (significant loss, urgent action)

**Correlation:** Churn ↑ corrélé avec Retards >48h ↑ ou NPS ↓. Analyser causalité.

---

### 2.3 SECTION C: EFFICACITÉ OPÉRATIONNELLE (5 KPIs)

**Cible Audience:** PDG (ressources), Logistique (process), RH (capacité)
**Visualisation Principale:** Jauge utilisation (tachygraphe), Heatmap reliability par fournisseur

#### KPI C.1: SCORING UTILISATION CHAUFFEURS (%)

**Définition:**
```
Utilisation = (Heures de travail productif / Heures disponibles) × 100%

Heures productif = Conduite + Livraison (actif) [Tachygraphe]
Heures disponibles = 8h × 220 jours/an = 1,760h/an par chauffeur

Exemple: Octobre 2025 (chauffeurs interne 2 ETP)
  Chauffeur 1: 150h/mois × 2 = 300h (heures disponible)
  Productivité: 265h (conduite+livraison), 35h (pause/admin)
  Utilisation: 265/300 = 88% ✓ VERT

  Moyenne dépôt: (Chauffeur 1 + Chauffeur 2) / 2 = 85% VERT (vs target 80%)
```

**Baseline Actuel:** ~70-75% (temps mort, attente client)
**Target Gedimat:** 80%+ (bonne utilisation)
**Benchmark PME:** 60-70%, Best-in-class: 85%+
**Fréquence Collecte:** Mensuel (tachygraphe + timesheets)
**Propriétaire:** RH/Logistique

**Formule Excel:**
```
Utilisation = Heures_Productif_Mois / Heures_Disponible_Mois × 100%

Heures_Disponible = 20 jours travail × 8h = 160h/mois (approximé)
Heures_Productif = Tachygraphe conduite + Livraison (timestamp CRM)

Détail:
  ├─ Temps conduite (tachygraphe)
  ├─ Temps livraison (CRM arrivée/départ par adresse)
  ├─ Pause déjeuner (30-60 min, soustrait)
  ├─ Temps mort attente client (trackable)
  └─ Temps admin (rare, soustrait)
```

**Interprétation Feu:**
- 🟢 VERT: ≥80% (excellente utilisation, ROI chauffeur bon)
- 🟡 JAUNE: 70-80% (acceptable, amélioration routes possible)
- 🔴 ROUGE: <70% (underutilization, analyser causes)

**Root Cause If ROUGE:**
  - Routes non-optimisées? (VRP à améliorer)
  - Client attente long? (38% cas d'après Pass 3)
  - Chauffeur absent/maladie? (RH issue)
  - Volume commandes faible? (saisonnal)

**Note:** Pass 3 identifié 30-40% temps productif = "attente client chantier". Acceptable.

---

#### KPI C.2: OVERRIDE RATE - % SCORINGS IGNORÉS (MANUELLE OVERRIDE)

**Définition:**
```
Override_Rate = (Décisions Manuelles / Décisions Totales) × 100%

Override = Cas où Angélique refuse scoring MDVRP Excel
           et force dépôt différent (en raison edge case, urgence, etc.)

Exemple: Octobre 2025
  Décisions totales: 35 commandes >10t candidates scoring
  Décisions scoring Excel: 28 (score confidence ≥60 points)
  Overrides manuels Angélique: 7 (score faible <60 OU edge case)
  Override rate: (7 / 35) × 100 = 20% ✓ VERT (vs target <25%)
```

**Baseline Actuel:** 100% (tout manuel Angélique, no scoring yet)
**Target Gedimat:** <25% (scoring confiance utilisé 75%+ cas)
**Fréquence Collecte:** Mensuel (log Excel override checkbox)
**Propriétaire:** Logistique (Angélique)

**Formule Excel:**
```
=COMPTE.SI(Override = OUI) / Nombre_Décisions × 100%

Log override obligatoire:
  ├─ Numéro Commande
  ├─ Score Original
  ├─ Dépôt Proposé par Scoring
  ├─ Dépôt Décidé par Angélique (manual)
  ├─ Raison Override (edge case? urgence? relation?)
  └─ Coûts Impact (ex: +€100 surcoût override vs scoring)
```

**Interprétation Feu:**
- 🟢 VERT: <15% (scoring très confriant, adoption forte)
- 🟡 JAUNE: 15-25% (scoring utilisé, exceptions normales)
- 🔴 ROUGE: >25% (trop d'overrides, scoring pas fiable? audit formule)

**Analysis If ROUGE:**
  - Problème 1: Scoring formula mal calibrée? (pondérations 40/30/30 pas bon?)
  - Problème 2: Angélique trop conservative? (préfère risque-averse?)
  - Problème 3: Edge cases nombreux non-couvert par scoring? (audit case types)

**Note:** Override rate est "health check" score MDVRP Pass 6. Si >25% → reviser pondérations Pass 6.

---

#### KPI C.3: WORKLOAD ANGÉLIQUE (HEURES/SEMAINE)

**Définition:**
```
Workload = Heures productifs Coordination Logistique par semaine

Tâches incluses:
  ├─ Suivi retards fournisseurs (alertes, email)
  ├─ Arbitrage scoring dépôt (review override)
  ├─ Gestion incidents & réclamations client
  ├─ Planning consolidation & milkrun
  └─ Réunion hebdo reporting

Exemple: Semaine 44 Octobre 2025
  Suivi retards: 4h
  Arbitrage scoring: 2h
  Incidents: 1h
  Consolidation planning: 2h
  Réunion + reporting: 1h
  Total: 10h/semaine ✓ VERT (vs baseline 11-18h, post-optimisation target 7-9h)
```

**Baseline Actuel:** 11-18h/semaine (Pass 4 Agent 2 estimé)
**Target Gedimat (Post-Automation):** 7-9h/semaine (30-40% libération)
**Fréquence Collecte:** Hebdomadaire (timesheet Angélique)
**Propriétaire:** RH/Logistique

**Formule Excel:**
```
=SOMME(Heures_Coordination_Semaine)

Tracking détaillé:
  Lundi: [Suivi retard 4h] = 4h
  Mercredi: [Arbitrage 2h] = 2h
  Jeudi: [Incidents 1h] + [Consolidation 2h] + [Reporting 1h] = 4h
  Total semaine: 10h
```

**Interprétation Feu:**
- 🟢 VERT: 7-9h/semaine (workload optimal post-automation)
- 🟡 JAUNE: 9-12h/semaine (workload moderate, acceptable)
- 🔴 ROUGE: >12h/semaine (overload, bottleneck, need support)

**Strategic Implication (ROUGE):**
- Angélique = single point of failure logistique
- If sick/absent = process collapse
- Solution = embauche agent support partial (€12-15k/an ROI 200%+)
  BUT requires budget arbitrage Finance vs Logistique

**Action If ROUGE:**
  - Prioritize automation: alertes fournisseur (API)
  - Consolidation milkrun delegation (can chauffeurs plan?)
  - Consider part-time support agent (24-30h/semaine)

---

#### KPI C.4: SUPPLIER RELIABILITY INDEX (%)

**Définition:**
```
Reliability = (Enlèvements À Temps / Total Enlèvements Fournisseur) × 100%

"À Temps" = Fournisseur livre dépôt avant date SLA promise

Exemple: Octobre 2025 (Émeris tracking)
  Enlèvements Émeris promis: 8
  Enlèvements à temps: 7 (1× retard 4 heures)
  Reliability: (7 / 8) × 100 = 87.5% 🟡 JAUNE (vs target 95%)
```

**Baseline Actuel:** ~85% (Émeris Pass 3) variability by supplier
**Target Gedimat:** 95%+ (high SLA expectation)
**Impact:** Retard fournisseur → Cascade urgences → Coûts +30% Médiafret
**Fréquence Collecte:** Mensuel (par fournisseur, Émeris+3 others tracked)
**Propriétaire:** Achats/Logistique

**Formule Excel (Par Fournisseur):**
```
=COMPTE.SI(Date_Enlèvement_Réelle ≤ Date_Promise) / Nombre_Enlèvements × 100%

Dashboard supplier:
  ├─ Émeris (tuiles): 87% 🟡
  ├─ Fournisseur B (briques): 94% 🟡
  ├─ Fournisseur C (ciment): 91% 🟡
  └─ Médiafret (transport): 96% 🟢 (when called on time)
```

**Interprétation Feu:**
- 🟢 VERT: ≥95% (fiable, peut compter dessus)
- 🟡 JAUNE: 85-95% (variable, plan buffer)
- 🔴 ROUGE: <85% (unreliable, problème sérieux)

**Action If ROUGE (Supplier):**
1. Documented SLA conversation (written commitment)
2. Penalty clause (if miss SLA 3x → adjust terms)
3. Alternative supplier audit (backup option?)
4. Payment terms adjust (reduce upfront, tie to SLA compliance)

**Note:** Pass 4 Contradiction 3 identified urgence vs reliability tension.
  High SLA expectation (95%+) needed because reliability = reduced cascade urgences.

---

#### KPI C.5: INTERNAL DRIVER UTILIZATION RATE (%)

**Définition:**
```
Utilization = (Heures Conduite Réelle / Heures Contrat Disponibles) × 100%

Différent de Scoring Utilisation (C.1) car inclut heures non-opérateur
(pause, admin, maladie, congé)

Exemple: Octobre 2025
  Contrat chauffeur 1: 160h/mois (20 jours × 8h)
  Contrat chauffeur 2: 160h/mois
  Heures totales disponible: 320h

  Heures réelles travaillées: 310h (maladie chauffeur 2: 10h absent)
  Utilization rate: 310/320 = 97% ✓ VERT
```

**Baseline Actuel:** ~90-92% (taux absence normal ~8-10% France)
**Target Gedimat:** ≥95% (bonne disponibilité, peu d'absence)
**Fréquence Collecte:** Mensuel (HR timesheet)
**Propriétaire:** RH

**Formule Excel:**
```
=Heures_Travaillées_Réelles / Heures_Contrat_Disponible × 100%

Heures_Travaillées = Heures_Contrat - Heures_Absence
Heures_Absence = Maladie + Congé + Autre absence

Détail tracking:
  ├─ Heures contrat: 160h/mois chauffeur
  ├─ Maladie: (certificat médical days)
  ├─ Congé PTO: (planifié HR)
  ├─ Absence non-justifiée: (rare)
  └─ Travaillées = 160 - Maladie - Congé
```

**Interprétation Feu:**
- 🟢 VERT: ≥95% (disponibilité très bonne)
- 🟡 JAUNE: 90-95% (acceptable, normal absence rates)
- 🔴 ROUGE: <90% (problème absenteeism, investigate)

**Strategic Link:** Chauffeur absent = Consolidation delayed ou client wait.
  Budget impact: Each chauffeur absence 1 day = €300-500 urgence Médiafret surcoût.

---

## SECTION 3: EXCEL STRUCTURE COMPLÈTE

### 3.1 Data Input Sheet (Saisie Hebdomadaire)

**Objectif:** Entrée unique source données pour calcul tous KPIs
**Responsable:** Angélique (coordinatrice) + Finance (coûts)
**Fréquence:** Hebdomadaire (Jeudi soir pour rapport vendredi matin)
**Temps Requis:** 30-45 min/semaine

#### Structure Data Input

```
SHEET: "DATA_INPUT_WEEKLY"
├─ Ligne 1-5: En-têtes & Instructions
│  ├─ Semaine: [Dropdown 1-52]
│  ├─ Mois: [Auto-calc du dropdown]
│  ├─ Année: [2025]
│  └─ Date collecte: [Jeudi auto-date]
│
├─ Bloc A: TRANSPORT INTERNE (Chauffeurs <10t)
│  ├─ Chauffeur 1: [Name]
│  ├─ Heures travaillées: [Tachygraphe auto-import SI système]
│  ├─ KM parcourus: [Tachygraphe]
│  ├─ Tonnes livrées: [CRM total]
│  ├─ Incidents (casse/perte): [Count manual]
│  └─ Consolidation réalisée: [Count checkbox]
│
├─ Bloc B: AFFRÈTEMENT EXTERNE (Médiafret >10t)
│  ├─ Nombre enlèvements: [Count]
│  ├─ Tonnage total: [Sum factures Médiafret]
│  ├─ Coûts totaux: [€ from invoice]
│  ├─ Urgences express: [Count + €premium]
│  ├─ KM moyenne par trajet: [Estimate SI disponible]
│  └─ Incidents (non-livraison, etc): [Count]
│
├─ Bloc C: NAVETTES INTER-DÉPÔTS
│  ├─ Nombre trajets: [Count]
│  ├─ KM totaux: [Estimate]
│  ├─ Coûts chauffeur (allocation): [€ calculé]
│  └─ Tonnes redistribuées: [By dépôt]
│
├─ Bloc D: FOURNISSEURS SUIVI
│  ├─ Émeris
│  │  ├─ Enlèvements promis: [N]
│  │  ├─ Enlèvements réalisés: [N]
│  │  ├─ Retards >2h: [Count]
│  │  ├─ Consolidation avec autre fournisseur: [Yes/No + économie €]
│  │  └─ Note incident: [Free text]
│  ├─ Fournisseur B, C: [Identique structure]
│
├─ Bloc E: COMMANDES CLIENT
│  ├─ Nombre commandes: [Count CRM]
│  ├─ Tonnes livrées: [Sum]
│  ├─ Livrées à temps: [Count scoring]
│  ├─ Retards >48h: [Count]
│  ├─ Incidents (réclamation): [Count]
│  └─ NPS partial (if collected weekly): [Average score]
│
└─ Bloc F: COÛTS RÉSUMÉ WEEKLY
   ├─ Coûts totaux semaine: [Auto-sum]
   ├─ € par tonne: [Auto-calc]
   ├─ € par KM: [Auto-calc]
   ├─ Variance vs budget semaine: [Auto-calc]
   └─ Alertes détectées: [Auto-flag IF seuils]
```

#### Formules Excel Clés Input Sheet

```Excel
// KPI A.1: €/tonne
=SOMME(D:D) / SOMME(E:E)
// Coûts = Col D (somme interne+externe+navettes)
// Tonnes = Col E (somme livrées)

// KPI A.3: Taux remplissage
=MOYENNE(F:F)
// Col F = tonnage/30t par trajet

// KPI C.1: Utilisation chauffeur
=SOMME(Heures_Productif) / SOMME(Heures_Disponible)
// Heure productif = conduite + livraison (tachygraphe - pause)

// Alert Flag: IF €/tonne > 0.35 THEN "ALERTE DÉPASSEMENT"
=SI(SOMME(Coûts)/SOMME(Tonnes) > 0.35, "ALERTE DÉPASSEMENT", "OK")
```

---

### 3.2 Dashboard Sheet (Visualisation)

**Objectif:** Résumé exécutif KPIs avec graphes colorés et feux tricolores
**Format:** Une page A4 (PDF exportable pour réunions)
**Refresh:** Automatique depuis Data Input (formules liées)
**Audience:** PDG (monthly), Angélique (weekly pour alertes)

#### Layout Dashboard (Wireframe)

```
┌─────────────────────────────────────────────────────────────────────┐
│  GEDIMAT - TABLEAU DE BORD LOGISTIQUE MENSUEL - MOIS: OCTOBRE 2025 │
│  Rapport généré: 01/11/2025 | Confiance données: 80%               │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ SECTION A: COÛTS TRANSPORT                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  KPI A.1: €/TONNE             KPI A.2: €/KM          KPI A.3: REMPLISSAGE
│  ┌──────────────────┐         ┌──────────────────┐    ┌──────────────────┐
│  │                  │         │                  │    │                  │
│  │ €0.30/t          │         │ €2.00/km         │    │ 72%              │
│  │ 🟢 VERT (Target) │         │ 🟡 JAUNE (-5km)  │    │ 🟡 JAUNE (-3pts) │
│  │ vs Target €0.30  │         │ vs Target €2.00  │    │ vs Target 75%    │
│  │                  │         │                  │    │                  │
│  └──────────────────┘         └──────────────────┘    └──────────────────┘
│
│  KPI A.4: €/COMMANDE          KPI A.5: CONSOLIDATION KPI A.6: VARIANCE
│  ┌──────────────────┐         ┌──────────────────┐    ┌──────────────────┐
│  │ €118              │         │ 25%               │    │ -8% (Économie)   │
│  │ 🟢 VERT (Target) │         │ 🟡 JAUNE (-10%) │    │ 🟢 VERT (±5%)    │
│  │ vs Target €120   │         │ vs Target 35%    │    │ Budget: €18,000  │
│  │                  │         │                  │    │ Réel: €16,500    │
│  └──────────────────┘         └──────────────────┘    └──────────────────┘
│
│  GRAPHE TREND 12 MOIS: €/TONNE TREND (Line Chart)
│  ┌────────────────────────────────────────────────────────────────────┐
│  │ €0.50 │                                                             │
│  │ €0.40 │  ╱‾‾‾╲                                                     │
│  │ €0.30 │─╯    ╲___                                                  │
│  │ €0.20 │        Target                                              │
│  │ €0.10 │                                                             │
│  │  NOV  DEC  JAN  FEB  MAR  APR  MAY  JUN  JUL  AUG  SEP  OCT        │
│  └────────────────────────────────────────────────────────────────────┘
│  Interprétation: Trend baisse =✓ Optimisation efficace (Oct €0.30 ✓)
│
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ SECTION B: SERVICE CLIENT                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  KPI B.1: DÉLAI MOYEN          KPI B.2: PONCTUALITÉ   KPI B.3: RETARDS >48H
│  ┌──────────────────┐         ┌──────────────────┐    ┌──────────────────┐
│  │ 4.2 jours        │         │ 90%              │    │ 10%              │
│  │ 🟡 JAUNE (vs 3d) │         │ 🟡 JAUNE (vs 95%)│    │ 🔴 ROUGE (vs 3%)│
│  │ Acceptable, amélioration │         │ 4 jours retard  │    │ ALERTE ESCALADE │
│  │                  │         │                  │    │                  │
│  └──────────────────┘         └──────────────────┘    └──────────────────┘
│
│  KPI B.4: NPS (Q3)             KPI B.5: CSAT         KPI B.6: INCIDENTS
│  ┌──────────────────┐         ┌──────────────────┐    ┌──────────────────┐
│  │ +20              │         │ 80%              │    │ 2.1/100 liv      │
│  │ 🟡 JAUNE (vs 35)│         │ 🟡 JAUNE (vs 85%)│    │ 🟢 VERT (vs 1.5) │
│  │ Satisfaction acceptable    │ Proche cible      │    │ Très bon         │
│  │                  │         │                  │    │                  │
│  └──────────────────┘         └──────────────────┘    └──────────────────┘
│
│  KPI B.7: CHURN RATE           GRAPHE ÉVOLUTION NPS 12 MOIS (Line)
│  ┌──────────────────┐         ┌──────────────────────────────────────┐
│  │ 6%               │         │ +40 ╱‾‾‾╲                            │
│  │ 🟡 JAUNE (vs 3%)│         │ +30│ Target                          │
│  │ 6% acceptable    │         │ +20│╱     ╲___                        │
│  │ Risk: atttrition │         │ +10│         ╲ (Actuel: +20)        │
│  │                  │         │  0 │          ╲___                   │
│  └──────────────────┘         │    └──────────────────────────────────┘
│                                 NOV DEC JAN FEB MAR APR MAY JUN JUL...
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ SECTION C: EFFICACITÉ OPÉRATIONNELLE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  KPI C.1: UTILISATION CHAUFFEUR   KPI C.2: OVERRIDE RATE           │
│  ┌──────────────────────────────┐ ┌──────────────────────────────┐ │
│  │        Gauge Utilisation      │ │ 20% Overrides                │ │
│  │     ┌─────────────────┐        │ │ 🟢 VERT (Target <25%)       │ │
│  │     │ ▓▓▓▓▓▓▓▓░░░░░░░ │        │ │ Scoring confiant 80% cas    │ │
│  │     │ 85% (vs 80% tgt)│        │ │                              │ │
│  │     └─────────────────┘        │ │ Trend: 100% → 20% (post-Pass 6)
│  │ 🟢 VERT (Bonne util)          │ │ Adoption scoring croissance  │ │
│  └──────────────────────────────┘ └──────────────────────────────┘ │
│                                                                     │
│  KPI C.3: WORKLOAD ANGÉLIQUE      KPI C.4: SUPPLIER RELIABILITY   │
│  ┌──────────────────────────────┐ ┌──────────────────────────────┐ │
│  │ 10h/semaine                  │ │ Émeris: 87% 🟡               │ │
│  │ 🟢 VERT (Target 7-9h post-auto) │ Fournisseur B: 94% 🟡        │ │
│  │ Baseline 11-18h → 10h (amélioration) │ Fournisseur C: 91% 🟡 │ │
│  │                              │ │ Moyenne: 91% (vs 95% tgt)    │ │
│  │ Priorité: Auto alertes (API) │ │ Action: Négociation SLA      │ │
│  └──────────────────────────────┘ └──────────────────────────────┘ │
│                                                                     │
│  KPI C.5: DRIVER AVAILABILITY                                       │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 97% (310h / 320h contrat)                                    │ │
│  │ 🟢 VERT (Target ≥95%, taux absence normal)                 │ │
│  │ Absence: 10h maladie (chauffeur 2). Normal.                 │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│ ALERTES AUTOMATIQUES & ACTIONS REQUISES                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 🔴 CRITIQUE: Retards >48h = 10% (vs target 3%)                    │
│    Action: Analyser Émeris retard (reliability 87%) + Médiafret    │
│    Escalade: Email PDG + Direction Ops (protocol: escalade imméd)  │
│                                                                     │
│ 🟡 MOYEN: NPS +20 (vs target +35) - Satisfaction en baisse        │
│    Action: Interviewer clients Q3 (focus groupe retards identifiés)│
│    Timeline: Semaine N+1                                           │
│                                                                     │
│ 🟡 MOYEN: Consolidation 25% (vs target 35%) - Opportunity gap     │
│    Action: Analyser blocages (client refuse attendre?) + plan      │
│    Timeline: Semaine N+1                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

LÉGENDE FEUX:
🟢 VERT  = Dans cible OU Acceptable (no action)
🟡 JAUNE = Attention (monitoring) OU Amélioration possible
🔴 ROUGE = Dépassement critique (action immédiate)

NOTES MÉTHODOLOGIE:
- Données source: CRM Gedimat, tachygraphe chauffeurs, factures Médiafret
- Baseline: M-1 & M-12 (month-over-month & year-over-year)
- Confiance: 80% (données validées via audit Q3 2025)
- Prochaine revue: 01/11/2025 (réunion PDG 10h30)
```

---

### 3.3 Historical Trends Sheet (24 Mois Rolling)

**Objectif:** Analyse tendances long-terme + Comparaison YoY
**Fréquence Refresh:** Mensuel (auto-update depuis Data Input)
**Audience:** Direction Franchise (trimestriel deep-dive), Finance (ongoing)

#### Structure Historical Trends

```
SHEET: "HISTORICAL_TRENDS_24M"

Colonnes:
├─ Mois (format: Nov-2023, Dec-2023, ..., Oct-2025)
├─ KPI A.1 €/tonne
├─ KPI A.2 €/km
├─ KPI A.3 Remplissage %
├─ KPI A.4 €/commande
├─ KPI A.5 Consolidation %
├─ KPI A.6 Variance budget %
├─ KPI B.1 Délai moyen (j)
├─ KPI B.2 Ponctualité %
├─ KPI B.3 Retards >48h %
├─ KPI B.4 NPS (trim only)
├─ KPI B.5 CSAT %
├─ KPI B.6 Incidents/100
├─ KPI B.7 Churn %
├─ KPI C.1 Utilisation %
├─ KPI C.2 Override %
├─ KPI C.3 Workload Angélique (h/wk avg)
├─ KPI C.4 Supplier Reliability %
└─ KPI C.5 Driver Availability %

Rows: Nov-2023 à Oct-2025 (24 mois)

EXAMPLE ROW (Oct-2025):
  Oct-2025 | €0.30 | €2.00 | 72% | €118 | 25% | -8% | 4.2j | 90% | 10% | +20 | 80% | 2.1 | 6% | 85% | 20% | 10h | 91% | 97%
```

#### YoY Comparison (Pivot Table)

```
YoY ANALYSIS:
┌─────────────────────────────────────────────────────────────────┐
│ METRIC                │ Oct-2024 │ Oct-2025 │ Change   │ Trend │
├─────────────────────────────────────────────────────────────────┤
│ €/tonne               │ €0.40    │ €0.30    │ -25%     │ ↓ Good│
│ €/km                  │ €2.25    │ €2.00    │ -11%     │ ↓ Good│
│ Remplissage           │ 65%      │ 72%      │ +7%      │ ↑ Good│
│ Délai moyen           │ 4.8j     │ 4.2j     │ -0.6j    │ ↓ Good│
│ Ponctualité           │ 85%      │ 90%      │ +5%      │ ↑ Good│
│ Retards >48h          │ 15%      │ 10%      │ -5%      │ ↓ Good│
│ NPS (Q4 vs Q3)        │ +10      │ +20      │ +10      │ ↑ Good│
│ CSAT                  │ 75%      │ 80%      │ +5%      │ ↑ Good│
│ Churn                 │ 8%       │ 6%       │ -2%      │ ↓ Good│
│ Supplier Reliability  │ 88%      │ 91%      │ +3%      │ ↑ Good│
└─────────────────────────────────────────────────────────────────┘

INSIGHT: Oct-2025 MAJORITY metrics improved YoY (post-Pass 6 optimization)
```

#### Graphes Historiques (Excel Charts)

```
Chart 1: TREND €/TONNE (12-month line chart)
┌────────────────────────────────────────────────────────┐
│ €0.50 │  NOV DEC JAN FEB MAR APR MAY JUN JUL AUG SEP OCT
│ €0.40 │   ●────────────────●──────────────────●
│ €0.30 │               ┌─────                  ╱╲
│ €0.20 │               │    ╲___             ╱  ╲
│ €0.10 │               │  Target           ╱    ╲
│        └────────────────────────────────────────────────┘
│ Trend: ↓ Declining (baseline €0.40 → target €0.30 reached Oct-2025)

Chart 2: PONCTUALITÉ ÉVOLUTION (12-month bar + trend)
┌────────────────────────────────────────────────────────┐
│ 100% │
│  95% │  ┬┬                               Target ───────
│  90% │  ││    ┬                          ╱╲
│  85% │  ││ ┬┬ │ ┬┬┬                     ╱  ╲
│  80% │  ││ ││ │ │││                    ╱    ╲
│  75% │  ││ ││ │ │││                   ╱      ╲
│        └────────────────────────────────────────────────┘
│        NOV DEC JAN FEB MAR APR MAY JUN JUL AUG SEP OCT
│ Trend: ↑ Improving (baseline 80% → current 90%)

Chart 3: 4-QUADRANT DASHBOARD (Coûts vs Satisfaction)
┌────────────────────────────────────────────────────────┐
│ HIGH │ ZONE A: High Cost, High Satisfaction
│SATIS │  (Rare, means price premium justified)
│  80% │  • Oct-2024: (€0.40, 75%)
│      │
│      │ ZONE B: Low Cost, High Satisfaction (IDEAL)
│ 70% │  • Oct-2025: (€0.30, 80%) ← TARGET
│      │
│ 60% │ ZONE C: High Cost, Low Satisfaction (BAD)
│      │                    ZONE D: Low Cost, Low Satis
│ 50% │
│      └────────────────────────────────────────────────┘
│          €0.30  €0.35  €0.40  €0.45  €0.50
│        (LOW COST ─────────────→ HIGH COST)
│
│ Interpretation: Oct-2025 in ZONE B (ideal position)
│ Movement: Oct-2024 → Oct-2025 = Quadrant down-left (improvement)
```

---

## SECTION 4: ALERTES AUTOMATIQUES & ESCALADE

### 4.1 Decision Tree Alertes (If-Then Logic)

```
ALERT LOGIC ENGINE (Exécuté quotidiennement via Excel + macro):

IF KPI_A1_COÛT_TONNE > €0.35 THEN
  ├─ Severity: MOYEN
  ├─ Email: Finance
  ├─ Message: "Coût/tonne dépassement cible (€0.35) - Analyser Médiafret"
  ├─ Data Analysis: Comparer vs mois N-1 (volatilité?)
  └─ Action Suggérée: Réduire volume Médiafret 5-10% ou consolider mieux

IF KPI_B3_RETARDS_48H > 8% THEN
  ├─ Severity: CRITIQUE
  ├─ Email: PDG + Direction Ops + Logistique
  ├─ Message: "ALERTE SERVICE - Retards >48h détectés (8%+) - Action immédiate"
  ├─ Root Cause: Analyser fournisseur? Médiafret? Chauffeur?
  └─ Escalade: Phone call PDG si >15%

IF KPI_B4_NPS < +25 THEN
  ├─ Severity: MOYEN
  ├─ Email: Commercial + PDG
  ├─ Message: "NPS baisse ou faible (+25) - Risk churn client"
  ├─ Data Analysis: Focus groupe clients détracteurs (raison?)
  └─ Action: Improvement plan Q+1

IF KPI_C3_WORKLOAD_ANGÉLIQUE > 15h/semaine THEN
  ├─ Severity: MOYEN
  ├─ Email: RH + Logistique
  ├─ Message: "Charge Angélique excessive (15h+) - Bottleneck risk"
  ├─ Root Cause: Automatisation insuffisante? Cas complexes?
  └─ Action: Embauche support ou API automation prioritaire

IF KPI_A3_REMPLISSAGE < 65% THEN
  ├─ Severity: BAS
  ├─ Email: Logistique
  ├─ Message: "Taux remplissage faible (65%) - Consolidation opportunity"
  ├─ Data Analysis: Quels trajets? Pourquoi pas consolidés?
  └─ Action: Audit processus consolidation

IF KPI_C4_SUPPLIER_RELIABILITY < 85% (par fournisseur) THEN
  ├─ Severity: MOYEN
  ├─ Email: Achats + Logistique
  ├─ Message: "[Fournisseur] unreliable (85%) - Escalade SLA"
  ├─ Action: Conversation fournisseur + written SLA commitment
  └─ Follow-up: Retest reliability 4 semaines

IF Variance_Budget > +10% (dépense) THEN
  ├─ Severity: MOYEN
  ├─ Email: Finance + PDG
  ├─ Message: "Budget dépassement (>10%) - Analyse déviations"
  ├─ Root Cause: Quelle ligne? (Chauffeur? Médiafret? Urgences?)
  └─ Action: Forecast N+1 ajusté

IF KPI_A5_CONSOLIDATION < 20% THEN
  ├─ Severity: BAS-MOYEN
  ├─ Email: Logistique
  ├─ Message: "Consolidation opportunity gap - Analyser blocages"
  ├─ Root Cause: Client refuse attendre? SLA trop tight?
  └─ Action: Plan amélioration consolidation Q+1
```

### 4.2 Escalade Matrix

```
┌────────────────────────────────────────────────────────────────────┐
│ ESCALADE LEVELS & CONTACTS                                         │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ LEVEL 1 - ALERTES JAUNES (Monitoring)                            │
│ ├─ Destinataires: Team leads (Logistique, Finance)              │
│ ├─ Format: Email auto-généré Excel                              │
│ ├─ Timing: Jeudi soir (rapport weekly)                          │
│ ├─ Action: Monitoring serré, report hebdo                       │
│ └─ Exemples: Remplissage 70%, Consolidation 20%, NPS +25       │
│                                                                    │
│ LEVEL 2 - ALERTES ORANGE (Investigation)                        │
│ ├─ Destinataires: Angélique + Finance + Logistique              │
│ ├─ Format: Email + call conference 30min semaine N+1            │
│ ├─ Timing: Vendredi matin ou lundi                              │
│ ├─ Action: RCA (root cause analysis) + action plan              │
│ └─ Exemples: €/tonne >0.35, Retards 5-8%, CSAT 75-85%         │
│                                                                    │
│ LEVEL 3 - ALERTES ROUGES (CRITIQUE)                             │
│ ├─ Destinataires: PDG + Direction Ops + ALL stakeholders        │
│ ├─ Format: Email urgent + phone call immédiate + meeting <2h    │
│ ├─ Timing: Same day detection ou Monday AM latest              │
│ ├─ Action: Crisis protocol - immediate corrective               │
│ └─ Exemples: Retards >10%, Service dégradation >15%, Fournisseur fail
│                                                                    │
│ ESCALADE SPÉCIALE - SUPPLIER FAILURE                             │
│ ├─ IF Supplier Reliability <70% deux mois consécutifs           │
│ ├─ THEN: Management discussion + written commitment             │
│ ├─ Timeline: Within 1 week                                       │
│ ├─ Outcome: SLA contract OR alternative supplier audit          │
│ └─ Owner: Achats directeur                                      │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## SECTION 5: GUIDE INTERPRÉTATION (1 Page Executive)

### 5.1 Comment Lire les Feux Tricolores

```
FEUX TRICOLORES EXPLIQUÉS:

🟢 VERT = Cible atteinte, pas action requise
  Interpétation: KPI dans envelope attendue
  Action: Maintenir niveau, continuer optimisation incremental
  Exemple: €/tonne €0.30 = Vert (vs target €0.30)

🟡 JAUNE = Attention, monitoring accéléré ou amélioration possible
  Interprétation: KPI acceptable mais marginal vs target
  Action: Analyser cause (trend?), plan minor improvement Q+1
  Exemple: Ponctualité 90% = Jaune (vs target 95%) → investiguer 5% gap

🔴 ROUGE = Dépasser critique, action immédiate requise
  Interprétation: KPI inacceptable, risk business
  Action: Root cause analysis immédiate, executive escalade
  Exemple: Retards >48h = 10% → Escalade PDG, intervention urgente
```

### 5.2 Action Guide Par KPI En Rouge

```
SI KPI A (COÛTS) EN ROUGE:

A.1 €/TONNE > €0.38:
  ├─ Diagnostic: A-t-on utilisé trop Médiafret (externe cher)?
  ├─ Data check: Comparer volumes interne vs Médiafret
  ├─ Action 1: Augmenter consolidation milkrun (< coûteux)
  ├─ Action 2: Négocier Médiafret (-5-10% tarif)
  ├─ Action 3: Audit chauffeur (utilisation 80%+?)
  └─ Timeline: 2 semaines plan, 4 semaines exécution

A.3 REMPLISSAGE < 65%:
  ├─ Diagnostic: Pourquoi camions demi-pleins?
  ├─ Data check: Analyser par trajet (% par route)
  ├─ Action 1: Augmenter consolidation (regrouper commandes)
  ├─ Action 2: Ajuster fréquence Médiafret (moins de petits trajets)
  └─ Timeline: Immédiat, amélioration dans 2 semaines

A.5 CONSOLIDATION < 20%:
  ├─ Diagnostic: Pourquoi pas regrouper commandes?
  ├─ Root Causes Possibles:
  │  ├─ Client SLA tight (ne peut pas attendre 48h consolidation)
  │  ├─ Fournisseur retard (pas assez de stock simultané)
  │  └─ Process not communicated (Angélique ne propose pas)
  ├─ Action: Analyser cas manqués (quick audit 10 cas)
  └─ Timeline: Semaine N+1 analysis, plan N+2

───────────────────────────────────────────────────────────

SI KPI B (SERVICE CLIENT) EN ROUGE:

B.2 PONCTUALITÉ < 85%:
  ├─ Diagnostic: Trop de retards livraison client
  ├─ Data check: Analyser pattern (jour semaine? région? fournisseur?)
  ├─ Root Causes Possibles:
  │  ├─ Fournisseur delay (supplier reliability faible?)
  │  ├─ Transport delay (chauffeur ou Médiafret non-optimal route)
  │  ├─ SLA client trop tight (impossible to honor)
  │  └─ Client dernière minute change (rush order)
  ├─ Action 1: Audit top 5 retards (causality?)
  ├─ Action 2: Review SLA negotiation (realistic targets?)
  └─ Timeline: Analysis <1 semaine, corrective plan N+1

B.3 RETARDS >48H > 8%:
  ├─ Diagnostic: CRITIQUE - Service dégradée
  ├─ Escalade: Email PDG + phone call immédiate
  ├─ Root Cause Analysis: Urgent (same day if possible)
  │  ├─ Fournisseur fail? (Émeris reliability audit)
  │  ├─ Médiafret fail? (call for capacity issue)
  │  ├─ Chauffeur interne lack? (absence, saturation)
  │  └─ Scoring fail? (wrong dépôt assigned, cascade delays)
  ├─ Action: Immediate corrective (add Médiafret? chauffeur? reroute?)
  └─ Timeline: Decision <24h, execution immediate

B.4 NPS < +25:
  ├─ Diagnostic: Clients not satisfied, risk churn
  ├─ Data check: Review detractor comments (why unhappy?)
  ├─ Root Causes Likely:
  │  ├─ Service (Retards >48h identifiés dans KPI B.3?)
  │  ├─ Price (cliente think expensive vs competitor?)
  │  └─ Relationship (communication insufficient?)
  ├─ Action 1: Focus group detractors (10 calls, 30min each)
  ├─ Action 2: Improvement plan based on feedback
  └─ Timeline: Focus group semaine N+1, plan N+2

───────────────────────────────────────────────────────────

SI KPI C (OPÉRATIONS) EN ROUGE:

C.1 UTILISATION < 70%:
  ├─ Diagnostic: Chauffeur not fully productive
  ├─ Root Causes Likely:
  │  ├─ Routes non-optimisées (VRP scoring could help)
  │  ├─ Client attente long (client facility bottleneck)
  │  ├─ Chauffeur absence/maladie (RH issue)
  │  └─ Volume commandes low (seasonality?)
  ├─ Action 1: Audit where time lost (time study 3 days)
  ├─ Action 2: Optimization plan (routes? consolidation? scheduling?)
  └─ Timeline: Analysis 1 semaine, corrective N+1

C.3 WORKLOAD ANGÉLIQUE > 15h/semaine:
  ├─ Diagnostic: Single-point-of-failure, sustainability risk
  ├─ Root Causes:
  │  ├─ Alertes fournisseur manually processed (need API automation)
  │  ├─ Scoring overrides excessive (need Excel macro automation)
  │  ├─ Incidents high (process fail?)
  │  └─ Volume growth (capacity expansion needed)
  ├─ Action 1: Automation prioritaire (API fournisseur alert)
  ├─ Action 2: Hire part-time support (24-30h/week) if trend continues
  └─ Timeline: Automation 4-6 weeks, hiring 2-3 weeks process

C.4 SUPPLIER RELIABILITY < 85%:
  ├─ Diagnostic: Fournisseur unreliable, cascade urgences
  ├─ Action 1: Management conversation (written SLA commitment)
  ├─ Action 2: Performance improvement plan (4-week trial)
  ├─ Action 3: If no improvement → Alternative supplier audit
  ├─ Timeline: Conversation <1 week, trial 4 weeks, decision 5 weeks
  └─ Escalation: Escalade to purchasing director if continue failing
```

### 5.3 MONTHLY REVIEW CHECKLIST - PDG 30MIN MEETING

```
CHECKLIST POUR RÉUNION MENSUELLE (Premier lundi 10h30, 30min):

PARTICIPANTS: PDG + Finance + Logistique (Angélique) + (optional) Commercial

PRE-MEETING (Friday before, 15min prep):
[ ] Télécharger dashboard latest (refresh data input Excel)
[ ] Identifier tous KPIs ROUGE ou JAUNE
[ ] Préparer RCA (root cause analysis) pour anomalies
[ ] Préparer 2-3 recommendations d'action (avec coûts)
[ ] Check vs previous month (trends improving or worsening?)

OPENING (2min):
[ ] Confirm previous month actions completed? Yes/No/Partial
[ ] Summarize key metrics (30-second recap)

SECTION A: COÛTS TRANSPORT (8min):
[ ] €/tonne: Target atteint? Trend?
[ ] Variance vs budget: Why deviation if exists?
[ ] Consolidation rate: On track 35% target?
[ ] Supplier reliability: Any rogue supplier?
→ Decision needed?: Negotiate Médiafret contract? Increase milkrun?

SECTION B: SERVICE CLIENT (8min):
[ ] Retards >48h: Any ROUGE alert?
[ ] NPS/CSAT: Customer satisfaction healthy?
[ ] Churn: Losing clients?
[ ] Incidents: Safety/quality issues?
→ Decision needed?: Root cause for delays? Client interviews needed?

SECTION C: OPERATIONS (7min):
[ ] Chauffeur utilization: Productive enough?
[ ] Angélique workload: Sustainable? Support needed?
[ ] Supplier reliability: SLA breaches?
→ Decision needed?: Hire support for Angélique? API automation?

FINANCIAL IMPACT (3min):
[ ] Total coûts vs budget: On track?
[ ] ROI optimisations (Pass 6): Gain vs plan?
[ ] Forecast N+1: Any expectation changes?

CLOSING & NEXT STEPS (2min):
[ ] Confirm action owners + deadlines
[ ] Schedule next month review
[ ] Escalate ROUGE items if needed (crisis protocol)

OUTPUTS:
[ ] Meeting minutes with actions + owners + dates
[ ] Updated KPI dashboard (PDF export for files)
[ ] Email summary to extended team (Finance, Commercial, HR)
```

---

## SECTION 6: PROCESSUS COLLECTE DONNÉES

### 6.1 Responsabilités & Timeline Hebdomadaire

```
PROCESSUS COLLECTE DONNÉES - GEDIMAT LOGISTIQUE

ACTEUR: Angélique (Coordinatrice Logistique) = Data Owner Principal
BACKUP: Finance (coûts affrètement), HR (chauffeur availability)
TOOLS: Excel (manual input) + CRM (auto-extract si possible) + Tachygraphe

TIMELINE HEBDOMADAIRE:

LUNDI-MERCREDI (Data Collection):
├─ Lundi: CRM export commandes (livrées, dates) → Import Excel "Data_Input"
├─ Mercredi: Tachygraphe export KM chauffeurs → Import Excel
├─ Mercredi: Médiafret invoice (if received) → Input coûts, tonnage
├─ Mercredi: Manual survey incidents (Angélique) → Input "Data_Input"

JEUDI (Data Entry + Validation):
├─ 14h: Angélique complete data input remaining fields (consolidation, override)
├─ 15h: Excel refresh (all KPIs auto-calculate from formulas)
├─ 15h30: Validation: Check for missing data, impossible values, anomalies
├─ 16h: Generate weekly alert report (if ROUGE/ORANGE alerts exist)
├─ 16h30: Quick call with logistics team (15min) to confirm data & discuss alerts

JEUDI EVENING:
├─ 17h: Email alert report to PDG (if ROUGE) or Finance
├─ 17h30: Archive "Data_Input_[Week]_[Year]" for audit trail

FRIDAY (Reporting):
├─ 08h: Dashboard refresh (historical trends auto-update)
├─ 10h: Email dashboard PDF to stakeholders (PDG, Finance, Commercial)
├─ 12h: Publish to shared drive (Data → Dashboard_Archive)
└─ EOD: Close data entry (lock cells prevent accidental overwrite)
```

### 6.2 Sources de Données & Validations

```
DATA SOURCE MATRIX:

KPI A.1 €/TONNE:
├─ Source 1: Chauffeur coûts (Finance - Paie) ← Salaire allocation
├─ Source 2: Carburant (Finance - Accounting) ← Diesel invoice
├─ Source 3: Affrètement Médiafret (Invoice) ← Monthly invoice
├─ Source 4: Tonnes livrées (CRM) ← Order shipment dates/quantities
├─ Validation: Cross-check invoice total vs sum coûts sections (balance?)
└─ Frequency: Mensuel (M+3 pour paie, M+5 pour Médiafret usually)

KPI A.3 TAUX REMPLISSAGE:
├─ Source: Médiafret bordereau (per shipment tonnage + truck capacity)
├─ Manual input: Angélique records % per trajet based on invoice
├─ Validation: Compare vs Médiafret "loaded weight" field (precision check)
└─ Frequency: Hebdomadaire (bordereau received ~same day)

KPI B.1-B.3 DÉLAI/PONCTUALITÉ/RETARDS:
├─ Source: CRM (order dates vs delivery dates) ← Automated IF CRM system
├─ Source: Manual (Angélique) IF no CRM integration
├─ Data points needed:
│  ├─ Commande numéro
│  ├─ Date commande client
│  ├─ Date promise au client
│  ├─ Date livraison réelle
│  └─ Statut (à temps / retard / reason si retard)
├─ Validation: Compare CRM vs chauffeur signatures (double-check delivery date)
└─ Frequency: Mensuel (compile from daily CRM logs)

KPI B.4 NPS (Trimestriel):
├─ Source: Client survey (email/phone)
├─ Sampling: 30-50 clients représentatives (mix grandes+PME)
├─ Question: "Recommanderiez-vous Gedimat sur échelle 0-10?"
├─ Timing: End of quarter (sept 30, dec 31, etc.)
├─ Analysis: Categorize réponses (9-10=Promoteur, 7-8=Passif, 0-6=Detracteur)
└─ Frequency: Trimestriel (collect, analyze, report M+3)

KPI C.1 UTILISATION CHAUFFEUR:
├─ Source 1: Tachygraphe (truck digital recorder) ← Hours driving
├─ Source 2: CRM timestamps (client arrival/departure) ← Delivery hours
├─ Source 3: Timesheet (Angélique manual) ← Breaks, admin time
├─ Calculation:
│  Productif = Tachygraphe driving + CRM delivery hours
│  Breaks/pause = Standard 30-60min deduct
│  Disponible = Contrat hours (160h/month)
│  Utilisation = Productif / Disponible
├─ Validation: Compare Tachygraphe vs CRM (should overlap for same periods)
└─ Frequency: Mensuel

KPI C.3 WORKLOAD ANGÉLIQUE:
├─ Source: Timesheet Angélique (manual logging)
├─ Categories tracked:
│  ├─ Supplier follow-up (hours/week)
│  ├─ Scoring/arbitrage (hours/week)
│  ├─ Incident management (hours/week)
│  ├─ Consolidation planning (hours/week)
│  └─ Meetings/reporting (hours/week)
├─ Tool: Excel timesheet (daily entry) OR toggle timer (app like Harvest)
├─ Validation: Total hours vs Angélique actual availability (sanity check)
└─ Frequency: Hebdomadaire (weekly average)

KPI C.4 SUPPLIER RELIABILITY:
├─ Source: Médiafret delivery dates + Promises
├─ Data: [Supplier name, Pickup date promised, Pickup date actual, On-time Y/N]
├─ Manual input: Angélique tracks per fournisseur (Émeris, B, C)
├─ Validation: Cross-check calendar (was promised date realistic?)
└─ Frequency: Mensuel (compile daily observations)
```

### 6.3 Data Quality & Audit Trail

```
DATA QUALITY CONTROLS:

Check 1 - MISSING DATA:
├─ Excel formula flags blank cells: IF(ISBLANK(cell), "MISSING DATA", "OK")
├─ Weekly validation: Angélique reviews + explains any blanks
└─ Action: No dashboard refresh IF critical data missing

Check 2 - OUTLIERS (Impossible Values):
├─ €/tonne <€0.10 OR >€1.00 = Flagged (unrealistic)
├─ Remplissage >100% = Flagged (impossible)
├─ Utilisation >110% = Flagged (overwork)
├─ Action: Investigate, correct source data, re-calculate

Check 3 - RECONCILIATION:
├─ Monthly: Sum coûts sections = Total invoice coûts (balance check)
├─ Monthly: Total tonnes input = CRM order total (volume match)
├─ Monthly: Chauffeur hours input = Tachygraphe export (time match)
└─ If mismatch >5% = Stop, investigate, correct

Check 4 - AUDIT TRAIL:
├─ Version control: "Data_Input_W44_2025.xlsx" (timestamp)
├─ Change log: Track who edited, when, what changed
├─ Backup: Archive weekly to shared drive (immutable copy)
├─ Retention: Keep all versions 24 months (legal/analysis purposes)

Check 5 - VALIDATION BY DOMAIN EXPERT:
├─ Weekly (Thursday 15h30): Angélique reviews data accuracy
├─ Monthly (M+3): Finance validates coûts sections
├─ Monthly (M+3): Logistics (Director) reviews KPI sanity
└─ Quarterly: External audit (if major discrepancy detected)
```

### 6.4 Data Entry Time Estimate & Tools

```
EFFORT REQUIRED (Estimate):

Per Week:
├─ CRM export + data input: 10-15 min (if automated export)
├─ Tachygraphe import: 5 min (if automated)
├─ Médiafret invoice: 5 min (copy/paste)
├─ Manual incidents/consolidation: 15 min (observation-based)
├─ Validation + error checking: 10 min
└─ TOTAL: 30-45 min per week (< 1 hour efficient)

Per Month:
├─ Data input (4 weeks): 2-3 hours
├─ Monthly reconciliation: 30 min
├─ Reporting/export: 30 min
├─ Analysis/anomaly investigation: 1 hour (as needed)
└─ TOTAL: 4-5 hours per month (1-1.5 hours per week average)

TOOLS REQUIRED:
├─ Excel (primary): Dashboard template, data input, formulas
├─ CRM export: Automated if possible (API or weekly export)
├─ Tachygraphe reader: USB export from truck device
├─ Email/shared drive: Alert distribution, archive
├─ Optional enhancements (Future):
│  ├─ Google Sheets (cloud-based, real-time)
│  ├─ Power BI (more advanced visualization)
│  ├─ API connectors (fournisseur alerts auto-import)
│  └─ Mobile app (field data entry for Angélique)
```

---

## SECTION 7: MAINTENANCE & ÉVOLUTION DASHBOARD

### 7.1 Calibrage Trimestriel

```
QUARTERLY CALIBRATION (Fin trimestre, 2h session):

Q+1 Review Meeting (tous experts):

AGENDA:
1. Verify KPI targets remain realistic (vs actuel performance)
   ├─ IF €/tonne consistently 0.28 → Lower target to 0.28 (motivational)
   ├─ IF Retard >48h stuck at 8% → Investigate root cause (not process)
   └─ IF NPS plateaus at +25 → Identify saturation ceiling

2. Scoring formula recalibration (if Override >25%)
   ├─ Analyze override patterns (which types most overridden?)
   ├─ IF "Proximity rule overridden" often → Reduce proximity weight
   ├─ IF "Urgency rule overridden" often → Increase urgency weight
   └─ Document formula change reason + date (audit trail)

3. Alert thresholds review
   ├─ IF 90% weeks trigger ORANGE alert → Threshold too tight (lower)
   ├─ IF <5% weeks trigger alert → Threshold too loose (raise)
   └─ Goal: ~10-20% weeks with actionable alerts (not noise)

4. Data quality improvements
   ├─ IF recurring data gaps → Automate collection (API/CRM export)
   ├─ IF manual input errors → Retrain Angélique or simplify form
   └─ IF outlier detections → Investigate source (real or data error?)

OUTPUT:
├─ Updated KPI targets (if changed)
├─ Revised scoring formula (if changed)
├─ Adjusted alert thresholds
├─ Documented decisions & dates (audit trail)
└─ Team communication: "Q+1 Dashboard Update - Targets Adjusted"
```

### 7.2 Annual Review & Audit

```
ANNUAL DASHBOARD AUDIT (End of year, 4h session):

PARTICIPANTS: PDG + Finance Director + IT + Gedimat Logistics Expert (external)

AGENDA:

1. VALIDATION: Are all 18 KPIs still relevant?
   ├─ Remove KPI if: No longer tracked, redundant with another, not actionable
   ├─ Add KPI if: New business priority emerged, gaps identified
   └─ Result: KPI list for Year+1 (propose modifications)

2. DATA QUALITY REVIEW:
   ├─ Audit 6 months of data (random sampling)
   ├─ Verify against source documents (invoices, CRM, tachygraphe)
   ├─ Assess reconciliation % (target: >95% match)
   ├─ Identify systematic errors (if any) → corrective action
   └─ Result: Data quality score (A/B/C rating)

3. ROI VALIDATION:
   ├─ Calculate actual savings vs Plan (Pass 6 expected €8-15k Year 1)
   ├─ Analyze reasons for variance (achieved more? less? why?)
   ├─ Project Year+1 savings (based on actual trends)
   └─ Result: Updated ROI forecast for executive planning

4. PROCESS IMPROVEMENTS:
   ├─ Interview data entry owner (Angélique): "What's painful? What can improve?"
   ├─ Review user feedback from weekly/monthly reviewers
   ├─ Identify automation opportunities (especially for Angélique workload)
   └─ Result: Prioritized improvements for Year+1 roadmap

OUTPUT:
├─ Annual Audit Report (10-page, submitted to PDG)
├─ KPI list refresh (any additions/deletions)
├─ Data quality certification (if >90% match = Certified)
├─ Year+1 Roadmap (automation priorities, process improvements)
└─ Budget proposal (any new tools/resources for Year+1)
```

---

## CONCLUSION & RÉFÉRENCES

### Dashboard Statut

```
STATUS: PASS 7 COMPLETE - Dashboard Mensuel KPI spécification prêt déploiement

CONTENU LIVRÉ:
✓ Section 1: Audience & Fréquence (3 profils utilisateur, calendrier réunions)
✓ Section 2: Architecture Dashboard (18 KPIs × 3 sections = COÛTS/SERVICE/OPÉRATIONS)
✓ Section 3: Excel Structure (Data Input + Dashboard Sheets + Historical Trends)
✓ Section 4: Alertes Automatiques (If-Then logic + Escalade matrix)
✓ Section 5: Guide Interprétation (Feux, Action Guide, Monthly Checklist)
✓ Section 6: Processus Collecte Données (Sources, Timeline, Data Quality)
✓ Section 7: Maintenance (Calibrage Q, Annual Audit)

PROCHAINES ÉTAPES (PASS 8+):
1. Finaliser template Excel (technical build, test formulas)
2. Pilot deployment (1 month with Angélique, gather feedback)
3. Fine-tune based on real data (dashboard vs reality validation)
4. Full rollout (Monthly reviews with all stakeholders)
5. Q+1 Calibration (targets, scoring formula, alert thresholds)

CONFIANCE: 75% (specification complète, implémentation technique requise)
```

### Documents Références

```
DOCUMENTATION COMPLÈTE:
├─ PASS 1: Gedimat Financière Overview
├─ PASS 2: Gedimat Coûts Transport Analysis
├─ PASS 3: Edge Cases & Sensibilité Analysis
├─ PASS 4 Agent 1: Logistique VRP/TSP & KPI Selection
├─ PASS 4 Agent 2: Finance ROI & Arbitrage Thresholds
├─ PASS 6: Decision Rules & Scoring MDVRP (À venir)
├─ PASS 7 Tool 1: Process Map Gedimat (À venir)
├─ PASS 7 Tool 2: Stakeholder Communication Plan (À venir)
└─ PASS 7 Tool 3: Dashboard Mensuel KPI (THIS DOCUMENT)
```

---

**END OF SPECIFICATION**

*Document créé: 16 novembre 2025*
*Status: PASS 7 Agent 3 Complete - Dashboard Mensuel Specification Prêt Déploiement*
*Prochaine étape: Technical build Excel + Pilot deployment (PASS 8)*

