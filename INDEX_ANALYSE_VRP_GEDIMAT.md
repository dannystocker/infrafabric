# INDEX - ANALYSE VRP & CONSOLIDATION LOGISTIQUE GEDIMAT
## Guide de Navigation et Points Clés

**Date :** Novembre 2025
**Statut :** Complet (2 documents, ~1 200 lignes)
**Public :** Équipe logistique, encadrement opérationnel, direction exploitation

---

## 📋 DOCUMENTS PRODUITS

### 1. **ANALYSE_VRP_CONSOLIDATION_GEDIMAT_2025.md** (2 pages)
**→ Lire EN PRIORITÉ pour décision rapide**

**Synthèse** (Page de couverture) :
- Opportunité principale : -78,7% coûts affrètement via consolidation
- Cas Émerge tuiles : 1 000€ affrètement → 213€ hub+navette
- Potentiel annuel : 50-100k€ économie + satisfaction client +15%
- **3 questions clés répondues avec chiffres concrets**

**Page 1 - Fondements Techniques :**
1. **Modèles VRP applicables** (MD-VRPBC formulation)
   - Formule mathématique optimisation multi-dépôts
   - 5 types de routes opérationnelles (coûts/délai)
   - Seuils quantitatifs consolidation (poids, délai, distance)

2. **Seuils de Consolidation** (Formules décision)
   - Quand regrouper 2+ commandes vs enlèvements séparés
   - Calcul ROI consolidation (cas Émerge détaillé : 786€ gain)
   - Tableau seuils empiriques calibrés Gedimat

3. **Algorithme Scoring Dépôt** (Multicritère)
   - Formule : 40% urgence + 30% pénalité + 20% volume + 10% distance
   - Remplace "volume prime" (biais actuel) par formule transparente
   - 3 cas applications concrètes (urgent, standard, flexible)

4. **Navettes - Optimisation** (2×/semaine vs flexible)
   - Coûts comparatifs 5 modes transport
   - Model actuel vs options (daily, 3-4×/week, chauffeur 3)
   - Recommandation : Rester 2×/sem + capacité ponctuelle +25t

**Page 2 - Applications Stratégiques :**
5. **Q1 : Milkrun Île-de-France Faisable ?**
   - ✓ OUI, 80%+ faisabilité
   - Consolider Émerge + Saint-Germaire + Leroy Merlin (1 tournée)
   - Économie : 1 030€/semaine = **53.5k€/an**
   - Implémentation : Test 4 semaines = faible risque

6. **Q2 : Hub Gisors Optimal ?**
   - ✓ OUI, meilleur choix (vs Montsouris/Paris)
   - Score 8,3/10 (localisation, infrastructure, couverture réseau)
   - Bénéfices : 65k€/an (réduction affrètement + satisfaction)
   - Payback : 14-18 mois (acceptable)

7. **Q3 : Algorithme Priorité Temps Réel ?**
   - ✓ Recommandation = HYBRIDE (pas dichotomie)
   - Filtre rapide (distance < 20km → navette)
   - Scoring dynamique (0,40U + 0,30P + 0,20V + 0,10D) pour autres
   - Gain temps : 3-5 min → 2 min (-60%)

**Roadmap 12 mois :**
- Q4 2025 : Scoring Excel + test 10 cas
- Q1 2026 : Milkrun + hub pilot + API intégration
- Q2-Q3 2026 : Déploiement complet
- Q4 2026 : Bilan +150-175k€ économies, service 95%+

---

### 2. **FORMULES_SEUILS_VRP_GEDIMAT_DETAILLES.md** (Annexe technique)
**→ Pour implémentation système & formation équipe**

**Section 1 - Seuils Consolidation Formules Précises**
- Formule binaire consolidation (coût isolé vs consolidé)
- Allocation proportionnelle coûts tournée
- Seuil empirique 10 tonnes (justification)

**Section 2 - Scoring Dépôt Détaillé**
- Normalisation variables U, P, V, D (0-1 échelle)
- Formule score pondérée (explications poids)
- Interprétation score ranges (0,75+, 0,50-0,75, <0,50)

**Section 3 - VRP Routing Algorithm**
- Problème milkrun Île-de-France (données entrée)
- Distance euclidienne calcul (coordonnées Gedimat)
- Nearest neighbor heuristique (algorithme glouton)
- Rerouting optimisation (2 véhicules vs surcharge)

**Section 4 - Coûts Comparatifs Formules**
- Formule affrètement Médiafret (base + distance + surcharge)
- Formule chauffeur interne (fixe + variable km + manutention)
- Formule navette marginal (transport interne coût variable only)
- Tableau 10 cas réels avec coûts/tonne

**Section 5 - Tableaux Opérationnels Poche**
- Matrice décision rapide (distance/tonnage/délai → action)
- Formules estimation 30 secondes (pour planificateurs)
- Procédure quotidienne Angelique (4 étapes)

**Section 6 - Étude Cas Réelle**
- Simulation semaine type (15 commandes)
- Regroupement 1 & 2 avec coûts détaillés
- Annualisation : 204k€ potentiel (50-100k€ conservateur)

---

## 🎯 POINTS CLÉS PAR AUDIENCE

### Pour Direction (PDG, DAF)
→ Lire : **Page 1 Synthèse Executive** + **Q1-Q3 Applications Stratégiques**

