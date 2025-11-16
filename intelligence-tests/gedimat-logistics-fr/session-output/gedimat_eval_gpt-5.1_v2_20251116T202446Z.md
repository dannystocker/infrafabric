## Scores
- Conformité IF.TTT: **88/100**
- Qualité des preuves: **87/100**
- Méthodologie (IF.search, structure): **95/100**
- Actionnabilité pour Gedimat: **92/100**
- Qualité du français: **92/100**
- **GLOBAL: 90/100**

## Écart vers 95%
- Score actuel estimé: **90/100**
- Écart vers 95: **5 points**
- Bloqueurs prioritaires:
  - Benchmarks externes (Point P, Leroy Merlin, Castorama) non vérifiables dans cet environnement (CAPTCHA/404) → citations à considérer comme **non confirmées**.
  - Quelques projections opérationnelles Gedimat non sourcées ou non explicitement balisées comme hypothèses (par ex. « retard client -50 % », « affrètement -12‑15 % », fourchettes de coût WMS) dans `PROMPT_V2_FACTUAL_GROUNDED.md:553-559` et `PROMPT_V2_FACTUAL_GROUNDED.md:661-665`.
  - Légère incohérence des sources évoquées pour l’NPS Castorama (Kingfisher vs TNS Sofres) et absence d’URL concrètes pour Point P.

---

## Violations Trouvées

### A. Projections non sourcées (CRITIQUE)

1. 
- Emplacement: `intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md:553-559`  
- Affirmations:
  - « 1. Quick Win (30 jours): Alertes fournisseur (impact: retard client -50%, coût: <1K€) »
  - « 2. Moyen Terme (90j): Scoring dépôt optimal (impact: affrètement -12-15% si calibration réussie, coût: 5K€) »
  - « 3. Long Terme (6-12m): WMS + analytics (impact: structurel, coût: 20-50K€ selon solution) »
- Problème:
  - Les réductions **-50 % des retards** et **-12‑15 % d’affrètement** sont présentées comme effets attendus Gedimat, sans lien explicite avec un benchmark sourcé ni avec des données historiques Gedimat.
  - Les coûts « <1K€ », « 5K€ », « 20‑50K€ » sont des ordres de grandeur plausibles mais non rattachés à des devis, fournisseurs ou cas documentés.
- Correction proposée:
  - Re-formuler clairement comme scénarios hypothétiques:
    - Par exemple: « impact potentiel (à confirmer après pilote) » au lieu de chiffres durs.
    - Remplacer « -50 % » et « -12‑15 % » par « réduction mesurable des retards / des coûts d’affrètement, à calibrer sur données 2024 ».
  - Associer chaque coût à une source:
    - Devis WMS/TMS (SAP, Generix, Divalto) ou fourchette publique, citée précisément (URL ou document interne).

2. 
- Emplacement: `intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md:661-665`  
- Affirmation: « Coût: 30-80K€ (solution SAP, Generix, Divalto) » pour un WMS/TMS intégré ERP Gedimat.
- Problème:
  - Fourchette très large mais sans référence explicite à des offres commerciales ou à un comparatif indépendant.
  - Pour un PDG, cela reste une projection de budget d’investissement non sourcée.
- Correction:
  - Citer au moins une offre réelle (ou un livre blanc fournisseur) avec fourchette de prix.
  - Ou reformuler: « Budget indicatif à confirmer par consultation fournisseurs (ordre de grandeur 30–80 k€ selon solution retenue). »

3. 
- Emplacement: `intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md:36`  
- Affirmation: « Angélique peut remplir formulaires et calculer son propre ROI en 30 minutes. »
- Problème:
  - Le temps « 30 minutes » est une estimation implicite sans test utilisateur documenté.
- Correction:
  - Reformuler en « moins d’une heure dans un premier test » ou retirer le chiffre précis tant qu’un test n’a pas été chronométré.

4. (héritage v1, bien traités mais à surveiller)  
- Les anciens chiffres **50K€ gains**, **5K€ investissement**, **10× ROI**, **30K€ / 120K€ affrètement**, **88 % taux de service**, **35 NPS**, **6,5 % coût logistique** sont désormais cantonnés à des tableaux de comparaison « v1 → v2 » et explicitement marqués comme éliminés (`PROMPT_V2_FACTUAL_GROUNDED.md:14-16`, `PROMPT_V2_FACTUAL_GROUNDED.md:1030-1033`).  
- Point positif: ils ne figurent plus comme projections actives, mais il serait plus sûr de les retirer totalement des sections orientées « livrable final » ou de les déplacer en annexe « histoire de la révision ».

---

