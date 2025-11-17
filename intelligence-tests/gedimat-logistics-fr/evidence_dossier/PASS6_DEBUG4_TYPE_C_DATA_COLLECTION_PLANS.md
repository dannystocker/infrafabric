# PASS 6 - DEBUG AGENT 4: Plans de Collecte de Données pour Contradictions Type C
## Résolution des Blocages Dépendants de Données - Gedimat Logistique

**Date:** 16 novembre 2025
**Agent Responsable:** Pass 6 Debug Agent 4 (Type C Resolution)
**Source:** Pass 5 Agent 3 (Cartographie Tensions) – Contradictions C1-C4
**Périmètre:** 4 contradictions de Type C (données manquantes bloquantes)
**Objectif:** Plans d'action détaillés pour chaque contradiction, décision arborescente, recommandations intérimaires

---

## EXECUTIVE SUMMARY

**4 Contradictions Type C Identifiées (Pass 5 Agent 3):**
- **C1:** Investissement WMS/ROI dépend croissance revenue inconnue (€50-150k décision bloquée)
- **C2:** Urgence client réelle % (70-80% estimée vs réalité potentielle 40-60%)
- **C3:** Pertes commandes détail (€3-12k/an variance énorme, churn CRM non documenté)
- **C4:** Capacité Médiafret urgences + faisabilité contrat (ad-hoc actuellement)

**Impact Total:** ~€100-150k décisions différées + €30-50k risque erreur si mauvaises hypothèses

**Timeline Data Collection:** 2-4 mois (parallélisable)
**Coût Total Collecte:** €2,500-3,500 + 120-180 heures travail
**ROI Investissement Data:** 15-25x (évite erreurs budget majeures)

---

## CONTRADICTION C1: INVESTISSEMENT WMS/ROI

### Énoncé du Problème

**Situation Actuelle:**
- WMS coûte €50-150k setup + €10-15k/an maintenance
- ROI supposé 15-24 mois (Pass 4 estimé, non-validé)
- MAIS: ROI dépend croissance annuelle revenue → **INCONNUE COMPLÈTE**
- Pass 1 dit €15-20M actuels, aucune prévision croissance 2025-2027

**Pourquoi Type C (Bloquant):**
- Impossible arbitrer "WMS justified?" sans connaître volume 2027
- IF croissance >15% → WMS ROI 18 mois ✅
- IF croissance 5-10% → WMS ROI 36+ mois ❌
- Decision différée 12 mois = perte opportunity si oui, gaspillage capital si non

---

### Plan de Collecte de Données C1

#### 1. Quelles Données Exactement Manquent?

| Donnée | Description | Usage | Actuel | Cible |
|--------|---|---|---|---|
| **Croissance revenue 2025** | Revenue réelle vs 2024 (YTD novembre) | Baseline actuelle | Estimée 5-10%? | Audit accounts payables/clients |
| **Prévision croissance 2026-2027** | Forecast volume clients (nouveaux + churn) | Modélisation ROI | Zéro = "stasis assumed" | Entretiens clients 30+ | forecasts commerciaux |
| **Nombre dépôts 2027 plannifié** | Rester 3 dépôts? Ajouter 5ème? Impact volume | Architecture système WMS | Flou = "maybe 4-5" | Business plan PDG formal |
| **Utilisation capacity actuell** | Angélique 37h/week = bottleneck? Espace automation gains réels? | Valeur réduction Angélique via WMS | Estimé 10-20% time save | Timesheet 3 mois + audit tâches |
| **Clients autonom système** | % clients interface direct vs Angélique mediate? | Demand WMS self-service capacity | "Most via Angélique" (estimation) | CRM audit: commandes manuelles vs API |
| **Benchmarks WMS small logistics** | Durée ROI payback petit réseau 3-5 dépôts | Réalité vs théorie | Pass 4 "15-24 mois" estimé | Cas études Odoo/Cegid users 3-5 dépôts |

#### 2. Méthodes de Collecte (Détaillées)

**2a) Revenue Audit Comptable (CRITIQUES)**

```
Responsable: PDG + Comptable
Timeline: 1 semaine (données disponibles)
Coûts: €0 (interne)

Étapes:
├─ 1. Extrait comptes: Revenue 2024 full year = baseline
├─ 2. Revenue 2025 YTD (janvier-octobre) = actual current
├─ 3. Calcul croissance % = (2025 YTD / 2024 base) × (12/10 mois) = annualisé
├─ 4. Flag: Si croissance <5% → alerte élevée (WMS unlikely ROI)
└─ 5. Document: Certificat audit PDG pour Pass 6 utilisation

Validation Seuil:
├─ Croissance >15% = "Go WMS justifié"
├─ Croissance 8-15% = "Marginal, attend 2026 data"
└─ Croissance <8% = "Defer WMS 24 months, stay Excel"
```

**2b) Clients Growth Forecast (Prévisionnel)**

```
Responsable: Angélique + PDG (interviews clients clés)
Timeline: 2-3 semaines (interviews 20-30 clients VIP)
Coûts: €0 (interne) + €100 SMS éventuels

Étapes:
├─ 1. Sélectionner 30 clients top revenue (80% de volume)
├─ 2. Appel structuré:
│   ├─ "Votre activité 2026 croissance vs 2025?"
│   ├─ "Commandes estimées 2026 volume augmentation?"
│   ├─ "Facteurs risque (marché économique, concurrence)?"
│   └─ "Besoin logistique évolue (nouveaux chantiers, dépôts additionnels)?"
├─ 3. Synthèse: Calcul moyenne croissance clients (volume-weighted)
└─ 4. Risk assessment: 10% discount (pessimistic) vs full estimate (optimistic)

Result Format:
└─ Clients forecast:
   ├─ Conservative: +7% volume 2026
   ├─ Base case: +12% volume 2026
   └─ Optimistic: +18% volume 2026
```

**2c) Dépôts Strategy Clarification (Business Plan)**

```
Responsable: PDG + Logistique Manager
Timeline: 1 semaine (stratégie existante → formalisée)
Coûts: €0

Étapes:
├─ 1. PDG decision: "Rester 3 dépôts ou ajouter 5ème 2026?"
├─ 2. IF 5ème dépôt planned:
│   ├─ Timeline lancement? (Q1/Q2/Q3 2026?)
│   ├─ Région? (Quel volume anticipé?)
│   └─ Coûts setup? (€20-40k impact ROI total)
├─ 3. IF rester 3: "Justification stasis? Saturé ou marché limité?"
└─ 4. Document: 1-page PDG business plan 2026-2027

Impact WMS:
├─ 3 dépôts stasis: WMS ROI marginal (Excel suffit)
├─ 4-5 dépôts: WMS becomes necessary (coordination complexity)
└─ Scale ambition: Determines WMS phase 2 vs never
```

**2d) Timesheet Angélique (Workload Bottleneck)**

```
Responsable: Angélique (tracking perso)
Timeline: 3 semaines data collection
Coûts: €50 (timesheet app simple ou Excel template)

Étapes:
├─ 1. Angélique log chaque semaine:
│   ├─ Heures coordination (arbitrage dépôts, clients urgence, fournisseur SLA)
│   ├─ Heures CRM (emails, appels clients, documentation)
│   ├─ Heures meetings/formation
│   └─ Heures ad-hoc crisis (perte client, incident fournisseur)
├─ 2. Tracker 3 semaines = sample représentatif (post-PASS 5, pre-change)
├─ 3. Calcul bottleneck:
│   ├─ IF coordination >20h/semaine → Angélique capacity limited
│   ├─ IF crisis >5h/semaine → reactive not strategic
│   └─ IF CRM manual >15h/semaine → automation potential high
└─ 4. Assessment: "Où peut WMS réduire charge?"

WMS Value Proposition:
├─ Coordination: WMS rules automate? Save 5-10h/week? (30-40%)
├─ CRM: WMS api clients reduce manual emails? Save 3-5h/week? (20-30%)
└─ Crisis: WMS alerts detect issues early? Reduce emergency hours? (10-20%)
```

**2e) Benchmarks WMS (Cas Études Comparables)**

```
Responsable: Agent 4 (IT) recherche + interviews
Timeline: 2 semaines (web research + 5-10 interviews clients WMS)
Coûts: €300 (téléphones, SAAS trial 2 semaines)

Étapes:
├─ 1. Identifier 5-10 small logistics companies 3-5 dépôts France
│   ├─ Odoo WMS users (logistique PME)
│   ├─ Cegid Financials users (scale Gedimat)
│   └─ Shopflex ou YesPlan (TMS/WMS SMB)
├─ 2. Entretien semi-structuré (30 min téléphone):
│   ├─ "Quand WMS implémenté? Coûts réels?"
│   ├─ "ROI payback timeline observé?"
│   ├─ "Kilo persons implementation (Angélique équivalent)?"
│   ├─ "Post-WMS Angélique-type still needed ou réduit 50%?"
│   └─ "Regrets? Referiez-vous choix WMS?"
├─ 3. Synthèse: benchmarks réels
└─ 4. Adjust Pass 4 assumptions (15-24 mois → réalité 18-36 mois?)

Expected Findings:
├─ Best case: WMS ROI 18 mois (scaling operations, automation high)
├─ Real case: WMS ROI 24-30 mois (learning curve, change management)
└─ Worst case: WMS ROI 36+ mois (culture resistance, integration delays)
```

**2f) Clients API Self-Service Audit**

```
Responsable: Agent 4 (IT) + Angélique
Timeline: 1-2 semaines (CRM audit)
Coûts: €0

Étapes:
├─ 1. CRM audit: Comment commandes arrivent actuellement?
│   ├─ Clients appel Angélique = % des commandes?
│   ├─ Clients email Angélique = % des commandes?
│   ├─ Clients système external (Point.P API, Leroy Merlin EDI)? = %?
│   ├─ Clients SMS/WhatsApp = %?
│   └─ Total 100% = source command breakdown
├─ 2. Calcul: IF client API self-service possible → % demand reduction?
│   ├─ Clients capable API adoption (50-70% des VIPs)?
│   ├─ Remaining 30-50% (small/manual clients) → always Angélique?
├─ 3. WMS value: "Si WMS api clients launch, % adoption réaliste?"
└─ 4. Conclusion: "WMS peut sauver X% Angélique time via self-service"

WMS Business Case:
├─ IF >50% clients can API self-service → WMS justifié (value clair)
├─ IF <30% clients can API → WMS value faible (Angélique still mediate)
└─ Réalité: Mixed model (Tier 1 clients = API, Tier 2-3 = manual Angélique)
```

