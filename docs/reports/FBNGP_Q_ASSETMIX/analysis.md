# Analyse du rapport FBNGP_Q_ASSETMIX

## Description utilisateur (spec fonctionnelle)

### À quoi sert ce rapport

Le rapport **Répartition d'actifs du portefeuille** (*Asset Allocation (Quarterly)*) présente la répartition
des actifs d'un portefeuille par sous-catégorie, sous forme de graphique circulaire accompagné d'un
en-tête. C'est un rapport **trimestriel** faisant partie du package de rapports GP1859 de la Banque
Nationale (FBN). Il montre, pour chaque classe d'actif (jusqu'à 6 niveaux de hiérarchie), la valeur, le
pourcentage, et les cibles/minimums/maximums d'objectif de placement.

### Contexte d'utilisation

- **Activation** : nécessite les deux préférences `PREF_REPORT_FBNGP_Q_ASSETMIX=YES` **et**
  `PREF_QUARTERLY_REPORT_GP1859=YES`. Sans ces deux prefs, le rapport n'apparaît pas dans le sélecteur.
- **Niveau d'usage** : rapport de niveau portefeuille/relation. Toutes les visibilités
  (`IsLinkVisible`, `IsClientVisible`, `IsAccountVisible`, `IsPortfolioVisible`) sont à `N` — c'est un
  rapport système (`ApplySystemReport = true`) orchestré par le package trimestriel, pas sélectionnable
  librement par pad.
- **Date par défaut** : la date de fin est initialisée à la **fin du dernier trimestre complet**.

### Ce que l'utilisateur voit en sortie

Le rapport est en orientation **paysage** et se compose de :

1. **En-tête FBN GP** (`SUB_FBNGPQHeader`) — bandeau d'en-tête du package trimestriel.
2. **Graphique circulaire de répartition d'actifs** (`SUB_FBNGPQGraphAm`) — camembert (*PieChart*) de la
   répartition de l'actif (type `GraphAssetAllocation`).

Le rapport n'a **pas de tableau détaillé visible** dans le corps principal (aucune colonne n'est marquée
comme colonne de base) : le rendu est entièrement porté par les deux sous-rapports.

### Options de configuration (paramètres visibles à l'utilisateur)

| Option | Type | Comportement |
|--------|------|--------------|
| Date de fin | Date | Initialisée à la fin du dernier trimestre. |
| Utiliser l'objectif de placement défini | Case à cocher | Décochée par défaut ; visible uniquement en contexte Relation, et seulement si la préférence `PREF_ENABLE_ASSET_INDEX` est active. |

### Comportements interactifs (règles UI)

Aucun comportement inter-champs actif : les seuls patterns C++ liés à `PARAM_EndDate` dépendent d'un
`PARAM_StartDate` / `PARAM_GeneratedDate` / `PARAM_DisplayDate` **absents de ce rapport**. Il n'y a donc
aucune dépendance dynamique entre paramètres à reproduire.

### Préférences administratives qui influencent le rapport

- **Affichage de la devise dans le titre** (`PREF_REPORT_HIDE_CURRENCY`) : masque la devise dans le titre.
- **Affichage du nom de la firme** (`PREF_REPORT_DISPLAY_FIRM_NAME`) : affiche le nom de la firme.
- **Affichage de la date et de l'heure** (`PREF_REPORT_DISPLAY_DATE_TIME`) : affiche date + heure de génération.
- **Objectif de placement / index d'actif** (`PREF_ENABLE_ASSET_INDEX`) : conditionne la visibilité de la
  case « Utiliser l'objectif de placement défini ».

---

## Identité

- **Template ID** : `5000103`
- **Nom interne** : `FBNGP_Q_ASSETMIX`
- **Classe C#** : `RPT_FBNGPAssetAllocationQuarterly` (hérite de `ReportImplementation`)
- **Fichier** : [RPT_FBNGPAssetAllocationQuarterly.cs](../../../ReportFoundations/ReportImplementations/Implementations/Reports/Main/FBN/AssetAllocationQuarterly/RPT_FBNGPAssetAllocationQuarterly.cs)
- **Template** : `TPL_FBNGPAssetAllocationQuarterly` (template minimal — `CreateGenericSourceCondition()` seul)
- **Sub-reports** : `SUB_FBNGPQHeader` (`FBNGP_Q_RPT_HEADER`), `SUB_FBNGPQGraphAm` (`FBNGP_Q_GRAPH_AM`, PieChart)
- **Rapport exclusif** : Non (`header.ValidationFunction` absent — ni `SingleSelect` ni `SingleSelectNotSame`)