### B. Benchmarks externes (CRITIQUE)

1. **Point P 2022 – 12 % de réduction affrètement**

- Emplacement (références dans le projet):  
  - Cas comparatif: `PROMPT_V2_FACTUAL_GROUNDED.md:840-843`  
  - Mentions plus générales: `LAUNCH_V2_INSTRUCTIONS.md:33`, `README_EVALUATION.md:80`  
- Source prétendue: « LSA Conso, Mars 2023, “Optimisation Multi‑Dépôt Distribution Matériaux” ».
- URL fournie: aucune URL précise dans les fichiers; seule la revue est citée.
- Vérification (environnement CLI sans navigateur graphique):
  - Tentatives via DuckDuckGo/Google (`curl`): blocage systématique par CAPTCHA/JS anti‑bot → aucune page de résultats lisible.
  - Impossible d’accéder à un PDF LSA Conso sans compte / interface web complète.
- Conclusion: **non vérifiable dans cet environnement**. On ne peut ni confirmer l’existence de l’article ni la valeur « 12 % ».
- Recommandation:
  - Ajouter une référence bibliographique complète (titre exact, numéro, pages, éventuellement DOI ou URL courte).
  - Prévoir une vérification manuelle par un humain avec navigateur, puis consigner le résultat (par ex. dans `AUDIT_UNSOURCED_NUMBERS.md`).
  - En attendant, formuler: « Étude LSA Conso (référence à vérifier) » et ne pas présenter « 12 % » comme vérité dure.

2. **Leroy Merlin 2021 – ROI 8,5×**

- Emplacements:
  - Tableau benchmark: `GEDIMAT_ENHANCEMENT_PROMPT.md:120-132`
  - Dans PROMPT V2:
    - Taux de service / NPS: `PROMPT_V2_FACTUAL_GROUNDED.md:226`
    - Cas détaillé: `PROMPT_V2_FACTUAL_GROUNDED.md:845-848`
- Source prétendue:
  - Rapport Annuel Leroy Merlin 2023, p.67, « Initiatives Logistiques 2021‑2023 ».
- URL utilisée: `https://www.leroymerlin.fr/rapport-annuel-2023.pdf`.
- Vérification:
  - Téléchargement via `curl` → page HTML Cloudflare demandant d’activer JS/cookies (fichier identifié comme HTML par `file`).
  - `pdftotext` échoue car le fichier n’est pas un PDF.
  - Sans navigateur complet, impossible d’atteindre le vrai rapport ni de chercher « ROI 8,5× » ou les pourcentages affichés.
- Conclusion: **benchmark plausible mais non confirmé**.
- Recommandation:
  - Lorsqu’un humain peut accéder au site, télécharger le PDF et confirmer:
    - L’existence d’un ROI 8,5× lié à un projet de dashboard logistique.
    - La cohérence des valeurs « taux de service 94,2 % » et « NPS 52 ».
  - Sans cette vérification, présenter ces chiffres comme **exemple inspiré** plutôt que cas documenté.

3. **Castorama 2023 – NPS 47**

- Emplacements:
  - Benchmarks agrégés: `PROMPT_V2_FACTUAL_GROUNDED.md:228, 398, 596`
  - Cas détaillé: `PROMPT_V2_FACTUAL_GROUNDED.md:850-853`
  - Références d’évaluation: `README_EVALUATION.md:82`, `GEDIMAT_ENHANCEMENT_PROMPT.md:129-135`
- Sources prétendues:
  - Tantôt « Kingfisher Annual Report 2023, p.45 », tantôt « étude TNS Sofres Pro 2023 ».
- URLs:
  - `https://www.kingfisher.com/investors/annual-report-2023` renvoie un « Page not found – Kingfisher plc » (HTML 404).
  - Aucun lien direct vers la supposée étude TNS Sofres.
- Vérification:
  - Impossible de récupérer un rapport 2023 Kingfisher sans navigation JS.
  - Pas de trace accessible de l’étude TNS dans cet environnement.
- Conclusion: citation non vérifiable et source incohérente (Kingfisher vs TNS).
- Recommandation:
  - Choisir une seule source principale, documentée: soit Kingfisher (si réellement publié), soit l’étude TNS, avec références complètes.
  - Tant que ce n’est pas confirmé, présenter le « NPS ~47 » comme fourchette sectorielle (« NPS autour de 45–50 selon études Kingfisher/TNS 2023 ») plutôt que chiffre précis.

---

### C. Qualité du français (CRITIQUE pour présentation C‑suite)

Globalement, le français est très bon (syntaxe solide, registre professionnel, lexique métier pertinent). Quelques points à corriger pour un Conseil d’administration exigeant:

