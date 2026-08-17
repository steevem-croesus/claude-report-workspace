# Migration Report: FBNGP_Q_MKTVALUEEVOL (Backend)
**Date:** 2026-07-22 15:38:20
**Mode:** Backend

## Déroulement

- [15:38:00] [ÉTAPE 0] Bootstrap depuis l'analyse — ✓
  - `docs/reports/FBNGP_Q_MKTVALUEEVOL/analysis.md` trouvé
  - Ticket Jira RPT-19560 (En cours) localisé — décisions reprises : réutilisation `LastQuarterStartDate`/`LastQuarterEndDate`, `DESC_REPARTITION_GP1859 = "Allocation - 1859"`, 1 seule classe custom
- [15:38:00] [ÉTAPE 2] Localisation classes C# — ✓
  - `RPT_FBNGPEvolutionOfMarketValue` (hérite de `ReportImplementation`)
  - `.../Reports/Main/FBN/EvolutionOfMarketValue/Parameters.cs`
- [15:38:00] [ÉTAPE 3] Extraction paramètres — ✓ (18 : 3 PRE + 15 POST)
- [15:38:00] [ÉTAPE 4] Analyse et classification — ✓
- [15:38:00] [ÉTAPE 5] Implémentation — ✓
- [15:38:20] [ÉTAPE 6] Build ReportManagerApi (0 erreur) + RTMTester (0 erreur) + tests (55/55) — ✓

## Plan de migration

| Catégorie | Nombre | Paramètres |
|-----------|--------|-----------|
| A — Config framework / déclaratif (commentaire seul) | 9 | AvgCostCalculMethod, DisableParamButton, DisplayDateAndTime, DisplayFirmName, FirmCurrency, HideTitleCurrency, IgnoreIdMasking, ReportTitle, UseNbPageTotal |
| B — InitialValue statique | 6 | H_PARAM_AssetMixRepartType, DataEntryPoint, DontDisplayKeyInHeader, ReportViewIdentifier, RPTSubId, UseLinkMgtDates |
| D — ValueProviderFunction existante | 2 | StartDate (LastQuarterStartDate), EndDate (LastQuarterEndDate) |
| F — Nouvelle classe | 1 | AddSpecificJoin (FbnGpQPortfSpecificJoin) |

---

## Détail par paramètre

### H_PARAM_AssetMixRepartType (1/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.64): `validationFunction: "UseMaturityRepartition", no initialValue, no valueProviderFunction`
- ValidationFunction actuelle: `"UseFBNGP1859Repartition"` (Specific)

**Analyse C++ (UseFBNGP1859Repartition):**
- Fichier: validation_hided.c L.15864
- Comportement: set la constante `DESC_REPARTITION_GP1859` = `"Allocation - 1859"` (description de la répartition GP1859 utilisée pour matcher la répartition côté report server)
- Complexité: Niveau 1

**Décision: Catégorie B — InitialValue statique**
- Raisonnement: constante fixe ; override le défaut `UseMaturityRepartition`. Valeur résolue via RPT-19560 (`BusinessLogicDefs.h`).
- Action: Ajout `InitialValue = "Allocation - 1859"` + commentaire.

**Résultat:**

    ValidationFunction = "UseFBNGP1859Repartition",
    InitialValue = "Allocation - 1859"
    // POST Hidden. In HiddenParametersImplementation.cs: validationFunction: "UseMaturityRepartition", no initialValue, no valueProviderFunction.
    // C++ UseFBNGP1859Repartition (validation_hided.c:15864): set la constante DESC_REPARTITION_GP1859 = "Allocation - 1859" ...

### PARAM_AddSpecificJoin (2/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.112): `no validationFunction, no initialValue, no valueProviderFunction`
- ValidationFunction actuelle: `"FbnGpQPortfSpecificJoin"` (Specific)

**Analyse C++ (FbnGpQPortfSpecificJoin → AddSpecificJoin):**
- Fichier: validation_hided.c L.9076
- Comportement: `switch` sur le pad (CLIENT/ACCOUNT/LINK) **sans break** (fall-through) → retourne toujours la valeur LINK `"PERH_Type:PERFO_HISTO-LINK,PERH_Type:PERFO_HISTO-REPORT_VIRTUAL,PY_StartingMarketCol1:PORTFOLIO_YMV-REPORT_VIRTUAL"`. Pads Portefeuille/Titre → vide.
- Complexité: Niveau 2 (dépend du pad)

**Décision: Catégorie F — Nouvelle classe**
- Raisonnement: logique dynamique (lecture du pad) → VPF obligatoire. Pattern calqué sur `InfoClientSpecificJoinParameter`.
- Action: Création `FbnGpQPortfSpecificJoinParameter` + 7 tests + enregistrement POST executer. Séparateurs C++ `,` → C# `|`.

