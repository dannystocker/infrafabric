# PASS 5 AGENT 3 - CARTOGRAPHIE TENSIONS & ARBITRAGES POUR PASS 6
## Zones de Tension Inter-Domaines & Mécanismes Résolution

**Date:** 16 novembre 2025
**Agent:** Pass 5 Agent 3 - Synthesis "Cartographie Tensions"
**Audience:** Pass 6 Debug Agents, PDG, Arbitrage Décisionnelle
**Statut:** Compilation Pass 4 Agents 1-8, structuration arbitrages
**Format:** 3 pages + tables référence

---

## 1. MATRICE CONTRADICTIONS PAR DOMAINE

### Tableau Synthétique - 14 Contradictions Identifiées

| ID | Contradiction | Domaines Conflictuels | Impact €/NPS | Complexité Arbitrage | Pass 6 Priorité |
|----|---------------|----------------------|--------------|---------------------|-----------------|
| **T1** | Urgence Client vs Consolidation Coûts | Finance vs Logistique vs Satisfaction | €4-10k/an, NPS -5 | Moyenne (tier pricing) | P1 HAUTE |
| **T2** | Proximité Dépôt vs Volume (Défense Territoriale) | Logistique vs RH vs SI | €2-4k/an, NPS +2 | Élevée (incitations RH) | P1 HAUTE |
| **T3** | Fiabilité SLA vs Urgences Ad-hoc | Logistique vs CRM | €3-8k/an, NPS +8 | Moyenne (rules formales) | P2 MOYENNE |
| **T4** | IT Investment (TMS/WMS) vs ROI Rapide | Finance vs SI | €30-50k, risque capital | Élevée (décision stratégique) | P1 HAUTE |
| **T5** | Coûts Fournisseurs Bas vs Relations Stables | Finance vs Juridique vs Relationnel | €5-15k/an, stabilité | Modérée (contrats) | P2 MOYENNE |
| **T6** | Automatisation Alertes vs Contact Personnel | SI vs CRM vs RH | €0/an, NPS +3 | Basse (hybrid possible) | P2 MOYENNE |
| **T7** | Autonomie Franchisés vs Coordination Centrale | Juridique vs Logistique | €0/an, risque légal | Élevée (gouvernance) | P1 HAUTE |
| **T8** | Transparence Coûts Dépôts vs Defensiveness | SI vs RH vs Logistique | €0/an, trust +10% | Basse (communication) | P3 BASSE |
| **T9** | Angélique Surcharge vs Coûts RH (Assistant) | RH vs Finance | €12-22k/an, risk bus factor | Basse (investment justifié) | P1 HAUTE |
| **T10** | Contrats Stricts vs Flexibilité Opérationnelle | Juridique vs Logistique | €500-2k/an, relation | Modérée (escalade progressive) | P2 MOYENNE |
| **T11** | Cost Leader vs Relationship Leader Positioning | Finance vs Marché vs Logistique | €100-200k/an (stratégie) | Très Élevée (stratégique) | P1 HAUTE |
| **T12** | Consolidation J+2 vs Service Express J+0 | Logistique vs Satisfaction vs Finance | €20-40k/an, NPS ±10 | Élevée (modèles opérationnels) | P2 MOYENNE |
| **T13** | Knowledge Concentration (Angélique) vs Scalabilité | RH vs Logistique vs SI | €25-50k/an, risk continuité | Basse (documentation process) | P1 HAUTE |
| **T14** | Scale 3 Dépôts vs Ambition Croissance Réseau | Marché vs Finance vs RH | €50-100k potentiel, vision | Très Élevée (stratégique long-terme) | P3 BASSE |

**Légende Impact:**
- €/NPS = Gain/Perte financier + NPS client estimé
- Complexité = Nombre domaines, dépendances, data requise
- Priorité = P1 (urgent, bloque autres), P2 (important, 3-6 mois), P3 (stratégique long-terme)

---

## 2. CLASSIFICATION TENSIONS: TROIS CATÉGORIES

### TYPE A: CONTRADICTIONS RÉSOLUES (Pass 4 Consensus ≥6 domaines alignés)

#### A1 - **Proximité Routing = Coûts + Satisfaction Alignés** ✅

**Énoncé:** "Finance croit coûts baissent si livrer dépôt loin (volumineux), mais proximité = moins cher ET meilleure satisfaction"

**Consensus Pass 4:**
- Agent 1 (Logistique): Scoring MDVRP 40% proximité = optimal
- Agent 2 (Finance): Break-even analysis = proximité gagne 90% cas
- Agent 3 (Satisfaction): Client urgence accepte navette si rapide
- Agent 5 (CRM): Client loyalty si délai prévisible (proximité = stable)
- Agent 8 (Marché): Leroy Merlin/Point.P = proximité règle (pas exception)

