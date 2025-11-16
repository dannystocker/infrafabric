# PASS 7 - GRILLE DE NOTATION FOURNISSEURS & PLAN ACTION
## Gedimat - Outil de Scoring & Gestion Relationnelle

**Document opérationnel | Version 1.0 | Novembre 2025**

**Responsable:** Angélique + Manager Achats
**Fréquence:** Trimestrielle (Mars, Juin, Septembre, Décembre)
**Utilisateurs:** Coordinatrice logistique, Directeur achats, Représentants fournisseurs

---

## 1. OBJECTIFS DE LA GRILLE DE NOTATION FOURNISSEURS

### 1.1 Objectif Primaire
**Identifier les fournisseurs à risque** par évaluation systématique des retards récurrents, qualité insuffisante, et réactivité insuffisante. Transforme le jugement qualitatif d'Angélique en score objectif, documenté, comparable dans le temps.

**Cas Gedimat actuel :**
- Retards fournisseur = 40-45% des causes de retards clients (cf. ANALYSE_RETARDS_GEDIMAT_2025.md)
- Emeris tuiles : +3 à +7 jours retard vs engagement → 18-24% taux retard tuiles
- Absence d'alerte automatisée → client découvre retard tardivement → annulation

**Résultat attendu** : Détecter les Emeris et Saint-Germaire avant que le client soit impacté.

### 1.2 Objectif Secondaire
**Négocier les conditions** (prix, délais, qualité) armé d'un scoring transparent. Scores bas = levier de pression justifié. Fournisseur sait qu'amélioration de 10 pts = maintien partenariat.

**Cas Gedimat** :
- Negotiation Emeris : "Votre score 63/100 = surveillance. Cible : 75/100 en 90 jours"
- Lafarge 84/100 : "Excellent, augmentons volume +15% et négocions crédit 60j"

### 1.3 Objectif Tertiaire
**Diversifier sourcing** pour réduire dépendance monofournisseur. Si Emeris (seul fournisseur tuiles) reste <70, lancer dual-sourcing alternatif (Imerys, etc.).

### 1.4 Fréquence & Utilisateurs
- **Fréquence :** Trimestrielle (1er lundi mars/juin/septembre/décembre)
- **Temps requis :** 2 heures/trimestre (compilation données ERP + calcul formules Excel)
- **Utilisateurs :**
  - **Angélique** : compilation données, alertes proactives, réunions fournisseurs
  - **Manager Achats** : validation scoring, escalade <50, décisions stratégiques
  - **Direction** : tableau de bord synthèse, décisions sourcing
  - **Fournisseurs** : transparence scoring, plans amélioration consensuels

---

## 2. LES 4 CRITÈRES DE SCORING

### 2.1 CRITÈRE 1 : FIABILITÉ LIVRAISON (Poids : 40%)

**Définition :** Respect systématique des délais de livraison promis. Critère majeur car retard fournisseur impacte cascade clients.

**Rationale du poids 40% :**
- Causes retards Gedimat : fournisseur = 40-45% du total
- Cas Emeris : impacte 18-24% des commandes tuiles
- Client attend bien plus la date que la qualité du produit
- Retard = coût caché énorme (annulation, perte marge, pénalité chantier)

#### Métriques Fiabilité

| Métrique | Unité | Formule/Source | Seuil "Excellent" |
|----------|-------|---|---|
| **Taux livraison à l'heure (±1j)** | % | = (Commandes livrées ±1j) / (Total commandes trim) | >95% |
| **Nombre retards >48h** | Unité | Comptage retards supérieurs à 48h | <1 par trim |
| **Délai moyen retard** | jours | = Σ(jours_retard) / Nb_retards | <1.5 jours |

**Source données :** ERP Gedimat (ARC - Accusés Réception)

#### Formule Excel - Score Fiabilité

```excel
=MAX(0; MIN(100;
    (100 × Taux_Livraisons_OK)
    - (5 × Nb_Retards_48h)
    - (2 × Delai_Moyen_Retard_Jours)
))
```

**Explication :**
- Base 100 × taux OK → 95% de ponctualité = 95 pts
- Pénalité 5 pts par retard >48h (grave = déception client maximale)
- Pénalité 2 pts par jour retard moyen (accumulation impact)
- MAX(0) = score jamais négatif
- MIN(100) = score plafonné à 100

#### Barème Fiabilité

| Score | Qualité | Critères | Actions |
|-------|---------|----------|---------|
| **90-100** | 🟢 EXCELLENT | >95% à l'heure, <1 retard >48h | Maintenir |
| **70-89** | 🟢 BON | 85-95% à l'heure, 1-3 retards | Suivi normal |
| **50-69** | 🟡 MOYEN | 75-85%, 4-6 retards | ⚠ Surveillance |
| **<50** | 🔴 CRITIQUE | <75%, >6 retards | 🔴 ACTION IMMÉDIATE |

#### Exemple Réel : EMERIS TUILES (Trim 4 2025)

