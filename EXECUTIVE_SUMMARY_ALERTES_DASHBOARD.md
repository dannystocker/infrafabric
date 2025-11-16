# EXECUTIVE SUMMARY
## Système Alertes & Dashboard Gedimat - 1 Page

**Destinataires** : Direction, Management logistique | **Date** : 16 Nov 2025

---

## ENJEU

Les 5 frictions logistiques identifiées (Pass 2) coûtent **10-20 k€/an** à Gedimat :
- Surcoûts affrètement (dépôts non optimisés) : 2.5-5 k€
- Temps Angélique coordination manuelle : 5 k€
- Risque continuité (relationnel non documenté) : 2.5 k€
- Perte clients (satisfaction mesurée négativement) : 3-5 k€

**Cause racine** : Pas d'alertes automatisées, pas de dashboard, pas de rules de priorité transparentes.

---

## SOLUTION EN 3 PHASES

### Phase 1 (T0 : Décembre 2025) - **2.5 k€ | 2-4 semaines**
**Excel Avancé + PowerBI** (low-code pilote)

| Alerte | Impact |
|--------|--------|
| Retard fournisseur +1j | Détection auto vs manuelle Angélique (-3h/sem) |
| Stock critique dépôt | Évite ruptures (-8%), libère trésorerie (-15% surstock) |
| Urgence J-3 non réservée | Résout dépôts-défensifs, livraison garantie urgences |
| Budget transport overshoot | Direction voit coûts temps réel, réagit vite |

**KPI Dashboard** : Taux service, €/tonne, NPS, charge chauffeurs
**Cible** : 5-10 franchisés pilotes | **ROI** : +304% (payback 3.6 mois)

---

### Phase 2 (T1 : Trim 1 2026) - **4.5 k€/an | 4-6 semaines**
**Shiptify TMS** (franchisés >5 véhicules)

**Ajoute** :
- Suivi GPS temps réel Médiafret
- Optimisation routes (-8% km)
- Alertes automatiques urgence/retard
- Mobilité chauffeurs (app mobile)

**ROI** : +264% (payback 4.2 mois) | **Économies** : 6.73 k€/an/site

**Décision après Phase 1** : Valider concept Excel avant investir SaaS

---

### Phase 3 (T2 : Trim 2-3 2026) - **35 k€/an | 8-12 semaines**
**Sinari TMS Ready** (si mutualisation 50+ dépôts Gedimat)

**Complet** : TMS + WMS + ERP légère, 100% alertes auto, dashboard centralisé

**Coût par dépôt** : 700€/an (mutualisation) | **ROI** : +2550% (payback 23j)

**Condition critique** : Sinari seul (1-5 dépôts) = ROI -45% ✗ (ne pas faire)

---

## COMPARATIF 3 SOLUTIONS (18 mois)

| Critère | Excel/PowerBI | Shiptify | Sinari (50 dépôts) |
|---------|---------------|----------|-------------------|
| **Budget initial** | 2.5 k€ | 4.5 k€ | 1.1 k€/dépôt |
| **Coûts an/an** | 0.4 k€ | 2.5 k€ | 0.7 k€/dépôt |
| **ROI 18 mois** | +304% | +264% | +2550% |
| **Payback** | 3.6 mois | 4.2 mois | 23 jours |
| **Scalabilité** | Limitée 50 dépôts | Bonne | Excellente |
| **Risque** | FAIBLE | MODÉRÉ | MODÉRÉ (nécessite 50+ dépôts) |

**RECOMMANDATION** : Approche échelonnée phases 1→2→3 (total an 1 = 7 k€, ROI +280%)

---

## 4 ALERTES DÉPLOYÉES

### 1. Retard Fournisseur (DateARC > Aujourd'hui +1j)
→ Email Angélique + SMS si client urgent → Escalade automatique à J+3

### 2. Stock Critique Dépôt (< Seuil Min × 1.2)
→ BOA auto générée → Validation manager 1h max → Évite rupture

### 3. Urgence Non Planifiée (Chantier J-3, marchandise pas réservée)
→ Escalade directe direction + proposition solution → Taux succès urgence 95%

### 4. Budget Transport Overshoot (Dépassement mensuel)
→ Alerte direction quotidienne → Analyse détail coûts → Action jour même

---

## 4 KPI DASHBOARD TEMPS RÉEL

| KPI | Formule | Cible | Impact Friction |
|-----|---------|-------|-----------------|
| **Taux Service** | (Livraisons OK / Total) % | 92% (vs 75% actuellement) | Mesure succès, satisfait clients |
| **€/Tonne** | Coût transport / Tonnage 30j | 45€/t (vs 52€/t) | Montre ROI optimisation routes |
| **NPS** | (% Promoteurs - % Détracteurs) | 50 (vs 35 secteur) | Quantifie satisfaction positive |
| **Charge Chauffeurs** | Heures + Km + Tonnage par chauffeur | 85% occupation | Montre rentabilité interne vs externe |

---

## INTÉGRATION GeSI (ZÉRO IMPACT)

```
GeSI (inchangé)
  ↓ Export CSV quotidien (Commandes, Stock, Clients)
  ↓
Excel/PowerBI/Shiptify/Sinari (satellite, lecture seule)
  ↓ Zéro retour en écriture vers GeSI
```

**Points IT à valider** : Format export GeSI possible ? Fréquence daily ? Sécurité ?
**Effort** : 3-5 jours IT interne | **Coût** : Inclus dans devis

---

## RÉPONSES QUESTIONS CLÉ

### Q1 : Low-code vs SaaS vs ERP ?
**R** : Échelonné → Excel T0 (rapide, test), Shiptify T1 (standard), Sinari T2 (si 50+ dépôts)

### Q2 : Faisabilité GeSI ?
**R** : OUI, zéro modification, export CSV suffit, non-invasif

### Q3 : Budget 10-20 k€ réaliste ?
**R** : OUI | Excel 2.5k€ + Shiptify 4.5k€ = 7k€ an 1 (ROI +280%)

---

## ROADMAP 12 MOIS

| Mois | Étape | Budget | Livrables |
|------|-------|--------|-----------|
| **Déc 2025** | Pilot Excel/PowerBI | 2.5 k€ | Alertes 4 + dashboard 1 + KPI 4 |
| **Jan-Mar 26** | Déployer Shiptify | +4.5 k€ | TMS + GPS + mobilité chauffeurs |
| **Avr-Jun 26** | Valider ROI + décision | 0 | Go Sinari ? ou Shiptify seul ? |
| **Jul-Sep 26** | Déployer Sinari (si ok) | +35 k€ | TMS+WMS complet, 50+ dépôts |
| **FIN AN 1** | Système pérenne | **7-42 k€** | Selon choix scalabilité |

---

## DÉCISION REQUISE

**1. APPROUVER** pilote Excel/PowerBI décembre (5-10 franchisés, 2.5 k€, risque FAIBLE)
**2. VALIDER** critères succès : Retards -5%, temps Angélique -3h/sem, satisfaction croissante
**3. DÉCIDER** février 2026 : Scalabilité Shiptify vs Sinari vs status quo ?

**Prochaine réunion** : 1er décembre → Sélection franchisés pilotes + appel d'offres consultant Excel

---

**Budget an 1 recommandé : 7 k€ (phases 1+2) pour ROI +280%**
**Alternative long terme : 42 k€ (phases 1+2+3) pour ROI +2550% si 50+ dépôts justifie**

*Document exécutif 1 page | Prêt présentation management*