**Arbitrage Consensuel:**
```
RÈGLE: Dépôt optimal = distance fournisseur MINIMALE (scoring 40% poids)
       SAUF si client urgence documentée (pénalité client > surcoût)
```

**KPI Validation:** Coûts -€100/trajet (vs volume-first) + Satisfaction +50 (NPS +2-3 points) → Win-Win.

**Implémentation PASS 6:** Codifier dans Excel scoring, pas débat.

---

#### A2 - **Service Tiers Explicite = Trade-offs Acceptés** ✅

**Énoncé:** "Client veut livraison rapide coûts bas = impossible. Si tiers explicites, clients acceptent délai si fiable."

**Consensus Pass 4:**
- Agent 3 (Satisfaction): Tiers ÉCONOMIE/EXPRESS/CRITIQUE = client agency
- Agent 2 (Finance): Marge preservation si prix transparent vs wars
- Agent 6 (RH): Dépôts collaborent si règles claires (pas favoritism caché)
- Agent 8 (Marché): Point.P = "J+1 garanti" (accepté vs "rapide aléatoire")

**Arbitrage Consensuel:**
```
ÉCONOMIE (70% volume): J+5-7, prix standard, marge 12%
EXPRESS (20% volume): J+3, +5% prix, marge 10%
CRITIQUE (10% volume): J+1, +15% prix, marge 8%
```

**KPI Validation:** Volume allocation stable vs chasing every urgent = moins retards, marge meilleure.

**Implémentation PASS 6:** Présenter tiers clients Q1 2026, tracker adoption.

---

#### A3 - **Scoring Multicritère Transparent = Conflit Dépôts Réduit** ✅

**Énoncé:** "Arbitrage dépôt pivot: si données (distance, urgence, volume) visibles, dépôts acceptent décision vs « Angélique feeling »"

**Consensus Pass 4:**
- Agent 1 (Logistique): Formule MDVRP 40/30/30 fournit légitimité
- Agent 6 (RH): Dashboard transparence élimine defensiveness
- Agent 7 (Juridique): Addendum SLA = gouvernance formelle
- Agent 8 (Marché): Leroy Merlin/Point.P = règles explicites (pas arbitrage)

**Arbitrage Consensuel:**
```
SCORE = (Proximité × 40%) + (Volume × 30%) + (Urgence × 30%)
Résultat ≥ 65 pts → Décision auto (pas escalade)
Résultat 45-65 pts → Angélique review + appel si contestation
Résultat < 45 pts → Escalade PDG (cas complexe)
```

**KPI Validation:** % arbitrages acceptés sans escalade: baseline 60% → target 90%.

**Implémentation PASS 6:** Excel macro MDVRP prête, test 100 cas.

---

### TYPE B: CONTRADICTIONS ARBITRABLES (2-3 options viables, PDG choix)

#### B1 - **Urgence Client vs Consolidation Coûts** 🔀

**Énoncé:** Quand accepter surcoût transport pour urgence client vs exiger consolidation 2-3j?

**Options Viables:**

| Option | Approche | Coûts | Service | Risque |
|--------|----------|-------|---------|--------|
| **A: Urgence Prioritaire** | Si client urgence documentée, payer express même si 30% surcoût | +€20-40/urgence | NPS +10, retention élevé | Marge écrasée si >15% urgences |
| **B: Consolidation Stricte** | Refuser urgences, tous J+3-5 consolidé | -€10-20/trajet | Opérations simples | Perte clients chantier date-fixe |
| **C: Tiering Explicite** | Client choisit tier (ÉCONOMIE/EXPRESS/CRITIQUE) avec transparence prix | Neutre (client paie) | Marge stable 12-15% | Adoption lente si client pas convaincu |

**Données Critiques (PASS 3 estimées):**
- % urgences réelles: 70-80% (à valider audit 2 mois)
- Perte client si retard: €3-5k (pénalité chantier)
- Surcoût urgence: 15-30% transport

**Philosophies Applicables (IF.guard):**

**Peirce (Pragmatisme):** "Quelle option FONCTIONNE pratiquement? Si 70% urgences réelles, refuser impossible → Option C tiering."

**James (Instrumentalisme):** "Quelle option maximise résultat client? Urgent → honoré. Standard → economical. Outcome: clients satisfaits."

**Quine (Cohérentisme):** "Quelle option crée système cohérent? Tiering C = cohérent (urgence + coûts explicites), pas tension implicite."

