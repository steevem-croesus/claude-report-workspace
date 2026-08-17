# Migration Report: FBNGP_Q_MKTVALUEEVOL (Frontend)
**Date:** 2026-07-22 15:52:00
**Mode:** Frontend

## Déroulement

- [15:50:00] [ÉTAPE 0] Bootstrap depuis l'analyse (analysis.md + RPT-19560) — ✓
- [15:50:00] [ÉTAPE 1] Rapport FBNGP_Q_MKTVALUEEVOL, Template ID 5000115 — ✓
- [15:50:00] [ÉTAPE 2] Paramètres PRE : 3 (StartDate, EndDate, AvgCostCalculMethod) — ✓
- [15:50:00] [ÉTAPE 3] Logique C++ : validation de plage de dates (EvalEndDateBeforeStartDate). Aucun pattern Observer disable/enable inter-champs — ✓
- [15:50:00] [ÉTAPE 4] Modèles : `fbngp-transactions-quarterly` (dates) + `fbngp-portfolio-evaluation-quarterly` (radio coût) — ✓
- [15:51:00] [ÉTAPE 5] Implémentation composant + fixtures + test e2e — ✓
- [15:52:00] [ÉTAPE 6] Lint EXIT 0 + typecheck ciblé EXIT 0 — ✓

## Ordre d'affichage (PRE)

```
Section 1 (dates) :
  Position 1, Col 1: PARAM_StartDate (Date)
  Position 2, Col 1: PARAM_EndDate (Date)
Section 8 (coût) :
  Position 1, Col 1: PARAM_AvgCostCalculMethod (Radio)
```

Note : rapport système (visibilités `N`, `ApplySystemReport`) mais exposé dans le générateur Xpert au même titre que ses frères FBN GP1859 (`FBNGP_Q_EVAL`, `FBNGP_Q_TRANSACTION`).

---

## Détail par paramètre PRE

### PARAM_StartDate (1/3)
**État source:**
- Widget: 5 (Date) | Position: Section 1, Pos 1, Col 1
- DateParametersImplementation.cs: `validationFunction: "StartMonthDate"` — backend override `BegOfLastQuarter` → VPF `LastQuarterStartDate`
- Condition de visibilité: aucune
- InitialValue (API/VPF): `2009-10-01` (début du dernier trimestre complet)

**Comportements C++ détectés:**
- **Validation C++:** `EvalEndDateBeforeStartDate` (enregistrée par le dispatch de `EndOfLastQuarter`)
  - Source C++: `validation_date.c` L.891
  - Effet: la date de fin ne peut pas être antérieure à la date de début
  - **Réplication Angular:** `rangeDateValidator(this.START_DATE, this.END_DATE)` sur le form + `[formControlMaxDate]="END_DATE"` + `[hideDateRangeErrorMsg]="true"` sur le champ StartDate

**Décision d'implémentation:**
- Composant: `<date-parameter>`
- Section: `templateSections.date` (Section 1)
- Validators: `requiredDateValidator()`
- Attributs: `[formControlMaxDate]="END_DATE"`, `[hideDateRangeErrorMsg]="true"`

**Résultat HTML:**

    <date-parameter
      *hasParam="START_DATE"
      [paramName]="START_DATE"
      [formControlMaxDate]="END_DATE"
      [hideDateRangeErrorMsg]="true"
    ></date-parameter>

### PARAM_EndDate (2/3)
**État source:**
- Widget: 5 (Date) | Position: Section 1, Pos 2, Col 1
- DateParametersImplementation.cs: `validationFunction: "EndMonthDate"` — backend override `EndOfLastQuarter` → VPF `LastQuarterEndDate`
- Condition de visibilité: aucune
- InitialValue (API/VPF): `2009-12-31` (fin du dernier trimestre complet)

**Comportements C++ détectés:**
- **Validation C++:** `EvalEndDateBeforeStartDate` + borne max = `sys_date_fin` (DPH)
  - Source C++: `validation_date.c` L.891 + `GetBatchEndDate`
  - Effet: EndDate ≥ StartDate et EndDate ≤ date de base (DPH)
  - **Réplication Angular:** `rangeDateValidator(START_DATE, END_DATE)` + `maxDateValidator(this.databaseDate)`

**Décision d'implémentation:**
- Composant: `<date-parameter>`
- Section: `templateSections.date` (Section 1)
- Validators: `requiredDateValidator()`, `maxDateValidator(this.databaseDate)`
- Attributs: `[maxDate]="databaseDate"`

**Résultat HTML:**

    <date-parameter
      *hasParam="END_DATE"
      [paramName]="END_DATE"
      [maxDate]="databaseDate"
    ></date-parameter>

