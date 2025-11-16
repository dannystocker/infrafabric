# Roadmap Implémentation : De Jour 1 à Opérationnel (12-16 semaines)

## PHASE 1 : FONDATIONS (Semaines 1-2) — 0€, ~5h travail

### Objectif
Cristalliser le savoir tacite, mettre en place suivi manuel des retards, tester NPS client.

### Livrables à Produire

**1.1 - Registre Fournisseurs (Google Sheets)**
```
Structure obligatoire :
- Colonne A: Nom fournisseur
- Colonne B: Contact principal (nom, tél, email)
- Colonne C: Contacts secondaires (dispatch, facturation)
- Colonne D: Points forts
- Colonne E: Points faibles observés
- Colonne F: Délai standard (ex: 3 jours)
- Colonne G: Notes personnelles (préférences, historique)
- Colonne H: Date dernière commande
- Colonne I: Dernière commande montant/volume

Temps : 1 jour remplissage (Angélique 4h, PDG validation 30min)
```

**1.2 - Scorecard Transporteur Médiafret (Excel)**
```
Metrics Q1 2025 (baseline) :
- Délai : % livraisons <+2h. Cible : 95%. Réalité : ?
- Coût : €/tonne vs budget. Cible : -5%. Réalité : ?
- Réactivité : Temps réponse retard. Cible : <2h. Réalité : ?
- Qualité : Casse/manquants par 100 livr. Cible : <0.5%. Réalité : ?

Temps : 1h data collection (Angélique) + 30min calcul Excel
Fréquence : Revoir Q2, Q3, Q4 (4x/an)
```

**1.3 - Sondage NPS Client (Google Forms)**
```
3 questions :
1. "Sur 0-10, recommanderiez-vous Gedimat ?"
2. "Raison main satisfaction ?" [dropdown]
3. "Un problème ces 3 derniers mois ?" [texte libre]

Diffusion : QR code sur factures/devis semaine 2
Cible : 10-15 réponses semaine 1, 20-30 semaine 2
Temps : 30min création form, 1h analyse réponses
```

**1.4 - Système d'Alerte Manuel**
```
Outlook Calendar :
- Pour chaque commande > 5t : rappel 3 jours avant ETA
- Rappel = "Appeler Luc Emeris commande #ABC"
- Si pas réponse : escalade "Envoyer SMS retard au client"

Temps : 20min setup, 5min par commande (inclus workflow normal)
Efficacité : -50% "découverte retard" en chantier
```

### Validation Semaine 2
- [ ] Google Sheets Fournisseurs complète (50+)
- [ ] Scorecard Médiafret Q1 template validé
- [ ] Google Form NPS liveé, 1ère réponse reçue
- [ ] PDG informé : "Ceci est l'état actuel"

### Coût Semaine 1-2
**0€** (Google/Outlook natif)

### Gain Semaine 1-2
- Documenté = protégé contre départ Angélique
- Visibility = PDG voit "NPS = 35, ça peut monter"
- Baseline = mesurer progrès mois 3, 6, 12

---

## PHASE 2 : ALERTES AUTOMATIQUES (Semaines 3-4) — 50-100€, ~8h travail

### Objectif
Enlever tâche manuelle "appeler fournisseur", remplacer par notification client proactive.

### Livrables

**2.1 - SMS/Email Retard Automatiques (Zapier)**
```
Setup Zapier (20€/mois) :
- Trigger : Quand tu marques colonne "Retard ?" = OUI dans Google Sheets
- Action 1 : Envoyer SMS client (Twilio)
- Action 2 : Notifier Angélique par email (Gmail)
- Action 3 : Log CRM pour trace

Template SMS :
"Commande #123 (tuiles Emeris) - Retard ETA.
Nouvelle livraison : MARDI 10h.
Quoi faire ? Contactez Angélique 06.XX.XX"

Temps : 3h setup Zapier + test 5 SMS (~5€)
Gain immédiat : Client prévenu = perte client -50%
```

**2.2 - Portail WhatsApp Business (Optional, mais efficace)**
```
Coût : 50€/mois (via provider comme Twilio Business)
Setup : 1 semaine
Cas usage : "Luc Emeris reçoit chaque dimanche message"
Message: "Commande XYZ enlèvement LUNDI 8h ?"
Luc répond OUI/NON → Zapier log réponse

Gain : Tu ne téléphones plus Luc = -2h/semaine Angélique
```

**2.3 - Rapport d'Alerte Hebdomadaire**
```
Tableau simple Google Sheets :
- Jour/Date : [alerte envoyée]
- Quoi : [retard Emeris, rupture stock, casse]
- À qui : [client/fournisseur/transporteur]
- Résultat : [client compris, annulation, cherche ailleurs]
- Action corrective : [prochaine fois = ?]

Temps : 10min/semaine remplissage
Utilité : PDG voit "semaine 1 = 2 retards, semaine 2 = 1 retard" = amélioration
```