**Recommendation PASS 6:** ✅ **Option C (Tiering Explicite)**
- Probabilité: 70% urgences réelles, client accepte prix premium si transparent
- Confiance: 75%
- Implémentation: 2-3 semaines (formation sales + SMStemplate)

---

#### B2 - **Proximité Dépôt vs Défense Territoriale (Incitations RH)** 🔀

**Énoncé:** Manager dépôt refuse pivot proximité (coûts) pour protéger son chiffre (volume), comment aligner?

**Options Viables:**

| Option | Approche | Coûts | Collaboration | Risque |
|--------|----------|-------|---------------|--------|
| **A: Penalty** | Manager qui refuse arbitrage = malus bonus (-€2-3k/an) | Aucun supplément | Risque: resentment, turnover | Légal mais agressif |
| **B: Bonus Groupe 40%** | 40% bonus basé network KPI (coûts, service, NPS groupe) + 60% local | Aucun supplément | Incite collaboration, gagne-gagne | Complexité calcul, perception équité |
| **C: Transparence Dashboard** | Voir coûts réels dépôts → dépôts auto-ajustent (no penalty, juste visibilité) | 1k€ setup | Collaboration naît transparence | Lent (3-6 mois adoption), peut pas marcher |

**Philosophies Applicables:**

**Locke (Empirisme):** "Basez-vous sur DATA visible, pas intuition/sentiment. Dashboard coûts = fait observable."

**Confucius (Harmonie):** "Bonus groupe préserve harmony (pas pénalité). Tous gagnent si réseau gagne."

**Buddha (Voie Milieu):** "Option B balance: incitation groupe + respect autonomie locale (60% bonus local)."

**Recommendation PASS 6:** ✅ **Option B (Bonus Groupe 40%)**
- Probabilité: RH accepte (voir succès Leroy Merlin model)
- Confiance: 70%
- Implémentation: 1 mois (définir KPIs, implémenter calcul, communication CEO)

---

#### B3 - **Angélique Surcharge vs Coûts RH (Assistant)** 🔀

**Énoncé:** Angélique 37h/semaine, bus factor = 1. Embaucher assistant (€22k/an) ou accepter risque?

**Options Viables:**

| Option | Approche | Coûts | Opérations | Risque |
|--------|----------|-------|------------|--------|
| **A: Embauche Assistant** | Recruter bac+2 logistique (22k€/an) pour tâches admin (alertes, CRM, emails) | €22k/an + 3k recrutement | Angélique peut mentoring + stratégie | Coûts RH impacts marge (-€22k) |
| **B: Automation + Cross-Training** | Excel macros alertes (€2-5k) + former 1 coordinateur dépôt backup | €5k investissement + temps | Risque partiel si Angélique absente, pas remplacement complet | Bus factor still ~1 (Angélique unique) |
| **C: Promotion Angélique + Assistant** | Angélique → Supply Chain Manager (€35-40k) + assistant (€22k) → 2 juniors learn from her | €34k additionnel/an | Scaling possible (3 coordinateurs régionaux possibles) | Chert augmentation budget RH (€34k) |

**ROI Calcul (Si Angélique quitte sans backup):**
- Coûts remplacement+ramp-up: €40k (nouvelle coordinatrice) + €30k churn (clients perdu 2-3 mois) = €70k
- Option A (€22k/an) = ROI 3x en 1 an (sauve 1 client vip)
- Option C (€34k/an) = Retent talent + scale possible, ROI 4-5 dépôts futur (+€50-80k/an)

**Philosophies Applicables:**

**Dewey (Expérimentalisme):** "Testez d'abord: automation + cross-training 2 mois (Option B), si échoue → assistant immédiat (Option A)."

**Peirce (Pragmatisme):** "Quelle marche? Risk €70k perte si Angélique part > coûts €22k assistant."

**James (Instrumentalisme):** "Outcome: Opérations stables + Angélique pas burnout → Option A ou C satisfont."

**Recommendation PASS 6:** ✅ **Option A (Immédiate) → Option C (6 mois)**
- Phase 1 (Janv 2026): Embauche assistant (€22k/an), automation emails/alertes
- Phase 2 (Fév 2026): Promote Angélique → Supply Chain Manager (€35-40k)
- Probabilité succès: 85% (RH standard, proven model autres entreprises)
- Confiance: 80%

---

#### B4 - **Cost Leader vs Relationship Leader Positioning** 🔀

**Énoncé:** Gedimat positionner comment? Pas-cher (impossible vs Leroy Merlin/Point.P) vs partenaire service (défendable)?

**Options Viables:**