#### 3. Timeline Collecte C1

```
SEMAINE 1 (Immédiate):
├─ Revenue audit: 1 jour PDG/Comptable
├─ Dépôts strategy: 1 demi-jour PDG
└─ WMS benchmarks: Start 5 interviews Agent 4

SEMAINE 2-3:
├─ Clients forecast: Angélique 20 appels + synthèse
├─ Timesheet Angélique: Start 3-week tracking
├─ WMS benchmarks: Finish 10 interviews, synthesis report

SEMAINE 4-5:
├─ Timesheet data: Compile 3 weeks log, analyse
├─ API audit: Agent 4 CRM deep-dive 2 jours
└─ ALL DATA READY: Synthesis report C1 complet (16-20 novembre 2025)

TOTAL TIMELINE: 3-4 semaines (parallélisable)
```

#### 4. Coûts de Collecte C1

| Activité | Coûts Directs | Heures Travail | Coûts Indirects | Total |
|----------|---|---|---|---|
| Revenue audit | €0 | 4h (PDG/Comptable) | €100 | €100 |
| Clients forecast | €100 SMS | 15h (Angélique) | €200 | €300 |
| Dépôts strategy | €0 | 2h (PDG) | €50 | €50 |
| Timesheet tracking | €50 (app) | 3h setup + 5h analysis | €100 | €150 |
| WMS benchmarks | €300 (calls/trial) | 20h (Agent 4 interviews + report) | €500 | €800 |
| API audit | €0 | 8h (Agent 4 + Angélique) | €150 | €150 |
| **TOTAL C1** | **€450** | **52 heures** | **€1,100** | **€1,550** |

#### 5. Responsables C1

| Rôle | Domaine | Tâches |
|-----|---------|--------|
| **PDG** | Leadership | Revenue audit, dépôts strategy formelle, final decision |
| **Comptable** | Finance | Extract 2024-2025 revenue data, certify baseline |
| **Angélique** | Logistique | Clients forecast interviews (30 appels), timesheet daily log |
| **Agent 4 (IT)** | Technologie | WMS benchmarks (interviews 10 users), API audit CRM, synthesis report |

---

### Decision Tree Post-Données C1

```
APRÈS COLLECTE DONNÉES (Semaine 5-6):

Decision Point 1: CROISSANCE RÉELLE 2025-2026?
├─ IF croissance revenue >15% annualisée
│  └─ Decision Point 2: DÉPÔTS STASIS OU EXPANSION?
│     ├─ IF 4-5 dépôts planifiés 2026
│     │  ├─ ALORS: WMS INVESTISSEMENT JUSTIFIÉ Q1-Q2 2026
│     │  ├─ Timeline: Phase 0 Excel (3-4 mois) → Phase 1 Odoo (6 mois) → Phase 2 WMS complet (12 mois)
│     │  ├─ Budget: €50-80k setup + €15k/an maintenance
│     │  ├─ Expected ROI: 20-24 mois
│     │  └─ Condition Success: Recruitment assistant (support WMS transition)
│     │
│     └─ IF rester 3 dépôts (stasis)
│        ├─ ALORS: WMS MARGINAL, DEFER 24 MOIS
│        ├─ Rationale: 3 dépôts = Excel scaling sufficient
│        ├─ Instead: Invest €20k Phase 0 (Excel + SMS + CSAT)
│        └─ Revisit WMS: 2027-2028 si croissance persistante
│
├─ IF croissance revenue 8-15% annualisée
│  ├─ Decision Point 2b: CLIENTS FORECAST OPTIMISTIC?
│  │  ├─ IF base/optimistic case >12% → WMS marginal but consider Phase 1 TMS
│  │  │  ├─ ALORS: PILOT WMS Q2 2026 (prove ROI before full commit)
│  │  │  ├─ Pilot: 1 dépôt + Angélique workflow, 6 months
│  │  │  ├─ Gate: IF pilot ROI >18 mois → full deploy
│  │  │  └─ Gate: IF pilot ROI >24 mois → abandon WMS, stay Excel/TMS
│  │  │
│  │  └─ IF conservative case <10% → DEFER COMPLETELY
│  │     ├─ ALORS: EXCEL SCALING PATH
│  │     ├─ Investment: €20k Phase 0 only
│  │     └─ Review: 2026 année prochaine si croissance recover
│  │
│  └─ Angélique Workload Analysis:
│     ├─ IF timesheet >35h coordination → WMS value HIGH (automate scoring)
│     └─ IF timesheet <25h coordination → WMS value LOW (manual arbitrage fast)
│
└─ IF croissance revenue <8% annualisée
   ├─ ALORS: WMS INVESTMENT REJECT
   ├─ Rationale: Growth insufficient to justify €50k capital
   ├─ Instead: Excel scaling 3-5 ans
   ├─ Revisit: 2027-2028 IF growth accelerates
   └─ Focus: Cost reduction via Milkrun + consolidation (no tech spend)

---

FINAL DECISION CRITERIA (Quantifiables):

├─ WMS GO DECISION = ALL conditions met:
│  ├─ Croissance 2025 >10% confirmed
│  ├─ Prévision 2026 >12% realistic
│  ├─ Dépôts 4-5 planned Q1-Q2 2026
│  ├─ Angélique coordination >20h/week (bottleneck)
│  └─ WMS benchmarks ROI <24 mois
│
├─ WMS PILOT DECISION = Mixed conditions:
│  ├─ Croissance 8-15% confirmed
│  ├─ Dépôts stasis 3 probables
│  ├─ Pilot 6 mois (prove ROI before full commit)
│  └─ Gate revisit Q3 2026 based pilot data
│
└─ WMS NO DECISION = Growth <8% OR stasis 3 dépôts + weak Angélique constraint
   ├─ Defer WMS 24-36 months
   └─ Invest €20k Phase 0 Excel instead
```

---

### Recommandation Intérimaire C1

**Pendant que les données collectées (4 semaines):**

```
1. CONTINUEZ Phase 0 (Immédiat - janvier 2026)
   ├─ Excel scoring MDVRP implémentation (Angélique + Agent 4)
   ├─ SMS infrastructure Zapier (test 50 clients)
   ├─ CRM baseline health score Excel
   └─ Budget: €5-10k (petit investment, haut retour si Excel optimisé)
   └─ Objectif: Prove 10%+ reduction retards BEFORE asking WMS budget

2. PLANIFIEZ (sans commit):
   ├─ Odoo WMS trial account (free 2 semaines novembre)
   ├─ Angélique testez scoring logic en Excel (100 cas simulés)
   ├─ Agent 4 gather WMS technical specs (readiness assessment)
   └─ Objectif: Ready to deploy Phase 1 TMS janvier IF data positive

3. COMMUNICATION:
   ├─ PDG annonce: "WMS decision JANVIER basé croissance audit"
   ├─ Team: "Phase 0 Excel essential BEFORE WMS, prove ROI"
   ├─ Clients: "Nouveaux service levels J+2-3 décembre (tiering launch)"
   └─ Objectif: Manage expectations, avoid "WMS delayed 9 months" frustration

4. ESCALADE DÉCISION:
   ├─ IF revenue audit shows croissance <5% → immediately REJECT WMS
   ├─ IF clients forecast shows <8% → pilot approach (not full commit)
   ├─ IF Angélique timesheet <20h/week → automation gains limited
   └─ Decision: JANVIER 2026 (post data)
```

---

### Confiance Post-Collecte C1

**Avant Données:** 45% (très conditionnel, hypothèses)
**Après Données:** 85% (robuste, fact-based, scenarios testables)

---

## CONTRADICTION C2: URGENCE CLIENT % RÉELLE

### Énoncé du Problème

**Situation Actuelle:**
- Pass 3 estimé 70-80% commandes "urgence" (chantier date-fixe)
- Basé sur observation Angélique, **ZÉRO données CRM historiques**
- Ce % DETERMINE scoring MDVRP (30% poids urgence vs autres critères)
- Si réel <50%: Scoring over-weights urgence → décisions arbitrage mauvaises
- Si réel >80%: Must embrace urgence service (coûts justifiés)

**Pourquoi Type C (Bloquant):**
- Tiering service strategy (C2 option B1) dépend completement ce %
- IF urgence <50%: Tiering fails (clients refusent premium pricing pour non-urgent)
- IF urgence >80%: Must invest urgence infrastructure (express, SLA strict)
- Decision tiers/pricing = impossible sans ce data

---

### Plan de Collecte de Données C2

#### 1. Quelles Données Exactement Manquent?

| Donnée | Description | Usage | Actuel | Cible |
|---|---|---|---|---|
| **% urgences réelles CRM** | Audit 500+ commandes 2025: classifié "urgence" vs "flexibilité" | Refine scoring weights | Estimé 70-80% | Audit CRM 2-3 mois |
| **Client self-assessment** | Appels clients 50 demandes: "Deadline fixe ou flexible?" | Validate perception vs reality | Zéro (ask Angélique intuition) | 50 phone interviews |
| **Retard impact** | Si livraison J+2 vs J+0 promis, client réaction? | Churn correlation urgence | Estimé "pénalité chantier €500-5k" | 30 clients interviews (post-retard) |
| **Point.P/Leroy urgence %** | Benchmark: competitor urgence demand % | Realistic market baseline | Zéro (assumed 60% typical) | Research OR contact users |
| **Saison variation** | % urgence été vs hiver vs printemps? | Staffing planning, capacity | Constant assumed | Audit 12 mois monthly breakdown |

#### 2. Méthodes de Collecte (Détaillées)

**2a) CRM Historical Audit (CRITIQUE)**