1. **Anglicismes**

- Emplacement: `PROMPT_V2_FACTUAL_GROUNDED.md:119`  
  - « KPI logistiques B2B »  
  - Suggestion: « indicateurs de performance logistique B2B ».
- Emplacement: `PROMPT_V2_FACTUAL_GROUNDED.md:845`  
  - « Dashboard alertes, ROI 8.5× »  
  - Suggestion: « tableau de bord d’alertes, retour sur investissement (ROI) 8,5× ».
- Emplacement: `PROMPT_V2_FACTUAL_GROUNDED.md:556`  
  - « Quick Win (30 jours) »  
  - Suggestion: « levier rapide à fort impact (30 jours) » ou « action rapide ».
- Acronymes:
  - « ROI » et « NPS » sont acceptables, mais il serait préférable de les définir une fois (« retour sur investissement (ROI) », « Net Promoter Score (NPS) »).

2. **Grammaire / micro‑style**

- Emplacement: `PROMPT_V2_FACTUAL_GROUNDED.md:36`  
  - « Angélique peut remplir formulaires… » → manque l’article.  
  - Correction: « Angélique peut remplir les formulaires et calculer son propre ROI en 30 minutes. »
- Emplacement: `LAUNCH_V2_INSTRUCTIONS.md` (plusieurs passages)  
  - Style parfois très oral (« c’est un dossier français pour client français »). Dans un Board Pack, un ton légèrement plus neutre serait préférable.
- Phrases longues:
  - Certaines phrases enchaînent plusieurs propositions et parenthèses; pour la présentation CA, il serait utile de segmenter en phrases plus courtes dans la synthèse exécutive (1 page).

3. **Registre et clarté**

- Le corps du dossier est d’un très bon niveau; la synthèse exécutive peut encore gagner en impact:
  - 3–5 bullet points, chacun « 1 phrase courte + 1 chiffre clé sourcé ».
- Les références à l’architecture IF.* (40 agents, 26 voix, Académie Française) pourraient être allégées ou renvoyées en annexe dans le document Board.

---

## Benchmarks vérifiés (ou non) – Synthèse

- Point P: ⚠️ Non vérifiable (LSA Conso bloqué par CAPTCHA; aucun PDF accessible).
- Leroy Merlin: ⚠️ Non vérifiable (Cloudflare + absence de PDF accessible en CLI).
- Castorama / Kingfisher / TNS: ⚠️ Non vérifiable (404 + pas d’accès direct aux études).

Dans l’état, ces benchmarks doivent être traités comme hypothèses plausibles plutôt que preuves formelles.

---

## Code Fonctionnel

### 1. Macro Excel VBA – Scoring multicritère dépôt optimal

```vba
Option Explicit

Function ScoreDepot(Volume As Double, Distance As Double, Delai As Double, Priorite As String) As Double
    Dim wUrg As Double, wCout As Double, wVol As Double, wDist As Double
    Dim fUrg As Double, fCout As Double, fVol As Double, fDist As Double
    wUrg = 0.4: wCout = 0.3: wVol = 0.2: wDist = 0.1
    Priorite = UCase(Trim(Priorite))
    If Priorite = "URGENT" Then
        fUrg = 1
    ElseIf Priorite = "NORMAL" Then
        fUrg = 0.6
    Else
        fUrg = 0.3
    End If
    fDist = 1 / (1 + Distance / 100)
    fVol = 1 / (1 + Volume / 20)
    fCout = 1 / (1 + Delai / 24)
    ScoreDepot = wUrg * fUrg + wCout * fCout + wVol * fVol + wDist * fDist
End Function

Function DepotOptimal(Volume As Double, DistLieu As Double, DistMeru As Double, DistBreuil As Double, _
                      Delai As Double, Priorite As String) As String
    Dim noms(1 To 3) As String, scores(1 To 3) As Double
    Dim i As Integer, best As Integer
    noms(1) = "Lieu": noms(2) = "Méru": noms(3) = "Breuilpont"
    scores(1) = ScoreDepot(Volume, DistLieu, Delai, Priorite)
    scores(2) = ScoreDepot(Volume, DistMeru, Delai, Priorite)
    scores(3) = ScoreDepot(Volume, DistBreuil, Delai, Priorite)
    best = 1
    For i = 2 To 3
        If scores(i) > scores(best) Then best = i
    Next i
    DepotOptimal = noms(best) & " (score " & Format(scores(best), "0.00") & ")"
End Function
```

### 2. Script Python – Analyse Sondage NPS

