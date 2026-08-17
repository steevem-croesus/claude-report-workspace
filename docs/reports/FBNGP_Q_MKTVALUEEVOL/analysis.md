# Analyse du rapport FBNGP_Q_MKTVALUEEVOL

## Description utilisateur (spec fonctionnelle)

### À quoi sert ce rapport

**Évolution de la valeur de marché** (EN : *Evolution of Market Value*, titre imprimé FR : *ÉVOLUTION DE LA VALEUR MARCHANDE PAR COMPTE*) est un relevé **trimestriel** du package de rapports **Gestion privée 1859 (GP1859) de la Banque Nationale (FBN)**. Pour chaque compte, il présente la **réconciliation de la valeur de marché entre le début et la fin du dernier trimestre complet** : valeur de départ, mouvements (dépôts, retraits, transferts nets), revenus (intérêts payés/reçus, dividendes, distributions), frais (gestion, autres), taxes, appréciation du capital, puis valeur de marché de fin et gain/perte réalisé.

Le rapport est un **rapport système** (`ApplySystemReport = true`), généré dans le cadre du package trimestriel GP1859 (typiquement en lot/batch), et non librement sélectionnable au niveau Relation/Client/Compte/Portefeuille dans l'UI standard (toutes les visibilités sont à `N`).

### Contexte d'utilisation

- **Activation** : nécessite **deux** préférences activées simultanément — `PREF_REPORT_FBNGP_Q_MKTVALUEEVOL=YES` **et** `PREF_QUARTERLY_REPORT_GP1859=YES`. Sans elles, le rapport n'est pas disponible.
- **Niveau d'usage** : rapport par **compte** (les données et colonnes sont préfixées `AME_` = *Account Market Evolution*). Les visibilités Link/Client/Account/Portfolio sont toutes à `N` → orchestration par le package GP1859, pas de sélection directe.
- **Période par défaut** : le **dernier trimestre complet** — date de début = début du dernier trimestre (`BegOfLastQuarter`), date de fin = fin du dernier trimestre (`EndOfLastQuarter`).

### Ce que l'utilisateur voit en sortie

Rapport en orientation **paysage**, police 8 pt. Pour chaque compte (une section par compte, avec saut de page réglé tous les 7 blocs) :

1. **En-tête de compte** — numéro de compte (masqué) et type de compte.
2. **Valeur de marché de départ** (début de trimestre).
3. **Détail des mouvements et revenus/frais du trimestre** : dépôts, retraits, transferts nets, intérêts payés, intérêts reçus, dividendes, distributions de titres, frais de gestion, autres revenus/frais, taxes, appréciation du capital.
4. **Valeur de marché de fin** (fin de trimestre).
5. **Gain/perte réalisé**.

Un sous-rapport d'en-tête partagé du package (`SUB_FBNGPQHeader` / `FBNGP_Q_RPT_HEADER`) fournit l'en-tête trimestriel commun.

### Options de configuration (paramètres visibles à l'utilisateur)

| Option | Type | Comportement |
|--------|------|--------------|
| Date de début | Date | Par défaut : début du dernier trimestre complet |
| Date de fin | Date | Par défaut : fin du dernier trimestre complet ; ne peut pas être antérieure à la date de début |
| Méthode de calcul du coût | Radio | *Coût moyen (ACB)* ou *Coût d'investissement* ; par défaut *Coût moyen (ACB)*. Disponible uniquement si la préférence de lots fiscaux est désactivée (`PREF_TAX_LOT=NO`) |

> ⚠️ Ces trois paramètres sont techniquement des paramètres PRE (widgets Date/Radio). Compte tenu du caractère « rapport système » (visibilités `N`), leur exposition réelle dans l'UI Xpert reste à confirmer avec l'équipe.

### Comportements interactifs (règles UI)

- **Cohérence des dates** : quand l'utilisateur modifie la date de fin, elle ne peut pas être antérieure à la date de début (et réciproquement). La génération est bloquée tant que l'intervalle est invalide.

### Préférences administratives qui influencent le rapport

- **Masquer la devise dans le titre** (`PREF_REPORT_HIDE_CURRENCY`) : masque/affiche la devise dans le titre.
- **Afficher le nom de la firme** (`PREF_REPORT_DISPLAY_FIRM_NAME`) : affiche/masque le nom de la firme.
- **Afficher la date et l'heure** (`PREF_REPORT_DISPLAY_DATE_TIME`) : affiche/masque l'horodatage de génération.