```
Responsable: Angélique + Agent 4 (data analyst)
Timeline: 6-8 semaines (systematic CRM review)
Coûts: €0 (interne)

Étapes:
├─ 1. CRM extract: Toutes commandes 2025 janvier-novembre (500+ records)
├─ 2. Tagging (Angélique expert judgment):
│   ├─ URGENCE RÉELLE (client a deadline fixe chantier):
│   │  ├─ "Électricien: must livrer samedi 17h"
│   │  ├─ "Maçon: chantier ouvert, delai implicite"
│   │  └─ "Gestionnaire immobilier: appel téléphone 'urgent besoin'"
│   │
│   ├─ FLEXIBILITÉ RÉELLE (client accepte délai):
│   │  ├─ "PME: stock bas, peut attendre J+5 si livraison cheapest"
│   │  ├─ "Appel pas spécifique deadline = flexible"
│   │  └─ "Email sans 'urgent' = standard timescale okay"
│   │
│   └─ AMBIGUOUS (Angélique decision call):
│      ├─ "Customer dit urgent mais pas deadline précise"
│      ├─ "Note peu claire, dépend contexte"
│      └─ → Default FLEXIBLE (pessimistic urgence count)
│
├─ 3. Analyse quantitative:
│   ├─ Count: Urgence réelle = X%, Flexible = Y%, Ambiguous = Z%
│   ├─ Result: "Urgence réelle baseline = X%"
│   ├─ Variance: Si Angélique tag, second pass Agent 4 validation (inter-rater reliability)
│   └─ Confidence: IF rater agreement >85% → high confiance, else flag systematic bias
│
├─ 4. Breakdown supplémentaire:
│   ├─ Par client segment (artisan vs PME vs grand compte)
│   ├─ Par saison (été vs hiver vs printemps)
│   ├─ Par fournisseur (Éméris vs Médiafret vs autre)
│   └─ Par montant commande (€<500 vs €500-2000 vs €>2000)
│
└─ 5. Output: Détail report + Dashboard urgence % réelle
   └─ "Urgence réelle baseline = X% (confiance 90%), not 70-80% estimate"

Expected Finding Scenarios:
├─ Optimistic: ~75% urgence réelle → estimate correct
├─ Realistic: ~55% urgence réelle → estimate too high
├─ Pessimistic: ~35% urgence réelle → major scoring calibration needed
└─ Variance: ±15pp possible → confidence in ±5pp band
```

**2b) Client Phone Audit (Validation)**

```
Responsable: Angélique + Assistant (téléphone entrevue)
Timeline: 2-3 semaines (50 clients calls)
Coûts: €150 (appels téléphone)

Étapes:
├─ 1. Sélectionner 50 clients random (stratifié par segment)
├─ 2. Appel structuré (3 min script):
│   ├─ "Bonjour, audit Gedimat service. Rapide question:"
│   ├─ "Quand vous commanderez matériel urgent, deadline est fixe vs you can adjust?"
│   ├─ "Exemple: si on peut livrer J+2 vs J+0 demandé, c'est problema?"
│   ├─ "Et prix, paierez-vous 10% plus si garantie livraison J+0?"
│   └─ "Merci beaucoup!"
│
├─ 3. Analyse:
│   ├─ % clients "deadline fixe absolue" = urgence-constrained
│   ├─ % clients "J+2 acceptable si cheaper" = flexible
│   ├─ % clients "willing pay premium urgence" = value perception
│   └─ Correlation: IT segment vs artisan vs PME?
│
└─ 4. Validation:
   ├─ IF CRM audit says 55% urgence, phone survey confirms 50-60% → VALID
   ├─ IF CRM says 55% but phone says 75% → bias dans Angélique tagging
   └─ Conclusion: Cross-validate two methods

Confidence Gain:
├─ CRM alone: 70% (Angélique judgement)
├─ Phone alone: 60% (small sample, self-report bias)
└─ Both combined: 85% (triangulation confidence)
```

**2c) Post-Retard Client Impact (Churn Correlation)**

```
Responsable: Angélique (interviews clients impactés)
Timeline: 2-3 semaines (30 clients récents avec retards)
Coûts: €0

Étapes:
├─ 1. CRM identify: Derniers 30 cas retards J+1 ou plus vs promis
├─ 2. Pour chaque: Appel client 5-10 min
│   ├─ "Nous avons livré J+2 vs J+0 promis en [date]. Impact chantier?"
│   ├─ "Pénalité client ou simplement inconvénient?"
│   ├─ "Considérez retard comme sérieux problème ou acceptable?"
│   └─ "Êtes-vous toujours satisfait Gedimat après ce retard?"
│
├─ 3. Analyse:
│   ├─ IF retard "urgence" commandes: Client frustration HIGH vs LOW?
│   ├─ IF retard "flexible" commandes: Client accepte vs churn signal?
│   ├─ Pénalité réel €: Count vs estimation (€500-5k vs réalité)
│   └─ Churn risk: Client parti après retard vs stayed?
│
└─ 4. Conclusion:
   ├─ "Urgence retards coûtent plus (pénalité + churn) vs flexible retards"
   ├─ "Churn réel pénalité = €X per retard urgence vs €Y per flexible"
   └─ "Value justifying urgence = (pénalité avoided + churn prevented)"
```

**2d) Benchmark Point.P/Leroy Urgence %**

```
Responsable: Marché research (Agent 8)
Timeline: 2 semaines (recherche online + 5-10 interviews)
Coûts: €200 (calls)

Étapes:
├─ 1. Research online: Point.P/Leroy communications, service levels
│   ├─ Point.P marketing: What % urgent vs standard?
│   ├─ Leroy Merlin: J+0 express vs standard delivery?
│   └─ Competitors positioning: Urgence is premium or standard?
│
├─ 2. Interviews: 5-10 users Point.P/Leroy customers
│   ├─ "What % your orders are urgent deadline vs flexible?"
│   ├─ "How much pay premium for express delivery?"
│   └─ "Is urgence what differentiates Point.P/Leroy or standard offering?"
│
└─ 3. Finding: Realistic market urgence baseline
   ├─ IF Point.P <40% urgence → Gedimat 55-75% may be HIGH
   ├─ IF Point.P 50-70% urgence → Gedimat 70% estimate REALISTIC
   └─ Insight: Market comparison validate Gedimat assumption or flag bias

Expected Findings:
├─ Construction supply market typical: 40-60% urgence
├─ Gedimat estimate 70-80%: Either higher urgence OR Angélique over-counts
└─ If benchmark <50%: Gedimat likely over-estimating
```

**2e) Saison et Volume Variation**

```
Responsable: Angélique (monthly breakdown)
Timeline: 1 semaine (data extraction)
Coûts: €0

Étapes:
├─ 1. CRM: Extract monthly urgence % 2025 (janvier-novembre)
├─ 2. Analyze:
│   ├─ Été (juin-août): Building season = urgence% HIGH?
│   ├─ Hiver (décembre-février): Off-season = urgence% LOW?
│   └─ Printemps/Automne: Middle ground?
│
├─ 3. Volume variation:
│   ├─ Mois fort vs faible volume?
│   ├─ Correlation: Urgence% ↑ when volume ↑ (clients rushing) OR stable?
│   └─ Staffing implication: Deve plan capacity seasonally?
│
└─ 4. Output:
   ├─ "Urgent % stable 55% year-round" → plan standard staffing
   ├─ OR "Summer 70%, Winter 40%" → seasonal capacity adjustment needed
   └─ Impact: Médiafret contract terms, Angélique scheduling, bonus structure
```

#### 3. Timeline Collecte C2

```
SEMAINE 1-2 (Immédiate):
├─ CRM data extract: 1 jour (500+ commandes)
├─ Angélique tagging: 10 heures (30-50 commandes/hour)
├─ Agent 4 validation tagging: 5 heures (check inter-rater reliability)

SEMAINE 2-3:
├─ Continue Angélique tagging: 10 heures/semaine
├─ Client phone audit: Angélique 50 appels (2-3 semaines, 2-3 appels/jour)
├─ Post-retard interviews: Angélique 30 appels (parallel)

SEMAINE 3-4:
├─ Finish CRM tagging: Final 100 commandes
├─ Benchmark research: Agent 8 (10 heures research + calls)
├─ Saison breakdown: Extract monthly 2025 data (2 heures)

SEMAINE 5:
├─ All data synthesis: Agent 4 + Angélique (5 heures report)
├─ Calibration: IF discrepancy CRM vs phone → troubleshoot bias
└─ Final: "Urgence réelle baseline = X% (confiance 85%)"

TOTAL: 6-8 semaines (mais parallélisable avec C1, C3, C4)
```

#### 4. Coûts de Collecte C2

| Activité | Coûts Directs | Heures Travail | Coûts Indirects | Total |
|----------|---|---|---|---|
| CRM audit + tagging | €0 | 40h (Angélique/Agent 4) | €500 | €500 |
| Client phone survey | €150 | 15h (Angélique assistant) | €200 | €350 |
| Post-retard interviews | €0 | 8h (Angélique) | €100 | €100 |
| Benchmark research | €200 | 10h (Agent 8) | €200 | €400 |
| Saison analysis | €0 | 2h (Angélique) | €50 | €50 |
| **TOTAL C2** | **€350** | **75 heures** | **€1,050** | **€1,400** |

#### 5. Responsables C2

| Rôle | Domaine | Tâches |
|-----|---------|--------|
| **Angélique** | Logistique/CRM | CRM historical tagging, client phone audit, post-retard interviews |
| **Agent 4 (IT)** | Données | CRM extract, tagging validation (inter-rater), synthesis analysis |
| **Agent 8 (Marché)** | Marché | Benchmark research Point.P/Leroy, competitive positioning |
| **Assistant** | Support | Parallel phone calling (50+ customers) |

---

### Decision Tree Post-Données C2

