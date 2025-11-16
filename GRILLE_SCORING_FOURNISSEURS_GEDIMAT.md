# GRILLE DE SCORING FOURNISSEURS GEDIMAT

**Outil opérationnel pour évaluation performance et continuité | Mise à jour mensuelle**

---

## 1. MODÈLE DE CALCUL - 4 CRITÈRES

### Critère 1 : FIABILITÉ DÉLAI (Poids 40%)

**Définition :** % de livraisons reçues à la date convenue ou avant (délai commandé)

**Formule :**
```
Score = (Livraisons on-time / Total livraisons) × 100
```

**Collecte données :**
- Date commandée (ETA convenu)
- Date livraison réelle
- Comptage mensuel dans logiciel ou Excel
- Seuil alerte : >3 jours de retard = incident enregistré

**Cible :** >90% (1 retard maximum pour 10 livraisons)

**Scoring points :**
| Performance | Points |
|---|---|
| 95-100% | 100 |
| 90-94% | 90 |
| 85-89% | 75 |
| 80-84% | 60 |
| <80% | 40 |

**Notes contexte à documenter :**
- Exemple : « 9/10 à l'heure = 90% | Retard 1 livraison = raison transports (tempête) »
- Tendance : « Fiabilité stable depuis 6 mois » vs « Dégradation depuis juillet »

---

### Critère 2 : QUALITÉ PRODUIT (Poids 25%)

**Définition :** % de retours/défauts qualité par rapport au total livré

**Formule :**
```
Score = (1 - (Retours qualité / Total quantité livrée)) × 100
```

**Collecte données :**
- Tickets retour (notes de retour dans logiciel)
- Classification : défaut fabrication, casse transport, packaging, autre
- Comptage trimestriel (données moins granulaires)
- Incluire : produits incomplets, endommagés, non conformes spécifications

**Cible :** <2% de retour (19/20 produits OK)

**Scoring points :**
| Retour % | Points |
|---|---|
| 0-1% | 100 |
| 1-2% | 90 |
| 2-3% | 70 |
| 3-5% | 50 |
| >5% | 30 |

**Notes contexte :**
- Exemple : « 1.5% retour | 2 retours sur 130 kg livrés »
- Cause retours : « Emballage faible, 1x produit défaut usine »
- Tendance : « Stable depuis 6 mois » vs « Dégradation (packaging nouveau) »

---

### Critère 3 : RÉACTIVITÉ INCIDENTS (Poids 20%)

**Définition :** Temps moyen de résolution d'un problème signalé (de l'appel à la solution)

**Formule :**
```
Score = 100 - ((Temps résolution moyen - 48h) / 48h × 100)
Score capped à 100 si <48h, capped à 30 si >5 jours
```

**Collecte données :**
- Heure d'appel client/Gedimat
- Heure de résolution (remplacement envoyé, remboursement, correction)
- Comptage trimestriel (ou mensuel si incidents nombreux)
- Incluir : délai transport + délai réaction fournisseur

**Cible :** <48h de résolution moyenne

**Scoring points :**
| Temps résolution moyen | Points |
|---|---|
| 0-24h | 100 |
| 24-48h | 90 |
| 48-72h | 70 |
| 72h-5j | 50 |
| >5j | 30 |

**Notes contexte :**
- Exemple : « Incident retard = résolu en 36h (deuxième transport en urgence) »
- Détail : « 4 incidents résolus en 32h moy | Réactivité excellente »
- Tendance : « Amélioration depuis accord escalade directe avec Mélissa »

---

### Critère 4 : FLEXIBILITÉ (Poids 15%)

**Définition :** % d'acceptation des demandes exceptionnelles (urgences, petites quantités, modifications)

**Formule :**
```
Score = (Demandes acceptées / Total demandes exceptionnelles) × 100
```

**Collecte données :**
- Liste demandes d'urgence, quantités minimum, changements commande
- Date demande + réponse + résultat
- Comptage trimestriel

**Cible :** >80% d'acceptation (4/5 urgences acceptées)

**Scoring points :**
| Taux acceptation | Points |
|---|---|
| 90-100% | 100 |
| 80-89% | 90 |
| 70-79% | 70 |
| 50-69% | 50 |
| <50% | 30 |

**Notes contexte :**
- Exemple : « Mélissa accepte 5/5 urgences ce trimestre = parfait »
- Détail : « 3 urgences 48h acceptées, 1 refusée (capacité), 1 modifiée (coût +15%) »
- Limite connue : « Refuse les quantités <50kg sauf regroupement »

---

## 2. MODÈLE DE GRILLE - FORMAT EXCEL/GOOGLE SHEETS

### Structure simplifiée (Mise à jour chaque fin de mois)

