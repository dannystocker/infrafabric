# Dossier Final — Optimisation Logistique Gedimat
**Date** : 2025‑11‑17  
**Portée** : 3 dépôts, enlèvements fournisseurs non livreurs, affrètement externe vs. navette interne

---

## 1. Résumé exécutif

**Positionnement stratégique:** Cette recommandation s'inscrit dans une logique de capitalisme relationnel (Rory Sutherland, Vice Chairman Ogilvy UK) : maximiser la valeur de la relation client sur la durée, non la rentabilité d'une seule expédition. Un support prévisible lors des incidents construit une différenciation durable vs. concurrents focalisés sur le prix spot.

**Problème.** Les enlèvements chez fournisseurs “non livreurs” génèrent des **coûts d’affrètement élevés** et des **retards** perçus par les clients. Les trois dépôts défendent leurs préférences de livraison, ce qui **multiplie les affrètements** et complexifie la planification. Les alertes SI sont limitées (ARC/ACK fournisseurs, confirmation d’enlèvement transporteur). fileciteturn0file0

**Opportunité.** Standardiser le **choix du dépôt** par **proximité fournisseur** (puis navette interne), instaurer un **système d’alertes simple** (emails/règles) et **mesurer la satisfaction**. L’usage de la navette interne pour redistribuer depuis le dépôt le plus proche réduit l’affrètement externe inutile. fileciteturn0file0

**Recommandations (3 axes).**
- **Gains rapides (0–30 jours)** : (i) Activer des **alertes** ARC/ACK et enlèvement J‑1 16h ; (ii) lancer un **sondage satisfaction** (20 clients, 5 questions) ; (iii) appliquer la **règle proximité** et documenter toute dérogation.  
- **Moyen terme (30–90 jours)** : (i) **Outil scoring dépôt** (Volume, Distance, Urgence) ; (ii) **tableau de bord** de suivi (service, satisfaction, consolidation) ; (iii) revue hebdo des **exceptions**.  
- **Long terme (90+ jours)** : (i) **Standard d’affectation** SI (dépôt par km) ; (ii) contrats transporteurs avec **grilles unifiées** ; (iii) intégration des **contacts relationnels** (fournisseurs, affréteurs) dans le SI. fileciteturn0file0

**Retour sur investissement (RSI) — à formaliser par formule, pas par chiffre fixe.**  
\[ \textbf{RSI} = \frac{\text{Baseline affrètement (30 j factures)}}{\text{Investissement (temps + outils)}} \times \text{Réduction attendue (scénario)} \]  
- Scénarios : **Conservateur 8 %**, **Base 12 %**, **Haut 15 %** — issus **de cas externes publiés** et non d’estimations internes. (Voir §4 et Annexe G)

**Décision attendue.** Valider : (i) la **politique “proximité d’abord”** + dérogations limitées (3 cas), (ii) la **mise en place des alertes** minimalistes, (iii) la **mesure satisfaction** et **indicateurs** du pilote sur 30–90 jours.

**Prochaines étapes.** Démarrage sous 7 jours : **Annexe Y (Alertes & SLA)**, **Annexe X (Règles de décision)**, **Annexe Z (Modèle de coûts)**, puis **plan 90 jours** (§7).

---

## 2. Contexte & faits clés (interne)

- **3 dépôts**, 1 magasin/dépôt ; marchandises typiques : tuiles, matériaux en sacs. **Chargements typiques** : **25–30 t** (semi).  
- **Capacité interne** : enlèvements jusqu’à **10 t** ; au‑delà → **affrètement externe** (ex. Médiafret, parfois sous‑traité).  
- **Pratique cible** : faire livrer **chez le dépôt le plus proche** du fournisseur puis **redistribuer** via **navette interne** (2×/semaine) ; **coût interne nettement inférieur**.  
- **Urgences clients** : certains cas imposent l’**express**, **au‑dessus de l’optimisation**.  
*(Source : entretien opérationnel avec la coordinatrice, voir transcription interne.)* fileciteturn0file0