```
APRÈS COLLECTE DONNÉES (Semaine 8-9):

Decision Point 1: URGENCE RÉELLE BASELINE?
├─ IF urgence réelle >70%
│  ├─ ALORS: Pass 3 estimate CORRECT (validation)
│  ├─ Conclusion: Service must be urgence-optimized
│  ├─ Scoring: Urgence 30% poids KEEP (maybe increase 35%)
│  ├─ Strategy: Embrace Tier CRITIQUE (10% volume, premium pricing)
│  ├─ Coûts: Médiafret contract urgence premium, express SLA, staffing buffer
│  └─ Investment: €15-20k urgence infrastructure justified
│
├─ IF urgence réelle 50-70%
│  ├─ ALORS: Pass 3 OVER-ESTIMATE par 10-20%pp
│  ├─ Scoring: Recalibrate urgence 20-25% poids (reduce from 30%)
│  ├─ Strategy: Balanced Tiering (EXPRESS 15%, ÉCONOMIE 75%)
│  ├─ Insight: Some urgence real, but majority flexible → consolidation possible
│  ├─ Consolidation gain: 20-25% cost reduction realistic
│  └─ Milkrun strategy: Viable pour 70% standard commandes
│
└─ IF urgence réelle <50%
   ├─ ALORS: Pass 3 SIGNIFICANT BIAS (estimate 70-80% vs reality <50%)
   ├─ Scoring: Urgence REDUCE to 15% poids (prioritize proximité + volume)
   ├─ Strategy: Consolidation-aggressive (ÉCONOMIE 85%, CRITIQUE 15%)
   ├─ Insight: Majority clients flexible → over-investing urgence is waste
   ├─ Coûts: Médiafret standard rates sufficient, less premium infrastructure
   ├─ ROI Improvement: Consolidation + milkrun 35-40% gain (vs 15-20% if 70% urgence)
   └─ Risk: Ensure CRITIQUE tier priced premium (cover express costs)

---

Decision Point 2: CHURN CORRELATION RETARDS?

├─ IF churn urgence-retards = HIGH (>20% clients churn after 1 retard)
│  ├─ ALORS: Urgence Service MANDATORY (retention value very high)
│  ├─ Cost/Benefit: Pay premium express for urgence clients (avoid €5-10k churn)
│  ├─ Strategy: Accept 15-20% margins on CRITIQUE tier (pour avoid churn)
│  └─ NPS Impact: Retards on urgent = NPS -5 to -8 points (major hit)
│
├─ IF churn urgence-retards = MODERATE (5-10% client impact)
│  ├─ ALORS: Urgence Service IMPORTANT but not CRITICAL
│  ├─ Cost/Benefit: Invest selectively in VIP urgence (high LTV clients)
│  ├─ Strategy: Standard tier + selective EXPRESS tier (20% volume)
│  └─ NPS Impact: Retards = NPS -2 to -3 points (manageable)
│
└─ IF churn urgence-retards = LOW (<5% impact)
   ├─ ALORS: Urgence Service NICE-TO-HAVE (not core business case)
   ├─ Cost/Benefit: Minimal investment (SMS alerts sufficient)
   ├─ Strategy: ÉCONOMIE tier dominant, CRITIQUE rare exception
   ├─ NPS Impact: Retards = NPS -1 to 0 (acceptable, clients expect delays)
   └─ Insight: Customers more flexible than assumed

---

Decision Point 3: SCORING PONDÉRATION FINALE

│ Current (Pass 3):    Proximité 40% | Volume 30% | Urgence 30%
│
├─ IF urgence >70% real: Urgence 35% | Proximité 40% | Volume 25%
├─ IF urgence 50-70%: Urgence 25% | Proximité 45% | Volume 30%
└─ IF urgence <50%: Urgence 15% | Proximité 50% | Volume 35%

│ Plus: Recalibrate thresholds (score 65 auto? 55 escalade?)
└─ Post-data: Retest scoring on 100 historical cases → validate new weights

---

FINAL DECISION FRAMEWORK:

├─ Tier 1 (CRITIQUE):
│  ├─ Volume: IF urgence >70% → 15% expected, IF <50% → 5% expected
│  ├─ Pricing: +15% premium (cover express costs)
│  └─ SLA: Livraison J+0/J+1 guaranteed
│
├─ Tier 2 (EXPRESS):
│  ├─ Volume: 20-25% IF urgence 50-70%, 5-10% IF urgence <50%
│  ├─ Pricing: +5% premium
│  └─ SLA: Livraison J+2 guaranteed
│
└─ Tier 3 (ÉCONOMIE):
   ├─ Volume: Remaining clients (65-85% depending on urgence %)
   ├─ Pricing: Standard
   └─ SLA: Livraison J+4-5 acceptable (consolidation)

Confidence Post-Data: 85-90% (robust fact-based)
```

---

### Recommandation Intérimaire C2

**Pendant que données collectées (6-8 semaines):**

```
1. CONTINUEZ Avec Hypothèse Actuell (70% urgence estimate)
   ├─ Implémentez scoring 40/30/30 en Excel
   ├─ Lancez pilot tiering 50 clients (ÉCONOMIE/EXPRESS/CRITIQUE)
   ├─ Mesurez adoption % + NPS impact
   └─ Objectif: Validate tiering concept before calibration

2. PRÉPAREZ Réaction Scenarios:
   ├─ IF urgence réelle <50%:
   │  ├─ Communication plan clients (consolidation = better margins)
   │  ├─ Restructure tiers (CRITIQUE moins attractive)
   │  └─ Renegociate Médiafret contract (less urgence premium)
   │
   ├─ IF urgence réelle 50-70%:
   │  ├─ Rebalance scoring live (urgence 25% → 20%)
   │  ├─ Adjust Médiafret capacity planning
   │  └─ Refine tiering pricing (less CRITIQUE premium needed)
   │
   └─ IF urgence réelle >75%:
      ├─ Increase CRITIQUE tier availability
      ├─ Negotiate Médiafret urgence volume + pricing
      └─ Plan express capacity Q1 2026

3. COMMUNICATION:
   ├─ Clients: "New service tiers Q1 2026 (you choose delivery speed)"
   ├─ Team: "Urgence baseline audit in progress, tier calibration coming"
   └─ Médiafret: "Forecast urgence % TBD, capacity discussion January"

4. ESCALADE DÉCISION:
   ├─ IF tagging shows <40% urgence → immediately replan tiers (reduce CRITIQUE)
   ├─ IF phone survey confirms <50% → pivot consolidation strategy
   └─ Decision: JANVIER 2026 (post data collection)
```

---

### Confiance Post-Collecte C2

**Avant Données:** 55% (estimée, zéro validation)
**Après Données:** 85% (CRM + phone + benchmark triangulation)

---

## CONTRADICTION C3: PERTES COMMANDES CLIENT

### Énoncé du Problème

**Situation Actuelle:**
- Pass 2 estimé "2-4 clients/an perte retard" = **€3-12k/an (variance énorme)**
- Zéro documentation formelle: "Électricien Y disparaît" découvert APRÈS, pas warning signal
- Aucun CRM tracking: Clients perdus, raisons non-enregistrées
- Pénalité cliente estimée €500-5k/jour si retard = **JAMAIS DOCUMENTÉ Gedimat**

**Pourquoi Type C (Bloquant):**
- Communication/NPS strategy justifiée par "éviter perte clients €50k+/an"
- MAIS: Réelle perte peut être €2-3k/an (faux justification) ou €15-25k/an (justification correcte)
- Decision WMS/assistant/SMS investment = ROI dépend churn réel
- IF perte <€5k/an: Communication investment ROI <100% (not justified)
- IF perte >€15k/an: Communication investment ROI 500%+ (URGENT)

---

### Plan de Collecte de Données C3

#### 1. Quelles Données Exactement Manquent?

| Donnée | Description | Usage | Actuel | Cible |
|---|---|---|---|---|
| **Clients perdus 2024-2025** | List formelle: qui parti, quand, pourquoi? | Churn rate baseline | "Y disparaît" anecdotal | CRM audit: 100% client coverage |
| **Raison churn** | Retard? Prix? Relation? Service autre? | Root cause NPS/satisfaction | Estimée "2-4 retard" | Entretiens 20+ clients partis |
| **Churn rate %** | % annual customer loss vs baseline | Metric benchmarking | Zéro mesure | Calculate: Lost/Total year-start |
| **Pénalité cliente** | € actual loss par chantier affecté | Economics churn | Estimé €500-5k/j = vague | Audit 10 cas: contract penalties + réel pertes |
| **LTV clients** | Revenue lifetime par client perdu | Importance valeur loss | Zéro = "électricien Y unknown" | Historical revenue 10 lost clients |
| **Replacement cost** | Time/effort acquire replacement customer | Invisible cost churn | Zéro | Sales effort estimate + acquisition cost |

#### 2. Méthodes de Collecte (Détaillées)

**2a) CRM Churn Audit (CRITIQUE)**

```
Responsable: Angélique + Agent 5 (CRM Manager)
Timeline: 2-3 semaines (CRM deep-dive)
Coûts: €0

Étapes:
├─ 1. CRM extract: All clients 2024 année complète (baseline)
├─ 2. CRM extract: All clients 2025 année complète (current)
├─ 3. Reconciliation: Clients in 2024 but NOT in 2025 = CHURNED
│   ├─ Count: X clients lost
│   ├─ Revenue loss: €Y (sum orders last 12 months each lost client)
│   ├─ Churn rate %: (X / Total 2024 clients) = %
│   └─ Churn-USD: €Y annual loss
│
├─ 4. Breakdown by dimension:
│   ├─ By client size (revenue): €0-500/an vs €500-2000 vs €2000+ churn %?
│   ├─ By segment: Artisan vs PME vs grand compte → different churn rates?
│   ├─ By geography: Région nord vs sud vs centre → concentration?
│   └─ By tenure: Clients <1 year old vs mature (retention improvement signal)?
│
├─ 5. Data quality check:
│   ├─ "Électricien Y": Confirm inactive (no orders >6 months)
│   ├─ Cross-check: Finance AR (if customer owes $ → might return, not truly lost)
│   ├─ Validation: Interview Angélique (she knows who's "really gone")
│   └─ Flag: If churn >15% → major concern, need root cause urgently
│
└─ 6. Output: Churn database
   ├─ Lost client list (30-50 clients likely)
   ├─ Churn rate baseline (expected 8-12% based benchmarks)
   ├─ Revenue impact (total €Y lost)
   └─ Segment analysis (which clients most at risk?)

Expected Findings:
├─ Baseline churn 8-12% typical SMB
├─ Gedimat likely 10-15% (construction business churn-prone)
├─ High-value churn: 20% of revenue from 80% lost clients (Pareto)
└─ Insight: Few big customers lost = major pain vs many small = less impact
```

**2b) Lost Client Exit Interviews**

```
Responsable: Angélique (or PDG for VIP clients)
Timeline: 2-3 semaines (20-30 entretiens)
Coûts: €200 (appels téléphone)

Étapes:
├─ 1. Sélectionner 20-30 clients churned (stratifié par revenue size)
├─ 2. Appel structuré (5-10 min):
│   ├─ "Bonjour [client name], nous vu que vous commandez plus avec Gedimat."
│   ├─ "Pouvons-nous comprendre: Avez-vous trouvé autre fournisseur?"
│   ├─ "Raison principal: Retard livraison? Prix? Service qualité? Autre?"
│   ├─ "Si retard était cause, quand avez-vous eu problèmes?"
│   ├─ "Possible revenir Gedimat si nous améliorons [spécifique]?"
│   └─ "Merci beaucoup pour feedback!"
│
├─ 3. Tagging reasons:
│   ├─ Retard/Service: "Livraison tard, manqué chantier deadline"
│   ├─ Prix: "Point.P moins cher" or "Amazon logistics cheaper"
│   ├─ Relation: "Angélique busy, hard to reach" or "PDG pas accessible"
│   ├─ Autre: "Business closed" or "Relocation autre région"
│   └─ Missing: "Ne sait pas, changé just because"
│
├─ 4. Analyse:
│   ├─ % retard-related churn: IF >40% → service quality issue
│   ├─ % price-related churn: IF >30% → margin compression risk
│   ├─ % relation-based churn: IF >20% → Angélique capacity/CRM issue
│   └─ Reversibility: "% clients willing return IF we fix [X]?" → win-back potential
│
└─ 5. Output:
   ├─ Churn root-cause distribution (% by reason)
   ├─ Actionable insights (what to fix first)
   ├─ Win-back targets (20% of lost clients potentially recoverable?)
   └─ NPS/satisfaction implication (service quality = churn driver = NPS critical)

Expected Findings Scenarios:
├─ Retard-driven: "Missed deadline cost us €5k, switched Point.P" → SERVICE issue
├─ Price-driven: "Point.P 10% cheaper for same service" → MARGIN issue
├─ Relation-driven: "Angélique never available, we felt unimportant" → RH/CRM issue
└─ Mix: Likely combination, but priority varies
```