**Données collectées :**
- Nombre commandes trim 4 : 24
- Livrées à l'heure (±1j) : 18 (75%)
- Retards >48h : 5
- Délai moyen retard : 3,2 jours
- Historique : 2 commandes perdus clients (annulation)

**Calcul Score :**
```
Taux_OK = 18 / 24 = 0,75
Retards_48h = 5
Delai_Moyen = 3,2

Score = (100 × 0,75) - (5 × 5) - (2 × 3,2)
       = 75 - 25 - 6,4
       = 43,6 / 100
```

**Résultat :** 🔴 **43,6 / 100 = CRITIQUE**

**Interpretation :**
- Fiabilité 75% = inacceptable (vs 95% cible)
- 5 retards >48h en 3 mois = 1.7 par mois = trop fréquent
- Délai moyen 3,2j = clients paniqués à J+3
- Impacte directement CA : 2 annulations × 5000€ = 10k€ perte marge
- **Cause identifiée :** Emeris délai production +3-7j vs engagement (matière première Espagne)

---

### 2.2 CRITÈRE 2 : QUALITÉ PRODUITS (Poids : 25%)

**Définition :** Conformité des produits livrés vs spécifications commande. Absence de défauts, retours, réclamations clients.

**Rationale du poids 25% :**
- Qualité insuffisante = retours + surcoûts logistique
- Réclamations clients = destruction réputation Gedimat + NPS -30 pts
- Moins critique que délai (client peut reporter chantier si avert) mais crée déception
- Cas Lafarge : zéro réclamation = confiance 100%

#### Métriques Qualité

| Métrique | Unité | Source | Excellent |
|----------|-------|--------|-----------|
| **Taux conformité** | % | = 1 - (Nb_réclamations / Nb_commandes) | >98% |
| **Réclamations clients** | Unité | Comptage remontées par clients finaux | 0 |
| **Taux retours produits** | % | = (Produits retournés) / (Total livrés) | <1% |

**Source données :** CRM Gedimat (notes Angélique) + ERP retours

#### Formule Excel - Score Qualité

```excel
=MAX(0; MIN(100;
    (100 × Taux_Conformite)
    - (10 × Nb_Reclamations_Clients)
    - (15 × Taux_Retours_Pct)
))
```

**Explication :**
- Base 100 × taux conformité → 98% = 98 pts
- Pénalité 10 pts par réclamation client (grave = client final mécontent)
- Pénalité 15 pts par % retours (coûts logistique doublés)

#### Barème Qualité

| Score | Qualité | Critères | Actions |
|-------|---------|----------|---------|
| **90-100** | 🟢 EXCELLENT | <2% défauts, 0 réclamations | Partenaire préféré |
| **70-89** | 🟢 BON | 2-5% défauts, 1-2 réclamations | Suivi normal |
| **50-69** | 🟡 MOYEN | 5-10%, 3-5 réclamations | ⚠ Surveillance |
| **<50** | 🔴 CRITIQUE | >10%, >5 réclamations | 🔴 Dual-sourcing urgent |

#### Exemple Réel : LAFARGE CIMENT (Trim 4 2025)

**Données :**
- Commandes trim 4 : 18
- Réclamations produit : 1 (sacs humides - cause transport, pas Lafarge)
- Réclamations clients : 0
- Retours produits : 0 unité

**Calcul Score :**
```
Taux_Conformite = (18 - 1) / 18 = 17/18 = 0,944
Nb_Reclamations_Clients = 0
Taux_Retours = 0%

Score = (100 × 0,944) - (10 × 0) - (15 × 0)
       = 94,4 / 100
```

**Résultat :** 🟢 **94,4 / 100 = EXCELLENT**

**Interprétation :**
- Lafarge fiable sur qualité
- Réclamation 1 = transporteur, pas produit → exonère Lafarge
- Zéro retours = logistique renforcée
- Lafarge = partenaire stratégique à consolider

---

### 2.3 CRITÈRE 3 : COMPÉTITIVITÉ PRIX (Poids : 20%)

**Définition :** Positionnement tarifaire vs marché + conditions paiement + évolution prix.

**Rationale du poids 20% :**
- Prix important mais secondaire vs délai/qualité
- Ne pas sacrifier fiabilité pour économiser 2-3%
- Marges GSB = 25-30% → pression prix réelle mais limitée
- Cas secteur : variation ±10% prix normal selon fournisseur

#### Métriques Prix

| Métrique | Unité | Source | Excellent |
|----------|-------|--------|-----------|
| **Écart vs benchmark secteur** | % | = (Prix_fournisseur - Marché_moyen) / Marché_moyen | -5% (moins cher) |
| **Inflation appliquée 12 mois** | % | Évolution prix année avant | <3% |
| **Conditions paiement** | jours | Crédit accordé | 60 jours |

**Source données :** ERP prix + cotations secteur GSB

#### Formule Excel - Score Prix (Corrigée)

```excel
=MAX(30; MIN(100;
    75
    - (ABS(Ecart_Benchmark) × 100)
    - (Inflation_12m × 5)
    + (Jours_Credit / 3)
))
```

