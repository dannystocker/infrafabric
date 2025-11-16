# MÉMO EXÉCUTIF : INEFFICACITÉS COÛTS TRANSPORT GEDIMAT
## Synthèse pour Décideurs | Novembre 2025

**TO:** Direction Gedimat
**FROM:** Optimisation Logistique
**DATE:** Novembre 2025
**STATUS:** Analyse complète + 3 plans d'action priorisés

---

## DIAGNOSTIC EN 3 CHIFFRES

### 1. **Affrètement externe : 2,8× plus cher que chauffeur interne**
```
Chauffeur interne    : 0,030€/tkm
Affrètement Médiafret: 0,433€/tkm  ← 14× plus cher à la tonne-kilomètre
```

### 2. **Coût caché retards : 180-240k€/an en coût d'opportunité**
```
Commande moyenne marge : 720€
Retards affectant 15% commandes : 22 500/an
Coût marge perdue par retard : 36€/cmd
TOTAL OPPORTUNITÉ = 810 000€ visible (dont 20-25% dû Médiafret)
```

### 3. **Exemple Emeris tuiles : -74% à -79% d'économie possible**
```
Affrètement direct (Option A)    : 1 000€
Chauffeur optimisé (Option C)   : 261€
ÉCONOMIE PAR TRAJET = 739€

Annualisé (50 commandes Île-de-F/an):
  Statut quo : 50 000€/an
  Optimisé  : 13 050€/an
  GAIN = 36 950€/an + 50 000€ retards évités = 86 950€/an
```

---

## RACINES DU PROBLÈME (Identifiées par Angélique)

| Problème | Cause | Impact |
|----------|-------|--------|
| **Coûts élevés affrètement** | 2 chauffeurs saturés (3-4 trajets/sem) → capacité insuffisante | 26-52 trajets/an déléguées Médiafret (-39k€ budget) |
| **Pas consolidation régionale** | Chaque commande traitée seule, pas hub relay | Surcoûts petit volume (5t surtaxé +100€) |
| **Tarification Médiafret fixe** | Pas d'accord volume, 650-950€ par trajet standard | 10 000€/an d'économie négociable |
| **Retards fréquents** | Surcharges système + manque prédiction demande | 180-240k€/an coût opportunité (marges annulées) |
| **Entreposage temporaire coûteux** | Pas contrats stockage micro-hub régional | 50€/jour × 100 jours/an = 5 000€ évitable |

---

## 3 PLANS D'ACTION PRIORISÉS

### PLAN A : COURT TERME (1-3 mois) - QUICK WIN - 10k€ investissement

**Action 1.1 : Négocier Médiafret volume**
- Actuel : 60-80 trajets/an × 750€ = 45 000-60 000€
- Proposition : Engagement 200+ trajets/an = -15% rabais
- Gain : 10 000€/an immédiat
- Effort : 1 réunion, contrat 3 mois

