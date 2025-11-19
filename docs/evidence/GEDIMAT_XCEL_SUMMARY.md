# Gedimat XCEL – Xpérience Client & Excellence Logistique

## 1. Synthèse stratégique (PDG)

- Objectif : transformer un problème logistique récurrent (affrètements coûteux, retards, incidents clients) en **avantage concurrentiel de fidélisation**.
- Principe : créer une fonction transversale **XCEL (Xpérience Client & Excellence Logistique)** jouant le rôle de **tour de contrôle** entre Vente, Dépôts et Transport.
- Périmètre : 3 dépôts, enlèvements fournisseurs non livreurs, arbitrage affrètement externe vs. navettes internes, incidents clients B2B.
- Approche : démarrer par un **pilote 90 jours** (alertes, règle de proximité, scoring, gestes relationnels) + cadrage d’une fonction XCEL claire, mesurable et documentée.
- Résultat attendu : moins de chaos pour les équipes, moins de doublons d’affrètement, plus de clients qui restent (et recommandent) après incident bien géré.

> Ce document est un résumé « lisible PDG & équipes » du dossier complet  
> `GEDIMAT_ARENA_REVIEW_COMPLETE_V3.2.md` (intelligence-tests/gedimat-logistics-fr).

---

## 2. XCEL en une page

### 2.1 Rôle

- **But** : garantir que ce qui est vendu est livré comme promis, sans surcharger les commerciaux.
- **Image** : XCEL = **conducteur de travaux des flux clients** (ni vendeur, ni chauffeur, mais chef d’orchestre).
- **Position** : interface **interne** entre Commerciaux, SAV, Dépôts et Transport, avec une vue unique sur les commandes sensibles.

### 2.2 Missions clés

- **Pilotage des flux**
  - Vérifier la faisabilité transport des commandes atypiques.
  - Choisir le dépôt optimal selon la **règle de proximité** et les contraintes de tournée.
  - Coordonner affrètements et navettes inter‑dépôts.
- **Suivi des incidents**
  - Centraliser les alertes (ARC/ACK, J‑1, retards).
  - Préparer les arbitrages (report, express, substitution).
  - Suivre chaque incident jusqu’à résolution.
- **Interface interne pour Commerciaux/SAV**
  - Servir de point de contact unique pour les problèmes de livraison.
  - Libérer du temps de vente en évitant que chaque commercial « refasse la logistique » au téléphone.
- **Traçabilité & indicateurs**
  - Tenir un journal des dérogations à la règle de proximité.
  - Alimenter un tableau de bord simple (Service, Coût, Incidents).

### 2.3 Périmètre de décision

- **Peut :**
  - Arbitrer le dépôt d’expédition.
  - Séquencer les livraisons (ordre, jour J/J+1).
  - Proposer une substitution produit équivalente documentée.
- **Ne peut pas :**
  - Accorder des remises ou modifier les prix.
  - Modifier les CGV.
  - Promettre un créneau horaire hors grille sans validation du dépôt concerné.

---

## 3. Indicateurs clés (KPI XCEL)

### 3.1 Définitions

- **OTIF (On Time In Full)**  
  % des commandes B2B livrées :
  - à l’heure (fenêtre ≤ **+30 min** vs. horaire confirmé)  
  - et complètes (lignes livrées ≥ **99 %**).

- **Incident clos en J+1**  
  Incident logistique (retard, erreur dépôt, quantité manquante) pour lequel un plan d’action est défini et appliqué au plus tard à **J+1**.

### 3.2 Pack minimal de KPIs

- **OTIF B2B prioritaire**  
  - Base T0 : à mesurer sur 30 jours.  
  - Cible pilote : **+5 à +8 points**.
- **Incidents clos en J+1**  
  - Base T0 : à mesurer.  
  - Cible : **≥ 85 %** des incidents standard.
- **Affrètements « évitables » / mois** (double affrètement, mauvais dépôt)
  - Base T0 : à extraire des factures Médiafret.  
  - Cible : **–30 %**.
