# AIDE À LA DÉCISION RAPIDE - Choix Mode Transport & Dépôt

**Utilisateur :** Logistique opérationnelle Gedimat
**Fréquence :** À chaque commande >5 tonnes
**Temps moyen :** 3-5 minutes par décision
**Gain attendu :** -30% à -75% coûts transport vs. statut quo

---

## OUTIL 1 : Questionnaire de Décision (3 min)

Remplir les informations de commande, répondre OUI/NON aux questions, aller au résultat.

### Bloc A : DONNÉES COMMANDE

```
Commande N° : ________________  Date : ________________
Fournisseur région : ________________________  Tonnage : _____ t
Dépôt destinataire PRINCIPAL : ________________  Distance : _____ km
Délai client demandé : ☐ J+1 urgent  ☐ J+2 std  ☐ J+3+ flexible
Client priorité : ☐ Très urgent (pénalités >5%) ☐ Standard ☐ Flexible
```

### Bloc B : QUESTIONS DE FILTRAGE (Répondre dans l'ordre)

#### QUESTION 1 : Distance jusqu'au dépôt destinataire
```
"Distance fournisseur → dépôt principal < 20 km ?"

☐ OUI  → ALLEZ RÉSULTAT 1 (Navette interne)
☐ NON  → CONTINUER QUESTION 2
```

#### QUESTION 2 : Volume chargement
```
"Tonnage > 14 tonnes (= >70% camion 20t)?"

☐ OUI  → Volume dense, continuez QUESTION 3
☐ NON  → Volume faible, continuez QUESTION 4
```

#### QUESTION 3 : Délai urgence (si volume > 14t)
```
"Délai client < 48 heures ?"

☐ OUI  → ALLEZ RÉSULTAT 2 (Chauffeur direct urgent)
☐ NON  → ALLEZ RÉSULTAT 3 (Chauffeur direct optimisé)
```

#### QUESTION 4 : Regroupement possible (si volume < 14t)
```
"Existe-t-il ≥ 2 autres commandes région A ou B
à livrer dans délai client + 48 heures ?"

☐ OUI  → ALLEZ RÉSULTAT 4 (Regroupement consolidé)
☐ NON  → ALLEZ RÉSULTAT 5 (Hub régional)
```

---

## OUTIL 2 : RÉSULTATS DÉCISIONNELS

### RÉSULTAT 1 - Navette Interne ✓ OPTIMAL
```
CONDITIONS RENCONTRÉES :
  • Distance < 20 km

ACTION RECOMMANDÉE :
  ➤ Utiliser navette interne 2×/semaine existante
  ➤ Ajouter en charge du trajet régulier

COÛTS ATTENDUS :
  Coût marginal : 25-50€ (pratiquement inclus)
  Coût/tonne : 1-3€/t
  Délai : J+0 à J+1

DÉLÉGUÉ À : Responsable logistique interne

TAUX DE SERVICE : 99%+ (très fiable, transport interne)
```

---

### RÉSULTAT 2 - Chauffeur Direct URGENT ✓ NÉCESSAIRE
```
CONDITIONS RENCONTRÉES :
  • Volume > 14t (efficacité chauffeur)
  • Délai < 48h (impossible regrouper)

ACTION RECOMMANDÉE :
  ➤ Réserver chauffeur interne immédiatement
  ➤ Si indisponible → Affrètement Médiafret en secours

COÛTS ATTENDUS :
  Chauffeur interne : 0,30€/km + 100€ fixe/trajet
  Affrètement secours : 6,50€/km (recours)
  Délai : J+1 (très rapide)

DÉLÉGUÉ À : Planning chauffeurs + Achat si secours

TAUX DE SERVICE : 100% (urgence contractuelle)
```

---

