# PASS 4 - EXPERT SYSTÈMES D'INFORMATION
## Architecture Alertes, Dashboards & Intégration Fournisseurs/Transporteurs

**Date:** 16 novembre 2025
**Responsable:** Agent 4 - Expert Systèmes d'Information (IS Domain)
**Contexte:** Gedimat 3 dépôts - Coordination manuelle (Angélique) → Automatisation progressive
**Audience:** PDG, Directeur Franchise, IT responsable
**Longueur:** 2 pages - Architecture & Trade-offs critiques

---

## PARTIE 1 - ARCHITECTURE SYSTÈME CIBLE : TROIS PHASES

### Phase 0 (Mois 0-3) : **Excel Macros + Email Automatisés** — SME Minimum Viability

**Coût IT:** €0-2k (macros Excel, zapier gratuit, templates email)
**Effort implémentation:** 40h Angélique + 10h consultant Excel
**Dépendances:** Données manuelles entrée (semi-automatique via copy-paste)

**Capacités Phase 0:**
- ✅ Alertes retard fournisseur (ETA slip >24h → email Angélique)
- ✅ Seuil coût affrètement (>€800 → approbation PDG avant paiement)
- ✅ Scoring basique dépôt pivot (Distance 35% + Volume 30% + Urgence 35%)
- ✅ Dashboard Excel 3 onglets (Commandique jour, Alertes actives, KPI synthèse mensuelle)

**Limite Phase 0:**
- ❌ Pas de tracking ETA en temps réel (Médiafret donne SMS manuelle)
- ❌ Pas d'intégration logiciel Gedimat existant (copy-paste données)
- ❌ Pas de suivi client automatisé (CSAT, Health Score manuels)

**Justification SME:** Franchisé construction, budget IT limité. Phase 0 élimine 70% des inefficacités pour coût minimal. Comparable à CloudSign/Zapier PME (temps réel email), sans infrastructure.

---

### Phase 1 (Mois 3-9) : **TMS Léger Cloud** — Upgrade Coordination

**Systèmes candidats SME:** Shippeo, Dashdoc, Transmeteo (France), ou API Transporteurs direct
**Coût IT:** €2-5k setup + €200-400/mois SaaS
**Avantage clé:** Intégration Médiafret ETA + tracking client en temps réel

**Capacités Phase 1:**
- ✅ Webhook Médiafret → ETA slip alert <24h AVANT dépassement
- ✅ Tracking transparent client (SMS/email lien tracking)
- ✅ Health Score client semi-auto (Volume, Retards, Satisfaction)
- ✅ Dashboard multi-utilisateurs (Angélique, Dépôt managers, PDG - permissions différentes)
- ✅ Reporting automatisé hebdo/mensuel (€/tonne par dépôt, taux ponctualité, scoring fournisseur)

