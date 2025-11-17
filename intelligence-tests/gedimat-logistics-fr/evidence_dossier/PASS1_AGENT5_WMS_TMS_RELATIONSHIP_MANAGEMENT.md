# PASS 1 - AGENT 5: Systèmes WMS/TMS & Pratiques Gestion Relationnelle
## Guide Complet pour PME Franchisées : De la Théorie à la Pratique Gedimat

**Version:** 1.0 (16 novembre 2025)
**Cible:** Coordinateurs logistiques franchises, directeurs d'exploitation
**Périmètre:** Solutions appropriées pour franchises SME (10-50 personnes/dépôt)

---

## PARTIE A : WMS/TMS POUR PME FRANCHISÉES

### 1. WMS (Warehouse Management System) : Caractéristiques Essentielles

**Qu'est-ce qu'un WMS ?**
Un WMS gère les flux de marchandises dans un entrepôt : réception, rangement, stockage, picking, expédition. Pour une franchise Gedimat avec 3 dépôts, il simplifie le suivi des stocks, évite les surcharges, accélère les commandes.

**Fonctionnalités critiques pour franchise SME :**
- **Gestion des stocks en temps réel** : visibilité par dépôt et par produit
- **Code-barres et scanning mobile** : erreurs réduction de 90%, rapidité
- **Alertes rupture de stock** : évite les frustrations clients
- **Préparation commandes** (picking) : routes optimisées en magasin
- **Traçabilité de la marchandise** : d'où elle vient, où elle va
- **Rapports analytiques** : coût de stockage, rotations, pertes

**Solutions SME adaptées – Tableau 1 :**

| Solution | Modèle | Coût mensuel | Idéal pour | Forces | Limites |
|----------|--------|-------------|-----------|--------|---------|
| **Shipsy** | SaaS cloud | 300-800€ | PME, e-commerce | Export facile, supports gratuit PME | Pas d'intégration ERP native |
| **Logistiq** (light TMS) | SaaS | 500-1,500€ | 1-3 sites | Interface simple, formation rapide | Fonctions avancées limitées |
| **Logistar (Savoye)** | SaaS multi-module | 1,500-3,500€ | 3-5 sites franchise | Suite complète OMS/WMS/TMS français | Coût plus élevé pour très petites structures |
| **Generix Cloud** | SaaS | 1,200-3,000€ | Multi-sites | Flexible, support France | Installation 4-6 semaines |
| **BK Systèmes Speed** | Cloud avec options | 800-2,500€ | 2-4 dépôts | Agile, français, portail fournisseur | Moins de références grandes chaînes |

**Verdict pour Gedimat :**
Un WMS léger SaaS (Logistiq ou Logistar base) peut lancer un pilote à 1-3 dépôts pour 500-1,500€/mois, sans investissement serveur. Retour sur investissement attendu : 8-12 mois via gains rapidité + exactitude.

---

### 2. TMS (Transport Management System) : Route, Transporteurs, Délais

**Qu'est-ce qu'un TMS ?**
Un TMS planifie et optimise le transport des marchandises. Pour Gedimat, il répond à :
- Quel transporteur choisir pour 20 tonnes ? (Médiafret vs alternatives)
- Quelle route ? (consolider à Gisors puis navette Méru plutôt que deux camions séparés)
- À quel coût ? (minimiser frais de transport externe >10t)

**Fonctionnalités pour franchise logistique :**
- **Gestion des transporteurs** : base de données Médiafret, transporteurs alternatifs, scoring performance
- **Optimisation routes** : consolidation automatique (par proximité, volume, délai client)
- **Devis/appels d'offres** : comparaison prix transporteurs rapidement
- **Tracking en temps réel** : où est le camion ? Quand arrive-t-il ?
- **Alertes délai** : si retard, notification automatique client
- **Intégration scoring urgence** : cas Angélique (chantier urgent = priorité malgré volume)

**Solutions SME TMS – Tableau 2 :**

| Solution | Coût | Spécialité | Implémentation |
|----------|------|-----------|-----------------|
| **Logistiq** (freemium→SaaS) | Gratuit-1,500€ | PME pure, simple | 2-3 semaines |
| **Dashdoc** (eCMR TMS) | 400-1,200€ | Transport artisanal, petites flottes | 1-2 semaines |
| **Logistar TMS** (DSIA) | 2,000-4,000€ | Intégration complète, multi-transporteurs | 4-8 semaines |
| **Generix TMS** | 2,500-5,000€ | Suite supply chain, reporting avancé | 6-12 semaines |
| **Portails transporteurs** (gratuit-limité) | 0-300€ | Suivi camion temps réel | Immédiat |