### RÉSULTAT 3 - Chauffeur Direct Optimisé ✓ BON COMPROMIS
```
CONDITIONS RENCONTRÉES :
  • Volume > 14t (efficacité chauffeur)
  • Délai ≥ 48h (flexible)

ACTION RECOMMANDÉE :
  ➤ Chauffeur interne priorité (coût -68% vs affrètement)
  ➤ Si indisponible ET volume urgent → Hub régional (Scénario B)
  ➤ Si 3+ autres commandes région → Regroupement J+2 (meilleur coût)

COÛTS ATTENDUS :
  Chauffeur interne : 150-300€ trajet (distance 50-150km)
  Coût/tonne : 10-20€/t
  Délai : J+1 à J+2

DÉLÉGUÉ À : Planning chauffeurs priorité 1, Achat secours

TAUX DE SERVICE : 98-99% (bon, délai flexible)
```

---

### RÉSULTAT 4 - Regroupement Consolidé ★ OPTIMAL (ÉCONOMIE -40% À -75%)
```
CONDITIONS RENCONTRÉES :
  • Volume < 14t (petites commandes)
  • ≥ 2 autres commandes région délai compatible
  • Délai client ≥ 48h (permet consolidation)

ACTION RECOMMANDÉE :
  ➤ REGROUPER avec autres commandes en tournée unique
  ➤ Optimiser itinéraire : réduire distance totale
  ➤ Planifier livraison J+2 ou J+3

EXEMPLE CAS ÉMERGE 20t RÉEL :
  - Commande Émerge (15t Méru + 5t Gisors)
  - Regroupée avec BigMat (10t Versailles) + Leroy M. (8t Montsouris)
  - Total 38t, tournée 150km, 2 trajets
  - Coût Émerge seul : 1000€ (affrètement direct)
  - Coût Émerge groupé : 261€ (-74%)

COÛTS ATTENDUS :
  Coût direct groupé : 150-300€/commande (selon taille tournée)
  Coût/tonne : 6-10€/t
  Délai : J+2 à J+3 acceptable

DÉLÉGUÉ À : Planification logistique 48h avant livraison

TAUX DE SERVICE : 97-98% (bon, exige coordination)

BÉNÉFICE SYSTÉMIQUE :
  • Chauffeur 1 trajet multi-clients = rentabilité max
  • Carburant partagé = -20% coûts km
  • Manutention regroupée = efficacité opér.
```

---

### RÉSULTAT 5 - Hub Régional ★★ EXCELLENT COMPROMIS (-70%)
```
CONDITIONS RENCONTRÉES :
  • Volume < 14t (petit chargement)
  • Impossibilité regroupement (R < 2 ou délai serré)
  • Délai ≥ 48h possible

ACTION RECOMMANDÉE :
  ➤ Livrer au HUB RÉGIONAL proche client
  ➤ Transbordement interne
  ➤ Navette redistribution client final J+1 ou J+2

HUBS RÉGIONAUX DISPONIBLES GEDIMAT :
  • Gisors (Île-de-France nord)  → Clients Évreux, Beauvais
  • Montsouris (Paris centre)    → Clients Paris, petite couronne
  • Lyon (Southeast hub)         → Clients Rhône-Alpes
  • Bordeaux (Southwest)         → Clients Aquitaine

EXAMPLE CAS ÉMERGE (Hub Gisors) :
  Trajet 1 : Fournisseur → Gisors (30km, 20t plein) = 133€
  Transbordement Gisors : 35€
  Stockage 12h : 20€
  Navette Gisors → Méru (50km, 15t) : 25€
  ────────────────────────────────
  TOTAL 213€ vs 1000€ direct (-78,7%)

COÛTS ATTENDUS :
  Trajet hub : 100-200€
  Transbordement : 20-40€
  Stockage 12-24h : 15-25€
  Navette redistrib. : 20-50€
  Coût/tonne global : 10-15€/t
  Délai : J+2 (1 jour transbordement)

DÉLÉGUÉ À : Logistique interne + Hub régional

TAUX DE SERVICE : 98-99% (excellent, moins d'intervenants externes)

⚠️ ATTENTION :
  Risque : Perte traçabilité si transbordement mal géré
  Mitigation : Code-barres + alerte passage hub
```

---

## OUTIL 3 : Synthèse Comparatif Rapide

