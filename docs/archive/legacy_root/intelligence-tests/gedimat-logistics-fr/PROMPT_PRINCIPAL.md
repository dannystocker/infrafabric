# Prompt Complet: Optimisation Logistique Gedimat - Session Claude Code Cloud
**Date:** 15 novembre 2025
**Méthodologie:** IF.search (8 passes) + IF.swarm (40 agents Haiku) + IF.guard (Conseil des Gardiens) + Académie Française
**Modèle:** Dossier Epic Games V4 (3 niveaux + plateau + debug)

---

## Mission Principale

Produire un **dossier complet, actionable et humble** pour Angélique (coordinatrice fournisseurs) et le PDG de Gedimat, analysant l'optimisation des enlèvements fournisseurs et affrètements externes, incluant:

- Analyse opérationnelle complète (IF.search 8 passes)
- Diagnostic des inefficiences actuelles
- Leviers d'optimisation avec arbitrages éclairés
- Modèles logistiques comparés (milkrun, cross-dock, consolidation, pooling)
- Métriques de satisfaction client B2B
- Recommandations décisionnelles graduées
- Français parfait (validation Académie Française)
- IF.TTT: toute affirmation vérifiable avec sources en annexe

---

## Contexte Opérationnel

### Géographie
- **3 dépôts Gedimat:** Lieu 271400 (probablement Évreux/Eure), Méru l'Oise 60110, Breuilpont 27xxx
- **1 magasin par dépôt** (dépôt = magasin)
- **Franchises Gedimat** (marque nationale, gestion locale)

### Contraintes Transport
- **≤10 tonnes:** Chauffeurs PL internes Gedimat (coût fixe salarial, très économique)
- **>10 tonnes:** Affrètement externe obligatoire (Médiafret + sous-traitants)
  - Exemple: 15t Méru + 5t Gisors = 20t total → transporteur externe
- **Semi-complet:** 25-30 tonnes (livraison 1 seul dépôt)
- **Navettes internes:** Redistribution entre dépôts (2×/semaine, coût salarial fixe)

### Problème Central
**Coût élevé des affrètements externes** quand commandes multiples dépôts dépassent 10t mais nécessitent transporteur unique.

**Arbitrage Actuel (source de conflit):**
- Dépôt avec le plus de volume veut livraison directe
- Mais dépôt plus proche du fournisseur = transport moins cher
- Urgences clients (chantier qui démarre) peuvent primer
- Coordination manuelle, tensions internes

### Points de Friction Identifiés
1. **Défense territoriale:** Chaque dépôt défend ses intérêts (volume ≠ urgence)
2. **Absence d'alertes automatisées:** Retards fournisseurs détectés manuellement
3. **Logiciel insuffisant:** Pas de statistiques, pas de suivi satisfaction, pas de scoring relationnel
4. **Relationnel critique:** Angélique connaît personnellement contacts fournisseurs/transporteurs (Mélissa chez Médiafret) - non documenté dans système
5. **Satisfaction client mesurée uniquement en négatif** (réclamations) - pas de feedback positif capturé

### Cas d'Échec Type
- Fournisseur Éméris (tuiles) retarde fabrication
- Marchandise arrive après date promise client
- Client annule commande, achète ailleurs
- Gedimat reste avec stock invendu + coût transport payé

### Objectif Dual
1. **Réduire coûts affrètement** (optimisation financière)
2. **Maintenir/améliorer satisfaction client** (fidélisation, pas seulement réduction coût)

---

## Méthodologie IF.search - 8 Passes Obligatoires

### Pass 1: Signal Capture (Recherche Primaire - 5 agents Haiku)
**Objectif:** Collecter données opérationnelles, bonnes pratiques secteur, benchmarks

**Recherches requises:**
1. Modèles logistiques distribution matériaux construction (France)
2. Optimisation multi-dépôts avec contraintes capacité transport
3. Milkrun / cross-dock / consolidation / pooling fret - applicabilité GSB (Grande Surface Bricolage)
4. KPI logistiques B2B: taux service, coût/tonne/km, délai moyen livraison, taux rupture
5. Mesure satisfaction client B2B distribution matériaux (NPS, CSAT, méthodes qualitatives)
6. Formules min/max stock (EOQ Wilson, stock sécurité, point commande) + évolutions ML/demand sensing
7. Systèmes WMS/TMS pour PME franchisées (intégration ERP Gedimat existant)
8. Pratiques gestion relationnelle fournisseurs/transporteurs (CRM, notes contextuelles)