### Validation Semaine 4
- [ ] Zapier actif, 10 SMS test envoyés
- [ ] WhatsApp Business décidé (oui/non)
- [ ] Rapport alertes semaine 3-4 rempli
- [ ] NPS client = 2ème round (comparer semaine 2 vs semaine 4)

### Coût Semaine 3-4
**50-100€/mois** (Zapier 20€ + SMS credits 30-80€)

### Gain Semaine 3-4
- 0 appels fournisseur oubliés = 100% alertes transmises
- Client reçoit SMS avant rupture = satisfaction +15%
- Tracking rentabilité : "combien SMS coûte vs combien client vaut ?"

---

## PHASE 3 : PILOTE TMS+WMS (Semaines 5-8) — 1,500-2,500€/mois, 40-60h

### Objectif
Déployer système coordonné (TMS route + WMS stock) sur 1 dépôt (Gisors, moins critique).

### Choix Technologie
Recommandation : **Dashdoc TMS (500-1,200€/mois) + Logistiq WMS (500-1,000€/mois)**
- Français natif, support France
- Cloud 100% (0 IT infrastructure)
- APIs ouvertes (compatible Google Sheets, Zapier, Twilio)
- Intégration 2-3 semaines
- Prix modulaire (par utilisateur, par transaction)

Alternative : **Logistar (DSIA) tout-en-un** (1,500-3,500€/mois) si budget unique.

### Semaine 5 : Sélection & Contrat

**5.1 - Demande Devis & Démo**
```
Contacter :
- Dashdoc : +33.X.XX / demo@dashdoc.com
- Logistiq : +33.X.XX / sales@logistiq.fr
- Demander : devis pour 1 dépôt 3 mois pilot

Négociation clés :
- Mois 1-3 = pilot prix réduit (-20%) ?
- Support décalé Franck = ok ?
- Data export = propriété Gedimat ?
- Contracter 3 mois (pas 12) si inquiet

Temps : 2h démo + 1h signature
Décision : signez semaine 5 latest
```

**5.2 - Preparation Environnement Gisors**
```
- Inventaire réel dépôt : combien palettes, tonnage, réf produits ?
- Liste transporteurs alternatifs (pas juste Médiafret)
- Top 5 fournisseurs (données volume historique)
- Identifier "power user" Gisors (vendeur magasin ?), dédier 10h formation

Temps : 1 jour Gisors audit + 1h PDG validation
Livrables : fichier Excel "baseline Gisors" (stocks, frais, incidents)
```

### Semaine 6 : Configuration & Data Migration

**6.1 - Paramétrage TMS Dashdoc**
```
Setup items :
- Créer 3 routes (Gisors → fournisseur A, B, C habituel)
- Importer transporteurs (Médiafret + 2 alternates)
- Définir règles consolidation (ex: ≤5t = pas consolidation, >5t = chercher 2e commande)
- Setup tracking live (GPS)

Temps : 3-4h Angélique/Dashdoc support
Délai : compléter semaine 6
```

**6.2 - Paramétrage WMS Logistiq**
```
Setup items :
- Importer référentiel produits (SKUs, codes barres)
- Créer zones rangement Gisors (A1-A10, B1-B20, etc.)
- Importer stock initial (combien tuiles section A1 ?)
- Setup scanning (téléphone/scanner code barre)

Temps : 2-3h Logistiq + 2h Angélique familiarisation
Délai : compléter semaine 6
```

**6.3 - Formation Équipe Gisors**
```
Qui : Vendeur magasin, chauffeur interne, responsable dépôt (3 pers)
Quoi :
- "Où je vois stock exact ?" (WMS)
- "Comment je sais si commande consolidée ?" (TMS)
- "Quand j'enlève chez fournisseur ?" (TMS alerte)
- "Où je scanne palette ?" (WMS barcode)

Durée : 2h par personne (groupe 1h + pratique)
Timing : fin semaine 6
```

### Semaine 7 : Test Parallèle

**7.1 - Mode Parallèle (Ancien + Nouveau)**
```
Période : semaine 7 entière
Tous les workflows se font DEUX FOIS :
1. Ancien (Angélique + papier/Excel)
2. Nouveau (TMS+WMS)

Comparaison :
- Jour 1-7 : 10 commandes gérées parallèle
- Mesurer "bruit" entre deux systèmes
- Trouver bugs avant "go-live"
- Équipe Gisors gagne confiance système
- AUCUNE opération ne dépend de nouveau (still safe)

Livrables : Liste bugs/ajustements (max 20)
Temps : 5h Angélique/support pour debug
```