| **Mode/Dépôt** | **Cas d'usage** | **Coût** | **Délai** | **Service** | **Choix opér.** |
|---|---|---|---|---|---|
| **Navette interne** | <20km, regroupé | ✓✓✓ 1-3€/t | J+0-1 | 99% | 1️⃣ **PRIORITÉ** |
| **Chauffeur direct** | >14t, urgence | ✓✓ 10-30€/t | J+1-2 | 100% | 2️⃣ **URGENT** |
| **Regroupement** | <14t, flexibilité | ✓✓✓ 6-10€/t | J+2-3 | 97% | 3️⃣ **OPTIMAL** |
| **Hub régional** | <14t, urgence+48h | ✓✓✓ 10-15€/t | J+2 | 99% | 4️⃣ **BON COMPRO** |
| **Affrètement direct** | ✗ À ÉVITER | ✗ 40-70€/t | J+2 | 100% | 🚫 **DERNIER** |

---

## OUTIL 4 : Checklist Prise de Décision

À remplir pour chaque commande >5 tonnes au moment réception MDL.

```
═══════════════════════════════════════════════════════════════
CHECKLIST DÉCISION DÉPÔT & MODE TRANSPORT
═══════════════════════════════════════════════════════════════

Commande : _________________________    Date : ___/___/_____

─── DONNÉES DE BASE ───
☐ Tonnage entré système : _____ t
☐ Fournisseur identifié : _________________
☐ Dépôt(s) destinataire(s) : _________________
☐ Distance fournisseur → principal : _____ km
☐ Délai client contractuel : _______ J+?

─── FILTRAGE RAPIDE ───
Distance < 20 km ?
☐ OUI → NAVETTE INTERNE (FIN, aller section signatures)
☐ NON → Continuer

Volume > 14 tonnes ?
☐ OUI → Aller QUESTION 3
☐ NON → Aller QUESTION 4

─── QUESTION 3 (Volume >14t) ───
Délai < 48h ?
☐ OUI  → CHAUFFEUR DIRECT URGENT (RÉSULTAT 2)
☐ NON  → CHAUFFEUR DIRECT OPTIMISÉ (RÉSULTAT 3)

─── QUESTION 4 (Volume <14t) ───
Regroupement possible (≥2 autres CMD région) ?
☐ OUI  → REGROUPEMENT CONSOLIDÉ (RÉSULTAT 4)
☐ NON  → HUB RÉGIONAL (RÉSULTAT 5)

─── COÛTS & DÉBLOCAGE ───
Mode transport choisi : _____________________________
Coût estimé : ________€  Coûts/tonne : _______€/t
Délai prévisional : J+_____  Taux service : ______%

─── INSTRUCTIONS OPÉRATIONNELLES ───
Actionneur principal : _________________________
Date limite action : _____/_____/_____
Hub/Dépôt intermédiaire si applicable : _________________________
Alerte/Notes spéciales : _________________________________

─── SIGNATAIRES ───
Responsable logistique : ________________  Date : ___/___/_____
Directeur d'exploitation approuve : ________  Date : ___/___/_____

═══════════════════════════════════════════════════════════════
```

---

## OUTIL 5 : Formule de Coût Rapide (Calcul <1 min)

Pour estimation coûts avant décision final :

### A. Formule Navette (si applicable)
```
COÛT NAVETTE = Fixe 25€ + (Distance km × 0,50€/km) ÷ Tonnage

Exemple 30km, 20t : (25 + 15) ÷ 20 = 2€/t ✓
```

### B. Formule Chauffeur Direct
```
COÛT CHAUFFEUR = (100€ fixe + Distance km × 0,30€/km + Manutention 24€) ÷ Tonnage

Exemple 80km, 15t : (100 + 24 + 24) ÷ 15 = 9,87€/t ✓
```

### C. Formule Affrètement Médiafret (RÉFÉRENCE)
```
COÛT AFFRÈTEMENT = Distance km × 6,50€/km ÷ Tonnage

Exemple 80km, 15t : (520) ÷ 15 = 34,67€/t ✗ CHER
Exemple 30km, 5t petit volume : ajouter surcharge +50% = 195€ ÷ 5 = 39€/t ✗ TRÈS CHER
```