**2c) Chantier Penalty Documentation**

```
Responsable: Angélique + Legal (if contracts exist)
Timeline: 1-2 semaines (audit 10-20 cases)
Coûts: €200 (legal review if needed)

Étapes:
├─ 1. Identify: Last 10-20 retards client (past 18 months)
├─ 2. For each: Collect
│   ├─ Date retard
│   ├─ Promised vs actual delivery
│   ├─ Raison retard (fournisseur, consolidation, Médiafret)
│   ├─ Client claim: "Retard coûte us €X penalty chantier"
│   ├─ Gedimat credit: What we paid/discounted (€0 or €Y?)
│   └─ Client satisfaction post-resolution?
│
├─ 3. Validation:
│   ├─ Contracts: Do we have formal penalty clauses? (probably NOT based Agent 7 review)
│   ├─ Negotiation: Was penalty negotiated vs refused?
│   ├─ Precedent: Did we set expectation for future refunds/credits?
│   └─ Revenue impact: Actual margin hit (lost margin vs full refund?)
│
├─ 4. Economics:
│   ├─ Average penalty per retard: €Y (vs estimé €500-5k broad range)
│   ├─ Margin loss: Cost refund vs cost prevent retard (€X infrastructure vs €Y refund?)
│   ├─ Insurance: Do we have liability insurance covering chantier penalties?
│   └─ Negotiation power: Can we recoup penalties from fournisseurs? (Éméris, Médiafret)
│
└─ 5. Output:
   ├─ Penalty baseline (actual €Y per retard, not €500-5k range)
   ├─ Frequency: How many retards/year → total penalty exposure?
   ├─ Contract policy: Should we formalize penalty clauses (reduce disputes)?
   └─ Insight: "Retard = €X cost, premium service delivery = ROI justified?"

Expected Findings:
├─ Actual penalties LOW: "€100-200 per retard, customer just unhappy"
│  → Service premium less justified economically
├─ Actual penalties HIGH: "€500-1000 per retard, multiple incidents"
│  → Service investment (€15-20k) ROI justified
└─ No data: Most retards NOT documented formally (Gedimat unaware cost)
   → Opportunity fix: formalize penalty tracking → force discipline
```

**2d) Client LTV Historical Analysis**

```
Responsable: Finance (Agent 2) + Angélique
Timeline: 1 semaine (historical data extraction)
Coûts: €0

Étapes:
├─ 1. For top 20 lost clients:
│   ├─ Extract revenue 2023, 2024, 2025 (if any)
│   ├─ Calculate: Total revenue per customer = LTV approximation
│   ├─ Estimate: Residual value (if they came back, expected future revenue)
│   └─ Loss: Lifetime value forgone
│
├─ 2. Analysis:
│   ├─ Pareto: Top 5 lost clients = what % revenue loss?
│   │  └─ If top 5 = 40% revenue lost → FEW CLIENTS but BIG impact
│   ├─ Average LTV: Mean revenue lost per customer
│   ├─ Replacement effort: How long to acquire same revenue (new customer)
│   └─ Economics: Cost of acquisition vs revenue time → payback period
│
├─ 3. Segment insight:
│   ├─ VIP churn vs Standard churn = different impact?
│   │  └─ If 3 VIP churn = €40k loss vs 30 small churn = €5k = clear priority
│   ├─ Early churn: Clients <1 year old churning = retention issue
│   ├─ Late churn: Mature clients churning = dissatisfaction signal
│   └─ NPS implication: Churn clients = were detractors before leaving?
│
└─ 4. Output:
   ├─ Revenue loss quantified (total €Y, not vague estimate)
   ├─ VIP vs Standard breakdown (priority focus)
   ├─ Replacement cost (payback period to acquire same revenue)
   ├─ Insight: "Retaining 3 VIP clients = higher value than 30 small clients"
   └─ ROI focus: Communication/NPS investment target VIPs first

Expected Findings:
├─ Balanced: Churn distributed many clients = low risk
├─ Concentrated: 20% clients = 80% revenue loss = HIGH RISK
└─ Likely reality: Mix with few big losses + many small = variable focus
```

**2e) Customer Satisfaction Trend (NPS Pre-Churn)**

```
Responsable: Agent 3 (Satisfaction) + Angélique
Timeline: 2-3 semaines (historical NPS reconstruction)
Coûts: €200 (survey 50 at-risk clients)

Étapes:
├─ 1. Historical NPS: If any past surveys, extract churned client scores
│   ├─ Were churned clients detractors (NPS <4) before leaving?
│   ├─ Pattern: "All churned clients had NPS <0 before disappearing?"
│   └─ Predictive power: NPS score = churn risk indicator?
│
├─ 2. At-risk current clients: Survey 50 clients
│   ├─ Target: Clients with low engagement (few orders, long silence)
│   ├─ Survey: "How likely recommend Gedimat (NPS 0-10)?"
│   ├─ Follow-up: "Why? Improvements needed?"
│   └─ Retention: "If we improve X, stay? Consider leaving?"
│
├─ 3. Analysis:
│   ├─ Churn predictor: "Clients NPS <4 = 50% churn risk within 6 months"
│   │  → Can we detect at-risk clients early?
│   ├─ Intervention: What % at-risk clients willing stay if contacted proactively?
│   └─ Win-back: What % churned willing return if we improve [specific issue]?
│
└─ 4. Output:
   ├─ NPS as churn predictor (confiance X%)
   ├─ Proactive intervention effectiveness (% retention uplift if early contact)
   ├─ Win-back potential (% churned clients recoverable via improvement)
   └─ Insight: "NPS 40+ = churn risk <5%, NPS <10 = churn risk 30%+ → monitor closely"
```

#### 3. Timeline Collecte C3

```
SEMAINE 1-2:
├─ CRM churn audit: Angélique 5 jours (extraction + reconciliation)
├─ Lost client list preparation: Agent 5 2 jours (validation)

SEMAINE 2-3:
├─ Lost client interviews: Angélique 50 appels (2-3 semaines, 2-3/jour)
├─ Retard penalty audit: 1 semaine (collect 20 cases)
├─ LTV historical analysis: Finance 3 jours (data extraction + analysis)

SEMAINE 3-4:
├─ NPS at-risk survey: Agent 3 2 semaines (50 clients survey)
├─ Data synthesis: Agent 5 CRM 3 jours (compile all data)

SEMAINE 5:
├─ Final report: Churn root cause, economics, recommendations
└─ Confidence assessment: Robust fact-based

TOTAL: 4-5 semaines (parallélisable avec C1, C2, C4)
```

#### 4. Coûts de Collecte C3

| Activité | Coûts Directs | Heures Travail | Coûts Indirects | Total |
|----------|---|---|---|---|
| CRM churn audit | €0 | 25h (Angélique/Agent 5) | €400 | €400 |
| Lost client interviews | €200 | 12h (Angélique) | €150 | €350 |
| Penalty audit | €200 | 8h (Angélique/Legal) | €100 | €300 |
| LTV analysis | €0 | 5h (Finance) | €100 | €100 |
| At-risk NPS survey | €200 | 10h (Agent 3) | €200 | €400 |
| **TOTAL C3** | **€600** | **60 heures** | **€950** | **€1,550** |

#### 5. Responsables C3

| Rôle | Domaine | Tâches |
|-----|---------|--------|
| **Angélique** | Logistique/CRM | CRM churn audit, lost client interviews (20-30), penalty audit |
| **Agent 5 (CRM)** | CRM Manager | Churn database validation, data quality, trend analysis |
| **Agent 3 (Satisfaction)** | Satisfaction | NPS at-risk survey, churn predictor analysis |
| **Finance (Agent 2)** | Finance | LTV calculation, revenue impact quantification |

---

### Decision Tree Post-Données C3