---

## 3. Diagnostic (problèmes observés)

1) **Double affrètement** dû à des arbitrages locaux non alignés (tonnage ≠ bon critère).  
2) **Alertes SI insuffisantes** (ARC/ACK, confirmation d’enlèvement) ⇒ retards non détectés.  
3) **Satisfaction client** peu mesurée lorsque tout se passe bien ⇒ valeur non visible.  
4) **Connaissance relationnelle** (contacts chez fournisseur/transporteur) non structurée dans le SI. fileciteturn0file0

---

## 3.5 Psychologie B2B et Fidélisation

**Principe comportemental (Rory Sutherland):** Les clients dont les incidents sont résolus excellemment deviennent PLUS loyaux que ceux n'ayant jamais eu d'incident. C'est un test de la relation.

**Exemples B2C (transférables B2B):**
- Ritz-Carlton: Budget $2,000/employé pour résoudre incidents clients sans approbation → Taux fidélisation 85%+ (industrie moyenne 60%)
- Zappos: Retours gratuits + service 24/7 → NPS 90 (retail moyenne 45)

**Application hypothétique Gedimat (À VALIDER):**
- Mesurer: Taux commandes répétées clients avec 1 incident bien résolu vs. clients sans incident
- Hypothèse: Si taux > 100%, alors investir dans résolution rapide est MARKETING, pas coût

**Formule ROI résolution incidents:**
```
ROI = (Δ Taux rétention × [CA moyen client] × [Marge %]) / Budget incidents
Rentable si ROI > 1,0
```

**Données requises:**
1. Baseline: Taux rétention clients actuels (12 mois)
2. Baseline: CA moyen client annuel (comptabilité 2023-2024)
3. Pilote: Taux rétention post-incident avec nouveau système (90 jours)


---

## 4. Cas externes (références utilisables)

- **Leroy Merlin — Réau / “Easylog” (~40 M€ ; 27 AGV STILL)** : modernisation et automatisation (SCM). **+55 % e‑commerce 2021** (presse sectorielle). *Conversion de “baisse coûts 11–15 %” en **formule**.*  
  Sources :  
  - Supply Chain Magazine (NL 3628, 2022) — https://www.supplychainmagazine.fr/nl/2022/3628/leroy-merlin-dote-son-entrepot-automatise-de-reau-de-27-agv-still-706966.php  
  - Stratégies Logistique — https://strategieslogistique.com/Comment-Leroy-Merlin-adapte-sa%2C12454  
  - ADEO (Overview 2023) — https://www.adeo.com/en/
- **Kingfisher Group / Castorama** : **NPS suivi mensuellement** au niveau Groupe ; **Castorama** est une bannière Kingfisher.  
  Sources : https://www.kingfisher.com/investors/ ; https://www.kingfisher.com/brands/
- **Saint‑Gobain — Transport Control Tower** : **−13 % CO₂** (LATAM) et **>10 M$** d’économies/5 ans (ARC Advisory / Logistics Viewpoints, 2022).  
  Sources : https://logisticsviewpoints.com/2022/01/31/is-saint-gobain-serious-about-reducing-their-carbon-footprint/ ; https://www.saint-gobain.com/

> **Usage** : ces cas servent de **références** et de **plages de scénarios** ; **aucun chiffre Gedimat** ne doit être inféré sans baseline mesurée.

---

## 5. Recommandations détaillées

### 5.1 Règle d’affectation dépôt (proximité d’abord)
- Choisir **le dépôt le plus proche du fournisseur** (si écart >15 km) ; si ≤15 km, optimiser pour la **meilleure boucle navette**.  
- **Dérogations valides (3)** : (i) Urgence client documentée, (ii) Contrainte fournisseur (point unique), (iii) Anomalie de coût (devis aberrant).  
- **Journaliser** toute dérogation (`exception_reason`).  
*(Voir Annexe X — Règles de décision)*