### D. Formule Hub Régional (APPROXIMATION)
```
COÛT HUB = (Trajet vers hub + Transbordement 35€ + Navette retour) ÷ Tonnage

Exemple Gisors (30km hub + 50km navette Méru, 20t, 5t resto) :
  Trajet hub : 133€ ÷ 20 = 6,65€/t
  Opérations : 55€ ÷ 20 = 2,75€/t
  Navette : 25€ ÷ 15 = 1,67€/t (chargement 15t seulement)
  ─────────────────────────
  TOTAL : 10,65€/t ✓ TRÈS BIEN
```

### E. Formule Regroupement (APPROXIMATION)
```
COÛT GROUPÉ = (Distance totale tournée km × 0,30€/km + 50€ manutention mult.) ÷ Tonnage total

Puis allouer proportionnellement à chaque commande.

Exemple 4 commandes, 38t total, 150km tournée :
  Coût total : (45€ carburant + 200€ chauffeur fixe + 50€ manut.) ÷ 38 = 7,76€/t moyen
  Émerge 20t (50%) = 7,76€/t × allocation volume = ~6,87€/t ✓ EXCELLENT
```

---

## OUTIL 6 : Tableau Seuils Décision Rapide (AIDE-MÉMOIRE POCHE)

Plastifier et garder à disposition planning/achat.

```
╔════════════════════════════════════════════════════════════════╗
║           SEUILS DÉCISION TRANSPORT GEDIMAT 2025              ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  DISTANCE   VOLUME   DÉLAI   AUTRES CMD   → CHOIX             ║
║  ─────────────────────────────────────────────────────────────║
║                                                                ║
║  <20km      any      any     -           → NAVETTE (1-3€/t)   ║
║  >20km      >14t     <48h    any         → CHAUFFEUR (10€/t)  ║
║  >20km      >14t     ≥48h    any         → CHAUFFEUR (12€/t)  ║
║  >20km      <14t     any     ≥2          → REGROUPEMENT (7€/t)║
║  >20km      <14t     ≥48h    <2          → HUB (11€/t)        ║
║  >20km      <14t     <48h    any         → AFFRÈTEMENT (40€/t)║
║                                                                ║
║  SYMBOLE : € estimé, chiffres arrondis. Calculer précis cas.  ║
║  COÛTS DE RÉFÉRENCE (2025) :                                   ║
║    • Navette interne : 0,50€/km marginal                      ║
║    • Chauffeur interne : 0,30€/km + 100€/trajet              ║
║    • Affrètement ext. : 6,50€/km (NE PAS UTILISER sauf force)║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

## OUTIL 7 : Exemple Pas-à-Pas - Cas Réel Émerge

**Commande Émerge tuiles 20t (réelle nov 2025)**

### Étape 1 : Remplir données
```
Tonnage : 20 tonnes ✓
Fournisseur région : Normandie (région Évreux)
Dépôt principal : Méru (80km)
Dépôt secondaire : Gisors (30km)
Délai client : J+3 flexible
Urgence : Standard (pas de pénalité)
```

### Étape 2 : Appliquer filtres
```
Distance < 20km ?
  NON (80km Méru) → Continuer

Volume > 14 tonnes ?
  OUI (20 tonnes) → Aller QUESTION 3
```

### Étape 3 : Question 3
```
Délai < 48h ?
  NON (J+3 flexible) → RÉSULTAT 3 (Chauffeur optimisé)

Mais ATTENDRE QUESTION 4 :
  Autres commandes région ?
  OUI (BigMat 10t + Leroy M. 8t) = 2 autres clients
  → PASSE À RÉSULTAT 4 (Regroupement prioritaire !)
```

### Étape 4 : Décision final & Coûts
```
SÉLECTION : RÉSULTAT 4 - REGROUPEMENT CONSOLIDÉ

Tournée optimisée :
  • Fournisseur → Gisors (5t Émerge)
  • Gisors → Paris Montsouris (8t Leroy M.)
  • Montsouris → Versailles (10t BigMat)
  • Versailles → Méru (15t Émerge)

Coûts :
  • Chauffeur 2 trajets : 200€
  • Carburant 150km : 45€
  • Manutention 4 sites : 50€
  ────────────
  TOTAL : 295€

Coût/tonne ÉMERGE : 261€ ÷ 20t = 13,05€/t
(Allocation équitable du trajet multi-clients)

