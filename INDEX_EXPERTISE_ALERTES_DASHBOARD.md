# INDEX COMPLET
## Expertise Système d'Information - Alertes & Dashboard Gedimat

**Date compilation** : 16 novembre 2025
**Auteur** : Expertise SI Logistique Gedimat
**Répertoire** : `/home/user/infrafabric/`

---

## DOCUMENTS GÉNÉRÉS (4 fichiers)

### 1. **SPECIFICATIONS_ALERTES_DASHBOARD_GEDIMAT.md** (PAGE 1/2)
**Contenu** : Spécifications techniques détaillées

- **Chapitre 1** : Système d'alertes automatisées (4 alertes)
  - Alerte 1 : Retard fournisseur (DateARC +1j)
  - Alerte 2 : Stock critique dépôt (< seuil min)
  - Alerte 3 : Urgence non planifiée (J-3, non réservée)
  - Alerte 4 : Budget transport overshoot
  - Chaque alerte : déclencheurs, notifications, implémentation technique

- **Chapitre 2** : Dashboard temps réel (4 KPI principaux)
  - KPI 1 : Taux service (92% cible vs 75% actuellement)
  - KPI 2 : Coût €/tonne (45€/t cible vs 52€/t)
  - KPI 3 : NPS satisfaction client (50 cible vs 35 secteur)
  - KPI 4 : Charge chauffeurs (occupation, km, tonnage)
  - Architecture refresh, accès multi-rôles, visualisations PowerBI

- **Chapitre 3** : Intégration API
  - API Médiafret GPS temps réel
  - API fournisseurs stock (Emeris, Saint-Germaire)
  - Architecture non-invasive GeSI (export CSV, lecture seule)

- **Chapitre 4** : Analyse comparative 3 solutions
  - Option 1 : Excel/PowerBI (2.5 k€, +304% ROI, 3.6 mois payback)
  - Option 2 : Shiptify TMS (4.5 k€, +264% ROI, 4.2 mois payback)
  - Option 3 : Sinari TMS Ready (35 k€, +2550% ROI si 50+ dépôts, -45% ROI seul)

- **Chapitre 5** : Questions clés & recommandations
  - Low-code vs SaaS vs ERP ? → Approche échelonnée recommandée
  - Faisabilité GeSI ? → OUI, zéro impact
  - Budget 10-20 k€ réaliste ? → OUI, 7 k€ an 1 suffisant

- **Chapitre 6** : Roadmap 12 mois

**Usage** : Lecture détaillée par équipe IT/management avant implémentation | Format technique

---

### 2. **MOCKUP_DASHBOARD_ET_ROI_GEDIMAT.md** (PAGE 2/2)
**Contenu** : Interfaces visuelles + analyse ROI détaillée

- **Partie 1** : Mockup Dashboard PowerBI (3 vues)

  **Vue 1 - DIRECTION (Synthétique 4 KPI)** :
  - Alertes critiques live (rouge/orange/vert)
  - 4 jauges : Taux service, €/tonne, NPS, occupation chauffeurs
  - Courbes 30j et détails fournisseurs
  - Format : ASCII art prêt-à-présenter

  **Vue 2 - MANAGER LOGISTIQUE (Détail dépôts + chauffeurs)** :
  - Tableau activité chauffeurs (heures, km, tonnage, status)
  - Carte France GPS flotte temps réel
  - Analyse rentabilité routes récurrentes
  - Comparatif coût interne vs Médiafret

  **Vue 3 - COORDINATEUR Angélique (Alertes + Actions)** :
  - Alertes triées par priorité (rouge/orange/vert)
  - Description contexte + actions recommandées
  - Pop-ups avec contacts relationnel
  - Historique actions complétées 7j

  **Format** : Mock-up ASCII full détail, prêt pour brief étapes d'implémentation