```python
import pandas as pd

def calculer_nps(fichier_csv: str) -> dict:
    df = pd.read_csv(fichier_csv)
    notes = df["note"].dropna().astype(int)
    n = len(notes)
    if n == 0:
        return {
            "nps": 0.0,
            "promoteurs_pct": 0.0,
            "passifs_pct": 0.0,
            "detracteurs_pct": 0.0,
        }
    promoteurs = (notes >= 9).sum()
    passifs = ((notes >= 7) & (notes <= 8)).sum()
    detracteurs = (notes <= 6).sum()

    to_pct = lambda x: 100.0 * x / n
    return {
        "nps": to_pct(promoteurs) - to_pct(detracteurs),
        "promoteurs_pct": to_pct(promoteurs),
        "passifs_pct": to_pct(passifs),
        "detracteurs_pct": to_pct(detracteurs),
    }

if __name__ == "__main__":
    import sys, pprint
    pprint.pp(calculer_nps(sys.argv[1]))
```

### 3. Requête SQL – Baseline factures Médiafret (Q1–Q3 2024)

```sql
WITH factures_2024 AS (
    SELECT
        date,
        montant,
        tonnage
    FROM factures
    WHERE date >= DATE '2024-01-01'
      AND date <  DATE '2024-10-01'
),
mensuel AS (
    SELECT
        DATE_TRUNC('month', date) AS mois,
        SUM(montant)              AS cout_total,
        SUM(tonnage)              AS tonnage_total,
        CASE WHEN SUM(tonnage) > 0
             THEN SUM(montant) / SUM(tonnage)
             ELSE NULL END       AS cout_par_tonne
    FROM factures_2024
    GROUP BY DATE_TRUNC('month', date)
)
SELECT
    mois,
    cout_total,
    tonnage_total,
    cout_par_tonne
FROM mensuel
ORDER BY mois;
```

---

## Chemin vers 95%+

### Priorité 1 (bloque déploiement Board)

1. **Vérifier / recadrer les benchmarks externes**
   - Impact: -3 à -4 points (Conformité IF.TTT + Qualité preuves).
   - Action: vérifier manuellement les rapports LSA, Leroy Merlin, Kingfisher ou reformuler les chiffres comme plages indicatives / hypothèses, en l’absence de preuve.

2. **Nettoyer les projections Gedimat restantes**
   - Impact: -2 points.
   - Action: transformer tous les pourcentages et montants Gedimat non testés (« -50 % retards », « -12‑15 % affrètement », coûts WMS) en objectifs à mesurer, reliés à des formulaires de collecte et à la requête SQL ci‑dessus.

### Priorité 2 (requis pour 95%)

1. Documenter explicitement les tests utilisateurs (temps réel pour remplir les formulaires, calcul ROI).
2. Simplifier et franciser la synthèse exécutive 1 page (moins de jargon IF.*, plus de chiffres sourcés et lisibles).

### Priorité 3 (polish 98%+)

1. Harmoniser le style (éviter « KPI », « dashboard », « quick win » dans le document Board).
2. Ajouter une annexe « Traçabilité IF.TTT » listant, pour chaque chiffre clé, la source exacte ou la formule de calcul.

---

## Verdict

- Prêt pour déploiement vers nouvelle session Claude Code Cloud ?
  - ☐ OUI – Aucun changement requis  
  - ☑ OUI AVEC CORRECTIONS – Appliquer les fixes ci-dessus d’abord  
  - ☐ NON – Bloqueurs critiques non résolus  

**Bloqueurs critiques si présentation CA immédiate:**

1. Benchmarks externes non vérifiés et difficilement auditables dans l’état (URLs non accessibles en environnement standard sans navigateur).
2. Quelques projections chiffrées Gedimat encore formulées comme résultats attendus plutôt que comme hypothèses à tester.

---

## Confiance Évaluation

- ☑ MOYENNE – Quelques réserves liées à l’impossibilité de vérifier les sources (CAPTCHA, 404).

**Justification:**  
- Lecture détaillée de `PROMPT_V2_FACTUAL_GROUNDED.md`, des audits (`AUDIT_UNSOURCED_NUMBERS.md`, `QUICK_REFERENCE_UNSOURCED_CLAIMS.md`) et des instructions de lancement V2 montre une amélioration majeure par rapport à v1 (élimination des gros chiffres inventés, ajout de formulaires et de méthodologies de calcul).  
- Cependant, l’impossibilité de confirmer les chiffres clés des benchmarks externes et la présence de quelques projections chiffrées Gedimat non explicitement balisées comme hypothèses empêchent de monter au‑delà de ~90/100 sans travail complémentaire.

