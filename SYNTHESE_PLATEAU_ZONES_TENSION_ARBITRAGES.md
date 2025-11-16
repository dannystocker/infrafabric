# SYNTHÈSE PLATEAU - ZONES DE TENSION
## Arbitrages Nécessaires - Passes 1-4
**Date :** Novembre 2025
**Périmètre :** Gedimat Logistics Optimization
**Statut :** Document de résolution interne

---

## CONTEXTE STRATÉGIQUE

Les quatre passes d'analyse (Competitive, Friction Angélique, Pragmatique Emeris, Juridique Franchises) ont identifié **5 zones de tension structurelles** qui créent des blocages décisionnels et des coûts cachés. Ces tensions opposent deux logiques valides mais incompatibles : optimisation opérationnelle vs satisfaction client, court terme vs scalabilité, automatisation vs expertise humaine.

**Enjeu critique** : Non-résolution = fragmentation logistique, surcoûts 15-20%, attrition clients 5-8% annuel.

---

## ZONE 1 : VOLUME vs PROXIMITÉ vs URGENCE

### Description de la tension

**Cas d'étude** : Emeris Tuiles (Pass 3 - Pragmatique)
- **Dépôt Méru** : 15 tonnes, livraison standard
- **Dépôt Gisors** : 5 tonnes, **chantier urgent (démarre lundi, besoin samedi)**
- **Logique volume** : Méru reçoit livraison directe (80km) → Gisors reporté J+2 via hub
- **Logique urgence** : Gisors reçoit priorité (30km) → Méru via navette (50km supplémentaires)

### Nature du conflit

| Critère | Logique Volume | Logique Urgence | Impact opérationnel |
|---------|---|---|---|
| **Coût transport direct** | 650€ (Méru direct) | 133€ + 25€ = 158€ (Gisors + navette) | **Économie 490€** |
| **Coût perte client** | 12 400€ (Gisors annule) | 0€ (client satisfait) | **Surcoût 12 400€** |
| **Coût total réel** | **13 400€** | **158€** | **Ratio 85:1** |
| **Priorité dépôt** | Haut volume facture | Urgence client | Conflit structurel |

**Scoring proposé** (Pass 3) : 40% urgence, 30% coût, 20% volume, 10% proximité
- Tension interne : poids urgence (40%) vs poids volume (20%) → **Résistance responsable Méru ?**

### Impacts si non-résolu

1. **Coût caché** : Décisions empiriques d'Angélique → 15-20% surcoûts non documentés
2. **Insatisfaction client** : 5-8% des urgences déçues → attrition 2-3% LTV client
3. **Conflit inter-dépôts** : « Toujours nous qui n'avons pas priorité » → baisse engagement équipes
4. **Absence métrique** : Pas de KPI pour mesurer optimisation → impossible ajustement

### Propositions d'arbitrage

#### Option A : Terrain validation (Recommandée)
- **Étape 1** : Validation empirique sur 20 cas représatifs (3-4 semaines)
  - 5 cas "volume > urgence" (Méru pattern)
  - 5 cas "urgence > volume" (Gisors pattern)
  - 10 cas mixtes (volume moyen, urgence variable)
- **Étape 2** : Mesure réelle coûts transport + coûts client (pénalités, annulations)
- **Étape 3** : Ajustement pondérations scoring si écarts > 15%

#### Option B : Directive centrale immédiate
- **Règle simple** : Urgence client ≥8/10 = priorité absolue, coût transport secondaire
- **Justification** : Données Pass 3 montrent **ratio coût 85:1** → économies logiques acceptent surcoût
- **Implémentation** : Scoring figé 40% urgence, 30% coût, 20% volume, 10% proximité dès J+1

#### Option C : Approche graduelle
- **Phase 1** (J0-J14) : Test Option B sur 10 cas Gisors urgence
- **Phase 2** (J14-J21) : Évaluation satisfait/coûts → ajustement règle si nécessaire
- **Phase 3** (J21+) : Généralisation à tous dépôts

**Recommandation** : **Option C** (test rapide + validation coûts avant généralisation)

---

## ZONE 2 : COÛT TRANSPORT vs SATISFACTION CLIENT

### Description de la tension

**Arbitrage financier classique** : Économie 50-100€ transport vs perte client 500-2000€/jour

### Données quantifiées

| Scénario | Coût transport réel | Perte client estimée | Seuil rentabilité |
|----------|---|---|---|
| **Gisors urgent non satisfait** | 158€ (hub interne) | 12 400€ (médiane 7j retard) | Surcoûts +7 800% justifiés |
| **Méru livraison directe** | 650€ | 0€ | Rentable si LTV > 650€ |
| **Benchmark GSB** | 100-200€/livraison | 300-800€ par client perdu | LTV client = 1 500-3 000€ |