**7.2 - Démarrage Consolidation Route**
```
Cas concret test :
- Commande Emeris tuiles : 3t Gisors, 2t Méru
- TMS dit : "enlever Emeris, livrer Gisors, puis navette Méru"
- Coût estimation : 40% moins cher que 2 camions

Valider :
- Navette interne peut faire Gisors→Méru en timeline client ?
- Stockage temporaire Gisors disponible ?
- Communication client OK ("reçoit mardi, retrait possible dimanche") ?

Décision : valider avant week-end semaine 7
```

### Semaine 8 : Go-Live Gisors

**8.1 - Lancement Production**
```
Mardi 8h : Ancien système OFF
Mardi 8h : Nouveau TMS+WMS ON
Mercredi : Support intensif (vendor + Angélique + PDG si needed)
Jeudi-Friday : Normalisation, monitoring

Métrique jour 1 :
- Combien commandes passées ? (10+ = ok)
- Erreurs ? (<2 acceptable)
- Temps moyen picking (vs ancien) ?
- Coût premier transport consolidé ?

Si crash grave : rollback ancien = possible jusqu'à vendredi 17h
```

**8.2 - Support Intensif**
```
Planning :
- Jour 1 (mardi) : Vendor + Angélique 6h presence
- Jour 2 (mercredi) : 2h check matin, 2h check soir
- Jour 3-5 : 1h matin, support on-call si besoin
- Week 2 : suivi quotidien court (15min)

Hotline : Dashdoc/Logistiq directement, pas passer par Gedimat IT
```

### Validation Semaine 8
- [ ] Gisors : 20+ commandes TMS+WMS sans incident majeur
- [ ] Consolidation : 2-3 routes économisées (mesurer coût réel)
- [ ] Satisfaction : Team Gisors "c'est ok" (pas "c'est nul")
- [ ] NPS client : semaine 8 sondage = monté vs semaine 4 ?

### Coût Semaine 5-8
**1,500-2,500€/mois** = Dashdoc + Logistiq abonnement
**Support** = inclus vendeur (pas coût additionnel)

### Gain Semaine 5-8
- Route consolidation : +8-15k€ economisé (3-4 mois projection annuel)
- Erreur picking : -40% (exactitude WMS)
- Délai stockage : -2 jours (stock visible)
- Confiance équipe : "on peut scaler"

---

## PHASE 4 : DÉPLOIEMENT PROGRESSIF (Semaines 9-12) — 1,800-2,800€/mois

### Objectif
Ajouter Méru et Breteuil-Ponton progressivement, stabiliser TMS+WMS en routine.

### Semaine 9-10 : Déploiement Méru

**Semaine 9 :** Migration data + formation (4h)
**Semaine 10 :** Lancement parallèle (7 jours) → production

Différence vs Gisors :
- Data Méru plus complète (plus grosse site)
- Contact Méru = déjà habitué Gisors succès
- Risque faible (leçons apprises)

### Semaine 11-12 : Déploiement Breteuil

Timing :
- Semaine 11 : Migration + formation
- Semaine 12 : Démarrage

Total :
- 3 dépôts opérationnel TMS+WMS end semaine 12

### Coût Semaine 9-12
Ajout utilisateurs TMS/WMS = +200-300€/mois (per site minimal)
**Total : 1,800-2,800€/mois pour 3 dépôts**

### Gain Semaine 9-12 (Cumulatif)
- Année complète projection : +25-35k€ transport (consolidation)
- Moins ruptures : +8-12k€ retention client
- Moins saisies doubles : +3-5k€ productivité temps
- **Total année 1 : +36-52k€ net** vs investissement 24k€

---

## PHASE 5 : OPTIMISATION & DÉCISION LONG TERME (Semaine 13-16)

### Semaine 13 : Premier Bilan Complet

**Check-list :**
- [ ] 3 dépôts TMS+WMS stable (uptime >99%)
- [ ] NPS client comparé semaine 1 vs semaine 13 (target +10 points)
- [ ] Coûts transport comparé semaine 1 vs semaine 13 (target -12%)
- [ ] Zero incidents majeurs 2+ semaines consécutives

**Décision 1 :** "Continuer TMS+WMS ?" → OUI (sauf catastrophe) → Signer contrats année 2

**Décision 2 :** "Ajouter WMS+" ou "Rester WMS léger ?" → Dépend volumes, mais rester léger probable

### Semaine 14-15 : Formation Continu + Optimisation

**Formation :**
- Nouvelles équipes (rotations)
- Power users (Angélique) = advanced features
- PDG = dashboard mensuel (ROI tracking)

**Optimisation :**
- Affiner règles consolidation (ex: "jamais retard >4h même si 30% plus cher")
- Ajouter champs CRM (notes Mélissa Médiafret performance)
- Intégrer portail WhatsApp + TMS notifications