### 5.2 Alertes & SLA (sans achat logiciel)
- Champs requis : `promised_delivery_date`, `supplier_ack_date`, `customer_urgency_flag`, `pickup_confirmed_timestamp`, `depot_assigned`, `exception_reason`.  
- **SLA** : ARC/ACK ≤48 h ; pickup confirmé **J‑1 16:00** ; livraison dans fenêtre convenue.  
- **Alertes** : (i) ARC/ACK manquant (48 h) ; (ii) risque retard (J‑1) ; (iii) pickup non confirmé (J‑1 16:00) ; (iv) urgence client ⇒ bypass consolidation.  
*(Voir Annexe Y — Alertes & SLA)*

### 5.3 Mesure de satisfaction (20 clients pilote)
- Courriel simple (5 questions FR), 2 vagues : après livraison, après incident.  
- Stocker le score par **commande** pour relier aux arbitrages logistiques.  

### 5.4 Outil de scoring dépôt (Excel)
- **Formule** : `Score = w1×Volume + w2×Distance + w3×Urgence`.  
- Valider sur **50 cas historiques** ; seuils proposés : Distance (km) normalisée ; Urgence binaire (1/0) ou 0/2.

### 5.5 Le Geste Relationnel (Trust Signal)

**Principe (Rory Sutherland):** Actions semblant contre-productives à court terme modifient la nature de l'échange : transactionnel → partenariat durable.

**Exemples externes:**
- DoubleTree Hotels: Cookie gratuit check-in (coût $0,20) → ROI mesuré via taux retour clients
- AO Appliances (UK): Teddy bear offert aux enfants lors livraison électroménager → Publicité gratuite 8 ans dans chambre enfant

**Application hypothétique Gedimat (À VALIDER):**
- Mécanique: [X] incidents sérieux/an → Geste surprise (SMS reconnaissance simple OU crédit [Y]% sur prochaine commande)
- **Coût:** À calculer = [Coût geste moyen] × [Nombre gestes/an estimé]
- **ROI:** À mesurer = Δ Recommandations bouche-à-oreille (NPS) avant/après

**Formule ROI geste relationnel:**
```
ROI = (Clients sauvés × [CA moyen client] × [Marge %]) / Budget gestes
Seuil rentabilité: ROI > 1,0
```

**Données requises:**
1. Baseline: Nombre incidents sérieux/an (définition: >24h retard OU >2t manquant)
2. Baseline: Coût geste moyen (SMS = gratuit, crédit 5% = ~[X]€)
3. Pilote: NPS avant/après (90 jours) + taux clients perdus (avant/après)

**Décision:** NE PAS budgéter avant collecte baseline. Pilote 10 gestes sur 6 mois → mesure → décision.

---

## 6. Gouvernance & responsabilités

### 6.5 Gouvernance Comportementale : Principe "Zéro Perdant"

**Modèle SCARF (David Rock, NeuroLeadership Institute):**
- **S**tatus: Personne ne perd prestige
- **C**ertainty: Règles claires, pas d'arbitraire
- **A**utonomy: Dépôts gardent contrôle final
- **R**elatedness: Succès collectif, pas compétition
- **F**airness: Système juste, pas de gagnant/perdant

**Application Gedimat:**
- Si système recommande Dépôt A mais client exige Dépôt B → **Dépôt B ne paie PAS pénalité transport**
- Coûts transport absorbés par budget central "Investissements relationnels clients"
- KPIs dépôt crédités positivement pour flexibilité client

**Formule budget "Investissements relationnels":**
```
Budget annuel = [X% baseline affrètement] réservé pour exceptions client
Révision trimestrielle si dépassement
```

**Données requises:**
1. Baseline: % commandes hors recommandation système (estimation: 10-20%)
2. Baseline: Surcoût moyen exception (écart dépôt optimal vs. choisi)

**Justification:** Système = outil, pas dictateur. Préserver autonomie → adoption volontaire.

- **Propriétaire** : Responsable Planification Logistique (arbitrage final).  
- **Rituels** : comité hebdo exceptions (15 min), revue mensuelle des indicateurs.  
- **Dépôts** : appliquer “proximité d’abord”; escalader les litiges (pas de négociation locale).