**Takeaways :**
- Levier principal : **Éliminer "volume prime" pour urgence-weighted scoring**
- Économie annuelle : **50-100k€** (baisse affrètement) + satisfaction client
- Investissement initial : 11-15k€ (Excel VRP + formation)
- ROI : 5-9× payback (6-18 mois selon levier)

### Pour Équipe Logistique (Angelique, Planificateurs)
→ Lire : **Sections 1-3 ANALYSE** + **Tableaux Opérationnels (Annexe Section 5)**

**Pratique immédiate :**
- Scoring formulaire Excel à implémenter → remplace intuition
- Seuils consolidation (10t, 48h délai, 100km max)
- Procédure quotidienne (7 min/commande vs 15 min ad-hoc)
- Milkrun test : 4 semaines IdF (priorité 1)

### Pour IT/Système
→ Lire : **Annexe Sections 2-3** + **Algorithme Routage Section 3**

**Développement :**
- Phase 1 (Mois 1-2) : Excel VBA scoring dynamique
- Phase 2 (Mois 3-6) : API légère SAP → calcul score automatique
- Intégration Google OR-Tools pour optimisation itinéraires
- Dashboard KPI mensuel (% navette, regroupement, coûts/t)

### Pour Encadrement Exploitation
→ Lire : **Page 2 Applications Q1-Q3** + **Roadmap 12 mois**

**Décisions immédiate :**
- Autoriser test milkrun Île-de-France (semaine 1-2 Jan 2026)
- Budget hub Gisors pilot : 98k€ infrastructure (ROI 14-18 mois)
- Recrutement chauffeur 3 : décision après test consolidation

---

## 📊 TABLEAU SYNTHÈSE ÉCONOMIES

| Levier | Bénéfice Annuel | Investissement | Payback | Priorité |
|--------|---|---|---|---|
| **Scoring multicritère** | 50k€ | 11k€ | 6-7 mois | 🔴 1 |
| **Milkrun IdF** | 54k€ | 2k€ | 1-2 mois | 🔴 2 |
| **Hub Gisors** | 65k€ | 98k€ | 14-18 mois | 🟡 3 |
| **Navettes flexibles** | 6k€ | 3k€ | 6 mois | 🟡 4 |
| **Chauffeur 3** | 20k€ (net) | 46k€/an | 18 mois | 🟢 5 |
| **TOTAL ANNÉE 1** | **150-175k€** | **~130k€** | **7-12 mois** | ✓ |

---

## 🚀 QUICK START - IMPLÉMENTATION IMMÉDIATE

### Semaine 1 (Nov 2025)
- [ ] Réunion équipe logistique : présenter scoring multicritère
- [ ] Créer formulaire Excel scoring (15 min formules)
- [ ] Identifier 5 cas tests Émerge/Saint-Germaire

### Semaine 2-3
- [ ] Appliquer scoring 5 cas, comparer vs intuition
- [ ] Calcul ROI consolidation (mesurer réelle economie)
- [ ] Validation avec Angelique : scoring fait-il sens ?

### Semaine 4
- [ ] Go/no-go décision milkrun test (semaine 1 Jan 2026)
- [ ] Budgétisation hub Gisors (si résultat scoring positif)
- [ ] Formation équipe nouvelle procédure (7 min/commande)

---

## 📚 FICHIERS ASSOCIÉS (Context Gedimat Existant)

Lire aussi pour contexte complet :
1. `DIAGNOSTIC_FLUX_LOGISTIQUES_GEDIMAT.md` - Cartographie actuelle flux
2. `ANALYSE_COUTS_TRANSPORT_GEDIMAT_2025.md` - Coûts détaillés baseline
3. `AIDE_DECISION_RAPIDEE_DEPOT_MODE_TRANSPORT.md` - Aide décision existante
4. `ANALYSE_PRAGMATIQUE_PRIORITE_DEPOT_VOLUME_VS_URGENCE.md` - Réfutation "volume prime"
5. `GEDIMAT_CALCULS_OPERATIONNELS.md` - Exemples calculs stock (context)

---

## ❓ FAQ

**Q: Quand démarrer implémentation ?**
A: Immédiatement (Nov 2025). Étape 1 = Excel scoring (3k€, 2 semaines). ROI 6-7 mois très rapide.

**Q: Faut-il un logiciel TMS complet ?**
A: Non. Excel VBA suffit phase 1-2. TMS lourd (SAP) optionnel après validation.

**Q: Hub Gisors remplace dépôts existants ?**
A: Non. C'est MICRO-HUB transbordement 12-24h, pas stock long terme. Dépôts gardent fonction complète.

**Q: Milkrun augmente délai client ?**
A: Non. Délai J+2-3 acceptable (milkrun collecte optimisée). Gagnes -78% coûts.

**Q: Et si fournisseur retard dans milkrun ?**
A: Tournée décalée 1-2 jours (délai still J+2-4). Client notifié proactivement. Acceptable non-urgent.

---

## 📞 CONTACTS & PROPRIÉTÉ

- **Rédacteur :** Équipe Optimisation Logistique Gedimat
- **Date :** Novembre 2025
- **Confidentiel :** Gedimat interne only
- **Question technique :** Voir Angelique (logistique) ou Section 5 Annexe

---

**Fin d'INDEX – Navigation facile des 2 documents d'analyse VRP**
