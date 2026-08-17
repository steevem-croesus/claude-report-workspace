# Conventions frontend (Angular — pf-web)

Base de connaissances frontend pour créer le composant de paramétrage Angular d'un rapport migré.
Source de vérité pour `frontend-migrator` (et `migration-reviewer`). Pipeline et chemins dans
`migration-protocol.md`.

> **Repo :** `repos/pf-web/` (symlink → `/c/Repos/pf-web`). ⚠️ Les anciennes commandes mentionnaient
> `c:/Repos/claude-pf-web` — ce chemin n'existe pas ici ; utiliser le symlink `repos/pf-web/`.

## Standards pf-web (SOURCE DE VÉRITÉ)

Les standards du projet vivent dans **`repos/pf-web/doc/standards/`** et **priment** sur les exemples de cette
convention. Les lire avant d'écrire du code (les fichiers récents du repo les adoptent — c'est la direction
du projet). Fichiers pertinents pour la migration : `angular.md`, `html.md`, `e2e-testing.md`, `testing.md`.

**Angular (`angular.md`)**
- `changeDetection: ChangeDetectionStrategy.OnPush` sur chaque composant.
- Pas de `standalone: true` (défaut). `inject()` (pas de constructeur). Entrées/sorties en signals
  `input()`/`input.required()`/`output()` (jamais `@Input()`/`@Output()`).
- Control flow natif `@if`/`@for`/`@switch`. Interdits : `ngClass`/`ngStyle`, `@HostBinding`/`@HostListener`,
  `any`, `NgModules`.

**HTML (`html.md`)**
- i18n : pipe `translate` + clé, jamais de texte en dur. `data-test` sur chaque élément testable.
- Control flow natif. Pas de style inline, pas d'attribut `id`. a11y (`aria-label` sur boutons icône).

**e2e Cypress (`e2e-testing.md`)**
- Nouveau spec en **`.functional.cy.ts`** (les `.cy.ts` du dossier report-templates sont l'ancienne convention).
- Happy-path seulement ; regrouper les vérifications dans peu d'`it()` (pas d'edge-case en e2e → Vitest).
- Page Object + sélecteurs `data-test` exclusifs. `cy.smartIntercept`/helpers + `.as()` + `cy.wait('@alias')` ;
  jamais `cy.intercept` direct ni `cy.wait(ms)`. `cy.smartLogin('uni00')` avant `cy.visit` ;
  `createAppStartIntercepts()` en tête de `beforeEach`. Pas d'`async`/`await` ; ne pas stocker un `cy.get`.
  Contrôles Material → cliquer l'`input` interne.

**Tests unitaires (`testing.md`)** — si un spec composant est créé : `MockProvider`/`MockOf` + Vitest, `sut`,
`data-test` pour les sélecteurs, format « should … when … », `// Arrange/Act/Assert`, pas d'`any`.

## Ce qu'on migre côté frontend

Seuls les paramètres **PRE** (visibles) donnent lieu à du frontend. Le composant reproduit :
positionnement (WindowOrder/Position/PositionH), patterns Observer inter-champs, validateurs
inter-champs, visibilité/désactivation conditionnelle, traductions, enregistrement, tests e2e.

## Positionnement (depuis `Parameters.cs`)

- **`WindowOrder`** = la section UI (mêmes WindowOrder = même section).
- **`Position`** = ordre vertical dans la section.
- **`PositionH`** = colonne (1 = gauche, 2 = droite).
- Seuls les PRE ont des valeurs significatives ; les POST/Hidden ont tous `1/1/1`.

## Patterns Observer (win_prm_grp_*.c → Angular)

⚠️ Les dépendances inter-paramètres sont définies dans **`win_prm_grp_*.c`** (via `NotifyOnChange`/
`WATCH_*`), **PAS** dans `validation_*.c`. Elles s'activent automatiquement dès que les paramètres
source **et** cible coexistent (PRE) dans le rapport. Pour chaque paramètre PRE, grep son nom dans
`win_prm_grp_{check,combo,radio,date}.c`.

**Catalogue Observer → `setupControlDisabling` :**