**Seuil acceptable identifié** (Pass 3) : +20% surcoûts transport tolérables si urgence >8/10

### Nature du conflit

- **Direction Finance** : Minimiser coûts variables, KPI rentabilité transport
- **Direction Commerciale** : Maximiser satisfaction, KPI rétention client, LTV
- **Réalité terrain** : Urgence 9/10 = client prêt à payer +20% → profit client > profit transport

### Impacts si non-résolu

1. **Optimisation locale sous-optimale** : Économie 50€ transport → perte 1 000€ marge client
2. **Attrition invisible** : Client ne revient pas → impact LTV 5 ans -15 000€ non visible finance
3. **Conflictualité inter-directions** : Finance refuse surcoûts → ventes annulent commandes
4. **Absence convergence métrique** : ROI transport ≠ ROI commercial

### Propositions d'arbitrage

#### Option A : Accepter surcoûts priorité
- **Règle** : Si urgence >8/10 ET client LTV >5 000€ (12 mois) → accepter surcoûts +20%
- **Justification économique** : 1€ surcoûts = 100€ rétention client
- **Mesure** : Perte LTV client 5 ans / surcoûts transport annuel

#### Option B : Tarification urgence client
- **Mécanisme** : Client urgence >8/10 paie +15% surcharge urgence
- **Résultat** : Surcoûts transport absorbés par client
- **Risque** : Acceptabilité client, légalité commerciale

#### Option C : Approche LTV (Recommandée)
- **Logique** : Chaque livraison décidée par ROI client, pas par coût transport
- **Processus** :
  1. Urgence >8/10 = cas exception
  2. Vérifier LTV client 12 mois (CRM Gedimat)
  3. Si LTV >5 000€ → autoriser surcoûts +20%
  4. Si LTV <5 000€ → négo client urgence alternative
- **Mesure succès** : Taux rétention client urgence >95% vs 85% baseline

**Recommandation** : **Option C** (LTV-based, client-centered, ROI cluster)

---

## ZONE 3 : AUTOMATISATION vs RELATIONNEL HUMAIN

### Description de la tension

**Pôles opposés** (Passes 2 + 4) :
- **Alertes ARC automatisées** : Systèmes scoring multicritère, dashboards temps réel
- **Expertise Angélique** : 4 ans expérience, jugement relationnel, négociation nuancée

### Nature du conflit

| Dimension | Automatisation | Relationnel Humain |
|-----------|---|---|
| **Vitesse décision** | <5 min | 30 min (coordination) |
| **Cas d'exception** | Non géré | Résolu négociation |
| **Traçabilité** | 100% | 20% (notes manuelles) |
| **Coût** | 1 500€/an SaaS | 4 × 35k = 140k/an |
| **Risque déshumanisation** | Élevé (clients anonymes) | Zéro (expert relationnel) |
| **Scalabilité** | Exponentielle | Linéaire |

**Citation Angélique** (Pass 2) : *« Notre logiciel est bien mais pas assez détaillé pour vraiment mettre des statistiques. Pas de suivi satisfaction, pas de scoring relationnel. »*

**Réalité observée** : 60% des arbitrages Angélique ignorent scoring standard → besoin jugement contextuel

### Impacts si non-résolu

1. **Automatisation pure** : Cas exception mal gérés, clients sentent décision « robot »
2. **Humain seul** : Pas d'alertes, surcharges Angélique, décisions oubliées, non scalable
3. **Cohabitation désordonnée** : Alertes auto confuse par humanité → frustration équipe
4. **Perte intelligence relationnel** : Départ Angélique = perte 4 ans expertise

### Propositions d'arbitrage

#### Option A : Voie du Milieu (Buddha Path) - **RECOMMANDÉE**
- **Logique** : Automatiser détection, conserver jugement final humain
- **Architecture** :
  - **Tier 1 (Automatisé)** : Alertes ARC retard, scoring multicritère (40% urgence, 30% coût, 20% volume, 10% proximité)
  - **Tier 2 (Humain)** : Angélique examine cas urgence >8/10 ou anomalies scoring
  - **Tier 3 (Décision)** : Angélique + responsable dépôt arbitrage final (5 min conversation)
- **Outils** : Système alerte + dashboard + CRM relationnel (500€/an add-on)
- **Résultat** :
  - Vitesse 5-10 min (amélioration 3-6x vs 30 min)
  - Traçabilité 100% (tous arbitrages enregistrés)
  - Scalabilité 80% (seules exceptions humaines)
  - Expertise Angélique dévalorisée 0% (reste « dernier mot »)

#### Option B : Automatisation agressive
- **Règle** : Scoring figé, exceptions rares, utiliser IA prédictif
- **Risque** : Perte relationnel, clients se sentent dépersonnalisés
- **Coût** : 1 500€/an SaaS TMS