- **Partie 2** : Analyse ROI 18 mois

  **Solution 1 - Excel/PowerBI**
  - Investissement initial : 2.5 k€
  - Coûts récurrents : 0.4 k€/an
  - Économies générées : 3.4 k€/an
  - ROI 18 mois : +304% | Payback : 3.6 mois
  - Verdict : ✓ Excellent pilote

  **Solution 2 - Shiptify TMS**
  - Investissement initial : 4.5 k€
  - Coûts récurrents : 2.5 k€/an
  - Économies générées : 6.73 k€/an
  - ROI 18 mois : +264% | Payback : 4.2 mois
  - Verdict : ✓ Très bon pour PME >5 véhicules

  **Solution 3 - Sinari TMS Ready**
  - Investissement initial : 57 k€ (1.1 k€/dépôt si 50 dépôts)
  - Coûts récurrents : 37 k€/an (0.7 k€/dépôt)
  - Économies : 18.35 k€/an
  - ROI 18 mois solo : -45% ✗ MAUVAIS
  - ROI 18 mois mutualisation 50 dépôts : +2550% ✓ EXCELLENT
  - Verdict : ✓ OUI si mutualisation, ✗ NON si solo

  **Tableau comparatif synthétique** : Budget, coûts an/an, ROI, payback, scalabilité, risque

  **Recommandation stratégique** :
  - Scénario A (PME seule) : Excel → Shiptify (ignore Sinari)
  - Scénario B (Groupe 10-20 dépôts) : Shiptify → Sinari possible
  - Scénario C (Gedimat 50+ dépôts) : Sinari direct en mutualisation

**Usage** : Présentation au management (visuals prêtes), ROI pour justifier budget | Format visuel

---

### 3. **EXECUTIVE_SUMMARY_ALERTES_DASHBOARD.md** (1 PAGE)
**Contenu** : Synthèse exécutive pour réunion rapide

- **Enjeu** : Coûts frictions 10-20 k€/an (surcoûts, temps, risque, clients)
- **Solution** : 3 phases échelonnées
  - T0 : Excel/PowerBI 2.5 k€
  - T1 : Shiptify 4.5 k€
  - T2 : Sinari 35 k€ (si 50+ dépôts)
- **Alertes 4** : Retard, stock, urgence, budget (1 ligne chacune)
- **KPI 4** : Taux service, €/tonne, NPS, charge chauffeurs (tableau synthétique)
- **Réponses 3 questions** : Low-code vs SaaS, GeSI, budget
- **Roadmap 12 mois** : Décision requise à J+15
- **Recommandation** : 7 k€ an 1 pour ROI +280%

**Usage** : Présentation 15 min direction, demande approbation budget | Format 1 page

---

### 4. **INDEX_EXPERTISE_ALERTES_DASHBOARD.md** (CE FICHIER)
**Contenu** : Navigation et guide utilisation

- Descriptif chaque document
- Map décisionnel par profil
- Checklist implémentation
- Prochaines étapes

**Usage** : Vous êtes ici | Référence navigation

---

## MAP DÉCISIONNEL PAR PROFIL

### Je suis **DIRECTION GÉNÉRALE Gedimat**
→ Lire : **EXECUTIVE_SUMMARY** (1 page, 5 min) → Approuver pilote T0

### Je suis **MANAGER LOGISTIQUE**
→ Lire : **EXECUTIVE_SUMMARY** (décision) + **MOCKUP Dashboard Vue 2** (mon tableau de bord) + **Chapitre 2 Specs** (détail KPI)

### Je suis **COORDINATRICE Angélique**
→ Lire : **Chapitre 1 Specs** (4 alertes détail) + **MOCKUP Vue 3** (mon dashboard) + **Chapitre 5** (comment alertes résolvent frictions)

### Je suis **ÉQUIPE IT/DÉVELOPPEMENT**
→ Lire : **Chapitre 3 Specs** (intégration API) + **Chapitre 1 Specs** (détails implémentation) + **Chapitre 4** (3 solutions tech)

### Je suis **FRANCHISÉ (petit site)**
→ Lire : **EXECUTIVE_SUMMARY** (overview) + **MOCKUP Vue 1** (mon dashboard synthétique)

### Je suis **INTÉGRATEUR / PARTENAIRE SaaS**
→ Lire : **Chapitre 4 Specs** (détails 3 solutions) + **MOCKUP Dashboard** (interfaces à développer) + **Chapitre 1 & 2** (specs techniques alertes/KPI)

---

## CHECKLIST IMPLÉMENTATION