| Option | Positionnement | Prix | Service | NPS Target | Marge |
|--------|-----------------|------|---------|-----------|-------|
| **A: Cost Leader** | "Gedimat = moins cher" | -10-15% vs Point.P | Standard J+5-7 | 25-30 | 11% |
| **B: Service Leader** | "Gedimat = rapide J+0-1" | +20-25% vs Point.P | Express garanti 48h | 35-40 | 9% |
| **C: Relationship Leader** | "Gedimat = partenaire artisan" | -2-5% vs Point.P | Stable J+2-3 + proactif | 40-50 | 12.5% |

**Marché Réalité:**
- Point.P = Cost Leader (75-80 dépôts, milkrun optimisé) → Gedimat cannot match
- Leroy Merlin = Service Leader (tech avancée, stock immense) → Gedimat cannot match
- Gedimat unique = Relationship (Angélique connaissance clients 10+ ans) → DEFENDABLE

**Philosophies Applicables:**

**Locke (Empirisme):** "Observez: Leroy Merlin gagne prix wars (scale). Point.P gagne J+1 (200 dépôts). Où Gedimat gagne? Relation artisan."

**Buddha (Voie Milieu):** "Ne cherchez extremes (moins cher OU plus rapide). Cherchez équilibre: prix correct + service stable + relation."

**Quine (Cohérentisme):** "Relationship leader crée système cohérent: prix + service + communication + knowledge = client fidèle vs transactionnel."

**Recommendation PASS 6:** ✅ **Option C (Relationship Leader)**
- 12-month roadmap: NPS 18-22 → 30-35 → 40-45
- Investment: €20k (NPS, SMS, CRM, FRET21 adhesion)
- ROI: Churn reduction 2-3% = €50-80k annually
- Probabilité: 80% (aligned Forces Gedimat)
- Confiance: 85%

---

### TYPE C: CONTRADICTIONS BLOQUANTES (Need Additional Data - Pass 6 research)

#### C1 - **WMS Investment ROI = Inconnue Croissance** 🔒

**Énoncé:** WMS coûte €50-100k setup, ROI 15-24 mois. À quel volume rentable?

**Données Manquantes:**
- Croissance annuelle revenue estimée: ?? (Pass 1 dit €15-20M actuels, pas croissance forecast)
- Volume 2027 anticipé: ?? (5 dépôts? Reste 3?)
- Automation economics: Si WMS réduit Angélique 10h/semaine, quelle valeur? (€10-20k? Ou impossible car expert conseil)

**Pass 6 Action:**
1. Audit croissance clients (3 mois): Si volume 2027 >€20M (growth >25%), WMS justifié
2. Scenario modeling: "If 5 dépôts + 2M€ volume → WMS ROI 18 mois?" vs "If 3 dépôts + €18M → ROI 36 mois (not viable)"
3. Decision gate: 2027 Q1 based on 2026 validated growth

**Arbitrage Provisoire PASS 6:** Phase 0-1 Excel/Zapier (3-6 months), defer WMS decision Q1 2027.

---

#### C2 - **Urgence Client % Réelle = Assumption A Valider** 🔒

**Énoncé:** Pass 3 estimé 70-80% commandes "urgence" (chantier date-fixe). Réalité?

**Données Manquantes:**
- Audit 500 commandes 2025: breakdown par type (réelle urgence vs "soon as possible")
- Client interviews: "What deadline is must-have vs negotiable?"
- Competing transporters: Point.P sees 40% urgence real, 60% flexible?

**Pass 6 Action:**
- CRM audit 2 mois: Tag réelle urgence vs client saying "urgent" but flexible
- Result: Refine urgency % accurate
- If <50% réel urgence → Option C tiering less appealing (fewer premium clients)
- If >80% réel urgence → Must embrace urgence service (expense justified)

**Arbitrage Provisoire PASS 6:** Assume 65% réel urgence, refine Q1 2026.

---

#### C3 - **Pertes Commandes Détail = CRM Audit Requis** 🔒

**Énoncé:** Pass 2 estimated €3-12k/an perte clients (Électricien Y disappears, réclamations non-documentées). Réalité?

**Données Manquantes:**
- CRM audit: clients 2024 vs 2025 (vrai churn rate percentage?)
- Raison churn: Retard (40%), Prix (30%), Relation (20%), Autre (10%)? Or different ratio?
- Pénalité client calculée vs réel (contrats signed =€X, actual payé = €Y?)

**Pass 6 Action:**
- CRM deep-dive 2 mois: Vrai churn clients €20k+ = 3? 10? None?
- Interview clients "lost": Pourquoi parti (retard, concurrence, autre)?
- Refine churn economics: Si 2-3 VIP clients/an perte = ROI communication/NPS justifié immédiate