```
APRÈS COLLECTE DONNÉES (Semaine 5-6):

Decision Point 1: CHURN RATE RÉELLE?
├─ IF churn <8% (below market average)
│  ├─ ALORS: Gedimat retention GOOD (not crisis)
│  ├─ Conclusion: Current operations adequate, improvements optional
│  ├─ Communication ROI: Lower priority investment (nice-to-have)
│  ├─ Focus: Cost reduction (milkrun) vs satisfaction investment
│  └─ Budget: Allocate to Phase 0 Excel instead of heavy NPS
│
├─ IF churn 8-15% (market average to high)
│  ├─ ALORS: Churn NORMAL but opportunity improve
│  ├─ Conclusion: Communication investment justified (15-25x ROI)
│  ├─ Root cause analysis: Retard-heavy? Price-heavy? Relation-heavy?
│  ├─ Focus: Fix top 2-3 drivers (not all simultaneously)
│  └─ Budget: €20k communication investment reasonable
│
└─ IF churn >15% (crisis)
   ├─ ALORS: Churn CRITICAL, immediate action required
   ├─ Conclusion: Service quality severely impaired
   ├─ Focus: Emergency: Fix retard + Angélique availability immediately
   ├─ Win-back: Proactive contact churned clients (recovery potential)
   └─ Budget: €25-30k communication + operations improvement URGENT

---

Decision Point 2: CHURN ROOT CAUSE?

├─ IF Retard >50% reason:
│  ├─ → ACTION: Service reliability improvement PRIORITY 1
│  ├─ → Invest: Médiafret SLA formelle, Angélique coordination automation
│  ├─ → Technology: Phase 0 Excel + SMS alerts (reduce retard)
│  ├─ → Timeline: Implement immediately (Q4 2025)
│  ├─ → ROI: Every prevented retard = client retention
│  └─ → Confidence: Service fixes have clear ROI
│
├─ IF Price >40% reason:
│  ├─ → ACTION: Pricing strategy review, NOT price reduction
│  ├─ → Insight: "Clients price-elastic" → communicate value + service differentiation
│  ├─ → DON'T: Panic discount (crush margins)
│  ├─ → DO: Tiering service (Relationship leader position)
│  │   └─ VIP clients willing pay 5% premium for reliability
│  ├─ → Timeline: Position change Q1 2026
│  └─ → Confidence: Can shift perception without price war
│
├─ IF Relation >30% reason:
│  ├─ → ACTION: Angélique availability + CRM proactive outreach
│  ├─ → Insight: "Clients feel neglected" → monthly touchpoint VIP
│  ├─ → Investment: Assistant hire (€22k) + SMS automation
│  ├─ → Timeline: Q1 2026 assistant onboarding
│  └─ → Confidence: Relation-driven churn most recoverable
│
└─ IF Multiple reasons (balanced):
   ├─ → ACTION: Prioritize service (retard) FIRST (easier fix)
   ├─ → THEN: Relation (proactive outreach) SECOND (quick win)
   ├─ → THEN: Pricing review (harder change, position reset)
   └─ → Timeline: Phased 3-6 months (not simultaneous)

---

Decision Point 3: PENALTY ECONOMICS?

├─ IF actual penalties <€300/retard (vs €500-5k estimate):
│  ├─ → Insight: "Retard costly operationally but not financially catastrophic"
│  ├─ → ROI: Premium service infrastructure less justified economically
│  ├─ → Alternative: Accept 5-10% retard rate, customer absorbs (negotiate penalty waiver)
│  └─ → Strategy: Cost-reduction focus (milkrun) vs prevention
│
├─ IF actual penalties €300-1000/retard:
│  ├─ → Insight: "Retard = real cost, prevention ROI positive"
│  ├─ → ROI: Service improvement investment (€15-20k) justified
│  ├─ → Strategy: Balance cost-reduction + reliability improvement
│  └─ → SLA: Fournisseur penalty (recoup from Médiafret/Éméris)
│
└─ IF actual penalties >€1000/retard (or customer churn):
   ├─ → Insight: "Retard = existential threat to relationship"
   ├─ → ROI: Premium service infrastructure URGENT
   ├─ → Strategy: Reliability over cost reduction (no compromise)
   ├─ → Clients: Proactively communicate SLA guarantee
   └─ → Confidence: Clear business case for service investment

---

Decision Point 4: WIN-BACK POTENTIAL?

├─ IF >30% churned clients willing return IF improvement:
│  ├─ → ACTION: Launch win-back campaign Q1 2026
│  ├─ → Approach: "We've improved [specific], interested reconnect?"
│  ├─ → Investment: €2-3k (SMS + Angélique calls + small incentive)
│  ├─ → ROI: High (recover €50-100k+ revenue if successful)
│  └─ → Timeline: Pilot 10-20 clients, scale IF success
│
├─ IF 10-30% willing return:
│  ├─ → ACTION: Selective win-back (target VIPs only)
│  ├─ → Focus: Top 20 churned clients by revenue
│  ├─ → Personalized approach (PDG call if needed)
│  └─ → Budget: €1-2k for VIP campaign
│
└─ IF <10% willing return:
   ├─ → Insight: "Bridge burned, focus on current retention"
   ├─ → ACTION: Accept loss, prioritize staying clients
   └─ → Budget: Use savings on acquisition for retention (current clients)

---

FINAL DECISION FRAMEWORK:

├─ IF Churn <8% + Retard-driven:
│  └─ → Quick fix: Phase 0 Excel (prevent retards) + maintain current NPS investment
│
├─ IF Churn 8-15% + Multiple causes:
│  └─ → Balanced: Service (retard prevention) + Relation (Angélique) + Position (tiering)
│
├─ IF Churn >15% + Price/Relation driven:
│  └─ → Emergency: Angélique assistant (immediate) + proactive VIP outreach
│
└─ Overall:
   ├─ NPS investment justified IF churn >10% (ROI clear)
   ├─ Communication ROI: 15-25x IF target churn reduction 2-3%
   ├─ Win-back potential: €50-100k upside IF 20%+ recovery
   └─ Confidence: Fact-based decision, not estimate-based

Confidence Post-Data: 85-90% (robust churn metrics)
```

---

### Recommandation Intérimaire C3

**Pendant que données collectées (4-5 semaines):**

```
1. ASSUME Moderate Churn (10-12% baseline)
   ├─ Plan: Communication investment €20k justified
   ├─ Budget: Allocate Phase 0 + Phase 1 (SMS + CRM health score)
   └─ Objective: Prove value before full Phase 2 WMS

2. PREVENTIVE ACTIONS (immediate):
   ├─ NPS baseline survey (start week 1): 50 clients
   ├─ At-risk client list (weekly): Flag NPS <4 clients for proactive contact
   ├─ Retard alert process: SMS Angélique if delivery delayed >24h
   └─ Objective: Early detection, proactive intervention

3. COMMUNICATION:
   ├─ Clients: "We're improving service (audit in progress)"
   ├─ Team: "Churn analysis underway, retention priority Q1 2026"
   └─ Médiafret: "SLA discussion January (backup for retard penalties)"

4. ESCALADE DÉCISION:
   ├─ IF early results show churn >15% → immediate Angélique assistant hiring
   ├─ IF interviews confirm retard-driven → emergency SLA negotiation Médiafret
   └─ Decision: JANVIER 2026 (post data collection)
```

---

### Confiance Post-Collecte C3

**Avant Données:** 50% (estimée €3-12k, zéro documentation)
**Après Données:** 85% (CRM audit + interviews + penalty quantified)

---

## CONTRADICTION C4: MÉDIAFRET CAPACITÉ URGENCES & CONTRAT

### Énoncé du Problème

**Situation Actuelle:**
- Gedimat relation Médiafret = **ad-hoc, NOT documented**
- Mélissa (Médiafret contact) = single point of failure (bus factor = 1)
- Urgence capacity: "5-10 urgent commandes/mois possible?" → **ASSUMÉ, not verified**
- Contrat termes: Pricing, penalty, capacity guarantees = **VERBAL only**
- Risk: "Médiafret dit non" (capacity exceeded or prioritize bigger accounts) = Gedimat blocked

**Pourquoi Type C (Bloquant):**
- Phase 1 TMS dépend Médiafret API (IF available) or email parsing (IF not)
- Urgence pricing (tiering strategy) dépend Médiafret accepter premium urgence
- Scénario B ROI dépend Médiafret capacity + reliability SLA
- Decision WMS/TMS = different IF Médiafret unstable vs stable

---

### Plan de Collecte de Données C4

#### 1. Quelles Données Exactement Manquent?

| Donnée | Description | Usage | Actuel | Cible |
|---|---|---|---|---|
| **Médiafret contrat termes** | Tarifs, pénalités, capacity, urgence pricing | Formal SLA négociation | Verbal only | Written agreement |
| **Urgence capacity réelle** | Can Médiafret handle 10/mois urgence? Peak load? | Tiering service planning | Assumed 5-10/mois | Direct conversation Mélissa |
| **API ETA availability** | Médiafret provides tracking API (standard TMS) | Phase 1 TMS feasibility | Assumed available | Technical specs from Mélissa |
| **Backup transporteurs** | IF Médiafret refuse/unavailable, alternatives? | Risk mitigation | Zéro identified | 3-5 transporteur options |
| **Mélissa escalade** | Who covers when Mélissa absent/leave? | Bus factor mitigation | Zéro (single contact) | Xavier ou autre backup formal |
| **Pricing negotiation** | Can we negotiate -10-15% master contract? | Cost reduction scenario | Assumed possible | Formal RFQ process |

#### 2. Méthodes de Collecte (Détaillées)

**2a) Formal Contract Review (Legal + Angélique)**

```
Responsable: PDG + Agent 7 (Juridique)
Timeline: 1 semaine (collect existing docs)
Coûts: €200 (legal review if needed)

Étapes:
├─ 1. Recherche: Does Gedimat have ANY written contract Médiafret?
│   ├─ PDG office: Email folder "Médiafret" for agreements
│   ├─ Finance: Invoices = implicit terms evidence?
│   ├─ Angélique: Any documents received?
│   └─ Legal: Any past amendments or discussions?
│
├─ 2. IF contract found:
│   ├─ Extract: Pricing, pénalités, urgence clauses
│   ├─ Legal review: Are terms favorable Gedimat?
│   ├─ Gaps: What's NOT covered (capacity, API, escalade)?
│   └─ Status: When expire? Renewal upcoming?
│
├─ 3. IF no contract (likely):
│   ├─ Implication: Relationship ad-hoc, legal exposure
│   ├─ Risk: Médiafret can change terms any time (no protection)
│   ├─ Action: Formalize immediately (priority P0)
│   └─ Timeline: Draft addendum (legal) + negotiate (Angélique/PDG)
│
└─ 4. Output:
   ├─ Current contract status (formal or ad-hoc)
   ├─ Key terms extracted (if any)
   ├─ Gaps identified
   └─ Formalization priority & timeline
```

**2b) Direct Conversation Mélissa (Capacity + API)**

```
Responsable: Angélique or PDG (telephone call)
Timeline: 1 semaine (30 min call)
Coûts: €0

Étapes:
├─ 1. Preparation: Script structured questions
│   ├─ "Mélissa, audit partenariat Gedimat here. Few technical/business questions ok?"
│   ├─ Tone: Collaborative, not accusatory
│   └─ Objective: Understand capacity + capability, not pressure
│
├─ 2. Questions (30 min call):
│   │
│   ├─ CAPACITY:
│   │  ├─ "Quand vous êtes surchargée, avez-vous refusé enlèvements Gedimat?"
│   │  ├─ "Quel volume maximum pouvez-vous garantir par mois?"
│   │  ├─ "Urgences (J+0-1): Combien par mois possible, peak load?"
│   │  └─ "Si nous demandons 20 urgences/mois possible ou problématique?"
│   │
│   ├─ PRICING:
│   │  ├─ "Current tarifs 2025: €/tonne baseline vs urgence premium?"
│   │  ├─ "Possible negotiate master contract -10-15% volume discount?"
│   │  ├─ "Urgence premium: how much extra for J+0-1 delivery?"
│   │  └─ "Minimum volume order (is there consolidation threshold)?"
│   │
│   ├─ TECHNICAL (API):
│   │  ├─ "Does Médiafret provide ETA tracking API for partners?"
│   │  ├─ "NDA/agreement process if we want technical integration?"
│   │  ├─ "Timeline: Can be ready January or need lead time?"
│   │  └─ "Alternative: Email tracking, document parsing possible?"
│   │
│   ├─ ESCALADE:
│   │  ├─ "Who is backup contact if you're unavailable (vacation, leave)?"
│   │  ├─ "Xavier, someone else? Contact info?"
│   │  └─ "Process: Should we formalize escalade procedure?"
│   │
│   └─ RELATIONSHIP:
│      ├─ "Any concerns Gedimat side? Issues with service level?"
│      ├─ "From Médiafret: room improve, any feedback?"
│      └─ "Open discussing master contract (formal terms)?"
│
├─ 3. Document: Notes call + action items
│   ├─ Capacity limits (quantified)
│   ├─ Pricing agreement (current + negotiation potential)
│   ├─ API feasibility (timeline + contacts)
│   ├─ Backup contact formalized
│   └─ Next steps: Contract discussion January
│
└─ 4. Output:
   ├─ Capacity reality: "Mélissa confirmed 15 urgences/mois possible" (vs assumed 5-10)
   ├─ Pricing: "Master contract discussion feasible, -10% possible if volume commit"
   ├─ API: "Standard TMS API available, NDA needed, ready January"
   ├─ Risk mitigation: "Xavier is backup, process doc coming"
   └─ Confidence: Direct conversation vs assumption
```

