# PASS 7 - Tool 5: Grille Scoring Fournisseurs
## Évaluation Quantifiée & Gestion Contractuelle Trimestrielle

**Date:** 16 novembre 2025
**Responsable:** Angélique + PDG
**Fréquence:** Trimestrielle (Q1, Q2, Q3, Q4)
**Utilisation:** Justification SLA, renegociation contrats, identification alternatives
**Format:** Excel scoreboard + réunion 2h PDG-Angélique chaque trimestre

---

## 1. OBJECTIF & FRÉQUENCE

### Qui Score? Quand? Pourquoi?

**Propriétaires du processus:**
- **Angélique:** Collecte data, évalue critères qualitatifs (communication, flexibilité observée)
- **PDG:** Valide scores, décide actions (renegociation, replacement RFQ, reconnaissance)
- **Récurrence:** Réunion 2h chaque trimestre (15 mars, 15 juin, 15 septembre, 15 décembre)

**Objectif stratégique:**
Remplacer jugement personnel ("je crois qu'Éméris est fiable") par évaluation data-driven permettant:
- Justification chiffrée pour renegocier SLA (ex: "délai promise 5j, vous livrez 7j en moyenne → −€X ou remplacement")
- Identification fournisseur backup quand score <60
- Reconnaissance fournisseur performant (conditions meilleur prix, délai garanti, priorité)
- Documentation objective pour PDG en cas absence Angélique

**Output trimestriel:**
1. Classement tous fournisseurs en 3 tiers (Préféré/Standard/Risque)
2. Plan d'action pour fournisseur tier Risque (ultimatum 30 jours améliorement)
3. Tableau de bord historique 4 trimestres (tendance)
4. Minutes réunion avec décisions contractuelles

---

## 2. GRILLE SCORING DÉTAILLÉE (4 Critères)

### Critère 1: DÉLAI (30% poids)

**Métrique primaire:** % livraisons respectant délai promis (fenêtre ±48h acceptée)

**Définition:**
- Délai promis = date convenue dans bon de commande
- Livraison OK = reçue entre J-2 et J+2 de délai promis
- Retard compté = dépassement fenêtre ±48h (ex: promis J5, reçu J8 = retard 3 jours)

**Grille scoring (0-100 pts):**

| Score | Ponctualité | Définition | Exemple |
|-------|------------|-----------|---------|
| **100 pts** | ≥95% | Livraisons respectées, max 1 retard sur 20 commandes | 19/20 on-time |
| **80 pts** | 85-94% | Fiable, occasionnels retards <2j | 17/20 on-time, 3 retard <2j |
| **60 pts** | 75-84% | Acceptable, retards fréquents mais <4j | 15/20 on-time, 5 retard <4j |
| **40 pts** | 65-74% | Problématique, retards récurrents >3j | 13/20 on-time, 7 retard >3j |
| **0 pts** | <65% | Critique, non-fiable, >35% retards | <13/20 on-time |

**Data source:** Historique 3 mois minimum (min 10 livraisons tracées)
- Source: Bon de livraison date/heure réception vs. date promis
- Collecte: Angélique vérifie bon livraison 1x/semaine

**Notes pratiques:**
- Retard météo (neige, grève SNCF) = pas compté contre fournisseur (force majeure)
- Retard dû à Gedimat (ex: "mercredi pas possible, reporter mardi") = pas compté
- Urgence demandée en J+1 si normalement 7j = tolérance +24h acceptable

---

### Critère 2: QUALITÉ (25% poids)

**Métrique primaire:** Taux conformité (zéro défaut, quantité exacte, emballage intact)

**Définition:**
- Conformité = Produit reçu = produit commandé (matière, format, quantité) + emballage OK
- Incident = Manquant, mauvais produit, défaut visible (casse, humidité), quantité incorrecte
- Critérium: Incident détecté immédiatement à réception (pas découvert après)

**Grille scoring (0-100 pts):**

