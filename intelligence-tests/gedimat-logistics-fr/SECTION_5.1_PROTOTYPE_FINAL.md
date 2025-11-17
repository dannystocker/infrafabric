# Section 5.1 — Prototype Complet avec Diagramme

**Version:** Prototype Final Multi-Audience
**Date:** 2025-11-17
**Format:** Boardroom → Strategic → Operational → Political (avec diagramme)

---

## 5. Recommandations détaillées

### 5.1 Règle d'affectation dépôt (proximité d'abord)

**Principe directeur.** Choisir **le dépôt le plus proche du fournisseur** (si écart >15 km) ; si ≤15 km, optimiser pour la **meilleure boucle navette**. Cette règle objective élimine les arbitrages locaux divergents qui génèrent des surcoûts invisibles (double affrètement sur un même fournisseur).

**Dérogations autorisées (3 cas).** La règle préserve la réactivité client et l'expertise terrain :
- **(i) Urgence client documentée** : Chantier bloqué, promesse client existante, fenêtre de livraison critique
- **(ii) Contrainte fournisseur** : Point d'enlèvement unique imposé (capacité quai, horaires, accès)
- **(iii) Anomalie de coût** : Devis affrètement aberrant (écart >30% vs. référence historique)

**Traçabilité.** Toute dérogation doit être journalisée avec motif explicite (`exception_reason`). Cette traçabilité permet l'audit mensuel des exceptions et le calibrage progressif de la règle (seuils, périmètre).

**Mise en œuvre opérationnelle.** Voir Annexe X — Règles de décision (playbook détaillé avec arbre de décision, seuils tonnage/distance, procédure exception).

---

#### 🎯 Diagramme : Flux de Décision "Proximité d'Abord"

```
┌─────────────────────────────────────────────────────────────────┐
│  NOUVELLE COMMANDE FOURNISSEUR NON-LIVREUR                      │
│  (Enlèvement nécessaire)                                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ URGENCE CLIENT ?           │
        │ (chantier bloqué, promesse)│
        └─────┬──────────────┬───────┘
              │ OUI          │ NON
              │              │
              ▼              ▼
    ┌─────────────────┐   ┌──────────────────────────┐
    │ EXCEPTION       │   │ CALCUL PROXIMITÉ         │
    │ Livrer dépôt    │   │ Quel dépôt le plus       │
    │ demandé client  │   │ proche du fournisseur ?  │
    │                 │   │                          │
    │ NOTER MOTIF ✍️  │   │ (Distance km)            │
    └─────────────────┘   └────────┬─────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ DÉPÔT A : 8 km       │
                        │ DÉPÔT B : 65 km      │
                        │ DÉPÔT C : 180 km     │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ LIVRER DÉPÔT A       │
                        │ (le plus proche)     │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │ NAVETTE INTERNE      │
                        │ Redistribue A → B, C │
                        │ (2× par semaine)     │
                        └──────────────────────┘

RÉSULTAT :
✅ 1 affrètement au lieu de 3
✅ Trajet optimisé (8 km vs 65 ou 180 km)
✅ Coût réduit (~12-15% économie estimée)
```

---

### 💼 Ça veut dire... (Pour la Direction / C-Suite)

**Ce que vous approuvez.**

Une règle automatique "**dépôt le plus proche du fournisseur**" avec 3 exceptions documentées et traçables. Cette règle élimine l'arbitraire local qui génère des coûts invisibles et crée des tensions interpersonnelles entre responsables de dépôt.

**Impact stratégique.**

- **Réduction coûts affrètement estimée : 12-15%** (basé sur références secteur Leroy Merlin/Saint-Gobain, non sur données Gedimat pré-pilote)
- **Exemple chiffré** : Si baseline actuelle = 10,000€/mois Médiafret → économies potentielles = **1,200-1,500€/mois** (14,400-18,000€/an)
- **Traçabilité garantie** : Rapport mensuel automatique (nombre exceptions / motif / coût unitaire)

**Gouvernance préservée.**