**2c) Transporteur Benchmark (Backup Options)**

```
Responsable: Agent 4 (IT) + Angélique
Timeline: 2 semaines (research + 3-5 conversations)
Coûts: €200 (calls + trial)

Étapes:
├─ 1. Identify 3-5 alternative transporteurs France (construction focused)
│   ├─ Research: FM Logistic, Transdev, regional carriers
│   ├─ Selection: Similar size/geography coverage Médiafret
│   ├─ Capability: Can they serve Gedimat 3 dépôts?
│   └─ Contact: Sales person + technical contact
│
├─ 2. Conversation each (15-20 min):
│   ├─ "Interested evaluate logistics partnership. Can you service 3 dépôts?"
│   ├─ "Volume: ~200-300 shipments/month, mix standard + urgent"
│   ├─ "Urgence: 10-15 urgent/month J+0-1. Feasible?"
│   ├─ "Pricing: How much for master contract vs à la carte?"
│   ├─ "API: ETA tracking, integration with WMS/TMS possible?"
│   └─ "Timeline: Could start January if needed?"
│
├─ 3. Comparison matrix:
│   ├─ Capacity: Médiafret vs Option A vs Option B (quantified)
│   ├─ Pricing: Standard + urgent rate each
│   ├─ API availability: Yes/No/TBD
│   ├─ Reliability: References from Gedimat peers?
│   └─ Risk: Single vs dual carrier strategy?
│
├─ 4. Strategic insight:
│   ├─ IF Médiafret only option → negotiate from weak position
│   ├─ IF multiple transporteurs available → leverage competition
│   ├─ Dual-carrier strategy: 70% Médiafret + 30% backup (risk mitigation)
│   └─ NPS consideration: Need reliability SLA (diverse carriers better?)
│
└─ 5. Output:
   ├─ Backup transporteur identified (name + contact + capabilities)
   ├─ Comparison: Médiafret vs alternatives (objective)
   ├─ Negotiation leverage: "We have options" (credible)
   ├─ Risk mitigation plan: IF Médiafret fails, executable pivot
   └─ Confidence: Alternatives reduce single-source risk

Expected Finding:
├─ Médiafret = good option (local, proven) but NOT monopoly
├─ Backup available (FM Logistic regional viable)
└─ Negotiation position: Dual-carrier approach improves terms
```

**2d) Invoice Analysis (Current Terms Implicit)**

```
Responsable: Angélique + Finance
Timeline: 1 semaine (extract 6-12 months invoices)
Coûts: €0

Étapes:
├─ 1. Extract: Last 12 months Médiafret invoices
├─ 2. Analysis:
│   ├─ Tarifs: €/tonne variation (why month-to-month change?)
│   ├─ Volume: Monthly shipments count + average kg/shipment
│   ├─ Peak: Which months highest volume/cost?
│   ├─ Urgence premium: Any line items for "express" or "urgent"?
│   ├─ Penalties: Any credits/adjustments (problem rebates)?
│   └─ Average cost: €/shipment baseline
│
├─ 3. Findings:
│   ├─ Trend: Costs rising/stable/declining? (inflation vs volume negotiation)
│   ├─ Variability: Why tariff changes? (not explained?)
│   ├─ Premium pricing: IF urgent orders, what cost differential?
│   └─ Documentation: Are terms clear on each invoice? (probably NOT)
│
└─ 4. Output:
   ├─ Médiafret cost baseline (€/shipment average)
   ├─ Urgence premium visible (if exists)
   ├─ Tariff trend (stable or volatile?)
   ├─ Invoice clarity (terms documented or opaque?)
   └─ Negotiation baseline: "We pay €X average, propose €Y master contract"
```

#### 3. Timeline Collecte C4

```
SEMAINE 1:
├─ Contract search: PDG + legal (1 jour)
├─ Mélissa call: Angélique (0.5 days)

SEMAINE 2:
├─ Transporteur research: Agent 4 (5 days research)
├─ Invoice analysis: Finance (2 days)

SEMAINE 2-3:
├─ Transporteur conversations: Agent 4 (3-5 calls, 1 day total)
├─ Documentation: Legal prepare contract template (2-3 days)

SEMAINE 3:
├─ Data synthesis: PDG + Angélique (1 day)
├─ Negotiation strategy: Decision whether proceed formal contract (1 day)

TOTAL: 2-3 semaines (fastest of all C contradictions)
```

#### 4. Coûts de Collecte C4

| Activité | Coûts Directs | Heures Travail | Coûts Indirects | Total |
|----------|---|---|---|---|
| Contract search/review | €200 | 5h (PDG/Legal) | €150 | €350 |
| Mélissa direct call | €0 | 0.5h (Angélique) | €50 | €50 |
| Transporteur benchmark | €200 | 15h (Agent 4 + Angélique) | €300 | €500 |
| Invoice analysis | €0 | 5h (Finance/Angélique) | €100 | €100 |
| Legal contract template | €200 | 8h (Legal) | €200 | €400 |
| **TOTAL C4** | **€600** | **33.5 heures** | **€800** | **€1,400** |

#### 5. Responsables C4

| Rôle | Domaine | Tâches |
|-----|---------|--------|
| **PDG** | Leadership | Contract review, Mélissa communication strategy, negotiation approval |
| **Agent 7 (Juridique)** | Legal | Contract review, SLA template draft, negotiation legal terms |
| **Angélique** | Logistique/CRM | Mélissa conversation, invoice analysis, relationship management |
| **Agent 4 (IT)** | Technologie | Transporteur benchmark, API technical evaluation |
| **Finance (Agent 2)** | Finance | Invoice cost analysis, pricing comparison |

---

### Decision Tree Post-Données C4

