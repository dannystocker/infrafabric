# PASS 2 - AGENT 2: Analyse Coûts Actuels
## Synthèse Exécutive & Récapitulatif Livrables

**Date:** 16 novembre 2025
**Statut:** ✅ COMPLET ET PRÊT VALIDATION
**Audience:** PDG Gedimat, Direction Franchise, Angélique (Coordinatrice)

---

## SYNTHÈSE EXÉCUTIVE (1 PAGE)

### Problème Gedimat

Gedimat opère un système de transport 3 modes simultanés avec **arbitrage inefficace** entre dépôts:
- **Chauffeurs internes** (<10t): €45-70k/an mais sous-optimisés
- **Affrètement Médiafret** (>10t): €80-120k/an avec défense territoriale dépôts
- **Navettes inter-dépôts** (2×/semaine): €9-15k/an mais inflexibles
- **Coûts cachés**: €14-31k/an (coordination Angélique, pertes commandes, surstock)

**Budget transport total estimé: €152-249k/an** avec écart-type ±40% (données manquantes)

### Opportunités Quantifiées

| Opportunité | Gains Estimés | Effort | Timeline |
|---|---|---|---|
| Alertes retards + Scoring dépôt | €8-16k | Faible (2-3 sem) | IMMÉDIAT |
| Consolidation dynamique | €8-20k | Faible | Semaine 4 |
| Réoptimisation navettes | €2-5k | Faible | Mois 3 |
| Réduction coûts cachés (Angélique) | €3-9k | Moyen | Mois 2 |
| **TOTAL QUICK WINS (3 mois)** | **€21-50k** | **Très faible** | **Semaine 1-12** |

**ROI: 10:1 à 25:1** (excellent pour Phase 1)

### Recommandation Immédiate

**GO IMMÉDIATEMENT sur Phase 1** (Quick Wins):
1. Semaine 1-2: Alertes retards + Formation Angélique scoring
2. Semaine 3-4: Excel scoring dépôt + Tests
3. Semaine 4-12: Consolidation manuelle + Dashboard validation

**Parallèlement: Collecte data validation** (factures Médiafret, paie chauffeurs, réclamations clients)

**Mois 3: Bilan + Décision Phase 2** basé sur ROI réel (si >15k validé, approuver Phase 2 intégration OR-Tools)

---

## LIVRABLES DÉTAILLÉS

### Document 1: ANALYSE COÛTS ACTUELS (11 sections, 3-4 pages)
**Fichier:** `/PASS2_AGENT2_ANALYSE_COUTS_ACTUELS.md`

**Contenu:**
- Section 1-3: Décomposition détaillée coûts (Chauffeurs, Affrètement, Navettes)
- Section 4: Coûts cachés non comptabilisés (Coordination, Incidents, Surstock)
- Section 5: Tableau comparatif 3 modes transport
- Section 6: Décomposition annuelle tous coûts
- Section 7-10: Opportunités + Cas réels (Émeris) + Limites analyse
- Section 11: Conclusions & Data gaps requis

**Qualité:**
- ✅ Tous coûts marqués "estimé" ou "à valider"
- ✅ Benchmarks industrie construction matériaux cités
- ✅ Données manquantes explicitement listées
- ✅ Écarts de confiance quantifiés (±25-40%)

### Document 2: TABLEAUX COMPARATIFS DÉTAILLÉS (7 matrices)
**Fichier:** `/PASS2_AGENT2_TABLEAUX_COMPARISON.md`

**Contenu:**
- **Table 1:** Comparaison synthétique 3 modes (12 métriques)
- **Table 2:** Arbre de décision mode optimal par scenario
- **Table 3:** 3 cas réels détaillés (Petit fournisseur, Émeris, Consolidation)
- **Table 4:** Budget transport annuel détaillé décomposition
- **Table 5:** Matrice opportunités impact × effort (3 zones)
- **Table 6:** Checklists validation data
- **Table 7:** Feuille de route exécution

**Utilité:**
- ✅ Matrices directement exploitables décisions
- ✅ Scenarios réels avec chiffres spécifiques
- ✅ Visualisations ASCII comparables
- ✅ Priorisation claire quick wins vs long term

### Document 3: DATA GAPS & CHECKLIST VALIDATION (7 sections)
**Fichier:** `/PASS2_AGENT2_DATA_GAPS_CHECKLIST.md`

**Contenu:**
- Section 1: Résumé data manquantes par criticité
- Sections 2-4: Détail data requises (Médiafret, Chauffeurs, Incidents, Fournisseurs)
- Section 5-6: Data secondaires & planning collecte
- Section 7: Impact chaque découverte sur recommandations

**Utilité:**
- ✅ Template Excel collecte fournis
- ✅ Responsables nommés par data
- ✅ Timeline collecte définie (semaine 1-4)
- ✅ Formule calcul coûts finaux donnée