| Score | Taux Conformité | Taux Défaut | Définition | Exemple |
|-------|-----------------|------------|-----------|---------|
| **100 pts** | ≥99% | <0,5% | Excellente, quasi zéro incident | 0-1 incident sur 20 livraisons |
| **80 pts** | 95-98% | 0,5-1,5% | Bon, incident rare et résolu vite | 2-3 incidents sur 20 livraisons |
| **60 pts** | 90-94% | 1,5-3% | Acceptable, incidents contrôlés | 4-6 incidents sur 20 livraisons |
| **40 pts** | 85-89% | 3-5% | Problématique, incidents récurrents | 7-10 incidents sur 20 livraisons |
| **0 pts** | <85% | >5% | Critique, non fiable, peu d'efforts correction | >10 incidents sur 20 livraisons |

**Data source:** Incident logs CRM + bon de réception
- Source: Fiche incident Angélique (création automatique si article refusé)
- Collecte: Angélique log immédiatement ou dépôtier rapporte
- Résolution: Fournisseur avis 48h → avoir/remplacement dans 5j

**Scoring pondéré par impact:**
- Incident mineur (1 produit manquant sur 100): -1 point conformité
- Incident majeur (livraison entièrement mauvais produit): -10 points conformité
- Incident qualité découvert client (casse tuile après): -15 points (réputation client)

---

### Critère 3: FLEXIBILITÉ (25% poids)

**Métrique primaire:** Acceptation commandes urgentes (<J+3) + flexibilité volume minimum

**Définition:**
- Urgence: Commande demandée avec délai <3j ouvragles
- Flexibilité volume: Acceptation minimum order size (MOQ)
- Critère composite: % urgences acceptées × % commandes petits volumes acceptées

**Grille scoring (0-100 pts):**

| Score | Urgences <J+3 | MOQ Flexibilité | Définition | Exemple |
|-------|---------------|-----------------|-----------|---------|
| **100 pts** | ≥90% accepte | <500kg / pas limite | Très flexible, accommodant | "Besoin 200kg tuiles lundi?" → OK |
| **80 pts** | 70-89% accepte | <1 tonne | Flexible, urgences OK avec surcoût | "Besoin 500kg ciment J+2?" → OK +€50 |
| **60 pts** | 50-69% accepte | 1-2 tonnes | Acceptable, urgences case-by-case | "Besoin 1,5t J+2?" → possible si stock |
| **40 pts** | 25-49% accepte | 2-3 tonnes | Peu flexible, refuse petites urgences | "Besoin 1t jeudi?" → non stock, attendre |
| **0 pts** | <25% accepte | >3 tonnes | Rigide, seules grosses commandes | "Besoin <3t?" → "Commandez 5t minimum" |

**Data source:** Urgent order tracking + historique acceptation
- Source: Tickets urgence (Angélique crée si "Besoin J+1 ou J+2")
- Collecte: Réponse fournisseur (accepte oui/non + délai + surcoût)
- Statut: Client satisfaction si urgence livrée, mécontentement si refusée

**Notes pratiques:**
- Urgence "météo imprévue sur chantier" = légitime (score le fournisseur)
- Urgence "oubli Angélique" = réduction score si récurrent
- Fournisseur accepte mais live +2j après promis = compte comme refus

---

### Critère 4: COMMUNICATION (20% poids)

**Métrique primaire:** Réactivité (appels/emails) + proactivité alertes

**Définition:**
- Réactivité: Temps pour répondre appel/email concernant statut commande/problème
- Proactivité: Alerte spontanée si retard détecté (avant Angélique appelle)
- Tonalité: Relation constructive, propose solutions (vs. blâme)

**Grille scoring (0-100 pts):**

| Score | Réactivité | Proactivité Alerte | Définition | Exemple |
|-------|-----------|-------------------|-----------|---------|
| **100 pts** | <1h réponse | ≥80% alertes proactives | Excellent, appelle Angélique si retard | "Éméris appelle: livraison retard +2j, OK?" |
| **80 pts** | 1-2h réponse | 60-79% proactif | Bon, réactif, alerte fréquente | "Email 10h: livraison Friday not Thursday" |
| **60 pts** | 2-4h réponse | 40-59% proactif | Acceptable, répond mais pas toujours alert | Email réponse le jour même, parfois tardif |
| **40 pts** | 4-8h réponse | 20-39% proactif | Faible, réactivité tardive | Réponse lendemain, jamais de proactivité |
| **0 pts** | >8h réponse | <20% proactif | Critique, radio silence | "Appelez demain" type response |

