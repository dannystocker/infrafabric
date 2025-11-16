# PASS 2 - AGENT 2: Data Gaps & Validation Checklist
## Identification Des Manques Pour Affiner L'Analyse Coûts

**Date:** 16 novembre 2025
**Audience:** Direction générale, Angélique, Équipes opérationnelles
**Objectif:** Clarifier données manquantes et plan de collecte pour Phase 3

---

## RÉSUMÉ EXÉCUTIF

Cette analyse coûts repose sur **estimations prudentes + benchmarks secteur**.

**Confiance globale: Moyen (±25-35%)**

**Facteurs limitants:**
1. ❌ Pas d'accès factures Médiafret réelles (estimation ±€30k plage)
2. ❌ Pas de données mileage chauffeurs (estimation ±€10k)
3. ❌ Pas d'audit CRM pertes commandes (estimation ±€15k)
4. ❌ Pas d'analyse time tracking Angélique (estimation ±€10k)
5. ❌ Pas de WMS détaillé (surstock buffer estimé ±€5k)

**Impact:** Coûts totaux estimés €152-249k avec écart-type ±€40k

**Solution:** Collecte data systématique semaines 1-4, recalcul mois 2

---

## SECTION 1: DONNÉES CRITIQUES (IMPACT >20% ANALYSE)

### 1.1 Factures Médiafret (CRITIQUE: 40% budget)

**Ce qui manque:**

```
Demander à: Direction générale / Comptabilité
Format: Fichier Excel ou PDF 6 derniers mois
Détails requis par facture:
  - Date enlèvement
  - Fournisseur (lieu d'enlèvement)
  - Tonnage exact
  - Destinations (quel dépôt)
  - Coût enlèvement (€)
  - Coût additionnels (urgence, zone, retard)
  - Sous-traitants impliqués? (visibilité)
  - Délai livraison effectif vs prévu

Calculs à valider:
  ✓ Coût moyen €/tonne par tranche tonnage
  ✓ Coût moyen €/km (distance enlèvement)
  ✓ Premium urgence réel vs hypothèse +30%
  ✓ Surcharges zone (Île-de-France vs provinces)
  ✓ Fréquence retards, pénalités appliquées?
  ✓ Marges Médiafret (si sous-traitants = visibilité coûts réels)

Gain precision: Écart actuellement ±€30k → ±€5k (si data complète)
```

**Template collecte à créer:**

| Date | Fournisseur | Tonnage | Dépôt Dest. | Distance Km | Coût € | Type | Retard? |
|------|------|------|------|------|------|------|------|
| 2025-11-01 | Émeris | 15 | Gisors | 50 | 220 | Standard | Non |
| 2025-11-02 | Ediliens | 12 | Méru | 60 | 200 | Standard | Oui +2h |
| ... | | | | | | | |

---

### 1.2 Données Chauffeurs Internes (CRITIQUE: 20% budget)

**Ce qui manque:**

```
Demander à: RH / Gestionnaire paie
Format: Tableaux Excel, confidentialité assurée

PAR CHAUFFEUR:
  - Salaire brut annuel
  - Charges sociales (%)
  - Primes/avantages (essence, repas, risque)
  - Contrat (CDI, CDD, temps partiel %)
  - Heures travail réelles (vs théorique)
  - RTT jours pris (vs droits)
  - Congés spéciaux (formation, maladie)

PAR MOIS / TRIM (si possible):
  - Kilométrage réel (tachygraphe, GPS, ou estimation)
  - Tonnage transporté
  - Nombre enlèvements
  - Heures par fonction (fournisseur vs client vs navette vs inactif)

Calculs à valider:
  ✓ Coût complet chauffeur €/an (salarial + frais)
  ✓ Coût marginal €/tonne (exluant salarial fixe)
  ✓ Coût €/km réel vs hypothèse
  ✓ Utilisation: % temps produit vs inactif/administratif
  ✓ Capacité réelle: tonnage moyen par trajet vs hypothèse 7t
  ✓ Jours travail effectifs: vs hypothèse 220 jours

Gain precision: Écart actuellement ±€10k → ±€2k
```