| # | Pattern C++ | Source → Cible | Condition | Angular |
|---|---|---|---|---|
| 1 | `WATCH_USE_LAST_YEAR` | UseLastYear → StartDate, EndDate | coché → disable **+ InitWidget** | `setupControlDisabling(form, USE_LAST_YEAR, [START_DATE, END_DATE], v => v == true)` + reset (§ InitWidget) |
| 2 | `WATCH_REPARTITION_COMBO` | AssetMixRepartType → AssetMixRepartitionID | `!= PERSONNAL_ASSETMIX_REPAR` | `setupControlDisabling(..., v => v !== 'PERSONNAL_ASSETMIX_REPAR')` |
| 3 | `WATCH_DISABLE_CHECK_IF_ASMPERSO` | AssetMixRepartType → RegionCheck, FundBreakDown, FundAnnex | `== PERSONNAL_ASSETMIX_REPAR`/`GSleeves` → disable+uncheck | `setupControlDisabling(..., v => v === 'PERSONNAL_ASSETMIX_REPAR', false)` |
| 4 | `WATCH_IND_CODE_COMBO` | IndCodeCheck → IndCodeCombo | décoché | `setupControlDisabling(..., v => v == false)` |
| 5 | `WATCH_PERFGRAPH_ASSETMIX` | PerfGraphAssetMix → AssetMixRepartType | décoché | `setupControlDisabling(..., v => v == false)` |
| 6 | `WATCH_FOREIGN_INCLUDE_SUMMARY` | IncludeSummaryTable → TableSummaryValueType | décoché | `setupControlDisabling(..., v => v === false)` |
| 7 | `WATCH_DISABLE_PERF_DATE` | PerfPeriodType → EndDate | `!= "0"` (pas FIXED) | `setupControlDisabling(..., v => v !== '0')` |
| 8 | `WATCH_ACC_INT_UNTIL_MATURITY` | AccIntUntilMaturity → EndDate | coché → disable **+ reset** | `setupControlDisabling(..., v => v == true)` + reset |
| 9 | `WATCH_DEV_WITH_IND_REF_CHANGE` | PerfDev*WithIndRef (×3) → RefIndex | tous décochés | logique custom `valueChanges` |

**Sous-pattern InitWidget (reset de valeur)** — patterns #1 et #8 : quand re-coché, les widgets cibles
doivent revenir à leurs **valeurs initiales du VPF**. Sauvegarder les valeurs initiales au chargement
puis les restaurer via `valueChanges` :

```typescript
const [sy, sm, sd] = (this.form.get(this.START_DATE)?.value ?? '').split('-').map(Number);
this.initialStartDate = new Date(sy, sm - 1, sd); // idem END_DATE
this.form.get(this.USE_LAST_YEAR)?.valueChanges.subscribe((checked: boolean) => {
  if (checked) { this.form.get(this.START_DATE)?.setValue(this.initialStartDate);
                 this.form.get(this.END_DATE)?.setValue(this.initialEndDate); }
});
```

Fichiers source (référence) : `repos/CroesusServer/Src/ReportApi/ReportView/ReportViewParam/win_prm_grp_{date,check,combo,radio}.c`.

## Validation dynamique (validation_*.c → Angular)

| Source C++ | Angular |
|---|---|
| Condition `PREF_*=*` (6e param du `*ParametersImplementation.cs`) | `*hasParam` (automatique) |
| `SetHideParam(true/false)` | `@if (condition)` ou getter |
| `ForceDisableParam()` | `setupControlDisabling(...)` |
| `EvalEndDateBeforeStartDate` | `rangeDateValidator(START_DATE, END_DATE)` + pattern `formValidity$` |
| `maxDate = sys_date_fin` | `maxDateValidator(this.databaseDate)` |
| date requise | `requiredDateValidator()` |

**Validation dates StartDate/EndDate** — quand le rapport a `PARAM_StartDate` + `PARAM_EndDate` et que
le C++ contient `EvalEndDateBeforeStartDate` (ou un appelant comme `AssetsMngPerPeriodValidation`),
ajouter `rangeDateValidator(this.START_DATE, this.END_DATE)` **et** propager l'invalidité au bouton
Generate :

```typescript
this.form.statusChanges
  .pipe(startWith(this.form.status), takeUntilDestroyed(this.destroyRef))
  .subscribe(() => this.formValidity$.next(this.form.valid));
```

(`takeUntilDestroyed` de `@angular/core/rxjs-interop`, `startWith` de `rxjs` ; `formValidity$` et
`destroyRef` déjà fournis par `ReportBaseTemplateComponent`.)