**Data source:** Angélique subjective assessment + CRM notes
- Source: Appels/emails log dans CRM + notes contextuelles (relation tone)
- Collecte: Angélique évalue qualitativement chaque trimestre
- Échelle tonalité: "Super sympa" (+10), "Neutre" (0), "Difficile" (-10)

**Scoring pondéré par criticité:**
- Communication excellente même si score autre critère moyen: +5 bonus points (confiance relationship)
- Communication très mauvaise (ignore appels): -10 pénalité (risque sécurité)

---

## 3. CALCUL FINAL & CLASSIFICATION

### Formule Composite

```
Score_Final = (Délai × 0.30) + (Qualité × 0.25) + (Flexibilité × 0.25) + (Communication × 0.20)

Exemple:
  Délai:       80 pts × 30% = 24 pts
  Qualité:     90 pts × 25% = 22,5 pts
  Flexibilité: 65 pts × 25% = 16,25 pts
  Communication: 70 pts × 20% = 14 pts
  ─────────────────────────────
  Score_Final = 76,75 / 100 → STANDARD tier
```

### Seuils & Classification

**3 tiers de relation:**

| Tier | Score | Statut Contrat | Conditions Achat | Action Immédiate |
|------|-------|---|---|---|
| **PRÉFÉRÉ** | ≥80 | Prioritaire | Délai J+60, volume garanti | Reconduire contrat, accordez bénéfices (prix -2%, urgence freemium) |
| **STANDARD** | 60-79 | Normal | Délai J+45, monitoring | Contractuel OK, réunion amélioration, exiger +5pts Q suivant |
| **RISQUE** | <60 | En vigilance | Délai J+30, appels hebdo | Ultimatum 30j améliorement sinon RFQ remplacement |

### Actions Associées par Tier

**PRÉFÉRÉ (≥80):**
- Reconduire contrat annuel sans renegociation de prix
- Offrir conditions avantageuses: délai paiement J+60, commandes anticipées, petit volume OK
- Invitation réunion annuelle "appréciation fournisseur" (PDG + Angélique)
- Priorité urgence si stock limité (tu livres Gedimat avant autres clients)

**STANDARD (60-79):**
- Contrat normal 1 an, révision trimestrielle score
- Conditions standard: paiement J+45, MOQ standard, urgence surcoût 10%
- Réunion amélioration si score baisse (ex: 75 → 70 → action plan)
- Alternative RFQ lancée discrètement en background si trend baisse

**RISQUE (<60):**
- Mise en demeure 30 jours: "amélioration +10pts OU remplacement fournisseur"
- Plan d'action écrit (Angélique + fournisseur): quoi changer (délai? qualité?), par qui, par quand
- Weekly check-in (appel mardi 10h fixe avec fournisseur) pour suivre progression
- RFQ remplacement lancée immédiatement (courant de secours)
- Si après 30j pas amélioration: rupture contrat, bascule fournisseur backup

---

## 4. EXEMPLE CONCRET: ÉMÉRIS TUILES

### Contexte

**Fournisseur:** Éméris (tuiles, produit clé Gedimat)
**Historique Angélique:** 4 ans, relation stable mais "souvent retard", refuse petites commandes, communication tardive
**Données trimestre (3 mois):** Octobre-Décembre 2025

### Collecte Données Trimestre

#### Délai

Historique livraisons 3 mois:
```
Semaine Oct 1: Commande 5t tuiles, livraison promise J+5 → reçu J+7 (retard 2j)
Semaine Oct 2: Commande 2t tuiles, livraison promise J+5 → reçu J+5 (OK)
Semaine Oct 3: Commande 3t tuiles, livraison promise J+5 → reçu J+5 (OK)
Semaine Oct 4: Commande 4t tuiles, livraison promise J+5 → reçu J+6 (retard 1j)
Semaine Nov 1: Commande 2,5t tuiles, livraison promise J+5 → reçu J+8 (retard 3j) ⚠️
Semaine Nov 2: Commande 6t tuiles, livraison promise J+5 → reçu J+5 (OK)
Semaine Nov 3: Commande 3,5t tuiles, livraison promise J+5 → reçu J+7 (retard 2j)
Semaine Nov 4: Commande 4t tuiles, livraison promise J+5 → reçu J+5 (OK)
Semaine Dec 1: Commande 2t tuiles, livraison promise J+5 → reçu J+5 (OK)
Semaine Dec 2: Commande 5t tuiles, livraison promise J+5 → reçu J+6 (retard 1j)
Semaine Dec 3: Commande 3,5t tuiles, livraison promise J+5 → reçu J+5 (OK)
Semaine Dec 4: Commande 4,5t tuiles, livraison promise J+5 → reçu J+5 (OK)
```