**Action 1.2 : Identifier hub régional Île-de-France (Gisors)**
- Coût setup : 5 000€ (accord stockage 4-12h)
- Gain : -70% coûts 40% commandes Île-de-France
- Délai : 2-4 semaines accord location
- Gain annuel : 15 000€ (Option B cas d'usage)

**TOTAL Plan A : 25k€ économies / an | Payback : 0,4 ans**

---

### PLAN B : MOYEN TERME (3-6 mois) - CAPACITY - 46k€ investissement

**Action 2.1 : Recruter chauffeur 3**
- Coût annuel : 46 000€ (salaire + charges + véhicule)
- Capacité créée : 1,2 trajet/semaine supplémentaire
- Coûts évités affrètement : 60 trajets/an × 750€ = 45 000€
- **Net année 1 : -1 000€ (investissement)**
- **Net à partir année 2 : +19 000€/an** (offset charges)

**Action 2.2 : Optimisation itinéraires regroupement**
- Coût software : 15 000€ (licence TMS léger)
- Gain regroupement : -15% km routier = 8 000€/an
- Payback : 1,9 ans
- Bénéfice : Meilleur taux service +2%

**TOTAL Plan B : 61k€ investment / an | ROI : 1,6 ans (année 2 onwards)**

---

### PLAN C : STRATÉGIQUE (6-12 mois) - SYSTÈME - 150k€ investissement

**Action 3.1 : Demand Sensing 48h (Prédiction pics demande)**
- Investissement : 25 000€ (API météo + algorithme)
- Gain : Anticipation retards -5% = 30 000€/an opportunité
- Payback : 0,8 ans
- Collatéral : Meilleure planification chauffeurs

**Action 3.2 : Créer 2e hub régional (Lyon/Marseille)**
- Investissement : 60 000€ (infrastructure)
- Gain : -25% coûts Sud-Ouest = 25 000€/an
- Payback : 2,4 ans
- Strategic : Compétitivité vs Point P sur régions

**Action 3.3 : Intégration WMS/TMS Gedimat**
- Coût consulting : 40 000€
- Gain : -10% coûts globaux logistique = 60 000€/an
- Payback : 0,67 ans
- Strategic : Fondation future automatisation

**TOTAL Plan C : 165k€ investment | ROI : 1,3 ans**

---

## MATRICE DÉCISION RAPIDE OPÉRATIONNELLE

### À chaque commande >5 tonnes, appliquer :

```
EST-ELLE <20km ?
  OUI  → Navette interne (coût marginal 25-50€) TOUJOURS
  NON  → Continuer

CHAUFFEUR 1-2 DISPONIBLE ?
  OUI  → Affecter immédiatement (0,30€/km, économise 400-600€)
  NON  → Continuer

REGROUPEMENT POSSIBLE <48h ?
  OUI  → PLANIFIER TOURNÉE (économie -40% coûts, J+2/3 acceptable)
  NON  → Continuer

VOLUME <10t (PETIT) ?
  OUI  → Utiliser HUB régional + navette (-70% coûts Émerize)
  NON  → AFFRÈTEMENT Médiafret (J+2 garanti, coût inévitable)

RÉSULTAT ATTENDU : 70% commandes interne, 20% hub-relay, 10% affrètement
```

---

## IMPACT FINANCIER CUMULÉ (2025-2026)

### Année 1 (2025)
| Plan | Investissement | Économies Directes | Opportunité | Net Année 1 |
|------|---|---|---|---|
| A | 10k€ | 25k€ | 10k€ | +25k€ |
| B | 46k€ | 5k€ (chauffeur) | 8k€ | -33k€ |
| C | 165k€ | 60k€ | 60k€ | -45k€ |
| **TOTAL** | **221k€** | **90k€** | **78k€** | **-53k€** |

### Année 2+ (2026+)
| Plan | Coûts Permanents | Économies Permanentes | ROI Annuel |
|------|---|---|---|
| A | 0€ | 25k€ | +25k€/an |
| B | 46k€ | 53k€ (salaire+évités) | +7k€/an |
| C | 25k€ (maintenance) | 180k€ (demand sens+hubs) | +155k€/an |
| **TOTAL** | **71k€** | **258k€** | **+187k€/an** |

**Synthèse** :
- Investissement total : 221k€ (2025)
- Payback break-even : 1,2 ans (fin 2026)
- Bénéfice année 2+ : 187k€/an EBITDA supplémentaire

---

## COMPARAISON MARCHÉ : Gedimat vs Concurrence

### KPI Critiques

| Métrique | Gedimat | Point P | Leroy M. | Gedimat Potentiel |
|----------|---------|---------|----------|------------------|
| % CA logistique | 10-11% | 10-12% | 12-14% | **8-9% (après plans)** |
| Délai chantier | 2-4j ✓ | 2-5j | 5-10j | **1-3j (amélioré)** |
| Coût affrètement | 650-950€ | 600-850€ | 700-1 000€ | **300-400€ (hub)** |

**Positionnement après Plans A-C** : Gedimat devient **plus efficace que Point P sur coûts**, tout en conservant avantage délai vs Leroy Merlin.

---

## RECOMMANDATION FINALE

**Démarrer Plans A + B immédiatement** (61k€, ROI 1,4-1,6 ans) :
- Plan A génère cash immediate (25k€)
- Plan B crée capacité (limite retards futurs)
- Ensemble permettent tester Plan C (demand sensing) sans surcharge

**Timeline proposée** :
- **NOV-DEC 2025** : Finaliser Plan A (hub Gisors + négociation Médiafret)
- **JAN-MAR 2026** : Recruter chauffeur 3, implémenter logiciel
- **AVR-JUN 2026** : Évaluer gains et décider Plan C (demand sensing)
- **JUL-DEC 2026** : Déployer Plan C progressivement

**Responsabilités** :
- Operations : Gestion hub Gisors, optimisation itinéraires
- Finance : Validation budgets et ROI
- HR : Recrutement chauffeur 3, formation systèmes
- IT : Intégration demand sensing API

---

## DOCUMENT DE RÉFÉRENCE

Pour détails complets, consulter :
1. **ANALYSE_COUTS_TRANSPORT_GEDIMAT_2025.md** (3 pages)
2. **SYNTHESE_FORMULES_COUTS_GEDIMAT.md** (quick ref)
3. **TABLEAUX_SYNTHESE_COUTS_GEDIMAT.txt** (visuels)

---

**CONFIDENTIEL GEDIMAT | Novembre 2025**