#### Option C : Humain centralisé
- **Règle** : Angélique reste seul arbitre, outils support seulement
- **Risque** : Non-scalable, surcharge workload, goulot étranglement

**Recommandation** : **Option A** - Voie du milieu
- Implémentation rapide (2-3 semaines)
- Coût modéré (500€/an)
- Préserve Angélique comme expert, la libère des cas routiniers
- Traçabilité complète pour futur ML/amélioration

---

## ZONE 4 : COURT TERME vs LONG TERME

### Description de la tension

**Quick Wins Excel vs Scalabilité Stratégique** (Pass 4 - Financière)

### Données chiffrées

| Approche | Investissement | ROI 12 mois | Scalabilité | Viabilité 3 ans |
|----------|---|---|---|---|
| **Phase 1 : Excel automation** | 0€ (ressource interne) | 304% (coûts transport -23 000€) | Non (<15 sites max) | Limitée (manuel) |
| **Phase 2 : TMS SaaS** | 8 000€ (licence + data) | 264% (optimisation +20 000€) | Illimitée | Excellente (automatisé) |
| **Combiné (Phase 1→2)** | 8 000€ (1 an délai) | 304% → 264% (décroissance progressive) | Excellent (transition douce) | Excellent (consolidation) |

### Nature du conflit

- **Pression Q1** : Résultats trimestriels, ROI 304% Excel visible immédiatement
- **Vision 2026** : 25 sites Gedimat = Excel non-scalable, besoin TMS centralisé
- **Arbitrage financier** : 12 mois gain Excel vs 3 ans gain TMS

### Impacts si non-résolu

1. **Excel seul** : Gains courts termes 12 mois, puis plateau non-scalable
2. **TMS immédiat** : Surcoûts 8k€ Q1, ROI moins impressionnant immédiatement
3. **Alternance décisions** : Politique + ROI court terme vs stratégie → confusion équipe

### Propositions d'arbitrages

#### Option A : Approche échelonnée (Recommandée)
- **Phase 1 (Mois 1-4)** : Excel automation, ROI 304%, focus Quick Wins
  - Objectif : Activer gains transport immédiatement (23 000€)
  - Budget : 0€ (ressource interne Angélique 10h/semaine)
  - Métrique : Réduction coûts transport, stabilité arbitrage
- **Phase 2 (Mois 5-12)** : Paralléliser TMS pilote
  - Test TMS sur 3-5 sites (Gisors, Méru, Paris)
  - Budget : 3 000€ (pilote SaaS 50%)
  - Parallélisation Excel (pas remplacement)
- **Phase 3 (Mois 13-36)** : Migration Progressive TMS
  - Généraliser sites > 10 enlèvements/mois à TMS
  - Excel résiduel sites faible volume
  - Budget : 5 000€ (licence complète)
- **ROI cumulé** : 304% (Excel) + 120% (TMS mois 13-36) = gains composés

#### Option B : Quick Wins Excel (short term)
- Focus Q1 résultats
- Risque : Non-scalable, revient à manual après 12 mois

#### Option C : TMS immédiat (long term)
- Focus vision 2026
- Risque : Surcoûts Q1, ROI moins visible immédiatement

**Recommandation** : **Option A** - Approche échelonnée
- Justifie Q1 résultats (304% Excel)
- Construit base TMS sans rupture
- Minimal risque opérationnel (Excel parallèle)
- Permet changement management progressif

---

## ZONE 5 : AUTONOMIE FRANCHISÉS vs DIRECTIVES CENTRALES

### Description de la tension

**Cadre juridique et opérationnel** (Pass 4 - Juridique)

### Nature du conflit

| Dimension | Autonomie franchisé | Directive centrale |
|-----------|---|---|
| **Référence légale** | Loi Doubin - autonomie opérationnelle locale | Contrat franchise - standards Gedimat national |
| **Cas exemple** | Franchise Méru livre direct (décision locale, +300€) | Client urgent Gisors = directive livrer via hub (délai respecté) |
| **Juridiquement** | Franchisé autonome gestion logistique locale ✓ | MAIS doit respecter délai client Gedimat (<48h) ✓✓ |
| **Conséquence** | Si délai respecté → autonomie prime | Si délai violé → directive centrale prime |

**Citation juridique** (Pass 4) : *« Franchisé DOIT respecter standards Gedimat (obligation contrat franchise) - Critère de conformité »*

### Impacts si non-résolu

1. **Fragmentation logistique** : Chaque franchise applique règles différentes → surcoûts 10-15%
2. **Inconsistance client** : Service différent selon franchise → marque dégradée
3. **Conflits contractuels** : Franchise refuse directive → risque remise en cause franchise
4. **Absence escalade** : Quand franchisé conteste directive → pas de process résolution

### Propositions d'arbitrage