**Arbitrage Provisoire PASS 6:** Conservatively assume €8k/an loss, make NPS investment mandatory.

---

#### C4 - **Médiafret Capacité Urgences = Contract Reality** 🔒

**Énoncé:** Si Gedimat demande 5 urgences/mois J+0, Médiafret accepte? À quel coûts?

**Données Manquantes:**
- Contract terms Médiafret-Gedimat: (likely ad-hoc, not documented per Agent 7)
- Mélissa actual capacity: Quand surchargée? Refus precedents?
- Alternative transporteurs availability: If Médiafret says non, qui appeler?

**Pass 6 Action:**
1. Immediate: Formalize Médiafret contract (SLA, urgence price +40%, capacity guarantee) ← JURIDIQUE PRIORITY
2. Validate: "Can you handle 5 urgences/mois?" from Mélissa (direct conversation)
3. Negotiate: "Si oui, à quel prix? Si non, backup transporteur?"
4. Prepare backup: Identify 2-3 alternative transporteurs (Transdev, FM Logistic, autres régionaux)

**Arbitrage Provisoire PASS 6:** Assume Médiafret can handle 10 urgences/mois, formalize contract immediately.

---

## 3. PHILOSOPHIES ARBITRAGE (IF.guard Framework)

Pour chaque contradiction Type B, appliqué 8 philosophers pour guider decision:

### **Locke (Empirisme): "Soyez Basés sur DATA"**

**Principe:** Évitez intuition/feeling. Choisir option appuyée par observations/mesures.

**Applications Gedimat:**
- T2 (Proximité vs Volume): "Dashboard coûts réels" (data) vs "mon feeling dépôt défend"
- T4 (IT Investment): "Pass en chiffre (ROI -40% année 1)" vs "ça ferait bien"

**Recommandation:** Audit data AVANT décision (€2-3k cost, sauve €50k erreurs)

---

### **Peirce (Pragmatisme): "Choisissez Ce Qui Fonctionne"**

**Principe:** Si deux théories contradictoires, celle qui produit résultats pratiques gagne.

**Applications Gedimat:**
- T1 (Urgence vs Consolidation): "Tiering fonctionnne?" (test 50 cas) vs "théorie consolidation pure"
- T12 (J+2 vs J+0): "Quel délai clients acceptent?" (pragmatique) vs "chercher perfection"

**Recommandation:** Pilot test quick-win 3 mois avant full rollout.

---

### **Buddha (Voie Milieu): "Équilibrez Extrêmes"**

**Principe:** Évitez polarisation. Solution souvent middle-ground entre deux extrêmes.

**Applications Gedimat:**
- T2 (Proximité strict vs Volume libre): "Bonus groupe 40%" = milieu (pas zéro, pas 100% groupe)
- T11 (Cost vs Service): "Relationship leader" = ni cheapest ni fastest, stable équilibre
- T6 (Automation vs Humain): "70% automation + 30% personal" = hybrid

**Recommandation:** Rejecter solutions 100/0, chercher 60/40 ou 70/30.

---

### **Confucius (Harmonie): "Préservez Relations"**

**Principe:** Efficacité importante, mais pas au prix de relations long-terme.

**Applications Gedimat:**
- T2 (Dépôt managers): "Bonus groupe" preserves harmony, vs "penalty" destruction relation
- T5 (Fournisseur): "Contrats justes" (pas extreme penalties), escalade progressive
- T10 (Contrats vs Flexibilité): "Clauses stricts MAIS escalade progressive" protège relation

**Recommandation:** Balance efficiency + relationship, pas win-at-all-costs.

---

### **Quine (Cohérentisme): "Créez Système Cohérent"**

**Principe:** Évitez contradictions internes. Solution doit fit ensemble (pas patchwork).

**Applications Gedimat:**
- T11 (Positioning): "Relationship leader" cohérent (service + prix + knowledge = tout aligne), vs "cost leader" interne contradiction (cher opérer, prétend cheap)
- T3 (SLA vs Urgences): "Tiering explicite" cohérent (chaque tier has own SLA), vs "mixture urgence/consolidation" = confusing

**Recommandation:** Chaque décision doit renforcer système, pas créer tensions.

---

### **James (Instrumentalisme): "Optimisez Outcomes"**

**Principe:** Jugez solution par résultats finals, pas process.

**Applications Gedimat:**
- T1 (Urgence): "What matters = client satisfied + margin preserved?" → option tiering
- T13 (Knowledge): "What matters = Angélique pas burnout + system documented?" → assistant + cross-training
- T14 (Scale): "What matters = croissance future possible?" → focus relationship (scalable via multiple Angéliques régionales)

