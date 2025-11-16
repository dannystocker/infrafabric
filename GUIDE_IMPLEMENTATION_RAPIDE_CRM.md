# GUIDE IMPLÉMENTATION RAPIDE - CRM GEDIMAT
## (Étapes détaillées pour mise en place Phase 1 - Novembre 2025)

**Responsables : Angélique (données) + Manager (validation) | Durée : 2-3 semaines**

---

## JOUR 1-2 : PRÉPARATION (Angélique)

### Tâche 1.1 : Compiler les informations existantes (2h)

```
Ouvrir fichier Excel/notes et rassembler :

□ Médiafret
  ├─ Nom complet Mélissa (vérifier orthographe)
  ├─ Téléphone direct (celui qu'on appelle vraiment)
  ├─ Email exact
  ├─ Horaires disponibilité
  ├─ Accords informels (délai urgence, flexibilité urgences)
  └─ Historique : depuis quand on travaille ensemble

□ Emeris
  ├─ Nom fournisseur exact
  ├─ Personne qu'on appelle (nom + tél + email)
  ├─ Délais standard : combien jours?
  ├─ Retards : fréquents? 15-20% selon Angélique?
  ├─ Historique problèmes
  └─ Alternative connue? (Saint-Germaire?)

□ Saint-Germaire
  ├─ Infos de base (personne contact, tél, email)
  ├─ Délais
  ├─ Fiabilité (observations)
  └─ Capacité tuiles (alternative Emeris?)

□ 3-5 autres fournisseurs clés
  ├─ Noms
  ├─ Contacts
  └─ Basiques
```

**LIVRABLE :** Document Word/Notes compilant toutes les infos = INPUT pour CRM

---

### Tâche 1.2 : Lister les TROUS dans la documentation (1h)

**Pour chaque fournisseur clé, identifier :**

```
MÉDIAFRET (CRITIQUE)
├─ ☐ Contact secondaire (qui appeler si Mélissa absent?) → À CRÉER
├─ ☐ Horaires précis → À confirmer
├─ ☐ Email correct → À vérifier
└─ ☐ Accords urgence par écrit? → Non (verbal seulement)

EMERIS (URGENT)
├─ ☐ Contact exact (nom complet)
├─ ☐ Email
├─ ☐ Contact secondaire → À identifier
├─ ☐ Délai urgence 48h possible? → À demander
└─ ☐ Tarif urgence? → À demander

SAINT-GERMAIRE (NORMAL)
├─ ☐ Contact nom exact
├─ ☐ Email correct
├─ ☐ Contact secondaire → À identifier
└─ ☐ Capacité tuiles (alternative) → À discuter

[AUTRES] (NORMAL)
├─ Contact basique
└─ Délai standard
```

**LIVRABLE :** Liste "À compléter" = Sprint d'appels semaine 2-3

---

## SEMAINE 2 : COLLECTE COMPLÉMENTAIRE (Angélique + Manager)

### Tâche 2.1 : Appels fournisseurs - Questions clés (3-4h)

**Modèle d'appel (15-20 min par fournisseur):**

```
« Bonjour [Personne],

J'appelle pour optimiser nos contacts avec vous. Quelques questions rapides :

1. CONFIRMATION
   - Vous êtes toujours le bon interlocuteur pour [type commandes] ?

2. CONTACT SECOURS
   - Si vous êtes absent plus de 2 jours, qui d'autre on appelle ?
   - Je pourrais avoir le numéro/email de cette personne ?

3. ACCORDS ACTUELS
   - Les délais standard toujours 5-7 jours ? [Ou adapter selon fournisseur]
   - En cas d'urgence, c'est possible 48h ? [Coût? Conditions?]
   - Petites quantités (<100kg) : acceptées ?

4. PRÉFÉRENCES CONTACT
   - Vous préférez appel ou email ?
   - Meilleurs horaires pour vous appeler ?

Merci! On va documenter tout ça pour notre équipe. »
```

