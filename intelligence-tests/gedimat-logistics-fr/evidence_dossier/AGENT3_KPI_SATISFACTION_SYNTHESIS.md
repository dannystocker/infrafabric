# Indicateurs Clés de Performance & Satisfaction Client B2B
## Synthèse de Recherche Pass 1 Agent 3
**Date:** 16 novembre 2025
**Contexte:** Gedimat - Distribution matériaux construction (Grande Surface Bricolage)
**Méthodologie:** Recherche benchmarks secteur + méthodologies mesure
**Format:** 2-3 pages synthèse + templates pratiques

---

## PARTIE A: INDICATEURS CLÉS DE PERFORMANCE (KPI) LOGISTIQUES

### 1. Taux de Service (Taux de Livraison À Temps)

**Définition:** Pourcentage de livraisons respectant la date promise au client

**Benchmark Industrie:**
- **Standard général:** 95% considéré comme norme industrie (APQC, RXO 2024)
- **Expectation haute:** 96%+ (41% des transporteurs visent ce seuil)
- **Construction matériaux France:**
  - Leroy Merlin: 2-3 jours commandes petites, 3-10 jours articles volumineux
  - Castorama: Données non disponibles publiquement
  - Point P (négoce): ~4-6 jours délai standard estimé
- **Mesure:** Norme industrie = livraison à fenêtre de 30 minutes (54% des chargeurs mesurent à cette précision)

**Réalité Gedimat:** Actuellement non mesuré systématiquement - **QUICK WIN 1:** Implémenter suivi taux service baseline

---

### 2. Coût de Transport par Tonne par Kilomètre (€/t/km)

**Définition:** Coût unitaire transport permettant comparaison inter-dépôts et optimisation routage

**Benchmark Industrie:**
- **Moyenne France (illustration):** ~€0.15-0.25 par tonne-kilomètre (données composites ELLA/Cerema 2023)
- **Facteurs de variation:**
  - Distance: Trajets courts (20-50km) coût élevé/t/km vs trajets longs (>200km)
  - Densité produit: Matériaux construction poids lourd (briques tuiles) vs léger (isolation)
  - Mode transport: Chauffeur interne vs affrètement externe (+30-50% coût)
  - Saisonnalité: Pic été-automne (rénovations) vs creux hiver

**Cas Gedimat:**
- **Chauffeur interne (<10t):** Coût salarial fixe estimé ~€25-35/heure → très économique par t/km si bon remplissage
- **Affrètement externe (>10t):** Médiafret + sous-traitants → premium de ~30-50% vs salarial interne
- **Navette interne:** Redistribution 2x/semaine = coût fixe réparti faible si consolidation optimale

**Calcul Pratique:** Total coûts transport (salaires PL + carburant + maintenance) / total tonnes transportées / total km parcourus = €/t/km

---

### 3. Délai Moyen de Livraison

**Définition:** Temps écoulé entre commande client et marchandise réceptionnée

**Benchmark Secteur Construction Matériaux France:**
- **Leroy Merlin (référence française):** 2-4 jours pour petits articles, jusqu'à 10 jours articles volumineux
- **Point P (négoce B2B):** ~4-6 jours délai standard estimé
- **Urgences (chantier date fixe):** Possibilité enlèvement immédiat magasin (+coût transport express)

**Décomposition Délai Type:**
- Commande → confirmation fournisseur: 1-3 jours (friction Gedimat: dépend fiabilité fournisseur)
- Fabrication/stockage fournisseur: 3-7 jours (délai critique Éméris cas type)
- Transport fournisseur → Gedimat: 0-2 jours selon proximité
- Redistribution intra-Gedimat si besoin: 1-2 jours (navette)
- **Total:** 5-14 jours délai global (très variable selon cas)

**Opportunité Gedimat:** Mesurer délai réel vs promis + analyser causes retards (40/30/30 fournisseur/transport/coordination estimé)

---

### 4. Taux de Rupture de Stock (Stockout Rate)

**Définition:** Pourcentage d'articles commandés non disponibles au moment de la commande client