**Livrables:** Synthèse recherche 2-3 pages, citations sources vérifiables

---

### Pass 2: Primary Analysis (Diagnostic Initial - 5 agents Haiku)
**Objectif:** Analyser situation actuelle, identifier inefficiences

**Axes d'analyse:**
1. **Cartographie flux:** Fournisseurs non-livreurs → 3 dépôts → clients
2. **Typologie commandes:** Distribution volume (0-5t, 5-10t, 10-20t, 20-30t, >30t)
3. **Répartition géographique:** Distances fournisseurs ↔ dépôts (si données disponibles)
4. **Coûts actuels:**
   - Chauffeur interne: €/heure (salarial fixe)
   - Affrètement externe: €/tonne ou €/trajet (variable Médiafret)
   - Navette interne: €/redistribution (salarial fixe)
5. **Taux urgence:** % commandes "express" dérogeant à optimisation coût
6. **Causes retards:** Fournisseur fabrication, transport, coordination interne

**Livrables:** Diagnostic structuré 3-4 pages, arbres de décision actuels

---

### Pass 3: Rigor (Validation Épistémologique - 3 agents Haiku + 1 Philosophe)
**Objectif:** Vérifier solidité des hypothèses, éviter biais confirmation

**Validations requises:**
1. **Hypothèse:** "Livrer dépôt le plus proche = toujours moins cher"
   - **Test:** Calculer coût transport fournisseur→dépôt A vs fournisseur→dépôt B + navette B→A
   - **Philosophe:** Locke (empirisme) - besoin données réelles, pas intuition

2. **Hypothèse:** "Dépôt avec plus de volume a priorité"
   - **Test:** Comparer impact urgence client (coût opportunité commande perdue) vs économie transport
   - **Philosophe:** Peirce (pragmatisme) - conséquences pratiques > règles fixes

3. **Hypothèse:** "Satisfaction client = réduction délais uniquement"
   - **Test:** Analyser réclamations - motifs (délai, communication, qualité, prix)
   - **Philosophe:** Quine (cohérentisme) - satisfaction = système cohérent (délai + communication + fiabilité)

**Livrables:** Matrice validation hypothèses, contradictions identifiées

---

### Pass 4: Cross-Domain (Expertise Multi-Domaines - 8 agents Haiku)
**Objectif:** Perspectives complémentaires (logistique, finance, client, SI, RH, juridique)

**Agent 1 - Logistique:**
- Modèles optimisation: TSP (Travelling Salesman), VRP (Vehicle Routing Problem), consolidation dynamique
- Seuils décision: quand affrètement externe devient rentable vs navette interne

**Agent 2 - Finance:**
- Coût complet affrètement: €/t, €/km, frais fixes, pénalités retard
- Coût opportunité: perte marge commande annulée vs surcoût transport express
- Analyse sensibilité: impact +10% coût transport sur marge globale

**Agent 3 - Satisfaction Client:**
- Mesure proactive satisfaction (appels post-livraison, sondages, NPS)
- Scoring urgence commande (chantier date fixe > rénovation flexible)
- Communication préventive retards (SMS, email alerte avec alternatives)

**Agent 4 - Systèmes Information:**
- Alertes automatisées: date livraison fournisseur dépassée, stock critique
- Dashboard temps réel: commandes en transit, charge dépôts, disponibilité chauffeurs
- API integration: Médiafret tracking, fournisseurs stock temps réel

**Agent 5 - Relationnel/CRM:**
- Documenter contacts clés (Mélissa Médiafret, responsables fournisseurs)
- Notes contextuelles: historique problèmes, accords informels, préférences
- Scoring fournisseurs: fiabilité délai, qualité, réactivité incidents

**Agent 6 - Ressources Humaines:**
- Gestion équitable charge travail chauffeurs internes
- Formation coordination (arbitrages, communication client)
- Incitations collaboration inter-dépôts (bonus satisfaction globale vs dépôt unique)

