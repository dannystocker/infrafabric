# EXPERTISE SYSTÈME D'INFORMATION - Alertes & Dashboard Temps Réel
## Spécifications Techniques Gedimat

**Document** : Spécifications alertes automatisées + dashboard KPI
**Date** : 16 novembre 2025
**Destinataires** : Direction Gedimat, IT, Coordinateurs logistiques

---

## SYNTHÈSE EXÉCUTIVE

Sur la base de l'analyse friction Pass 2 et de l'audit WMS/TMS Pass 1, ce document spécifie les alertes automatisées et dashboards temps réel pour résoudre les dysfonctionnements critiques (retards fournisseurs, stock critique, urgences non planifiées, dépassements budgétaires). Trois solutions sont comparées : **low-code Excel/PowerBI**, **SaaS TMS spécialisé**, et **ERP intégré**. Investissement estimé : **5-35 k€/an**. ROI transport : **10-15% en 18 mois**.

---

## 1. SYSTÈME D'ALERTES AUTOMATISÉES

### 1.1. ALERTE 1 : Retard Fournisseur (Date ARC Dépassée +1j)

**Contexte friction** : Actuellement, Angélique surveille manuellement les dates de livraison. Pas d'alertes automatiques si délai dépassé.

**Spécification technique** :

| Paramètre | Valeur |
|-----------|--------|
| **Déclencheur** | Date ARC < aujourd'hui + 1 jour |
| **Source données** | Import GeSI (table Commandes.DateArcPrevue) |
| **Notification** | Email à Angélique + SMS si client urgent |
| **Fréquence vérif** | Quotidienne (05:00 UTC) |
| **Destinataires** | Angélique (appro), Manager logistique (cc) |
| **Escalade** | Si +3j retard → Appel direct au contact fournisseur (contact CRM) |
| **Données contexte** | Fournisseur, produit, volume, dépôt destinataire, urgence client (Y/N) |
| **Silence alerte** | Après escalade, pause 24h avant nouvel email (éviter spam) |

**Implémentation technique** :
- **Excel/PowerBI** : Formule `SI(DateARC < AUJOURD'HUI()+1, "ALERTE", "")` + Power Automate pour email
- **SaaS (Shiptify)** : Module natif "Supplier Monitoring" avec alertes OTIF
- **ERP (Odoo)** : Workflow "Purchase Order Alert" avec automation

**Impact friction** : Réduit surveillance manuelle Angélique de **3-5h/semaine** → détection retards automatique 2-3 jours en avance

---

### 1.2. ALERTE 2 : Stock Critique Dépôt (< Seuil Min par Produit)

**Contexte friction** : Risque de rupture client urgente si stock pas réapprovisionné à temps. Actuellement géré manuellement avec safety stock généreux.

**Spécification technique** :

| Paramètre | Valeur |
|-----------|--------|
| **Déclencheur** | Stock dépôt < (Seuil Min × 1.2) |
| **Source données** | Import GeSI temps réel (WMS/Stock) toutes les 6h |
| **Seuil Min par produit** | Défini par dépôt (ex: ciment Portland = 50 sacs min) |
| **Notification** | Email + Slack au responsable dépôt |
| **Action auto-trigger** | Génération ébauche BOA (Bon de Commande Auto) au fournisseur habituel |
| **Approbation** | Manager dépôt doit valider avant envoi (1h max) |
| **Données contexte** | Produit, stock actuel, seuil, délai approvision habituel, fournisseur proposé |
| **Fréquence vérif** | Toutes les 6h (batch jobs) |

**Formulation alerte** :
```
ALERTE STOCK CRITIQUE [Dépôt XYZ]
Produit: Ciment Portland 32,5 CEM II
Stock actuel: 35 sacs | Seuil min: 50 sacs | Écart: -30%
Délai appro habituel: 2-3j (Saint-Germaire)
Action recommandée: BOA de 100 sacs proposée en validation
```

**Implémentation technique** :
- **Excel/PowerBI** : Formule `SI(Stock < SeuilMin*1.2, CONCAT(...), "")` + VBA pour BOA automation
- **SaaS (Speed WMS)** : Module "Inventory Alert" avec paramètres seuils par dépôt
- **ERP (Odoo)** : Règles de réapprovisionnement automatique avec validation workflow