**Recommandation:** Clarify desired outcome FIRST, then pick option producing it.

---

### **Dewey (Expérimentalisme): "Testez D'Abord"**

**Principe:** Pas choix définitive sans evidence. Pilot, learn, iterate.

**Applications Gedimat:**
- T4 (IT Investment): "Try Excel 3 mois, validate ROI, THEN decide WMS"
- T9 (Assistant): "Automation 2 mois, if fails → hire assistant"
- T12 (Service levels): "Pilot tiering 50 clients, measure NPS, refine THEN rollout"

**Recommandation:** Chaque option Type B mérite test 4-8 weeks avant full commitment.

---

### **Popper (Falsificationnisme): "Choisissez Testable"**

**Principe:** Bonne hypothèse = testable (peut être prouvée fausse). Mauvaise = vague unfalsifiable.

**Applications Gedimat:**
- T11 (Positioning): "Relationship leader will achieve NPS 40+ in 12 months" = TESTABLE (mesurable)
  vs "Nous sommes bons" = UNFALSIFIABLE (vague)
- T2 (Bonus): "40% group bonus will increase collaboration" = testable (survey managers, behavior change)
  vs "Ça va marcher psychologiquement" = unfalsifiable

**Recommandation:** Pour chaque décision, définir hypothèse falsifiable + KPI mesure.

---

## 4. DÉCISIONS PASS 6 REQUIRED

### Décision Tree Format

**Décision 1: Tiers Service Explicites ou Tout Standard?**

```
├─ Option A: ÉCONOMIE/EXPRESS/CRITIQUE tiers (recommandé Pass 4)
│   ├─ Pro: Transparent, clients accepte délai si stable, marge stable
│   ├─ Con: Sales training, potential confusion, slower adoption
│   ├─ Test: 50 clients pilot, 4 weeks, measure NPS
│   └─ Go/No-Go: If NPS +3 above baseline → Deploy full
│
├─ Option B: All standard J+3-5 (lowest cost path)
│   ├─ Pro: Simple, operationally easy, coûts minimums
│   ├─ Con: Lose urgence clients (5-10%), margin war Point.P
│   ├─ Test: Monitor churn clients requesting urgent
│   └─ Go/No-Go: If churn <2% → viable, else abandon
│
└─ Decision Gate (PASS 6):
    ├─ Assign: Pass 6 Agent 4 (SI) coordinate logistics + sales pilots
    ├─ Timeline: 4-6 semaines test → decision PDG Décembre
    ├─ Success Criteria: ≥50% adoption tier, NPS +2, no churn increase
    └─ Fallback: If test fails → stick Option B (safe path)
```

---

**Décision 2: Embauche Assistant Angélique ou Automation Only?**

```
├─ Option A: Hire Assistant (€22k/an) immediately (janvier 2026)
│   ├─ Pro: Réduit Angélique burden 30-40%, documentation + continuity
│   ├─ Con: Budget RH impact -€22k, recruitment 2-3 weeks
│   ├─ Test: Job posting, first interview candidate → validate market
│   └─ Go/No-Go: If qualified candidate found <3 weeks → Deploy
│
├─ Option B: Automation only (Excel macros, €2-5k)
│   ├─ Pro: Aucun coûts RH, quick ROI
│   ├─ Con: Angélique still overloaded, bus factor = 1
│   ├─ Test: Automation 8 weeks, measure if Angélique time saved
│   └─ Go/No-Go: If time saved <5h/week → abandon, hire assistant
│
└─ Decision Gate (PASS 6):
    ├─ Assign: Pass 6 Agent 2 (Finance) + RH validation
    ├─ Timeline: 1 week job posting → assess candidate pool
    ├─ Success Criteria: Qualified candidate identified + Angélique confirms workload relief
    └─ Committed Path: Hire January 2026 + promote Angélique Feb (Supply Chain Manager)
```

---

**Décision 3: Proximité Dépôt Rule ou Case-by-Case Arbitrage?**

```
├─ Option A: Formalize Proximité Rule (40/30/30 scoring, binding decision)
│   ├─ Pro: Transparent, eliminates Angélique burden arbitrage, reduces conflict
│   ├─ Con: Lose flexibility edge cases (client political)
│   ├─ Test: Apply scoring 100 historical cases, validate vs actual decisions
│   └─ Go/No-Go: If 85%+ alignment with actual → implement binding
│
├─ Option B: Scoring advisory only (Angélique can override + document)
│   ├─ Pro: Preserve flexibility, case-by-case judgment
│   ├─ Con: Still ad-hoc, doesn't reduce conflicts, dépôts contest "why override?"
│   ├─ Test: Same 100 cases, track overrides + reasons
│   └─ Go/No-Go: If <10% overrides needed → Option A viable
│
└─ Decision Gate (PASS 6):
    ├─ Assign: Pass 6 Agent 1 (Logistique) + Angélique validation
    ├─ Timeline: 3 weeks audit 100 cases
    ├─ Success Criteria: 85%+ scoring alignment, Angélique comfort with rule
    └─ Implement: January 2026 (Excel macro + training)
```

