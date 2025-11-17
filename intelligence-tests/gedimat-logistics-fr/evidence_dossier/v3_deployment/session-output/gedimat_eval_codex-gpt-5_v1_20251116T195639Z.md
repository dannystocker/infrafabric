## Scores
- Conformité IF.TTT: 78/100 (formules présentes mais coûts >5K€ restent déclaratifs sans preuve)
- Qualité preuves: 70/100 (citations textuelles, aucun lien testable ni capture)
- Méthodologie: 86/100 (architecture IF.search cohérente, formulaires prêts)
- Actionnabilité: 82/100 (checklists et gabarits fournis mais il manque données réelles)
- Qualité français: 72/100 (plusieurs anglicismes et tournures anglo-saxonnes persistantes)
- **GLOBAL: 78/100**

## Écart vers 95%
- Score actuel estimé: 78/100
- Écart: 17 points
- Bloqueurs prioritaires: benchmarks externes impossibles à vérifier, budgets/ROI encore posés sans rattachement aux données Gedimat, anglicismes visibles en synthèse PDG.

## Violations Trouvées

### A. Projections non sourcées (CRITIQUE)
1. Emplacement: `infrafabric/intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md:556-558`  
   Affirmation: "Quick Win (coût <1K€), scoring dépôt (coût 5K€), WMS + analytics (coût 20-50K€)"  
   Problème: montants >5K€ publiés dans la synthèse exécutive sans lien vers factures, offres éditeurs ou formules paramétrées → un décideur pourra les prendre pour des engagements financiers.  
   Correction: remplacer ces nombres par champs calculés (ex: `Coût = [Jours dev] × TJM`), pointer vers offres concrètes (devis Generix/Divalto) ou indiquer explicitement "À confirmer via RFP".

2. Emplacement: `infrafabric/intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md:637` et `:663`  
   Affirmation: "Dev scoring externe 15-20K€, macro Excel 5K€, WMS/TMS 30-80K€"  
   Problème: absence totale de source (contrat, URL fournisseurs, attestation Angélique), alors que ces montants dimensionnent les ROI et les décisions d’investissement.  
   Correction: lier chaque valeur à (a) devis daté ou (b) formule `nombre de jours × coût journalier`, puis stocker la preuve dans l’annexe audit avec référence commit/Git.