**Résultat:**

    ValidationFunction = "FbnGpQPortfSpecificJoin",
    ValueProviderFunction = "FbnGpQPortfSpecificJoin"
    // POST Hidden. In HiddenParametersImplementation.cs: no validationFunction, no initialValue, no valueProviderFunction.
    // C++ FbnGpQPortfSpecificJoin (validation_hided.c:9076): switch sur le pad ... (converti , → |). Pads Portefeuille/Titre → vide.

### PARAM_AvgCostCalculMethod (3/18)
**État source:**
- Widget: 2 (Radio) | PRE | Position: 1.1
- RadioParametersImplementation.cs (L.41): `validationFunction: "CostCalculation", initialValue: "COST_CALC_ACB", possibleDisplayValues: ACB/INVEST, activation PREF_TAX_LOT=NO`
- ValidationFunction actuelle: `""`

**Analyse C++ (CostCalculation):**
- Comportement: méthode de calcul du coût. Simplifié côté web (commentaire C#) : valeur initiale toujours Book Value.
- Complexité: Niveau 0 (déclaratif)

**Décision: Catégorie A — Config framework complète**
- Raisonnement: `RadioParametersImplementation.cs` couvre déjà `initialValue` + `possibleDisplayValues`. Specific_Function vide → défaut appliqué.
- Action: Commentaire seul.

**Résultat:**

    ValidationFunction = ""
    // PRE Radio. In RadioParametersImplementation.cs: validationFunction: "CostCalculation", initialValue: "COST_CALC_ACB", ... activation PREF_TAX_LOT=NO.

### PARAM_DataEntryPoint (4/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.134): `no validationFunction, no initialValue, no valueProviderFunction`
- ValidationFunction actuelle: `"FBNGPAccountMarketEvolutionEntryPoint"` (Specific)

**Analyse C++ (FBNGPAccountMarketEvolutionEntryPoint → DataEntryPoint):**
- Fichier: validation_hided.c L.2078 — set la constante `"AME_StartingMarket"`
- Complexité: Niveau 1

**Décision: Catégorie B — InitialValue statique**
- Action: Ajout `InitialValue = "AME_StartingMarket"`.

**Résultat:**

    ValidationFunction = "FBNGPAccountMarketEvolutionEntryPoint",
    InitialValue = "AME_StartingMarket"

### PARAM_DisableParamButton (5/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 2.2
- HiddenParametersImplementation.cs (L.136): `validationFunction: "CheckFalse", initialValue: "0"`
- ValidationFunction actuelle: `""`

**Décision: Catégorie A — Config framework complète**
- Raisonnement: `CheckFalse` set "0", déjà couvert par `initialValue: "0"`.
- Action: Commentaire seul.

**Résultat:**

    ValidationFunction = ""
    // POST Hidden. In HiddenParametersImplementation.cs: validationFunction: "CheckFalse", initialValue: "0".

### PARAM_DisplayDateAndTime (6/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.142): `validationFunction: "GetBoolFromPref(PREF_REPORT_DISPLAY_DATE_TIME)", initialValueFromPref: "PREF_REPORT_DISPLAY_DATE_TIME"`

**Décision: Catégorie A — Config framework complète (pref)**
- Action: Commentaire seul.

### PARAM_DisplayFirmName (7/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.144): `validationFunction: "GetBoolFromPref(PREF_REPORT_DISPLAY_FIRM_NAME)", initialValueFromPref: "PREF_REPORT_DISPLAY_FIRM_NAME"`

**Décision: Catégorie A — Config framework complète (pref)**
- Action: Commentaire seul.

### PARAM_DontDisplayKeyInHeader (8/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 2.2
- HiddenParametersImplementation.cs (L.153): `validationFunction: "CheckTrue", no initialValue, no valueProviderFunction`
- ValidationFunction actuelle: `""`

**Analyse C++ (CheckTrue):** set la valeur constante "1". Complexité: Niveau 0.

**Décision: Catégorie B — InitialValue statique**
- Raisonnement: le défaut n'a pas d'`initialValue` → sans ajout, la valeur serait vide. C++ CheckTrue = "1".
- Action: Ajout `InitialValue = "1"` (réf. PortfolioSummaries/Detailed).

**Résultat:**

    ValidationFunction = "",
    InitialValue = "1"

### PARAM_EndDate (9/18)
**État source:**
- Widget: 5 (Date) | PRE | Position: 2.1
- DateParametersImplementation.cs (L.37): `validationFunction: "EndMonthDate", no initialValue, no valueProviderFunction`
- ValidationFunction actuelle: `"EndOfLastQuarter"` (Specific)

**Analyse C++ (EndOfLastQuarter):**
- Fichier: validation_date.c L.4647 — fin du dernier trimestre complet (garde "déjà fin de trimestre") + validation `EvalEndDateBeforeStartDate`. Base = batch end date sinon `sys_date_fin`.
- Complexité: Niveau 2

**Décision: Catégorie D — ValueProviderFunction existante (réutilisation)**
- Validation C# vs C++: ✓ `LastQuarterEndDateParameter` utilise `GetDateValue(LastProcessedDate)` (= `sys_date_fin` hors batch) + `GetEndDateOfLastQuarter`, sortie `API_LONG_DATE_STANDARD`. Sémantique « fin du dernier trimestre complet » identique.
- Action: Ajout `ValueProviderFunction = "LastQuarterEndDate"` (déjà enregistrée dans PreParamEntry executer).

**Résultat:**

    ValidationFunction = "EndOfLastQuarter",
    ValueProviderFunction = "LastQuarterEndDate"

### PARAM_FirmCurrency (10/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.165): `validationFunction: "GetFirmCurrency", initialValue: "CAD", valueProviderFunction: "FirmCurrency"`

**Décision: Catégorie A — Config framework complète**
- Raisonnement: `valueProviderFunction: "FirmCurrency"` + `initialValue: "CAD"` couvrent déjà.
- Action: Commentaire seul.

### PARAM_HideTitleCurrency (11/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.190): `validationFunction: "GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)", initialValueFromPref: "PREF_REPORT_HIDE_CURRENCY"`

**Décision: Catégorie A — Config framework complète (pref)**
- Action: Commentaire seul.

### PARAM_IgnoreIdMasking (12/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.192): `validationFunction: "GetDisplayUnmaskedId", initialValue: "0", valueProviderFunction: "GetDisplayUnmaskedId"`

**Analyse C++ (GetDisplayUnmaskedId):** masque/démasque l'ID compte. Défaut C++ masqué ("0").

**Décision: Catégorie A — Config framework complète + enregistrement**
- Raisonnement: VPF par défaut `GetDisplayUnmaskedId` déjà câblée. Mais elle renvoie "1" (non masqué) si le rapport n'est pas dans `ReportsWithInitialValueZero`.
- Action: Commentaire seul dans Parameters.cs + ajout de `FBNGP_Q_MKTVALUEEVOL` dans `GetDisplayUnmaskedIdParameter.ReportsWithInitialValueZero` + InlineData test → "0" (masqué, conforme C++).

### PARAM_ReportTitle (13/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.258): `validationFunction: "ReportTitle", valueProviderFunction: "ReportTitle", initialValue: ""`

**Décision: Catégorie A — Config framework complète**
- Raisonnement: `valueProviderFunction: "ReportTitle"` déjà câblée. Différence connue Conseiller/Xpert (non fonctionnelle).
- Action: Commentaire seul.

### PARAM_ReportViewIdentifier (14/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.261): `validationFunction: "SetReportViewIdentifier", no initialValue, no valueProviderFunction`
- ValidationFunction actuelle: `"SetFBNGPAccountMarketEvolutionViewIdentifier"` (Specific)

**Analyse C++ (SetFBNGPAccountMarketEvolutionViewIdentifier):**
- Fichier: validation_hided.c L.15950 — set la constante `"AME_StartingMarket:AccountMarketEvolution"`
- Complexité: Niveau 1

**Décision: Catégorie B — InitialValue statique**
- Action: Ajout `InitialValue = "AME_StartingMarket:AccountMarketEvolution"`.

**Résultat:**

    ValidationFunction = "SetFBNGPAccountMarketEvolutionViewIdentifier",
    InitialValue = "AME_StartingMarket:AccountMarketEvolution"

### PARAM_RPTSubId (15/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.268): `no validationFunction, no initialValue, no valueProviderFunction`
- ValidationFunction actuelle: `"FBNGPQAccountMarketEvolutionSubRptField"` (Specific)

**Analyse C++ (FBNGPQAccountMarketEvolutionSubRptField):**
- Fichier: validation_hided.c L.16005 — set la constante `"AME_StartingMarket"`
- Complexité: Niveau 1

**Décision: Catégorie B — InitialValue statique**
- Action: Ajout `InitialValue = "AME_StartingMarket"`.

**Résultat:**

    ValidationFunction = "FBNGPQAccountMarketEvolutionSubRptField",
    InitialValue = "AME_StartingMarket"

### PARAM_StartDate (16/18)
**État source:**
- Widget: 5 (Date) | PRE | Position: 1.1
- DateParametersImplementation.cs (L.44): `validationFunction: "StartMonthDate", no initialValue, no valueProviderFunction`
- ValidationFunction actuelle: `"BegOfLastQuarter"` (Specific)

**Analyse C++ (BegOfLastQuarter):**
- Fichier: validation_date.c L.4598 — début du dernier trimestre complet. Base = batch start date sinon `sys_date_fin`.
- Complexité: Niveau 2

**Décision: Catégorie D — ValueProviderFunction existante (réutilisation)**
- Validation C# vs C++: ✓ `LastQuarterStartDateParameter` utilise `GetDateValue(LastProcessedDate)` + `GetStartDateOfLastQuarter`, sortie `API_LONG_DATE_STANDARD`. Sémantique identique.
- Action: Ajout `ValueProviderFunction = "LastQuarterStartDate"` (déjà enregistrée PreParamEntry).

**Résultat:**

    ValidationFunction = "BegOfLastQuarter",
    ValueProviderFunction = "LastQuarterStartDate"

### PARAM_UseLinkMgtDates (17/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.293): `validationFunction: "CheckFalse", no initialValue, no valueProviderFunction`
- ValidationFunction actuelle: `"CheckTrue"` (Specific — override)

**Analyse C++ (CheckTrue):** set la valeur constante "1" (override le défaut "0"). Complexité: Niveau 0.

**Décision: Catégorie B — InitialValue statique**
- Action: Ajout `InitialValue = "1"`.

**Résultat:**

    ValidationFunction = "CheckTrue",
    InitialValue = "1"

### PARAM_UseNbPageTotal (18/18)
**État source:**
- Widget: 8 (Hidden) | POST | Position: 1.1
- HiddenParametersImplementation.cs (L.294): `validationFunction: "CheckFalse", initialValue: "0"`
- ValidationFunction actuelle: `""`

**Décision: Catégorie A — Config framework complète**
- Raisonnement: `CheckFalse` = "0", déjà couvert par `initialValue: "0"`.
- Action: Commentaire seul.

---

## Résumé
| Métrique | Valeur |
|----------|--------|
| Paramètres traités | 18/18 |
| Cat. A (framework/déclaratif) | 9 |
| Cat. A' (config incomplète) | 0 |
| Cat. B (InitialValue) | 6 |
| Cat. C (Pref) | 0 |
| Cat. D (VPF existante) | 2 |
| Cat. E (Radio/Combo) | 0 |
| Cat. F (Nouvelle classe) | 1 |
| Fichiers modifiés | 4 |
| Classes créées | 1 (+ 1 classe de tests) |
| Tests ajoutés | 7 (FbnGpQPortfSpecificJoin) + 1 InlineData (GetDisplayUnmaskedId) |
| Traductions | 0 clé (aucune nouvelle) |
| Divergences C++ corrigées | 0 |
| Build ReportManagerApi | ✓ (0 erreur) |
| Build RTMTester | ✓ (0 erreur) |
| Tests | ✓ (55/55 sur le filtre) |

## Fichiers modifiés
- **Modifié** : `ReportFoundations/.../Reports/Main/FBN/EvolutionOfMarketValue/Parameters.cs` (18 paramètres commentés + InitialValue/ValueProviderFunction)
- **Créé** : `ReportManagerApi/.../ValueProviderFunctions/Parameters/Hidden/FbnGpQPortfSpecificJoinParameter.cs`
- **Créé** : `ReportManagerApi/.../SmallTests/.../Parameters/Hidden/FbnGpQPortfSpecificJoinParameterTests.cs`
- **Modifié** : `ReportManagerApi/.../ValueProviderFunctions/PostParamEntryValueProviderFunctionsExecuter.cs` (enregistrement FbnGpQPortfSpecificJoin)
- **Modifié** : `ReportManagerApi/.../Parameters/Hidden/GetDisplayUnmaskedIdParameter.cs` (+ FBNGP_Q_MKTVALUEEVOL)
- **Modifié** : `ReportManagerApi/.../SmallTests/.../GetDisplayUnmaskedIdParameterTests.cs` (+ InlineData)
- **Modifié** : `ReportFoundations/ReportServices/WebRTMRunner.cs` (+ RPT_FBNGPEvolutionOfMarketValue)

## Notes / à valider en validation XML vs JSON
- **`FbnGpQPortfSpecificJoin`** : le fall-through C++ est reproduit (CLIENT/ACCOUNT/LINK → valeur LINK). À confirmer par comparaison Conseiller/Xpert sur le pad effectif du rapport système.
- **`H_PARAM_AssetMixRepartType = "Allocation - 1859"`** : valeur reprise de RPT-19560 (`DESC_REPARTITION_GP1859`, non résolue dans le périmètre des symlinks). À valider que le report server matche bien cette description de répartition.
- **`PARAM_ReportTitle`** : différence connue Conseiller/Xpert (non fonctionnelle).