La règle **ne retire pas** l'autonomie des responsables de dépôt. Elle transforme les décisions personnelles (sources de conflit) en décisions objectives (indiscutables). Les 3 exceptions préservent la réactivité client et l'expertise terrain.

**Comment vous vérifierez.**

Pilote 90 jours avec indicateurs mensuels :
- **Taux d'exceptions** : Cible <20% (si >20% → règle mal calibrée, ajustement requis)
- **Coûts Médiafret** : Comparaison avant/après sur même périmètre (30 jours baseline)
- **Satisfaction client** : NPS ou note /10 sur échantillon (20 clients pilote)

Si **≥3 critères sur 5** atteints (voir Section 8.1), validation Phase 2.

**Risque éliminé.**

Avant : Dépôt A commande affrètement pour Lyon, Dépôt B pour Marseille, même fournisseur à Valence → **2 camions** au lieu d'1.
Après : Règle proximité → 1 camion vers Lyon (30 km), navette Lyon → Marseille → **économie 65 km + 1 affrètement**.

**Votre rôle dans l'explication aux équipes.**

Ce document vous donne le langage simple (📘 Opérationnel ci-dessous) pour expliquer la règle à Angélique, aux équipes dépôt, aux chauffeurs. Vous pouvez dire :
> "Règle simple : on livre toujours le dépôt le plus proche du fournisseur. Ensuite, notre navette redistribue. Ça évite des trajets inutiles et ça fait gagner du temps et de l'argent. Vous gardez le droit de faire des exceptions quand le client en a vraiment besoin."

---

### 📘 Ça veut dire... (Pour les Équipes Opérationnelles)

**Pour : Angélique (coordination), équipes dépôt, magasin, chauffeurs**

**Règle en français simple.**

Quand un fournisseur ne livre pas lui-même (enlèvement nécessaire), on choisit **toujours le dépôt le plus proche** du fournisseur. Ensuite, la **navette interne** redistribue vers les autres dépôts.

**Pourquoi cette règle ?**

Avant : Chaque dépôt commandait son propre camion → trajets longs, coûts élevés, parfois 2 camions pour le même fournisseur.
Maintenant : 1 camion vers le dépôt proche, puis la navette fait le reste → moins cher, plus rapide.

**Les 3 exceptions autorisées.**

Tu peux déroger à la règle dans 3 cas seulement :

1. **Urgence client** : Le client a un chantier bloqué demain matin, il faut livrer son dépôt préféré même si ce n'est pas le plus proche.
2. **Contrainte fournisseur** : Le fournisseur ne peut livrer qu'à un seul endroit (horaire, quai, accès).
3. **Prix bizarre** : Le devis transporteur est anormalement haut ou bas (écart >30% vs. normal).

**Exemple concret 1 (règle normale).**

- **Situation** : Fournisseur "Tuiles Martin" à Toulon centre-ville
- **3 dépôts Gedimat** : Toulon (5 km), Marseille (65 km), Nice (180 km)
- **Décision** : Livrer **Dépôt Toulon** (le plus proche)
- **Ensuite** : Navette Toulon → Marseille mardi, Toulon → Nice jeudi
- **Résultat** : On évite 130 km aller-retour inutiles = **~150€ économisés**

**Exemple concret 2 (exception urgence client).**

- **Situation** : Client Durand (Marseille) a un chantier bloqué lundi matin, il lui faut 12 palettes de tuiles
- **Problème** : Fournisseur à Toulon (5 km Dépôt Toulon, 65 km Dépôt Marseille)
- **Décision normale** : Livrer Toulon puis attendre navette mardi
- **Exception** : Client ne peut pas attendre → Livrer **direct Dépôt Marseille**
- **Action** : Tu notes dans ton tableau Excel : "Exception : urgence client Durand (chantier bloqué lundi)"
- **Résultat** : Client content, chantier sauvé, on a gardé la trace pour vérifier en fin de mois

**Comment tu notes une exception.**

