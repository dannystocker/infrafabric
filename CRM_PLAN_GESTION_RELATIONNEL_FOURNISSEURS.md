# PLAN CRM - GESTION RELATIONNELLE ET SCORING FOURNISSEURS GEDIMAT

**Document confidentiel | Version 1.0 | Novembre 2025**

---

## SYNTHÈSE EXÉCUTIVE

Gedimat dispose d'une relation personnelle forte avec ses fournisseurs clés (Mélissa Médiafret, contacts Emeris, Saint-Germaire), mais cette connaissance réside uniquement dans la tête d'Angélique. L'absence de CRM crée une **dépendance critique** et un risque majeur de continuité opérationnelle.

**Enjeu central :** Pérenniser et valoriser le relationnel pour que les améliorations logistiques bénéficient à l'entreprise, pas uniquement à Angélique.

**Objectifs du CRM Gedimat :**
- Documenter les contacts clés et accords informels
- Scorer objectivement les fournisseurs pour évaluer alternatives
- Tracer historique incidents et resolutions
- Créer redondance relationnelle (2+ contacts par fournisseur)
- Supporter continuité opérationnelle en cas absence

---

## 1. ARCHITECTURE CRM - SOLUTION RECOMMANDÉE

### 1.1 Approche progressive : Excel structuré → Logiciel léger → Intégration

**Phase 1 (Immédiate - 0-1 mois) : Excel structuré**

*Avantage :* Déploiement immédiat, pas de coûts, maîtrise totale
*Outil :* Google Sheets (version partagée, accès offline, historique) + commentaires

**Composants Excel Phase 1 :**
1. **Feuille "Contacts Fournisseurs"** (modèle en section 2)
   - Colonne A: Fournisseur | Colonne B: Société | Colonne C: Contact principal | ...
2. **Feuille "Scoring Fournisseurs"** (grille mensuelle)
   - Fournisseur | Fiabilité délai | Qualité produit | Réactivité incidents | Flexibilité
3. **Feuille "Journal des incidents"** (tracabilité)
   - Date | Fournisseur | Incident | Cause | Résolution | Temps résolution
4. **Feuille "Alertes actives"** (suivi des livraisons urgentes)
   - Commande | Fournisseur | ETA | Days-to-ETA | Risk flag

**Mise à jour :** Contacts: chaque contact nouveau | Scoring: mensuel (lundi) | Incidents: temps réel | Alertes: hebdomadaire

---

**Phase 2 (3-6 mois) : Logiciel léger**

*Avantage :* Automatisation alertes, rapports, historique, multi-user
*Coût :* 50-150€/mois (HubSpot gratuit pour 2 users + 1 pipeline, Monday.com, Notion)
*Choix recommandé :* **HubSpot CRM gratuit** (pas de limite de contacts, alertes natives, formulaires)

**Pourquoi HubSpot plutôt que Salesforce ?**
| Critère | HubSpot gratuit | Salesforce |
|---------|---|---|
| **Coût** | 0€ | 165€/user/mois minimum |
| **Contacts** | Illimité | Illimité |
| **Onboarding** | 1 jour | 1 mois |
| **Complexité** | Faible | Élevée |
| **Scoring natif** | Oui | Oui (plugin) |
| **Alertes e-mail** | Automatiques | Workflow |

