# DIAGNOSTIC - Cartographie Flux & Typologie Commandes
## PASS 2 - Analyse Flux Logistique Gedimat

**Date:** 16 novembre 2025
**Responsable Analyse:** Angélique (Coordinatrice Fournisseurs)
**Périmètre:** 3 dépôts Gedimat (Évreux, Méru, Gisors) + chaîne clients
**Document:** 3-4 pages - Diagnostic directeur

---

## PARTIE A - CARTOGRAPHIE FLUX APPROVISIONNEMENT

### 1. Diagramme Global : Fournisseurs → 3 Dépôts → Clients

```
┌──────────────────────────────────────────────────────────────────┐
│                    CHAÎNE LOGISTIQUE GEDIMAT                      │
└──────────────────────────────────────────────────────────────────┘

ÉTAPE 1 : APPROVISIONNEMENT (Fournisseur → Dépôt)
═════════════════════════════════════════════════════════

Fournisseurs non-livreurs (ex: Éméris, Édiliens, etc.)
              │
              │  [DÉCISION 1: Poids total?]
              │
         ─────┴─────────────────────────
         │                              │
    ≤10 TONNES                     >10 TONNES
    (Capacité Driver)              (Transporteur Externe)
         │                              │
    ┌────▼────┐                   ┌────▼──────────┐
    │Chauffeur│                   │Médiafret      │
    │Interne  │                   │+ Sous-traitants│
    │Gedimat  │                   │(Transporteurs) │
    └────┬────┘                   └────┬──────────┘
         │                             │
         │          ┌──────────────────┤
         │          │                  │
         │          │  [DÉCISION 2: Dépôt prioritaire?]
         │          │  Distance? Volume? Urgence?
         │          │
    ┌────┴──┐   ┌───┴───┬──────┬──────┐
    │        │   │       │      │      │
    │        │   │       │      │      │
   DÉPÔT   DIRECT?    ┌──▼──────┴──────▼──┐
   ÉVREUX  │   │      │  DÉPÔT PIVOT      │
   (27140) │   │      │  (Proximité fournisseur)
    │      │   │      │  ex: GISORS(27xxx)
    │      │   │      └──────┬───────────┘
    │      │   │             │
    │      └───┘             │
    │          │             │
    │    ┌─────┴──────┐      │
    │    │ Délivré à  │      │
    │    │ ce dépôt   │      │
    │    └────────────┘      │
    │                        │
    └─────────────┬──────────┘


ÉTAPE 2 : REDISTRIBUTION INTERNE (Dépôt → Dépôts)
════════════════════════════════════════════════

APRÈS livraison dépôt pivot, redistribution via:

    Navette Interne (Chauffeur Gedimat)
    ├─ Fréquence : 2 fois/semaine (estimé)
    ├─ Capacité : Flexible (jusqu'à 10t généralement)
    ├─ Coût : Salarial fixe (très économique)
    ├─ Trajectoire typique :
    │   └─ Gisors (pivot) → Évreux → Méru
    │   └─ Ou Gisors → Méru → Évreux
    └─ Temps moyen : 1-2 jours après livraison

         DÉPÔT PIVOT
         (Gisors)
            │
            │ NAVETTE 1
            ├──┐
            │  │
    ┌───────▼──▼────────┐
    │                    │
  DÉPÔT              DÉPÔT
  ÉVREUX             MÉRU
  (27140)            (60110)
    │                  │
    │ (Magasin        │ (Magasin
    │  Gedimat)       │  Gedimat)
    │                  │
    └────┬──────┬──────┘
         │      │
      CLIENTS (petits, moyens, gros)


ÉTAPE 3 : LIVRAISON CLIENT FINAL
═════════════════════════════════

Dépôt → Client par:
  ├─ Enlèvement client (lui-même)
  ├─ Livraison Gedimat interne (si demande)
  └─ Livraison externe si client gros volume

```

---

### 2. Exemple Concret : Cas Tuiles Éméris