**Benchmark Industrie:**
- **Moyenne retail (2000s):** ~8% (élevé, impact très négatif)
- **Cible performance forte:** <2% (représente excellence)
- **Coût rupture:** Jusqu'à 20% perte ventes + 36% clients migrent concurrents (NetSuite)

**Seuils Acceptables par Contexte:**
- **Produits critiques (tuiles, ciment urgent):** <1% acceptable
- **Produits saisonniers:** 2-5% acceptable si bien communiqué client
- **Produits lents:** 5-10% acceptable (moins critique)

**Variables Gedimat:**
- EOQ (Economic Order Quantity) Wilson: optimiser taille commandes vs coûts stockage
- Demand sensing: prévoir pics (rénovation printemps/été vs baisse hiver)
- Coordination 3 dépôts: centraliser stock de sécurité vs répartir localement?

---

### 5. Taux de Remplissage Véhicules (Vehicle Fill Rate - VFR)

**Définition:** Ratio (capacité utilisée / capacité totale) × 100

**Benchmark Industrie:**
- **Measure simple (tonnage):** Viser 75-85% capacité poids moyen
- **Measure complète (volume):** Considérer pallet + hauteur + deck-area coverage
- **Courier/Express (CEP):** Minimiser trajets à vide (économie carburant + CO2)

**Calcul Pratique:**
```
VFR = (Tonnage réel chargé / Capacité max véhicule) × 100
Exemple: 18 tonnes chargées / 24 tonnes capacité = 75% VFR
```

**Opportunité Gedimat:** Consolider commandes petites dépôts avant expédition externe = augmenter VFR = réduire coût/t/km

**Objectif Recommandé:** 80%+ pour affrètement externe, 65%+ acceptable pour navettes internes (flexibilité stock)

---

### 6. Coût par Commande (Order Fulfillment Cost)

**Définition:** Coût total handling commande (picking, packing, shipping) / nombre commandes

**Formule Standard:**
```
Coût par commande = (Total frais warehouse + packing + shipping) / Nombre commandes
Exemple: €50,000 frais / 1,000 commandes = €50/commande
```

**Benchmark B2B Logistique:**
- **E-commerce pure:** €3-8 par commande (volumes hauts, automatisés)
- **B2B distribution matériaux:** €10-25 par commande (plus complexe, lots variables)
- **Gedimat estimé:** €8-15 par commande estimé (à valider avec données réelles)

**Composantes À Inclure:**
1. Main d'œuvre directe: réception, picking, packing, expédition
2. Main d'œuvre indirecte: supervision, nettoyage, inventaire
3. Occupancy: loyer, électricité, amortissement équipement WMS
4. Packing: cartons, papier, protection (exclure shipping = coût variable par transporteur)

**Sensibilité:** Chaque €/commande réduit = impact direct sur marge globale (exemple: réduire 10€ par commande sur 1,000 commandes = €10k économies annuelles)

---

## PARTIE B: MESURE SATISFACTION CLIENT B2B

### 1. NPS - Net Promoter Score

**Méthodologie:**
- **Question unique:** "Quelle probabilité recommanderiez-vous Gedimat à collègue/client? (0-10)"
- **Calcul:** % Promoteurs (9-10) - % Détracteurs (0-6) = NPS
- **Exemple:** 50% Promoteurs - 20% Détracteurs = NPS 30

**Interprétation Scores:**
- **Négatif:** Problème sérieux urgence
- **0-30:** Bon (entreprises stables)
- **30-70:** Excellent (croissance potentielle)
- **70+:** Exceptionnel (champions)

**Benchmarks B2B Industrie (2024):**
- **Healthcare:** NPS 58 (meilleur secteur)
- **Manufacturing & Industrial:** NPS ~45 estimé (données NICE Satmetrix)
- **Logistique/Transport:** NPS ~30-40 (secteur moins mature)
- **Construction matériaux (estimé):** NPS 35-45 baseline attendue

**Gedimat Quick Start:**
- **Échantillon:** 50 clients pilotes (artisans BTP, petites entreprises construction)
- **Fréquence:** Trimestrielle (mesurer évolution)
- **Suivi:** Appeler Promoteurs (10-15%) = fidélisation, Détracteurs = diagnostic raison