---

## Identité

- **Template ID** : `5000115`
- **Nom interne** : `FBNGP_Q_MKTVALUEEVOL`
- **Classe C#** : `RPT_FBNGPEvolutionOfMarketValue` (hérite de `ReportImplementation`)
- **Fichier** : [RPT_FBNGPEvolutionOfMarketValue.cs](../../../ReportFoundations/ReportImplementations/Implementations/Reports/Main/FBN/EvolutionOfMarketValue/RPT_FBNGPEvolutionOfMarketValue.cs)
- **Template** : `TPL_FBNGPEvolutionOfMarketValue` ([TPL_FBNGPEvolutionOfMarketValue.cs](../../../ReportFoundations/ReportImplementations/Templates/Main/FBN/EvolutionOfMarketValue/TPL_FBNGPEvolutionOfMarketValue.cs))
- **Sub-reports** : `SUB_FBNGPQHeader` (nom interne `FBNGP_Q_RPT_HEADER`)
- **Type** : `ReportTypes.Standard`, `ApplySystemReport = true`

## Noms (Resource.*.resx)

| Clé | EN | FR |
|-----|----|----|
| `RPT_mgr_rpt_GFBNGPQAccountMarketValueEvolution` | Evolution of Market Value | Évolution de la valeur de marché |
| `RPT_mgr_tit_GFBNGPQAccountMarketValueEvolution` | ACCOUNT ACTIVITY | ÉVOLUTION DE LA VALEUR MARCHANDE PAR COMPTE |

## Activation et visibilité

- `PrefValidation = "PREF_REPORT_FBNGP_Q_MKTVALUEEVOL=YES,PREF_QUARTERLY_REPORT_GP1859=YES"`
- `IsLinkVisible="N"`, `IsClientVisible="N"`, `IsAccountVisible="N"`, `IsPortfolioVisible="N"`
- `HelpToken` : non défini dans `InitHeader`
- `ApplySystemReport = true` (rapport système / package batch)

## Paramètres

**Total : 18 paramètres** (3 PRE + 15 POST)

### PRE — visibles dans l'UI

| # | Paramètre | Étape | Widget | Default_Function | Specific_Function |
|---|-----------|-------|--------|------------------|-------------------|
| 1 | `PARAM_AvgCostCalculMethod` | PRE | Radio | `CostCalculation` | *(vide)* |
| 2 | `PARAM_StartDate` | PRE | Date | `StartMonthDate` | `BegOfLastQuarter` |
| 3 | `PARAM_EndDate` | PRE | Date | `EndMonthDate` | `EndOfLastQuarter` |

### POST — Hidden (15 paramètres)

Tous les paramètres POST ont le widget **Hidden** (`PARAMETER_ENTRY_TYPE = 8`).

**Identité / structure du rapport**

| Paramètre | Étape | Widget | Function (Default → Specific) |
|-----------|-------|--------|-------------------------------|
| `PARAM_DataEntryPoint` | POST | Hidden | *(vide)* → `FBNGPAccountMarketEvolutionEntryPoint` |
| `PARAM_RPTSubId` | POST | Hidden | *(vide)* → `FBNGPQAccountMarketEvolutionSubRptField` |
| `PARAM_ReportViewIdentifier` | POST | Hidden | `SetReportViewIdentifier` → `SetFBNGPAccountMarketEvolutionViewIdentifier` |
| `PARAM_AddSpecificJoin` | POST | Hidden | *(vide)* → `FbnGpQPortfSpecificJoin` |
| `H_PARAM_AssetMixRepartType` | POST | Hidden | `UseMaturityRepartition` → `UseFBNGP1859Repartition` |
| `PARAM_ReportTitle` | POST | Hidden | `ReportTitle` → *(vide)* |

**Affichage / titre**

| Paramètre | Étape | Widget | Function (Default → Specific) |
|-----------|-------|--------|-------------------------------|
| `PARAM_HideTitleCurrency` | POST | Hidden | `GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)` → *(vide)* |
| `PARAM_DisplayFirmName` | POST | Hidden | `GetBoolFromPref(PREF_REPORT_DISPLAY_FIRM_NAME)` → *(vide)* |
| `PARAM_DisplayDateAndTime` | POST | Hidden | `GetBoolFromPref(PREF_REPORT_DISPLAY_DATE_TIME)` → *(vide)* |
| `PARAM_DontDisplayKeyInHeader` | POST | Hidden | `CheckTrue` → *(vide)* |
| `PARAM_UseNbPageTotal` | POST | Hidden | `CheckFalse` → *(vide)* |