**Agent 7 - Juridique/Contrats:**
- Franchises Gedimat: autonomie vs directives centrales logistique
- Pénalités retard contractuelles (fournisseurs, transporteurs)
- Responsabilité marchandise en transit (assurances, litiges)

**Agent 8 - Compétitivité Marché:**
- Benchmark concurrents (Leroy Merlin, Castorama, Point P): délais moyens, promesses livraison
- Avantage différenciant: service premium (garantie délai) vs low-cost (délai flexible, prix réduit)

**Livrables:** 8 analyses domaine (1-2 pages chacune), synthèse contradictions

---

### Pass 5: Plateau (Synthèse Intermédiaire - 3 agents Haiku)
**Objectif:** Consolider acquis, identifier zones grises, préparer approfondissements

**Synthèse 3 volets:**

1. **Ce qu'on sait (haute confiance):**
   - Chauffeurs internes <10t très économiques
   - Affrètement externe >10t coûteux mais nécessaire
   - Navettes internes redistribution économiques
   - Satisfaction client = délai + communication + fiabilité
   - Relationnel Angélique = atout non documenté

2. **Ce qui reste flou (nécessite données):**
   - Répartition exacte commandes par tranche poids
   - Coûts réels comparés affrètement vs navette (€/t/km)
   - Taux satisfaction client actuel (baseline manquante)
   - Causes précises retards (fournisseur 60%? transport 20%? coordination 20%?)
   - Impact géographique: distances réelles fournisseurs ↔ dépôts

3. **Zones de tension (arbitrages nécessaires):**
   - Volume vs proximité vs urgence (3 critères compétitifs)
   - Coût transport vs satisfaction client (trade-off acceptable?)
   - Automatisation vs relationnel humain (quel équilibre?)

**Livrables:** Matrice connaissances (sait/flou/tendu), questions ouvertes

---

### Pass 6: Debug (Résolution Contradictions - 5 agents Haiku)
**Objectif:** Résoudre tensions identifiées, proposer arbitrages éclairés

**Contradiction 1: Dépôt prioritaire - Volume vs Proximité**
- **Règle proposée:** Scoring pondéré (40% proximité, 30% volume, 30% urgence client)
- **Calcul exemple:**
  - Dépôt A: 15t, 80km, urgence faible → Score = 0.3×15 + 0.4×(1/80) + 0.3×2 = ?
  - Dépôt B: 5t, 30km, urgence haute → Score = 0.3×5 + 0.4×(1/30) + 0.3×8 = ?
  - **Philosophe:** James (pragmatisme) - choisir ce qui fonctionne mieux en pratique

**Contradiction 2: Coût vs Satisfaction**
- **Règle proposée:** Seuil tolérance coût +20% si urgence client haute (chantier date fixe)
- **Rationale:** Perte client = perte récurrence (LTV) > économie ponctuelle transport
- **Philosophe:** Dewey (instrumentalisme) - satisfaction client = instrument fidélisation long terme

**Contradiction 3: Automatisation vs Relationnel**
- **Règle proposée:**
  - Automatiser: alertes délais, calculs coûts, suggestions dépôt optimal
  - Préserver humain: arbitrage final urgences, négociation fournisseurs, gestion crises
- **Philosophe:** Buddha (voie du milieu) - ni tout automatique, ni tout manuel

**Livrables:** Règles arbitrage documentées, exemples calculs, validation philosophique

---

### Pass 7: Deep Dive (Approfondissements Ciblés - 6 agents Haiku)
**Objectif:** Modèles détaillés, outils pratiques, recommandations actionnables

**Approfondissement 1: Modèle Décision Dépôt Optimal**
- **Algorithme:** Score multicritère pondéré
  ```
  Score_dépôt = w1×(Volume_tonnage) + w2×(1/Distance_km) + w3×(Urgence_client_1-10) + w4×(Disponibilité_stock_dépôt)
  ```
- **Poids recommandés:** w1=0.25, w2=0.35, w3=0.30, w4=0.10 (ajustables selon priorités PDG)
- **Outil:** Fichier Excel avec macro calcul automatique (fourni en annexe)