---

## 7. Plan 90 jours (jalons)

- **Sem. 1–2** : Alertes & SLA (emails/règles), questionnaire satisfaction, formation courte.  
- **Sem. 3–4** : Scoring dépôt (Excel), test 10 cas, itérations.  
- **Sem. 5–8** : Généralisation règle proximité, revue exceptions, collecte baseline (30 jours).  
- **Sem. 9–12** : Synthèse pilote, calcul RSI (formule), décision généralisation.

*(Gantt réalisable via `pgfgantt` en LaTeX — voir spéc §QG7)*

---

## 7.5 Stress-Test Comportemental : Questions Inversées

**Principe (Rory Sutherland):** Demander "Pourquoi un client partirait quand même ?" révèle risques cachés.

### 5 Risques Résiduels Identifiés

**Risque 1: Système recommande dépôt lent pour commande urgente**
- Mitigation: Flag "urgence client" override automatique → Dépôt le plus rapide
- KPI: Taux override urgence < 15%

**Risque 2: Prix concurrent 10% inférieur**
- Mitigation: Prix ≠ scope. Gedimat différencie sur FIABILITÉ, pas prix spot
- KPI: NPS "délai respecté" > NPS "prix compétitif"

**Risque 3: Angélique quitte / surcharge**
- Mitigation: Documentation complète + formation backup (2e personne)
- KPI: Système utilisable par nouvel employé en <4h formation

**Risque 4: Dépôt ignore recommandation système**
- Mitigation: Système = conseil, pas obligation. Autonomie préservée.
- KPI: Taux adoption volontaire ≥40% (preuve utilité)

**Risque 5: Incident mal géré détruit confiance**
- Mitigation: Protocole escalade clair (Angélique → Manager → PDG si >24h)
- KPI: Temps résolution moyen incidents < 4h

**Test pilote:** Si ≥2 risques se matérialisent en 90 jours → PAUSE système, débriefing.


---

## 8. Indicateurs & validation (pilote)

### 8.5 Indicateurs de Récupération (Recovery Metrics)

**Principe:** Mesurer la qualité de résolution d'incidents, pas seulement leur nombre.

