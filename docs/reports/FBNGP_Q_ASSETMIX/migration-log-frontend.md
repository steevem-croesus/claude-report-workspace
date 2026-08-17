# Migration Report: FBNGP_Q_ASSETMIX (Frontend)
**Date:** 2026-07-23 16:30:00
**Mode:** Frontend

[16:30:00] [ÉTAPE 0] Bootstrap depuis l'analyse existante — ✓
- analysis.md trouvé : docs/reports/FBNGP_Q_ASSETMIX/analysis.md
- Ticket Jira : RPT-19569 (En cours)
- Paramètres PRE : 2 (PARAM_EndDate [Date], PARAM_UseRepartitionFromInvObj [CheckBox])
- Patterns Observer détectés : 0 (contreparties de dates absentes)
- Validations inter-champs : 0 (pas de PARAM_StartDate → EvalEndDateBeforeStartDate N/A)
- Rapport exclusif : Non (pas de header.ValidationFunction SingleSelect)

[16:31:00] [ÉTAPE 1] Repo frontend = /c/Repos/pf-web (pas claude-pf-web). Template ID = 5000103 — ✓
[16:32:00] [ÉTAPE 2] Paramètres PRE extraits (2) — ✓
[16:33:00] [ÉTAPE 3] Analyse validation/visibilité — ✓
- PARAM_EndDate : C++ EndOfLastQuarter → SetDateRange(max = sys_date_fin) → maxDateValidator(databaseDate) + requiredDateValidator
- PARAM_UseRepartitionFromInvObj : visible Relation + PREF_ENABLE_ASSET_INDEX → géré automatiquement par *hasParam
- Aucun pattern Observer applicable

### PARAM_EndDate (1/2)
**État source:**
- Widget: 5 (Date) | Position: Section 1, Pos 1, Col 1
- DateParametersImplementation.cs: validationFunction: "EndMonthDate" ; ValidationFunction (Parameters.cs): "EndOfLastQuarter", valueProviderFunction: "EndOfLastQuarter" (backend)
- Condition de visibilité: aucune — toujours visible
- initialValue: (calculé par VPF EndOfLastQuarter = fin du dernier trimestre)

**Comportements C++ détectés:**
- **Validation C++:** EvalEndDateBeforeStartDate (validation_date.c:891) — N/A ici (aucun PARAM_StartDate dans le rapport)
- **Plage de dates:** SetDateRange(pDate, GetFirmStartDate(), sys_date_fin) → borne max = date base de données
  - **Réplication Angular:** `requiredDateValidator()` + `maxDateValidator(this.databaseDate)`

**Décision d'implémentation:**
- Composant: `<date-parameter>` [showLabel]="false" [maxDate]="databaseDate"
- Section: `templateSections.endDate` (WindowOrder 1)
- Validators: requiredDateValidator() + maxDateValidator(databaseDate)

**Résultat HTML:**

    <date-parameter [paramName]="END_DATE" [showLabel]="false" [maxDate]="databaseDate"></date-parameter>

### PARAM_UseRepartitionFromInvObj (2/2)
**État source:**
- Widget: 3 (CheckBox) | Position: Section 1, Pos 1, Col 1
- CheckBoxParametersImplementation.cs: validationFunction: "CheckFalseVisibleForRelOnly", initialValue: "0", possibleValues: {0,1}, valueProviderFunction: "CheckFalseVisibleForRelOnly"
- Condition de visibilité: PREF_ENABLE_ASSET_INDEX=YES + contexte Relation (géré par *hasParam)

**Comportements C++ détectés:** Aucun — paramètre simple (checkbox visible en Relation seulement).

**Décision:** `<checkbox-parameter>` spacing="none" dans section `assetAllocation`, visibilité via `*hasParam`.

**Résultat HTML:**

    <checkbox-parameter [paramName]="USE_REPARTITION_FROM_INV_OBJ" spacing="none"></checkbox-parameter>

---

## Comportements C++ répliqués en Angular

### Validations inter-champs

| Validation C++ | Source (fichier, ligne) | Effet | Implémentation Angular |
|----------------|----------------------|-------|----------------------|
| Plage de dates EndOfLastQuarter | validation_date.c:4647 | EndDate ≤ date base de données | `maxDateValidator(this.databaseDate)` + `requiredDateValidator()` |

_Aucun pattern Observer ni visibilité dynamique inter-champs (les contreparties StartDate/GeneratedDate sont absentes du rapport)._

[16:40:00] [ÉTAPE 5] Composant créé (fbngp-asset-allocation-quarterly.ts + .html) — ✓
[16:41:00] [ÉTAPE 5] Enregistrements : factory (import + case), internal-report-name.ts — ✓
[16:42:00] [ÉTAPE 5] cleanParamType : N/A (aucun param Radio/Combo) — ✓
[16:43:00] [ÉTAPE 5] Fixtures e2e : Account.v1.json (entrée 5000103) + params-5000103.Account.v1.json — ✓
[16:44:00] [ÉTAPE 5] Test Cypress créé — ✓
[16:45:00] [ÉTAPE 5] exclusive-report-names : N/A (rapport non exclusif) — ✓
[16:50:00] [ÉTAPE 6] Lint report-view-generate — ✓ 0 erreur (warnings label-has-associated-control préexistants, communs à tous les templates)
[16:51:00] [ÉTAPE 6] Validation JSON fixtures — ✓

---

## Résumé
| Métrique | Valeur |
|----------|--------|
| Paramètres PRE affichés | 2 (PARAM_EndDate, PARAM_UseRepartitionFromInvObj) |
| Sections UI | 2 (End Date, Asset Allocation) |
| Validators ajoutés | 2 (requiredDateValidator, maxDateValidator) |
| Patterns Observer répliqués | 0 |
| setupControlDisabling | 0 |
| Visibilité dynamique (@if) | 0 |
| Traductions ajoutées | 0 clé (endDate + assetAllocation existent déjà) |
| Rapport exclusif | Non |
| cleanParamType mis à jour | 0 param (Date + CheckBox, pas de Radio/Combo) |
| Compilation (lint) | ✓ 0 erreur |

## Fichiers créés/modifiés
- **Créé** : libs/report/domain-view/generate/src/lib/generator/report-templates/templates/fbngp-asset-allocation-quarterly.ts
- **Créé** : libs/report/domain-view/generate/src/lib/generator/report-templates/templates/fbngp-asset-allocation-quarterly.html
- **Modifié** : libs/report/domain-view/generate/src/lib/generator/factories/get-template-by-internal-report-name.ts (import + case FBNGP_Q_ASSETMIX)
- **Modifié** : libs/util-shared/ng-types/src/lib/types/report/internal-report-name.ts (FBNGP_Q_ASSETMIX)
- **Créé** : libs/util-shared/cypress-shared/src/fixtures/resources/reports-templates/params-5000103.Account.v1.json
- **Modifié** : libs/util-shared/cypress-shared/src/fixtures/resources/reports-templates/Account.v1.json (entrée 5000103)
- **Créé** : apps/xpert-e2e/src/e2e/reports/views/accounts/report-template-fbngp-asset-allocation-quarterly.cy.ts

## Note
- InitialValue de PARAM_EndDate dans la fixture = "2009-12-31" (fin du dernier trimestre, aligné sur la databaseDate du harness e2e comme le rapport voisin FBNGP_Q_EVAL). À confirmer contre la sortie réelle Xpert.
- Repo frontend réel : /c/Repos/pf-web (pas claude-pf-web).