---

## METRICS CLÉS DU DIAGNOSTIC

### Budget Transport Annuel (Ordre de Grandeur)

```
Chauffeurs internes:              €45-75k (±€15k) - Confiance: MOYEN
Affrètement Médiafret:            €80-120k (±€30k) - Confiance: FAIBLE ⚠️
Navettes inter-dépôts:            €9-15k (±€3k) - Confiance: MOYEN
Coûts cachés (Coord., incidents): €14-31k (±€10k) - Confiance: FAIBLE ⚠️
───────────────────────────────────────────────────
TOTAL:                            €152-249k (±€40k) - Confiance: MOYEN
```

**Plus probable (médian): €190-200k/an**

### Coûts Unitaires Par Mode (€/Tonne)

| Mode | Coût | Remarques |
|---|---|---|
| Chauffeur interne | €8-12 | Salarial fixe dominant |
| Affrètement Médiafret | €15-25 | +40-70% premium vs interne |
| Navette inter-dépôts | €15-18 | Coûts marginaux, salarial fixe |

### Premium Affrètement vs Interne (Seuil Critique 10t)

**Cas 13 tonnes:**
- Option 1 (2 chauffeurs internes): €50-60
- Option 2 (1 affrètement >10t): €150-180
- **Premium: €90-130 (40-70% plus cher)**

→ C'est la raison du conflit inter-dépôts (défense 10t seuil)

---

## OPPORTUNITÉS IDENTIFIÉES & PRIORITÉS

### ZONE 1 - QUICK WINS (0-3 Mois, €0-2k Investissement)

**1.1 Alertes Retards Fournisseurs** (Semaine 1)
- Effort: 2 jours dev Excel
- Gain: €3-5k/an (libération temps Angélique)
- Risk: Très bas

**1.2 Scoring Dépôt Multicritère** (Semaine 2-3)
- Effort: 1-2 jours dev + tests
- Gain: €4-12k/an (5-10% affrètement optimisé)
- Risk: Bas

**1.3 Consolidation Dynamique Manuelle** (Semaine 4)
- Effort: Processus + Excel (0€)
- Gain: €8-20k/an (si 50-100 consolidations/an)
- Risk: Moyen (client accepte délai +1-3h?)

**Sous-total Zone 1: €15-37k potentiel sur 3 mois, effort faible**

### ZONE 2 - MEDIUM TERM (3-9 Mois, €5-12k Investissement)

**2.1 Dashboard + Satisfaction Client**
- Gain: €0 direct, révèle opportunités supplémentaires
- Timeline: Mois 2

**2.2 Audit Coûts Cachés & Timesheet Angélique**
- Gain: €3-9k (libération temps via automation)
- Timeline: Mois 1-2

**2.3 Réoptimisation Navettes (Fréquence Flexible)**
- Gain: €2-5k (adaptation demand réelle)
- Timeline: Mois 3

**2.4 Contrats Fournisseurs SLA**
- Gain: €2-5k (moins incidents, pénalités appliquées)
- Timeline: Mois 4-6

**Sous-total Zone 2: €7-28k additionnel si phase 1 successful**

### ZONE 3 - LONG TERM (9-24 Mois, €30-50k Investissement)

**3.1 Système Optimisation Intégré (OR-Tools/Jsprit)**
- Gain: €10-25k/an (cumul zones 1+2 + meilleur routing)
- Timeline: Mois 9-12
- **Condition gating: SEULEMENT si Zone 1-2 ROI >10k validé**

**3.2 Partenariats Pooling Transport**
- Gain: €15-25k/an (consolidation non-concurrents)
- Timeline: Mois 6-12
- Risk: Élevé (partenaire alignment)

---

## DONNÉES CRITIQUES MANQUANTES

### Top 5 Data Gaps (Impact >20% Analyse)

1. **Factures Médiafret 6 mois** (Criticité: URGENT)
   - Impact: Affine €80-120k affrètement ±€30k → ±€5k
   - Source: Comptabilité
   - Timeline: Cette semaine

2. **Données Paie Chauffeurs** (Criticité: URGENT)
   - Impact: Affine €45-75k internes ±€15k → ±€3k
   - Source: RH
   - Timeline: Cette semaine

3. **Audit CRM Réclamations** (Criticité: URGENT)
   - Impact: Valide coûts incidents €1.6-4.8k vs réalité
   - Source: Manager commercial
   - Timeline: Semaine 2

4. **Kilométrage Chauffeurs Réel** (Criticité: IMPORTANT)
   - Impact: Valide €/km et utilisation réelle
   - Source: Tachygraphe ou GPS
   - Timeline: Semaine 2