**Migration Phase 1→2 :** Export CSV + import HubSpot (1 jour d'effort)

---

**Phase 3 (9-12 mois) : Intégration logiciel logistique**

*Objectif :* Synchroniser Commandes ↔ CRM ↔ Scoring
*Exemple :* Si retard fournisseur → Automatiquement baisse score fiabilité + Alerte Angélique + Notification client
*Coûts :* Considérer si logiciel TMS/WMS actuel offre CRM intégré

---

### 1.2 Gouvernance des données CRM

| Rôle | Responsabilité | Fréquence |
|-----|---|---|
| **Angélique (Coordinatrice)** | Mise à jour contacts, incidents | Temps réel |
| **Manager logistique** | Validation scoring, escalade incidents | Mensuel + critiques |
| **Admin CRM** | Backup, sécurité, rapports | Hebdomadaire |
| **Direction** | Lecture dashboards, décisions sourcing | Trimestriel |

**Accès :**
- Lecture tous : Tableaux bord synthèse scores
- Écriture Angélique : Tous sauf scores validation
- Écriture Manager : Scoring + validation incidents
- Admin : Configurations + sauvegardes

---

## 2. CONTACTS CLÉS - DOCUMENTATION STRUCTURÉE

### 2.1 Modèle de fiche contact

**Format simplifié (1 contact = 1 page Excel ou HubSpot)**

```
SOCIÉTÉ : Médiafret (Transporteur)
ADRESSE : [Adresse siège]
CODE CLIENT GEDIMAT : [Référence interne]

CONTACT PRINCIPAL
├─ Nom : Mélissa [NOM]
├─ Titre : Gestionnaire de comptes transport
├─ Tél direct : +33 [XXX]
├─ Email : mélissa@mediafret.com
├─ Whatsapp/Telegram : [Si oui, numéro]
├─ Préférences contact : Téléphone 9-11h, Email pour documents
├─ Disponibilité urgences : Lun-Ven 8h-18h (demander avant 15h pour lendemain)

CONTACTS SECONDAIRES (REDONDANCE)
├─ Nom : [Contact alternatif, superviseur, etc.]
├─ Titre : [Responsable équipe transport]
├─ Tél/Email : [Numéro secours]
├─ Quand utiliser : Si Mélissa absente >2j

ACCORDS INFORMELS DOCUMENTÉS
├─ Délai express (urgence) : 24-48h si demande avant 14h
├─ Réduction volume minimum : Accepte charges partielles >100kg
├─ Favoris tarif : Enlèvements regroupés = -8% par rapport tarif unitaire
├─ Conditions paiement : Net 30, jamais en retard
├─ Escalade problèmes : Appel direct Mélissa (sauf week-end)

HISTORIQUE RELATIONNEL
├─ Depuis : [Date premier enlèvement]
├─ Nombre enlèvements/an : [Estimation]
├─ Score confiance : [9/10]
├─ Note personnelle : "Mélissa vraiment fiable, accepte urgences, à maintenir relation"

ALERTES
├─ Augmentation tarifaire dernier : [Mois/année] → +5%
├─ Incident majeur dernier : [Description] → Résolu en [temps]
├─ Prochaine renegociation : [Trimestre]
```

---

### 2.2 Fiches précomplétées pour Gedimat

#### FOURNISSEUR 1 : MÉDIAFRET (Transporteur logistique)

```
CONTACT PRINCIPAL
│ Mélissa [Nom complet à verifier]
│ Tél : +33 XXX / Email : mélissa@mediafret.com
│
│ ACCORDS CLÉS :
│ • Urgences 24-48h si demande avant 14h
│ • Charges partielles >100kg acceptées
│ • Regroupement enlèvements = -8%
│ • Escalade directe Mélissa en critiques
│
│ RISQUE ABSENCE : CRITIQUE
│ └─ Redondant : Manager équipe (à identifier)
│
│ NOTES CONTEXTE :
│ • Relation 4+ ans (Angélique historique)
│ • Transporteur habituel = 80%+ des enlèvements
│ • Maintenir relation ++ (prix peut augmenter sinon)
```

#### FOURNISSEUR 2 : EMERIS (Tuiles & matériaux toit)

```
CONTACT PRINCIPAL
│ [Nom à documenter]
│ Titre : Responsable commercial / Logistique
│ Tél : +33 XXX / Email : contact@emeris.fr
│
│ ACCORDS CLÉS :
│ • Délais standard : 5-7 jours
│ • Urgence possible : +20% = 48h
│ • Retours qualité : Acceptés sous 5j
│ • Historique retards : ~15% (à valider)
│
│ RISQUE ABSENCE : MOYEN
│ └─ Redondant : [A ajouter - demander 2e contact]
│
│ NOTES CONTEXTE :
│ • Fournisseur régulier (tuiles Gedimat)
│ • Contact informel seulement chez Angélique
│ • URGENCE : Documenter + créer redondance
```

#### FOURNISSEUR 3 : SAINT-GERMAIRE (Matériaux généraux)

```
CONTACT PRINCIPAL
│ [Nom à documenter]
│ Titre : Responsable commercial
│ Tél : +33 XXX / Email : contact@saintgermaire.fr
│
│ ACCORDS CLÉS :
│ • Délais : 3-5 jours
│ • Petites quantités : Acceptées (minima flexibles)
│ • Historique qualité : À documenter
│
│ RISQUE ABSENCE : MOYEN
│ └─ Redondant : [A ajouter]
│
│ NOTES CONTEXTE :
│ • Fournisseur stratégique (volume régulier)
│ • Contact Angélique seule = RISQUE
│ • URGENT : Structurer accès redondant
```

---

### 2.3 Actions d'amélioration relationnelle (Court terme)

**Semaine 1 :** Angélique compile les contacts existants dans template Excel
- Médiafret / Mélissa
- Emeris / Saint-Germaire (contacts à identifier)
- 3-5 fournisseurs supplémentaires

**Semaine 2-3 :** Créer contact secondaire pour chaque fournisseur clé
- Appeler manager/superviseur : « Pour continuité opérationnelle, qui gérerait le dossier si vous êtes absent ? »
- Documenter préférences contact / escalade

**Mois 1:** Lancer CRM (Google Sheets) avec fiches précomplétées
- Accès équipe : Angélique (admin) + Manager (consultation)
- Synchroniser avec alertes défauts logiciel existant

---

## 3. SCORING FOURNISSEURS - GRILLE COMPLÈTE

### 3.1 Méthodologie (4 critères, pondération)

| Critère | Poids | Cible | Formule |
|---------|-------|-------|---------|
| **Fiabilité délai** | 40% | >90% on-time | (Livraisons à l'heure) / (Total livraisons) par mois |
| **Qualité produit** | 25% | <2% retour | (Retours qualité) / (Total livraisons) par trimestre |
| **Réactivité incidents** | 20% | <48h résolution | (Temps moyen résolution incident) en heures |
| **Flexibilité** | 15% | >80% acceptation | (Urgences acceptées) / (Urgences demandées) par trimestre |

**Score final = (Fiabilité × 0.40) + (Qualité × 0.25) + (Réactivité × 0.20) + (Flexibilité × 0.15)**

**Échelle :**
- **≥85** : Excellent (partenaire stratégique)
- **70-84** : Bon (continuer)
- **60-69** : Risque (discussion amélioration requise)
- **<60** : Critique (alternative ou dual sourcing immédiat)

---

### 3.2 Grille de scoring (Format Excel mensuel)

```
MOIS : Novembre 2025

FOURNISSEUR : Médiafret
════════════════════════════════════════════════════════════════
│ Critère              │ Valeur Mois │ Cible │ Score 0-100 │ Note
├──────────────────────┼─────────────┼───────┼─────────────┼─────────
│ Fiabilité délai      │ 92%         │ >90%  │ 92          │ ✓ OK
│ Qualité produit      │ 0% retour   │ <2%   │ 100         │ ✓ Excellent
│ Réactivité incidents │ 24h moy     │ <48h  │ 98          │ ✓ Excellent
│ Flexibilité          │ 100%        │ >80%  │ 100         │ ✓ Parfait
├──────────────────────┼─────────────┼───────┼─────────────┤
│ SCORE MENSUEL        │             │       │ 96/100      │ ★★★★★
└──────────────────────┴─────────────┴───────┴─────────────┘

Notes contexte :
• Excellent partenaire, maintenir relation
• Pas d'incident ce mois
• Urgences acceptées (2x demandées = 2x acceptées)
```

---

### 3.3 Actions par seuil de score

| Score | Action |
|-------|--------|
| **≥85** | • Maintenir | • Envisager partenariat long-terme | • Reconnaître excellent service |
| **70-84** | • Suivi normal | • Réunion amélioration (trimestriel) | • Identifier axes faiblesse |
| **60-69** | • **Réunion amélioration URGENTE** | • Plan d'action 90j | • Identifier alternatives en parallèle |
| **<60** | • **Escalade direction** | • 30j pour amélioration | • Lancer dual sourcing | • Prévoir transition |

---

### 3.4 Exemple d'action suite à scoring <70%

**Scénario : Emeris score = 65/100 (Fiabilité 62%, Réactivité 3j de retard moyen)**

**Réunion amélioration (Proposée par Gedimat)**

```
OBJECTIF : Remonter à 75+ dans 90 jours

POINTS DISCUTÉS
├─ Retards : Cause identifiée (problème préparation commandes, pas logistique)
├─ Solution : Emeris ajoute 1 jour avance pour buffer
├─ Engagement : Atteindre 90%+ on-time dans 3 mois
├─ Vérification : Scoring Janvier 2026

SI NON ATTEINT EN JAN 2026
├─ Lancer recherche alternative (Saint-Germaire pour 30% volume)
├─ Renégociation tarifaire (moins de flexibilité = impact prix)
└─ Réévaluer partenariat dans 6 mois
```

---

## 4. FRÉQUENCE DE MISE À JOUR & RESPONSABILITÉS

| Tâche | Fréquence | Responsable | Effort |
|-------|-----------|-------------|--------|
| Ajouter nouveau contact | À chaque contact | Angélique | 5 min |
| Mettre à jour accords informels | Après négociation | Angélique | 10 min |
| Enregistrer incident | Temps réel | Angélique | 10 min |
| Calculer score mensuel | 1er lundi mois | Manager | 30 min (4 fournisseurs) |
| Réunion amélioration (si <70) | Après calcul | Manager + Fournisseur | 1h |
| Rapporter à direction | Mensuel | Manager | 15 min |

**Règle d'or :** Si l'information n'est pas dans le CRM, elle n'existe pas pour l'entreprise.

---

## 5. CONTINUITÉ OPÉRATIONNELLE - RISQUE MITIGATION

### 5.1 Scénarios de risque et réponses

| Scénario | Risque | Mitigation | Délai |
|----------|--------|-----------|-------|
| **Absence Angélique (1-2j)** | Pas d'accès contacts, urgences non traitées | Contact secondaire documenté, accès CRM Manager | 0-2h |
| **Absence Angélique (1-4 sem)** | Grosses perturbations | Manager prend relais avec CRM, contact redondants | <1h |
| **Départ Angélique** | Perte 4 ans relationnel | CRM complet transfert nouveau coordinateur | 1-2 sem transition |

### 5.2 Checklist transition (Si départ Angélique)

- [ ] CRM 100% à jour (contacts, accords, historique incidents)
- [ ] Contacts secondaires documentés et présentés aux fournisseurs
- [ ] Réunion de transition : nouveau coordinateur + Manager + Fournisseurs clés (Médiafret)
- [ ] Période chevauchement 2-3 semaines (Angélique + Nouveau)
- [ ] Handover appels/emails : Mélissa reçoit email de Nouveau présenté par Angélique

---

## CONCLUSION

**Investissement requis :**
- **Phase 1 (Immédiate):** 2 jours Angélique (compilation) + 0€
- **Phase 2 (3 mois):** 1 jour configuration HubSpot + 50€/mois
- **Phase 3 (12 mois):** Évaluation selon logiciel logistique existant

**ROI estimé :**
- Continuité opérationnelle en cas absence :** Perte estimée évitée = 10-20k€ (rupture service)
- Négociation fournisseurs basée données :** +5-10% conditions tarifaires/délai
- Réduction surprises logistiques :** Moins d'incidents = meilleure satisfaction client

**Risque critique non mitigué :** Si Angélique ne met pas à jour le CRM, la dépendance personnelle persiste. **Solution = Responsabilité partagée** (Manager audit hebdomadaire).

---

**Approuvé pour déploiement immédiat Phase 1 | CRM Gedimat v1.0**