**Approfondissement 2: Dashboard Alertes & Suivi**
- **Alertes automatiques:**
  1. Retard fournisseur (date livraison ARC dépassée +1 jour)
  2. Stock critique dépôt (<seuil min définition par produit)
  3. Commande urgente non planifiée (chantier J-3, marchandise pas réservée)
  4. Coût transport >seuil budget mensuel
- **Indicateurs dashboard:**
  - Taux service (livraisons à temps / total)
  - Coût transport €/tonne moyen 30 jours glissants
  - NPS satisfaction client (si sondages implémentés)
  - Charge chauffeurs internes (heures, km, tonnage)

**Approfondissement 3: Processus Communication Client**
- **Avant livraison:** SMS confirmation date (J-2)
- **Retard détecté:** Appel proactif client (alternatives: attente, enlèvement magasin, fournisseur alternatif)
- **Après livraison:** Email/SMS satisfaction (échelle 1-5 + commentaire libre)
- **Gestion réclamation:** Workflow standardisé (enregistrement, traitement, suivi résolution, compensation si besoin)

**Approfondissement 4: Scoring Fournisseurs**
- **Critères:**
  1. Fiabilité délai (% livraisons à temps)
  2. Qualité produit (taux retour/défaut)
  3. Réactivité incidents (temps réponse, résolution)
  4. Flexibilité (urgent, petites quantités)
- **Actions:** Fournisseurs score <70% → réunion amélioration, si persistant → recherche alternatives

**Approfondissement 5: Formation Équipes**
- **Coordination inter-dépôts:** Ateliers arbitrage collaboratif (simulations cas réels)
- **Communication client:** Scripts appels retard, gestion objections, propositions alternatives
- **Utilisation outils:** Formation dashboard, saisie notes relationnelles, scoring urgence

**Approfondissement 6: Quick Wins (90 jours)**
1. **Semaine 1-2:** Implémenter alertes retard fournisseur (Excel + email automatique)
2. **Semaine 3-4:** Lancer sondage satisfaction 20 clients pilotes (template fourni)
3. **Semaine 5-8:** Former Angélique + 2 coordinateurs sur scoring dépôt optimal
4. **Semaine 9-12:** Dashboard mensuel coûts transport + taux service (PowerBI ou Excel)

**Livrables:** 6 fiches détaillées (2-3 pages), outils Excel/templates, planning 90 jours

---

### Pass 8: Meta-Validation (Conseil des Gardiens - 6 agents: CEO, Philosophe, Client, Auditeur, Innovateur, Académicien)
**Objectif:** Validation finale dossier, cohérence globale, qualité français

**Gardien 1 - IF.ceo/sam (PDG Perspective):**
- **Questions:**
  - Recommandations actionnables immédiatement sans CAPEX majeur?
  - ROI estimé optimisations (économies annuelles vs effort)?
  - Risque opérationnel changement processus (formation, résistance)?
- **Validation:** Dossier convaincant pour décision PDG? (oui/non, ajustements)

**Gardien 2 - Philosophe (Académie Française):**
- **Questions:**
  - Français parfait? Pas de anglicismes inutiles (KPI→indicateurs, dashboard→tableau de bord)?
  - Terminologie grounded (stock vs inventaire, fournisseur vs vendor)?
  - Clarté exposition (compréhensible non-expert logistique)?
- **Validation:** Langue irréprochable? (corrections inline)

**Gardien 3 - Gardien du Client:**
- **Questions:**
  - Client au centre recommandations? Pas seulement réduction coût?
  - Communication proactive retards bien définie?
  - Mesure satisfaction robuste (pas que réclamations)?
- **Validation:** Centricity client authentique? (oui/non, renforcements)

**Gardien 4 - Auditeur Épistémologique:**
- **Questions:**
  - Toutes affirmations vérifiables? (IF.TTT respect absolu)
  - Sources citées? (recherches Pass 1, benchmarks, formules)
  - Pas de bullshit? (éviter "solution innovante révolutionnaire" sans preuves)
- **Validation:** Annexe sources complète? (liste 20+ références minimum)

**Gardien 5 - Innovateur Pragmatique:**
- **Questions:**
  - Quick wins réalistes 90 jours?
  - Outils fournis utilisables (Excel, templates, scripts)?
  - Pas de recommandations "consultant classique" vagues?