**Template collecte:**

| Mois | Km Réels | Tonnage | Enlèvements | Heures Fournisseur | Heures Interne | Heures Navette | Heures Inactif |
|------|------|------|------|------|------|------|------|
| Oct | 3,200 | 45 | 12 | 80 | 20 | 10 | 8 |
| Nov | 2,800 | 38 | 10 | 75 | 25 | 8 | 12 |

---

### 1.3 Historique Incidents Clients (CRITIQUE: 10% budget "coûts cachés")

**Ce qui manque:**

```
Demander à: Responsable commercial / CRM / Manager dépôts
Format: Export CRM ou liste emails réclamations

RÉCLAMATIONS PASSÉES 6-12 MOIS:
  - Date incident
  - Client (nom, lieu)
  - Type incident (retard, dommage, rupture stock, mauvaise quantité)
  - Cause attribué (fournisseur retard? transport retard? coordination?)
  - Impact client (chantier arrêté? commande annulée? déplacée concurrent?)
  - Coût estimé (perte marge, compensation client, urgence transport)
  - Résolution (qui a payé? combien?)

COMMANDES PERDUES (annulées par client):
  - Fréquence: nombre/mois
  - Motif primaire: délai trop long? autre fournisseur moins cher? qualité?
  - Montant marge perdue/commande
  - Dépôt concerné

Calculs à valider:
  ✓ Nombre incidents réels vs hypothèse 2-4/an
  ✓ Cause distribution (fournisseur % vs transport % vs coordination %)
  ✓ Coût moyen incident réel vs hypothèse €800-1.2k
  ✓ Tendance: stable vs augmentant?
  ✓ Corrélation incidents ↔ dépôts spécifiques?

Gain precision: Écart actuellement ±€15k → ±€3k
```

**Template collecte:**

| Date | Client | Type | Cause | Chantier Impact | Coût € | Résolut. |
|------|------|------|------|------|------|------|
| 2025-09-15 | Macon X | Retard 3j | Transport retard | Oui, arrêt 1j | 500 | Compensation |
| 2025-10-02 | Entreprise Y | Rupture | Coord. mauvaise | Oui, changé fournisseur | 1200 | Perte client |

---

### 1.4 Localisation Fournisseurs Principaux (SECONDAIRE: 5-10% analyse)

**Ce qui manque:**

```
Demander à: Responsable achats / Angélique
Format: Fichier Google Sheets avec géolocalisation

TOP 15 FOURNISSEURS PAR VOLUME:
  - Nom fournisseur
  - Adresse complète (code postal)
  - Volume annuel estimé (tonnes)
  - Distance réelle fournisseur → Évreux (km)
  - Distance réelle fournisseur → Gisors (km)
  - Distance réelle fournisseur → Méru (km)
  - Horaires enlèvement (fenêtre d'accès)
  - Qualité délai (ponctuel? retards fréquents?)
  - Type matériau (tuiles? ciment? bois?)
  - Livrent-ils directement? (si oui: quand et coûts)

Utilité:
  ✓ Calculer distances réelles vs hypothèse
  ✓ Identifier milkrun opportunités (fournisseurs clusterisés)
  ✓ Évaluer coûts €/km réels vs benchmark
  ✓ Prioriser fournisseurs pour SLA négociation

Gain precision: Affine coûts routing ±5-10%
```

**Template collecte (Google Maps):**

| Fournisseur | Adresse | Volume/an | Dist Évreux | Dist Gisors | Dist Méru | Qualité Délai |
|------|------|------|------|------|------|------|
| Émeris | Montsouris, 75 | 500t | 48 | 72 | 95 | Modérée (retards 20%) |
| Ediliens | Beaumont, 95 | 400t | 55 | 60 | 88 | Bonne |

---

## SECTION 2: DONNÉES SECONDAIRES (IMPACT 10-20% ANALYSE)

### 2.1 Allocation Temps Angélique