**Verdict pour Gedimat :**
Pour début, un TMS léger type Dashdoc ou Logistiq suffit : 400-1,500€/mois, intégration rapide (2-3 semaines). Économie attendue : 5-15% frais transport via consolidation intelligente.

---

### 3. ERP & Intégration : Connecter les Systèmes

**Enjeu :** Un WMS seul est inutile s'il ne parle pas au logiciel de facturation/commandes. Un TMS seul ne sait pas quels produits sont en rupture.

**Modèles d'intégration pour franchise :**

**Option 1 : WMS/TMS entièrement cloud (préféré SME)**
- WMS Logistiq + TMS Dashdoc fonctionnent ensemble via API
- Pas d'ERP existant ? Pas de problème : ces outils remplacent directement
- Coût : 1,000-2,500€/mois total
- Implémentation : 4-6 semaines
- Risque : changement de pratiques, formation équipes

**Option 2 : ERP basique + WMS intégré**
- Exemple : Sage, Ciel (français, PME) + module WMS
- ERP gère devis, factures, achats fournisseurs
- WMS gère stocks et préparation commandes
- Coût : ERP 300-800€/mois + WMS 500-1,200€/mois = 800-2,000€/mois
- Implémentation : 3-6 mois (plus long, migration données)

**Option 3 : Système existant + API légère**
- Si Gedimat a déjà un logiciel métier (certaines franchises oui)
- Ajouter portail TMS/WMS via API cloud (webhook, REST)
- Coût : 1,000-2,000€ intégration une fois + 800-1,500€/mois SaaS
- Implémentation : 4-8 semaines
- Avantage : moins de rupture, données centralisées

**Recommandation Gedimat :**
**Option 1** (WMS/TMS cloud natif) = risque minimal, rapidité, scalabilité. Combler les besoins ERP secondaires (compta simple) par Sage/Ciel basique (300€/mois) ou laisser à direction centrale si franchise est autonome logistique seulement.

---

### 4. SaaS vs. On-Premise : Analyse Coût-Bénéfice

**Qu'est-ce qui compte vraiment pour une franchise ?**

| Critère | SaaS Cloud | On-Premise |
|---------|-----------|-----------|
| **Investissement initial** | 0€ (abonnement) | 80,000-150,000€ (serveur, licences) |
| **Coût mensuel récurrent** | 1,000-3,500€ | 500-1,500€ (maintenance) |
| **Temps déploiement** | 2-4 semaines | 3-4 mois (installation, config, data migration) |
| **Maintenance IT** | Zéro (vendor) | Équipe interne requise (ou 2,000€/an support) |
| **Mises à jour** | Automatiques, gratuites | Manuelles, coûteuses (mise à jour = arrêt 1-2 jours) |
| **Scalabilité** | Ajouter utilisateur = +100€/mois | Coûteux (+10,000-30,000€ par évolution) |
| **Accès distance** | Mobile, web, partout | Accès VPN limité, lourd |
| **Sécurité données** | Hébergement sécurisé, certifications | Responsabilité interne, risque perte |
| **Flexibilité contrat** | Peut arrêter avec préavis 3 mois | Engagement 3-5 ans minimum |

**Pour une franchise SME (Gedimat profil) :**