**Fournisseurs prioritaires (Appels semaine 2-3):**

| Fournisseur | Responsable | Urgence | Duree Appel |
|---|---|---|---|
| Médiafret | Angélique | CRITIQUE | 15 min |
| Emeris | Manager | URGENT | 20 min |
| Saint-Germaire | Angélique | Normale | 15 min |
| [Autres 3-5] | Angélique | Basse | 10-15 min |

**LIVRABLE :** Notes d'appels compilées → Input pour fiches contact

---

### Tâche 2.2 : Validation Manager des données (2h)

**Manager fait :**

```
□ Vérifie données compilées par Angélique
□ Teste 1-2 contacts directement (appel/email court)
  "Bonjour, c'est [Manager] de Gedimat.
   Je vérifiez que c'est bien votre numéro direct?"
□ Identifie données manquantes
□ Flag fournisseurs critiques (redondance manquante)
```

**Check-list validation :**

```
MÉDIAFRET
□ Mélissa : nom + email + tél vérifié?
□ Contact secours identifié + contacté?
□ Accords urgence documentés?
□ Score 96 confirmé?

EMERIS
□ Contact principal confirmé?
□ Contact secondaire identifié?
□ Délais/tarifs urgence clarifiés?
□ Raison retards 15-20% documentée?
□ Score 68 confirmé?

SAINT-GERMAIRE
□ Contact confirmé?
□ Capacité tuiles clarifiée?
□ Score 81 confirmé?
```

---

## SEMAINE 3 : CRÉATION CRM GOOGLE SHEETS

### Tâche 3.1 : Créer Google Sheet partagé (30 min)

**Étapes :**

1. Aller sur Google Sheets → Créer nouveau document
2. Nommer : `[GEDIMAT] CRM-Fournisseurs-2025`
3. Partager (Accès) :
   - Angélique : Éditeur
   - Manager : Éditeur
   - Direction (optionnel) : Consultation

4. Créer onglets (feuilles) :
   - `Contacts` (liste maître)
   - `Scoring` (mensuel)
   - `Incidents` (traçabilité)
   - `Alertes` (suivi actif)

---

### Tâche 3.2 : Remplir onglet CONTACTS (2-3h)

**Copier modèle :** Utiliser template fiches contact précomplétées (doc separate)

**Colonnes minimales :**

```
A: Fournisseur
B: Contact 1 Nom
C: Contact 1 Email
D: Contact 1 Tél
E: Contact 1 Préférences (horaires, canal)
F: Contact 2 Nom
G: Contact 2 Tél (secours)
H: Délai Standard
I: Délai Urgence
J: Coût Urgence
K: Flexibilité
L: Paiement
M: Augmentation tarifaire dernière (%)
N: Note contexte
O: Date création fiche
P: Dernière MAJ
```

**Exemple données :**

```
Médiafret | Mélissa Durand | mélissa@mediafret.fr | +33 1 XX XX XX | Appel 9-17h |
Superviseur (Nom?) | +33 1 YY YY YY | 2-3j | 24-48h si avant 14h | Gratuit |
3/3 urgences | Net 30 | +3% oct 2025 | Partenaire critique - Excellent | 2025-11-01 | 2025-11-10

Emeris | [Contact] | [Email] | [Tél] | À confirmer |
[Contact 2] | [Tél] | 5-7j | À vérifier | À demander |
4/5 urgences (75%) | À vérifier | À vérifier | Retards fréquents - Plan 90j | 2025-11-10 | 2025-11-10
```

**Tip :** Si données manquent, laisser "[À compléter]" → Rappel visuel

---

### Tâche 3.3 : Remplir onglet SCORING (1h)

**Copier template mensuel :**

