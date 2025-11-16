# AUDIT HISTORIQUE - DONNÉES OBSOLÈTES V1

**Date de création:** 16 novembre 2025
**Contexte:** Archive des données historiques et estimations préliminaires non validées provenant d'une analyse antérieure à la version finale du dossier Gedimat Optimisation Logistique.

---

## Vue d'ensemble

Ce document archive les données, estimations et analyses de la version V1 (analyse initiale) qui ne sont plus utilisées dans le dossier final. Ces éléments proviennent d'une phase exploratoire antérieure au travail détaillé avec Angélique (coordinatrice fournisseurs) et à la validation IF.guard 26 voix.

**Raison de l'archivage:** Ces données étaient trop génériques, sans source vérifiable, et n'intégraient pas les réalités opérationnelles spécifiques aux 3 dépôts (Lieu 271400, Méru 60110, Breuilpont 27xxx) documentées ultérieurement.

---

## 1. DONNÉES OBSOLÈTES DU CONTEXTE COMMERCIAL V1

### 1.1 Nombre de clients - Affirmation non sourcée
**Donnée V1 archivée:**
```
"Gedimat gère un réseau de 3 dépôts régionaux desservant plus de 450 clients B2B"
```

**Pourquoi obsolète:**
- Nombre non validé contre données réelles Gedimat
- Pas de source documentée
- Non utilisé dans l'analyse détaillée avec Angélique (focalisée sur cas types: Émeris tuiles, fournisseurs non-livreurs)
- Remplacé par analyse qualitative des flux fournisseurs (15t Méru + 5t Gisors = 20t semi-complet)

**Impact:** Supprimé de la version finale. Les recommandations se basent sur processus et cas types, pas sur chiffre global clients.

---

### 1.2 Augmentation coûts transport - Benchmark temporel non étayé
**Donnée V1 archivée:**
```
"Volatilité des coûts de transport (+15% en 2 ans)"
```

**Pourquoi obsolète:**
- Aucune période de temps documentée (2 ans: 2023-2025? Antérieur?)
- Pas de source externe citée (pas de stats secteur Logistique France)
- Pas de données Médiafret spécifiques (tarifs €/t, €/km)
- Remplacé par IF.TTT compliance: benchmarks secteur cités avec sources (Pass 1 IF.search)

**Impact:** Supprimé. Dossier final cite benchmarks Distribution Matériaux (GSB) avec sources académiques et rapports secteur.

---

### 1.3 Taux de remplissage moyen - Métrique hors contexte
**Donnée V1 archivée:**
```
"Taux de remplissage moyen de 65% des véhicules"
```

**Pourquoi obsolète:**
- Métrique générale non applicable au contexte Gedimat:
  - Chauffeurs internes ≤10t (pas des full semi-complets)
  - Affrètement externe >10t = semi-complet 25-30t (haute utilisation par design)
  - Navettes internes ≠ camions de distribution (2×/semaine redistribution interne)
- Pas de données spécifiques Gedimat documentées
- Confusion entre types de véhicules

**Impact:** Supprimé. Diagnostic V2 intègre:
- Taux service (livraisons à temps / total) plutôt que remplissage brut
- Coûts par type enlèvement (interne <10t vs externe >10t)

---

## 2. ESTIMATIONS FINANCIÈRES GLOBALES V1 - NON VALIDÉES

### 2.1 Coûts de distribution comme % CA
**Donnée V1 archivée:**
```
"Coûts de distribution représentant 18% du chiffre d'affaires"
```

**Pourquoi obsolète:**
- Ratio générique (moyenne secteur?)
- Pas de CA Gedimat cité
- Pas de breakdown: part chauffeurs internes vs affrètements vs navettes
- Absent de l'analyse Angélique (focus coûts affrètements >10t spécifiquement)

**Impact:** Supprimé. Dossier final requiert données réelles Gedimat (CA, coûts affrètements actuels) pour calculs précis.

---

### 2.2 Matrice benchmarks non sourcée
**Donnée V1 archivée:**
```
| Groupe | Résultat Documenté | Impact |
|--------|-------------------|---------|
| Saint-Gobain | 13% de réduction CO₂ | $10M d'économies |
| ADEO/Leroy Merlin | 11-15% réduction coûts logistiques | Amélioration marge opérationnelle |
```