```
Demander à: Angélique + RH
Méthode: Auto-pointage ou timesheet 4 semaines

DÉCOMPOSITION TÂCHES (heures/semaine):
  - Suivi fournisseurs (appels, emails, relances ARC)
  - Arbitrage dépôt (décisions, débats, résolutions conflit)
  - Gestion incidents (réclamations, escalades)
  - Coordination Médiafret (devis, suivi, reclamations retards)
  - Saisie données, rapports
  - Attentes (chargement, débourrage, administrative)

Validation hypothèse: Estimation 11-18h/semaine = réalité?

Bénéfice: Si automation réduit 30-40% temps = économie réelle €3-9k/an
```

---

### 2.2 Inventory Surstock & WMS Data

```
Demander à: Responsable dépôts ou WMS
Format: Rapport stock situation au 30 novembre 2025

PAR DÉPÔT:
  - Tonnage stock total actuel
  - Tonnage par catégorie (tuiles, ciment, bois, etc.)
  - Rotation moyenne (jours stock)
  - Estimation surstock "buffer défensif" (tonnes vs optimum)
  - Localisation buffer (quel dépôt défend le plus?)

Calculs à valider:
  ✓ Surstock estimé: 8-12k€ immobilisé?
  ✓ Coûts intérêt trésorerie (3%) = €240-360/an?
  ✓ Obsolescence/usure (2%) = €160-240/an?

Gain precision: Affirme ou réfute hypothèse surstock
```

---

## SECTION 3: DONNÉES TERTIAIRES (IMPACT <10%)

### 3.1 Contrats Médiafret & Fournisseurs

```
Demander à: Direction générale / Juridique
Utilité: Identifier SLA, pénalités, options contrats

Médiafret:
  - Tarifs selon tonnage (vérifier vs factures)
  - Durée engagement, clause révision prix
  - SLA délai (ex: "livraison J+2")
  - Pénalités retard (montant?)
  - Options sous-traitance (visible? coûts supplémentaires?)

Top 5 fournisseurs:
  - Délai de fabrication (ex: "ARC J+7 de commande")
  - Frais de transport (fournisseur paie? Gedimat?)
  - Pénalités retard (contrats spécifient?)

Utilité: Négocier SLA futurs, clarifier responsabilités
```

---

### 3.2 Saisonnalité & Patterns Demande

```
Demander à: Angélique / Manager commercial
Analyse: Data 12 derniers mois

Patterns:
  - Volumes par mois (été vs hiver)
  - Urgence patterns (% commandes J+1, flexible)
  - Consolidation opportunités par mois (varie?)
  - Fournisseur availability (blocages saisonniers?)

Utilité: Affiner modèles par saison, prévisions
```

---

## SECTION 4: PLANNING COLLECTE DATA

### SEMAINE 1 (URGENT - FIN NOVEMBRE)

**Responsable: PDG / Direction générale**

- [ ] Demander factures Médiafret 6 derniers mois (email comptabilité)
- [ ] Demander salaires chauffeurs (email RH, confidentiel)
- [ ] Demander historique réclamations CRM (email manager)
- [ ] Informer équipes: "audit coûts en cours, données confidentielles"

**Responsable: Angélique**

- [ ] Compiler top 15 fournisseurs + distances Google Maps
- [ ] Estimer temps travail par fonction (auto-pointage 1 semaine)
- [ ] Rassembler factures perso 6 derniers mois (trace devis, incident)

**Responsable: RH**

- [ ] Confirmer disponibilité données paie (timeline)
- [ ] Préparer NDA si données sensibles requises

---

### SEMAINE 2-4 (COLLECTE + CONSOLIDATION)

**Responsable: Consultant/Agent analytique**

- [ ] Recevoir + analyser factures Médiafret
- [ ] Recevoir + nettoyer données chauffeurs
- [ ] Recevoir + classifier réclamations client
- [ ] Créer templates standardisées pour affinage
- [ ] Identifer anomalies (ex: surcoûts ponctuels, pénalités)

---

### MOIS 2 (VALIDATION + RECALCUL)

- [ ] Réunion bilan: coûts réels vs estimations
- [ ] Recalcul budget transport avec data confirmée
- [ ] Identifier écarts (ex: Médiafret coûte 30% plus cher que benchmark?)
- [ ] Analyser causes écarts
- [ ] Réajuster roadmap Phase 1 selon réalité