**Observer PerfSummaryLevel** (radio Niveau) — enum `E_PERF_LEVEL` : ACCOUNT=0, CLIENT=1,
RELATIONSHIP=2, REP=3, BRANCH=4, REGION=5, FIRM=6 (Xpert n'expose que 3–6). Ex. `WATCH_SUMM_PERF_QUARTILE`
→ `PARAM_PerfQuartile` disable si niveau = Firm(6) : `setupControlDisabling(form, PERF_SUMMARY_LEVEL,
[PERF_QUARTILE], v => v === '6', false)`.

## Structure du composant

`.ts` + `.html` dans `repos/pf-web/libs/report/domain-view/generate/src/lib/generator/report-templates/templates/{report-slug}.{ts,html}`
(slug dérivé du nom interne : `FOREIGN_PROPERTY` → `foreign-property`). Le `.ts` `extends
ReportBaseTemplateComponent`, déclare les constantes `PARAM_*`, met les validators/dépendances dans
`override onFormInitialized = () => {…}`, n'importe **que** les composants réellement utilisés. Le
décorateur `@Component` porte un `selector: "report-view-{report-slug}-template"` (cohérence avec les
templates FBNGP récents, aide au debug) en plus de `templateUrl` et `changeDetection: OnPush`. HTML par
sections (`WindowOrder`), `*hasParam` sur chaque paramètre/groupe, classes
`section col-12 col-xs-6 col-md-4 col-lg-6 col-xl-4`. Toujours lire 1-2 templates existants comme
modèle (`assets-under-management.ts`).

Conventions composants : `<date-parameter [showLabel]="false" [maxDate]="databaseDate">`,
`<radio-parameter>`, `<combobox-parameter [showLabel]="false">`, `<checkbox-parameter spacing="none">`.
**Pagination toujours en `<radio-parameter>`**, jamais `<combobox-parameter>`.

## Enregistrement (ordre alphabétique partout)

1. `libs/util-shared/ng-types/src/lib/types/report/internal-report-name.ts` → `INTERNAL_REPORT_NAMES`.
2. `.../generator/factories/get-template-by-internal-report-name.ts` → import + `case` du switch.
3. `libs/util-shared/api-services/custom-services/src/lib/services/report-template-parameters.service.ts`
   → `cleanParamType` : chaque PRE **Radio** dans le `case` `'Radio'`, chaque **Combo** dans `'Combobox'`
   (les Boolean/Date/List n'ont pas besoin).
4. **Rapport exclusif** : si `RPT_*.cs` a `header.ValidationFunction = "SingleSelect"` **ou**
   `"SingleSelectNotSame"` (les deux rendent exclusif) → ajouter dans
   `libs/util-shared/ng-types/src/lib/types/report/exclusive-report-names.ts` (`EXCLUSIVE_REPORTS_NAMES`).
5. i18n (si nouvelle clé de section `templateSections.*`) : `generator/i18n/{base,en,fr}.ts`. Nouvelles
   clés préfixées `RPT_mgr_`, jamais `CRESUS_rpt_`.

## Tests e2e (Cypress)

⚠️ **Source de vérité : `repos/pf-web/doc/standards/e2e-testing.md`.** Les règles ci-dessous en sont l'extrait
appliqué à la migration ; en cas de doute, relire le standard. **Toujours lire un `.functional.cy.ts`
récent comme modèle** (ex. `report-template-fbngp-historical-performance-quarterly.functional.cy.ts`) —
il incarne le pattern « helper actions-only + assertions dans l'`it()` ».

**Fichier & emplacement**
- Spec : `apps/xpert-e2e/src/e2e/reports/views/accounts/report-template-{slug}.functional.cy.ts` — suffixe
  **`.functional.cy.ts`** (les `.cy.ts` nus sont l'ancienne convention, ne plus les créer).
- Fixtures : entrée dans `libs/util-shared/cypress-shared/src/fixtures/resources/reports-templates/Account.v1.json`
  + `params-{templateId}.Account.v1.json`.
- ⚠️ Les `InitialValue` des fixtures reflètent la **valeur réelle retournée par l'API** (après VPF), pas
  la valeur par défaut du `*ParametersImplementation.cs`. Lire le `ValueProviderFunction` dans
  `Parameters.cs` pour la déterminer ; en cas de doute, demander les valeurs observées dans Xpert.

**Sélecteurs — jamais de `data-test` en dur dans le spec** (findings PR #1, #4)
- Tout sélecteur `data-test` se déclare dans l'objet `ReportAccountGenerateSelectors` (const, en tête de
  `support/reports/views/accounts/accounts-generate.po.ts`), **pas** inline dans le spec.
- **Réutiliser** un sélecteur existant avant d'en recréer un : `paramEndDateInput` existe déjà comme
  `'[data-test="PARAM_EndDate"] input'` — l'utiliser tel quel, ne pas reconstruire
  `` `[data-test="${...paramEndDate}"] input` `` inline.
- Nouveau paramètre → ajouter une entrée nommée (suffixe `Input`/`Button`/… ) :
  `paramsUseRepartitionFromInvObjInput: '[data-test="PARAM_UseRepartitionFromInvObj"] input'`. Contrôle
  Material → viser l'`input` interne.

**Alias d'intercept — jamais de `const` local** (finding PR #6)
- Les alias vivent dans `AccountGenerateFixturesId` (const de `accounts-generate.interceptors.ts`), ex.
  `reportTemplateAccount5000103: 'reports_template_account_5000103'`. Le spec référence
  `` cy.wait(`@${AccountGenerateFixturesId.reportTemplateAccount5000103}`) `` — pas de chaîne littérale.

**Structure du spec** (findings PR #2, #3, #5, #7)
- **Un seul `describe('… Functional Tests')` par fichier.** Tout le setup dans `beforeEach`
  (`createAppStartIntercepts()` en premier, puis `createReportAccountGenerateIntercepts()`). Jamais de
  `describe` imbriqué, jamais de `before`/`after`.
- **Helper de configuration = actions seulement** (login, visit, wait, clics de sélection). **Aucune
  assertion** dans le helper — elles remontent dans l'`it()` pour que l'échec pointe le test (le seul
  `should('exist')` toléré est le `root()` du PO). Modèle : le helper
  `configure…` du spec `fbngp-historical-performance-quarterly`.
- **Nommer les `it()` en minuscule** : `it('should … when …', …)` (format `should … when …`).
- **Regrouper** les vérifications d'un même flux dans un `it()` cohérent (le standard §*Spec size*
  déconseille de multiplier les petits `it()` : chaque `it()` repaie login + boot + intercepts).
  Ne découper en plusieurs `it()` que si les comportements sont **réellement indépendants**. Rester
  happy-path (edge-cases → Vitest).

## Checklist avant compilation
- [ ] `internal-report-name.ts`, `get-template-by-internal-report-name.ts` (import + case), alpha.
- [ ] `exclusive-report-names.ts` si `SingleSelect`/`SingleSelectNotSame`.
- [ ] `cleanParamType` : chaque PRE Radio/Combo présent.
- [ ] `.ts` extends `ReportBaseTemplateComponent`, tous les PARAM_* PRE en constantes ; imports = utilisés seulement.
- [ ] `.html` vérifié contre le legacy (WindowOrder → sections, Position/PositionH → ordre).
- [ ] Dates : `requiredDateValidator()`, `maxDateValidator(databaseDate)`, `rangeDateValidator()` si Start+End.
- [ ] Chaque pattern Observer applicable (source+cible PRE) → `setupControlDisabling` (+ reset si InitWidget).
- [ ] Visibilité conditionnelle → `@if` + getter.
- [ ] `@Component` porte un `selector: "report-view-{slug}-template"`.
- [ ] Fixtures + spec `.functional.cy.ts` créés, `InitialValue` cohérentes avec le VPF.
- [ ] e2e : sélecteurs dans `ReportAccountGenerateSelectors` (aucun `data-test` en dur dans le spec, réutiliser l'existant).
- [ ] e2e : alias d'intercept dans `AccountGenerateFixturesId` (aucun `const` local).
- [ ] e2e : un seul `describe`, setup dans `beforeEach`, helper actions-only (assertions dans l'`it()`), noms `should … when …`.

## Anti-patterns
1. Inclure les POST/Hidden dans le template (seuls les PRE sont visibles).
2. Coder la logique de préférence (`*hasParam` gère la visibilité).
3. Importer des composants non utilisés.
4. Casser l'ordre alphabétique.
5. Clés `CRESUS_rpt_` (utiliser `RPT_mgr_`).
6. `<combobox-parameter>` pour Pagination (toujours `<radio-parameter>`).
7. Chercher les Observer dans `validation_*.c` (ils sont dans `win_prm_grp_*.c`).
8. **e2e** : `data-test` en dur / reconstruit inline dans le spec (→ `ReportAccountGenerateSelectors`, réutiliser l'existant).
9. **e2e** : alias d'intercept en `const` local (→ `AccountGenerateFixturesId`).
10. **e2e** : `describe` imbriqué, ou assertions dans un helper de setup (→ un seul `describe`, assertions dans l'`it()`).
11. **e2e** : spec en `.cy.ts` nu (→ `.functional.cy.ts`) ou `it()` avec « Should » majuscule (→ `should … when …`).
12. Oublier le `selector` sur `@Component` du template.