**Situation:**
- Fournisseur Éméris fabrique tuiles (non-livreur)
- Commande groupée : 15 tonnes pour Méru + 5 tonnes pour Gisors = **20 tonnes total**
- Total >10 tonnes → affrètement externe **obligatoire**

**Décision Routage Actuelle:**

```
COMMANDE GROUPÉE
  ├─ 15t tuiles → Dépôt MÉRU (60110)
  └─ 5t tuiles → Dépôt GISORS (27xxx)

POIDS TOTAL: 20 tonnes > 10t

  ┌─ OPTION A (Défense territoriale - Non optimal)
  │  └─ Transporteur va d'abord à MÉRU (15t = plus volume)
  │     └─ Puis redistribution Méru → Gisors (navette)
  │     └─ COÛT: Trajet Éméris→Méru + navette Méru→Gisors
  │
  ├─ OPTION B (Proximité dépôt - RECOMMANDÉ actuel)
  │  └─ Transporteur va à GISORS (plus proche Éméris)
  │     └─ Livre 5t direct
  │     └─ Puis navette GISORS→MÉRU (15t)
  │     └─ COÛT: Trajet Éméris→Gisors + navette Gisors→Méru (moins cher)
  │
  └─ OPTION C (Urgence client - À évaluer)
     └─ Si Méru a commande urgente (chantier J+2)
        └─ Peut justifier surcoût livraison directe Éméris→Méru
        └─ COÛT: Plus cher transport, mais évite pénalité client

ARBITRAGE RÉEL:
- Gisors est généralement plus proche d'Éméris
- Option B (Gisors pivot) économise environ 15-25% sur trajet vs Méru direct
- MAIS: Si clients Méru sont urgents → négociation coût vs satisfaction
```

---

### 3. Mapping Fournisseurs & Dépôts (Distance approximative)

| Fournisseur | Localité | Type | Dépôt Closest | Distance (km estim.) | Dépôt 2e | Dépôt 3e |
|---|---|---|---|---|---|---|
| Éméris | Nord Oise | Tuiles | GISORS | ~30 | Méru 40 | Évreux 80 |
| Édiliens | Loire-Atlantique | Ciment/Matériaux | ÉVREUX? | ~150 (A) | Gisors ~170 | Méru ~190 |
| Distributeurs Sud | Provence | Divers | ÉVREUX? | ~400 | Gisors ~420 | Méru ~440 |
| Fournisseurs locaux | Île-de-France | Divers | GISORS/MÉRU | ~20-50 | Variable | Variable |

*Note: Distances approximatives - Requête: Cartographie géographique précise + coords GPS fournisseurs clés*

---

### 4. Points de Décision Critique (Arbitrage)

**DÉCISION 1: Poids Total Détermine Mode Transport**

```
Poids total commandes groupées (fournisseur unique)
      │
      ├─ ≤10 tonnes
      │  └─ Chauffeur interne (coût fixe très faible)
      │     └─ Peut aller dépôt optimal = distance mini
      │
      └─ >10 tonnes
         └─ Affrètement externe (Médiafret, coût variable, important)
            └─ ALORS: Décision 2 critique
```

**DÉCISION 2: Dépôt Pivot (>10 tonnes) - Trois Critères Conflictuels**

```
       ┌─── CRITÈRE DISTANCE ───┐
       │  "Dépôt + proche"      │
       │  Économise transport   │
       │  Priorité LOGISTIQUE   │
       │                        │
ARBITRAGE ────────────────────────── → SCORE DÉCISION
       │                        │
       │  Critère VOLUME       │
       │  "Dépôt + gros volume"│
       │  Défend « son » dépôt │
       │  Priorité TERRITORIAL │
       │                        │
       └─── CRITÈRE URGENCE ────┘
          "Client chantier J+2"
          Priorité CLIENT
          Accepte surcoût?
```

**Trois Règles Actuelles (Conflictuelles):**