**Avantage NPS:** Simple, comparable industrie, lié à croissance revenue (70% B2B ignorent ce lien)

---

### 2. CSAT - Customer Satisfaction Score

**Méthodologie:**
```
Question post-livraison:
"Êtes-vous satisfait de cette livraison?"
Réponses: Très insatisfait (1) → Très satisfait (5)

CSAT = (Réponses 4-5) / Total réponses × 100
Exemple: 35 clients très satisfaits / 50 total = CSAT 70%
```

**Benchmarks B2B (2025):**
- **Below 50%:** Problématique urgent
- **50-70%:** Neutre, pas engageant
- **70-90%:** Sain, bon service
- **90%+:** Excellence
- **B2B SaaS/Software:** 75-80%+ (leader)
- **Construction/Distribution matériaux:** 70-75% benchmark raisonnable

**Dimensions à Mesurer (5 questions max):**
1. Satisfaction délai livraison
2. Qualité marchandise reçue
3. Clarté communication
4. Courtoisie équipe Gedimat
5. Probabilité réapprovisionner ailleurs? (mini-NPS)

**Template CSAT Gedimat 5 Questions:**
```
"Livraison commande #12345 - 16 novembre 2025"

1. Délai respect date promise?
   [ ] Très insatisfait [ ] Insatisfait [ ] Neutre [ ] Satisfait [ ] Très satisfait

2. Qualité produits/emballage?
   (même 5 choix)

3. Communication avant livraison?
   (même 5 choix)

4. Probabilité recommander Gedimat?
   (NPS 0-10 intégré)

5. Commentaire libre (raison insatisfaction si ≤3)
   [________________________________________]

Envoi: SMS 2h après livraison (courte fenêtre réponse)
```

**Timing Critique:** Sondage <6 heures après livraison (in-moment feedback maximise réponse taux 20-35%)

---

### 3. Méthodes Qualitatives - Entretiens & Focus Groups

**A. Entretiens Individuels Approfondis (IDI)**

**Quand:** Quarterly avec 8-10 clients clés (top artisans, entreprises BTP taille moyenne)

**Structure (30 min):**
- Ouverture: "Comment se passe votre approvisionnement chez nous vs concurrents?"
- Exploration: "Quel est votre plus gros pain? (délai, prix, qualité, communication)"
- Sondage: "Si on améliore X, cela change décision future?"
- Clôture: "Conseils spécifiques pour nous?"

**Avantage B2B:** Peut aborder enjeux sensibles (prix, exclusivité partenaire, problèmes relationnels)

**Gedimat Exemple IDI:**
- Interviewé: Patron entreprise couverture (client Gedimat 10 ans)
- Question clé: "Pourquoi cherchez-vous Point P en parallèle?"
- Réponse typique: "Délai plus court + garantie prix si volume annuel"
- Action: Clarifier termes Gedimat (engagement prix existence?)

**B. Focus Groups**

**Quand:** Semi-annuel avec 6-8 clients mix (petit/moyen, fidèles/churned)

**Structure (60 min modéré):**
1. **Icebreaker (10 min):** Historique commandes, problèmes rencontrés
2. **Thème 1 (15 min):** "Délai livraison - qu'est-ce qui compte vraiment?"
   - Possible découverte: "Pas délai absolu, mais prévisibilité - si 5j toujours = ok"
3. **Thème 2 (15 min):** "Communication retards - comment voulez-vous être alertés?"
   - Possible découverte: "SMS + appel humain. Emails, on lit pas"
4. **Thème 3 (15 min):** "Fidélité - qu'il faudrait pour partir concurrents?"
   - Possible découverte: "Garantie délai + après-vente technique = worth premium 5%"
5. **Synthèse (5 min):** Confirmation insights priorité

**Avantage Focus Groups:** Dynamique groupe révèle émotions, tensions réelles, découvertes inattendues

**Limitation B2B:** Participants occupés, préfèrent 1:1 vs groupe. Solution = petits groups 4-6 max, téléconférence acceptable