## Noms (Resource.*.resx)

| Clé | EN | FR |
|-----|----|----|
| `RPT_mgr_rpt_GFBNGPQAssetMix` | Asset Allocation (Quarterly) | Répartition d'actifs du portefeuille |
| `RPT_mgr_tit_GFBNGPQAssetMix` | ASSET ALLOCATION | RÉPARTITION D'ACTIFS DU PORTEFEUILLE |

## Activation et visibilité

- `PrefValidation = "PREF_REPORT_FBNGP_Q_ASSETMIX=YES,PREF_QUARTERLY_REPORT_GP1859=YES"`
- `IsLinkVisible="N"`, `IsClientVisible="N"`, `IsAccountVisible="N"`, `IsPortfolioVisible="N"`
- `ApplySystemReport = true`
- `HelpToken` : non défini dans `InitHeader`

## Paramètres

**Total : 21 paramètres** (2 PRE + 19 POST)

### PRE — visibles dans l'UI

| # | Paramètre | Étape | Widget | Default_Function | Specific_Function |
|---|-----------|-------|--------|------------------|-------------------|
| 1 | `PARAM_UseRepartitionFromInvObj` | PRE | CheckBox | `CheckFalseVisibleForRelOnly` | — |
| 2 | `PARAM_EndDate` | PRE | Date | `EndMonthDate` | `EndOfLastQuarter` |

### POST — Hidden (19 paramètres)

Tous les paramètres POST ont le widget **Hidden** (`PARAMETER_ENTRY_TYPE = 8`).

**Identifiants / structure**

| Paramètre | Étape | Widget | Function (Default → Specific) |
|-----------|-------|--------|-------------------------------|
| `PARAM_ReportPad` | POST | Hidden | `GetPad` |
| `PARAM_ReportViewIdentifier` | POST | Hidden | `SetReportViewIdentifier` → `SetFBNGPQAssetMixViewIdentifier` |
| `PARAM_RPTSubId` | POST | Hidden | — → `FBNGPQAssetMixSubRptField` |
| `PARAM_DataEntryPoint` | POST | Hidden | — → `FBNGPAssetMixEntryPoint` |
| `PARAM_AddSpecificJoin` | POST | Hidden | — → `AssetMixSumGP1859SpecificJoin` |
| `H_PARAM_AssetMixRepartType` | POST | Hidden | `UseMaturityRepartition` → `UseFBNGP1859Repartition` |

**Affichage / titre / devise**

| Paramètre | Étape | Widget | Function (Default → Specific) |
|-----------|-------|--------|-------------------------------|
| `PARAM_ReportTitle` | POST | Hidden | `ReportTitle` |
| `PARAM_FirmCurrency` | POST | Hidden | `GetFirmCurrency` |
| `PARAM_ForceCurrency` | POST | Hidden | `GetDefaultCurrency` |
| `PARAM_HideTitleCurrency` | POST | Hidden | `GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)` |
| `PARAM_DisplayFirmName` | POST | Hidden | `GetBoolFromPref(PREF_REPORT_DISPLAY_FIRM_NAME)` |
| `PARAM_DisplayDateAndTime` | POST | Hidden | `GetBoolFromPref(PREF_REPORT_DISPLAY_DATE_TIME)` |
| `PARAM_DontDisplayKeyInHeader` | POST | Hidden | `CheckTrue` |

**Options rapport / graphique**

| Paramètre | Étape | Widget | Function (Default → Specific) |
|-----------|-------|--------|-------------------------------|
| `Hided_PARAM_MutFundBreakDown` | POST | Hidden | `MutualFundBreakDown` → `CheckFalse` |
| `PARAM_HideMinMaxTarget` | POST | Hidden | `CheckFalse` → `CheckTrue` |
| `PARAM_IncludeCoverPage` | POST | Hidden | `CheckFalse` → `CheckFalse` |
| `PARAM_DisableParamButton` | POST | Hidden | `CheckFalse` |
| `PARAM_UseNbPageTotal` | POST | Hidden | `CheckFalse` |
| `PARAM_IgnoreIdMasking` | POST | Hidden | `GetDisplayUnmaskedId` |