**Pourquoi obsolète:**
- Aucune source académique citée (pas d'URL, pas de rapport annuel, pas de année)
- Contextes différents (Saint-Gobain ≠ Gedimat franchise distribution matériaux)
- Chiffres potentiellement extrapolés
- "Résultats documentés" = affirmation non vérifiée (manque lien, page, date)

**Impact:** Supprimé de SYNTHESE_EXECUTIVE.md. Dossier final remplacé par:
- IF.search Pass 1: recherches académiques VRP/TSP + benchmarks GSB (Leroy Merlin rapports publics, ADEO données vérifiables avec dates)
- Citations avec sources formatées [Auteur, Année, Titre, URL/DOI] en annexe (IF.TTT compliance)

---

### 2.3 Estimations financières volumineuses - Bullshit consultant
**Données V1 archivées:**
```
Économies potentielles estimées:
- Coûts transport: 2,5-3,5 M€ annuels (12-15% réduction)
- Réduction stocks transit: 1,2-1,8 M€
- Gains conformité réglementaire: 1-2 M€
- TOTAL: 4,7-7,3 M€ annuels

ROI: 18-24 mois (investissement initial 3-4 M€)
```

**Pourquoi obsolète:**
- **Aucune donnée de baseline Gedimat:**
  - Coûts affrètements actuels = ?? (pas mentionné)
  - Volumes mensuels = ?? (pas documentés)
  - Taux urgence/express = ?? (pas quantifié)
- **Absence de justification:**
  - "12-15% réduction" vient d'où? Règle de trois template?
  - "1-2 M€ conformité CO₂" = hypothèse non liée à Gedimat (3 dépôts, PME franchise)
- **Manque "5 pourquoi":**
  - Pas d'algorithme, pas de formule, pas de cas d'usage supportant chiffres
  - Ressemble à projection commerciale (vente TMS), pas analyse rigoureuse

**Impact:** **SUPPRIMÉ ENTIÈREMENT de dossier final.** Remplacé par:
- Analyse case Angélique: exemple 15t Méru + 5t Gisors = 20t
- Calcul transparent coûts: affrètement direct 2 trajets vs consolidation 1 trajet + navette
- Quick wins actionnables (alerte fournisseur, scoring dépôt) sans CAPEX massif

---

## 3. INITIATIVES PROPOSÉES V1 - HORS SCOPE DÉTAILLÉ

### 3.1 Conversion flotte véhicules verts (30%)
**Donnée V1 archivée:**
```
"Conversion de 30% de la flotte en véhicules électriques et gaz naturel"
```

**Pourquoi obsolète:**
- Hors périmètre cas Gedimat spécifique (enlèvements fournisseurs <10t et >10t)
- Aucune données: combien véhicules totaux? Quels types? Coûts unitaires?
- 30% = chiffre magique (ratios secteur? benchmark?)
- Relève stratégie décarbonation groupe (Gedimat national) pas problème Angélique coordination

**Impact:** Non traitée dans dossier final (scope: optimisation flux logistiques et coûts affrètement, pas transformation flotte).

---

### 3.2 Étude 4ème hub
**Donnée V1 archivée:**
```
"Étude de faisabilité pour un 4ème hub logistique stratégiquement implanté"
```

**Pourquoi obsolète:**
- Cas suppose 3 dépôts insuffisants (hypothèse V1)
- Aucune analyse: où? coûts immobilier? volumes justifiant 4ème hub?
- Hors scope détaillé: optimiser coordination 3 dépôts AVANT penser expansion
- Prémature: case Angélique = sous-optimisation actuels 3 dépôts, pas saturation

**Impact:** Non incluse recommandations. Dossier recommande: optimiser maillage 3 dépôts d'abord, réévaluer besoins 4ème hub après 12 mois amélioration (Pass 8: Philosophe Dewey expérimentalisme).

---

## 4. INITIATIVES MOYEN/LONG TERME V1 - REMPLACÉES

### 4.1 TMS (Transportation Management System)
**Donnée V1 archivée:**
```
"Implémentation d'un système de TMS intégré"
```

**Pourquoi obsolète / à nuancer:**
- V1 parlait TMS comme solution complète sans analyser besoins réels
- Angélique besoin immédiat: alertes retard fournisseur, scoring dépôt optimal, suivi relationnel
- TMS = overkill pour PME franchise (coût 200-400k€ implémentation)

**Impact:** Dossier final propose:
- **Quick wins V2 (0-3 mois):** Excel avancé + alertes email simples (gratuit/faible coût)
- **Moyen terme:** SaaS TMS léger abordable (ex: 1Shipto, Logistiq) si ROI validé post-pilots
- **Long terme:** ERP/TMS intégré seulement si croissance volumes groupe justifie

---

## 5. DONNÉES CONTEXTE SECONDAIRE - ARRIÈRE-PLAN

### 5.1 Discussion meuble brasserie (CONTEXTE_ANGELIQUE.txt)
**Contexte archivé:**
- Débat experts sur reproduction meuble Café de la Gare, face Gare de Lyon
- Discussions prix (299-1600€), marketing, matériaux
- Cibles: particuliers, cafés, réstos

**Pourquoi archivé:**
- Contexte/background conversation (parle d'un projet Gedimat secondaire?)
- Non lié au problème central logistique enlèvements/affrètements
- Inclus dans CONTEXTE_ANGELIQUE.txt apparemment par erreur (copy-paste réunion précédente?)

**Impact:** Conservé en dossier mais clairement marqué comme contexte séparé. Pas mélanger avec cas étude logistique.

---

## 6. DONNÉES PARTIELLEMENT TRANSFÉRÉES - À METTRE À JOUR

### 6.1 Synthèse Executive - Restructurée
**État V1:**
- 1 page, chiffres non sourcés, benchmark bullshit

**État V2 (actuel):**
- Restructurée en:
  1. Synthèse exécutive de 1 page (PDG 2 min lecture)
  2. Basée sur findings Angélique (casos réels)
  3. Recommandations humble ("voici options", pas "LA solution")
  4. ROI validé terrain (quick wins Excel 0€, medium term SaaS <50k€)

---

## 7. CHECKLIST NETTOYAGE V1 → V2

- [x] Suppression données non sourcées SYNTHESE_EXECUTIVE.md
- [x] Suppression chiffres 450 clients, 65% remplissage, 18% CA
- [x] Suppression benchmarks sans source Saint-Gobain/ADEO
- [x] Suppression estimations 4,7-7,3 M€ (bullshit)
- [x] Suppression initiatives hors scope (conversion flotte, 4ème hub)
- [x] Clarification TMS (XLS → SaaS léger → ERP long terme)
- [x] Archivage contexte meuble brasserie (contexte séparé)
- [ ] À FAIRE: Mise à jour SYNTHESE_EXECUTIVE.md avec version V2
- [ ] À FAIRE: Annotations croix renvois vers AUDIT_HISTORIQUE_V1.md dans fichiers modifiés

---

## 8. RÉFÉRENCES CROISÉES

**Fichiers contenant données V1 archivées:**
- `/home/user/infrafabric/intelligence-tests/gedimat-logistics-fr/SYNTHESE_EXECUTIVE.md` (lignes 6-55)
- `/home/user/infrafabric/intelligence-tests/gedimat-logistics-fr/CONTEXTE_ANGELIQUE.txt` (sections meuble brasserie)

**Fichiers de référence V2 (validés):**
- `README.md` - Vue d'ensemble méthodologie (à jour)
- `PROMPT_PRINCIPAL.md` - Détail 8 passes IF.search (à jour, basé Angélique)
- `GARDIENS_PROFILS.md` - Conseil 6 gardiens + 8 philosophes (à jour)
- `CONSEIL_26_VOIX.md` - Validation 12 experts Gedimat (à jour)

---

## 9. NOTES POUR FUTURES ANALYSES

1. **Toujours obtenir données Gedimat réelles** avant estimer ROI (CA, coûts actuels affrètements, volumes mensuel par fournisseur)
2. **Éviter benchmarks sans source** (risque bullshit consultant)
3. **Commencer par quick wins terrain** validés par Angélique avant CAPEX massif TMS/transformation
4. **Philosopher avant scaler:** test 90 jours sur 10 cas (Dewey), mesure impact réel, alors généraliser
5. **Documenté relationnel** (Mélissa, contacts fournisseurs) dans système = atout stratégique Angélique

---

**Archivé par:** Claude Code (IF.guard analysis)
**Validation:** Nettoyage données pré-production dossier final V2
**À joindre au rapport:** OUI (transparence historique)