ÉCONOMIE vs Affrètement direct :
  Direct affrètement : 1000€
  Groupé : 261€
  GAIN : 739€ (-74%)

Délai : J+2 à J+3 (acceptable flexible)
Taux service : 98% (regroupement = coordination)
```

### Étape 5 : Signature & Déploiement
```
Responsable logistique : Planifier tournée avant J-2
Actionneur : Planning chauffeurs + coordonner 3 autres clients
Alert deadline : 48h avant départ
Monitoring : Traçabilité GPS, vérifier délais clients
```

---

## OUTIL 8 : FAQ Objections Opérationnelles

### Q1 : "Le hub ajoute un jour de délai, client n'acceptera pas !"
**R :** Vrai pour client urgentissime (<48h). Pour J+2-3, hub = même délai que direct et **coûte 70% moins cher**. Proposer client "livraison J+2 -10% prix" instead de J+1 affr.

### Q2 : "Regroupement demande coordination, c'est complexe !"
**R :** Vraiment ? Voir planification 2×/semaine existante + 48h anticipation = **faisable 80% cas**. Logiciel planning peut automatiser. ROI = -40% coûts transport > efforts coordination.

### Q3 : "Et si fournisseur ne peut pas attendre regroupement ?"
**R :** Déclencher livraison standard (résultat 2 ou 5). Pas perdu. Mais si client flexible, TOUJOURS tester regroupement **avant** affrètement direct.

### Q4 : "Chauffeur interne saturé, pas dispo pour direkt !"
**R :** Ceci est root-cause Gedimat. Intérim ou recruter chauffeur 3. Payback = 18 mois sur volume. Décision RH, pas logistique.

### Q5 : "Le calcul coûts navette 0,50€/km semble très bas !"
**R :** C'est **coût marginal**, pas coût complet. Navette 2×/semaine roulée de toute façon (salaire chauffeur = fixe). Ajouter cargo = 0,50€ km carburant supplémentaire. Correct.

---

## OUTIL 9 : Monitoring Impact - KPIs Mensuels

Chaque mois, suivre :

```
╔══════════════════════════════════════════════════════════════╗
║              KPI TRANSPORT GEDIMAT (Mensuel)                ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ Indicateur              │ Target    │ Réel    │ Variance     ║
║ ─────────────────────────┼───────────┼─────────┼──────────    ║
║ % Navette (< 20km)      │ 20%       │ ___%    │              ║
║ % Chauffeur direct      │ 35%       │ ___%    │              ║
║ % Regroupement          │ 30%       │ ___%    │ ← CROÎTRE    ║
║ % Hub régional          │ 10%       │ ___%    │ ← CROÎTRE    ║
║ % Affrètement           │ 5% max    │ ___%    │ ← RÉDUIRE    ║
║ ─────────────────────────────────────────────────────────── ║
║ Coût moyen transport/t  │ 15€/t     │ __€/t  │              ║
║ (vs statut quo 50€/t)                                        ║
║                                                              ║
║ Délai service (% J+2)   │ 85%       │ ___%    │              ║
║ Rupture stocks          │ <2%       │ ___%    │              ║
║ Satisfaction client     │ 4,5/5     │ ___/5   │              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Cibles début année 1 :**
- Réduire affrètement 30% → 5% commandes
- Augmenter regroupement 5% → 30% commandes
- Coût moyen : 50€/t → 18€/t (-64%)
- Payback : 6-9 mois

---

## CONCLUSION - UTILISATION QUOTIDIENNE

**Cette aide à la décision s'utilise :**

1. **À la réception MDL** (commande > 5 tonnes)
2. **Avec 3-5 minutes d'analyse** (questionnaire + formule)
3. **Signée par logistique et achat** (tracabilité)
4. **Montée en système** (ERP/WMS intégration cible)

**Résultat attendu :**
- Moins d'intuitions ("proximité = moins cher")
- Plus de calculs empiriques ("vraiment moins cher ?")
- Économies mesurées : -40% à -75% cas applicables

---

**Document opérationnel Gedimat – Décision transport quotidienne**
*Version 1.0 – Novembre 2025*