## Préférences impliquées

### Activation (header.PrefValidation)

- `PREF_REPORT_FBNGP_Q_ASSETMIX` — active le rapport dans le package.
- `PREF_QUARTERLY_REPORT_GP1859` — active la suite trimestrielle GP1859 (Banque Nationale).

### Runtime — POST params via `GetBoolFromPref(...)`

- `PREF_REPORT_HIDE_CURRENCY` → `PARAM_HideTitleCurrency` (masque la devise dans le titre)
- `PREF_REPORT_DISPLAY_FIRM_NAME` → `PARAM_DisplayFirmName` (affiche le nom de la firme)
- `PREF_REPORT_DISPLAY_DATE_TIME` → `PARAM_DisplayDateAndTime` (affiche date + heure)

### UI logic — lues dans les handlers Observer

- `PREF_ENABLE_ASSET_INDEX` → conditionne la visibilité du checkbox `PARAM_UseRepartitionFromInvObj`
  (`PrefValidation` du paramètre dans `CheckBoxParametersImplementation.cs`).

## Comportements UI (Observer patterns)

**Aucun pattern Observer actif.**

Recherche effectuée dans `win_prm_grp_date.c` et `win_prm_grp_check.c` :
- `PARAM_EndDate` déclenche des notifications (`WATCH_START_DATE_VALUE`, `NOTIFY_DISPLAY_DATE`,
  `GET_END_DATE_VALUE`) qui ciblent `PARAM_StartDate`, `PARAM_GeneratedDate`, `PARAM_DisplayDate`,
  `PARAM_EndDatePortDetail` — **tous absents de ce rapport**. Les patterns ne s'appliquent donc pas.
- `PARAM_UseRepartitionFromInvObj` : aucun handler `win_prm_grp_*.c`.

Conséquence : pas de validation croisée de dates, pas de dépendance enable/disable/select à reproduire
côté Angular.

## Contenu du rapport

### Colonnes affichées par défaut

> **Aucun corps tabulaire classique.** Le rapport définit 50+ colonnes `ASMS_*` (Asset Mix Summary) via
> `ConfigurableColumnJoinEntity`, mais aucune n'est marquée `IncludeAsBaseColumn = true` / `SetBaseColumns`.
> Le rendu visuel provient exclusivement des sous-rapports.

### Colonnes de données (`ASMS_*`, 6 niveaux de hiérarchie)

- **Classification** : `ASMS_ClassIdLvl1..6`, `ASMS_DescriptionLvl1..6`, `ASMS_DisplayOrderLvl1..6`
- **Objectifs** : `ASMS_ObjMinLvl1..6`, `ASMS_ObjMaxLvl1..6`, `ASMS_ObjTargetLvl1..6` (pourcentages)
- **Valeurs** : `ASMS_ValueLvl1..6`, `ASMS_PercentLvl1..6`
- **Totaux** : `ASMS_TotalObjTarget`, `ASMS_TotalPercent`, `ASMS_TotalValue`

### Sous-rapports

- `SUB_FBNGPQHeader` (`FBNGP_Q_RPT_HEADER`) — en-tête, template `SUBTPL_FBNGPQHeader`, aucune config/style spécifique.
- `SUB_FBNGPQGraphAm` (`FBNGP_Q_GRAPH_AM`) — camembert, `MetaData.Set(GraphAssetAllocation, PieChart)`, template `SUBTPL_FBNGPQGraphAm`.

### Template

`TPL_FBNGPAssetAllocationQuarterly` : template minimal, `CreateConditions()` n'appelle que
`recordSetCondition.CreateGenericSourceCondition()`. Logique métier déléguée au data entry point
(`FBNGPAssetMixEntryPoint`) et aux sous-rapports.

### Configurations visuelles