**Analyse:**
- Total 12 livraisons tracées
- OK à l'heure: 8/12 (67%)
- Retard <2j: 3/12 (25%)
- Retard >2j: 1/12 (8%)
- Ponctualité nette: 8/12 = **67%** → Falling in 65-74% bracket

**Score DÉLAI: 40 pts** (zone "problématique, retards récurrents >3j moyenne")

*Justification:* Plusieurs retards >2j sur petit volume (2-3t), indiquant possibilité dépassement capacité. Délai 5j promis pas fiable.

---

#### Qualité

Incidents tracés 3 mois (CRM log Angélique):
```
Oct 15: Livraison 5t tuiles → 1 palette endommagée (crasse angle) → remplacement J+2
Oct 28: Livraison 2t tuiles → OK
Nov 5: Livraison 2,5t tuiles → 3 tuiles fêlées détectées → avoir €150 accepté
Nov 12: Livraison 6t tuiles → OK
Nov 26: Livraison 3,5t tuiles → 2 tuiles mauvais format → remplacement J+3
Dec 8: Livraison 2t tuiles → OK
Dec 15: Livraison 5t tuiles → OK
Dec 26: Livraison 3,5t tuiles → 1 palette avec humidité → client découverte (!) → crédit €300

Total incidents: 4 incidents sur 12 livraisons → taux = 4/12 = **33% taux d'incident**
```

**Calcul conformité:**
- Livraisons sans incident: 8/12 (67%)
- Incidents détectés Gedimat: 3/12 (3 palettes, 6 tuiles)
- Incidents découverts client: 1/12 (critique pour réputation)

**Score QUALITÉ: 60 pts** (zone "acceptable, incidents contrôlés" mais incident client détecté = alert pour futur)

*Justification:* Taux défaut ~3% acceptable, MAIS incident client détecté après livraison = risque réputation. Besoin amélioration qualité contrôle emballage (humidité).

---

#### Flexibilité

Demandes urgence & petits volumes 3 mois:
```
Oct 10: Urgence J+2 (2t) → Éméris répond "possible mais +€80 surcoût"
Oct 21: Commande 500kg (petit volume) → Éméris "pas possible, MOQ 2t minimum"
Nov 8: Urgence J+1 (urgent client) → Éméris "non possible, stock épuisé"
Nov 18: Commande 1,5t (petit volume) → Éméris "acceptable 1,5t car stock"
Dec 5: Urgence J+3 (3t) → Éméris "oui possible, livraison normal"
Dec 12: Commande 800kg (petit volume) → Éméris "trop petit, reportez 2t minimum"

Acceptation urgence: 2 acceptées sur 3 demandées = 67% taux acceptation
Acceptation petit volume: 1 acceptée sur 3 demandées = 33% taux acceptation
```

**Score FLEXIBILITÉ: 65 pts** (zone "acceptable, urgences case-by-case" + "MOQ 1-2t")

*Justification:* Accepte urgences 2j sur 3, acceptable. Refuse systématiquement <1t, problème car Gedimat a besoin flexibilité petites commandes. Négociation nécessaire.

---

#### Communication

Réactivité & proactivité Angélique subjective:
```
Oct-Dec interactions:
- Appels/emails en moyenne: Éméris répond <4h en 70% cas, >8h en 30% cas
- Proactivité alerte: Alerté retard seulement 1 fois sur 4 retards → 25% proactif
- Tonalité relation: Neutre-correcte (pas difficile, pas sympa), transactions business
- Réaction incidents: Réactif en remplacement (J+2-3), pas d'excuses préalables

Évaluation Angélique: "Répond OK mais jamais d'appel proactif si problème. J'attends toujours son coup de fil pour savoir retard, je dois appeler moi."
```