---

### 4. Suivi Réclamations Structuré (Beyond Negative-Only)

**Problème Gedimat Actuel:** Satisfaction mesurée uniquement en négatif (quand client crie)

**Approche Recommandée: Complaint Workflow Standardisé**

**Étape 1: Capture Structurée**
```
Chaque réclamation → CRM ticket (date, client, produit, type)
Catégories automatiques:
- Délai (commande non arrivée à date promise)
- Qualité (produit cassé/non-conforme livraison)
- Prix (facturation correcte?)
- Service (courtoisie, communication)
- Stock (indisponibilité non annoncée)
```

**Étape 2: Diagnostic Rapide**
```
Question immédiate: "Cause de cette réclamation?"
- Fournisseur livraison tardive? → action Éméris/Lafarge
- Transport retard? → action Médiafret
- Gedimat coordination? → action interne processus
- Client attente déraisonnable? → action éducation client
```

**Étape 3: Résolution & SLA**
```
SLA GEDIMAT PROPOSÉ:
- Réclamation délai: Réponse <24h, résolution compensation <72h
- Réclamation qualité: Échange <48h
- Réclamation prix: Remboursement <5 jours ouvrables
```

**Étape 4: Analyse Root Cause (Mensuel)**
```
Dashboard réclamations:
Janvier 2025: 12 total
  - Délai fournisseur: 6 (50%) → Réunion Éméris
  - Délai transport: 3 (25%) → Audit Médiafret routes
  - Coordination interne: 2 (17%) → Formation équipes
  - Client: 1 (8%) → Coaching contact

KPI Suivi: % réclamations résolues <SLA = cible 95%+
```

**Avantage:** Convertit data réclamations négatives en leviers amélioration proactive

---

### 5. Scoring de Relation Long Terme (Relationship Health Score)

**Concept:** Pas juste satisfaction un achat, mais santé globale relation partenariat multi-année

**Dimensions Mesure (Framework 4 Piliers):**

| Pilier | Métrique | Cible | Fréquence |
|--------|----------|-------|-----------|
| **Engagement Produit** | Volume annuel €, fréquence commande, ≠ catégories achetées | ↑ 5-10% an | Mensuel |
| **Utilisation Outil** | % clients utilisant extranet Gedimat, # appels vs email | ↑ 30% | Trimestriel |
| **Sentiment NPS** | NPS individuel client, trend +/- | NPS >50 | Trimestriel |
| **Risk Score** | Recherche concurrents? (mots-clés), paiement retard?, plaintes? | Risk <30% | Mensuel |

**Calcul Health Score (Simple):**
```
Health Score = (Engagement 25%) + (Utilisation 25%) + (NPS Sentiment 25%) + (Risk -25%)

Exemple Client Artisan X:
- Engagement: €12k/an ↑8% YoY = 25/25 points
- Utilisation: 45% connexions extranet = 15/25
- NPS: Score 7 dernier trimestre = 20/25
- Risk: Aucun signal = 0/-25 déduction
HEALTH SCORE = 60/100 → STABLE (vert)

Seuils Action:
- 70-100: VIP vert → Account manager priorité, offre spéciale rétention
- 50-69: STABLE jaune → Monitoring, contact trimestriel standard
- <50: ATAT RISQUE rouge → Intervention urgente, diagnostic raison churn
```

**Gedimat Implementation Pratique:**
1. **Feuille Excel simple** (4 colonnes × 100 clients) = suffisant pour départ
2. **Review mensuel** avec Angélique = identifier clients rouge
3. **Action spéciale** si chute rapide santé (ex. Artisan X: €12k → €6k derniers 2 mois)

**Avantage:** Identifie clients churn AVANT qu'ils partent (prévention vs réaction)

---

## SYNTHÈSE COMPARATIF: B2B vs B2C Mesure Satisfaction