```
┌────────────────────────────────────────────────────────────────────────┐
│ SCORING FOURNISSEURS GEDIMAT - NOVEMBRE 2025                           │
│ Mise à jour : 2 novembre | Période : Nov-2025 | Resp. : Manager        │
└────────────────────────────────────────────────────────────────────────┘

FOURNISSEUR : Médiafret (Transporteur)
═══════════════════════════════════════════════════════════════════════

Critère                  │ Données Mois    │ Cible  │ Points │ Pondér │ Contrib.
─────────────────────────┼─────────────────┼────────┼────────┼────────┼─────────
Fiabilité délai (40%)    │ 23/25 livraisons│ >90%   │  92    │ 0.40   │  36.8
                         │ à l'heure       │        │        │        │
Qualité produit (25%)    │ 0 retours       │ <2%    │ 100    │ 0.25   │  25.0
                         │ sur 250kg       │        │        │        │
Réactivité incidents(20%)│ 24h moy (2x)    │ <48h   │  98    │ 0.20   │  19.6
                         │ sur 2 incidents │        │        │        │
Flexibilité (15%)        │ 3/3 urgences    │ >80%   │ 100    │ 0.15   │  15.0
                         │ acceptées       │        │        │        │
─────────────────────────┴─────────────────┴────────┴────────┴────────┼─────────
SCORE TOTAL MENSUEL                                                     │  96.4
ÉTAT SANTÉ                                            ████████████░░░░ │ ✓✓✓✓✓
─────────────────────────────────────────────────────────────────────────┴─────────

Contexte Notes :
  • Excellent service stable | Partenaire stratégique
  • Pas d'incident majeur ce mois
  • Augmentation tarifaire : +3% depuis octobre (inflation transposts)

Tendance 6 mois : 96 → 96 → 94 → 95 → 96 → 96 = STABLE EXCELLENT
```

---

### Format détaillé (Colonnes Excel complètes)

```
A          | B           | C         | D          | E         | F      | G      | H
Fournisseur│ Fiabilité % │ Qual %ret │ Réactiv(h) │ Flexib %  │ Points │ Seuil  │ Statut
───────────┼─────────────┼───────────┼────────────┼───────────┼────────┼────────┼────────
Médiafret  │ 92          │ 0         │ 24         │ 100       │ 96.4   │ >85    │ ✓✓✓✓
Emeris     │ 62          │ 2.5       │ 48         │ 75        │ 68.2   │ 70-85  │ ⚠️ RISQUE
Saint-Germ │ 85          │ 1.8       │ 36         │ 80        │ 81.1   │ 70-85  │ ✓ OK
[Autres]   │ ...         │ ...       │ ...        │ ...       │ ...    │ ...    │ ...
```

---

## 3. FOURNISSEURS GEDIMAT - GRILLE PRÉCALCULÉE (NOVEMBRE 2025)

### FOURNISSEUR 1 : Médiafret (Transporteur)

```
╔════════════════════════════════════════════════════════════════╗
║ MÉDIAFRET - SCORING NOVEMBRE 2025                              ║
║ Contact : Mélissa | Relation : 4+ ans | Criticité : TRÈS ÉLEVÉE║
╚════════════════════════════════════════════════════════════════╝

MÉTRIQUES MENSUELLES
┌──────────────────────────┬──────────────────────────────────┐
│ Fiabilité délai          │ 92% (23/25 livraisons on-time)   │
│ Qualité produit          │ 0% retour (250kg sans réclamation)
│ Réactivité incidents     │ 24h moyen (2 incidents résolus)   │
│ Flexibilité              │ 100% (3/3 urgences acceptées)     │
└──────────────────────────┴──────────────────────────────────┘

CALCUL DU SCORE
(0.92 × 40%) + (1.00 × 25%) + (0.98 × 20%) + (1.00 × 15%) = 96.4 / 100

INTERPRÉTATION
✓ EXCELLENT - Partenaire stratégique à maintenir
  • Stable depuis 6 mois (96-96-94-95-96-96)
  • Pas d'incident majeur
  • Flexibilité remarquable sur urgences

RISQUES IDENTIFIÉS
  ⚠ Augmentation tarifaire +3% (inflation transports)
  ⚠ Dépendance Mélissa (contact clé) → Documenter redondant

ACTION
  → Maintenir excellence | Renegociation tarifaire Q1 2026
  → Créer contact secondaire (superviseur équipe)
  → Envisager accord long-terme (rabais volume)
```

---

### FOURNISSEUR 2 : Emeris (Tuiles - Matériaux toit)

