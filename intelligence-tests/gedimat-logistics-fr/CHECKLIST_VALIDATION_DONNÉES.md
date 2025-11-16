# CHECKLIST DE VALIDATION - Données Urgence & Retards Gedimat

**Objectif:** Confirmer les estimations du diagnostic avec données réelles
**Responsable:** Angélique (data) + Finance (coûts) + IT (export historique)
**Durée estimée:** 2 semaines
**Coût:** ~5k€ (1 FTE × 10 jours)

---

## MODULE 1: AUDIT RETARDS HISTORIQUES

### Tâche 1.1 - Collecte Données

**Collecte 30-50 derniers retards (3 mois historique)**

**Données requises par incident:**

| Champ | Source | Format | Exemple |
|---|---|---|---|
| Numéro PO | ERP | Format XXX-20251101 | ERM-20250915 |
| Fournisseur | ERP | Nom | Émeris Tuiles |
| Date ARC promise | ERP/Email | JJ/MM/YYYY | 05/09/2025 |
| Date réelle dépôt reçoit | Logistique/Chauffeur | JJ/MM/YYYY | 08/09/2025 |
| Jours glissement | Calc auto | Jours | +3 |
| Dépôt destination | Adresse | Gisors / Méru / Breuil | Méru |
| Tonnage | Bon livraison | Tonnes | 15 |
| Urgence client | Vendeur/Angélique | Extrême/Haute/Standard/Flexible | Haute |
| Cause retard (classification) | Angélique enquête | Fab/Stock/Planning/Transport/Coordination/Incident | Fab |
| Impact client | Statut PO | Annulée/Réduite/Maintenue | Maintenue |
| Coût mitigation (navette urgente, pénalité) | Finance | € | 500 |

**Template Excel:** [Préparer fichier AUDIT_RETARDS.xlsx avec 50 lignes]

**Effort:** Angélique 8 heures (recherche historique, enquête fournisseurs)

---

### Tâche 1.2 - Analyse Causes Racines

**Pour chaque retard, classifier cause:**

| Cause Primaire | Définition | Questions de diagnostic |
|---|---|---|
| **FOURNISSEUR - Fabrication** | Délai fab usine dépassa promesse | "Fournisseur a-t-il confirmé date ARC avant date due?" |
| **FOURNISSEUR - Stock** | Article manquant, réappro usine | "Fournisseur avait-il stock jour commande?" |
| **FOURNISSEUR - Planning** | Oubli saisie, mauvaise plannification | "Qui a signalé, fournisseur ou Angélique?" |
| **TRANSPORT - Dispo** | Camion indisponible, en attente consolidation | "Médiafret a-t-il confirmé date enlèvement?" |
| **TRANSPORT - Route** | Optimisation multi-dépôts, détour | "Plusieurs dépôts sur même enlèvement?" |
| **TRANSPORT - Incident** | Météo, accident, embouteillage | "Cause véhicule ou externe (trafic)?" |
| **COORDINATION - Alerte** | Retard détecté tardivement | "Angélique a-t-elle détecté <48h?" |
| **COORDINATION - Conflit** | Arbitrage dépôts tardif | "Tension Méru vs Gisors sur routage?" |
| **COORDINATION - Info** | Urgence client pas transmise | "Vendeur a-t-il averti Angélique urgence?" |

**Résultat attendu:** Matrice causes % conforme estimations (Fournisseur 50%, Transport 25%, Coordination 17%, Autres 8%)

**Tolérance écart:** ±10% acceptable

**Effort:** Angélique 6 heures (enquête + classification)

---

### Tâche 1.3 - Analyse Impact Client

**Pour chaque retard, noter client reaction:**

```
Retard détecté
    │
    ├─ Client ANNULE commande
    │   ├─ Perte marchandise Gedimat = Invendu (1-5 jours stock)
    │   ├─ Perte marge commande estimée: 1,000-3,000€
    │   └─ Perte fidélité estimée: 5,000-10,000€ LTV
    │
    ├─ Client RÉDUIT commande ou REPORTE
    │   ├─ Perte partielle: 500-1,500€
    │   └─ Perte fidélité: 1,000-5,000€ LTV
    │
    └─ Client ACCEPTE (surtout si communication proactive)
        └─ Impact minimal si satisfaction maintenue
```

**Template suivi:**