- `PAGE_ORIENTATION` = `Landscape` (paysage)
- `REPORT_TITLE` = `RPT_mgr_tit_GFBNGPQAssetMix` (« RÉPARTITION D'ACTIFS DU PORTEFEUILLE »)

## Résumé

`FBNGP_Q_ASSETMIX` est un rapport système trimestriel du package FBN GP1859 qui affiche la répartition
d'actifs d'un portefeuille sous forme de camembert, précédé d'un en-tête, en orientation paysage. Il
expose deux paramètres visibles (date de fin par défaut à la fin du trimestre précédent, et une case à
cocher d'objectif de placement visible uniquement en contexte Relation). Les 19 paramètres POST sont
majoritairement déclaratifs (prefs, constantes de devise, identifiants de vue). La migration se
concentre sur quelques valeurs de configuration spécifiques FBN et une VPF de date.

## ValueProviderFunctions (VPF)

> Note méthodologique : le framework C# résout le VPF via le named parameter `valueProviderFunction:`
> du `*ParametersImplementation.cs` (défaut) ou la propriété `ValueProviderFunction` de `Parameters.cs`.
> Le `ValidationFunction` de `Parameters.cs` **n'est pas** la clé de lookup (config C++ préservée).

### Catégorie A — VPF déjà existante (réutilisation)

| Paramètre | Étape | Widget | VPF C# existante | Statut |
|-----------|-------|--------|------------------|--------|
| `Hided_PARAM_MutFundBreakDown` | POST | Hidden | `FalseParameter` (`CheckFalse`) | Le défaut `valueProviderFunction: "MutualFundBreakDown"` est **dynamique** ; le rapport force `CheckFalse`. **Action : ajouter `ValueProviderFunction = "CheckFalse"` dans Parameters.cs** pour surcharger le défaut (rappel : `ValueProviderFunction = ""` ne bypasse pas). |

### Catégorie B — Constante simple : `InitialValue` dans Parameters.cs

| Paramètre | Étape | Widget | Function C++ | InitialValue à mettre |
|-----------|-------|--------|--------------|-----------------------|
| `PARAM_DontDisplayKeyInHeader` | POST | Hidden | `CheckTrue` (aucun `initialValue:` dans l'impl) | `"1"` |
| `PARAM_HideMinMaxTarget` | POST | Hidden | Specific `CheckTrue` (défaut impl = CheckFalse) | `"1"` |
| `PARAM_DataEntryPoint` | POST | Hidden | `FBNGPAssetMixEntryPoint` → `"ASMS_ObjTargetLvl1,ASMS_DisplayColorLvl1"` | `"ASMS_ObjTargetLvl1\|ASMS_DisplayColorLvl1"` |
| `PARAM_RPTSubId` | POST | Hidden | `FBNGPQAssetMixSubRptField` → `"ASMS_ObjTargetLvl1,ASMS_DisplayColorLvl1,RPT_V_AccClassTypeSpec"` | `"ASMS_ObjTargetLvl1\|ASMS_DisplayColorLvl1\|RPT_V_AccClassTypeSpec"` |
| `PARAM_ReportViewIdentifier` | POST | Hidden | `SetFBNGPQAssetMixViewIdentifier` → chaîne constante | `"ASMS_ObjTargetLvl1:AssetMixSummaryDetails\|ASMS_DisplayColorLvl1:AssetMixSummaryGroupedDetails\|RPT_V_AccClassTypeSpec:ReportAccountTypeReportDetails"` |

> Conversion `,` → `|` obligatoire pour les listes (CLAUDE.md). Chaque `InitialValue` doit être accompagné
> d'un commentaire de traçabilité citant la fonction C++ source et la valeur `,`-séparée d'origine.
> Alternative pour les identifiants de vue / entry points : enregistrer un `StringParameter` dans le
> Post-executer (convention existante : `SetCorpAsmRptViewIdentifier`, `SetTransReportViewIdentifier`) —
> à trancher en implémentation selon la cohérence recherchée.

### Catégorie C — NOUVELLES VPF à créer (logique dynamique)

#### 1. `EndOfLastQuarterParameter` (PRE, Date)

**Paramètre concerné** : `PARAM_EndDate`

**Logique C++** ([validation_date.c:887](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_date.c)) :
```
SetInit(EndOfLastQuarter);            // initialise à la fin du dernier trimestre complet
SetValidation(EvalEndDateBeforeStartDate);  // N/A ici : aucun PARAM_StartDate dans le rapport
SetGetValue(GetBatchEndDate);         // ⚠️ getter batch-aware : en mode batch, prend la BATCH END DATE
```

**Classe C# à créer** : `Parameters/Date/EndOfLastQuarterParameter.cs`
- Dépendances : `IParameterDateValueService` + `IDateTimeService` (calcul de fin de trimestre à placer
  dans `DateTimeService` si absent) + `string dateTimeFormat` (constructeur dual).
- Logique : retourner la date de fin du dernier trimestre complet.
- **⚠️ Batch-aware (obligatoire)** : le C++ utilise `SetGetValue(GetBatchEndDate)` → la VPF C# **doit**
  être enveloppée dans le décorateur `BatchEndOverride(...)` à l'enregistrement, afin qu'en génération
  batch la valeur soit surchargée par la batch end date. Modèle exact des autres VPF de date de fin :
  ```csharp
  implementationsDictionary["EndOfLastQuarter"] = () =>
      BatchEndOverride(new EndOfLastQuarterParameter(parameterDateValueService, dateTimeService, DateTimeFormat.API_LONG_DATE_STANDARD));
  ```
  (Si le C++ utilisait `GetBatchStartDate` → `BatchStartOverride`.)
- Étape : **PRE**, format `API_LONG_DATE_STANDARD` (`yyyy-MM-dd`) ; enregistrer une variante POST
  `REPORT_SERVER_STANDARD` (`BatchEndOverride` version POST) seulement si nécessaire.
- Enregistrement : clé `"EndOfLastQuarter"` dans le **Pre**-executer + `ValueProviderFunction = "EndOfLastQuarter"` dans Parameters.cs.
- Note : la validation `EvalEndDateBeforeStartDate` ne s'applique pas (pas de `PARAM_StartDate`).
- ⚠️ Vérifier si `LastQuarterEndDateParameter` (déjà enregistré sous `LastQuarterEndDate`, lui aussi
  wrappé dans `BatchEndOverride`) calcule exactement la même date « fin du dernier trimestre » — si oui,
  réutiliser sa logique / le `DateTimeService` sous-jacent plutôt que dupliquer.

#### 2. `UseFBNGP1859RepartitionParameter` (POST, Hidden)

**Paramètre concerné** : `H_PARAM_AssetMixRepartType`

**Logique C++** ([validation_hided.c:15864](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_hided.c)) :
```
pAtt->SetValue( DESC_REPARTITION_GP1859 );  // description de répartition (constante #define)
```

**Classe C# à créer** : `Parameters/Hidden/UseFBNGP1859RepartitionParameter.cs`
- Dépendances : `IRepartitionService` (résolution de la répartition prédéfinie GP1859 par description).
- Logique : positionner `PARAM_AssetMixRepartType` sur la répartition GP1859 (voir CLAUDE.md, tableau
  `PARAM_AssetMixRepartType` 6 patterns — pattern « UseFBNGP1859Repartition »).
- Enregistrement : clé `"UseFBNGP1859Repartition"` dans le **Post**-executer + `ValueProviderFunction`
  dans Parameters.cs.
- ⚠️ **Valeur non résolue** : le `#define DESC_REPARTITION_GP1859` n'est pas présent dans les fichiers
  accessibles du workspace (voir Limites). Résoudre la description exacte avant implémentation.

#### 3. `AssetMixSumGP1859SpecificJoinParameter` (POST, Hidden)

**Paramètre concerné** : `PARAM_AddSpecificJoin`

**Logique C++** ([validation_hided.c:9009](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_hided.c)) :
```
switch (GetPad()) {
  case REPORT_CLIENT:  "ASMS_ObjTargetLvl1:ASSET_MIX_SUM_GP1859-CLIENT,ASMS_DisplayColorLvl1:ASSET_MIX_SUM_GP1859-CLIENT"
  case REPORT_ACCOUNT: "...-ACCOUNT,...-ACCOUNT"
  case REPORT_LINK:    "...-LINK,...-LINK"
  case REPORT_PORTEF / SECURITY / ... : break (aucune valeur)
}
```

**Classe C# à créer** : `Parameters/Hidden/AssetMixSumGP1859SpecificJoinParameter.cs`
- Dépendances : `IReportCommandAndQueryContextRepository.RequestSourceType` (mapping SourceType → pad).
- Logique : selon le contexte source (Client/Account/Relation), retourner la chaîne de join
  correspondante (convertir `,` → `|`). Similaire au VPF existant `EvalSpecificJoinParameter`.
- Enregistrement : clé `"AssetMixSumGP1859SpecificJoin"` dans le **Post**-executer + `ValueProviderFunction` dans Parameters.cs.
- ⚠️ **Bug C++ à décider** : les `case` n'ont pas de `break` (fall-through) → en C++, CLIENT et ACCOUNT
  retombent sur la valeur LINK. Déterminer avec l'équipe s'il faut reproduire ce comportement legacy ou
  corriger (mapper chaque pad à sa vraie valeur). **À valider avec le développeur.**

### Catégorie D — Déjà déclaratif (pas d'action)

| Paramètre | Étape | Widget | Configuration |
|-----------|-------|--------|---------------|
| `PARAM_UseRepartitionFromInvObj` | PRE | CheckBox | `valueProviderFunction: "CheckFalseVisibleForRelOnly"` (existe), `initialValue: "0"`, `possibleValues {0,1}` |
| `PARAM_ReportPad` | POST | Hidden | `valueProviderFunction: "GetPad"` (existe) |
| `PARAM_ReportTitle` | POST | Hidden | `valueProviderFunction: "ReportTitle"` (existe) — ⚠️ diff connue Conseiller/Xpert |
| `PARAM_FirmCurrency` | POST | Hidden | `valueProviderFunction: "FirmCurrency"`, `initialValue: "CAD"` |
| `PARAM_IgnoreIdMasking` | POST | Hidden | `valueProviderFunction: "GetDisplayUnmaskedId"`, `initialValue: "0"` — voir note ci-dessous |
| `PARAM_DisableParamButton` | POST | Hidden | `initialValue: "0"` |
| `PARAM_DisplayDateAndTime` | POST | Hidden | `initialValueFromPref: "PREF_REPORT_DISPLAY_DATE_TIME"` |
| `PARAM_DisplayFirmName` | POST | Hidden | `initialValueFromPref: "PREF_REPORT_DISPLAY_FIRM_NAME"` |
| `PARAM_HideTitleCurrency` | POST | Hidden | `initialValueFromPref: "PREF_REPORT_HIDE_CURRENCY"` |
| `PARAM_ForceCurrency` | POST | Hidden | `initialValue: "DEFAULT"` |
| `PARAM_IncludeCoverPage` | POST | Hidden | `initialValue: "0"` (Specific `CheckFalse` = défaut) |
| `PARAM_UseNbPageTotal` | POST | Hidden | `initialValue: "0"` |

> **Note `PARAM_IgnoreIdMasking`** : le paramètre a `initialValue: "0"`. Utiliser le skill
> `register-ignore-id-masking` pour ajouter `FBNGP_Q_ASSETMIX` dans `GetDisplayUnmaskedIdParameter`
> (`ReportsWithInitialValueZero`) et son `InlineData` de test.

### Synthèse migration

- **Réutilisation VPF (A)** : 1 action (`Hided_PARAM_MutFundBreakDown` → override `CheckFalse`)
- **InitialValue uniquement (B)** : 5 (`DontDisplayKeyInHeader`, `HideMinMaxTarget`, `DataEntryPoint`, `RPTSubId`, `ReportViewIdentifier`)
- **Nouvelles VPF à créer (C)** : 3 (`EndOfLastQuarterParameter`, `UseFBNGP1859RepartitionParameter`, `AssetMixSumGP1859SpecificJoinParameter`)
- **Déjà déclaratif (D)** : 12

Étapes d'enregistrement complémentaires : `register-web-report` (WebRTMRunner), `activate-web-report-pref`,
`register-ignore-id-masking`, `update-e2e-baselines`.

## Limites de l'analyse

- ⚠️ **`#define DESC_REPARTITION_GP1859` non résolu** : introuvable dans les fichiers accessibles du
  workspace (`CroesusServer/Src/**`). La valeur/description exacte de la répartition GP1859 utilisée par
  `UseFBNGP1859Repartition` doit être confirmée avant l'implémentation de la Catégorie C #2.
- ⚠️ **Fall-through C++ dans `AssetMixSumGP1859SpecificJoin`** : les `case` sans `break` produisent, en
  C++, la valeur LINK pour tous les pads Client/Account/Link. Comportement à confirmer (legacy vs bug) —
  à valider avec le développeur avant de figer la logique C#.
- Les templates de sous-rapports (`SUBTPL_FBNGPQHeader`, `SUBTPL_FBNGPQGraphAm`) n'ont pas été lus en
  détail (structure de dessin) — hors périmètre backend paramètres.
- Confluence non consulté (aucune recherche lancée).
- Rendu visuel réel (contenu du camembert, en-tête FBN) non vérifiable sans génération.