**Comportement / divers**

| Paramètre | Étape | Widget | Function (Default → Specific) |
|-----------|-------|--------|-------------------------------|
| `PARAM_FirmCurrency` | POST | Hidden | `GetFirmCurrency` → *(vide)* |
| `PARAM_IgnoreIdMasking` | POST | Hidden | `GetDisplayUnmaskedId` → *(vide)* |
| `PARAM_UseLinkMgtDates` | POST | Hidden | `CheckFalse` → `CheckTrue` |
| `PARAM_DisableParamButton` | POST | Hidden | `CheckFalse` → *(vide)* |

## Préférences impliquées

### Activation (header.PrefValidation)

- `PREF_REPORT_FBNGP_Q_MKTVALUEEVOL` — active spécifiquement ce rapport.
- `PREF_QUARTERLY_REPORT_GP1859` — active le package trimestriel GP1859. Les deux sont requises (AND).

### Runtime — POST params via `GetBoolFromPref(...)`

- `PREF_REPORT_HIDE_CURRENCY` → `PARAM_HideTitleCurrency` (masque la devise du titre)
- `PREF_REPORT_DISPLAY_FIRM_NAME` → `PARAM_DisplayFirmName` (affiche le nom de firme)
- `PREF_REPORT_DISPLAY_DATE_TIME` → `PARAM_DisplayDateAndTime` (affiche date/heure de génération)

### UI logic — lues dans la config des widgets

- `PREF_TAX_LOT` — pref d'activation du widget radio `PARAM_AvgCostCalculMethod` (`PREF_TAX_LOT=NO` → le radio est disponible ; source : `RadioParametersImplementation.cs`). Aucune règle inter-champ Observer détectée pour ce paramètre dans `win_prm_grp_*.c`.

## Comportements UI (Observer patterns)

### 1. Validation de plage de dates StartDate / EndDate