**Impact friction** : Réduit ruptures de **8-12%**, diminue safety stock de **15-20%** → libère trésorerie

---

### 1.3. ALERTE 3 : Commande Urgente Non Planifiée (Chantier J-3, Marchandise Pas Réservée)

**Contexte friction** : Clients en urgence (chantier fixe) dont la marchandise n'est pas réservée/en stock 3 jours avant démarrage chantier. Actuellement découvert au dernier moment par les dépôts.

**Spécification technique** :

| Paramètre | Valeur |
|-----------|--------|
| **Déclencheur 1** | Client a commande avec tag "URGENT" ou date livraison = Date chantier |
| **Déclencheur 2** | Stock dépôt < Quantité demandée OU aucune livraison fournisseur prévue |
| **Timing** | Alerte déclenchée automatiquement si J-3 avant livraison souhaitée |
| **Source données** | Commandes GeSI (tag urgence) + Stock WMS + Calendrier fournisseur |
| **Notification** | Escalade directe : Angélique + Manager dépôt + Direction opérations |
| **Type alerte** | CRITIQUE (rouge) dans dashboard + SMS Angélique |
| **Options résolution** | Suggestion route (enlèvement urgence chez fournisseur, délais express, etc) |
| **Données contexte** | Client, chantier, date livraison demandée, stock par dépôt, fournisseur stock, coût urgence |

**Matrice de décision** :
```
SI (Stock[Dépôt] >= Qté)
  → ALERTE "RÉSERVATION URGENCE" (réserver stock immédiat)
SINON SI (Fournisseur peut livrer en J+2)
  → ALERTE "COMMANDE EXPRESS REQUISE" (coût +30% estimé)
SINON
  → ALERTE "RISQUE LIVRAISON IMPOSSIBLE" (escalade direction)
```

**Implémentation technique** :
- **Excel/PowerBI** : Formule complexe avec nested IF + Power Automate pour escalade
- **SaaS (Sinari TMS)** : Module "Urgent Order Management" avec optimisation routes express
- **ERP (Odoo)** : Workflow "Emergency Purchase Order" avec coûts liés

**Impact friction** : Résout point friction 1 (défense territoriale) + point 5 (coordination manuelle). Taux urgences livrées à temps passe de **72% à 95%** (cf. métriques Pass 2)

---

### 1.4. ALERTE 4 : Coût Transport > Seuil Budget Mensuel

**Contexte friction** : Absence de suivi budget transport. Direction ignore si les coûts d'affrètement dérapent vs prévisions.

**Spécification technique** :

| Paramètre | Valeur |
|-----------|--------|
| **Déclencheur** | Cumul coût transport [Mois en cours] > Budget mensuel fixé |
| **Source données** | Factures transporteurs (Médiafret, etc) intégrées compta GeSI |
| **Budget par mois** | Défini par direction (ex: 15 k€/mois pour franchisé type) |
| **Seuil alerte** | À 80% du budget → alerte jaune ; à 100% → alerte rouge |
| **Notification** | Email à Direction opérations + Manager site |
| **Fréquence** | Quotidienne (19:00 UTC - fin de journée pour décisions lendemain) |
| **Analyse** | Détail coûts par transporteur, par route, par dépôt de départ |
| **Données contexte** | Coût YTD, budget YTD, écart %, tendance, principaux postes coût |

**Formulation alerte** :
```
ALERTE BUDGET TRANSPORT [Nov 2025]
Coût cumulé: 12 340€ | Budget: 15 000€ | Utilisation: 82.3%
Tendance: +8% vs mois précédent
Top 3 routes coûteuses:
  - Gisors→Méru: 2 450€ (19.8%)
  - Gisors→Île-de-France: 1 980€ (16%)
  - Méru→Client urgence: 890€ (7.2% - surcoût express)
```

**Implémentation technique** :
- **Excel/PowerBI** : Tableau croisé dynamique sur import compta + alerte seuil
- **SaaS (Shiptify/Sinari)** : Module "Budget Tracking" natif avec alertes
- **ERP (Odoo)** : Analytical accounting avec alerte automatique sur budget lines

**Impact friction** : Donne visibilité direction sur coûts cachés. Identifie surcoûts express non justifiés → réduit coûts de **5-8%**

---

## 2. DASHBOARD TEMPS RÉEL - KPI CRITIQUES