5. **Localisation Fournisseurs** (Criticité: SECONDAIRE)
   - Impact: Calcul distances réelles vs hypothèse
   - Source: Achats + Google Maps
   - Timeline: Semaine 1

**Collecte Planning: Semaine 1-4, recalcul Mois 2**

---

## RECOMMANDATIONS POUR PDG

### DÉCISION 1: Valider Phase 1 Quick Wins?

**Recommandation: OUI** (faible risque, ROI >10:1)

**Budget requis:** €1-2k consultant (Excel dev)
**Timeline:** 2-3 semaines première vague
**Retour attendu:** €8-16k économies mois 3

**Conditions acceptabilité:**
- ✅ Angélique disponible pour formation (4h)
- ✅ Budget 1-2k consultant approuvé
- ✅ Sponsor IT désigné pour alertes/scoring dev
- ✅ Accepter délai 2-3 semaines avant résultats visibles

### DÉCISION 2: Parallèle - Collecte Data Validation?

**Recommandation: OUI (obligatoire pour Phase 2)**

**Effort:** 2-4 semaines collecte
**Coût:** 0€ (IT interne)
**Bénéfice:** Affine coûts ±40% → ±10% pour décisions ultérieures

**Sponsor requis:** Direction générale ou Dir. Finance

### DÉCISION 3: Quand Décider Phase 2?

**Recommandation: Mois 3 après validation Phase 1 ROI réel**

**Critères go Phase 2:**
- ✅ Phase 1 économies >10k validées
- ✅ Data collecte 80%+ complète
- ✅ Budget Phase 2 (€20-50k) approuvé
- ✅ Équipe IT disponible 8-12 semaines

**Si criteria non respectés:** Continuer optimisations Zone 2 (navettes, SLA, audit) avant Phase 3

---

## RÉSUMÉ CONFIANCE DONNÉES

| Composante | Confiance | Écart | Priorité Validation |
|---|---|---|---|
| Chauffeurs internes | MOYEN | ±€15k | URGENT (paie) |
| Affrètement Médiafret | FAIBLE | ±€30k | URGENT (factures) |
| Navettes inter-dépôts | MOYEN | ±€3k | Important |
| Coûts cachés | FAIBLE | ±€10k | Important (CRM audit) |
| **TOTAL** | **MOYEN** | **±€40k** | **Semaine 1-4** |

---

## FICHIERS LIVRÉS

```
/PASS2_AGENT2_ANALYSE_COUTS_ACTUELS.md
  └─ 11 sections, ~4 pages, analyse detaillée tous coûts

/PASS2_AGENT2_TABLEAUX_COMPARISON.md
  └─ 7 tables comparatives, matrices décision, cas réels

/PASS2_AGENT2_DATA_GAPS_CHECKLIST.md
  └─ Data requirements, templates collecte, checklists

/PASS2_AGENT2_DELIVERABLES_SUMMARY.md (ce fichier)
  └─ Synthèse exécutive, roadmap, recommandations
```

---

## PROCHAINES ÉTAPES (ACTIONS IMMÉDIATE)

### Pour PDG
1. ✅ **Lire synthèse** (cette doc, 10 min)
2. ✅ **Approuver Phase 1** (1-2k€ consultant)
3. ✅ **Nommer sponsor** (Dir. Finance ou Dir. Logistique)
4. ✅ **Demander data** (factures Médiafret, paie, CRM)

### Pour Angélique
1. ✅ **Réunion formation** (scoring multicritère, 2h semaine prochaine)
2. ✅ **Compiler fournisseurs** (top 15 avec distances)
3. ✅ **Estimer temps** (auto-pointage 1 semaine)
4. ✅ **Documenter incidents** (dernier mois exemples)

### Pour IT/Consultant
1. ✅ **Planifier Phase 1 dev** (alertes Excel, scoring)
2. ✅ **Estimer timeline** (2-3 semaines réaliste?)
3. ✅ **Préparer templates** (Excel, Google Sheets)
4. ✅ **Planifier Phase 2 IF** (OR-Tools timeline)

### Réunion Lancement
**Quand:** Semaine du 24 novembre (avant fin novembre)
**Qui:** PDG, Angélique, Dir. IT, Sponsor
**Durée:** 1h
**Agenda:**
  1. Approuver Phase 1 quick wins
  2. Assigner responsables collecte data
  3. Fixer deadlines: factures Médiafret, paie, CRM
  4. Planifier première review: mois 1

---

**Fin Synthèse Pass 2 - Analyse Coûts Actuels**

**Status:** ✅ COMPLET
**Prêt pour:** Validation données + Phase 1 exécution
**Date cible Phase 1 wins:** Fin décembre 2025 (estimé €8-16k)

---

*Document préparé pour PDG Gedimat*
*Confiance globale analyse: MOYEN (±30-40%) - Affinage garanti après collecte data*