1. **Règle Volume:** « Dépôt avec le plus de tonnage veut être livré d'abord »
   - Exemple: Méru (15t) > Gisors (5t) → Méru exige livraison directe
   - Problème: Ignorer proximité fournisseur (coût +20% vs pivot)

2. **Règle Distance:** « Dépôt le plus proche du fournisseur = pivot »
   - Exemple: Éméris-Gisors 30km << Éméris-Méru 40km → Gisors pivot
   - Économie transport: Gisors pivot vs Méru direct (économie estim. 70-100€/trajet)
   - Problème: Méru « crie » moins de proximité = sentiment inéquité

3. **Règle Urgence:** « Client urgent prime sur optimisation coût »
   - Exemple: Client chantier Méru J+2 → livraison directe Éméris-Méru acceptée
   - Surcoût estimé: 70-100€
   - Bénéfice: Client satisfait, pas de pénalité (LTV > économie transport)
   - Problème: Mal documentée, créée arbitrage informel (Angélique décide au feeling)

---

## PARTIE B - TYPOLOGIE COMMANDES PAR POIDS

### Estimation Distribution Poids Commandes (à valider données réelles)

Basée sur contexte Gedimat (matériaux construction) + franchiisé:

| Tranche | Poids | % Estimé | Mode Transport | Coût Unité Transporteur | Délivrable Dépôt Unique |
|---|---|---|---|---|---|
| **T1** | 0-2 tonnes | ~15% | Chauffeur interne | Gratuit (fixe) | Oui, direct |
| **T2** | 2-5 tonnes | ~20% | Chauffeur interne | Gratuit (fixe) | Oui, direct |
| **T3** | 5-10 tonnes | ~25% | Chauffeur interne | Gratuit (fixe) | Oui, direct |
| **T4** | 10-15 tonnes | ~20% | Médiafret/Externe | ~500-700€/trajet | Pivot + navette |
| **T5** | 15-20 tonnes | ~12% | Médiafret/Externe | ~700-900€/trajet | Pivot + navette |
| **T6** | 20-30 tonnes | ~6% | Médiafret (semi) | ~1000-1300€/trajet | Pivot + navette |
| **T7** | >30 tonnes | ~2% | Multiple livraisons | Cas par cas | À segmenter |
| **TOTAL** | | **100%** | | | |

**Insights:**

- **60% sous 10 tonnes:** Pas de problème affrètement externe
- **40% au-dessus 10 tonnes:** Nécessite affrètement → **zone critique arbitrage**
- **T4-T5 (32% total):** Tranche majeure, enjeu décision dépôt pivot crucial
- **Cas urgence:** Estimé ~5-10% des T4-T6 (urgence client déroge optimisation)

---

## PARTIE C - INEFFICACITÉS IDENTIFIÉES (Diagnostic PASS 2)

### **Inefficacité 1: Défense Territoriale (Dépôts vs Logistique)**