**Score COMMUNICATION: 70 pts** (zone "acceptable, répond mais pas toujours alert")

*Justification:* Réactivité 2-4h acceptable, mais proactivité très faible (25%). Pas d'alerte préalable = Angélique doit appeler elle. Relation professionnelle correcte, pas chaleureuse.

---

### Calcul Final

```
Score DÉLAI:       40 pts × 30% = 12 pts
Score QUALITÉ:     60 pts × 25% = 15 pts
Score FLEXIBILITÉ: 65 pts × 25% = 16,25 pts
Score COMMUNICATION: 70 pts × 20% = 14 pts
─────────────────────────────────────
SCORE FINAL: 57,25 / 100
```

### Classification & Décision

**Tier: RISQUE (<60)**

Raison: Combinaison délai défaillant (40 pts) + qualité limite (60 pts, incident client) + flexibilité faible (65 pts) entraîne score <60.

### Actions à Prendre (Réunion PDG-Angélique)

**Décision:** Mise en demeure 30 jours + RFQ remplacement lancé en background

**Plan d'action écrit pour Éméris (30 jours):**

1. **Délai:** Améliorer ponctualité 67% → 85% min
   - Raison: Retard <2j trop fréquent, limite notre service client
   - Action concrète: Engagement écrit "J+5 en ±48h fenêtre sinon avoir proportionnel €X"
   - Mesure Angélique: Weekly tracking (appel mardi 10h chaque semaine pour confirmer stock)
   - Target: 85% on-time dans 30 jours (J5-15j de janvier 2026)

2. **Flexibilité:** MOQ ajusté 2t → 1t minimum
   - Raison: Gedimat a projets client urgence petits volumes, MOQ 2t = refus service
   - Action concrète: "Acceptez 1t minimum commandes, surcoût +€50/cmd autorisé"
   - Mesure Angélique: Confirmer nouvelle MOQ par email écrit

3. **Qualité:** Audit emballage humidité
   - Raison: Incident client tuiles humides = réputation risque
   - Action concrète: "Investissez packaging anti-humidité pour palette, coût Éméris ou partagé"
   - Mesure Angélique: Inspecter 1ère livraison janvier, photos contrôle qualité

**Résultat 30j (15 janvier 2026):** Re-scoring 3 critères (Délai, Flexibilité, Qualité)
- Si ≥70 pts: Reconduire contrat avec nouvelles conditions
- Si 60-69 pts: Prolonger 30j supplémentaires avec conditions dures
- Si <60 pts: Rupture contrat, bascule fournisseur backup identifié (RFQ en cours)

**RFQ Remplacement lancé parallèlement:**
- Appel 3 fournisseurs tuiles alternatifs (demain 17 nov)
- Devis délai 5j, MOQ 1t, qualité, flexibilité urgence
- Comparaison tableau (délai/prix/conditions) semaine du 20 nov
- Signature contrat backup si Éméris ne s'améliore pas J+30

**Communication Éméris:**
- Email PDG + Angélique vendredi (17 nov): "Discussion relation Gedimat-Éméris"
- Appel PDG lundi (20 nov, 14h) avec responsable Éméris (pas email, appel direct)
- Message clair: "Partenariat stratégique MAIS amélioration requise 30 jours sinon remplacement"

---

## 5. EXCEL TEMPLATE STRUCTURE

### Sheet 1: Scoring Input (Grille Saisie Données)

**Colonnes par fournisseur:**