#### Option A : Directive conditionnelle (Recommandée)
- **Règle simple** :
  1. **Urgence client ≥8/10** = directive centrale absolue (primauté délai client)
  2. **Urgence client <8/10** = autonomie franchisé (optimisation coûts locale)
- **Justification légale** : Standards Gedimat incluent « délai <48h », donc urgence >8/10 = obligation directive
- **Processus** :
  - Alertes auto détectent urgence >8/10
  - Si oui → directive centralisée (Méru doit utiliser hub Gisors même si -300€)
  - Si non → franchisé autonome (peut optimiser coûts)
- **Implémentation** : Formaliser dans contrats franchisé (1 mois révision juridique)

#### Option B : Autonomie maximale
- Franchisé décide priorité urgence vs coûts
- Risque : Non-conformité standards Gedimat → marque dégradée

#### Option C : Centralisation totale
- Head office Gedimat décide tous arbitrages logistiques
- Risque : Perte avantage franchisé (autonomie locale), attrition franchisés

**Recommandation** : **Option A** - Directive urgence >8/10
- Juridiquement conforme (standards <48h Gedimat)
- Économiquement justifié (ratio coûts 85:1)
- Préserve autonomie franchisé dans 85% cas
- Formalisation contractuelle claire (réduit conflits)

---

## SYNTHÈSE DES ARBITRAGES

| Zone tension | Option recommandée | Délai implémentation | Coût | KPI succès |
|---|---|---|---|---|
| **1. Volume vs Urgence** | Option C : Test terrain 20 cas | 3-4 semaines | 500€ | Scoring validé terrain, écarts <15% |
| **2. Coût vs Client** | Option C : Approche LTV | 2 semaines (CRM) | 200€ | Taux rétention client urgence >95% |
| **3. Auto vs Humain** | Option A : Voie du milieu | 2-3 semaines | 500€/an | Temps arbitrage <10 min, traçabilité 100% |
| **4. Court vs Long terme** | Option A : Approche échelonnée | 36 mois phased | 8 000€ (TMS mois 13) | ROI cumulé 304% + scalabilité 2026 |
| **5. Franchisé vs Central** | Option A : Directive urgence >8/10 | 4 semaines (révision contrats) | 1 000€ (juridique) | Conformité 100%, conflits franchisés -80% |

---

## RISQUES ET CONTINGENCES

### Risque 1 : Résistance franchisés (Zone 5)
- **Scénario** : Franchise Méru refuse directive urgence
- **Mitigation** : Clarifier légalement obligation (contrat franchise existant) + négociation commerciale compensation

### Risque 2 : Angélique surchargée (Zone 3)
- **Scénario** : Augmentation cas exception → surcharge humain
- **Mitigation** : Monitoring charge travail, ajustement Tier 1 alertes si >40% cas excédentaires

### Risque 3 : Scoring multicritère rejeté terrain (Zone 1)
- **Scénario** : Validation 20 cas montre scoring inadapté
- **Mitigation** : Itération rapide, consultation dépôts, révision pondération mois 2-3

### Risque 4 : Clients refusent surcoûts (Zone 2)
- **Scénario** : Client urgence refuse +15% option B
- **Mitigation** : Inclure dans contrats, clarifier urgence vs standard, communication proactive

---

## PROCHAINES ÉTAPES

**Semaine 1 (Déc 2-6)** :
- [ ] Présentation synth zones tension à COMEX (1h)
- [ ] Validation arbitrages Zone 1-2-5 (urgence + LTV + franchisé)
- [ ] Lancement test terrain Zone 1 (20 cas sélection)

**Semaine 2-3 (Déc 9-20)** :
- [ ] Configuration alertes Zone 3 (voie du milieu) + formation Angélique
- [ ] Révision contrats franchises Zone 5 (juridique)
- [ ] Paramétrage CRM LTV Zone 2 (commercial)

**Mois 2 (Janvier)** :
- [ ] Résultats test terrain Zone 1 → ajustement scoring
- [ ] Parallélisation Excel + TMS pilote Zone 4
- [ ] Mesure KPI tous zones (baseline établissement)

---

## CONCLUSION

**Les 5 zones de tension ne sont pas des défaillances, mais des **contradictions structurelles** de toute organisation logistique complexe.**

La résolution proposée (options A/C/A/A/A) repose sur **trois principes**:

1. **Pragmatisme empirique** : Data (Emeris 85:1 ratio) > théorie (volume prime)
2. **Voie du milieu** : Auto + humain (pas dichotomie), court + long terme (pas dilemme)
3. **Client-centrée** : Urgence et LTV client = critères décision, pas administratifs

**Risque non-décision** : Maintien status quo = +15-20% surcoûts, -5-8% attrition, fragmentation croissante.

**Implémentation proposée = 8 semaines, 10 000€, ROI 304% + scalabilité 2026.**

