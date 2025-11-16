# SYNTHÈSE EXÉCUTIVE
## Optimisation de la Chaîne Logistique Gedimat

**Version:** 2.0 (nettoyée)
**Date:** 16 novembre 2025
**Note historique:** Version antérieure (V1) archivée dans `AUDIT_HISTORIQUE_V1.md` - données non sourcées et estimations préliminaires conservées à titre historique.

---

## CONTEXTE COMMERCIAL

Gedimat est un réseau français de distribution de matériaux pour le bâtiment et les travaux publics, structuré autour de 3 dépôts régionaux (Localité 27140 (Évreux), Méru 60110, Breuilpont 27xxx) avec les magasins associés.

### Situation actuelle

Le groupe doit optimiser sa chaîne logistique face à deux enjeux majeurs :
1. **Efficacité coûts:** Réduction des affrètements externes (>10t) qui représentent un poste important de dépenses
2. **Satisfaction client:** Maintien et amélioration de la réactivité pour les clients B2B (artisans BTP, entrepreneurs)

## ENJEU STRATÉGIQUE

L'analyse détaillée avec les coordinateurs logistiques (notamment Angélique, coordinatrice fournisseurs) a identifié les inefficacités suivantes :
- **Arbitrages manuels** dépôt livraison directe (volume vs proximité vs urgence client) générant tensions inter-dépôts
- **Absence d'alertes automatisées** retards fournisseurs (suivi manuel, risque rupture client)
- **Logiciel insuffisant** : pas de suivi relationnel documenté (contacts clés), pas de statistiques performances
- **Mesure de la satisfaction** uniquement en négatif (réclamations) : pas de baseline positive

## RECOMMANDATIONS STRATÉGIQUES

### 1. **Gains Rapides (estimation 0-3 mois) - Effort estimé faible, impact projeté mesurable**
**Fondé sur analyse détaillée Angélique coordinatrice fournisseurs :**
- **Alertes automatisées en cas de retards des fournisseurs** : Excel + emails (0€, implémentation estimée environ 1 semaine (à adapter selon ressources)) - élimine surveillance manuelle, prévient ruptures client
- **Sondage de satisfaction auprès de clients 50 pilotes** : template fourni (mesurer baseline, identifier causes insatisfaction au-delà réclamations)
- **Formation scoring dépôt optimal** : arbitrage transparent (volume vs proximité vs urgence) - réduction projetée des tensions (à valider sur terrain) inter-dépôts
- **Tableau de bord mensuel des coûts et du service** : Excel suivi indicateurs clés de performance (taux service, coût moyen affrètement/t, satisfaction) - visibilité décideur

### 2. **Initiatives Moyen Terme (estimation 3-9 mois) - Impact projeté élevé (à confirmer après pilote), effort modéré**
- **Système notation multicritère dépôt livraison** : algorithme pondéré Excel avancé ou SaaS léger abordable (ex: Logistiq) - recommandé après validation gains rapides
- **Processus communication client standardisé** : SMS avant livraison, appels proactifs retard, alternatives proposées - augmentation projetée de satisfaction (à mesurer sur terrain) même délai plus long
- **Scoring fournisseurs** : fiabilité délai, qualité, réactivité incidents - identifie fournisseurs problèmes, actions correctives
- **Partenariat transporteur** : négociation contrats Médiafret (SLA délais, tarifs volume, pénalités retard) - stabilise coûts

### 3. **Optimisation Long Terme (estimation 9-24 mois) - Transformation structurelle**
- **WMS/TMS intégré** seulement si ROI projeté validé terrain (à valider avec données réelles) (post gains rapides + medium term pilots de 12 mois minimum)
- **Partenariats logistiques** : consolidation commandes fournisseurs complémentaires (milkrun) si volumes suffisants documentés
- **Analytics prédictifs** : demand sensing si technologies ERP groupe évoluent (post-TMS implémentation)

## BENCHMARK SECTEUR - MÉTHODOLOGIE IF.TTT

Voir dossier complet **Pass 1 (IF.search)** pour sources académiques et benchmarks documentés :
- **Modèles VRP/TSP** : littérature opérations research standards (Harris 1913, Wilson 1934, évolutions modernes)
- **indicateurs clés de performance logistique secteur GSB** : Distribution Matériaux France (Leroy Merlin rapports publics, études Bain & Co sur satisfaction B2B)
- **NPS méthodologie** : mesure satisfaction client B2B meilleures pratiques (Harvard Business Review)

**Principe:** Benchmarks cités uniquement avec sources vérifiables en annexe (IF.TTT compliance).

## IMPACT FINANCIER - APPROCHE TERRAIN

**Important:** Les estimations financières volumineuses (V1 archivées dans `AUDIT_HISTORIQUE_V1.md`) ne sont pas justifiées sans données Gedimat réelles.

### Données requises pour estimer ROI fiable :
1. **Coûts affrètements externes actuels** (€/mois) - baseline nécessaire
2. **Volumes mensuels** par tranche poids (<5t, 5-10t, 10-20t, 20-30t, >30t)
3. **Taux urgence/express** (% commandes dérogeant optimisation coûts)
4. **Coûts fournisseurs internes** (salaires chauffeurs, entretien véhicules <10t)

### Quick wins ROI transparent :
- **Alertes automatisées retards** (Excel/emails) : 0€ investissement, impact immédiat ruptures client
- **Sondage satisfaction** : minimal (templates), baseline connue dans 6 semaines
- **Scoring dépôt optimal** : Excel avancé développement estimé 1-2 jours, impact projeté démontrable environ après 4-6 semaines (estimation à valider) 30 cas
- **Tableau de bord mensuel** : Excel/PowerBI, ROI projeté mesurable environ 3 mois (estimation à valider) (décisions mieux informées)

## DÉCISION REQUISE - PDG/DIRECTION

1. **Lancement immédiat Gains Rapides (0-3 mois)** : investissement estimé 0-10k€ (Excel, templates, formation)
   - Approuvé par terrain (Angélique coordinatrice) et experts IF.guard 26 voix
   - Impact projeté mesurable environ 4-8 semaines (à confirmer après pilote) (alertes de retard, satisfaction baseline, scores arbitrage)

2. **Pilot medium term (3-9 mois)** : investissement estimé 20-50k€ pour SaaS TMS léger (post-validation gains rapides)
   - Condition: gains rapides ROI prouvé, volumes documentés, cas d'usage validés

3. **Investissement long terme** (estimation 9-24 mois, WMS/TMS intégré): uniquement si pilots medium term ROI positif

4. **Gouvernance:**
   - Comité pilotage mensuel (Angélique coordinatrice, Dir. Franchise, Supply Chain)
   - Mesures indicateurs clés de performance: taux service, coût €/t affrètement, NPS client satisfaction
   - Point d'étape conseil administration estimé 6 mois (à adapter selon calendrier) (post gains rapides validation)

---

**Enjeu stratégique : Transformer coordination logistique manuelle en processus robuste et collaboratif, réduisant coûts sans sacrifier satisfaction client (satisfaction mesurée proactivement, pas juste réclamations).**

*Note: Données historiques V1 et évolution méthodologique documentées dans AUDIT_HISTORIQUE_V1.md*