```
╔════════════════════════════════════════════════════════════════╗
║ EMERIS - SCORING NOVEMBRE 2025                                 ║
║ Contact : [À documenter] | Relation : 2+ ans | Criticité : ÉLEVÉE
╚════════════════════════════════════════════════════════════════╝

MÉTRIQUES TRIMESTRIELLES (Septa-Oct-Nov)
┌──────────────────────────┬──────────────────────────────────┐
│ Fiabilité délai          │ 62% (13/21 livraisons on-time)   │
│ Qualité produit          │ 2.5% retour (6 retours/240kg)    │
│ Réactivité incidents     │ 48h moyen (3 incidents, max 72h)  │
│ Flexibilité              │ 75% (3/4 urgences acceptées)      │
└──────────────────────────┴──────────────────────────────────┘

CALCUL DU SCORE
(0.62 × 40%) + (0.975 × 25%) + (0.70 × 20%) + (0.75 × 15%) = 68.2 / 100

INTERPRÉTATION
⚠️ RISQUE - Action amélioration requise
  • Score <70 = Seuil critique
  • Fiabilité faible (62% vs cible 90%)
  • Qualité limite (2.5% vs cible <2%)

CAUSE RACINE
  Préparation commande lente (pas logistique Emeris)
  Problème qualité : emballage faible → casse en transport

ACTION REQUISE
  → RÉUNION AMÉLIORATION immédiate
  → Plan d'action 90j (Janvier 2026 évaluation)
    ☐ Emeris ajoute 1 jour avance buffer = cible 90%+
    ☐ Améliorer packaging (spécifier fournisseur)
    ☐ Accepter urgences <48h minimum 80%
  → Lancer recherche alternative en parallèle (Saint-Germaire ?)
  → Si non atteint Jan 2026 → Dual sourcing ou changement
```

---

### FOURNISSEUR 3 : Saint-Germaire (Matériaux généraux)

```
╔════════════════════════════════════════════════════════════════╗
║ SAINT-GERMAIRE - SCORING NOVEMBRE 2025                         ║
║ Contact : [À documenter] | Relation : 1+ ans | Criticité : MOYENNE
╚════════════════════════════════════════════════════════════════╝

MÉTRIQUES TRIMESTRIELLES
┌──────────────────────────┬──────────────────────────────────┐
│ Fiabilité délai          │ 85% (17/20 livraisons on-time)   │
│ Qualité produit          │ 1.8% retour (4 retours/220kg)    │
│ Réactivité incidents     │ 36h moyen (2 incidents)           │
│ Flexibilité              │ 80% (4/5 urgences acceptées)      │
└──────────────────────────┴──────────────────────────────────┘

CALCUL DU SCORE
(0.85 × 40%) + (0.982 × 25%) + (0.75 × 20%) + (0.80 × 15%) = 81.1 / 100

INTERPRÉTATION
✓ BON - Continuer partenariat, suivi régulier
  • Score dans zone saine (70-85)
  • Fiabilité acceptable (85% vs cible 90%)
  • Qualité très bonne (1.8%)

POINTS POSITIFS
  • Réactivité rapide (36h)
  • Flexibilité bonne (4/5 urgences)
  • Relation stable

OPPORTUNITÉ
  → Fournisseur alternatif potentiel si Emeris continue de décrocher
  → Envisager test volume supplémentaire (tuiles au lieu Emeris)
  → Documenter contact secondaire pour redondance

SUIVI
  → Réunion satisfaction Q1 2026 (identifier axes amélioration)
  → Cible : atteindre 85+ fiabilité délai
```

---

## 4. ACTIONS SELON SEUIL DE SCORE

### Tableau décisionnel

```
┌────────┬─────────────────────────────────┬────────────────────────────────┐
│ Score  │ Statut                          │ Action Requise                  │
├────────┼─────────────────────────────────┼────────────────────────────────┤
│ ≥85    │ ✓ EXCELLENT                     │ • Maintenir relation            │
│        │ Partenaire stratégique          │ • Reconnaître service           │
│        │                                 │ • Envisager long-terme          │
│        │                                 │ • Suivi annuel                  │
├────────┼─────────────────────────────────┼────────────────────────────────┤
│ 70-84  │ ✓ BON                           │ • Continuer partenariat         │
│        │ Fournisseur stable              │ • Réunion satisfaction tri-ann. │
│        │                                 │ • Identifier axes amélioration  │
│        │                                 │ • Monitorer tendance            │
├────────┼─────────────────────────────────┼────────────────────────────────┤
│ 60-69  │ ⚠️ RISQUE                        │ • RÉUNION AMÉLIORATION URGENT   │
│        │ Dégradation probable            │ • Plan d'action 90j             │
│        │                                 │ • Identifier cause racine       │
│        │                                 │ • Recherche alternative         │
│        │                                 │ • Réévaluation après 90j        │
├────────┼─────────────────────────────────┼────────────────────────────────┤
│ <60    │ ✗ CRITIQUE                      │ • ESCALADE DIRECTION IMMÉDIATE  │
│        │ Partenaire défaillant           │ • 30j ultimatum amélioration    │
│        │                                 │ • Lancer DUAL SOURCING          │
│        │                                 │ • Préparer transition           │
│        │                                 │ • Réévaluation fin 30j          │
└────────┴─────────────────────────────────┴────────────────────────────────┘
```