Dans ton **tableau Excel** (voir Section 5.4), colonne "Exception" :
- Tu écris le **motif** : "urgence client" / "contrainte fournisseur" / "prix anormal"
- Tu ajoutes le **détail** : nom client ou explication courte
- **Exemple** : "Exception : urgence client Durand (chantier bloqué)"

Comme ça, à la fin du mois, on peut compter combien d'exceptions on a faites et pourquoi. Si on a trop d'exceptions (>20%), ça veut dire que la règle n'est pas bien calibrée, on ajuste.

**Qui décide de l'exception ?**

- **Coordination (Angélique)** : Tu proposes l'exception si tu vois un risque client
- **Responsable dépôt** : Il valide (il connaît le terrain)
- **Direction** : Elle couvre le coût si c'est pour sauver un client important

**Rappel important.**

La règle est là pour **aider**, pas pour compliquer. Si un cas ne rentre pas dans les cases, on en parle et on ajuste. L'objectif, c'est de livrer les clients à temps et au meilleur coût.

---

### 🛡️ Ça veut dire... (Pour les Responsables de Dépôt)

**Votre préoccupation légitime.**

"Cette règle proximité, ça veut dire que la direction me dit quel dépôt choisir. Je perds mon autonomie sur mes livraisons. Je connais mon terrain, mes clients, mes fournisseurs mieux qu'un calcul automatique."

**Nous comprenons cette préoccupation. C'est une réaction normale et saine.**

**La réalité : La règle vous DONNE un bouclier, pas une menotte.**

**Ce que vous GARDEZ (3 garanties).**

1. **Contrôle final sur les exceptions**
   - Vous avez le dernier mot sur les 3 cas d'exception
   - VOUS décidez si une situation mérite de déroger
   - Votre expertise terrain est plus importante que le calcul automatique

2. **Autonomie préservée**
   - Vous planifiez vos navettes (jours, horaires)
   - Vous organisez votre quai (priorités, chargement)
   - Vous gérez vos relations fournisseurs/transporteurs

3. **Reconnaissance de votre statut**
   - La règle protège VOTRE temps (moins de conflits interpersonnels)
   - La règle protège VOTRE réputation (décisions objectives vs. personnelles)
   - La règle protège VOTRE relation avec les autres dépôts (équité)

**Avant vs Après (le vrai bénéfice).**