```
Fournisseur | Fiabilité % | Qualité % Retour | Réactivité h | Flexibilité % |
Points Pondérés | Score Total | Tendance | Statut | Action

Médiafret | 92 | 0 | 24 | 100 |
36.8+25+19.6+15 | 96.4 | Stable 6 mois | ✓✓✓✓ | Maintenir excellence
Emeris | 62 | 2.5 | 48 | 75 |
24.8+24.4+14+11.3 | 68.2 | Dégradation | ⚠️ RISQUE | Réunion déc
Saint-Germaire | 85 | 1.8 | 36 | 80 |
34+24.6+15+12 | 81.1 | Stable | ✓✓ BON | Suivi normal
```

**Fréquence MAJ :** 1er lundi du mois (30 min)

---

### Tâche 3.4 : Remplir onglet INCIDENTS (15 min template)

**Colonnes :**

```
Date | Fournisseur | Contact | Problème (Retard/Qualité/Service) |
Cause | Résolution | Temps résolution (h) | Statut
```

**Exemples :**

```
2025-11-10 | Médiafret | Mélissa | Urgence 48h | Capacité limite |
Enlèvement express OK | 24h | ✓ Bon

2025-11-05 | Emeris | [Contact] | Retard 3 jours | Préparation lente |
Remplacement enlèvement | 72h | ⚠️ Risque

2025-10-28 | Saint-Germaire | [Contact] | Retour qualité (emballage) |
Packaging faible | Remplacement produit | 48h | ✓ Bon
```

**Fréquence MAJ :** Temps réel (Angélique enregistre incident le jour même)

---

### Tâche 3.5 : Remplir onglet ALERTES (15 min template)

**Colonnes :**

```
Commande | Fournisseur | ETA Prévu | Aujourd'hui | Jours Avant ETA |
Risk Flag (Retard probable?) | Action
```

**Exemple :**

```
COM-001 | Médiafret | 2025-11-15 | 2025-11-10 | 5j | Non | Suivi normal
COM-002 | Emeris | 2025-11-18 | 2025-11-10 | 8j | À surveiller (historique) | Appel rappel j-2
COM-003 | Saint-Germaire | 2025-11-20 | 2025-11-10 | 10j | Non | Suivi normal
```

**Fréquence MAJ :** Hebdomadaire (lundi matin = check toutes les ETA futures)

---

## SEMAINE 4 : VALIDATION & OPÉRATIONNALISATION

### Tâche 4.1 : Test de continuité (30 min)

**Manager teste :** Peux-je appeler un contact #2 et obtenir les infos?

```
□ Appeler Superviseur Médiafret (contact 2)
  "Bonjour, j'appelle de Gedimat. Est-ce que vous pouvez me passer un statut
   sur la commande COM-XXX chez Médiafret?"
  → RÉSULTAT : Oui/Non → Si Non = Données incomp

□ Appeler Emeris contact 2 (si créé)
  "Quel est votre délai standard pour les tuiles?"
  → RÉSULTAT : Réponse rapide = OK
```

**Livrable :** Test checklist ✓ (continuité opérationnelle validée)

---

### Tâche 4.2 : Audit final données (30 min)

**Manager valide :**

```
☑ 100% contacts clés documentés (5+ fournisseurs)
☑ 2+ contacts par fournisseur stratégique minimum (Médiafret, Emeris)
☑ Accords informels tracibilisés (délais, tarifs, urgences)
☑ Aucun "[À compléter]" dans données critiques (Médiafret, Emeris)
☑ Scoring mensuel rempli et cohérent
☑ Incidents documentés avec causes
```

**Action :** Si items manquent → Appels complémentaires sem 4

---

### Tâche 4.3 : Formation équipe (30 min)

**Manager fait démo :**

```
□ Montrer onglet Contacts (où trouver un numéro)
□ Montrer onglet Scoring (comment on évalue fournisseurs)
□ Montrer onglet Incidents (comment enregistrer problème)
□ Montrer accès partagé (chacun peut lire, Angélique peut écrire)
□ Rappeler : "Si Angélique absente, utilisez contact #2 + notes contexte"
```