| Aspect | B2B (Gedimat) | B2C (E-commerce) |
|--------|---------------|------------------|
| **Répondants** | Décideur unique (chef chantier) | Fragmentation (acheteur + utilisateur) |
| **Timing** | Relation long-terme, répétée | Transactionnel, une-off |
| **Drivers Satisfaction** | Délai + prix + fiabilité + service tech | Facilité achat + prix + flexibilité |
| **Méthode Primaire** | IDI 1:1, focus groups, NPS tracking | Surveys en masse, ratings 5 étoiles |
| **Sample Size** | Petit (50-100 clients clés), qualitatif riche | Grand (1000s), trends statistiques |
| **Feedback Loop** | Direct: Angélique appel client | Indirect: Système auto (pas contact) |
| **Churn Detection** | Proactive: Health Score + comportement volume | Réactive: Pas réachat détecté post-facto |

---

## RECOMMANDATIONS QUICK WIN GEDIMAT (90 jours)

**Semaine 1-2:** Implémenter NPS baseline
- Appel/SMS 30 clients pilotes: "Recommanderiez-vous Gedimat? 0-10"
- Classer Promoteurs/Neutres/Détracteurs
- Appeler 3-4 Détracteurs = raisons vraies

**Semaine 3-4:** Lancer CSAT template post-livraison
- SMS 2h après chaque livraison (lien court sondage 5 questions)
- Target: 30-40% taux réponse (normal B2B)
- Analyser patterns (délai pb? qualité? communication?)

**Semaine 5-8:** Créer Excel Health Score
- Colonnes: Client, Volume €, NPS, Risk Indicators, Action
- Review mensuel Angélique + PDG
- Identifier clients <50 points = intervention priorité

**Semaine 9-12:** Premier IDI qualitatif
- Appeler 5 meilleurs clients + 3 problématiques
- Questions: "Qu'on fait bien vs Point P? Où on failli?"
- Synthèse thèmes recurrents

**ROI Estimé:** Coût implémentation ~€2k, bénéfice prévention churn 1-2 clients valeur €50k+ >> ROI

---

## SOURCES CITÉES

1. **APQC (American Productivity & Quality Center).** 2024. Logistics Key Benchmarks - Distribution/Transportation Industry. https://www.apqc.org/
2. **RXO (Russell Tobin Logistics Operations).** 2024. Logistics KPI Research Study from 1,000+ Shippers & Carriers. https://rxo.com/
3. **NetSuite/Oracle.** 2023. Essential Logistics KPIs & Metrics. https://www.netsuite.com/
4. **B2B International.** 2025. Customer Satisfaction in B2B - CSAT Methodology. https://www.b2binternational.com/
5. **Retently.** 2025. CSAT Benchmarks & Calculation Guide. https://www.retently.com/
6. **CustomersGauge.** 2024. B2B NPS Benchmarks 2025 - Industrial Distribution. https://customergauge.com/
7. **Net Promoter Network.** 2024. NPS Benchmarks - Manufacturing & Industrial Sector. https://www.netpromoter.com/
8. **Leroy Merlin France.** 2025. Modes Livraison - Construction Materials. https://www.leroymerlin.fr/
9. **Qualtrics.** 2024. Customer Health Scores & Experience Management. https://www.qualtrics.com/
10. **Vitally.** 2024. How to Create Customer Health Score with 4 Metrics. https://www.vitally.io/
11. **Werk Insight.** 2024. B2B Qualitative Research Complete Guide. https://www.werkinsight.com/
12. **NewtonX.** 2024. In-depth Interviews for B2B Customer Satisfaction. https://www.newtonx.com/
13. **Chalmers University.** 2019. Fill Rate in Road Freight Transport - Academic Paper. https://publications.lib.chalmers.se/
14. **SCMDOJO.** 2024. Vehicle Utilization KPIs & Fleet Metrics. https://www.scmdojo.com/
15. **ELLA (European Logistics Learning Alliance).** 2023. Transport Cost Benchmarks France. Transport.ec.europa.eu

---

**Synthèse rédigée:** 16 novembre 2025
**Agent:** Pass 1 - Agent 3 (Indicateurs & Satisfaction)
**Statut:** ✅ Prêt passage Pass 2 (Primary Analysis Diagnostic)