### PARAM_AvgCostCalculMethod (3/3)
**État source:**
- Widget: 2 (Radio) | Position: Section 8, Pos 1, Col 1
- RadioParametersImplementation.cs (L.41): `initialValue: "COST_CALC_ACB", possibleDisplayValues: COST_CALC_ACB (Book Value) / COST_CALC_INVEST (Invested Capital), activation PREF_TAX_LOT=NO`
- Condition de visibilité: `PREF_TAX_LOT=NO` (gérée automatiquement via `*hasParam`)
- InitialValue (API/VPF): `COST_CALC_ACB` (Book Value)

**Comportements C++ détectés:** Aucun pattern Observer inter-champs. Radio à valeurs fixes.

**Décision d'implémentation:**
- Composant: `<radio-parameter>`
- Section: `templateSections.costCalculation` (Section 8)
- `cleanParamType` : `PARAM_AvgCostCalculMethod` déjà présent (retourne `'Radio'`) — aucune modification

**Résultat HTML:**

    <radio-parameter [paramName]="AVG_COST_CALCUL_METHOD"></radio-parameter>

---

## Comportements C++ répliqués en Angular

### Patterns Observer du framework C++

Aucun pattern Observer disable/enable inter-champs détecté dans `win_prm_grp_*.c` pour les 3 paramètres PRE (le radio `PARAM_AvgCostCalculMethod` n'apparaît dans aucun `win_prm_grp_*.c`).

### Validations inter-champs

| Validation C++ | Source (fichier, ligne) | Effet | Implémentation Angular |
|----------------|----------------------|-------|----------------------|
| `EvalEndDateBeforeStartDate` | `validation_date.c` L.891 | EndDate ≥ StartDate | `rangeDateValidator(START_DATE, END_DATE)` + `[formControlMaxDate]` + `[hideDateRangeErrorMsg]` |
| Borne max EndDate = DPH | `validation_date.c` (GetBatchEndDate / sys_date_fin) | EndDate ≤ date de base | `maxDateValidator(this.databaseDate)` |

### Visibilité dynamique

| Mécanisme C++ | Paramètre | Condition | Implémentation Angular |
|---------------|-----------|-----------|----------------------|
| Condition pref (statique) | `PARAM_AvgCostCalculMethod` | `PREF_TAX_LOT=NO` | Automatique via `*hasParam` |

---

## Résumé
| Métrique | Valeur |
|----------|--------|
| Paramètres PRE affichés | 3 |
| Sections UI | 2 (dates, coût) |
| Validators ajoutés | 3 (requiredDate x2, maxDate, rangeDate) |
| Patterns Observer répliqués | 0 (aucun inter-champs) |
| setupControlDisabling | 0 |
| Visibilité dynamique (@if) | 0 (via `*hasParam`) |
| Traductions ajoutées | 0 clé (date + costCalculation déjà existantes) |
| Rapport exclusif | Non (pas de `SingleSelect`) |
| cleanParamType mis à jour | 0 param (AvgCostCalculMethod déjà présent) |
| Lint | ✓ (EXIT 0) |
| Typecheck ciblé | ✓ (EXIT 0) |

## Fichiers créés/modifiés
- **Créé** : `libs/report/domain-view/generate/src/lib/generator/report-templates/templates/fbngp-evolution-of-market-value.ts`
- **Créé** : `libs/report/domain-view/generate/src/lib/generator/report-templates/templates/fbngp-evolution-of-market-value.html`
- **Modifié** : `libs/report/domain-view/generate/src/lib/generator/factories/get-template-by-internal-report-name.ts` (import + case `FBNGP_Q_MKTVALUEEVOL`)
- **Modifié** : `libs/util-shared/ng-types/src/lib/types/report/internal-report-name.ts` (+ `FBNGP_Q_MKTVALUEEVOL`)
- **Modifié** : `libs/util-shared/cypress-shared/src/fixtures/resources/reports-templates/Account.v1.json` (+ entrée 5000115)
- **Créé** : `libs/util-shared/cypress-shared/src/fixtures/resources/reports-templates/params-5000115.Account.v1.json`
- **Créé** : `apps/xpert-e2e/src/e2e/reports/views/accounts/report-template-fbngp-evolution-of-market-value.cy.ts`

## Notes
- `cleanParamType` et les clés i18n (`date`, `costCalculation`) étaient déjà en place → aucune modification.
- Pas de `exclusive-report-names.ts` dans cette version du repo ; le rapport n'est de toute façon pas `SingleSelect`.
- Repo réel : `/c/Repos/pf-web` (le chemin `claude-pf-web` de la commande est absent). Branche courante : `feature/rpt-19550`.