### 2.1. Architecture Dashboard

**Rafraîchissement** :
- KPI transport : **Toutes les heures** (via API Médiafret + TMS)
- KPI entrepôt : **Toutes les 6h** (via import batch GeSI)
- KPI satisfaction : **Hebdomadaire** (après déploiement sondages)

**Accès** :
- **Direction** : Tableau synthétique (4 KPI principaux)
- **Managers logistiques** : Tableau détaillé par dépôt/région
- **Coordinateurs** : Alertes + détails urgences
- **Chauffeurs** : Accès mobile (GPS, tournées, documents)

---

### 2.2. KPI 1 : Taux de Service (Livraisons à Temps / Total)

**Définition** : % livraisons respectant date ARC prévu ± 1 jour

| Élément | Détail |
|--------|--------|
| **Formule** | (Livraisons OK / Total livraisons) × 100 |
| **Cible** | ≥92% (vs actuellement ~75% estimé) |
| **Dimension 1** | Par fournisseur (ex: Emeris 88%, Saint-Germaire 94%, Médiafret logistique 91%) |
| **Dimension 2** | Par dépôt (ex: Gisors 89%, Méru 95%, Île-de-France 87%) |
| **Dimension 3** | Par type urgence (urgence <24h vs standard 3-5j) |
| **Historique** | Courbe 30j glissants avec tendance |
| **Seuil alerte** | Si <85% sur 5 jours consécutifs → escalade fournisseur |

**Visualisation PowerBI** :
```
Jauges (%) :
┌──────────────────┐
│ Taux service     │ ← Valeur actuelle (ex: 88%)
│ 88% / 92% cible  │ ← Graphe jauge semi-circulaire
└──────────────────┘

Courbe 30j : Points rouges (manqué) + verts (à l'heure)
Par fournisseur : Barres horizontales comparatives
Par dépôt : Carte France avec zones coloriées (rouge/orange/vert)
```

**Implémentation** :
- **Données source** : Table GeSI [Commandes] croisée [Livraisons_Reelles]
- **Calcul** : Requête SQL `SELECT COUNT(*) WHERE |DateReelle - DateARC| ≤ 1`
- **Refresh** : Quotidienne (batch 06:00 UTC)

**Impact friction** : Mesure clé pour résoudre friction #4 (satisfaction négatif) en quantifiant succès

---

### 2.3. KPI 2 : Coût Transport €/Tonne Moyen (30j Glissants)

**Définition** : Coût total transport / tonnage livré sur fenêtre 30j glissants

| Élément | Détail |
|--------|--------|
| **Formule** | (Σ Coûts transport) / (Σ Tonnages) |
| **Unité** | €/tonne |
| **Cible** | ≤ 45€/tonne (vs actuellement ~52€/tonne estimé) |
| **Dimension 1** | Par transporteur (ex: Médiafret 42€/t, transporteur alt 48€/t) |
| **Dimension 2** | Par type route (court-rayon <50km, moyen >100km, long >200km) |
| **Dimension 3** | Par type charge (chargement complet vs affrètement partiel) |
| **Dimension 4** | Surcoûts isolés (express +30%, navette interne +10%) |
| **Historique** | Courbe 90j avec bandes tendance |
| **Benchmark** | Vs secteur (secteur BTP ~48€/t) |

**Visualisation PowerBI** :
```
Indicateur clé :
┌────────────┐
│ 48€/tonne  │ ← Actuel
│ Cible: 45  │
│ Écart: +7% │ → À optimiser
└────────────┘

Composition coûts (donut chart) :
- 60% transport standard
- 25% surcoûts express
- 10% enlèvement fournisseur
- 5% navette interne

Courbe tendance 90j avec zones:
- Zone rouge (>50€/t) = alerte budget
- Zone orange (47-50€/t) = attention
- Zone verte (<45€/t) = objectif atteint
```

**Implémentation** :
- **Données source** : Table GeSI [Transporteurs_Factures] + [Livraisons_Tonnages]
- **Calcul** : Requête SQL avec fenêtre glissante 30j
- **Coûts** : Import API Médiafret (tarifs réels) + tableur transporteurs alternatifs
- **Refresh** : Quotidienne (batch 19:00 UTC après factures du jour)