```
A: Fournisseur Name
B: Catégorie Produit (Tuiles, Ciment, Transport, etc.)
C: Délai Promis Usuel (jours)

DÉLAI (30% poids):
D: Nb Livraisons 3 mois
E: Nb Livraisons On-Time (±48h)
F: % Ponctualité (E/D)
G: Délai Score 0-100 (lookup table % → pts)

QUALITÉ (25% poids):
H: Nb Incidents Total
I: Nb Incidents Mineur (vs. Majeur)
J: Taux Conformité % ((D-H)/D)
K: Qualité Score 0-100

FLEXIBILITÉ (25% poids):
L: Demandes Urgence J+3
M: Urgence Acceptées
N: % Acceptation Urgence (M/L)
O: MOQ Pratique (kg)
P: Flexibilité Score 0-100

COMMUNICATION (20% poids):
Q: Tempo Réponse Moyen (heures)
R: % Alertes Proactives
S: Tonalité Relation (Sympa +10, Neutre 0, Difficile -10)
T: Communication Score 0-100

CALCUL FINAL:
U: Score Pondéré = (G×0.3 + K×0.25 + P×0.25 + T×0.2)
V: Tier (IF U≥80 "PRÉFÉRÉ", IF U≥60 "STANDARD", "RISQUE")
W: Couleur Alerte (Red <60, Yellow 60-79, Green ≥80)
```

**Format pratique:**
- Lignes = Fournisseurs (10-20 fournisseurs scorés)
- Données saisies manuellement par Angélique 15-30 min avant réunion trimestrielle
- Lookup tables: % ponctualité → score points (table prédéfinie)
- Formule Excel automatique: score final = somme pondérée
- Visualisation: Barre graphique score (rouge/jaune/vert par fournisseur)

---

### Sheet 2: Tendance Historique (4 Trimestres)

**Structure:**

```
Colonne A: Fournisseur
Colonne B: Q4 2024 Score
Colonne C: Q1 2025 Score
Colonne D: Q2 2025 Score
Colonne E: Q3 2025 Score
Colonne F: Q4 2025 Score

Calcul automatique:
- Moyenne 4 trimestres (stabilité)
- Tendance (flèche ↑ si +5pts, ↓ si -5pts)
- Couleur: Rouge si trend négatif 2+ trimestres

Exemple Éméris:
Q4 2024: 75 (STANDARD)
Q1 2025: 73 (STANDARD, -2)
Q2 2025: 71 (STANDARD, -2) ⚠️ Trend baisse
Q3 2025: 68 (STANDARD, -3) ⚠️⚠️ Alerte
Q4 2025: 57 (RISQUE, -11) 🔴 Critique
Moyenne: 68,8 → "Trend baisse marquée" → RFQ remplacement lancé
```

**Utilité:**
- Identifier fournisseur en dégradation progressive (action préventive)
- Valider reconnaissance fournisseur stabilisé en PRÉFÉRÉ (2+ trimestres ≥80)
- Justifier remplacement: "Éméris score 57 après trend 68→57 depuis 12 mois"

---

### Sheet 3: Action Plans (Risk Tier)

**Structure:**

```
Colonne A: Fournisseur (Risk <60)
Colonne B: Trigger Score Q
Colonne C: Critère Principal Weakness (Délai? Qualité? Flexibilité?)
Colonne D: Action Plan Écrit (texte 2-3 lignes)
Colonne E: Date Mise en Demeure
Colonne F: Target Score Q+1 (ex: 70 pts min)
Colonne G: Follow-up Status

Exemple Éméris:
- Trigger: Q4 2025 score 57
- Weakness: Délai (40 pts) + Flexibilité (65 pts)
- Action: "Délai J+5±48h garanti, MOQ 1t accepté, weekly call mardi 10h"
- Mise en Demeure: 17 nov 2025
- Target: 70 pts (min STANDARD)
- Follow-up: Status "1ère semaine OK, délai holding"
```