### Semaine 16 : Décision Année 2

**3 Options :**

**Option A : Rester TMS+WMS léger (Rec)**
- Coûts : 1,800-2,500€/mois
- Avantage : simple, ROI clair, équipe habituée
- Limite : pas ERP (compta/devis séparé), automatisation modérée

**Option B : Ajouter ERP léger**
- Ajouter Sage 100 (300-500€/mois) pour devis, compta, achats
- Intégrer API vers TMS+WMS (coûts dev 3-5k€ one-time)
- Coûts total : 2,500-3,500€/mois
- Gain : flux end-to-end, moins saisies doubles
- Année 2 ROI : +50-70k€

**Option C : Migration ERP complet**
- Remplacer tous outils par Logistar suite (3,500-5,000€/mois)
- Avantage : suite intégrée, French vendor
- Désavantage : migration 3-4 mois, risque, coût élevé
- Only si volumes >500t/mois ou franchises multiples

**Recommandation :** **Option A an 1** (stable + léger), **Option B an 2** (si ROI confirme).

---

## RÉSUMÉ TIMELINE & COÛTS

| Phase | Semaines | Coût/Mois | Coût Total | Gain Année 1 | Status |
|-------|----------|-----------|-----------|------------|--------|
| **1. Fondations** | 1-2 | 0€ | 0€ | +5-8k€ | ✅ Immédiat |
| **2. Alertes** | 3-4 | 50€ | 200€ | +10-15k€ | ✅ Semaine 3 |
| **3. Pilote** | 5-8 | 1,500-2,500€ | 6-10k€ | +15-25k€ | ⚠️ Gisors |
| **4. Déploiement** | 9-12 | 1,800-2,800€ | 5-8k€ | +10-15k€ | 📅 3 dépôts |
| **5. Optimisation** | 13-16 | 1,800-2,800€ | 5-8k€ | +5-10k€ | 🎯 Décision |
| **TOTAL AN 1** | **16 sem** | **Avg 1,500€** | **16-26k€** | **+45-73k€** | **ROI 2-4x** |

---

## GESTION DES RISQUES

### Risque 1 : "C'est trop compliqué, équipe refuse"
**Mitigation :**
- Phase 1 = 0 technologie (Excel/Google Sheets)
- Phase 2 = 1 alerte simple (SMS)
- Phase 3 = seulement 1 dépôt (pas tous d'un coup)
- Formation on-site = soutien constant

**Plan B :** Si semaine 5 consensus "c'est pas bon" → stop, pas continuer

### Risque 2 : "Retard fournisseur lors déploiement"
**Mitigation :**
- Signer Dashdoc/Logistiq semaine 5 = 2 semaines buffer
- Demo compte avant signature (vérifier vraiment fonctionne)
- Support continu inclus (pas coûts additionnel)

**Plan B :** Si vendor échoue semaine 7 → utiliser solution alternative (Logistar) ou rester phase 2

### Risque 3 : "Données migrer mal = confusion semaine 8"
**Mitigation :**
- Phase 7 = double saisie (ancien + nouveau parallèle)
- Zero risque "go live" car ancien système toujours actif
- Audit données semaine 6 (corriger avant lancement)

**Plan B :** Si erreur données découverte week-end → rollback lundi, fix, redeploy mercredi

### Risque 4 : "PDG dit 'non' avant semaine 5"
**Mitigation :**
- Phase 1 résultats = NPS data + score transporteur objectif
- Phase 2 = SMS coûte 50€/mois, pas 50k€
- Présenter ROI conservateur (20k€ an 1) vs optimiste (70k€)
- "3 mois pilote Gisors" = simple commit

---

## DÉCISIONS CLÉS À DOCUMENTER

**Semaine 2 :** PDG approuve Phase 1 résultats
**Semaine 4 :** PDG décide "continuer Phase 2 SMS ?" (oui probable)
**Semaine 5 :** PDG signe contrat TMS+WMS pilot
**Semaine 8 :** PDG approuve Gisors résultats, valide Phase 4 (Méru+Breteuil)
**Semaine 13 :** PDG décide "Contrat an 2 ?" (oui probable) + "ERP année 2 ?" (maybe)

---

**Responsable Exécution :** Angélique (Coordinatrice) + Support Vendor (Dashdoc/Logistiq) + PDG (décisions budgétaires)

**Contact Principal Risque :** Si Angélique absent → qui gère TMS/WMS ?
**Mitigation :** Former 2 "power users" (Méru vendeur + Breteuil responsable dépôt) en semaine 13

---

*Roadmap préparée par Agent 5 - InfraFabric PASS 1*
*Méthodologie : IF.optimise (phasing), IF.search (timeline benchmarks), IF.guard (risk mitigation)*