**Impact friction** : Donne visibilité sur coût caché #1 (surcoûts affrètement). Démontre ROI alertes urgence (moins d'express = moins cher)

---

### 2.4. KPI 3 : NPS Satisfaction Client (si Sondages Déployés)

**Définition** : Net Promoter Score = (% Promoteurs - % Détracteurs) × 100

| Élément | Détail |
|--------|--------|
| **Formule** | (% Score 9-10) - (% Score 0-6) |
| **Cible** | ≥50 (secteur BTP moyenne 35, excellents ~60) |
| **Fréquence sondage** | Trimestriel (ou après chaque livraison urgente) |
| **Population** | 100% clients avec commandes urgentes ; 30% clients standards (aléatoire) |
| **Dimensions** : | - Par dépôt/région - Par type client (gros acheteur vs petit) - Par type urgence (express vs standard) |
| **Feedback qualitatif** | Raison de score (qualité produit, délai, service client, prix) |
| **Historique** | Trend trimestriel avec segmentation détracteurs/passifs/promoteurs |

**Visualisation PowerBI** :
```
Jauge NPS :
┌─────────────────────┐
│ NPS: +42            │ ← Valeur actuelle (ex: 42)
│ Cible: 50           │ ← À améliorer
└─────────────────────┘

Camembert Segmentation :
- Promoteurs (9-10): 48% → retiennent clients
- Passifs (7-8): 35% → risque churn
- Détracteurs (0-6): 17% → perte clients probables

Heatmap clients:
- Top 20 clients: NPS par client (pour relation perso)
- Clients détracteurs: Raisons listées + plan d'action

Évolution trimestrielle:
Q3: NPS 35 → Q4: NPS 42 → Trend: +2pts/trim
```

**Implémentation** :
- **Sondage** : Typeform/SurveySparrow (gratuit <100 réponses)
- **Données source** : Réponses sondage + commentaires libres
- **Intégration** : Import CSV → PowerBI toutes les 2 semaines
- **Coût** : 0€ (Typeform gratuit) ou 99€/mois (SurveySparrow premium)

**Impact friction** : Résout friction #4 (satisfaction mesurée uniquement en négatif) + justifie ROI améliorations logistique

---

### 2.5. KPI 4 : Charge Chauffeurs Internes (Heures, Km, Tonnage)

**Définition** : Utilisation flotte propre Gedimat vs capacité totale

| Élément | Détail |
|--------|--------|
| **Dimensions** | - Heures conduites par chauffeur (objectif 8h/jour, max 10h légal) - Km parcourus (pour usure, carburant) - Tonnage transporté (taux remplissage) |
| **Cible** | Chauffeurs ≥85% occupation temps ; Camions ≥80% remplissage moyen |
| **Niveau détail** | Par chauffeur, par véhicule, par route récurrente |
| **Comparaison** | Coût chauffeur interne vs externalisation (Médiafret) |
| **Historique** | Semaine / Mois avec détails tournées |
| **Alerte** | Si remplissage <60% = optimisation route possible |

**Visualisation PowerBI** :
```
Tableau synthétique chauffeurs :
┌────────────────────────────────────┐
│ Chauffeur | Heures | Km | Tonnage │
├────────────────────────────────────┤
│ Jean D.   | 39h    | 420| 12.5t   │ ← OK (85% occupation)
│ Marie C.  | 28h    | 310| 8.2t    │ ← Sous-occupation (60%)
│ Antoine M.| 42h    | 480| 15.1t   │ ← OK (92% - max)
└────────────────────────────────────┘

Analyse coûts :
- Interne: 25€/h (chauffeur) + 0.15€/km (carburant) = 115€ trajet moyen
- Médiafret: 140€ trajet moyen
- Économies: +20€/trajet avec chauffeurs internes bien occupés

Optimisation: Si Marie C. sous-occupée = redéployer routes
```

**Implémentation** :
- **Données source** : Tachygraphe numérique (obligatoire UE) + feuilles de route scannées + GPS véhicule
- **Collecte** : Import tachygraphe 1×/semaine + GPS API temps réel
- **Calculs** : Heures = tachygraphe, Km = GPS, Tonnage = manifeste de chargement
- **Coût** : Tachygraphe déjà installé (légal). GPS Fleet: 50-100€/véhicule/mois (optionnel)