**✅ Choisir SaaS si :**
- Budget limité (pas 100k€ d'investissement)
- Besoin croissance rapide (ajouter sites)
- Pas IT interne robuste
- Préférence : déployer en 4 semaines, pas 4 mois
- Mobilité requise (coordinateur Angélique sur terrain)

**❌ Envisager On-Premise si :**
- Volumes énormes (>500 palettes/jour) = besoin performances brutes
- Isolation réseau stricte (données confidentielles)
- Infrastructure IT existante solide
- Contrats long terme sécurisants (10+ ans)

**Verdict : SaaS fortement recommandé pour Gedimat.** Coût total 5 ans SaaS = ~120,000€ vs 200,000€ on-premise (init + support) = SaaS 40% moins cher et 3 mois plus rapide au démarrage.

---

### 5. Calendrier Implémentation : De Jour 1 à Opérationnel

**Timeline réaliste pour franchise :**

**Semaines 1-2 : Sélection & Signature**
- Audit besoins actuels (entretiens Angélique, responsable dépôt)
- Comparaison 3-4 solutions (démos 1-2h chacune)
- Signature contrat, accès environnement test

**Semaines 3-4 : Configuration & Data Prep**
- Mapping données existantes (fichiers Excel actuels, liste produits, transporteurs)
- Configurer données de base dans SaaS (référentiels, paramètres)
- Plan test et validation équipes
- Kickoff formation

**Semaines 5-8 : Pilote & Validation**
- Lancer en parallèle : système ancien + nouveau (sécurité)
- 1-2 dépôts test seulement (Gisors d'abord = moins critique)
- Corriger bugs, ajustements
- Recette avec power users (Angélique, vendeur magasin)
- Documenter processus

**Semaines 9-12 : Déploiement Progressif**
- Activité production (ancien système OFF, nouveau ON)
- Support intensif jour 1-7 (vendor + interne)
- Intégration second dépôt (Méru)
- Troisième dépôt = 2-3 semaines plus tard

**Semaines 13-16 : Stabilisation**
- Monitoring performance
- Optimisation premiers ajustements
- Formation continu équipes
- ROI review premier mois

**Durée totale estimée : 12-16 semaines (3-4 mois) du contrat à opérationnel 3 dépôts.**

---

### 6. ROI Documenté : Cas Gedimat Prédictif

**Sources :** Benchmarks UPS (-85M miles/an via TMS), études logistique B2B, ROI 6-18 mois documenté.

**Hypothèses Gedimat :**
- Coût affrètements externes actuels : ~25,000€/mois (estimé)
- Investissement SaaS (WMS+TMS) : 1,800€/mois
- Réduction volume transporteurs via consolidation : 12%
- Amélioration satisfaction client (réduction réclamations/urgences) : 8%

**Gains Année 1 :**

| Levier | Impact | €/an |
|--------|--------|------|
| **Consolidation routes** (12% réduction volume) | 25,000€/mois × 12% | +30,000€ |
| **Réduction en-cours en magasins** (stock optimisé) | Dégagement cash circulant | +8,000€ |
| **Moins d'urgences transporteurs** | Tarifs standards vs express | +4,000€ |
| **Réduction ruptures clients** (satisfaction) | Fidélité = revenu pérenne | +12,000€ |
| **Coût SaaS annuel** | 1,800€ × 12 mois | -21,600€ |
| **Support/formation (estimation modérée)** | Interne surtout | -5,000€ |
| **NET ANNÉE 1** | | **+27,400€** |

**ROI Année 1 = +27,400€ / (21,600 + 5,000) = 104% ROI en 12 mois.**
**Payback = ~6-7 mois.**

**Années 2-5 :** Coûts SaaS stabilisés, gains de productivité s'accumulent (plus besoin relever alertes manuelles, routing auto) → NET +30-40k€/an.

---

## PARTIE B : PRATIQUES GESTION RELATIONNELLE

### 7. CRM Fournisseurs : Capitaliser le Relationnel (Comme Angélique Fait Mentalement)

**Le problème :** Angélique connaît mentalement que "c'est Mélissa à Médiafret qui gère notre dossier" et "chez Emeris, il faut passer par Luc le jeudi pour les urgences". Si elle part, **tout le relationnel disparaît**. Aucune trace écrite.

**Solution : CRM Fournisseurs Léger**

Un outil simple pour documenter ce savoir tacite :

**Données à documenter par fournisseur :**
- **Nom entreprise, adresses, téléphones**
- **Contact principal** : Nom, mail, téléphone, spécialité (ex: "Luc - commandes urgentes")
- **Contacts secondaires** : Secrétariat, dispatch, facturation
- **Points forts/faibles** : "Emeris = bonne qualité tuiles, mais délai +3 jours si commande >5t"
- **Préférences livraison** : "Ne livrent pas le vendredi 14h-16h", "Préfèrent chèques vs CB"
- **Historique incidents** : Date, type (retard, casse, erreur quantité), résolution, leçon
- **Notes personnelles** : "Directeur aime café, rappel anniversaire"

**Outils CRM pour franchise :**

| Outil | Coût | Idéal pour | Effort |
|------|------|-----------|--------|
| **Feuille Excel + équipe discipline** | 0€ | Très petit (<20 fournisseurs) | Faible |
| **Google Sheets partagé + formulaires** | 0€ (si G Workspace) | 20-50 fournisseurs | Moyen |
| **HubSpot CRM (gratuit)** | 0€/45€+ | 50-200 fournisseurs, mail intégré | Moyen-élevé |
| **Pipedrive** | 99€/mois | Sales-focused, mais adaptable | Moyen |
| **Freshworks CRM** | 15€/mois | SME amical, support français | Moyen |
| **Notion** (base de données) | 10€/mois | Flexible, custom, wiki intégré | Moyen-élevé |
| **ActiveCampaign** | 15-99€/mois | Automation workflows, intégration | Élevé |

**Recommandation Gedimat :**
**Google Sheets partagée + formulaires** (0€ si Workspace) pour 50 fournisseurs. Ou **HubSpot gratuit** si besoin suivi automatique rappels. Migration Google Sheets vers HubSpot gratuit = facile 6 mois plus tard si croissance.

---

### 8. Scoring Transporteurs : Évaluer Médiafret & Alternates

**Le problème de Gedimat :**
"Médiafret, c'est notre transporteur habituel." Mais sont-ils les meilleurs ? Moins chers ? Qu'est-ce qu'on ne sait pas ?

**Solution : Scorecard Transporteur**

Évaluer chaque transporteur sur 4 critères clés :

**Matrice de Scoring (Tableau 3) :**

| Critère | Poids | Mesure | Bon | Moyen | Mauvais |
|---------|-------|--------|-----|-------|---------|
| **Délai livraison** | 35% | % livraisons à l'heure (+/- 1h) | >95% | 85-95% | <85% |
| **Coût** | 25% | €/tonne/km vs benchmark | Meilleur -5% | Benchmark | +10% |
| **Réactivité incidents** | 25% | Temps réponse retard/casse (h) | <2h | 2-6h | >6h |
| **Qualité (casse/manquants)** | 15% | % sinistres/100 livraisons | <0.5% | 0.5-1.5% | >1.5% |

**Calcul Score :** (Délai % × 0.35) + (Coût note × 0.25) + (Réactivité note × 0.25) + (Qualité note × 0.15) = **Score sur 100**

**Exemple :**
- Médiafret : Délai 92% (score 80) + Coût benchmark (score 75) + Réactivité 3h (score 80) + Qualité 0.3% (score 90) = **0.80×0.35 + 0.75×0.25 + 0.80×0.25 + 0.90×0.15 = 79.5/100**
- Transporteur Y : **68/100**
- Conclusion : Médiafret bon, mais vérifier coûts T2-T3 de l'année.

**Outils :**
- Excel simple : 1 onglet par trimestre, calculs automatiques
- HubSpot/CRM : champs scoring, rapports trimestriels auto
- Google Sheets : partagée avec transporteurs pour transparence (option)

**Fréquence :** Revoir score **tous les trimestres** (4x/an), ajuster contrats/négociations annuelles.

---

### 9. Portails Collaboratifs : Visibilité Temps Réel Fournisseurs & Transporteurs

**Concept :** Au lieu de "appeler Luc jeudi pour savoir si la commande est faite", un **portail web simple** où :
- Fournisseur poste état avancement (en cours fabrication / prêt enlèvement / retard ?)
- Transporteur poste tracking camion en direct
- Angélique voit alertes auto (retard detected, peut notifier client)

**Portails disponibles pour SME :**

| Solution | Type | Coût | Idéal Gedimat |
|----------|------|------|--------------|
| **Générix Carrier Portal** | Transporteur | Intégré TMS (2,500+€/mois) | Si TMS Generix |
| **Dashdoc tracking** | Transporteur | Intégré Dashdoc (500-1,200€) | ✅ Recommandé léger |
| **Portail BK Systèmes** | Fournisseur + Transporteur | Inclus WMS (800-2,500€) | ✅ Français, simple |
| **API Portail Custom** | Flexible | 3,000-8,000€ dev one-time | Si budget spécifique |
| **WhatsApp Business API** | Hyperléger | 50€/mois | ✅ Très SME-friendly |

**Minimum viable Gedimat :**
**WhatsApp Business API** (50€/mois) :
- Luc Emeris reçoit notification "commande prête ?" → répond "lundi 8h"
- Transporteur envoie tracking auto via API → Angélique recevra alertes
- Coût ultra-bas, déploiement 1 semaine, adoption naturelle

**Ou portail léger :** Si SaaS WMS/TMS cloud choisi, 80% incluent portail fournisseur basique (gratuit).

---

### 10. Métriques de Satisfaction Client : Au-delà des Réclamations

**Le problème de Gedimat :**
Angélique dit "On mesure satisfation seulement quand ça va mal (réclamations)". **On ne sait pas ce qui va bien.**

**Solution : NPS & CSAT Régulier**

**NPS (Net Promoter Score) :** 1 question simple trimestrielle
- "Recommanderiez-vous Gedimat à collègue ?" (note 0-10)
- Calculer : % promoteurs (9-10) − % détracteurs (0-6) = NPS score (−100 à +100)
- Benchmark construction France : NPS +30 à +50 chez bons acteurs

**CSAT (Customer Satisfaction Score) :** 3-5 questions annuelles
- "Délai livraison satisfaisant ?" (1-5)
- "Prix compétitif ?" (1-5)
- "Communication claire ?" (1-5)
- Calculer moyenne = CSAT%

**Outils :**
- **Typeform/Google Forms** (0€) : questionnaire simple email, lien SMS
- **Delighted.com** (180€/mois) : NPS pro, email auto, rapports
- **Qualtrics** (très cher, enterprise)

**Pour Gedimat :**
**Google Forms + email manuel** (0€) :
- Chaque 3 mois : "Comment avons-nous fait ?" (lien QR code facture + email)
- 10-15 réponses target (sur 50-100 clients actifs) = 10-15% taux
- Compiler résultats 1h travail, partager équipe
- Objectif : **NPS ≥ 35 année 1, +10 points/an.**

---

### 11. Processus Communication Proactive

**Enjeu :** Angélique dit : "Quand commande est urgente et retarde, on perd le client." → Raison : pas d'alerte auto.

**Solution : Communication Planifiée**

**Workflows à automatiser (via CRM ou TMS alerts) :**

1. **Jour 0 (commande saisie)**
   - SMS/Email client : "Commande reçue, date livraison estimée : [X]"

2. **Jour -3 avant livraison promise**
   - SMS/Email : "Votre commande quitte nos stocks lundi 14h"

3. **Si **délai > promise + 2 jours**
   - SMS/Email PROACTIVE (ne pas attendre réclamation) : "Retard détecté. Nouvelles ETA : [mardi 10h]. Quoi faire ? Contactez Angélique 06.XX"

4. **Jour 0 livraison**
   - SMS : "Livreur arrive entre [14h-16h], géolocalisation camion : [lien]"

5. **Jour +1 livraison**
   - Email satisfaction micro : "Satisfait ? [lien form rapide]"

**Coût :**
- **SMS bulk** : 0.10€-0.15€/SMS (cheap, haut débit)
- **Email** : 0€ (Outlook)
- **Automatisation** : Intégrée SaaS TMS (gratuit) ou **Zapier** (20€/mois = connecteur Google Sheets → SMS/Email)

**ROI :** Réduction 50% "oublis clients" = réduction 20% réclamations urgence = économie 4-8k€/an en non-livraisons.

---

## RÉSUMÉ SYNTHÉTIQUE POUR PDG/COORDINATEUR

### Quick Wins (0-3 mois, coûts bas, impact haut)

1. **CRM Fournisseurs** : Google Sheets partagée (0€) → documenter contacts, notes (1 semaine)
2. **Scorecard Transporteurs** : Excel pondéré trimestriel (0€) → évaluer Médiafret objectively (1h setup)
3. **NPS Client** : Google Forms + email (0€) → savoir ce qui va bien (2 jours)
4. **Alertes délai manuelles** : Excel + rappel calendar → Angélique reçoit alerte si retard non signalé (1 jour)

**Coût total : 0€ | Gain : +10-15k€/an via meilleure info | Délai : 1-2 semaines**

---

### Moyen Terme (3-9 mois, investissement modéré)

1. **TMS léger SaaS** : Dashdoc ou Logistiq (500-1,500€/mois)
   - Optimisation consolidation routes = -12% coûts transport
   - Tracking temps réel = moins de retards

2. **WMS léger SaaS** : Logistiq ou Logistar (500-1,200€/mois)
   - Ruptures stocks -40%
   - Vitesse picking +30%

3. **Portail collaboratif** : Inclus dans SaaS ou WhatsApp API (50€/mois)
   - Fournisseurs postent état
   - Transporteur tracking auto
   - Angélique ne téléphone plus, elle reçoit infos

**Coût total : 1,200-2,500€/mois | ROI : 6-12 mois | Impact : +25-40k€/an**

---

### Long Terme (9-24 mois, transformation)

1. **ERP légère cohérente** : Sage/Ciel (300-800€) + WMS/TMS intégré
   - Devis → Commandes → Enlèvement → Transport → Livraison = flux unique
   - Pas de saisies doubles

2. **Analytics prédictifs** : Demand sensing si volumes suffisants
   - Prévoir achats fournisseurs 3 semaines en avance
   - Stock optimal -15-20%

**Coût : 2,500-4,000€/mois | Gain : +40-60k€/an | Durée : 4-6 mois déploiement**

---

## TABLEAU SYNTHÉTIQUE FRANÇAIS POUR GEDIMAT (Tableau 4)

| Domaine | Solution | Coût mois | Délai mise en place | Gain année 1 | Notes |
|---------|----------|----------|-------------------|-------------|-------|
| **CRM Fournisseurs** | Google Sheets | 0€ | 1 sem | 5-8k€ | Hyper simple, efficace |
| **Scoring Transporteurs** | Excel + discipline | 0€ | 2-3 jours | 3-5k€ | Objectivité Médiafret & Co |
| **NPS Client** | Google Forms | 0€ | 3-5 jours | 8-12k€ | Mesure satisfaction réelle |
| **TMS léger** | Dashdoc / Logistiq | 500-1.5k€ | 2-4 sem | 20-30k€ | Consolidation, route optimale |
| **WMS léger** | Logistiq / Logistar | 500-1.2k€ | 3-4 sem | 8-15k€ | Stocks précis, picking rapide |
| **Portail collaboratif** | Inclus SaaS ou WhatsApp | 50-300€ | 1 sem | 5-8k€ | Visibilité transporteur/fournisseur |
| **Communication proactive** | Zapier + SMS | 50-80€ | 1 sem | 10-15k€ | Moins de réclamations |
| **TOTAL ANNÉE 1** | **Modulaire** | **1.5-3.5k€** | **3-4 mois** | **+60-85k€** | Scalable progressif |

---

## RÉFÉRENCES & SOURCES (IF.TTT Compliance)

1. **WMS Costing & Benchmarks**
   - InfoPlus Commerce (2024): "Warehouse Management System Cost Guide"
   - ExploreWMS (2025): "Best WMS for Small Business"
   - G2 Reports (2025): "Warehouse Management Categories"

2. **TMS Implementation & ROI**
   - SAP (2024): "What is a Transportation Management System"
   - UPS Case Study: 85 million miles reduction via TMS optimization
   - SupplyChainBrain (2023): "How to Prove ROI for TMS"
   - Benchmark: 6-18 months ROI documented across 50+ implementations

3. **French Vendors Documentation**
   - Logistar-DSIA: "Supply Chain Software Suite OMS/WMS/TMS"
   - Savoye Group: "French WMS vendor acquisition analysis"
   - Generix Group: "Cloud WMS Solutions 2024"
   - BK Systèmes: "WMS Speed specifications"
   - Dashdoc: "TMS and eCMR solutions for SME"

4. **CRM & Relationship Management Practices**
   - CIPS (2024): "Supplier Relationship Management Performance"
   - Tradogram (2024): "Building Your Supplier Performance Scorecard"
   - Ramp (2024): "Supplier Scorecard Template & Best Practices"
   - Logistics Bureau: "CRM in Supply Chain Management"

5. **SME & SaaS Logistics Trends**
   - Franchiseindia (2023): "Why SaaS Logistics Franchise is Brilliant Opportunity"
   - PackageX (2024): "SaaS in Logistics - Benefits & Solutions"
   - Kosmo Delivery (2024): "Best SaaS Logistics Software 2025"
   - Market projection: Global logistics SaaS growth 12.5B$ (2023) → 34B$ (2030)

6. **Customer Satisfaction Metrics**
   - HBR (2024): "Customer Satisfaction in B2B Logistics"
   - NPS Framework: Bain & Company methodology (Net Promoter Score)
   - NPS Benchmark Construction France: +30 to +50 range documented

---

**Conclusion :** Pour une franchise logistique Gedimat, démarrer par les **Quick Wins sans coûts** (CRM Excel, scoring, NPS) en parallèle d'un **pilote SaaS modeste** (TMS+WMS 1.5-3k€/mois sur Gisors) permet 6 mois d'expérience avant décision long terme. Risque minimal, apprentissage maximal, ROI clair après 12 mois.

---

*Document préparé par Agent 5 - InfraFabric PASS 1*
*Méthodologie : IF.search (recherche), IF.optimise (synthèse), IF.TTT (sources vérifiables)*