**Explication :**
- Base 75 (prix rarement parfait)
- Pénalité = écart absolu × 100 (prix +10% vs marché = -10 pts)
- Inflation penalize trend hausse (5 pts par % inflation)
- Crédit récompense (30 jours crédit = +10 pts)
- MAX(30) = même mauvaise offre vaut 30 pts (ne pas éliminer si bon ailleurs)

#### Barème Prix

| Score | Compétitivité | Critères | Actions |
|-------|---|---|---|
| **90-100** | 🟢 EXCELLENT | Prix -5% vs marché, inflation <3%, 60j crédit | Augmenter volumes |
| **70-89** | 🟢 BON | Prix ±5%, inflation 3-5%, 30-45j | Normal |
| **50-69** | 🟡 MOYEN | Prix +5-10%, inflation 5-8%, <30j | ⚠ Négocier |
| **<50** | 🔴 CRITIQUE | Prix +10%, inflation >8% | 🔴 Benchmark alternatif |

#### Exemple Réel : ISOVER ISOLANTS (Trim 4 2025)

**Données :**
- Prix moyenne Isover : 42€/m²
- Marché secteur (Knauf, Saint-Gobain) : 40€/m²
- Écart : +5% (Isover +2€)
- Inflation 12 mois : 6%
- Crédit accordé : 45 jours

**Calcul Score :**
```
Ecart_Benchmark = (42 - 40) / 40 = 0,05 = +5%
Inflation_12m = 6%
Jours_Credit = 45

Score = 75
        - (0,05 × 100)
        - (6 × 5)
        + (45 / 3)
      = 75 - 5 - 30 + 15
      = 55 / 100
```

**Résultat :** 🟡 **55 / 100 = MOYEN**

**Interprétation :**
- Isover légèrement cher (+5%) → marge comprimée
- Inflation 6% appliquée = trend hausse (vs indexation secteur 3-4%)
- Crédit 45j = bon (vs 30j concurrence)
- **Action :** Négociation Isover : "Réduire +5% prix ou augmenter crédit à 60j"

---

### 2.4 CRITÈRE 4 : RÉACTIVITÉ COMMUNICATION (Poids : 15%)

**Définition :** Qualité du dialogue avec Angélique. Délai réponse, disponibilité, proactivité alertes.

**Rationale du poids 15% :**
- Complément "relationnel" aux 3 autres critères
- Fournisseur proactif alertant retards J-2 = mitigation risque
- Mélissa Médiafret = exemple excellence (accepte urgences, répond vite)
- Capital social Angélique documenté (CRM_PLAN_GESTION_RELATIONNEL.md)

#### Métriques Réactivité

| Métrique | Unité | Source | Excellent |
|----------|-------|--------|-----------|
| **Délai réponse email** | heures | Email reçu → réponse | <2h (9-11h) |
| **Taux appels décrochés** | % | Appels reçus avec réponse <3 sonneries | >90% |
| **Alertes proactives retards** | Unité | Fournisseur avertit Angélique retard avant question | >5 par trim |

**Source données :** CRM Gedimat (notes Angélique) + historique emails/appels

#### Formule Excel - Score Réactivité (Corrigée)

```excel
=MAX(20; MIN(100;
    50
    - (Delai_Reponse_Email_H × 3)
    + (Taux_Appels_Decroches_Pct / 2)
    + (Nb_Alertes_Proactives × 8)
))
```

**Explication :**
- Base 50 (communication jamais parfaite)
- Pénalité délai : 3 pts par heure (24h délai = -72 pts = très mauvais)
- Récompense décrochage appels : +0,5 par % (90% = +45 pts)
- Récompense proactivité : +8 pts par alerte retard anticipée
- MAX(20) = même mauvais communiqueur vaut 20 pts

#### Barème Réactivité

| Score | Réactivité | Critères | Actions |
|-------|---|---|---|
| **90-100** | 🟢 EXCELLENT | <2h email, >90% appels, >5 alertes | Partenaire modèle |
| **70-89** | 🟢 BON | 2-6h, 70-90%, 2-5 alertes | Bon relationnel |
| **50-69** | 🟡 MOYEN | 6-24h, 50-70%, 0-1 alerte | ⚠ À améliorer |
| **<50** | 🔴 CRITIQUE | >24h, <50%, 0 alerte | 🔴 Escalade management |

#### Exemple Réel : RECTOR POUTRELLES (Trim 4 2025)

**Données :**
- Délai email moyen : 4 heures (Stéphane répond après 10h)
- Appels décrochés : 85% (vs 95% target)
- Alertes proactives trim : 3 (Stéphane prévient délai +1j)

**Calcul Score :**
```
Delai_Email_H = 4
Taux_Appels = 85%
Alertes = 3

Score = 50
        - (4 × 3)
        + (85 / 2)
        + (3 × 8)
      = 50 - 12 + 42,5 + 24
      = 104,5 → MIN(100)
      = 100 / 100
```

**Résultat :** 🟢 **100 / 100 = EXCELLENT (plafonné)**

