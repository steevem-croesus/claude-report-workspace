# Migration Report: PMFA_COVERPAGE2 (Frontend)
**Date:** 2026-04-16
**Mode:** Frontend

---

## [ÉTAPE 1] Identification du rapport et template ID

- **Nom interne:** PMFA_COVERPAGE2
- **Template ID:** 5000253
- **Classe C#:** RPT_RJ_PMFACover2 → hérite de RPT_RJ_BaseProgramCover
- **Repo frontend:** c:/Repos/pf-web

---

## [ÉTAPE 2] Paramètres PRE identifiés — 2 paramètres visibles

📐 Ordre d'affichage:
```
Section 2:
  Position 1, Col 1: PARAM_GeneratedDate (Date)
  Position 2, Col 1: PARAM_ReportTitlePicker (Combo)
```

---

## [ÉTAPE 3] Analyse de la logique C++

- **Patterns Observer détectés:** Aucun (les paramètres PARAM_GeneratedDate et PARAM_ReportTitlePicker ne participent à aucun pattern du catalogue)
- **Validations inter-champs:** Aucune (pas de StartDate+EndDate)
- **Visibilité dynamique:** Aucune
- **Rapport exclusif:** Non (pas de SingleSelect dans RPT_RJ_PMFACover2.cs ni dans la classe parent)

---

## [ÉTAPE 4] Modèle de référence

Composant existant **pmfa-cover-page-1** utilisé comme modèle — mêmes paramètres PRE (PARAM_GeneratedDate + PARAM_ReportTitlePicker), même structure.

---

## [ÉTAPE 5] Implémentation — Paramètres PRE

### PARAM_GeneratedDate (1/2)
**État source:**
- Widget: 5 (Date) | Position: Section 2, Pos 1, Col 1
- DateParametersImplementation.cs (L.42): `new ParameterEntity(Params.PARAM_GeneratedDate, "", "RPT_mgr_prm_date_prm_AsOf", "AsOfDate", WidgetTypes.Date, "", initialValueDateType: "LastProcessedDate")`
- Condition de visibilité: (aucune — toujours visible)
- initialValue: calculé par le framework (LastProcessedDate)
- valueProviderFunction: (aucun)
- ValidationFunction dans Parameters.cs: `""` (base)

**Comportements C++ détectés:** Aucun — paramètre simple.

**Décision:** `<date-parameter>` dans section asOf. Validators: `requiredDateValidator()` + `maxDateValidator(this.databaseDate)`.

**Résultat HTML:**

    <div *hasParam="GENERATED_DATE" class="section mt-4">
      <label class="section-title">{{ 'reportFeature.generator.templateSections.asOf' | translate }}</label>
      <div class="section-content">
        <date-parameter [paramName]="GENERATED_DATE" [showLabel]="false" [maxDate]="databaseDate"></date-parameter>
      </div>
    </div>

### PARAM_ReportTitlePicker (2/2)
**État source:**
- Widget: 1 (Combo) | Position: Section 2, Pos 2, Col 1
- ComboParametersImplementation.cs (L.71): `new ParameterEntity(Params.PARAM_ReportTitlePicker, "", "RPT_mgr_prm_combo_prm_GReportTitlePicker", "ReportTitlePickerCombo", WidgetTypes.Combo, "", initialValue: "PIMG_PORTFOLIO_MANAGER", possibleDisplayValues: ReportTitlePickerDisplayValues)`
- Condition de visibilité: (aucune — toujours visible)
- initialValue: `"PIMG_PORTFOLIO_MANAGER"`
- possibleDisplayValues: PIMG_PORTFOLIO_MANAGER / PCG_PORTFOLIO_MANAGER / PCG_FINANCIAL_ADVISOR
- valueProviderFunction: (aucun)
- ValidationFunction dans Parameters.cs: `""` (spécifique)

**Comportements C++ détectés:** Aucun — paramètre simple. C++ ReportTitlePickerCombo est purement déclaratif (3 choix fixes, défaut index 0).

**Décision:** `<combobox-parameter>` dans section title, visibilité via `*hasParam`.

**Résultat HTML:**

    <div *hasParam="REPORT_TITLE_PICKER" class="section mt-4">
      <label class="section-title">{{ 'reportFeature.generator.templateSections.title' | translate }}</label>
      <div class="section-content">
        <combobox-parameter [paramName]="REPORT_TITLE_PICKER" [showLabel]="false"></combobox-parameter>
      </div>
    </div>

---

## Comportements C++ répliqués en Angular

Aucun comportement C++ spécifique détecté pour ce rapport. Les deux paramètres PRE sont de simples contrôles statiques sans interdépendances.

---

## Résumé
| Métrique | Valeur |
|----------|--------|
| Paramètres PRE affichés | 2 |
| Sections UI | 2 (asOf, title) |
| Validators ajoutés | 2 (requiredDateValidator, maxDateValidator) |
| Patterns Observer répliqués | 0 |
| setupControlDisabling | 0 |
| Visibilité dynamique (@if) | 0 |
| Traductions ajoutées | 0 clés |
| Rapport exclusif | Non |
| cleanParamType mis à jour | 0 params (PARAM_ReportTitlePicker déjà présent) |
| Compilation | ✓ (aucune erreur dans nos fichiers) |

## Fichiers créés/modifiés
- **Créé:** `libs/report/domain-view/generate/src/lib/generator/report-templates/templates/pmfa-cover-page-2.ts`
- **Créé:** `libs/report/domain-view/generate/src/lib/generator/report-templates/templates/pmfa-cover-page-2.html`
- **Modifié:** `libs/report/domain-view/generate/src/lib/generator/factories/get-template-by-internal-report-name.ts` (import + case)
- **Modifié:** `libs/util-shared/ng-types/src/lib/types/report/internal-report-name.ts` (ajout nom)
- **Créé:** `apps/xpert-e2e/src/e2e/reports/views/accounts/report-template-pmfa-cover-page-2.cy.ts`
- **Modifié:** `libs/util-shared/cypress-shared/src/fixtures/resources/reports-templates/Account.v1.json` (ajout entrée)
- **Créé:** `libs/util-shared/cypress-shared/src/fixtures/resources/reports-templates/params-5000253.Account.v1.json`