**Description:**
Chaque dépôt défend ses intérêts (volume, chiffre d'affaires local) plutôt que optimisation groupe.

**Manifestation concrète:**
- Dépôt Méru (15t): « J'ai le plus de commandes, je veux livraison directe Éméris→Méru »
- Dépôt Gisors (5t): « Moi j'en ai que 5, mais c'est urgent, je veux directe aussi »
- Résultat: Négociation informelle chaque fois, décision variable
- Impact: Coûts transport +20-30% vs optimal, délais imprévisibles

**Cause racine:**
- Pas de règle formalisée (multi-critère)
- Responsabilité décision floue (déléguée à Angélique ad-hoc)
- Pas de visibilité sur coûts par dépôt

---

### **Inefficacité 2: Absence Alertes Automatisées (Suivi Fournisseurs)**

**Description:**
Retards fournisseurs détectés **manuellement** après coup par Angélique, pas en amont.

**Manifestation concrète:**
- Éméris devait livrer le 15/11, effectif 20/11 (retard +5 jours)
- Angélique s'aperçoit le 20/11 en fin de journée (par appel, SMS, email aléatoire)
- Client chantier qui démarre 22/11 → panique, solution d'urgence coûteuse
- Exemple impact: Client annule, achète ailleurs, stock invendu coûte pénalité stockage

**Cause racine:**
- Pas de dashboard alertes automatiques (ARC date livraison dépassée → email/SMS alarm)
- Logiciel Gedimat « insuffisant » = pas d'alertes, pas de stats, pas de scoring fiabilité fournisseur
- Suivi manuel = dépend de mémoire Angélique + appels aléatoires

---

### **Inefficacité 3: Logiciel Insuffisant (Pas Statistiques, Pas Relationnel Documenté)**

**Description:**
Outils IT ne capturent pas contexte critique pour arbitrage intelligent.

**Manifestation concrète:**

| Info Manquante | Impact | Exemple |
|---|---|---|
| **Contacts clés non documentés** | Dépend de mémoire Angélique (4 ans métier) | Mélissa chez Médiafret = seul interlocuteur connu, si elle part = risque |
| **Notes relationnelles** | Pas d'historique « Éméris retard chronique mais réactif urgences » | Arbitrage coût vs urgence basé sur intuition, pas données |
| **Stats satisfaction client** | Pas de feedback positif capturé | On sait quand ça va mal (réclamation), pas quand ça va bien |
| **Scoring fournisseur** | Pas de classement fiabilité, qualité, réactivité | Tous fournisseurs traités pareils |
| **Coûts par dépôt** | Pas de visibilité transport Évreux vs Méru vs Gisors | Défense territoriale = pas de data pour arbitrer |

**Cause racine:**
- ERP Gedimat existant « pas assez performant et assez détaillé »
- Pas de module CRM logistique (suivi fournisseurs)
- Pas de dashboard coûts/performance

---

### **Inefficacité 4: Arbitrage Manuel & Non-Documenté (Décisions Informelles)**

**Description:**
Décisions critiques sur dépôt pivot, urgences, exceptions prises par Angélique informellement.

**Manifestation concrète:**
- « Normalement dépôt optimal = le plus proche »
- « Mais si client urgent = on change »
- « Mais si dépôt gros volume = conflictueux »
- Résultat: Pas de règle claire, autres coordinateurs ne peuvent pas décider seuls

**Cause racine:**
- Processus d'arbitrage pas formalisé
- Pas d'algorithme décision (scoring multicritère)
- Pas de documentation: « Si X → faire Y »
- Connaissance tacite Angélique non transférable

---

### **Inefficacité 5: Satisfaction Client Mesurée Uniquement Négativement**

**Description:**
Feedback client capturé seulement en cas de problème (réclamation), pas proactivement.

**Manifestation concrète:**
- Client chantier reçoit marchandise à temps → pas de feedback
- Client chantier reçoit marchandise tardive → réclamation, négo compensation
- Impact: « Quand ça va mal, on le sait tout de suite. Quand ça va bien, on ne sait rien. »
- Arbitrage coûts vs satisfaction donc aveugle: on justifie surcoût transport « pour satisfaction » mais pas de baseline

**Cause racine:**
- Pas de processus mesure satisfaction proactive (appel J+1, sondage, NPS)
- Logiciel ne sauve pas feedback
- Culture réactive vs proactive

---

### **Inefficacité 6: Navette Interne Pas Optimisée (Fréquence, Trajectoire, Charge)**

**Description:**
Redistribution interne (2x/semaine estimé) non orchestrée vs demande.

**Manifestation concrète:**
- Marchandise arrive pivot (Gisors) le mardi → redistribution vendredi (3 jours attente)
- Mais client Méru urgent avait besoin lundi
- Trajectoire navette: Gisors→Évreux→Méru (pas optimisée vs charges réelles)
- Chauffeur interne peut faire 10t, mais souvent sous-chargé (7-8t) = inefficacité

**Cause racine:**
- Fréquence navette fixe (2x/semaine) vs demande variable
- Pas de suivi charge réelle navette (utilisation % capacité?)
- Pas d'optimisation route (TSP tournée laitière)

---

### **Inefficacité 7: Communication Client Insuffisante (Pas d'Alerte Proactive Retard)**

**Description:**
Client n'est pas informé proactivement si retard détecté → crée incertitude, panique.

**Manifestation concrète:**
- Retard fournisseur détecté J+2, mais client pas informé tout de suite
- Client découvre jour du chantier que marchandise pas arrivée → chaos, annulation
- Alternative: Appel proactif J+1 retard → « Retard X jours, voici alternatives: attendre, enlever ailleurs, fournisseur concurrent »
- Client reprendre se réorganiser vs panique totale

**Cause racine:**
- Pas de process d'alerte client automatique (SMS/email template)
- Dépend de volonté Angélique de appeler individuellement
- Pas de script standardisé communication retard

---

## PARTIE D - SYNTHÈSE DIAGNOSTIQUE

### Points Clés PASS 2

| Aspect | État Actuel | Problème | Impact Priorité |
|---|---|---|---|
| **Flux général** | Fonctionnel | Coûts affrètement élevé, arbitrage non-optimal | ÉLEVÉE |
| **Décision dépôt pivot** | Manuel, ad-hoc | 3 critères conflictuels, pas de règle multi-critère | ÉLEVÉE |
| **Alertes fournisseurs** | Manuelles | Retards détectés trop tard (J+2/3) | ÉLEVÉE |
| **Données dépôts** | Manquantes | Pas de coûts, stats par dépôt | MOYENNE |
| **Logiciel** | Insuffisant | Pas d'alertes, pas de scoring, pas de relationnel documenté | ÉLEVÉE |
| **Satisfaction client** | Réactive uniquement | Pas de baseline positive, arbitrage coûts vs satis aveugle | MOYENNE |
| **Navette interne** | Fonctionnelle | Pas optimisée fréquence/charge/route | BASSE |
| **Communication client** | Réactive | Pas d'alerte retard proactive | MOYENNE |

### Opportunités Quick Wins (PASS 3 Recommandations)

1. **Alertes retard fournisseur** (Excel + Email auto) → Détection J+1 au lieu J+3
2. **Scoring multicritère dépôt** (Proximité 35%, Volume 30%, Urgence 35%) → Règle formalisée
3. **Sondage satisfaction 50 clients pilotes** → Baseline positive (NPS, CSAT)
4. **Dashboard coûts/taux service** → Transparence par dépôt (élimine « territorial »)

---

## ANNEXE: Diagramme Décision Dépôt (Simplifié)

```
COMMANDE GROUPÉE ARRIVÉE
  │
  ├─ Poids total?
  │  ├─ ≤10t → Chauffeur interne (dépôt optimal = distance mini)
  │  └─ >10t → DÉCISION 2 (voir ci-dessous)
  │
  └─ >10 TONNES (Affrètement externe)
     │
     ├─ Urgence client?
     │  ├─ OUI (chantier J+2) → Accepter surcoût, livrer dépôt urgent
     │  └─ NON → Aller à "Distance"
     │
     ├─ Distance?
     │  ├─ Dépôt A (20km du fournisseur) → A = Pivot
     │  ├─ Dépôt B (50km du fournisseur) → A = Pivot
     │  └─ Calcul: Trajet À→B + navette B→autres < Trajet direct B
     │
     └─ LIVRAISON DÉPÔT PIVOT
        │
        └─ Navette interne redistribue J+1 à J+2
```

---

**Document généré:** PASS 2 - Cartographie Flux & Typologie
**Prochaine étape:** PASS 3 (Rigor Validation) + PASS 4 (Cross-Domain Expertise)
**À affiner avec:** Données géographiques précises, coûts réels Gedimat, volumes exact 12 derniers mois