- **Changements de dernière minute** (> X h avant enlèvement)
  - Base T0 : nombre de changements forcés par semaine.  
  - Cible : **–40 %**.
- **Temps commercial consacré aux incidents**  
  - Mesure simple : nb d’appels / logs incidents par commercial et par semaine.  
  - Cible : **–35 %**.
- **% de dérogations documentées**  
  - Base T0 : souvent faible / implicite.  
  - Cible : **100 %** avec motif + estimation de surcoût.

---

## 4. Vue opérationnelle (schéma J0 → J+1)

*(Diagramme logique – à représenter en swimlane ou Graphviz)*  

1. **Vente**
   - Saisit commande + date / fenêtre souhaitée.
   - Taggue « client sensible » si applicable.
2. **XCEL**
   - Vérifie disponibilité stock J0/J+1.  
   - Applique la règle de proximité pour choisir le dépôt.  
   - Crée l’alerte si ARC/ACK manquant ou risque de retard.
3. **Dépôt**
   - Confirme ou ajuste le plan (capacité, tournées).  
   - Valide ou refuse les dérogations demandées.
4. **Transport**
   - Affrètement externe si >10 t ou cas spécifique.  
   - Navette inter‑dépôts si besoin de redistribution.
5. **XCEL (suivi incident)**
   - Surveille les alertes J‑1 et J0.  
   - Escalade si incident non résolu (Dépôt → Direction).
6. **Retour Commerciaux / SAV**
   - Informés proactivement (succès ou problème).  
   - Ne gèrent que les cas client vraiment relationnels.

---

## 5. Pilote 90 jours – résumé exécutable

- **Semaines 1–2** :  
  - Définir champs de données minimum (dates, dépôt, ARC/ACK, exceptions).  
  - Mettre en place les alertes simples (emails / règles).
- **Semaines 3–4** :  
  - Tester la règle de proximité sur ~50 commandes, ajuster.  
  - Valider la mesure OTIF et incidents J+1.
- **Semaines 5–8** :  
  - Généraliser l’usage de la règle + journaliser les dérogations.  
  - Commencer le suivi des affrètements « évitables ».
- **Semaines 9–12** :  
  - Calculer les KPIs (OTIF, affrètements, incidents, temps commerciaux).  
  - Décider : généralisation, ajustements, extension du périmètre XCEL.

Conditions de validation pour passer en Phase 2 (moyen terme) :  
au moins **3 KPIs sur 5** atteignent ≥ 90 % de leur cible.

---

## 6. Annexes – liens & extraits

### 6.1 Dossier complet Gedimat (v3.2)

- `intelligence-tests/gedimat-logistics-fr/GEDIMAT_ARENA_REVIEW_COMPLETE_V3.2.md`  
- Contenu : version intégrale (sections 1–10, annexes X/Y/Z, métriques détaillées, références externes).

### 6.2 Prompts d’évaluation LLM (IF.council)

- Reorg / stratégie infra (référence)  
  - `docs/evidence/IF_council_llm_arena_reorg_prompt.md`
- Marketing / promesses publiques  
  - `docs/evidence/IF_council_llm_arena_marketing_prompt.md`
- Corpus d’audit / transparence  
  - `docs/evidence/IF_council_llm_arena_audit_corpus_prompt.md`
- Licensing Yologuard (structure IF.council, réutilisable pour XCEL si besoin)  
  - `docs/evidence/IF_council_llm_arena_licensing_prompt.md`  
  - `docs/evidence/IF_llm_arena_licensing_single_prompt.md`

*(Pour un test ciblé du dossier Gedimat, adapter ces prompts avec la question A/B/C « Dossier prêt pour Conseil d’Administration ? ». )*

### 6.3 Visuals suggérés

- `Gedimat-XCEL-LOGO.png` – sceau « XCEL – Excellence Logistique ».  
- Schéma J0→J+1 (swimlane) – ventes / XCEL / dépôts / transport.  
- Tableau simple « Règle standard vs. dérogations typiques » (3–5 lignes).