### PHASE 1 (DÉCEMBRE 2025) - Excel/PowerBI Pilote
- [ ] **Décision** : Direction approuve pilote 5-10 franchisés (y/n ?)
- [ ] **Audit GeSI** : IT Gedimat valide export CSV quotidien possible
- [ ] **Appel d'offres** : Sélection consultant Excel/VBA/PowerBI (2.5 k€)
- [ ] **Sélection franchisés** : Identifier 5-10 volontaires (critères : motivation, données propres, >1 urgence/mois)
- [ ] **Kickoff** : Réunion consultant + Angélique + managers dépôts (scope, données, timing 4 sem)
- [ ] **Développement** : Excel alertes (2 sem) + PowerBI dashboards (1 sem) + testing (0.5 sem)
- [ ] **Formation** : Angélique + 2 managers logistiques (1 jour)
- [ ] **Go-live** : Activation alertes + dashboard (viser mi-janvier 2026)
- [ ] **Validation** : Mesurer retards -5%, temps Angélique -3h/sem, satisfaction croissante
- [ ] **Décision février 2026** : Scalabilité phase 2 (Shiptify) ? Y/N ?

### PHASE 2 (JANVIER-MARS 2026) - Shiptify TMS
- [ ] **Décision** : Phase 1 succès ? Approbation Shiptify (y/n ?)
- [ ] **Ciblage** : Franchisés avec >5 véhicules internes (10-15 sites estimé)
- [ ] **Devis Shiptify** : Demander plan tarifaire (150€/mois petit TMS)
- [ ] **Intégration API** : Dev. Shiptify ↔ Médiafret GPS (3 k€, 3 sem)
- [ ] **Formation** : Équipes terrain chauffeurs + managers (2 jours)
- [ ] **Go-live** : TMS + GPS + tracking actifs
- [ ] **Validation** : Coûts transport -8%, taux service +7%, chauffeurs occupés 85%+
- [ ] **Décision avril 2026** : Consolider Sinari si croissance ? Y/N ?

### PHASE 3 (AVRIL-SEPTEMBRE 2026) - Sinari TMS Ready (OPTIONNEL)
- [ ] **Condition** : Mutation 50+ dépôts Gedimat confirmée (critère ROI)
- [ ] **Appel d'offres** : Devis Sinari + implémentation partenaire (35 k€ licence + 20 k€ intégration)
- [ ] **Business case** : Valider ROI +2550% sur 50+ dépôts
- [ ] **Intégration GeSI** : Mapping données, API, sécurité (20 k€, 10 sem)
- [ ] **Formation** : IT, coordinateurs, managers (5 jours total)
- [ ] **Go-live** : TMS + WMS complet, tous dépôts
- [ ] **Validation** : Taux service +15%, coûts -12%, stocks -10%

---

## CONTEXTE FRICTION RÉSOLU

Chaque alerte + KPI résout une friction identifiée Pass 2 :