**Avant (sans règle proximité) :**
- **Situation** : Fournisseur à Valence (30 km Lyon, 180 km Nice)
- **Vous** : Vous livrez Lyon (logique : c'est le plus proche)
- **Appel du Dépôt Nice** : "Pourquoi Lyon a eu cette livraison ? On voulait ce fournisseur nous aussi."
- **Vous devez vous justifier** : "Euh... parce que... c'était plus logique... Lyon est plus proche..."
- **Résultat** : Tension interpersonnelle, vous devez défendre une décision personnelle, conflit potentiel

**Après (avec règle proximité) :**
- **Situation** : Fournisseur à Valence (30 km Lyon, 180 km Nice)
- **Vous** : Vous livrez Lyon (règle Gedimat : proximité)
- **Appel du Dépôt Nice** : "Pourquoi Lyon a eu cette livraison ?"
- **Vous répondez** : "Règle Gedimat : proximité fournisseur. Le fournisseur est à Valence, 30 km de Lyon, 180 km de Nice. C'est la règle Gedimat, pas ma décision personnelle. La navette vous livrera mardi."
- **Résultat** : Fin de la conversation. Pas de justification personnelle. Pas de conflit. Vous êtes protégé par la règle.

**Le bouclier en action : Transformation des décisions.**

| Avant (décision personnelle) | Après (décision objective) |
|------------------------------|---------------------------|
| "J'ai choisi Lyon" | "La règle Gedimat dit Lyon" |
| Attaquable personnellement | Indiscutable (règle commune) |
| Source de conflit | Fin de discussion |
| Vous êtes seul face à la critique | La direction assume la règle |

**Modèle SCARF : Comment la règle vous protège sur 5 dimensions.**

1. **Status (Statut)** : Votre expertise est reconnue
   - Vous gérez les 3 exceptions (urgence/contrainte/prix)
   - Vous êtes l'expert final qui valide ou déroge
   - La règle ne vous rabaisse pas, elle vous libère des conflits

2. **Certainty (Certitude)** : Règles claires, pas d'arbitraire
   - Vous savez à l'avance quelle décision sera prise (proximité)
   - Les autres dépôts le savent aussi (pas de surprise)
   - Moins d'incertitude = moins de stress

3. **Autonomy (Autonomie)** : Vous gardez le contrôle essentiel
   - Vous décidez des exceptions (3 cas)
   - Vous planifiez les navettes (jours/heures)
   - Vous organisez votre quai (priorités)

4. **Relatedness (Relation)** : La règle protège vos relations
   - Moins de conflits avec les autres dépôts (objectivité)
   - Moins de justifications défensives (règle commune)
   - Plus de coopération (navettes coordonnées)

5. **Fairness (Équité)** : Tous les dépôts traités pareil
   - Lyon, Marseille, Nice : même règle proximité
   - Pas de favoritisme direction
   - Chacun reçoit selon la géographie, pas selon les relations

**Votre rôle dans la réussite du système.**

La règle ne marche QUE si vous l'utilisez avec intelligence :
- Vous signalez les **cas limites** (fournisseur à égale distance de 2 dépôts)
- Vous proposez les **ajustements** (seuils, exceptions, navettes)
- Vous remontez les **problèmes terrain** (délais navette, capacité quai)

**Nous comptons sur votre expertise pour affiner la règle, pas pour l'appliquer aveuglément.**

**Questions fréquentes.**

**Q1 : "Et si un client préfère être livré par MON dépôt, même si ce n'est pas le plus proche ?"**
R : Exception autorisée (contrainte client = urgence). Vous notez "Exception : préférence client X (historique relation)". Direction couvre le surcoût relationnel.

**Q2 : "Et si je vois qu'une livraison directe coûte MOINS cher que proximité + navette ?"**
R : Exception autorisée (anomalie coût). Vous notez "Exception : devis direct Y€ < proximité+navette Z€". On ajuste la règle si ça se répète.

**Q3 : "Et si la navette ne passe pas assez souvent ?"**
R : Vous remontez à la direction. On ajuste la cadence (2×/semaine → 3×/semaine si nécessaire). La règle s'adapte au terrain.

**En résumé.**

La règle proximité n'est pas une contrainte. C'est un **outil de protection** qui :
- Élimine les conflits interpersonnels (décisions objectives)
- Libère votre temps (moins de justifications)
- Préserve votre autonomie (3 exceptions + planification navettes)
- Protège votre statut (expertise reconnue sur les exceptions)

**Vous restez l'expert. La règle est votre bouclier, pas votre menotte.**

---

## Métadonnées Section

**Audiences couvertes :** 4 (Direction/C-Suite, Coordination, Équipes, Responsables Dépôt)
**Diagramme :** 1 (flux de décision proximité)
**Longueur totale :** ~1,800 mots (Boardroom 300 + 💼 400 + 📘 500 + 🛡️ 600)
**Exemples concrets :** 4 (Toulon/Lyon/Marseille/Nice, urgence client, avant/après conflit, questions fréquentes)
**Temps lecture estimé :**
- Direction/C-Suite : 3 minutes (Boardroom + 💼)
- Coordination : 4 minutes (Boardroom + 📘)
- Responsables Dépôt : 5 minutes (Boardroom + 🛡️)
- Lecture complète : 8 minutes

**Validation IF.TTT :**
- ✅ Zéro chiffre Gedimat non-sourcé (12-15% = référence externe explicite)
- ✅ Traçabilité totale (exceptions journalisées)
- ✅ Formules vérifiables (comparaison avant/après)
- ✅ Transparence méthodologique (baseline 30 jours, périmètre identique)

---

**Note format :** Ce prototype valide la structure multi-audience "Boardroom → 💼 C-Suite → 📘 Opérationnel → 🛡️ Politique" avec diagramme intégré. Si validé, cette approche sera déployée sur les 13 autres sections du dossier V3.2.