```
APRÈS COLLECTE DONNÉES (Semaine 3-4):

Decision Point 1: CONTRAT FORMELLE EXIST?

├─ IF written contract found (formal):
│  ├─ Review: Terms favorable? Urgence clauses clear? Capacity guaranteed?
│  ├─ Renewal: When expire? Negotiation timing?
│  ├─ Action: Formalize addendum (API + SLA + urgence pricing) vs new master contract
│  └─ Timeline: Negotiation 4 weeks (January 2026)
│
└─ IF NO contract (ad-hoc only) ← LIKELY:
   ├─ Risk: HIGH (Médiafret can change terms anytime, legal exposure)
   ├─ Action: IMMEDIATE formalize (priority P0)
   ├─ Approach: Draft addendum + present Mélissa (quick vs new contract)
   ├─ Timeline: DECEMBER 2025 urgent negotiation
   └─ Budget: €200-500 legal cost (worth investment)

---

Decision Point 2: MÉLISSA CAPACITY CONFIRMED?

├─ IF Mélissa confirms capacity 15-20 urgences/mois:
│  ├─ → Tiering service VIABLE (CRITIQUE tier feasible)
│  ├─ → Planning: Urgence capacity abundant (not bottleneck)
│  ├─ → Strategy: Service tiers launch confirmed (no risk urgence fail)
│  └─ → Confidence: Mélissa reliable partner
│
├─ IF Mélissa says 5-10 urgences/mois (capacity limited):
│  ├─ → Tiering service RISKY (CRITIQUE tier small)
│  ├─ → Planning: Must limit urgent % (negotiate with clients IF demand >capacity)
│  ├─ → Strategy: Standard tier dominant, CRITIQUE premium small
│  ├─ → Alternative: Dual-carrier strategy (backup transporteur for overflow)
│  └─ → Confidence: Limited capacity, need mitigation
│
└─ IF Mélissa unclear/evasive (red flag):
   ├─ → Risk: HIGH (relationship unstable)
   ├─ → Action: Accelerate backup transporteur activation
   ├─ → Strategy: Move to 50% Médiafret + 50% backup (reduce dependency)
   ├─ → Timeline: Start backup January (parallel operations)
   └─ → Contingency: IF Mélissa unable scale, transition seamless

---

Decision Point 3: API ETA AVAILABLE?

├─ IF Médiafret API available + NDA straightforward:
│  ├─ → Phase 1 TMS DEPLOYMENT CONFIRMED (January-March 2026)
│  ├─ → Integration: Standard approach (vendor supports API integration)
│  ├─ → Timeline: 6-8 weeks implementation (no custom delays)
│  ├─ → Cost: €3-5k estimated still valid
│  └─ → ROI: 20-24 months payback remains realistic
│
├─ IF Médiafret API NOT available (email tracking only):
│  ├─ → Phase 1 TMS DELAYED (alternative parsing needed)
│  ├─ → Custom solution: Email regex parser (€5-10k more expensive)
│  ├─ → Timeline: 10-12 weeks implementation (custom build)
│  ├─ → Cost: €8-15k (significant increase)
│  ├─ → ROI: 30-36 months payback (marginal)
│  └─ → Alternative: Evaluate Shippeo/other TMS with built-in Médiafret parsing
│
└─ IF API unknown/TBD (customer technical support weak):
   ├─ → Risk: HIGH (Médiafret not TMS-ready)
   ├─ → Implication: Upgrade Médiafret impossible (change transporteur?)
   ├─ → Decision: Evaluate backup transporteur ASAP (urgent)
   └─ → Timeline: Backup assessment accelerated (week 2)

---

Decision Point 4: BACKUP TRANSPORTEUR VIABLE?

├─ IF viable alternative identified (cost + capacity ok):
│  ├─ → Negotiation leverage: "We have options" (credible)
│  ├─ → Strategy: Dual-carrier 60% Médiafret + 40% backup (risk mitigation)
│  ├─ → Pricing: Better negotiation power (Médiafret competes)
│  ├─ → Capacity: Overflow handled (service reliability improved)
│  └─ → Timeline: Formal RFQ both carriers (December-January)
│
├─ IF backup available but MORE expensive:
│  ├─ → Insight: Médiafret competitive (keep primary relationship)
│  ├─ → Strategy: Single-carrier Médiafret, but backup contractually available
│  ├─ → Risk mitigation: IF Médiafret fails, execute pivot (2-3 weeks ramp)
│  ├─ → Budget: Small retainer with backup (€500-1000/month) worth cost
│  └─ → Confidence: Reliable backup = operational resilience
│
└─ IF NO viable backup found:
   ├─ → Risk: CRITICAL (Médiafret single-source dependency)
   ├─ → Action: Formalize contract aggressively (protection)
   ├─ → SLA: Strong capacity guarantees + low penalty for non-performance
   ├─ → Escalade: Xavier + other backup Médiafret formal (bus factor mitigation)
   └─ → Contingency: Plan in-house backup (cross-dock own vehicle?) TBD

---

Decision Point 5: PRICING NEGOTIATION?

├─ IF Mélissa indicates master contract negotiation possible:
│  ├─ → RFQ process: Formal pricing request (volume commitment + duration)
│  ├─ → Target: -10-15% volume discount + urgence premium clear
│  ├─ → Timeline: RFQ December → responses January → signature January
│  ├─ → Leverage: Backup transporteur option (mention confidentially)
│  ├─ → ROI: €5-10k/year savings (payback contracts, quick win)
│  └─ → Confidence: Negotiation standard practice (likely successful)
│
├─ IF Mélissa resistant (rates fixed, no negotiation):
│  ├─ → Insight: Médiafret takes or leaves approach (not flexible)
│  ├─ → Decision: Accept current rates vs evaluate backup seriously
│  ├─ → IF backup better: Migrate (strategic change)
│  ├─ → IF backup same: Keep Médiafret (relationship known)
│  └─ → Acceptance: Rates non-negotiable, no immediate cost advantage
│
└─ IF pricing unclear/varying (inconsistent invoices):
   ├─ → Risk: Médiafret billing practices opaque (control issue)
   ├─ → Action: Demand contract written (protect Gedimat)
   ├─ → Requirement: Fixed rates + scaling bands (volume brackets)
   └─ → Contingency: IF unclear, activate backup transporteur evaluation

---

FINAL DECISION FRAMEWORK:

├─ STEP 1 - CONTRACT FORMALIZE (IMMEDIATE, P0):
│  └─ Draft addendum: Capacity guarantees + urgence pricing + API terms
│     Negotiation: December 2025 (4 weeks)
│     Success criteria: Formal agreement signed (not verbal)
│
├─ STEP 2 - CAPACITY CONFIRMATION (WEEK 1):
│  └─ IF confirmed 15+ urgences/month: Tiering service GO
│     IF limited 5-10/month: Tiering service limited (strategy adjust)
│     IF unclear: Backup transporteur P1 (activate Jan)
│
├─ STEP 3 - API DECISION (WEEK 2):
│  └─ IF available: Phase 1 TMS January 2026 (standard path)
│     IF not available: Custom solution or backup TMS evaluation
│     Timeline: If decision changes, re-evaluate WMS cost/ROI
│
├─ STEP 4 - BACKUP STRATEGY (WEEK 2-3):
│  └─ IF viable alternative: Dual-carrier (60/40 split)
│     IF not available: Single-carrier (Médiafret contract protection)
│     Risk mitigation: Esclade formal (Xavier backup contact)
│
└─ OVERALL CONFIDENCE POST-DATA:
   └─ IF all positive: 90% confidence Phase 1 TMS/Tiering viable
      IF mixed: 70% confidence (mitigations needed)
      IF negative: 40% confidence (strategy recalibration required)

Confidence Post-Data: 80-85% (fact-based, direct source)
```

---

### Recommandation Intérimaire C4

**Pendant que données collectées (2-3 semaines):**

```
1. PREPARE Contract Template (Legal):
   ├─ SLA addendum draft (capacity + urgence pricing + API terms)
   ├─ Timeline: Ready by December 10 (before Mélissa conversation)
   └─ Objective: Professional negotiation starting point

2. SCHEDULE Mélissa Discussion (Angélique):
   ├─ Email: "Want audit partenariat Gedimat-Médiafret, 30 min call?"
   ├─ Tone: Collaborative, not confrontational
   ├─ Timing: Schedule early December (2-3 weeks before contract)
   └─ Objective: Understand capacity + establish relationship upgrade

3. RESEARCH Backup Transporteurs (Agent 4):
   ├─ Identify 3-5 alternatives (FM Logistic, Transdev, regional)
   ├─ Quick qualification: "Can you service 3 dépôts, construction supply?"
   ├─ Keep confidential (not mention to Médiafret yet)
   └─ Objective: Have options credible for negotiation

4. COMMUNICATION:
   ├─ Team: "Formalizing Médiafret contract (upgrade from ad-hoc)"
   ├─ PDG: "Will negotiate API access + capacity guarantees"
   └─ Objectif: Manage expectations (contract formalization = good news)

5. DECISION ESCALADE:
   ├─ IF Mélissa unavailable or evasive → activate backup research urgently
   ├─ IF contract negotiation difficult → consider dual-carrier strategy
   └─ Timeline: Contract SIGNED by January 31, 2026
```

---

### Confiance Post-Collecte C4

**Avant Données:** 60% (assumed, not verified)
**Après Données:** 85% (direct conversation + benchmark + contract formal)

---

## RÉSUMÉ GLOBAL - TOUS CONTRADICTIONS TYPE C

### Timeline Parallélisée

```
NOVEMBRE 2025 (Weeks 45-48):

SEMAINE 1:
├─ C1: Revenue audit (1 day), Dépôts strategy (0.5 day)
├─ C2: CRM data extract (1 day)
├─ C3: CRM churn audit (1 day)
├─ C4: Contract search (1 day), Mélissa schedule

SEMAINE 2-3:
├─ C1: Clients forecast (20 appels), WMS benchmarks (start 5 interviews)
├─ C2: CRM tagging (15 heures), Client phone survey (start)
├─ C3: Lost client interviews (20+ appels)
├─ C4: Transporteur research + Mélissa call

SEMAINE 4-5:
├─ C1: Timesheet data, API audit, finish WMS benchmarks
├─ C2: Saison breakdown, finish phone survey, benchmark research
├─ C3: Penalty audit, LTV analysis, NPS survey finish
├─ C4: Transporteur calls, invoice analysis, contract template ready

SEMAINE 6-7 (JANVIER 2026):
├─ C1: Data synthesis, decision gate (WMS go/no-go)
├─ C2: Data synthesis, scoring recalibration
├─ C3: Churn report, win-back strategy
├─ C4: Contract negotiation, backup strategy
```

### Investment & ROI Total

| Type C | Collection Cost | Hours | Timeline | Confidence Before | Confidence After |
|--------|---|---|---|---|---|
| **C1 WMS** | €1,550 | 52h | 4 weeks | 45% | 85% |
| **C2 Urgence** | €1,400 | 75h | 6-8 weeks | 55% | 85% |
| **C3 Churn** | €1,550 | 60h | 4-5 weeks | 50% | 85% |
| **C4 Médiafret** | €1,400 | 33.5h | 2-3 weeks | 60% | 85% |
| **TOTAL** | **€6,000** | **220.5h** | **6-8 weeks parallel** | **53% avg** | **85% avg** |

### ROI Data Investment

```
Cost of data collection: €6,000 + 220 hours (€4-8k labor at €20-30/hour)
Total data cost: ~€10-14k

Value avoiding bad decisions:
├─ WMS wrong call: €50-150k capital error
├─ Urgence wrong call: €30-50k misdirected investment
├─ Churn underestimated: €50-100k opportunity cost (missed retention)
├─ Médiafret unstable: €20-40k operational disruption

Total risk mitigation: €150-350k

ROI: 10-35x return on €10-14k investment
= HIGHLY RECOMMENDED IMMEDIATE INVESTMENT
```

---

## CONCLUSION & NEXT STEPS

### Decision Authority

| Contradiction | Decision Owner | Timeline | Authority |
|---|---|---|---|
| **C1 WMS** | PDG + Finance | January 2026 (post data) | Strategic investment decision |
| **C2 Urgence %** | Agent 3 + Logistique | January 2026 | Tier service design decision |
| **C3 Churn** | PDG + Satisfaction | January 2026 | Communication investment ROI |
| **C4 Médiafret** | PDG + Legal | December 2025 | Contract negotiation + execution |

### Immediate Actions (This Week)

- [ ] Revenue audit (PDG + Comptable): 1 day
- [ ] CRM audit initiate (Angélique + Agent 5): 1 day
- [ ] Contract search (PDG + Legal): 1 day
- [ ] WMS benchmarks start (Agent 4): 5 calls week 1
- [ ] Transporteur research (Agent 4): 2 days week 1

### Contingency Plans

**IF data collection delays >2 weeks:**
└─ Proceed with interim recommendations (use current estimates)
└─ Defer final decisions to February 2026 instead of January

**IF data reveals negative surprises (e.g., churn >20%):**
└─ Escalate to PDG immediately (emergency action plan needed)
└─ Accelerate assistant hiring (December not January)

**IF Médiafret contract negotiation fails:**
└─ Activate backup transporteur (dual-carrier strategy)
└─ Phase 1 TMS timeline adjust (alternative provider)

---

**Document:** PASS6_DEBUG4_TYPE_C_DATA_COLLECTION_PLANS.md
**Statut:** ✅ COMPLET - PRÊT EXÉCUTION
**Confiance:** 85% post-data (vs 53% actuellement)
**Timeline:** 6-8 semaines parallélisable
**ROI:** 10-35x return on €10-14k investment
**Prochaine Étape:** Lancer collecte semaine 45 (cette semaine)
**Responsable:** Pass 6 Debug Agents + PDG + Angélique

---

**Préparé:** 16 novembre 2025
**Par:** Pass 6 Debug Agent 4 (Type C Resolution Expert)
**Pour:** PDG Gedimat + Pass 6 Steering Committee