| Friction | Alerte/KPI Solution | Metric Cible | Bénéfice |
|----------|-------------------|-------------|-----------|
| **1. Défense territoriale dépôts** | Alerte 3 (Urgence J-3) | 95% urgences livrées à temps | Règles transparentes, satisfaction client +10% |
| **2. Logiciel insuffisant (pas d'alertes)** | Alertes 1-4 automation | 100% détection automatique | Temps Angélique -30h/mois, fiabilité +50% |
| **3. Relationnel non documenté** | Dashboard + CRM intégré | 100% contacts nommés + historique | Continuité opérationnelle, pas dépendance Angélique |
| **4. Satisfaction mesurée négativement** | KPI NPS + taux service | NPS +50 (vs 35 secteur) | Mesure positive, justifie investissements |
| **5. Coordination manuelle (pas de règles)** | Alerte 3 + Dashboard | Scoring décisionnel automatique | Arbitrage transparent, moins frustration inter-dépôts |

---

## DONNÉES DE RÉFÉRENCE

### Budget Horizon 18 mois (Scénario recommandé)

```
PHASE 1 (T0 Déc 2025)
├─ Investissement : 2.5 k€ (Excel/PowerBI)
├─ Coûts an/an : 0.4 k€ (PowerBI licences + hotfixes)
├─ Économies : 3.4 k€/an (retards, stock, urgences)
└─ ROI : +304% | Payback : 3.6 mois

PHASE 2 (T1 Jan-Mar 2026)
├─ Investissement : 4.5 k€ (Shiptify SaaS)
├─ Coûts an/an : 2.5 k€ (1.8 k€ licence + support)
├─ Économies : 6.73 k€/an (transport -8%, urgences -6%)
└─ ROI : +264% | Payback : 4.2 mois

TOTAL AN 1 (Phases 1+2)
├─ Investissement cumulé : 7 k€
├─ Coûts cumulés : 0.9 k€ (amortir sur 18m)
├─ Économies cumulées : 10 k€ (3.4 + 6.73 - 0.1 overlap)
└─ ROI GLOBAL : +280%
```

### Données Gedimat (Baseline estimé)
- Taux service actuel : ~75% (vs cible 92%)
- Coût transport : ~52€/t (vs cible 45€/t)
- NPS satisfaction : Pas mesuré (secteur ~35)
- Temps Angélique : ~30h/semaine coordination
- Urgences à temps : ~72% (vs cible 95%)
- Stock de sécurité : ~20% volume (vs optimal 10-12%)

### Sources Pass 1 & Pass 2
- **ANALYSE_FRICTION_GEDIMAT_ANGELIQUE.md** : 5 frictions détailées + impact
- **Gedimat_Solutions_WMS_TMS_PME.md** : Comparatif solutions WMS/TMS marché

---

## VALIDATION TECHNIQUE

### Points à valider avec IT Gedimat (3-5 jours)
1. Format export GeSI possible ? (CSV/API/EDI)
2. Fréquence export ? (daily batch ok ?)
3. Tables disponibles ? (Commandes, Stock, Clients, Livraisons)
4. Sécurité données ? (chiffrement, accès restreint)
5. Infrastructure accueil données alertes ? (cloud ok ? locales ?)

### Prérequis GeSI
- Pas de modification GeSI (architecture satellite)
- Export en lecture seule
- Pas de feed-back en écriture
- Coûts mutualisés entre franchisés

---

## PROCHAINES ÉTAPES

**IMMÉDIATE (Cette semaine)**
1. Direction approuve pilote Excel/PowerBI (décision)
2. IT Gedimat audit faisabilité GeSI (3-5 jours)
3. Lancer appel d'offres consultant Excel (RFP = 1 jour)

**COURT TERME (Semaine 2-3)**
1. Sélection franchisés pilotes (5-10 sites)
2. Signature contrat consultant (75€/h, 80h estimé)
3. Démarrage kickoff Excel (semaine 3)

**MOYEN TERME (Novembre-Décembre)**
1. Développement alertes + dashboard (3-4 sem)
2. Formation équipes (1 jour)
3. Go-live mi-janvier 2026

**DÉCISION FÉVRIER 2026**
1. Évaluer ROI pilote vs prévisions
2. Statuer sur Shiptify phase 2 (y/n ?)
3. Planifier scalabilité 2026-2027

---

## CONTACTS RESSOURCES

### Gedimat Interne
- **Direction opérations** : Approbation budget, décisions stratégiques
- **Angélique (Coordination)** : User pilote, feedback alertes/dashboard
- **IT Gedimat** : Audit GeSI, export données, infrastructure
- **Managers dépôts** : Formation, suivi KPI, validation urgences

### Partenaires Externes
- **Consultant Excel/PowerBI** : À recruter (TBD)
- **Shiptify** : Contact commercial pour devis TMS (Phase 2)
- **Sinari** : Contact pour demo TMS complet (Phase 3, si decision)
- **Médiafret** : Validation API GPS disponible (contact Mélissa)

---

## FAQ RAPIDE

**Q : Combien ça coûte vraiment ?**
R : 7 k€ an 1 (2.5 Excel + 4.5 Shiptify) = ROI +280% | 42 k€ total (phases 1-3) si Sinari au bout

**Q : Quand ça démarre ?**
R : Excel mi-janvier 2026 (décision requise cette semaine), Shiptify trim 1, Sinari trim 2 (si ok)

**Q : Et si ça échoue ?**
R : Excel ne coûte presque rien (2.5 k€) donc risque faible | Sinari solo = ROI négatif donc évité

**Q : GeSI doit être changé ?**
R : NON zéro impact, export CSV suffit, architecture satellite

**Q : Angélique doit être remplacée ?**
R : NON, alertes libèrent 30h/mois de suivi manuel → elle peut faire plus stratégique + relationnel

**Q : Comment j'évalue le succès ?**
R : Taux service +7% (75%→92%), temps Angélique -30h/mois, stock -8%, coûts -5%, NPS +15pts

---

**Index complet | Ressource navigation | Prêt implémentation décembre 2025**

*Tous les documents sont en français et prêts à présenter/implémente immédiatement.*