**Participants :** Angélique + Manager + [Éventuellement) remplacement Angélique

---

## RÉUNIONS CLÉS À CALENDRIER DÈS MAINTENANT

### Réunion 1 : Compilation données (Jour 1)
- **Quand :** Lundi 4 novembre 2025
- **Participants :** Angélique + Manager
- **Durée :** 1h
- **Ordre du jour :**
  - Démarrage CRM Phase 1
  - Qui compile quoi (responsabilités)
  - Dates limites (appels sem 2-3)

### Réunion 2 : Appels fournisseurs (Semaine 2)
- **Quand :** Mercredi 12 novembre 2025 (check de mi-semaine)
- **Participants :** Angélique + Manager
- **Durée :** 30 min
- **Ordre du jour :**
  - Quel(s) appel(s) restent à faire?
  - Données manquantes?
  - Ajustements avant Google Sheets

### Réunion 3 : Validation CRM (Semaine 4)
- **Quand :** Lundi 1 décembre 2025
- **Participants :** Angélique + Manager
- **Durée :** 1h
- **Ordre du jour :**
  - CRM Google Sheets opérationnel?
  - Test continuité réussi?
  - Qui appelle en cas absence Angélique?
  - Prochaines étapes (Réunion Emeris, etc.)

### Réunion 4 : Amélioration Emeris (Décembre)
- **Quand :** 15 décembre 2025
- **Participants :** Manager Gedimat + Emeris (contact principal + secondaire)
- **Durée :** 1h
- **Ordre du jour :**
  - Score 68/100 expliqué
  - Plan d'action 90j (atteindre 75+)
  - Engagement Emeris sur actions
  - Suivi hebdomadaire confirmé

---

## FICHIERS DE RÉFÉRENCE À UTILISER

```
Document | Usage | Quand |
─────────────────────────────────────────────────────────────
CRM_PLAN_GESTION_RELATIONNEL_FOURNISSEURS.md |
  Architecture complète + gouvernance | Lecture direction

GRILLE_SCORING_FOURNISSEURS_GEDIMAT.md |
  Méthodologie 4 critères + actions | Réunion amélioration Emeris

TEMPLATES_CONTACTS_CRM_GEDIMAT.md |
  Modèles fiches + checklist | Compilation données

CRM_CONTACTS_GEDIMAT_TEMPLATE.csv |
  Import direct Google Sheets | Jour 5-6 création CRM

RESUME_EXECUTIF_CRM_2PAGES.md |
  Synthèse direction | Présentation approbation
```

---

## INDICATEURS DE SUCCÈS PHASE 1

```
Week 4 (fin novembre) - CRM "GO LIVE"

✓ Contacts 100% documentés : 5+ fournisseurs
✓ 2+ contacts par partenaire stratégique (Médiafret, Emeris)
✓ Aucune dépendance personne unique
✓ Test continuité réussi (Manager appelle contact #2 = OK)
✓ Scoring novembre rempli (scores identifiés vs cibles)
✓ Incidents documentés (root cause traçable)
✓ Équipe formée (savent où trouver infos)

Si ✓ TOUS : Phase 1 SUCCESS → Passer Phase 2 (HubSpot) en janvier
Si ✗ CERTAINS : Ajustements décembre → Réévaluation 15 déc
```

---

**Checklist impression :**

```
□ Jour 1 : Compilation Angélique
□ Sem 2-3 : Appels fournisseurs clés
□ Sem 3 : Création Google Sheets
□ Sem 3 : Test Manager (contact #2 OK?)
□ Sem 4 : Audit final données
□ Sem 4 : Réunion validation équipe
□ Décembre : Réunion amélioration Emeris
□ Janvier : Réévaluation scores + Go Phase 2?
```

**Document de travail | À imprimer + cocher au fur et mesure | Version 1.0**