Source : [win_prm_grp_date.c:~440-540](../../../CroesusServer/Src/ReportApi/ReportView/ReportViewParam/win_prm_grp_date.c) + dispatch [validation_date.c:891](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_date.c#L891)

Le rapport possède `PARAM_StartDate` **et** `PARAM_EndDate`. Le dispatch de `EndOfLastQuarter` enregistre `EvalEndDateBeforeStartDate` (`SetValidation`), et le groupe de dates générique (`win_prm_grp_date.c`) échange les valeurs entre les deux champs (`WATCH_START_DATE_VALUE` / `WATCH_END_DATE_VALUE`). Effet : la date de fin ne peut pas être antérieure à la date de début.

**Migration frontend** : ajouter `rangeDateValidator(START_DATE, END_DATE)` + le pattern `formValidity$` (voir convention CLAUDE.md « Validation dates StartDate/EndDate »).

> Aucun autre pattern Observer détecté : `PARAM_AvgCostCalculMethod` n'apparaît dans aucun `win_prm_grp_*.c`.

## Contenu du rapport

### Colonnes

Toutes les colonnes sont déclarées avec `IsAvailable = new BooleanFormula(true)` et `SummaryType = null` (pas de totalisation de tableau classique — le rendu est **columnar**, piloté par le template). Colonnes source (préfixe `AME_` = *Account Market Evolution*) :

| Colonne | Rôle |
|---------|------|
| `AME_AccountCurrency` | Devise du compte |
| `AME_AccountNumber` / `AME_AccountNumberMasked` | Numéro de compte (brut / masqué) |
| `AME_AccountType` | Type de compte |
| `AME_DisplayOrder` | Ordre d'affichage (tri + groupage par blocs de 7) |
| `AME_StartingMarket` | Valeur de marché de départ |
| `AME_EndingMarket` | Valeur de marché de fin |
| `AME_CapitalAppreciation` | Appréciation du capital |
| `AME_GainLoss` | Gain/perte réalisé |
| `AME_TotalDeposits` / `AME_TotalWithdrawals` | Dépôts / retraits |
| `AME_TotalCreditingTransfers` / `AME_TotalDebitingTransfers` | Transferts entrants / sortants (→ transferts nets) |
| `AME_TotalPaidInterests` / `AME_TotalInterestsReceived` | Intérêts payés / reçus |
| `AME_TotalDividends` / `AME_TotalDistribution` | Dividendes / distributions |
| `AME_TotalManagementFees` / `AME_TotalOtherFees` | Frais de gestion / autres frais |
| `AME_TotalTaxes` | Taxes |

> **Aucun corps tabulaire classique** avec totalisation. Le rendu vient d'un layout **columnar** (deux tables virtuelles : `mainTable` valeurs de marché début/fin, `secTable` détail des mouvements) trié par `AME_DisplayOrder`.

### Template

`TPL_FBNGPEvolutionOfMarketValue` : condition minimale (`recordSetCondition.CreateGenericSourceCondition()`) — logique métier déléguée au `DataEntryPoint` `AME_StartingMarket` et aux fonctions de rendu (`FBNGPQMVE*`). Corps columnar, saut de page tous les 7 blocs (`AME_DisplayOrder`, calcul `(AME_DisplayOrder - 1) / 7`, ref. CROES-12013 / CR-875).

### Configurations visuelles

- Police : 8 pt (`FONT_SIZE`)
- Hauteur minimale du corps : 7780 (`MINIMUM_BODY_HEIGHT`)
- Orientation : **Paysage** (`PAGE_ORIENTATION`)
- Titre : `RPT_mgr_tit_GFBNGPQAccountMarketValueEvolution`

### Sous-rapports

- `SUB_FBNGPQHeader` (`FBNGP_Q_RPT_HEADER`) — en-tête trimestriel partagé du package GP1859 (template `SUBTPL_FBNGPQHeader`), également utilisé par les autres rapports FBN GP1859 (AssetAllocationQuarterly, TransactionsQuarterly, GainsAndLossesQuarterly, etc.).

## Résumé

Relevé trimestriel système du package GP1859 (FBN) présentant, par compte, la réconciliation de la valeur de marché entre le début et la fin du dernier trimestre complet (mouvements, revenus, frais, taxes, appréciation, gain/perte). Très peu de paramètres interactifs (dates + méthode de coût), l'essentiel étant des paramètres POST cachés qui figent l'entry point, le sub-report field, le view identifier, la répartition GP1859 et le join spécifique. La majeure partie de l'effort backend porte sur 3 fonctions POST FBN-spécifiques (constantes) et 2/3 VPF de dates de trimestre (réutilisation probable des classes existantes).

## ValueProviderFunctions (VPF)

### Catégorie A — VPF déjà existante (réutilisation)

| Paramètre | Étape | Widget | VPF C# existante | Statut |
|-----------|-------|--------|------------------|--------|
| `PARAM_ReportTitle` | POST | Hidden | `ReportTitleParameter` | Câblé via le défaut (`valueProviderFunction: "ReportTitle"`). ⚠️ différence connue Conseiller/Xpert. |
| `PARAM_FirmCurrency` | POST | Hidden | `FirmCurrencyParameter` | Câblé via le défaut (`valueProviderFunction: "FirmCurrency"`, `initialValue: "CAD"`). |
| `PARAM_IgnoreIdMasking` | POST | Hidden | `GetDisplayUnmaskedIdParameter` | Câblé via le défaut. **Action** : ajouter `FBNGP_Q_MKTVALUEEVOL` à `ReportsWithInitialValueZero` (skill `register-ignore-id-masking`) pour matcher le défaut C++ masqué (`initialValue "0"`). Actuellement absent → renverrait `"1"` (non masqué). |

### Catégorie B — Constante simple : pas de VPF, juste `InitialValue`

| Paramètre | Étape | Widget | Function C++ | InitialValue à mettre |
|-----------|-------|--------|--------------|-----------------------|
| `PARAM_DataEntryPoint` | POST | Hidden | `FBNGPAccountMarketEvolutionEntryPoint` ([validation_hided.c:2078](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_hided.c#L2078)) | `"AME_StartingMarket"` |
| `PARAM_RPTSubId` | POST | Hidden | `FBNGPQAccountMarketEvolutionSubRptField` ([validation_hided.c:16005](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_hided.c#L16005)) | `"AME_StartingMarket"` |
| `PARAM_ReportViewIdentifier` | POST | Hidden | `SetFBNGPAccountMarketEvolutionViewIdentifier` ([validation_hided.c:15950](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_hided.c#L15950)) | `"AME_StartingMarket:AccountMarketEvolution"` |
| `PARAM_DontDisplayKeyInHeader` | POST | Hidden | `CheckTrue` (défaut, sans `initialValue`) | `"1"` |
| `PARAM_UseLinkMgtDates` | POST | Hidden | `CheckTrue` (Specific ; défaut Hidden = `CheckFalse` sans `initialValue`) | `"1"` |
| `H_PARAM_AssetMixRepartType` | POST | Hidden | `UseFBNGP1859Repartition` → `SetValue(DESC_REPARTITION_GP1859)` ([validation_hided.c:15864](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_hided.c#L15864)) | ⚠️ valeur du `#define DESC_REPARTITION_GP1859` **non résolue** dans le code accessible (voir Limites) — description de la répartition GP1859. À résoudre avant implémentation. |

### Catégorie C — NOUVELLES VPF à créer (logique dynamique / à valider)

#### 1. `BegOfLastQuarterParameter` (PRE)

**Paramètre(s) concerné(s)** : `PARAM_StartDate`

**Logique C++** ([validation_date.c:4598](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_date.c#L4598)) : début du **dernier trimestre complet**. Prend la batch start date (sinon `sys_date_fin`), recule d'un trimestre (`mois = ((month-1)/3)*3+1 - 3`, avec report d'année si négatif), positionne au 1er du mois.

**Classe C# à créer** : `Parameters/Date/BegOfLastQuarterParameter.cs`
- Dépendances : `IParameterDateValueService`, `IDateTimeService`
- Étape : **PRE** → format `DateTimeFormat.API_LONG_DATE_STANDARD` (`yyyy-MM-dd`) ; variante POST BatchDateOverride si exposé en batch
- Enregistrement : `PreParamEntryValueProviderFunctionsExecuter` (+ POST si nécessaire)
- ⚠️ **Réutilisation probable** : `LastQuarterStartDateParameter` (fonction C++ jumelle `DebutDernierTrimestre` via `LastQuarterStartDate`) implémente la même sémantique « début du dernier trimestre ». Comparer point par point avant de créer une nouvelle classe (candidat Catégorie A).

#### 2. `EndOfLastQuarterParameter` (PRE)

**Paramètre(s) concerné(s)** : `PARAM_EndDate`

**Logique C++** ([validation_date.c:4647](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_date.c#L4647)) : fin du **dernier trimestre complet**. Prend la batch end date (sinon `sys_date_fin`) ; si déjà une fin de trimestre (31/03, 30/06, 30/09, 31/12) on la conserve, sinon on calcule le début du trimestre courant et on recule d'un jour. Enregistre aussi la validation `EvalEndDateBeforeStartDate`.

**Classe C# à créer** : `Parameters/Date/EndOfLastQuarterParameter.cs`
- Dépendances : `IParameterDateValueService`, `IDateTimeService`
- Étape : **PRE** → format `DateTimeFormat.API_LONG_DATE_STANDARD` ; variante POST BatchDateOverride si exposé en batch
- Enregistrement : `PreParamEntryValueProviderFunctionsExecuter` (+ POST si nécessaire)
- ⚠️ **Réutilisation probable** : `LastQuarterEndDateParameter` (fonction C++ jumelle `FinDernierTrimestre` via `LastQuarterEndDate`, qui porte aussi `EvalEndDateBeforeStartDate`) implémente la même sémantique. Comparer avant de créer (candidat Catégorie A).

#### 3. `FbnGpQPortfSpecificJoinParameter` (POST)

**Paramètre(s) concerné(s)** : `PARAM_AddSpecificJoin`

**Logique C++** ([validation_hided.c:9076](../../../CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_hided.c#L9076)) : `switch` sur le pad du rapport (CLIENT/ACCOUNT/LINK) **sans `break`** (fall-through) → quel que soit le pad parmi ces trois, la valeur finale retenue est celle de `REPORT_LINK` : `"PERH_Type:PERFO_HISTO-LINK,PERH_Type:PERFO_HISTO-REPORT_VIRTUAL,PY_StartingMarketCol1:PORTFOLIO_YMV-REPORT_VIRTUAL"`.

**Classe C# à créer** : `Parameters/Hidden/FbnGpQPortfSpecificJoinParameter.cs`
- Dépendances : `IReportCommandAndQueryContextRepository` (pad/source)
- Logique : reproduire le comportement C++ (attention au fall-through) ; réutiliser le pattern des VPF existantes `EvalSpecificJoinParameter` / `InfoClientSpecificJoinParameter`
- Étape : **POST**
- Enregistrement : `PostParamEntryValueProviderFunctionsExecuter`
- ⚠️ À valider avec le développeur : le pad effectif d'un rapport système GP1859 et l'intention du fall-through (potentiel bug C++ historique).

### Catégorie D — Déjà déclaratif (pas d'action)

| Paramètre | Étape | Widget | Configuration |
|-----------|-------|--------|---------------|
| `PARAM_AvgCostCalculMethod` | PRE | Radio | `RadioParametersImplementation.cs` : `initialValue: "COST_CALC_ACB"`, `possibleDisplayValues` = ACB/INVEST, activation `PREF_TAX_LOT=NO`. Note web : valeur initiale toujours Book Value, modifiable par l'utilisateur. |
| `PARAM_HideTitleCurrency` | POST | Hidden | `initialValueFromPref: "PREF_REPORT_HIDE_CURRENCY"` |
| `PARAM_DisplayFirmName` | POST | Hidden | `initialValueFromPref: "PREF_REPORT_DISPLAY_FIRM_NAME"` |
| `PARAM_DisplayDateAndTime` | POST | Hidden | `initialValueFromPref: "PREF_REPORT_DISPLAY_DATE_TIME"` |
| `PARAM_UseNbPageTotal` | POST | Hidden | `CheckFalse`, `initialValue: "0"` |
| `PARAM_DisableParamButton` | POST | Hidden | `CheckFalse`, `initialValue: "0"` |

### Synthèse migration

- **Réutilisation VPF** : 3 (`ReportTitle`, `FirmCurrency`, `GetDisplayUnmaskedId` — + ajout du rapport à `ReportsWithInitialValueZero`)
- **InitialValue uniquement** : 6 (`PARAM_DataEntryPoint`, `PARAM_RPTSubId`, `PARAM_ReportViewIdentifier`, `PARAM_DontDisplayKeyInHeader`, `PARAM_UseLinkMgtDates`, `H_PARAM_AssetMixRepartType` — valeur GP1859 à résoudre)
- **Nouvelles VPF à créer** : 3 (`BegOfLastQuarterParameter`, `EndOfLastQuarterParameter`, `FbnGpQPortfSpecificJoinParameter`) — dont **2 candidates à réutilisation** des classes de trimestre existantes après comparaison
- **Déjà déclaratif** : 6

⚠️ **Pas de pointage / story points dans ce document** — l'estimation est faite par l'équipe en affinage (effet d'ancrage).

## Limites de l'analyse

- **`DESC_REPARTITION_GP1859`** : la valeur de ce `#define` (utilisée par `UseFBNGP1859Repartition` pour `H_PARAM_AssetMixRepartType`) n'a **pas** été trouvée en clair dans le code source accessible (`win_prm_const.h` définit les `DESC_REPARTITION_*` connexes mais pas celui-ci ; il provient probablement de `Foundations/BusinessLogic/Api/BusinessLogicDefs.h`, hors périmètre des symlinks). Valeur à résoudre avant implémentation.
- **Réutilisation dates** : `LastQuarterStartDate`/`LastQuarterEndDate` (C++ `DebutDernierTrimestre`/`FinDernierTrimestre`) sont sémantiquement équivalents à `BegOfLastQuarter`/`EndOfLastQuarter` mais utilisent une init légèrement différente (gestion batch date + garde « déjà fin de trimestre »). Équivalence **à confirmer** par comparaison de code avant de décider réutilisation vs nouvelle classe.
- **Exposition UI Xpert** : le rapport est un rapport système (`ApplySystemReport`, visibilités toutes `N`). L'exposition réelle des 3 paramètres PRE dans le frontend Xpert n'a pas pu être confirmée dans le code.
- **`FbnGpQPortfSpecificJoin`** : le `switch` C++ sans `break` (fall-through) rend le comportement effectivement constant (valeur LINK) — intention historique à valider avec l'équipe.
- **Enregistrement WebRTMRunner** : aucun enregistrement Web trouvé pour `FBNGP_Q_MKTVALUEEVOL` ni pour les rapports frères GP1859 → migration à faire depuis zéro (aucune des fonctions FBN GP1859 spécifiques n'est enregistrée dans les executers C#).
- **Sub-report `SUB_FBNGPQHeader`** : contenu détaillé du template `SUBTPL_FBNGPQHeader` non analysé en profondeur (en-tête partagé du package).
- **Confluence** : non consulté.