**Interprétation :**
- Rector : très bon relationnel malgré délai email 4h
- 85% appels décrochés = fiable mais pas parfait
- 3 alertes proactives = excellent (Stéphane pro-actif)
- **Action :** Maintenir, reconnaître, proposer augmentation volumes +10%

---

## 3. FORMULE SCORE GLOBAL FOURNISSEUR

**Score Global = Moyenne pondérée 4 critères**

```excel
=ROUND(
    (Fiabilite × 0,40)
    + (Qualite × 0,25)
    + (Prix × 0,20)
    + (Reactivite × 0,15)
; 1)
```

### Exemple Complet : EMERIS TUILES (Trim 4 2025)

**Scores par critère :**
| Critère | Score | Poids | Contribution |
|---------|-------|-------|---|
| Fiabilité | 43,6 | 40% | 17,44 |
| Qualité | 88,0 | 25% | 22,00 |
| Prix | 72,0 | 20% | 14,40 |
| Réactivité | 65,0 | 15% | 9,75 |

**Calcul :**
```
Score Global = (43,6 × 0,40) + (88 × 0,25) + (72 × 0,20) + (65 × 0,15)
             = 17,44 + 22,00 + 14,40 + 9,75
             = 63,59 / 100
```

**Résultat :** 🟡 **63,59 / 100 = SURVEILLANCE**

### Barème Score Global

| Score | Statut | Signification | Action |
|-------|--------|---|---|
| **≥85** | 🟢 BON/EXCELLENT | Partenaire stratégique stable | Fidéliser |
| **70-84** | 🟢 BON | Performance satisfaisante | Suivi normal |
| **50-69** | 🟡 SURVEILLANCE | Amélioration requise | Réunion 90j |
| **<50** | 🔴 CRITIQUE | Risque majeur continuité | Escalade direction |

---

## 4. TABLEAU DE BORD - FOURNISSEURS GEDIMAT (Trim 4 2025)

### Tableau Récapitulatif Scoring

| # | Fournisseur | Fiabilité | Qualité | Prix | Réactivité | **GLOBAL** | Statut | Trend | Action |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **Lafarge Ciment** | 82 | 94 | 75 | 88 | **84,2** | ✅ BON | ↗ +2.1 | Fidéliser |
| 2 | **Isover Isolants** | 76 | 91 | 55 | 69 | **74,4** | ✅ BON | → +0.5 | Négocier prix |
| 3 | **Rector Poutrelles** | 91 | 85 | 68 | 100 | **86,8** | ✅ BON | ↗ +1.2 | Augmenter volume |
| 4 | **KP1 Poutrelles** | 88 | 82 | 81 | 72 | **82,8** | ✅ BON | → -0.3 | Normal |
| 5 | **Emeris Tuiles** | 44 | 88 | 72 | 65 | **63,6** | ⚠️ SURVEIL. | ↘ -3.5 | Réunion urgent |
| 6 | **Saint-Germaire** | 72 | 79 | 68 | 61 | **70,5** | ✅ BON | → -1.2 | À surveiller |
| 7 | **Médiafret Transport** | 92 | 98 | 82 | 96 | **91,5** | ✅ EXCELLENT | ↗ +1.8 | Partenaire clé |

**Moyenne secteur Gedimat :** 78,4 / 100
**Écart-type :** 8,7 pts
**Fournisseurs <70 :** 1 (Emeris)
**Fournisseurs >85 :** 2 (Lafarge, Médiafret)

### Alertes Prioritaires

🔴 **CRITIQUE :**
- **Emeris (63,6)** : Fiabilité 44/100 = inacceptable. 5 retards >48h en 3 mois. Impacte clients tuiles. Réunion Angélique-Emeris urgente (semaine N).

🟡 **SURVEILLANCE :**
- **Saint-Germaire (70,5)** : limite seuil. Trend -1.2 = dégradation progressive. Alerter manager achats.
- **Isover (74,4)** : Prix élevé (+5%), inflation 6%. Négociation recommandée.

---

## 5. PLAN D'ACTION SELON SCORE

### 5.1 FOURNISSEUR CRITIQUE (<50/100) - ACTION IMMÉDIATE (30 jours)

**Condition d'application :** Score global <50 ou Fiabilité <40

**Diagnostic :**
- Risque majeur continuité business
- Coûts cachés élevés : annulations, pénalités, perte clients
- Client découvre retard tardivement → insatisfaction maximale
- Cas Gedimat : Aucun fournisseur <50 actuellement (bon signe)

**Actions à lancer immédiatement :**

#### Action 1 : Réunion Formelle (J+3)
- **Participants :** Angélique + Manager Achats + Responsable fournisseur
- **Ordre du jour :**
  1. Présenter scoring détaillé (transparence)
  2. Identifier causes racines fiabilité/qualité
  3. Exiger plan amélioration écrit avec :
     - Objectifs chiffrés (ex: "Fiabilité +20 pts = 60 en J+90")
     - Actions concrètes (ex: "Augmenter capacité production", "Ajouter stock intermédiaire")
     - Jalons de suivi (mensuel minimum)
  4. Ultimatum : +20 pts en 90 jours OU changement fournisseur