**Utilité:**
- Tracker fournisseur problématique (qui est au plan d'action?)
- Documentation RH si rupture contrat future (justification écrite)
- Rappel PDG-Angélique: "Éméris ultimatum expire 17 décembre, decision jeudi 14 dec"

---

## 6. PROCESSUS REVIEW TRIMESTRIEL (2h Meeting PDG + Angélique)

### Agenda Type (2 heures)

**Timing:**
- 1ère semaine de Q+1 (ex: Q4 2025 review = semaine du 12-16 janvier 2026)
- Mercredi 14h-16h (fixe chaque trimestre)
- Lieu: Bureau PDG (confidentialité fournisseurs)
- Préparation: Angélique prépare Excel + notes scoring 1 jour avant

**Format réunion:**

**0:00-0:10 (10 min) - Opening & Context**
- PDG relit résumé trimestre précédent (actions à suivre?)
- Angélique résume "climat fournisseurs" (retards? crises? bon climat?)
- Vérifier absence changement majeur (ex: nouveau fournisseur ajouté)

**0:10-1:20 (70 min) - Scoring Review (5-7 fournisseurs top priorité)**

*Par fournisseur Top 5-7 (10-15 min each):*

1. **Présentation données:**
   - Score final Q4
   - Tier classification (Préféré/Standard/Risque)
   - Tableau tendance 4 trimestres (trend up/down?)

2. **Analyse scoring par critère:**
   - Quelle critère tire le score down? (Délai? Qualité?)
   - Raison concrète (Angélique contexte): "Éméris retard = stock limité, pas capacité augmentation"
   - Data anecdotique: "Incident oct (palette endommagée) résolu 2j, bon service"

3. **Décision action:**
   - Si PRÉFÉRÉ: "Reconduire contrat, offrir meilleur prix (-€500/an)?"
   - Si STANDARD: "Monitoring OK, réunion amélioration si score baisse Q+1"
   - Si RISQUE: Décision type/alternativ remplacement? "Lancez RFQ tuiles alternatif cette semaine"

4. **Minutes décision:**
   - PDG valide action → Angélique notes "décision: reconduire vs. renegocier vs. replacement"
   - Owner follow-up: "Angélique: email Éméris plan amélioration jeudi"
   - Timing: "Re-score janvier 15, appel mardi 10h chaque semaine suivi"

**1:20-1:50 (30 min) - Risk Tier Management**

*Pour fournisseur Risque <60:*
- Review plan d'action précédent (amélioré? pas?)
- Nouvelles demandes RFQ lancées? (combien de dossiers?)
- Timeline switch: "Si pas amélioration, switch date cible décembre 31"
- Budget risk: "Perte Éméris = impact? Avons-nous backup stock? Délai client?"

**1:50-1:55 (5 min) - Preferred Tier Recognition**

*Fournisseur ≥80:*
- Brief recognition (qui mérite bonus/prix meilleur?)
- "Éméris tuiles non, mais si Éméris ciment 90pts → accord prix meilleur Q+1"

**1:55-2:00 (5 min) - Close & Next Steps**

- Angélique: "Confirmez 3 actions priorité cette semaine?"
- PDG: "Validez minutes décisions" (email suivi)
- Calendar: "Prochaine réunion 15 avril?" (Q2 review fixé)

---

### Output Documents (Email à PDG + Dossier conservé)

**1. Excel updated (Angélique copie nouvelle ligne Q4 2025)**
- Envoyé à PDG vendredi 17 jan (jour après réunion)
- Format: Color codes (Red/Yellow/Green) visibles d'un coup d'oeil
- Historique: 4 trimestres visibles = trend clair

**2. Minutes Décisions (Document Word simple)**
```
═══════════════════════════════════════════════════════════════
RÉUNION REVIEW FOURNISSEURS Q4 2025
16 janvier 2026 | PDG + Angélique | Durée 2h
───────────────────────────────────────────────────────────────

DÉCISIONS PRISES:

1. ÉMÉRIS TUILES
   Score Q4: 57/100 (RISQUE)
   Tier: RISQUE → Mise en demeure 30 jours
   Action: Plan amélioration (Délai J+5±48h, MOQ 1t, weekly calls)
   Timeline: RFQ backup tuiles lancé, decision 17 décembre
   Owner: Angélique, appel PDG lundi 20 jan 14h

2. CIMENT SUPPLIER XYZ
   Score Q4: 78/100 (STANDARD)
   Trend: +3 pts vs Q3 (improvement!)
   Action: Monitoring OK, meeting amélioration si >60
   Owner: Angélique, next check avril

[... autres fournisseurs ...]

───────────────────────────────────────────────────────────────
QUESTIONS OUVERTES / FOLLOW-UP:
- RFQ tuiles: 3 fournisseurs contactés, devis jeudi 18 jan?
- Éméris réaction email plan? Follow-up call lundi
- Backup stock ciment si Éméris out: oui, 2 mois buffer secured

───────────────────────────────────────────────────────────────
Next Review: 15 avril 2026 (Q2 2025)
═══════════════════════════════════════════════════════════════
```

**3. Action Tracker (simple list)**
- Qui: Angélique
- Quoi: Email plan Éméris, RFQ tuiles, appel lundi PDG Éméris
- Par quand: Cette semaine (17-21 jan)
- Status: ☐ Todo, ☐ In Progress, ✓ Done

---

## 7. BONNES PRATIQUES & PIÈGES À ÉVITER

### Ce Qu'il Faut Faire

✅ **Scope data:** Minimum 10 livraisons 3 mois pour score crédible
✅ **Séparer Doutes:** Force majeure (grève, météo) ≠ fournisseur failure
✅ **Documenter Contexte:** "Retard oct car Éméris stock épuisé" = important pour négociation
✅ **Communication Constructive:** "Éméris, score baisse délai 40pts, besoin J+5±48h" (factual) vs. "tu es mauvais" (accusatoire)
✅ **RFQ Proactif:** Lancer backup dès Risk <60, pas attendre rupture urgente
✅ **Trend Monitoring:** Baisse progressive 75→70→65 = action dès 70pts (avant RISQUE)
✅ **Confidentialité:** Scores Éméris ≠ show to Ciment supplier (competitif info)

### Pièges À Éviter

❌ **Subjectivité Pure:** Scoring Angélique émotionnel sans data ("j'aime pas Éméris") = invalide
❌ **Cherry-picking Data:** Prendre seulement bonne semaine pour score meilleur = fraude
❌ **Ignorer Trend:** Score stable 60pts OK trimestre = danger si trend 75→65→60
❌ **Abus Plan d'Action:** Ne pas lancer RFQ backup, juste ultimatum "improve ou else" sans altern
❌ **Fusion Critères:** Compter retard dans qualité (sont indépendants) = double-punish
❌ **Oubli Communication:** Ne pas prévenir fournisseur score baisse = surpris rupture contrat

---

## 8. INTÉGRATION AVEC AUTRES PROCESSUS

### Lien CRM Relationnel

**Carnet Relationnel (PASS4 Agent5) ↔ Scoring Fournisseurs:**
- Carnet = contact principal + accords formalisés (SLA, tarif)
- Scoring = évaluation périodique respect accords
- Exemple: "Carnet dit SLA 5j promis → Score mesure 67% respect → Action plan J+5±48h"

### Lien Achat/Commande

**Système commandes → Scoring data:**
- BDC (bon de commande) = enregistre date promis (baseline délai)
- Bon livraison = enregistre date réception
- CRM = alerte si retard, log incidents qualité
- Tri-mensuel: Angélique extrait 3 mois historique → scoring

### Lien Gestion Client

**Incident client impact scoring fournisseur:**
- Si client reçoit produit défectueux (Éméris humidité) = score qualité fournisseur baisse
- If client souffre retard Éméris (project delay) = escalade PDG potentielle

---

## RÉSUMÉ IMPLÉMENTATION

**Phase 1 (Semaine 1):** Angélique crée Excel template (sample 3 fournisseurs)
**Phase 2 (Semaines 2-4):** Data collection 3 mois octobre-décembre (rétro-scoring)
**Phase 3 (Semaine 5):** Réunion PDG-Angélique (2h, scoring Q4 2025)
**Phase 4 (Ongoing):** Trimestriel (chaque semaine 1 Q+1)

**Bénéfices:**
- Objectivité renegociation ("Score 57, data dit ceci")
- Détection précoce problème fournisseur (trend 75→65→55 = alerte Q2)
- Documentation pour succession Angélique (scoring clair si elle part)
- Justification coûts: "RFQ remplacement lancé car Éméris score RISQUE <60"

---

**Rédigé:** 16 novembre 2025
**Responsable:** Pass 7 - Tool 5 (Supplier Scoring Expert)
**Source données:** PASS4_AGENT5_CRM_RELATIONNEL_KNOWLEDGE.md (sections scoring)
**Status:** ✅ Prêt déploiement Excel + réunion Q4 2025
**Propriétaire Process:** Angélique (collecte) + PDG (validation) Tri-mensuel