---

## 5. TEMPLATE RÉUNION AMÉLIORATION (Score 60-69)

### Checklist de réunion

```
RÉUNION AMÉLIORATION FOURNISSEUR
Date : [Date] | Fournisseur : [Nom] | Score actuel : [X/100]

PARTICIPANTS
□ Manager Gedimat
□ Contact principal fournisseur
□ Angélique (Coordination) - si possible

AGENDA (60 minutes)

1. PRÉSENTATION SCORE (10 min)
   □ Afficher score 60-69 et tendance
   □ Expliquer 4 critères
   □ Clarifier cause faiblesse principale

2. DIAGNOSTIC PARTAGÉ (20 min)
   □ Quels sont les vrais obstacles ?
   □ Fournisseur : problème capacité, ressource, processus ?
   □ Gedimat : attentes réalistes ?

3. PLAN D'ACTION 90J (20 min)
   □ Objectif cible (ex: Fiabilité 90%+ délai)
   □ Actions spécifiques (ex: buffer +1j, nouvelle équipe)
   □ Mesure de succès (comment on sait que c'est ok)
   □ Fréquence reporting (hebdo vs bihebdo)

4. ENGAGEMENT RÉCIPROQUE (5 min)
   □ Fournisseur s'engage sur actions
   □ Gedimat s'engage sur support/délais
   □ Date réévaluation (90j = Février)

5. SUIVI POST-RÉUNION (5 min)
   □ Email recap envoyé j+1
   □ Calendrier suivi hebdo confirmé
```

### Template email de synthèse

```
Objet : Réunion amélioration Emeris - Plan d'action 90j

Cher [Contact],

Merci pour la réunion du [date]. Voici la synthèse de notre discussion :

SCORE ACTUEL : 68.2/100 (Objectif : >75 fin février)

ACTIONS REQUISES
1. Préparation commandes : Ajouter 1 jour buffer logistique
   ☐ Emeris : Nouveau processus opérationnel en place (31 déc)
   ☐ Mesure : Réduction retards de 62% → 90%

2. Qualité packaging : Améliorer emballage tuiles
   ☐ Emeris : Nouveau fournisseur packaging testé (15 jan)
   ☐ Mesure : Réduction retours de 2.5% → <1.5%

3. Flexibilité urgences : Accepter 80%+ des demandes 48h
   ☐ Emeris : Réserver capacité (min 2h/semaine)
   ☐ Mesure : Suivi demandes urgences vs acceptations

REPORTING
Chaque lundi 14h : Call 15 min (Mélissa + vous) suivi progrès

RÉÉVALUATION : Février 2026 (Nouveau score de 90j)
Si score ≥75 → Continuation | Si <75 → Alternative considérée

Cordialement,
[Manager Gedimat]
```

---

## 6. DASHBOARD SYNTHÈSE - Vue DIRECTION

```
╔═══════════════════════════════════════════════════════════════════╗
║ SYNTHÈSE SCORING FOURNISSEURS - NOVEMBRE 2025                    ║
║ Responsable : Manager Logistique | Période : Nov 2025            ║
╚═══════════════════════════════════════════════════════════════════╝

RÉSUMÉ PERFORMANCE GLOBALE
┌────────────────────────────────────────────────────────────────┐
│ Nombre fournisseurs suivi   : 10                               │
│ Score moyen                 : 78.5/100                         │
│ Fournisseurs Excellent (≥85): 3 (30%)                          │
│ Fournisseurs Bon (70-84)    : 5 (50%)                          │
│ Fournisseurs Risque (60-69) : 1 (10%) → Emeris ⚠️             │
│ Fournisseurs Critique (<60) : 1 (10%) → [Nom] 🔴             │
└────────────────────────────────────────────────────────────────┘

ACTIONS REQUISES IMMÉDIATE
├─ Réunion Emeris : Semaine 1 déc (Score 68 → Plan 90j)
├─ Recherche alternative : Saint-Germaire test (tuiles)
├─ Escalade fournisseur <60 : Discussion alternatives fin nov

TENDANCE 6 MOIS
  Nov 2025 : 78.5 ▼ (↓0.2 vs oct)
  Oct 2025 : 78.7
  Sep 2025 : 79.2
  Août 2025: 79.8
  Juil 2025: 80.1
  Juin 2025: 80.5

  Analyse : Légère dégradation (inflation coûts + nouveau retard Emeris)
  Action : Réunions amélioration trimestrielles confirmées
```

---

**Document opérationnel | Mise à jour mensuelle 1er lundi du mois | Version 1.0**
