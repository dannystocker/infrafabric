# SYNTHÈSE PLATEAU - LACUNES DONNÉES GEDIMAT
## Zones Grises Identifiées et Méthodes de Collecte

**Document stratégique** | 2 pages | Novembre 2025

---

## 1. RÉPARTITION EXACTE COMMANDES PAR TRANCHE POIDS

**SITUATION ACTUELLE :**
- Estimation Pass 2 : 45-50% (0-5t), 25-30% (5-10t), 15-20% (10-20t), <5% (>20t)
- Basée sur analyse secteur GSB et extrapolation de 12 commandes-pilotes
- Variance estimée : ±10 points de pourcentage

**BESOIN DE DONNÉES :**
- Extraction ERP GeSI : 12 derniers mois (janvier-décembre 2024 + YTD 2025)
- Requête précise : volume par tranche poids, par client, par fournisseur principal
- Volume attendu : 800-1200 commandes analysées
- Source : données facturées (fiables) vs estimées à la réception (à croiser)

**IMPACT SI NON-COMBLÉ :**
- Calibrage imprécis du scoring multicritère VRP (poids = 30% pondération)
- ROI chauffeur "type" incertain pour taille de flotte (3PL vs propre)
- Dimensionnement hub consolidation biaisé (surfaces, équipements)
- Décision dépôts supplémentaires ou affrètement sans fondement

**MÉTHODES DE COLLECTE :**
1. **Approche ERP (prioritaire)** : requête SQL GeSI, export CSV, validation 5 factures-tests
2. **Validation terrain** : entretien 30 min avec responsable warehouse (poids réel vs déclaré)
3. **Contrôle qualité** : vérification 10% des lignes (poids aberrants, doublons)
4. **Timeline** : 5-7 jours après accès ERP confirmé
5. **Responsable** : pilote projet + data analyst Gedimat

---

## 2. COÛTS RÉELS MÉDIAFRET DÉTAILLÉS

**SITUATION ACTUELLE :**
- Données Pass 2 : estimations secteur 6,50€/km + frais de gestion
- Hypothèse marges Médiafret : 15-20% (standard 3PL)
- Pas d'analyse prix/tonne/km réel, pas de variante par trajet ou urgence

**BESOIN DE DONNÉES :**
- Factures 2024 Médiafret : minimum 50 factures, couvrant saisons + volumes variables
- Détail par ligne : km parcourus, tonnes réelles, type trajet (appel à quai vs standard), urgences
- Tarification : structure forfait vs variable, rabais volume, surcharges (urgence, poids)
- Comparatif interne : trajets réalisés en propre vs affrètement (coûts réels propriété)

**IMPACT SI NON-COMBLÉ :**
- Négociation tarifs Médiafret sans données factuelles (faible levier)
- Business case hub/dépôts validé sur estimations 6,50€/km (peut dériver de ±20%)
- Décision affrètement vs flotte propre non objective
- Risque : investissement dépôt sur ROI fictif

**MÉTHODES DE COLLECTE :**
1. **Factures historiques** : récupération 2024 (pdf ou export comptable)
2. **Analyse granulaire** : création matrice prix/km/tonne, par type trajet
3. **Entretien Médiafret** : 1h30 avec commercial, structure tarifaire future, volume discounts
4. **Comparatif 3PL alternatifs** : 2-3 appels d'offres concurrents (Geodis, DPD, XPO)
5. **Timeline** : 8-10 jours (étapes 1-2), 15-20 jours (étapes 3-4)
6. **Responsable** : supply chain + finance Gedimat

---

## 3. TAUX SATISFACTION CLIENT BASELINE

**SITUATION ACTUELLE :**
- Estimation Pass 4 : NPS 16-18 (faible)
- CSAT estimée : 62-68%
- Basée sur retours fragmentaires (plaintes service, feedback informels)
- Pas de sondage structuré, pas de baseline pré-optimisation

**BESOIN DE DONNÉES :**
- Sondage 50 clients pilotes : questions CSAT (livrabilité, délai, communication, état produit)
- Format : 1-5 échelle Likert, email post-livraison ou SMS (24h après)
- Couverture : petits (0-5t), moyens (5-10t), gros (10-20t) clients
- Segmentation réponses : par région, par type produit, par type délivrance (dépôt vs chantier)

**IMPACT SI NON-COMBLÉ :**
- Progrès communication/service non mesurable (avant/après optimisation)
- Investissements (tracking, staff, hub) justifiés sans ROI client visible
- Déperdition clients insidieuse (churn invisible avant trop tard)
- Crédibilité direction auprès stakeholders (clients, actionnaires)

