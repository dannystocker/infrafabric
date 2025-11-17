# PROMPT GPT-5 PRO : Section 5.1 avec "Ça veut dire..." (Prototype)

**Objectif :** Générer la section 5.1 du dossier Gedimat avec 3 couches "Ça veut dire..." pour validation de concept.

---

## CONTEXTE

Tu vas lire la Section 5.1 (Règle d'affectation dépôt) du dossier technique Gedimat V3.2 et ajouter 3 traductions audience-spécifiques immédiatement après le texte technique.

**Inspiration :** InfraFabric v11 utilise 4 couches narratives simultanées (Page-Zero/Boardroom/Cynical/Imagery). Nous adaptons ce modèle au contexte français business avec "Ça veut dire..." pour 3 audiences.

**Innovation :** Un seul document qui parle à TOUS - direction, opérationnels, résistance politique - simultanément.

---

## SECTION 5.1 À TRAITER (TEXTE TECHNIQUE ACTUEL)

```markdown
### 5.1 Règle d'affectation dépôt (proximité d'abord)

- Choisir **le dépôt le plus proche du fournisseur** (si écart >15 km) ; si ≤15 km, optimiser pour la **meilleure boucle navette**.
- **Dérogations valides (3)** : (i) Urgence client documentée, (ii) Contrainte fournisseur (point unique), (iii) Anomalie de coût (devis aberrant).
- **Journaliser** toute dérogation (`exception_reason`).
*(Voir Annexe X — Règles de décision)*
```

---

## TA MISSION : AJOUTER 3 COUCHES "ÇA VEUT DIRE..."

Après le texte technique ci-dessus, ajoute une ligne de séparation (`---`) puis les 3 traductions suivantes :

### 1. 📘 Ça veut dire... (Pour Angélique - Opérationnel)

**Audience :** Angélique Montanarini, coordinatrice logistique, formation non-universitaire, expérience terrain
**Objectif :** Comprendre quoi faire, quand, pourquoi, comment
**Ton :** Simple, chaleureux, respectueux, jamais condescendant
**Longueur :** 150-200 mots

**Contenu obligatoire :**
- Règle en français très simple (10-15 mots par phrase)
- 2 exemples concrets Gedimat (Toulon/Lyon/Marseille/Nice)
- Quand faire une exception (3 cas expliqués simplement)
- Comment noter l'exception (tableau Excel, colonne "exception")
- Pourquoi c'est important (éviter trajets inutiles + argent)

**Format :**
```markdown
### 📘 Ça veut dire... (Pour Angélique)

[Traduction opérationnelle ici]

**Exemple concret 1 :**
[Exemple avec dépôts Gedimat]

**Exemple concret 2 :**
[Exemple avec exception]

**Comment noter une exception :**
[Instructions tableau Excel]
```

---

### 2. 💼 Ça veut dire... (Pour le PDG - Stratégique)

**Audience :** PDG Gedimat, préoccupation business/ROI/risque
**Objectif :** Comprendre l'impact business, pourquoi approuver, quel risque évité
**Ton :** Direct, stratégique, chiffres quand pertinents
**Longueur :** 80-120 mots

**Contenu obligatoire :**
- Impact business : économies potentielles (fourchette)
- Décision : qu'est-ce que j'approuve exactement ?
- Risque évité : que se passe-t-il SANS cette règle ?
- Traçabilité : comment je sais si ça marche ? (exceptions journalisées)
- ROI simple : règle = shield contre arbitraire coûteux

**Format :**
```markdown
### 💼 Ça veut dire... (Pour le PDG)

**Ce que vous approuvez :**
[Décision claire]

**Impact business :**
[Économies estimées ou risque évité]

**Pourquoi maintenant :**
[Urgence ou opportunité]

**Comment vous vérifierez :**
[Traçabilité des exceptions]
```

---

### 3. 🛡️ Ça veut dire... (Pour les Responsables de Dépôt - Résistance)

**Audience :** Responsables de dépôt Lyon/Marseille/Nice, préoccupation autonomie/status
**Objectif :** Désarmer résistance SCARF (Status/Certainty/Autonomy/Relatedness/Fairness)
**Ton :** Empathique, reconnaissance préoccupation, reframing protection
**Longueur :** 100-150 mots

**Contenu obligatoire :**
- Reconnaissance préoccupation : "Vous pensez : je perds mon autonomie"
- Reframing threat → protection : "La règle vous DONNE un bouclier"
- Autonomie préservée : "Vous gardez contrôle sur les 3 exceptions"
- Avant/Après : Conflit interpersonnel vs. Règle Gedimat (fin de discussion)
- SCARF : Status maintenu (vous êtes expert final), Certainty augmentée (règles claires)

**Modèle SCARF (David Rock) :**
- **S**tatus : Personne ne perd prestige
- **C**ertainty : Règles claires, pas d'arbitraire
- **A**utonomy : Vous gardez contrôle final
- **R**elatedness : Règle protège relations entre dépôts
- **F**airness : Tous traités pareil (proximité = objectif)

**Format :**
```markdown
### 🛡️ Ça veut dire... (Pour les Responsables de Dépôt)

**Votre préoccupation légitime :**
[Reconnaissance perte autonomie perçue]

**La réalité :**
[Reframing : règle = protection, pas menace]

**Ce que vous GARDEZ :**
[3 exceptions + contrôle final]

**Avant vs Après :**
- **Avant (sans règle) :** [Conflit interpersonnel]
- **Après (avec règle) :** [Bouclier objectif]
```

---

## EXEMPLES DE QUALITÉ ATTENDUE

### Exemple : Traduction Opérationnelle (📘)

**BON :**
> Règle simple : toujours choisir le dépôt le plus proche du fournisseur.
>
> **Exemple 1 :** Fournisseur Martin à Toulon (centre-ville) → Dépôt Toulon (5 km). PAS Dépôt Marseille (65 km), même si Marseille le demande.
>
> **Exemple 2 - Exception urgence :** Client Durand a un chantier bloqué, seul Marseille peut livrer demain → OK, exception autorisée. Tu notes dans ton tableau : "Exception : urgence client Durand (chantier bloqué)."
>
> Pourquoi c'est important : On évite 130 km aller-retour inutiles = 150€ économisés par livraison.

**MAUVAIS (trop technique) :**
> La règle d'affectation optimise le coût de transport en minimisant la distance parcourue selon un algorithme de proximité géographique...

**MAUVAIS (condescendant) :**
> C'est très simple ma petite Angélique, tu vas voir, c'est facile...

---

### Exemple : Traduction Stratégique (💼)

**BON :**
> **Ce que vous approuvez :** Règle automatique "dépôt le plus proche" avec 3 exceptions documentées.
>
> **Impact business :** Réduction estimée 12-15% des coûts Médiafret (traçable via exceptions journalisées). Si baseline = 10,000€/mois, économies = 1,200-1,500€/mois.
>
> **Risque évité :** Arbitrages locaux non alignés → double affrètement → surcoûts invisibles. La règle rend les anomalies visibles.
>
> **Comment vous vérifierez :** Rapport mensuel : nombre exceptions / motif / coût. Si >20% exceptions → règle mal calibrée, ajustement.

**MAUVAIS (trop vague) :**
> Cette règle améliore l'efficacité logistique et réduit les coûts.

---

### Exemple : Désarmement Résistance (🛡️)

**BON :**
> **Votre préoccupation légitime :** "Cette règle, ça veut dire que la direction me dit comment faire mon travail. Je perds mon autonomie."
>
> **La réalité :** La règle vous DONNE un bouclier, pas une menotte.
>
> **Ce que vous GARDEZ :**
> - Contrôle final : vous validez chaque livraison
> - 3 exceptions autorisées : urgence, contrainte fournisseur, prix bizarre
> - Expertise : vous décidez si le cas mérite exception
>
> **Avant vs Après :**
> - **Avant :** Dépôt Nice vous appelle : "Pourquoi Lyon a eu cette livraison ?" → Conflit personnel
> - **Après :** "Règle Gedimat : proximité fournisseur. Lyon était à 5 km, Nice à 180 km." → Fin de la conversation. Pas de conflit.
>
> La règle transforme les décisions personnelles en décisions objectives. Vous êtes protégé.

**MAUVAIS (ignore préoccupation) :**
> La règle est simple et tout le monde doit la suivre.

**MAUVAIS (pas de reframing) :**
> Vous devez respecter la règle mais vous pouvez faire des exceptions.

---

## STYLE ET TON FINAL

### Règles Générales

✅ **À FAIRE :**
- Français très clair (phrases 10-15 mots max)
- Ton chaleureux mais professionnel
- Exemples concrets avec villes Gedimat réelles (Toulon, Lyon, Marseille, Nice)
- Chiffres quand pertinents (km, €, %)
- Reconnaissance des préoccupations avant de reframer
- "Tu" pour Angélique, "Vous" pour PDG/Responsables

❌ **À ÉVITER :**
- Jargon technique non-expliqué
- Anglicismes (utiliser français : "tableau de bord" pas "dashboard")
- Ton condescendant ou infantilisant
- Promesses chiffrées trop précises (rester fourchettes)
- Ignorer les préoccupations émotionnelles

---

## VALIDATION FINALE

Avant de fournir le résultat, vérifie :

- [ ] Les 3 couches "Ça veut dire..." sont présentes
- [ ] 📘 Angélique : 2 exemples concrets minimum
- [ ] 💼 PDG : Impact business chiffré (fourchette)
- [ ] 🛡️ Responsables : Reconnaissance préoccupation + reframing threat → protection
- [ ] Zéro anglicisme dans tout le texte
- [ ] Ton respectueux partout (jamais condescendant)
- [ ] Longueurs respectées (150-200 / 80-120 / 100-150 mots)

---

## FORMAT DE SORTIE ATTENDU

```markdown
### 5.1 Règle d'affectation dépôt (proximité d'abord)

- Choisir **le dépôt le plus proche du fournisseur** (si écart >15 km) ; si ≤15 km, optimiser pour la **meilleure boucle navette**.
- **Dérogations valides (3)** : (i) Urgence client documentée, (ii) Contrainte fournisseur (point unique), (iii) Anomalie de coût (devis aberrant).
- **Journaliser** toute dérogation (`exception_reason`).
*(Voir Annexe X — Règles de décision)*

---

### 📘 Ça veut dire... (Pour Angélique)

[Ton texte ici - 150-200 mots]

**Exemple concret 1 :**
[...]

**Exemple concret 2 :**
[...]

**Comment noter une exception :**
[...]

---

### 💼 Ça veut dire... (Pour le PDG)

[Ton texte ici - 80-120 mots]

**Ce que vous approuvez :**
[...]

**Impact business :**
[...]

**Pourquoi maintenant :**
[...]

**Comment vous vérifierez :**
[...]

---

### 🛡️ Ça veut dire... (Pour les Responsables de Dépôt)

[Ton texte ici - 100-150 mots]

**Votre préoccupation légitime :**
[...]

**La réalité :**
[...]

**Ce que vous GARDEZ :**
[...]

**Avant vs Après :**
- **Avant (sans règle) :** [...]
- **Après (avec règle) :** [...]
```

---

## COMMENCE MAINTENANT

Génère la Section 5.1 complète avec les 3 couches "Ça veut dire..." en suivant exactement ces instructions.

**Important :** C'est un prototype. Si validé, nous appliquerons cette approche aux 13 autres sections du dossier Gedimat V3.2.