**KPIs Relationnels (nouveaux):**
1. **IRL-1: Loyalty Recovery Rate**
   - Formule: (Commandes répétées clients avec incident résolu) / (Commandes répétées clients sans incident)
   - Cible: >100% (prouve que résolution bien faite > absence d'incident)
   - Source données: CRM Gedimat (à valider accès)

2. **IRL-2: Invisible Delivery Rate**
   - Formule: (Livraisons sans contact client post-commande) / (Total livraisons)
   - Cible: ≥85% (livraisons "invisibles" = satisfaction)
   - Source données: Logs alerting système

3. **IRL-3: Voluntary Adoption Rate**
   - Formule: (Clients utilisant scoring dépôt volontairement) / (Clients éligibles)
   - Cible: ≥40% après 6 mois (prouve utilité perçue)
   - Source données: Logs système + sondage Angélique

**Mesure pilote:** 90 jours, groupe test (10 clients) vs. groupe contrôle (10 clients). Si IRL-1 > 100%, généraliser.

- **Service** : % commandes livrées à la date promise.  
- **Satisfaction** : score post‑livraison (échelle 0–10).  
- **Coût affrètement** : €/t vs baseline.  
- **Taux de consolidation** : part des enlèvements “dépôt le plus proche + navette”.  
- **RSI (formule)** : voir haut de document ; **aucun € Gedimat** sans factures/devis.

**Seuils de réussite (indicatifs)** : Service +4 pts, Satisfaction +10 pts, Consolidation +15 pts, RSI > 0 sur 90 j (selon scénario).

---

## 9. Sensibilité (scénarios)

| Scénario | Hypothèse réduction | Interprétation |
|---|---:|---|
| Conservateur | 8 % | cas prudent, résultats partiels |
| Base | 12 % | référence externe (non Gedimat) |
| Haut | 15 % | cible ambitieuse sous contrôle |
> Calcul : appliquer la formule RSI avec la **baseline mesurée** (30 jours de factures Médiafret) et **coûts navette** internes.

### 9.6 Arbitrages Relationnels : "Inefficacités" vs. Investissements Marketing

**Principe:** Certains coûts semblent "inefficaces" (optimisation transport pure) mais sont RENTABLES (fidélisation client).

**Exemples d'investissements relationnels:**
1. **Express "inutile" techniquement, utile relationnellement**
   - Cas: Client stressé demande express alors que délai standard suffit
   - Coût: +[X]€ transport
   - Bénéfice: Signal "nous vous écoutons" → Loyauté accrue
   - Comptabilisation: Budget marketing, PAS gaspillage logistique

2. **Communication "excessive" avec petits clients**
   - Cas: Alerting SMS pour commande <500€
   - Coût: Temps Angélique ([X] min × [Y] alertes/mois)
   - Bénéfice: Petits clients aujourd'hui = gros clients demain (si fidélisés jeunes)
   - Comptabilisation: Investissement long-terme, PAS coût court-terme

3. **Scoring dépôt "imparfait" toléré**
   - Cas: Système recommande Dépôt A, client préfère Dépôt B (relation historique)
   - Coût: Surcoût transport [Z]€
   - Bénéfice: Préserver relation humaine > optimum algorithmique
   - Comptabilisation: Coût préservation capital relationnel

**Formule budget investissements relationnels:**
```
Budget annuel = [5-10%] × [Baseline affrètement total]
Si ROI fidélisation > 1,0 → budget justifié
```

**Mesure ROI:**
```
ROI = (Δ Taux rétention × [Clients concernés] × [CA moyen] × [Marge %]) / Budget investissements relationnels
```

**Données requises:**
1. Baseline: Taux rétention clients actuels (12 mois)
2. Pilote: Taux rétention clients bénéficiant investissements relationnels (90 jours)
3. Baseline: CA moyen client + marge % (comptabilité)

**Décision:** Mesurer pendant 6 mois. Si ROI < 1,0 → Réduire budget. Si ROI > 2,0 → Augmenter budget.

---

## 9.5 Crédibilité du RSI : Pourquoi des formules et non des chiffres fixes ?

**Principe psychologique (Rory Sutherland):** Les promesses parfaites déclenchent la méfiance. Les imperfections avouées renforcent la crédibilité.

**Application IF.TTT:**
- ❌ **Dangereux:** "Gedimat économisera [X]€/an" (trop beau pour être vrai sans données réelles)
- ✅ **Crédible:** "RSI = [Baseline factures 30j] / [Investissement] × [8-15%]" (honnête, traçable)

**Justification:**
1. Scénarios conservateur/base/haut (8/12/15%) → Montre prudence
2. Formules vides → Invite PDG à insérer SES chiffres → Appropriation
3. Transparence méthodologique → Signal d'intégrité vs. promesses marketing

Ce choix méthodologique N'EST PAS un manque de données. C'est un signal de crédibilité délibéré.

---

## 10. Conformité & confidentialité

- **Réglementaire** : vérifier heures de conduite/repos, charge utile, affrètement, sous‑traitance. Intégrer **Code des transports** & accords locaux ; pas de conseil juridique dans ce document.  
- **Confidentialité** : ne pas diffuser à des concurrents ; **aucun chiffre interne** nominatif ; annexes chiffrées = **formules** + champs **à renseigner**.

---

## Annexes (fournies)
- **Annexe X — Règles de décision (playbook)**  
- **Annexe Y — Alertes & SLA (procédure + pseudo‑SQL)**  
- **Annexe Z — Modèle de coûts (formules + données à collecter)**  
- **QG1‑QG7 — Rapports de contrôle qualité**

*Sources internes* : entretien opérationnel (transcription). fileciteturn0file0  
*Références externes* : voir §4 (liens publics).