---

**Décision 4: Contrat Fournisseurs SLA Strict or Flexible?**

```
├─ Option A: Formal SLA addendum (Émeris, Médiafret, others)
│   ├─ Pro: Clear expectations, pénalités enforceable, legal protection
│   ├─ Con: Risk fournisseur refuse, relationship tension
│   ├─ Action: Send addendum templates (Juridique prepare), negotiate 2 weeks
│   └─ Go/No-Go: If >80% fournisseurs sign → Deploy, else renegotiate terms
│
├─ Option B: Verbal agreements + escalade progressive
│   ├─ Pro: Relationship preserved, flexibility opérationnelle
│   ├─ Con: Pénalités non-enforceable, Gedimat eats costs
│   ├─ Test: Document next 50 retards, see penalties enforceable?
│   └─ Go/No-Go: If <30% recoup penalties → Option A necessary
│
└─ Decision Gate (PASS 6):
    ├─ Assign: Pass 6 Agent 7 (Juridique) lead, Angélique negotiate
    ├─ Timeline: 2 weeks SLA send + 4 weeks negotiation
    ├─ Success Criteria: >80% major suppliers signed, escalade clear, pénalités <€500/violation
    └─ Fallback: If fournisseurs refuse → stay verbal but document all incidents (audit trail)
```

---

**Décision 5: Positioning Gedimat (Cost vs Relationship vs Service)?**

```
├─ Option A: Cost Leader (Impossible, Leroy Merlin/Point.P win scale → Reject)
│
├─ Option B: Service Leader (J+0/J+1 Premium)
│   ├─ Pros: NPS 35-40, attractif clients urgence
│   ├─ Cons: Infrastructure €50-100k, risky operationally (1 failure = credibility lost)
│   ├─ Probability: 30% if volumes allow, 70% if not
│   └─ Go/No-Go: Only if verified 15%+ urgence volume + budget approved
│
├─ Option C: Relationship Leader (Recommended ★★★)
│   ├─ Pros: Aligned Forces (Angélique), defendable vs giants, marge sustainable
│   ├─ Cons: Slower NPS ramp (18-22 → 40 over 18 months)
│   ├─ Roadmap: 12-month, €20k investment, €60-80k annual ROI
│   └─ Go/No-Go: If PDG committed 18-month evolution → Deploy
│
└─ Decision Gate (PASS 6):
    ├─ Assign: Pass 6 Agent 8 (Marché) lead, PDG strategic validation
    ├─ Timeline: 2 weeks decision (strategic choice)
    ├─ Success Criteria: PDG alignment + communication cascaded all org
    ├─ If Option C chosen:
    │   ├─ Immediate: Launch NPS baseline (50 clients)
    │   ├─ Month 1: SMS automation + FRET21 adhesion
    │   ├─ Month 3: Milkrun + consolidation quick-wins
    │   ├─ Month 6: CRM Health Score live + communication proactive
    │   └─ Month 12: NPS 30-35 target + churn reduction evident
    └─ Contingency: If NPS stalls <25 month 6 → reassess positioning
```

---

## 5. ROADMAP ARBITRAGE (Timeline Décisions)

### Qui Décide Quand?