- **Validation:** Actionnabilité maximale? (notation 1-10, justification)

**Gardien 6 - Joe Coulombe (Trader Joe's Founder - Humilité Client):**
- **Questions:**
  - Dossier humble? Pas "voici LA solution" mais "voici options, vous décidez"?
  - Angélique peut s'approprier? (pas jargon intimidant)
  - PDG peut présenter conseil administration? (synthèse exécutive 1 page)
- **Validation:** Humilité + appropriabilité? (oui/non, ton ajustements)

**Livrables:** Rapport validation 2 pages, corrections langue inline, matrice confiance (haute/moyenne/faible par recommandation)

---

## Architecture Swarm - 40 Agents Haiku

### Répartition Agents par Pass

| Pass | Nombre Agents | Rôle | Durée Estimée |
|------|--------------|------|---------------|
| 1 - Signal Capture | 5 | Recherche primaire (logistique, KPI, satisfaction, WMS, stock) | 20 min |
| 2 - Primary Analysis | 5 | Diagnostic (flux, coûts, inefficiences, causes retards) | 25 min |
| 3 - Rigor | 4 | Validation hypothèses (3 agents + 1 philosophe) | 15 min |
| 4 - Cross-Domain | 8 | Expertises (logistique, finance, client, SI, CRM, RH, juridique, marché) | 30 min |
| 5 - Plateau | 3 | Synthèse intermédiaire (sait/flou/tendu) | 15 min |
| 6 - Debug | 5 | Résolution contradictions (volume vs proximité, coût vs satisfaction, automatisation vs humain) | 20 min |
| 7 - Deep Dive | 6 | Modèles détaillés (algorithme scoring, dashboard, communication client, scoring fournisseurs, formation, quick wins) | 35 min |
| 8 - Meta-Validation | 6 | Conseil Gardiens (CEO, Philosophe, Client, Auditeur, Innovateur, Joe Coulombe) | 20 min |
| **Total** | **42** | (40 + 2 coordination) | **~3h** |

### Coordination Centrale (2 agents orchestrateurs)

**Agent Coordinateur Principal:**
- Lance passes séquentiellement (1→8)
- Collecte livrables chaque pass
- Détecte blocages (agent timeout, contradiction non résolue)
- Déclenche escalade si nécessaire

**Agent Synthétiseur Final:**
- Compile tous livrables en dossier unique structuré
- Génère table des matières, index citations, annexes
- Vérifie cohérence inter-passes (aucune contradiction Pass 2 vs Pass 7)
- Produit synthèse exécutive 1 page PDG

---

## Structure Dossier Final

### Partie 1: Synthèse Exécutive (1 page - PDG)
- Problème en 3 lignes
- 3 recommandations clés numérotées (quick wins, moyen terme, long terme)
- ROI estimé (€ économies annuelles, effort implémentation)
- Décision requise PDG (go/no-go, arbitrages)

### Partie 2: Contexte & Diagnostic (5-7 pages)
- Cartographie flux actuels (schéma)
- Analyse coûts (tableau comparatif chauffeur interne vs affrètement vs navette)
- Points de friction identifiés (5 principaux avec exemples)
- Causes retards (répartition % fournisseur/transport/coordination)

### Partie 3: Bonnes Pratiques Secteur (3-4 pages)
- Benchmarks distribution matériaux (délais moyens concurrents)
- Modèles logistiques applicables (milkrun, cross-dock, consolidation)
- KPI standards (taux service, coût/t/km, NPS B2B)
- Exemples réussite (cas Saint-Gobain, Lafarge, Point P si disponible)

### Partie 4: Recommandations Graduées (8-10 pages)

**Niveau 1 - Quick Wins (0-3 mois, effort faible, impact moyen):**
1. Alertes retard fournisseur (Excel + email auto)
2. Sondage satisfaction 50 clients pilote (template fourni)
3. Formation scoring dépôt optimal (Angélique + coordinateurs)
4. Dashboard mensuel coûts/taux service (Excel PowerBI)

**Niveau 2 - Moyen Terme (3-9 mois, effort moyen, impact élevé):**
1. Implémenter algorithme scoring multicritère (outil web simple ou Excel avancé)
2. Processus communication client standardisé (SMS avant/après, appels retard)
3. Scoring fournisseurs (fiabilité, qualité, réactivité)
4. Formation coordination inter-dépôts (ateliers arbitrage collaboratif)

**Niveau 3 - Long Terme (9-24 mois, effort élevé, impact structurel):**
1. WMS/TMS intégré ERP Gedimat (suivi temps réel, optimisation routes)
2. Partenariats transporteurs (contrats volume, SLA délais, pénalités)
3. Analytics prédictifs (ML demand sensing, prévision retards)
4. Programme fidélisation client B2B (garantie délai, compensation retards)

### Partie 5: Outils & Templates (10-15 pages annexes)
1. **Fichier Excel Scoring Dépôt Optimal** (formules pré-remplies, exemples)
2. **Template Sondage Satisfaction Client** (5 questions NPS + commentaires)
3. **Dashboard Mensuel PowerBI/Excel** (KPI prédéfinis, graphiques)
4. **Scripts Communication Client** (appel retard, email confirmation, SMS alerte)
5. **Grille Scoring Fournisseurs** (critères, pondérations, seuils actions)
6. **Planning 90 Jours Quick Wins** (Gantt semaine par semaine)

### Partie 6: Validation Philosophique (2-3 pages)
- Citations philosophes appliquées (Locke empirisme, Peirce pragmatisme, Quine cohérentisme, James instrumentalisme, Dewey expérimentalisme, Buddha voie milieu)
- Justification choix méthodologiques (pourquoi scoring multicritère vs règle fixe)
- Garde-fous épistémologiques (éviter biais confirmation, vérifier hypothèses données réelles)

### Partie 7: Annexe Sources (IF.TTT Compliance - 5-8 pages)
- **Minimum 25 sources citées:**
  1. Recherches académiques logistique (TSP, VRP, consolidation fret)
  2. Benchmarks secteur GSB (Leroy Merlin, Castorama rapports annuels)
  3. Formules stock (Wilson EOQ, safety stock, demand sensing)
  4. NPS B2B méthodologies (Harvard Business Review, Bain & Company)
  5. WMS/TMS solutions PME (comparateurs, études cas)
  6. Réglementations transport France (Code transport, assurances marchandises)
  7. Franchises Gedimat statuts (autonomie vs directives centrales)

**Format citations:** [Source, Année, Titre, URL/DOI si applicable]

### Partie 8: Glossaire & Abréviations (1 page)
- Éviter anglicismes:
  - KPI → Indicateurs clés performance
  - Dashboard → Tableau de bord
  - Warehouse → Entrepôt
  - Milkrun → Tournée laitière (si utilisé, expliquer)
- Définir termes techniques: EOQ, TSP, VRP, NPS, CSAT, WMS, TMS, cross-dock

---

## Validation Académie Française (Agent Final)

**Critères qualité langue:**
1. **Terminologie:** Français privilégié vs anglicismes (sauf si usage standard accepté)
2. **Clarté:** Phrases courtes (15-20 mots max), voix active préférée
3. **Grammaire:** Zéro faute orthographe, syntaxe, conjugaison
4. **Registre:** Professionnel mais accessible (éviter jargon inutile)
5. **Cohérence:** Terminologie uniforme (stock vs inventaire: choisir 1 terme, garder partout)

**Relecture complète inline avec corrections surlignées.**

---

## Contraintes Techniques Session Claude Code Cloud

### Limitations Contexte
- **Pas d'accès papers InfraFabric** → Utiliser méthodologies décrites dans prompt (IF.search, IF.swarm, IF.guard)
- **Session cloud limitée tokens** → Agents Haiku optimisés coût (1/3 Sonnet)
- **Pas d'accès données réelles Gedimat** → Utiliser exemples génériques, demander données si besoin précision

### Gestion Agents
- **Timeout:** 10 minutes par agent (connectivité train possible)
- **Retry:** Si agent timeout, relancer 1×
- **Échec multiple:** Signaler coordination, possibilité skip pass si bloquant

### Format Outputs
- **Markdown structuré** (titres ##, listes, tableaux)
- **Diagrammes texte** (ASCII art ou description pour outil externe: Mermaid, Lucidchart)
- **Fichiers séparés annexes** (Excel templates description structure, pas fichiers binaires)

---

## Estimation Taille Dossier Final

**Baseline:** 40-60 pages (hors annexes)

**Détail par section:**
- Synthèse exécutive: 1 page
- Contexte & Diagnostic: 5-7 pages
- Bonnes pratiques: 3-4 pages
- Recommandations graduées: 8-10 pages
- Outils & Templates: 10-15 pages (descriptions structures)
- Validation philosophique: 2-3 pages
- Annexe sources: 5-8 pages
- Glossaire: 1 page

**Annexes externes (fichiers descriptions):**
- 6 templates Excel/outils (10-15 pages descriptions)

**Total estimé:** **50-75 pages PDF** (format A4, police 11pt, marges standard)

---

## Instructions Lancement Session

### Étape 1: Préparation
1. Créer session Claude Code Cloud
2. Copier intégralité ce prompt
3. Confirmer disponibilité 40+ agents Haiku parallèles
4. Vérifier timeout 10 min par agent configuré

### Étape 2: Lancement
```
Prompt: [Coller intégralité prompt ci-dessus]

Demande confirmation avant exécution:
- Méthodologie comprise? (IF.search 8 passes validées)
- Architecture swarm OK? (42 agents répartition confirmée)
- Livrables clairs? (dossier 50-75 pages structure validée)
- Langue française parfaite? (Académie Française relecture finale)
- IF.TTT compliance? (25+ sources annexe obligatoire)
```

### Étape 3: Exécution
- Laisser agents travailler séquentiellement
- Monitorer progression passes 1-8
- Intervention uniquement si blocage signalé

### Étape 4: Livraison
- Dossier final Markdown
- Fichiers annexes descriptions (Excel, templates)
- Validation Académie Française inline
- Sources citées annexe (format standardisé)

---

## Philosophies Appliquées (Footnotes Dossier Final)

**Méthodologie IF.search inspirée:**
1. **Locke (Empirisme):** Données observables > intuitions [^1]
2. **Peirce (Pragmatisme):** Conséquences pratiques définissent vérité [^2]
3. **Quine (Cohérentisme):** Système cohérent > faits isolés [^3]
4. **James (Instrumentalisme):** Ce qui fonctionne = vrai [^4]
5. **Dewey (Expérimentalisme):** Tester hypothèses terrain [^5]
6. **Popper (Falsificationnisme):** Chercher à réfuter, pas confirmer [^6]
7. **Buddha (Voie Milieu):** Équilibre automatisation/humain [^7]
8. **Confucius (Harmonie):** Coordination collaborative > défense territoriale [^8]

**Footnotes exemples:**
[^1]: Locke, J. (1689). "Essay Concerning Human Understanding" - Validation empirique hypothèses Pass 3
[^2]: Peirce, C.S. (1878). "How to Make Our Ideas Clear" - Critères décision scoring multicritère Pass 6
[^3]: Quine, W.V.O. (1951). "Two Dogmas of Empiricism" - Cohérence système satisfaction client Pass 4
[etc.]

---

## Succès Critères

**Dossier réussi si:**
1. ✅ PDG peut présenter conseil administration (synthèse 1 page claire)
2. ✅ Angélique peut s'approprier (langage accessible, outils utilisables)
3. ✅ 3 quick wins actionnables <90 jours (effort faible, impact mesurable)
4. ✅ Français irréprochable (Académie Française validation)
5. ✅ IF.TTT compliance (25+ sources vérifiables annexe)
6. ✅ Philosophies citées contexte (8 footnotes minimum)
7. ✅ Humble (options présentées, décision laissée PDG/Angélique)

**Échec si:**
1. ❌ Jargon incompréhensible non-expert
2. ❌ Recommandations vagues ("améliorer communication") sans méthode précise
3. ❌ Aucune source citée (bullshit consultant classique)
4. ❌ Anglicismes excessifs (KPI, dashboard, warehouse partout)
5. ❌ Ton arrogant ("LA solution est...", "vous devez absolument...")

---

**Prêt lancement? Confirmer avant exécution swarm 42 agents.**