| PO | Fournisseur | Retard Jours | Urgence | Client Réaction | Coût Perte Estimé |
|---|---|---|---|---|---|
| ERM-20250915 | Émeris | +3 | Haute | Accepte (appel Angélique) | 0€ |
| XXX-20251002 | Lafarge | +5 | Extrême | Annule | -2,500€ |
| YYY-20251010 | CMP | +1 | Standard | Accepte | 0€ |

**Effort:** Finance 4 heures (collect impacts, coûts)

---

## MODULE 2: SONDAGE SATISFACTION CLIENT (Pilote 30 Clients)

### Tâche 2.1 - Sélection Clients Pilote

**Critères:**
- Clients réguliers (>5 commandes 6 derniers mois)
- Mix de 3 dépôts (10 clients/dépôt)
- Mix d'urgences (extrême/haute/standard)
- Contact direct disponible (appel possible)

**Liste:** [Préparer fichier CLIENTS_PILOTE.xlsx avec contacts]

**Effort:** Angélique 2 heures

---

### Tâche 2.2 - Sondage 5 Questions (SMS/Email)

**Template Message:**

```
Bonjour [Nom],

Vous avez commandé [Produit] le [Date]. Vous avez été satisfait?

1. Satisfaction globale: ⭐ (1=pas du tout, 5=très satisfait) [Répondre avec emoji]
2. Délai livraison: ⭐ (1=trop long, 5=parfait)
3. Communication: ⭐ (1=aucune info, 5=très clair)
4. Qualité produit: ⭐ (1=décevant, 5=excellent)
5. Recommander Gedimat? ⭐ (1=non, 5=oui certain)

Commentaire libre: [Zone optionnelle]

Répondre à ce SMS ou cliquer: [Lien sondage 2 minutes]

Merci! Angélique - Gedimat Coordination
```

**Effort:** Angélique 3 heures (lancement sondage, relance)

---

### Tâche 2.3 - Analyse Résultats

**Métriques:**

- **NPS (Net Promoter Score):** % Promoteurs (note 5) - % Détracteurs (note 1-2)
  - Target: +50 (exceptionnel), 0-50 (bon), <0 (problème)

- **Satisfaction par axe:** Délai vs Communication vs Qualité → où est le plus gros impact?

- **Corrélation retard-satisfaction:** Clients ayant subi retard: satisfaction réduite de combien?

**Résultat attendu:** Identifier si communication retard améliore satisfaction (+40% si alerte vs silence)

**Effort:** Finance/Analytics 2 heures

---

## MODULE 3: ENTRETIENS FOURNISSEURS TOP-5

### Tâche 3.1 - Sélection & Planification

**Top-5 fournisseurs par:** Volume tonnage (éligible pour transport >10t)

**Template entretien téléphone:** 15-20 minutes

| Question | Objectif |
|---|---|
| "Votre délai moyen de fabrication pour tuiles/ciment/gravier?" | Baseline fiabilité |
| "Quand confirmez-vous la date de livraison pour une commande?" | Process SLA |
| "Avez-vous eu des retards durables 6 derniers mois?" | Transparence |
| "Pouvez-vous respecter délai garanti (pénalité si non)?" | Capacité engagement |
| "Quels obstacles risquent délai: stock? fab? autre?" | Anticipation |
| "Pouvez-vous livrer directement nos 3 dépôts ou passer par un seul?" | Logistics flex |

**Effort:** Angélique 5 heures (5 × 1h appel + prep + notes)

---

## MODULE 4: COÛTS RÉELS RETARDS

### Tâche 4.1 - Collecte Coûts Opérationnels

**Données collecte par Finance:**

| Poste Coût | Source | Exemple |
|---|---|---|
| Coût navette urgente (€/déplacement) | Facturation chauffeur | 200-500€ |
| Coût chauffeur temps urgente (€/heure) | Paie | 25€ grossi-charges |
| Coût capital immobilisé stock (intérêt) | Taux financement | 5% annuel → 0.014%/jour |
| Marge brute moyennes produits | Comptabilité | 20-30% |
| Pénalité client pour retard (si contractuelle) | Contrats | Si applicable |
| Coût invendu (démarque marchandise retard) | Magasins | % rebut |

**Effort:** Finance 4 heures

---

### Tâche 4.2 - Calcul Coûts Totaux Récurrents

**Formule par type retard:**