| Timeline | Décision | Blocking What? | Data Needed | Responsable PASS 6 |
|----------|----------|----------------|-------------|-------------------|
| **Semaine 1-2** | **1. Formaliser SLA Fournisseurs** (Émeris, Médiafret) | Alertes efficaces, pénalités enforceable | Contrats actuels validé juridique | Agent 7 (Juridique) |
| **Semaine 2-3** | **2. Décider Tiers Service** (Économie/Express/Critique) | Pricing, sales process, client communication | Urgence % réelle audit 2 mois | Agent 3 (Satisfaction) + Sales |
| **Semaine 3-4** | **3. Embauche Assistant DECISION** (start posting) | Angélique burden relief timeline | Candidate pool validation | Agent 2 (Finance) + RH |
| **Semaine 4** | **4. Proximité Rule APPROVAL** (scoring 40/30/30) | Arbitrage consistency, dépôt collaboration | Case audit 100 decisions | Agent 1 (Logistique) |
| **Mois 2** | **5. IT Phase 0 LAUNCH** (Excel macros, SMS, Zapier) | Alertes, NPS baseline, automation foundation | Technology decisions triaged | Agent 4 (SI) |
| **Mois 2-3** | **6. Positioning DECISION** (Cost vs Relationship vs Service) | Marketing, sales messaging, budgets | Strategic alignment PDG | Agent 8 (Marché) + PDG |
| **Mois 3** | **7. Promote Angélique** (Supply Chain Manager) + **Assistant Start** | Operations continuity, scalability path | Candidate onboarding ready | Agent 6 (RH) + Logistique |
| **Mois 3-4** | **8. Milkrun & Consolidation PILOT** (20-30 quick-win cases) | Coûts reduction validation, NPS tracking | Baseline coûts audit | Agent 1 (Logistique) |
| **Mois 4-6** | **9. Dépôt Dashboard & Collaboration MODEL** (bonus 40% group) | Transparency, incentive alignment | KPI definitions, calculation templates | Agent 6 (RH) + SI |
| **Mois 6-9** | **10. NPS ASSESSMENT + Positioning ADJUSTMENT** | Strategic course correction if NPS <25 | Quarterly NPS data, churn analysis | Agent 3 (Satisfaction) + PDG |

---

## 6. FILOSOFI ARBITRAGE - RÉSUMÉ SYNTHÉTIQUE

### Principes Guides (IF.guard Philosophy Applied)

**1. Empirisme > Intuition (Locke)**
- Toute décision doit être data-backed
- Audit 2 mois priorité (€2-3k cost, save €50k errors)

**2. Pragmatisme > Pureté (Peirce)**
- Si deux options, celle qui marche opérationnellement gagne
- Pilot test 4-8 weeks avant full commitment

**3. Harmonie > Efficacité Maximale (Confucius)**
- Balance efficiency + relationship (no win-at-all-costs)
- Bonus groupe 40% preserves dépôt harmony

**4. Équilibre > Extrêmes (Buddha)**
- Solution rarement 100/0, cherchez 60/40 ou 70/30
- Relationship leader = ni cheapest ni fastest, stable middle

**5. Cohérence > Patchwork (Quine)**
- Chaque décision doit renforcer système, pas créer tensions
- Positioning strategy doit être cohérent (pricing + service + messaging aligned)

**6. Outcomes > Process (James)**
- Judge solution par résultats finals
- Define desired outcome FIRST, pick option producing it

**7. Test > Certitude (Dewey)**
- Pas choix définitive sans evidence
- Pilot, learn, iterate before full rollout

**8. Falsifiable > Vague (Popper)**
- Hypothèse doit être testable (peut être prouvée fausse)
- KPI measurable défini AVANT décision

---

## CONCLUSION: ARBITRAGE READY FOR PASS 6

### Synthèse Exécutive

**14 Contradictions Identifiées:**
- **Type A (Résolues):** 3 domaines consensus → code immediately
- **Type B (Arbitrables):** 8 contradictions → 5 décisions majeures → pilot tests 4-6 weeks → go/no-go points
- **Type C (Bloquantes):** 3 contradictions → data collection 2-3 months → defer decision Q1 2027 or Q1 2026

**5 Décisions Majeures PASS 6:**
1. Tiers Service (ÉCONOMIE/EXPRESS/CRITIQUE) → 4 weeks pilot
2. Assistant Angélique (€22k) + Promotion Supply Chain Manager → immediate job posting
3. Proximité Rule (40/30/30 scoring) → binding decision → January 2026
4. SLA Fournisseurs (formelle) → 2 weeks negotiation → juridique lead
5. Positioning (Relationship Leader) → strategic PDG approval → 12-month evolution

**Investment Required (12 months):**
- Technology: €20k (NPS, SMS, CRM, Zapier, FRET21)
- RH: €22k assistant + €6k promotion = €28k
- Training/Formation: €14k (Angélique, dépôts, drivers, sales)
- **Total: €62k investment → €120-150k annual ROI potential** (churn reduction + marge preservation)

**Success Metrics (18-month):**
- NPS: 18-22 → 40-45 (+100% improvement)
- Churn: ~10% → 5% (€50k retention)
- Coûts logistique: €0.35-0.50/t/km → €0.20-0.25/t/km (-30%)
- Marge: 12% → 12.8% (+€20-30k)

---

**Document Rédigé:** 16 novembre 2025
**Agent:** Pass 5 Agent 3 (Synthesis)
**Status:** ✅ COMPLET - PRÊT PASS 6 ARBITRAGE
**Format:** 3 pages + tables, philosophiquement grounded, opérationnellement actionable
**Distribution:** Pass 6 Agents, PDG, Steering Committee