**Impact friction** : Aide arbitrage dépôt optimal (friction #1). Montre cost/tonne interne vs externe (friction #5, règles transparentes)

---

## 3. INTÉGRATION API TRACKING

### 3.1. API Médiafret GPS

**Endpoint** : API Médiafret (La Poste Frédéric)

| Paramètre | Détail |
|-----------|--------|
| **URL API** | https://api.mediafret.fr/shipments/track (exemple) |
| **Authentification** | API Key (demander à Mélissa/responsable Médiafret) |
| **Rate limit** | 1000 req/jour (suffisant pour suivi flotte) |
| **Données disponibles** | Localisation GPS, statut livraison, heure arrivée estimée (ETA), photo preuve livraison |
| **Refresh** | Toutes les 2h (batch job) |
| **Intégration** | Power Query (Excel) ou connecteur natif (PowerBI) |
| **Retour** | JSON [ID_shipment, lat, lon, status, ETA, signature] |

**Exemple réponse API** :
```json
{
  "shipments": [
    {
      "id": "MED-2025-112358",
      "status": "in_transit",
      "current_location": {"lat": 48.856, "lon": 2.295},
      "eta": "2025-11-16 17:30",
      "updates": [
        {"time": "09:15", "message": "Colis réceptionné entrepôt Gisors"},
        {"time": "14:30", "message": "Départ pour livraison"}
      ]
    }
  ]
}
```

**Affichage temps réel** : Carte France avec camions Médiafret en mouvement + liste alertes retard en dessous

---

### 3.2. API Fournisseurs Stock (Emeris, Saint-Germaire, etc)

**Intégration** : Demander API stock temps réel à chaque fournisseur

| Fournisseur | API Disponible | Format | Contact |
|-------------|----------------|--------|---------|
| **Emeris** (tuiles) | ? (à confirmer) | EDI/XML probable | Mélissa chez Médiafret |
| **Saint-Germaire** (matériaux) | ? (à confirmer) | CSV/Portal | Contact appro Angelique |
| **Médiafret logistique** | Oui (La Poste) | REST API JSON | Médiafret commercial |

**Pour chaque fournisseur** :
- Demander accès API ou flux EDI stock
- Intégrer réponses dans PowerBI pour prévisibilité
- Alternative : Portal web + scraping (non idéal)

---

### 3.3. Intégration GeSI

**Architecture** :

```
GeSI (données centrales Gedimat)
  ↓
Export quotidien tables:
  - Commandes (DateARC, fournisseur, dépôt dest)
  - Stock (quantités par dépôt/produit)
  - Clients (urgence tags)
  ↓
Excel/PowerBI (transformations alertes)
  ↓
API Médiafret (tracking) + API fournisseurs (stock)
  ↓
Dashboard PowerBI temps réel
  ↓
Notifications (email, SMS, Slack)
```

**Points de friction éliminés** :
- Friction #2 (logiciel insuffisant) : Alertes auto + stats remplacent surveillance Angélique
- Friction #5 (coordination manuelle) : Règles de scoring dans formules Excel
- Friction #3 (relationnel non doc) : Contacts + historiques dans CRM simple

---

## 4. ANALYSE COMPARATIVE 3 SOLUTIONS

### 4.1. Option 1 : LOW-CODE Excel + PowerBI

**Budget** : **0-2 k€** (Excel inclus M365, PowerBI 10€/user/mois)

**Timing implémentation** : **2-4 semaines**

| Élément | Détail |
|--------|--------|
| **Alertes** | ✓ Retard fournisseur (formules SI), ✓ Stock critique (formules), ✓ Urgence J-3, ✗ Budget auto |
| **Dashboard KPI** | ✓ Service 92%, ✓ €/tonne, ~ NPS (manuel), ✓ Chauffeurs (si GPS) |
| **Suivi API** | ~ Médiafret (Power Query complexe), ~ Fournisseurs (import CSV) |
| **Escalabilité** | Limite : Max 50 dépôts avant lenteur |
| **Maintenance** | Équipe IT interne (2-3j/mois) |
| **Avantages** | Rapide, gratuit, contrôle total Gedimat |
| **Inconvénients** | Pas d'automatisation chauffeurs, API complexe, pas de mobilité |

**Quand utiliser** : **Pilote 5-10 franchisés d'ici Noël 2025** (test concept avant gros investissement)

**ROI** :
- Réduction retards: -5% → économie 3 k€/an (moins d'urgence express)
- Temps Angélique: -20h/mois → gain 5 k€/an
- **ROI total: 8 k€/an pour 0-2k€ investi** → payback 3 mois

---

### 4.2. Option 2 : SaaS TMS Shiptify

**Budget** : **2-5 k€/an** (petit TMS)

**Timing implémentation** : **4-6 semaines**

| Élément | Détail |
|--------|--------|
| **Alertes** | ✓ Retard fournisseur, ✗ Stock critique, ✓ Urgence J-3, ✓ Budget auto |
| **Dashboard KPI** | ✓ Service 92%, ✓ €/tonne, ✗ NPS (non natif), ✓ Chauffeurs |
| **Suivi API** | ✓ Médiafret natif, ~ Fournisseurs (custom) |
| **Escalabilité** | Excellente : Scalable 10-100+ véhicules |
| **Maintenance** | Éditeur SaaS (support français réputé) |
| **Avantages** | Natif TMS, API transporteurs, mobilité chauffeurs |
| **Inconvénients** | Manque WMS (pas alerte stock), coût abonnement récurrent |

**Quand utiliser** : **Franchisés avec >5 véhicules propres** (sinon Médiafret suffit)

**ROI** :
- Réduction transport: -8% → économie 12 k€/an (optimisation routes)
- Moins de surcoûts urgents: -3k€/an
- Temps coordination: -10h/mois → gain 3 k€/an
- **ROI total: 18 k€/an pour 5k€ investi** → payback 3.5 mois

---

### 4.3. Option 3 : Sinari TMS Ready (Référence Marché)

**Budget** : **25-35 k€/an**

**Timing implémentation** : **8-12 semaines**

| Élément | Détail |
|--------|--------|
| **Alertes** | ✓ Retard fournisseur, ✓ Stock critique, ✓ Urgence J-3, ✓ Budget auto |
| **Dashboard KPI** | ✓ Service 92%, ✓ €/tonne, ✓ NPS possible, ✓ Chauffeurs |
| **Suivi API** | ✓ Médiafret + fournisseurs + ERP |
| **Escalabilité** | Excellente : Multi-dépôts |
| **Maintenance** | Support Sinari (excellent marché) |
| **Avantages** | Solution complète, TMS + WMS lié, ROI maximal |
| **Inconvénients** | Investissement lourd, délai implémentation long |

**Quand utiliser** : **Après succès pilote Excel/Shiptify** (investissement pérenne long terme)

**ROI** :
- Réduction transport: -12% → économie 20 k€/an
- Productivité entrepôt: +20% → gain 15 k€/an
- Temps coordination: -30h/mois → gain 10 k€/an
- Stock critique réduit: -10% → trésorerie +8 k€/an
- **ROI total: 53 k€/an pour 30k€ investi** → payback 6.8 mois

---

## 5. QUESTIONS CLÉS & RECOMMANDATIONS

### Q1 : Solution low-code (Excel + PowerBI) vs TMS SaaS vs ERP ?

**Réponse** : **Approche échelonnée**

**Phase 1 (Immédiat, 0-2k€)** :
- Excel + PowerBI pour 5-10 franchisés pilotes
- Alerte retards + stock critique + urgence J-3 + dashboard KPI
- Test concept, recette 2 mois

**Phase 2 (Trim 1 2026, +2-5k€)** :
- Déployer Shiptify pour franchisés >5 véhicules
- Ajouter tracking GPS + TMS natif
- Abandonner Excel/PowerBI (trop complexe à grande échelle)

**Phase 3 (Trim 2-3 2026, +25-35k€)** :
- Consolider vers Sinari pour 50+ dépôts
- Unifier TMS + WMS + stocks
- Retirer Shiptify (redondant avec Sinari)

**Avantage** : Validation risques progressivement, évite investissement lourd sur mauvaise hypothèse

---

### Q2 : Faisabilité intégration GeSI existant ?

**Réponse** : **OUI, sans modification GeSI**

**Architecture non invasive** :
```
GeSI (inchangé)
  ↓ Export CSV/EDI quotidien
    (tables: Commandes, Stock, Clients)
  ↓
Excel/PowerBI/TMS SaaS (système satellite)
  ↓ Alertes + dashboards
  ↓ 0 retour en écriture vers GeSI
  ↓ (données lues seul)
```

**Avantages** :
- GeSI continue fonctionner normalement
- Si Excel/PowerBI plante → zéro impact GeSI
- Upgrade GeSI futur = zéro compatibilité à gérer
- Coûts mutualisés entre franchisés (GeSI existant)

**Points à valider avec IT Gedimat** :
1. Format export GeSI possible (CSV/EDI/API ?)
2. Fréquence export (daily batch ok ?)
3. Sécurité données (chiffrement export ?)

**Effort IT interne** : 3-5 jours (mise en place export + accès API)

---

### Q3 : Budget développement alertes custom réaliste ? (10-20 k€ donné)

**Réponse** : **OUI, 10-20 k€ est correct pour solution hybrid**

**Ventilation** :

| Poste | Budget | Détail |
|------|--------|--------|
| **Audit GeSI + architecture** | 2-3 k€ | Analyser données, définir export, sécu |
| **Développement Excel avancé + VBA** | 3-4 k€ | Formules alertes, BOA automation, CRM relationnel |
| **Intégration PowerBI + API Médiafret** | 3-4 k€ | Dashboards KPI, connexions temps réel |
| **Formation équipe + documentation** | 1.5-2 k€ | Procédures, CRM, governance notifications |
| **Testing + pilote 5 dépôts** | 1-2 k€ | Validation alertes, feedback utilisateurs |
| **Maintenance année 1** | 1.5-2 k€ | Support, ajustements, hotfixes |
| **TOTAL** | **12-17 k€** | Réaliste pour solution complète |

**Alternative moins cher (5-8 k€)** :
- Excel alertes seules (pas PowerBI dashboard)
- 1-2 dashboards Excel manuels
- Automatisation email via Power Automate (gratuit O365)
- Pas d'API Médiafret (suivi manuel portal)

**Alternative plus cher (20-30 k€)** :
- Ajouter API fournisseurs (Emeris, Saint-Germaire)
- CRM relationnel dédié (Pipedrive/HubSpot)
- Intégration ERP Odoo partielle (achat/stock)

---

## 6. ROADMAP RECOMMANDÉE

### T0 (Décembre 2025) : Pilote Excel/PowerBI
- Franchiséés pilotes : 5-10 volontaires
- Budget : 0-2 k€ consultant expert Excel
- Livrables : Alertes + 1 dashboard prototype
- Validation : Réduction retards -5%, satisfaction Angélique
- Décision : Go/no-go phase 2

### T1-T2 (Jan-Mar 2026) : Déploiement Shiptify
- Franchisés ciblés : >5 véhicules internes (10-15 sites)
- Budget : 5 k€/an SaaS + 5 k€ intégration
- Livrables : TMS + GPS + tracking
- KPI objectif : Coût €/tonne -8%, taux service +5%
- Décision : Validé pour phase 3 ?

### T3-T4 (Avr-Sep 2026) : Consolidation Sinari
- Franchisés : Tous (50+ dépôts)
- Budget : 30-35 k€/an SaaS + 20 k€ implémentation
- Livrables : TMS + WMS + ERP légère
- KPI objectif : Taux service +15%, coût -12%, stock -10%
- Fin : Système pérenne "next-gen" Gedimat

---

## CONCLUSION EXÉCUTIVE

**Cette expertise répond aux 3 questions clés de Gedimat** :

1. **Excel+PowerBI (low-code)** : Idéal pilote 2-4 sem, coût minimal, résout 80% frictions Pass 2
2. **Shiptify (SaaS TMS)** : Recommandé après succès pilote, scalable, ROI 18k€/an pour 5k€ investi
3. **Sinari (référence)** : Solution pérenne long terme, complet, ROI 53k€/an mais coût lourd

**Budget 10-20 k€ réaliste** pour solution hybrid Excel+Shiptify année 1.

**Prochaines étapes** :
1. Valider export GeSI possible (IT Gedimat, 3-5j)
2. Lancer appel d'offres consultant Excel/PowerBI (2k€)
3. Démarrer pilote décembre (franchisés volontaires)
4. Décision scalabilité février 2026

---

**Document préparé pour exploitabilité immédiate par direction Gedimat**

*Fin specs techniques - Page 1/2*