**MÉTHODES DE COLLECTE :**
1. **Questionnaire maison** : 5 questions clés CSAT (délai ±, communication, produit intact, prix, recommandation)
2. **Logiciel sondage** : Typeform gratuit ou Qualtrics (si budget)
3. **Distribution** : email post-livraison (automatisé via GeSI si possible), relance SMS si <10% réponse
4. **Analyse** : NPS = % promoteurs - % détracteurs, CSAT moyenne, analyse verbatims plaintes
5. **Timeline** : 2-3 semaines (10 jours sondage + analyse)
6. **Responsable** : responsable client/commercial + data analyst

---

## 4. CAUSES PRÉCISES RETARDS (RÉPARTITION %)

**SITUATION ACTUELLE :**
- Estimation Pass 2 : fournisseur 40-45%, transport 25-30%, coordination interne 15-20%, autres 10%
- Basée sur retours secteur + interviews 3 stakeholders (pas exhaustif)
- Manque granularité : retards fournisseur = stocke épuisé vs production retardée vs erreur adresse

**BESOIN DE DONNÉES :**
- Analyse 100 derniers retards : origine exacte, durée (h), impact client (péremption, chantier arrêté, etc.)
- Source : traçabilité GeSI, appels clients, mails fournisseurs, logs transport
- Segmentation : par catégorie retard (stock, production, transport, réclamation client), par fournisseur principal

**IMPACT SI NON-COMBLÉ :**
- Actions correctives déployées sur mauvaise cible (investir en dépôt si retards = transport)
- Négociations fournisseurs sans chiffres probants
- SLA client non respectés sans diagnostic clair
- Déperdition crédit auprès clients (défaut de service chronique)

**MÉTHODES DE COLLECTE :**
1. **Audit dossiers** : 100 derniers retards >24h, documenation faits
2. **Entretiens ciblés** : fournisseur top 5, gestionnaire warehouse, chauffeurs 3PL
3. **Traçabilité aller-retour** : email/SMS date commande → date livraison → cause décalage
4. **Classement** : matrice cause × fréquence × durée moyenne × impact client
5. **Timeline** : 10-12 jours (audit + entretiens)
6. **Responsable** : responsable logistique + supply chain

---

## 5. DISTANCES RÉELLES FOURNISSEURS ↔ DÉPÔTS

**SITUATION ACTUELLE :**
- Estimation Pass 2-3 : géographie Normandie/Île-de-France, seuil 16km proximité
- Basée sur cartographie Google Maps (5 trajets-tests)
- Pas de matrice distances-péages, pas de variantes itinéraires (autoroute vs routes)

**BESOIN DE DONNÉES :**
- Matrice distances exactes : 10 fournisseurs principaux ↔ 3-4 dépôts cibles
- Détail : distance km (aller-retour), temps trajet moyen, coût péages, heures ouverture fournisseur
- Variantes : saison (trafic), type véhicule (35t vs 19t), itinéraires prioritaires

**IMPACT SI NON-COMBLÉ :**
- Seuil 16km proximité arbitraire (réglage VRP) non validé (sous-/sur-dimensionné)
- Hub consolidation localisé sur hypothèse (peut nécessiter relocalisation)
- Optimisation routes VRP inefficace (coûts transport non minimisés)
- Investissement dépôt sur périmètre de chalandise fictif

**MÉTHODES DE COLLECTE :**
1. **Cartographie RouteFlex/HERE/TomTom** : API, 50 trajets principaux, tarif péages réels
2. **Appels fournisseurs** : validation temps trajet estimé vs constaté, heures réception
3. **Données transport** : registres Médiafret (heures départ/arrivée de 50 trajets 2024)
4. **Agrégation matrice** : distance, durée, coût péages, créneaux horaires fournisseur
5. **Timeline** : 7-10 jours (API + appels)
6. **Responsable** : supply chain + IT/SIG

---

## SYNTHÈSE IMPACT ET PRIORITÉ

| **Lacune** | **Effort** | **Impact ROI** | **Urgence** | **Dépendances** |
|---|---|---|---|---|
| Répartition poids | 7j | Très haut (scoring) | Haute | Accès ERP |
| Coûts Médiafret | 20j | Très haut (négo) | Très haute | Factures 2024 |
| Baseline satisfaction | 21j | Haut (client) | Moyenne | Outil sondage |
| Causes retards | 12j | Très haut (opérations) | Haute | Archive retards |
| Distances fournisseurs | 10j | Haut (VRP) | Haute | API cartographie |

**RECOMMANDATION :** Lancer en parallèle répartition poids + coûts Médiafret + causes retards (semaine 1), chaîner satisfaction + distances (semaine 2-3). Responsable unique pour séquençage : pilote projet Gedimat.

**INVESTMENT ESTIMÉ :** 30-40 jours H.T., coût outils ~2k€ (sondage, API cartographie, accès ERP external si nécessaire).

---

*Document révisé Nov 2025 | À valider CoDir*