### B. Benchmarks externes (CRITIQUE)
- **Point P 2022 (12% réduction)**  
  - Source prétendue: LSA Conso Mars 2023, p.34  
  - URL fournie: aucune URL ni PDF dans `PROMPT_V2_FACTUAL_GROUNDED.md:574-581`  
  - VÉRIFICATION: ❌ Introuvable (LSA Conso protégé par Captcha, aucune capture/notice locale à partager)  
  - Source alternative française suggérée: publier un extrait du « Rapport Annuel Saint-Gobain Distribution Bâtiment France 2022 » ou d’un communiqué LSA accessible, avec URL officielle (rubrique Actualités Saint-Gobain: https://www.saint-gobain.com/fr/actualites).

- **Leroy Merlin 2021 (ROI 8.5×)**  
  - Source: Rapport annuel 2023 p.67 + Supply Chain Magazine Juin 2022  
  - VÉRIFICATION: ⚠️ Non vérifiable (aucun hyperlien, pas de référence ADEO officielle, Supply Chain Magazine payant)  
  - Correction: intégrer le lien public vers le rapport annuel ADEO/Adeo URD 2021 (portail publications ADEO) et préciser page/table figurant le ROI; sinon citer un article libre (ex. Supply Chain Magazine n°365 via https://www.supplychainmagazine.fr s’il est accessible).

- **Castorama 2023 (NPS 47)**  
  - Source: Kingfisher 2023 Rapport RSE + "Internal Analytics 2023"  
  - VÉRIFICATION: ❌ "Internal Analytics" est invérifiable, et aucun lien Kingfisher n’est fourni (section `PROMPT_V2…:587-590`)  
  - Correction: pointer vers « Kingfisher plc Annual Report 2022/23 » ou « Responsible Business Report 2023 » téléchargeable depuis https://www.kingfisher.com/investors/results-reports-and-presentations, citer la page NPS, supprimer la mention “Internal Analytics” tant qu’un document partagé n’existe pas.

### C. Qualité français (CRITIQUE pour présentation C-suite)
- Anglicismes trouvés:  
  - `infrafabric/intelligence-tests/gedimat-logistics-fr/PROMPT_V2_FACTUAL_GROUNDED.md:119` — « KPI logistiques » → proposer « indicateurs clés de performance ».  
  - `infrafabric/.../PROMPT_V2_FACTUAL_GROUNDED.md:252` et `:583` — « dashboard alertes » → « tableau de bord d’alertes ».  
  - `infrafabric/.../PROMPT_V2_FACTUAL_GROUNDED.md:556` — « Quick Win » → « gain rapide » / « levier immédiat ».  
- Fautes de grammaire détectées: pas d’erreur bloquante, mais plusieurs phrases mixtes franglais (« Dashboard alertes automatisées ») nuisent à la crédibilité.  
- Ton inapproprié: la synthèse PDG demeure prescriptive (“Quick Win”/“Long Terme”) sans modalisation; préférer « Priorité courte », « Investissement long terme » pour coller au ton Conseil d’administration.

## Code Fonctionnel

### 1. Macro Excel VBA: Scoring Multicritère Dépôt Optimal
```vba
Option Explicit

Public Sub CalculerDepotOptimal()
    Dim wsCmd As Worksheet, wsDepots As Worksheet
    Dim lastCmd As Long, lastDepot As Long
    Dim i As Long, j As Long
    Dim volume As Double, distanceKm As Double, delaiH As Double
    Dim priorite As String, score As Double
    Dim meilleurDepot As String, meilleurScore As Double

    Set wsCmd = ThisWorkbook.Worksheets("Commandes")
    Set wsDepots = ThisWorkbook.Worksheets("Depots")

    lastCmd = wsCmd.Cells(wsCmd.Rows.Count, "A").End(xlUp).Row
    lastDepot = wsDepots.Cells(wsDepots.Rows.Count, "A").End(xlUp).Row

    For i = 2 To lastCmd
        If Application.CountA(wsCmd.Cells(i, "C").Resize(1, 4)) = 4 Then
            volume = wsCmd.Cells(i, "C").Value
            distanceKm = wsCmd.Cells(i, "D").Value
            delaiH = wsCmd.Cells(i, "E").Value
            priorite = wsCmd.Cells(i, "F").Value

            meilleurScore = -1
            meilleurDepot = ""

            For j = 2 To lastDepot
                score = ScoreDepot(volume, distanceKm, delaiH, priorite, wsDepots, j)
                If score > meilleurScore Then
                    meilleurScore = score
                    meilleurDepot = wsDepots.Cells(j, "A").Value
                End If
            Next j

            wsCmd.Cells(i, "G").Value = meilleurDepot
            wsCmd.Cells(i, "H").Value = Round(meilleurScore, 3)
            ConsommerCapacite wsDepots, meilleurDepot, volume
        End If
    Next i
End Sub

Private Function ScoreDepot(volume As Double, distanceKm As Double, delaiH As Double, _
                             priorite As String, wsDepots As Worksheet, depotRow As Long) As Double
    Dim rayonMax As Double, capaciteMax As Double, chargePlanifiee As Double, prepHeures As Double
    Dim distanceScore As Double, chargeScore As Double, urgenceScore As Double, facteurPriorite As Double

    rayonMax = wsDepots.Cells(depotRow, "B").Value
    capaciteMax = wsDepots.Cells(depotRow, "C").Value
    chargePlanifiee = wsDepots.Cells(depotRow, "D").Value
    prepHeures = wsDepots.Cells(depotRow, "E").Value

    If rayonMax > 0 Then
        distanceScore = Application.Max(0#, 1# - (distanceKm / rayonMax))
    Else
        distanceScore = 0#
    End If

    If capaciteMax > 0 Then
        chargeScore = Application.Max(0#, 1# - ((chargePlanifiee + volume) / capaciteMax))
    Else
        chargeScore = 0#
    End If

    If delaiH <= 0 Then delaiH = 1#
    urgenceScore = Application.Max(0#, 1# - Application.Max(0#, (prepHeures - delaiH) / delaiH))

    Select Case LCase$(priorite)
        Case "critique": facteurPriorite = 1.15
        Case "urgent":   facteurPriorite = 1#
        Case Else:      facteurPriorite = 0.9
    End Select

    ScoreDepot = facteurPriorite * (0.35 * distanceScore + 0.25 * chargeScore + 0.4 * urgenceScore)
End Function

Private Sub ConsommerCapacite(wsDepots As Worksheet, depotNom As String, volume As Double)
    Dim lastDepot As Long, r As Long
    lastDepot = wsDepots.Cells(wsDepots.Rows.Count, "A").End(xlUp).Row

    For r = 2 To lastDepot
        If wsDepots.Cells(r, "A").Value = depotNom Then
            wsDepots.Cells(r, "D").Value = wsDepots.Cells(r, "D").Value + volume
            Exit For
        End If
    Next r
End Sub
```
_Prérequis_: feuilles `Commandes` (col C=Tonnes, D=Distance km au chantier, E=heures avant livraison, F=priorité) et `Depots` (A=Nom, B=rayon maximal, C=capacité totale, D=charge déjà planifiée, E=heures de préparation).

### 2. Script Python: Analyse Sondage NPS
```python
#!/usr/bin/env python3
"""
Analyse un CSV de réponses NPS et génère les pourcentages + score global ou par segment.
Colonnes attendues : "note" (0-10) et, optionnellement, un champ segment (ex: "region").
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calcule le NPS et les répartitions Promoteurs/Passifs/Détracteurs.")
    parser.add_argument("fichier", type=Path, help="CSV exporté (UTF-8) du sondage Gedimat.")
    parser.add_argument("--segment", help="Nom de la colonne utilisée pour segmenter (ex: depot, zone).")
    parser.add_argument("--export", type=Path, help="Chemin d’export CSV pour les indicateurs.")
    return parser.parse_args()


def bucket(note: float) -> str:
    if note >= 9:
        return "promoteurs"
    if note >= 7:
        return "passifs"
    return "detracteurs"


def lire_reponses(fichier: Path, segment_col: str | None):
    compteur_global = Counter()
    segments: Dict[str, Counter] = defaultdict(Counter)
    notes_par_segment: Dict[str, List[float]] = defaultdict(list)

    with fichier.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            brute = row.get("note") or row.get("Note")
            if brute is None or brute == "":
                continue
            note = float(str(brute).replace(",", "."))
            classe = bucket(note)
            compteur_global[classe] += 1

            if segment_col:
                cle = row.get(segment_col, "INDETERMINE")
                segments[cle][classe] += 1
                notes_par_segment[cle].append(note)

    return compteur_global, segments, notes_par_segment


def score_nps(compteur: Counter) -> float | None:
    total = sum(compteur.values())
    if total == 0:
        return None
    return ((compteur["promoteurs"] - compteur["detracteurs"]) / total) * 100


def formatter_resultats(compteur_global, segments, notes_par_segment):
    def ratios(compteur: Counter):
        total = sum(compteur.values())
        if total == 0:
            return 0, 0, 0
        return (
            compteur["promoteurs"] / total * 100,
            compteur["passifs"] / total * 100,
            compteur["detracteurs"] / total * 100,
        )

    global_nps = score_nps(compteur_global)
    prom, passif, detr = ratios(compteur_global)
    print(f"NPS global: {global_nps:.1f} (Promoteurs {prom:.1f} %, Passifs {passif:.1f} %, Détracteurs {detr:.1f} %)")

    for segment, compteur in segments.items():
        nps_segment = score_nps(compteur)
        prom, passif, detr = ratios(compteur)
        print(f"- {segment}: NPS {nps_segment:.1f} | +{prom:.1f}% / ={passif:.1f}% / -{detr:.1f}% | Réponses: {sum(compteur.values())}")


def ecrire_export(export_path: Path, compteur_global, segments):
    rows = [{
        "segment": "GLOBAL",
        "nps": f"{score_nps(compteur_global):.1f}",
        "promoteurs_pct": "",
        "passifs_pct": "",
        "detracteurs_pct": ""
    }]
    for segment, compteur in segments.items():
        total = sum(compteur.values())
        rows.append({
            "segment": segment,
            "nps": f"{score_nps(compteur):.1f}" if total else "",
            "promoteurs_pct": f"{compteur['promoteurs']/total*100:.1f}" if total else "",
            "passifs_pct": f"{compteur['passifs']/total*100:.1f}" if total else "",
            "detracteurs_pct": f"{compteur['detracteurs']/total*100:.1f}" if total else "",
        })

    with export_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main():
    args = parse_args()
    compteur_global, segments, notes_par_segment = lire_reponses(args.fichier, args.segment)
    formatter_resultats(compteur_global, segments, notes_par_segment)
    if args.export:
        ecrire_export(args.export, compteur_global, segments)


if __name__ == "__main__":
    main()
```

### 3. Requête SQL: Baseline Factures Médiafret
```sql
WITH factures AS (
    SELECT
        invoice_id,
        invoice_date::date AS date_facture,
        montant_eur,
        tonnage_t,
        route
    FROM factures_mediafret
    WHERE invoice_date >= DATE '2024-01-01'
      AND invoice_date <  DATE '2024-10-01'
),
mensuel AS (
    SELECT
        date_trunc('month', date_facture) AS mois,
        SUM(montant_eur) AS cout_mensuel_eur,
        SUM(tonnage_t) AS tonnage_mensuel
    FROM factures
    GROUP BY 1
),
enrichi AS (
    SELECT
        mois,
        cout_mensuel_eur,
        tonnage_mensuel,
        CASE WHEN tonnage_mensuel > 0 THEN cout_mensuel_eur / tonnage_mensuel END AS cout_par_tonne,
        date_trunc('quarter', mois) AS trimestre
    FROM mensuel
),
trimestriel AS (
    SELECT
        trimestre,
        SUM(cout_mensuel_eur) AS cout_total,
        SUM(tonnage_mensuel) AS tonnage_total,
        AVG(cout_par_tonne) AS cout_par_tonne_moyen
    FROM enrichi
    GROUP BY 1
)
SELECT
    to_char(mois, 'YYYY-MM') AS periode,
    cout_mensuel_eur,
    tonnage_mensuel,
    round(cout_par_tonne, 2) AS cout_par_tonne_eur,
    to_char(trimestre, '"T"Q YYYY') AS trimestre
FROM enrichi
UNION ALL
SELECT
    'TOTAL ' || to_char(trimestre, '"T"Q YYYY'),
    cout_total,
    tonnage_total,
    round(CASE WHEN tonnage_total > 0 THEN cout_total / tonnage_total END, 2),
    NULL
FROM trimestriel
ORDER BY 1;
```
_Résultat_: baseline mensuelle Q1–Q3 2024 + coût/tonne et récapitulatif par trimestre.

## Chemin vers 95%+

**PRIORITÉ 1 (BLOQUE DÉPLOIEMENT):**
1. Documenter les benchmarks externes avec preuves vérifiables.  
   Impact: -8 points (IF.TTT + Qualité preuves).  
   Correction: héberger les PDF/URLs (Saint-Gobain, ADEO, Kingfisher) dans l’annexe et citer page + lien fonctionnel.
2. Réécrire toutes projections financières >5K€ en formules ou en références contractuelles.  
   Impact: -5 points.  
   Correction: utiliser les champs `€____` déjà prévus et renvoyer vers factures Médiafret/contrats fournisseurs.

**PRIORITÉ 2 (REQUIS POUR 95%):**
1. Franciser totalement la synthèse PDG, les titres et les livrables (Quick Win, KPI, dashboard, baseline).  
2. Ajouter les preuves de calcul pour ROI externes (ex: capture de l’article LSA ou résumés chiffrés).  
3. Intégrer les scripts fournis (VBA/Python/SQL) dans `tools/` avec notice d’usage pour Angélique.

**PRIORITÉ 3 (POLISH 98%+):**
1. Ajouter tests unitaires rapides (CSV témoin pour le script NPS, exemple Excel avec résultats) et tracer leur exécution dans l’annexe d’audit.

## Verdict
☐ OUI - Aucun changement requis  
☐ OUI AVEC CORRECTIONS - Appliquer fixes ci-dessus d'abord  
☑ NON - Bloqueurs critiques non résolus

**Bloqueurs critiques:**
1. Benchmarks clés (Point P, Leroy Merlin, Castorama) restent non vérifiés et sans URL partageable.  
2. Montants budgétaires >5K€ toujours affichés comme faits établis dans la synthèse exécutive.

## Confiance Évaluation
☐ HAUTE  
☑ MOYENNE  
☐ BASSE  
**Justification:** Dossier très structuré, mais l’absence de sources testables (paywalls LSA/Supply Chain, mention “Internal Analytics”) m’empêche de garantir la conformité IF.TTT >95% sans nouvelles pièces. Les constats s’appuient sur lecture exhaustive des fichiers locaux et tentatives de vérification web (bloquées par Captcha/paywalls).