```
Si client ANNULE:
  Perte Marge = Volume Tonnes × Taux Marge Moyen × Prix €/tonne
  Perte Stock = Jours Stock × Intérêt Capital/Jour
  Perte Client LTV = Client Perdu × Commandes/An × Marge/Commande × Durée Fidélité

Si client ACCEPTE (communication proactive):
  Coût Mitigation = Navette Urgente + Heure Chauffeur
  Perte Client = 0€ (satisfaction maintenue)
```

**Résultat attendu:** Confirmer 105-200k€ impact annuel vs estimation

**Tolérance écart:** ±20% acceptable

**Effort:** Finance 6 heures

---

## MODULE 5: INDICATEURS ACTUELS BASELINE

### Tâche 5.1 - Indicateurs Logistiques

**Collecte 3 mois données:**

| Indicateur | Calcul | Baseline Actuel | Target Ambition |
|---|---|---|---|
| **Taux Service** | Livraisons à temps / Total | ? | >95% |
| **Délai Moyen** | Moyenne glissement jours | ? | <2 jours |
| **Coût Transport €/Tonne** | €Affrètement / Tonnage | ? | -15% |
| **% Retards Fournisseur** | Retards fournisseur / Total | ? | <30% |
| **% Retards Coordination** | Retards Gedimat / Total | ? | <10% |
| **Satisfaction Client NPS** | % Promoteurs - % Détracteurs | ? | >50 |
| **Commandes Perdues** | Annulations/Réductions | ? | -40% |

**Effort:** IT (exports) + Logistique (collecter) = 4 heures

---

## SYNTHÈSE VALIDATION

### Timeline d'Exécution

```
Semaine 1:
├─ Lun-Mar: Collecte retards historiques (Angélique 8h)
├─ Mer-Jeu: Analyse causes racines (Angélique 6h)
└─ Ven: Première synthèse causes %

Semaine 2:
├─ Lun: Lancement sondage 30 clients (Angélique 3h)
├─ Lun-Jeu: Entretiens fournisseurs top-5 (Angélique 5h)
├─ Mar-Jeu: Collecte coûts (Finance 10h)
└─ Ven: Synthèse résultats all modules
```

### Checkliste Validation

- [ ] **Causes retards:** % fournisseur confirme ~50%? (tolérance ±10%)
- [ ] **Causes retards:** % coordination confirme ~17%? (tolérance ±10%)
- [ ] **Impact client:** % commandes perdues sur retards = combien?
- [ ] **Satisfaction client:** NPS baseline vs clients avec retard = quel écart?
- [ ] **Coûts retards:** Total annuel estimé 105-200k€ confirmé? (tolérance ±20%)
- [ ] **Fournisseurs:** Top-5 acceptent SLA garanti + pénalités?

### Décision Post-Validation

**Si résultats confirment diagnostic (+80% des estimations dans tolérance):**
- ✅ Go plan 90 jours (gains rapides validés)
- ✅ Autoriser investissement WMS (ROI clair)
- ✅ Négocier SLA fournisseurs (impact chiffrable)

**Si résultats divergent (-30% vs estimations):**
- ⚠️ Réviser estimations
- ⚠️ Réévaluer priorité optimisation
- ⚠️ Peut-être retards moins critiques que prévu

---

## RESPONSABILITÉS

| Tâche | Owner | Effort | Délai |
|---|---|---|---|
| Collecte retards + causes | Angélique | 14h | Semaine 1 |
| Sondage clients 30 pilotes | Angélique | 3h | Semaine 1-2 |
| Entretiens fournisseurs | Angélique | 5h | Semaine 2 |
| Coûts opérationnels | Finance | 10h | Semaine 2 |
| Exports IT historique | IT | 2h | Semaine 1 |
| Synthèse résultats | PDG/Angélique | 2h | Fin semaine 2 |
| **TOTAL** | | **36h** | **2 semaines** |

---

## RESSOURCES NÉCESSAIRES

- **Accès ERP** (Angélique): Historique PO, dates ARC, status livraison
- **Accès Finance:** Coûts transport, marges produits, intérêts financiers
- **Accès Logistique:** Dates réelles dépôt, coûts navettes, tonnages
- **Accès Clients:** Contacts directs pour sondage (SMS/email)
- **Excel + sondage web** (Google Forms libre)

---

**Responsable exécution validation:** Angélique
**Date de délivrance prévue:** Date + 14 jours
**Validation par:** PDG + Finance