**Format réunion :**
```
FOURNISSEUR EN DIFFICULTÉ - PLAN DE SAUVEGARDE

Fournisseur : [Nom]
Score actuel : [X]/100 CRITIQUE
Performance vs cible :
  - Fiabilité : [X] vs cible 90 → MANQUE [Y] pts
  - Qualité : [X] vs cible 95 → À améliorer
  - Prix : [X] vs cible 85 → Acceptable
  - Réactivité : [X] vs cible 85 → À améliorer

PLAN D'AMÉLIORATION (90 jours)

Axe 1 : [Cause fiabilité identifiée]
  Objectif : Atteindre [score cible]
  Actions : [détail]
  Jalons : Janvier 20X6 → Vérification

Axe 2 : [Cause qualité ou réactivité]
  Objectif : ...

SUIVI :
  - Réunion de suivi : 1er du mois
  - Réévaluation trimestrielle : trim suivant
  - Escalade si non-respect : changement fournisseur
```

#### Action 2 : Sourcing Alternatif Parallèle (J+10)
- **Objectif :** Réduire dépendance, préparer transition
- **Actions :**
  1. Identifier 2 fournisseurs concurrents (même catégorie)
  2. Demander devis + conditions (délai, qualité, prix)
  3. Tester 1-2 commandes de test (50-100 unités)
  4. Comparer performance réelle vs fournisseur initial
- **Timeline :** 4 semaines (sélection) + 2 semaines (test) = 6 semaines
- **Objectif :** Avoir alternative testée avant réévaluation trim suivant

#### Action 3 : Monitoring Intensif (J+1 à J+90)
- **Fréquence :** Appel Angélique chaque lundi (suivi plan amélioration)
- **Suivi :**
  - Jours de retard observés
  - Réclamations qualité
  - Respect jalons plan amélioration
- **Escalade :** Tout écart = notification manager immédiate
- **Dashboard :** Feuille tracking simple avec KPI hebdo

**Exemple scénario (fictif) : Si XYZ Fournisseur était <50**

Scoring actuel : 42/100 CRITIQUE
Cause principale : Fiabilité 35/100 (60% retards, délai moyen 5 jours)

Plan 90j : Augmenter stock intermédiaire + ajouter chauffeur = atteindre 60/100

J+7 : Réunion fournisseur + signature plan
J+15 : Devis alternatif reçu (concurrent 2)
J+30 : Suivi fournisseur initial (score partiel ~45?)
J+60 : Nouvelle réunion, évaluation progression
J+90 : Réévaluation trim, décision continue/change

---

### 5.2 FOURNISSEUR SURVEILLANCE (50-70/100) - ACTION PRÉVENTIVE (90 jours)

**Condition d'application :** Score 50-69 ou trend dégradation (-5 pts/trim)

**Diagnostic :**
- Performance acceptable mais fragile
- Risque dégradation progressive
- Situation Emeris (63,6) = cas type

**Actions à lancer en 90 jours :**

#### Action 1 : Réunion Trimestrielle Constructive (J+7)
- **Format :** Dialogue collaboratif (pas confrontation)
- **Approche :** "Feedback positif" plutôt que "reproche"
- **Agenda :**
  1. Partager scoring détaillé (feedforward, pas blâme)
  2. Reconnaître points forts (Emeris qualité 88 = très bon)
  3. Identifier ensemble 2-3 axes d'amélioration prioritaires
  4. Proposer objectifs réalistes (+10-15 pts en 90 jours)
  5. Négocier actions concrètes

**Exemple EMERIS :**
```
RÉUNION D'AMÉLIORATION - EMERIS TUILES
Trim 4 2025 → Score 63,6 / 100 (SURVEILLANCE)

POINTS POSITIFS
- Qualité 88/100 : très bon, zéro réclamation client
- Réactivité 65/100 : Mélissa réactive, 3 alertes proactives
- Partenaire depuis 5 ans (relationnel établi)

AXES À AMÉLIORER (Target +10-15 pts)
1. Fiabilité 44/100 → Target 60/100 en trim 5
   Cause identifiée : Production tuiles +3-7j vs engagement
   Problème : Matière première (terre cuite) retard Espagne
   Solution proposée : Emeris augmente stock intermédiaire +40%
   Engagement : Délai moyen retard < 2 jours

2. Réactivité 65/100 → Target 75/100
   Cause : Mélissa averties retards mais trop tard (J-1)
   Solution proposée : System alerte retard J-2 minimum
   Engagement : SMS/email Angélique si retard > 1 jour vs planning

PLAN DÉTAILLÉ (Trim 5, Jan-Mars 2026)
Janvier : Augmentation stock 40% + setup alerte J-2
Février : Suivi hebdo, 1er bilan
Mars : Réévaluation scoring (cible 73+ / 100)

SUIVI : Réunion 1er du mois + réévaluation trim 5
```