---

## SECTION 5: IMPACT DE CHAQUE DATA SUR RECOMMANDATIONS

### Si Factures Médiafret Révèlent...

| Découverte | Impact | Action Recommandée |
|------|------|------|
| Coûts 50% plus élevés que benchmark | CRITIQUE | Rénégocier contrat Médiafret URGENT |
| Marges sous-traitants importants (20%+) | MOYEN | Chercher alternatives transporteurs |
| Pénalités retard jamais appliquées | MOYEN | Renforcer SLA / application pénalités |
| Surcharges zone masquées | FAIBLE | Revoir structure tarifaire |

### Si Data Chauffeurs Révèlent...

| Découverte | Impact | Action Recommandée |
|------|------|------|
| Utilisation réelle <60% (beaucoup inactif) | CRITIQUE | Réaffecter ressources ou réduire FTE |
| Kilométrage 50% supérieur estimé | MOYEN | Revoir routing, optimisation urgente |
| Rotation matériaux mauvaise | MOYEN | Audit WMS, meilleure planification |

### Si Audit Réclamations Révèle...

| Découverte | Impact | Action Recommandée |
|------|------|------|
| 10+ incidents/an au lieu de 2-4 | CRITIQUE | Audit causes urgente, SLA fournisseurs |
| 50% incidents = coordination interne | MOYEN | Priorité: automation alertes + scoring |
| Fournisseur X = 30% incidents | MOYEN | Renegotier ou sourcing alternatif |

---

## SECTION 6: CHECKLIST DE VALIDATION FINALE

### Questions pour PDG / Direction

```
□ Avez-vous accès factures Médiafret 6+ mois?
□ Pouvez-vous obtenir données paie chauffeurs (confidential)?
□ Avez-vous système CRM avec historique réclamations?
□ Êtes-vous à l'aise partageant données sensibles?
□ Pouvez-vous nommer sponsor collecte data (ex: Dir. Finance)?
□ Timeline acceptable: 2-4 semaines collecte?
```

### Questions pour Angélique

```
□ Pouvez-vous estimer vos heures par tâche cette semaine?
□ Avez-vous liste fournisseurs avec adresses?
□ Accepteriez-vous auto-pointage 1 mois pour affinage?
□ Quels incidents clients vous souvenez-vous récemment?
```

### Questions pour IT / Consultant

```
□ Pouvez-vous accéder factures digitales Médiafret?
□ Pouvez-vous extraire données WMS (stock, rotations)?
□ Avez-vous outils nettoyage/analyse données?
□ Quelle priorité donneriez-vous collecte vs implémentation Phase 1?
```

---

## SECTION 7: PROCHAINES ÉTAPES

### IMMÉDIAT (Ce Jour/Demain)

1. Partager cette checklist avec PDG + équipes
2. Confirmer sponsor collecte data
3. Envoyer demandes email factures Médiafret + data paie
4. Planifier réunion lancement semaine prochaine

### SEMAINE 1 (FIN NOVEMBRE)

1. Recevoir première vague données
2. Commencer nettoyage + consolidation
3. Lancer auto-pointage Angélique

### SEMAINE 4 - MOIS 2

1. Analyse data complète
2. Recalcul budgets coûts réels
3. Recommandations révisées basées sur réalité

---

## ANNEXE: FORMULE CALCUL COÛTS FINAUX

**Une fois data collectée, utiliser formule:**

```
COÛTS CHAUFFEURS = (Salaire annuel × FTE) + Carburant + Maintenance + Assurance + Amort.
COÛTS AFFRÈTEMENT = (Σ Factures Médiafret 6 mois) × 2 [annualisation]
COÛTS NAVETTES = Allocation salarial × % temps + Carburant
COÛTS CACHÉS = Temps Angélique € + Incidents € + Surstock €
────────────────────────────────────────────────────────────────────
TOTAL COÛTS ANNUELS = CHAUFFEURS + AFFRÈTEMENT + NAVETTES + CACHÉS
```

---

**Fin Checklist Data Gaps - Pass 2**
*Prêt pour collecte semaine 1*