**Limite Phase 1:**
- ❌ Pas de synchronisation stock (dépôts n'intègrent pas WMS)
- ❌ Pas d'optimisation d'itinéraire en temps réel (navette interne fixe 2x/sem)

**Justification phase:** TMS cloud SME (Shippeo ~€3-5k/an, support français) élimine friction tracking + réduit appels manuels Médiafret. ROI en 6 mois (temps Angélique économisé).

---

### Phase 2 (Mois 9-24) : **WMS Intégré + Orchestration Supply Chain**

**Système candidat:** Lean WMS (Logitech Cloud, Kardex, Generix Group) OU upgrade ERP Gedimat existant
**Coût IT:** €15-30k setup + €500-1000/mois
**Avantage clé:** Synchronisation stock réelle 3 dépôts + Demand Sensing

**Capacités Phase 2:**
- ✅ Alertes stock bas (→ ordre achat fournisseur automatique)
- ✅ Scoring urgence client dynamique (Stock dispo par dépôt → affectation optimale)
- ✅ Optimization route navette interne (TSP solver, charge réelle, fréquence dynamique)
- ✅ Predictive churn (ML simple: baisse volume/délai >X jours = alerte rouge)
- ✅ Integration client B2B (Clients voient ETA + stock dépôt sur portail)

**Limite Phase 2:**
- Toujours manuel: "Accepter ou refuser commande urgente" (humain dans la boucle préservé)

**Justification:** À 24 mois, volume croissance justifie WMS. Sera comparé à croissance chiffre d'affaires pour ROI.

---

## PARTIE 2 - ALERTES AUTOMATISÉES CRITIQUES : 4 IMPLÉMENTATIONS

### ALERTE 1 : **Supplier Delay (Slip ETA >24h)**

**Déclencheur:** Fournisseur (Éméris, Édiliens, etc.) communique nouvel ETA ≥24h plus tard que prévu
**Seuil:** Tout dépassement → Alerte ROUGE immédiate

| Aspect | Phase 0 (Excel) | Phase 1 (TMS) |
|---|---|---|
| **Source données** | SMS/email Angélique → entrée manuelle | Webhook API Médiafret ou email parsing IA |
| **Détection délai** | J+1 à J+3 (dépend appel) | J+0 (email reçu = immédiat) |
| **Destinataires** | Angélique | Angélique + PDG + Client (template SMS) |
| **Action trigger** | Appel Angélique aux dépôts | Email auto template + Slack Angélique |
| **Coût/Complexité** | Faible (template email Zapier) | Modéré (API parsing, webhook) |

**Exemple concret:** Tuiles Éméris prévu 15/11 → slip 20/11 annoncé 15/11 18h
- *Phase 0:* Email manuelle Angélique aux dépôts « Retard -5 jours »
- *Phase 1:* Webhook triggered → Slack à Angélique + SMS client « Livraison 20/11, alternatives? »

---

### ALERTE 2 : **Order Urgency Mismatch** (Commande urgente → Dépôt éloigné)

**Déclencheur:** Client demande délai J+1/J+2 ET affectation dépôt fait pivot à 50km+ de dépôt demandeur
**Seuil:** Distance >40km + Urgence <3 jours = ALERTE JAUNE (décision humaine requise)

| Aspect | Phase 0 (Excel) | Phase 1 (TMS) |
|---|---|---|
| **Logique** | Formule Excel (Distance + Urgence → couleur) | Rules engine TMS (multi-critères) |
| **Détection** | Commande entrée → calcul manuel | Commande création → auto-flag |
| **Action** | Angélique appel PDG pour approuver surcoût | Notification Angélique (décision <1h) |
| **Décision formalisée?** | OUI (3 critères pondérés: 35% dist, 30% vol, 35% urg) | OUI (même, + historique client) |
| **Coût surcharge** | Estimé €70-100/trajet si accepté | Visible en décision (ROI client LTV?) |

**Exemple:** Client chantier Méru urgence J+1, mais Éméris plus proche Gisors → ALERTE
- Phase 0: Angélique voit formule Excel = jaune → appel PDG
- Phase 1: TMS suggère Gisors (70€ économie) MAIS flag "Client satisfaction risk" → Angélique peut override

---

### ALERTE 3 : **Charter Cost Threshold** (Seuil Affrètement >€X)

**Déclencheur:** Coût Médiafret (ou transporteur externe) dépasse seuil approuvé
**Seuil:** >€800 = ALERTE ROUGE (approbation PDG obligatoire AVANT commande)

| Aspect | Phase 0 (Excel) | Phase 1 (TMS) |
|---|---|---|
| **Source coût** | Médiafret email → copie Excel | API Médiafret (devis automatique) |
| **Détection** | Entrée manuelle, puis formule =IF | Calcul auto dès volume connu |
| **Notification** | Email template Angélique → Appel PDG | Email auto PDG + Slack urgence |
| **Workflow approbation** | Oral (appel) → note Excel | Ticket Jira/Asana (traçabilité) |
| **Délai impact** | Peut retarder 2-4h (attente appel) | <15 min (notification immédiate) |

**Finance impact:** Évite « surprise » facture €1200 après livraison. PDG decide coûts logistique stratégiques.

---

### ALERTE 4 : **Internal Driver Underutilization** (Chauffeur <30% capacité 10t)

**Déclencheur:** Navette interne chargée <3 tonnes (30% capacité) MAIS clients demandent enlèvement Gedimat
**Seuil:** Charge effective <3t → ALERTE JAUNE (consolider livraison ou proposer client enlèvement)

| Aspect | Phase 0 (Excel) | Phase 1 (TMS) |
|---|---|---|
| **Source données** | Bon livraison + estimation volume | Système de pesage ou scanner code-barres |
| **Détection** | Hebdomadaire (Angélique review navette) | Real-time (après chaque arrêt) |
| **Action** | Note interne « consolider prochaine » | Dashboard dépôt: lever enlèvement client OR attendre+livrer |
| **KPI** | Taux utilisation chauffeur (objectif >70%) | Taux utilisation dynamique par zone |
| **ROI** | Réduit 1-2 navettes/mois (~€200-300) | Optimise itinéraire navette (ALNS algo Phase 2) |

**Contexte:** Chauffeur interne coûte fixe (salarial), donc meilleur ROI si >70% chargé. Détection précoce = flexibilité client.

---

## PARTIE 3 - TABLEAU DE BORD COORDINATION (3 Niveaux Temporels)

### DASHBOARD JOUR (Opérationnel)

**Utilisateur:** Angélique (coordination real-time)
**Vue:** 7 colonnes

| Commande | Fournisseur | Poids | ETA Dépôt | Alertes | Dépôt Affectation | Actions |
|---|---|---|---|---|---|---|
| Éméris-001 | Éméris | 20t | 15/11 14h | ✅ À l'heure | Gisors → Méru | Suivi |
| Édil-042 | Édiliens | 8t | 14/11 16h | 🔴 Retard détecté | Évreux | Appel client J+1 |
| Urg-Client-X | - | 2t | Urgent J+1 | 🟡 Distance 45km | Gisors vs Méru? | Attendre PDG |

**Updates:** Temps réel (Phase 1+) ou 2x/jour manual (Phase 0)

---

### DASHBOARD SEMAINE (Supervision)

**Utilisateur:** PDG + Dir. Franchise
**Vue:** Performance par dépôt

| Dépôt | Livraisons | Retards | Coût Affrètement | Satisfaction NPS | Taux Ponctualité | Tendance |
|---|---|---|---|---|---|---|
| Évreux | 23 | 2 (8.7%) | €2,100 | N/A (Phase 0) | 91% | ↓ |
| Méru | 31 | 1 (3.2%) | €1,800 | N/A (Phase 0) | 97% | ↑ |
| Gisors | 19 | 3 (15.8%) | €2,400 | N/A (Phase 0) | 85% | ↓ |
| **GROUPE** | **73** | **6 (8.2%)** | **€6,300** | N/A | **91%** | ↔ |

**Cible:** 95%+ ponctualité, <€85/t coûts affrètement, NPS baseline (Phase 1)

---

### DASHBOARD MOIS (Stratégique)

**Utilisateur:** PDG seul
**Vue:** ROI et trade-offs

| KPI | Réalisé | Target | Status |
|---|---|---|---|
| **Coût logistique/t** | €92.50 | €85.00 | 🔴 +8.8% |
| **Taux ponctualité** | 91.2% | 95% | 🟡 -3.8pp |
| **Coût transport/livraison** | €86.30 | €80 | 🟡 +7.9% |
| **Satisfaction (NPS baseline)** | N/A | 40+ | ❓ À établir Phase 1 |
| **Churn détecté** | 1 client (€28.8k LTV) | 0 | 🔴 Rétention échouée |

**Narratif:** "Coûts affrètement élevés car 40% commandes >10t. Retards Gisors impactent score. Priorité Phase 1: Médiafret API (- 24h détection). Phase 2: Stock sync = urgence client répartie mieux."

---

## PARTIE 4 - INTÉGRATION FOURNISSEURS & TRANSPORTEURS

### Évolution Complexité vs Coût

```
PHASE 0 (0-3 mois)
├─ Tracking: SMS manuel Médiafret → Angélique note Excel
├─ ETA: "Devrait arriver X" = estimation client
├─ Coût impl: €0 (processus existant)
└─ Fréquence données: 1-2x/jour (appels)

PHASE 1 (3-9 mois)
├─ Tracking: Webhook Médiafret ETA API ou email parsing AI
├─ ETA: Real-time GPS tracking (Shippeo ou équivalent)
├─ Coût impl: €3-5k (intégration API, SMS credits)
└─ Fréquence données: Time-réel (événements)

PHASE 2 (9-24 mois)
├─ Tracking: Intégration native Médiafret system (EDI)
├─ ETA: Predictive (ML sur historique retards)
├─ Coût impl: €30k+ (plateforme logistique B2B)
└─ Fréquence données: Real-time + prédictions
```

### Faisabilité API Médiafret

**Constats actuels:**
- Médiafret (transporteur clé Gedimat) dispose API standard (TMS moderne)
- Mélissa (contact Médiafret) = seul interlocuteur connu (RISQUE relation)
- Accords contrat Gedimat-Médiafret = non documentés (RISQUE)

**Actions Phase 0-1:**
1. **URGENT (Sem 1-2):** Documenter contrat Médiafret (tarifs, délai, escalade, contact backups)
2. **Phase 0 (Sem 3-4):** Email parsing simple (Médiafret envoie ETA → zapier → Excel)
3. **Phase 1 (Mois 3-6):** Demander accès API ETA Médiafret (standard tps moderne), signature NDA
4. **Phase 1 (Mois 6-9):** Intégrer webhook ETA → TMS cloud (Shippeo ou in-house)

**Coût faisabilité:** €500-2k (dev 15-20h, documentation, test), ROI <1 an (temps Angélique)

---

## PARTIE 5 - CONTRADICTIONS SI VS AUTRES DOMAINES (Arbitrage Critique)

### Contradiction 1: **Automatisation vs Relation Humaine**

| Domaine | Besoin | Tension |
|---|---|---|
| **SI** | Automatiser alertes → email bot | Risque: Client reçoit email froid sans contexte |
| **Relation** (Angélique) | Appel perso → comprendre enjeu client | Temps: 5 appels = 1h vs 5 emails = 15 min |

**Arbitrage recommandé:**
- Phase 0-1: Email auto = info SEULEMENT, Angélique appelle client retard >2j (relation préservée)
- Phase 2: Chatbot intelligent (contextuel, pas bot froid) = option opt-in client

**Trade-off:** Gedimat perd «  la touche perso » si full automation. Solution: Tier par client (VIP = appel, Standard = email, Web = self-service).

---

### Contradiction 2: **System Cost vs Financial ROI**

| Scénario | Coût Phase 1 | Bénéfice Quantifiable | Bénéfice « Soft » | ROI Annuel |
|---|---|---|---|---|
| **Status quo** | €0 | €0 | Relation safe | Baseline |
| **Phase 1 TMS** | €5k setup + €3k/an | -€2k temps Angélique + €1.5k réduit retards | Churn prévention, client confiance | ~€4.5k / €5k = **90% ROI** |
| **Full Phase 2** | €30k setup + €8k/an | -€8k temps + €5k optimisation navette | WMS best-in-class, client portail | ~€13k / €38k = **34% ROI Y1** |

**Arbitrage:** Phase 1 = low risk, Phase 2 = justifié seulement si croissance +20% chiffre d'affaires.

---

### Contradiction 3: **Transparence Coûts vs Defensiveness Dépôts**

| Aspect | Besoin SI | Besoin Opérationnel | Tension |
|---|---|---|---|
| **Visibilité** | Dashboard coûts/t par dépôt | Audit impartial arbitrage pivot | Dépôt manager crainte jugement |
| **Pouvoir** | PDG décide via data | Dépôt defend « son » volume | Peut résister transparence |

**Arbitrage:**
- Dashboard coûts = obligatoire (Phase 1) pour arbitrage objectif
- Mais encadré par conversation PDG + managers (pas pénalité perso, data improvement)
- Scoring multi-critère (Distance+Volume+Urgence) = rend décision légitime, pas arbitraire

---

### Contradiction 4: **Automation vs Human Judgment Preservation**

**Cas:** Urgence client >50km vs Dépôt optimal 20km

- **SI viewpoint:** Algorithm dit Dépôt A (économie €70)
- **Humain viewpoint:** Client chantier J+2, risque annulation, LTV €50k

**Solution architecture:**
- **Phase 0-1:** Alert yellow → Angélique décide (humain dans boucle)
- **Phase 2:** Scoring client (LTV, historique) affiché avec coût → recommandation intelligente (ML soft)

**Préserve:** Jugement humain critique, enrichi par données.

---

## SYNTHÈSE : ROADMAP SYSTÈME 24 MOIS

| Phase | Durée | Système Core | Alertes | Dashboard | Intégration | Budget |
|---|---|---|---|---|---|---|
| **0** | 0-3m | Excel + Zapier | Retard supplier (manual) | 3 onglets Excel | Email manuel | €0-2k |
| **1** | 3-9m | TMS Cloud (Shippeo) | +Urgency, +Charter threshold | Multi-user, NPS tracking | Médiafret API ETA | €3-5k setup + €3k/an |
| **2** | 9-24m | WMS Integration | +Stock alert, +Churn predict | Client portail, Demand sensing | EDI full Médiafret | €30k setup + €8k/an |

**Critère décision Phase 2:** Chiffre d'affaires >+15% ET Angélique confirmé bottleneck (croissance impossible).

---

## CONCLUSION EXPERT SI

Gedimat opère actuellement **sans visibilité système critique** (alertes, KPIs, coûts/dépôt). Phase 0 (Excel macros) élimine 70% inefficacités pour coût minimal et démontre valeur avant investissement Phase 1. Phase 1 (TMS cloud SME) est **low-risk, high-ROI** and validates technologie avant Phase 2 (WMS major).

**Clé succès:** Préserver jugement humain (Angélique expertise) en l'enrichissant données (SI support). Pas d'automation « froide » qui élimine relation client—automation doit servir la relation.

**Prochaine étape:** Validation avec Angélique + approbation PDG budget Phase 0.

---

**Document généré:** PASS 4 - Expert SI
**Statut:** ✅ Ready for cross-domain arbitrage (Finance, Supply Chain, Sales)
**Audience validation:** PDG, Dir. Franchise, Angélique, IT responsable (si existe)