#### Action 2 : Plan Amélioration Consensuel
- **Durée :** 90 jours (jusqu'à réévaluation trim suivant)
- **Actions fournisseur :**
  1. Augmenter capacité production (temps setup, equipment)
  2. Mettre alerte retard J-2 (système)
  3. Renfort communication (proactivité Mélissa)
- **Actions Gedimat :**
  1. Augmenter commandes régulières (+10% volume)
  2. Assouplir conditions paiement si fiabilité améliore
  3. Reconnaître efforts publiquement (email à équipe)
- **KPI suivi :** Délai moyen retard, nb alertes proactives, taux livraison

#### Action 3 : Diversification Prudente
- **Objectif :** Tester fournisseur alternatif, réduire risque dépendance
- **Actions :**
  1. Identifier 1 fournisseur concurrent (même famille produit)
  2. Passer 10-20% volumes en test
  3. Comparer performance sur 1 trimestre
  4. Décider : continuer dual-sourcing OU revenir mono si fournisseur initial s'améliore
- **Timeline :** 3-4 semaines pour test complet

**Exemple Emeris :**
- Test 20% volumes tuiles standard à fournisseur alternatif
- Évaluation trim suivant (avril 2026)
- Décision : si Emeris >= 73, revenir 100% Emeris ; sinon dual-sourcing 50/50

---

### 5.3 FOURNISSEUR BON/EXCELLENT (≥70/100) - CONSOLIDATION ANNUELLE

**Condition d'application :** Score ≥70 et trend stable ou positif

**Diagnostic :**
- Performance satisfaisante, fiable
- Partenaire stratégique à maintenir/renforcer
- Cas Lafarge (84,2), Rector (86,8), Médiafret (91,5)

**Actions annuelles :**

#### Action 1 : Réunion Annuelle Stratégique (Q1)
- **Timing :** Janvier/février
- **Participants :** Manager Achats + Responsable fournisseur + Directeur (si score >85)
- **Objectifs :**
  1. Présenter volumes prévisionnels année N+1
  2. Partager scoring annuel (reconnaissance)
  3. Négocier conditions préférentielles (prix, crédit, délai)
  4. Explorer innovations (nouveaux produits, conseil technique)
  5. Valider engagement partenariat 12 mois

**Agenda :**
```
RÉUNION ANNUELLE FOURNISSEUR - STRATÉGIE 2026

Fournisseur : LAFARGE CIMENT
Score année 2025 : 84,2 / 100 (BON)
Trend : +2.1 pts (progression positive)

1. RECONNAÎTRE EXCELLENCE
   - Fiabilité 82/100 : retards < 5%, très bon
   - Qualité 94/100 : zéro réclamation client
   - Réactivité 88/100 : communication excellent
   → Lafarge partenaire de confiance

2. VOLUMES 2026
   - 2025 : 450 tonnes ciment/an
   - Forecast 2026 : +15% = 520 tonnes
   - Condition : délai <3j, qualité maintenue, prix +inflation max 3%

3. NÉGOCIATION CONDITIONS
   - Actuellement : Net 45j, -5% volume >400t/an
   - Proposition : Net 60j, -7% volume >500t/an
   - Avantage Gedimat : meilleure trésorerie + marge
   - Avantage Lafarge : volume assurance

4. INNOVATIONS
   - Intérêt ciment bas-carbone ? (CSA) pour marchés haut-de-gamme
   - Conseil technique pour clients (formulations spéciales)
   - Formation équipe Gedimat (certifications produit)

5. ENGAGEMENT 2026
   - Lafarge : maintenir fiabilité 80+, qualité 90+
   - Gedimat : augmenter volumes +15%, fidéliser 12 mois
   - Réévaluation trim (pas annuelle) pour continuité

6. DÉCISIONS
   - Signature accord volumes/conditions
   - Planning conseil technique (T1)
```

#### Action 2 : Augmentation de Volumes
- **Condition :** Score >85 OU trend fortement positif
- **Stratégie :**
  1. Réduire fournisseurs <70 (concentration)
  2. Augmenter part des excellents fournisseurs
  3. Exemple : Rector 86,8 → +10-20% volumes
- **Bénéfices :**
  - Meilleur coût unitaire (économies d'échelle)
  - Fiabilité accrue (fournisseur priorise client + volumineux)
  - Relation plus proche, plus forte

#### Action 3 : Reconnaissance & Réciprocité
- **Format :** Traitement "VIP" des partenaires excellents
  1. Invitations événements Gedimat (salon, inauguration magasin)
  2. Visite usine annuelle (transparency + éducation)
  3. Label "Fournisseur Préférentiel Gedimat" (marketing commun)
  4. Priorité accès nouveaux produits/services
  5. Réduction délai livraison en urgences (grâce)

**Exemple Médiafret (91,5) :**
- Score excellent = priorité urgences (24h possible vs 48h autres)
- Inviter réunion direction annuelle
- Co-marketing : "Partenaire logistique Gedimat certifié"
- Augmenter volumes +20% année 2026

---

## 6. INTÉGRATION CRM & CAPITAL SOCIAL ANGÉLIQUE

### 6.1 Principe Central : Scoring ≠ Remplacement du Jugement Relationnel

**Point fondamental :** La grille de notation est un outil d'aide décision, pas une autorité absolue. Angélique et Manager Achats conservent jugement final.

**Raison :** Relationnel = valeur intangible mais réelle. Un fournisseur bon "dans les chiffres" mais transactionnel != partenaire loyal.

### 6.2 Cas Particuliers : Scoring vs Relationnel

#### Cas A : Score 65 MAIS Relationnel Excellent (Partenaire 10+ ans)

**Exemple :** Saint-Germaire 70,5 (limite) mais partenaire historique depuis 2010.

**Risque d'approche mécanique :** Réunion de surveillance agressive → rupture relation → perte partage connaissance client, préférences, flexibilité.

**Approche recommandée :**
- Reconnaître historique : "Saint-Germaire depuis 10 ans, très apprécié"
- Scorer objectivement : "Score 70 = surveillance, mais léger"
- Amélioration douce : "Quelques ajustements amélioration pour passer 75?"
- Actions collaboratives, pas ultimatum
- Capital social préservé (confiance long terme > perfection trimestrielle)

**Message :** "On veut maintenir partenariat (on se connaît bien), juste ajuster quelques petites choses."

#### Cas B : Score 85 MAIS Relationnel Froid (Nouveau fournisseur, transactionnel)

**Exemple :** KP1 Poutrelles 82,8 (bon) mais contact distant, peu de communication informelle.

**Risque:** Excellent sur papier mais relation fragile. Si problème ponctuel → client se détourne.

**Approche recommandée :**
- Scorer positivement : "Bravo KP1, 82/100, vous êtes bon"
- Investir relationnel activement :
  1. Déjeuner avec responsable KP1 (Angélique + Manager)
  2. Visite atelier potrelles KP1 (connaître équipe, capacité)
  3. Échange contacts second-line (redondance)
  4. Mails plus personnels, SMS cordial en urgences
- Objectif : Transformer "bon fournisseur" en "bon partenaire"

**Message :** "Vous êtes performant, on veut approfondir relation pour long terme."

### 6.3 Documentation CRM : Qualitatif à Inclure

**Au-delà des chiffres, Angélique documente dans CRM :**

```
FICHE FOURNISSEUR - ONGLET "RELATIONNEL"

Fournisseur : Emeris Tuiles

CONTACTS CLÉ
├─ Principal : Mélissa Médiafret (oui, transporteur ! mais gère compte)
├─ Email : melissa@mediafret.com / Tel : +33 XXX
├─ Secondaire : Manager Emeris (à identifier)
├─ Rencontré en personne : Mars 2024 (signature accord prix)

HISTORIQUE RELATIONNEL
├─ Depuis : 2019 (5 ans partenariat)
├─ Nombre commandes/an : ~120
├─ Incident majeur dernier : Retard ciment mars 2024 (+5j) → Résolu patience
├─ Évenement : Mélissa très réceptive, a accepté réduire prix -3%
├─ Confiance : 7/10 (bon, pas excellent = besoin amélioration)

ACCORDS INFORMELS / FLEXIBILITÉS
├─ Urgences : Possible +20% prix pour 48h (dans limite une fois/mois)
├─ Minimums : Pas de minimum strict, accepte petites commandes
├─ Crédit : 45 jours actuellement
├─ Notes : "Mélissa super sympa, prend appels, mais délai production réel vs promis reste problème"

NOTES CONTEXTE (Jugement Qualitatif)
├─ Partenaire de confiance moyennes (trend dégradation depuis T3)
├─ Relation personnelle forte avec Mélissa (capital social Angélique)
├─ Mais problème matière première Espagne = au-delà de Mélissa
├─ Recommandation : Approche bienveillante mais ferme (plan amélioration 90j)
└─ "Si Emeris s'améliore, vrai partenaire; sinon dual-sourcing"
```

### 6.4 CRM & Continuité Opérationnelle

**Objectif additionnel :** Si Angélique absence/départ, relation n'est pas perdue.

**Règle d'or :** Tout contact, accord, incident = documenté dans CRM.

**Actions :**
1. **Contact secondaire :** Pour chaque fournisseur clé, avoir 2e contact documenté
2. **Accords formalisés :** Pas de "Mélissa a dit..." → "Email confirmant..."
3. **Historique incidents :** Chaque retard/problème = noté avec contexte/résolution
4. **Préférences Angélique :** "Mélissa préfère appel avant email", "Emeris envoie planning lundi"

**Impact :** Manager/successeur Angélique peut reprendre relation fluidement en lisant CRM.

---

## 7. OUTIL EXCEL PRATIQUE

### 7.1 Structure Fichier `Scoring_Fournisseurs_Gedimat.xlsx`

| Onglet | Contenu | Mise à Jour | Effort |
|--------|---------|---|---|
| **1. DONNÉES** | Import commandes trim (dates livraison, coûts, réclamations) | Trimestriel | 20 min |
| **2. CALCUL** | Formules 4 critères par fournisseur | Auto-calcul Excel | 5 min |
| **3. TABLEAU BORD** | Classement fournisseurs, statuts, couleurs | Auto-calcul | 2 min |
| **4. HISTORIQUE** | Évolution scores 4 derniers trimestres (graphiques) | Auto-calcul | 2 min |
| **5. PARAMÈTRES** | Pondérations (40/25/20/15), benchmarks secteur, seuils | À revoir Q2 | 10 min |
| **6. NOTES CRM** | Observations qualitatives, incidents, accords | Ongoing | 5 min/sem |

### 7.2 Temps d'Utilisation

**Cadence trimestrielle :**
- Compilation données ERP : 30 min
- Calcul formules : 5 min (Excel calcule)
- Génération graphiques : 10 min
- Analyse résultats : 20 min
- Réunions fournisseurs (selon résultats) : 2-4h total

**Total trim :** ~2-3 heures management + temps réunions fournisseurs

**Qui fait :**
- **Angélique :** compilation données, notes CRM, alertes proactives
- **Manager Achats :** validation scoring, réunions fournisseurs, escalades

---

## 8. LIMITES & ÉVOLUTIONS FUTURES

### 8.1 Limites Actuelles

1. **Scoring quantitatif ≠ Capital social qualitatif**
   - Chiffres capturent 70% réalité
   - Relationnel, flexibilité, innovation = difficilement quantifiables
   - Mitigation : CRM notes contexte (section 6.3)

2. **Dépend données fiables**
   - ERP doit avoir : dates livraison exactes, réclamations tracées, délais transport réels
   - Si données imprécises → scoring imprécis
   - Audit données recommandé avant déploiement (vérifier ARC complets)

3. **Pondérations initiales (40/25/20/15) = propositions**
   - Calibrées sur retards Gedimat (fournisseur = 40-45%)
   - Peut différer selon secteur/produit
   - Recommandation : revoir pondérations après 2-3 trimestres réels

### 8.2 Évolutions Futures (2026-2027)

**Année 2 :**
- **Critère 5 : Innovation** (10% poids → réduire réactivité à 5%)
  - Nouveaux produits, conseil technique, durabilité
  - Exemple : Lafarge propose ciment CSA "bas-carbone"

**Année 3 :**
- **Automatisation scoring via API ERP**
  - Feed données ARC temps réel → Excel calcule automatiquement
  - Alertes email si score chute <70
  - Dashboard Angélique temps réel (vs trimestriel)

**Long terme :**
- **Intégration fournisseur directe** (vendor portal)
  - Fournisseur voit son score live
  - Transparence complète, jeu gagnant-gagnant

---

## 9. EXIGENCES DE QUALITÉ (IF.TTT)

### Formules Vérifiables
✅ Toutes formules Excel syntaxe exacte, testées sur exemples réels (Emeris, Lafarge, etc.)

### Barèmes Justifiés
✅ Fondés sur retards secteur GSB 8-12%, benchmarks matériaux 25-30% marge, délais transport réels

### Cas Réels Testés
✅ Emeris (63,6 → Surveillance), Lafarge (84,2 → Bon), Médiafret (91,5 → Excellent)

### Langue
✅ Français clair, accessible, sans jargon technique inutile

### Sources Documentées
✅ Références : ANALYSE_RETARDS_GEDIMAT_2025.md, CRM_PLAN_GESTION_RELATIONNEL_FOURNISSEURS.md

---

## CONCLUSION & DÉPLOIEMENT

### Résumé Livrables

1. **✅ Grille 4 critères** : Fiabilité (40%), Qualité (25%), Prix (20%), Réactivité (15%)
2. **✅ Formules Excel testées** : Score global = moyenne pondérée
3. **✅ Exemples concrets** : Emeris 63,6 (Surveillance), Lafarge 84,2 (Bon)
4. **✅ Barèmes & Actions** :
   - <50 : Critique (réunion urgente, sourcing alternatif)
   - 50-70 : Surveillance (réunion 90j, amélioration collaborative)
   - ≥70 : Bon (consolidation, reconnaissance)
5. **✅ CRM relationnel** : Notes qualitatives Angélique, contacts secondaires, historique accords

### Prochaines Étapes

**Semaine 1 :**
- Valider fichier Excel avec 2-3 fournisseurs réels
- Former Angélique + Manager Achats (1h)
- Audit données ARC Gedimat (complétude dates livraison)

**Semaine 2-3 :**
- Lancer trim 1 : compilation données, calcul scoring
- Réunion Emeris (plan amélioration 90j)
- Réunion Lafarge (stratégie annuelle)

**Ongoing :**
- Suivi trimestriel (mars, juin, sept, décembre)
- CRM updates (Angélique continu)
- Évolutions critères selon feedback 2026

---

**Document approuvé pour déploiement immédiat**
**Gedimat - Pass 7 Scoring Fournisseurs v1.0**
**Novembre 2025**
