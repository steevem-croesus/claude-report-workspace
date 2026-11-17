# Skill: Framework Implementation Patterns Reference

**Objectif:** Déterminer la bonne approche pour implémenter une fonction de rapport.

**Règle critique:** >90% des paramètres utilisent l'approche déclarative (configuration dans Parameters.cs). Vérifier TOUJOURS les patterns déclaratifs AVANT de créer une classe.

---

## Statistiques Réelles du Codebase

| Pattern | Utilisations | % | Fichier | Classe Requise |
|---------|-------------|---|---------|----------------|
| ValidationFunction="" | 1,904 | >90% | Parameters.cs | ❌ |
| InitialValue | 356 | 58% | Parameters.cs | ❌ |
| ValueProviderFunction | 254 | 41% | Parameters.cs + Executer | ✅ |
| InitialValueFromPref | 26 | 4% | Parameters.cs | ❌ |
| Helper Parameters | 24 | 4% | Executer | ⚠️ Déprécié |
| InitialValueDateType | 1 | <1% | Parameters.cs | ❌ |

**Conclusion:** >90% des implémentations N'ONT PAS besoin de classe.

---

## Hiérarchie de Décision (Ordre Obligatoire)

### Niveau 1: ValidationFunction Vide (>90%) - Default Function

**Utiliser si:** Fonction gérée par `*ParametersImplementation.cs`

**Indicateurs:** Nom générique, utilisée dans plusieurs rapports, logique simple

**Code C++:**
```c
void C_VALIDATION_HIDED::CheckTrue(...) {
    pAtt->SetValue("1");
}
```

**Implémentation C# (Parameters.cs):**
```csharp
this.AddParameter(new ParameterJoinEntity(...PARAM_KeepInvalidPeriods)
{
    ValidationFunction = "",  // Vide = géré par framework
});
```

**Métriques:** 1 fichier | 10s | 0 classe | 0 test

**Default functions par widget:**
- Widget 8 (Hidden): CheckTrue, CheckFalse, PureValueZero, GetBoolFromPref, GetDisplayDate
- Widget 3 (Checkbox): InitCheckTrue, InitCheckFalse
- Widget 2 (Radio): CostCalculation, PaginationVisible
- Widget 5 (Date): GetStartDate, GetEndDate
- Widget 1 (Combo): AsOfDate, IndCodeCombo

**Vérification:**
```bash
grep -r "FunctionName" repos/ReportFoundations/.../SpecificTypes/*ParametersImplementation.cs
```

---

### Niveau 2: InitialValue (58%) - Constante Simple

**Utiliser si:** C++ fait `SetValue("constante")` sans conditions

**Code C++:**
```c
void MaturitySubReportField(...) {
    pAtt->SetValue("SEC_V_Desc");
}
```

**Implémentation C# (Parameters.cs):**
```csharp
this.AddParameter(new ParameterJoinEntity(...PARAM_RPTSubId)
{
    ValidationFunction = "MaturitySubReportField",
    InitialValue = "SEC_V_Desc"  // Pas de classe!
});
```

**Métriques:** 1 fichier | 2min | 0 classe | 0 test

**Exemples réels (356 utilisations):**
- `"Allocation - Maturity"` (DistributionByMaturity)
- `"0"`, `"Region"` (StockAllocation)
- `"SEC_V_Desc:SECURITY|..."` (Maturity)

**Erreur à éviter:**
```csharp
// ❌ NE PAS créer classe pour constante
public class MaturitySubReportFieldParameter : IValueProvidedParameter { ... }

// ❌ NE PAS utiliser Helper Parameter (déprécié)
implementationsDictionary["MaturitySubReportField"] = () => new StringParameter("SEC_V_Desc");

// ✅ CORRECT
InitialValue = "SEC_V_Desc"
```

---

### Niveau 3: InitialValueFromPref (4%) - Préférence Simple

**Utiliser si:** C++ lit `GetConfig()->get("PREF_XXX")` avec mapping simple

**Code C++:**
```c
void Function(...) {
    CF_STRING pref = GetConfig()->get("PREF_STRIP_BOND_GL1");
    // Retour direct ou mapping YES/NO → 1/0
}
```

**Implémentation C# (Parameters.cs):**
```csharp
this.AddParameter(new ParameterJoinEntity(...PARAM_CIBCGainLossCalcul)
{
    ValidationFunction = "GetBoolFromPref(PREF_STRIP_BOND_GL1)",
    InitialValueFromPref = "PREF_STRIP_BOND_GL1"
});
```

**Métriques:** 1 fichier | 2min | 0 classe | 0 test

**Exemples réels (26 utilisations):**
- `PREF_STRIP_BOND_GL1` (DistributionByMaturity, GainsAndLosses)
- `PREF_NB_MAX_LEVEL_ASSET` (Performance/AssetClass)
- `PREF_GROSS_PERFORMANCE` (Performance/Base)

**Pattern alternatif - Commentaire si géré par Default:**
```csharp
this.AddParameter(new ParameterJoinEntity(...PARAM_DisplayDateAndTime)
{
    ValidationFunction = "",
    // InitialValueFromPref (PREF_REPORT_DISPLAY_DATE_TIME) set in HiddenParametersImplementation
});
```

**Créer classe SEULEMENT si:** Logique conditionnelle complexe, multiples préférences (2+), transformations non-standard

---

### Niveau 4: InitialValueDateType (<1%) - Date Système

**Utiliser si:** C++ utilise `sys_date_fin`, `GetLastProcessingDate()` sans calcul

**Code C++:**
```c
void LastProcessingDate(...) {
    pDate = new DATE_FIN(*sys_date_fin);  // Date système directe
    pGroup->SetDate(pDate);
}
```

**Implémentation C# (Parameters.cs):**
```csharp
this.AddParameter(new ParameterJoinEntity(...PARAM_StartDate)
{
    ValidationFunction = "LastProcessingDate",
    InitialValueDateType = "LastProcessedDate"
});
```

**Métriques:** 1 fichier | 2min | 0 classe | 0 test

**DateType enum disponibles:**
- `LastProcessedDate` - sys_date_fin
- `FirmStartDate` - Date début firme
- `CurrentDate` - Date actuelle
- `AsOfDate` - Date contextuelle

**Vérification:**
```bash
grep -A 50 "enum DateType" Croesus.Reports.Parameters/Services/DateType.cs
```

**Créer classe SI:** Calcul sur date (AddMonths, AddDays), logique conditionnelle

---

### Niveau 5: Helper Parameters (4%) - DÉPRÉCIÉ

**Approche ancienne remplacée par InitialValue (Niveau 2).**

**Pourquoi déprécié:** Nécessite executer, valeur dispersée, moins visible, plus long (5-10min vs 2min)

**Ancienne approche (24 utilisations restantes):**
```csharp
// Dans executer - NE PLUS UTILISER
implementationsDictionary["Period1"] = () => new StringParameter("3");
```

**Approche moderne:**
```csharp
// Dans Parameters.cs
InitialValue = "3"
```

**Helper Parameters disponibles (compatibilité):**
- `StringParameter(value)` → Remplacer par `InitialValue = value`
- `TrueParameter()` → Remplacer par `InitialValue = "1"`
- `FalseParameter()` → Remplacer par `InitialValue = "0"`

---

### Niveau 6: ValueProviderFunction Custom (41%) - Logique Complexe

**Utiliser si:** Calculs, conditions multiples, transformations, services, dépendances multiples (2+ PREF_/PARAM_)

**Code C++:**
```c
void InitGainLossCostDisplayed(...) {
    sAddTheo = GetConfig()->get("PREF_ADD_THEORETICAL_VALUE");
    sStripBond = GetConfig()->get("PREF_STRIP_BOND_GL1");
    if (iAddTheo == 1 && iStripBond == 0)
        pAtt->SetValue("1");
    else
        pAtt->SetValue("0");
}
```

**Implémentation C#:**

**1. Classe Parameter (Parameters/Preference/InitGainLossCostDisplayedParameter.cs):**
```csharp
public class InitGainLossCostDisplayedParameter : IValueProvidedParameter
{
    private readonly IPreferencesRepository _preferencesRepository;

    public InitGainLossCostDisplayedParameter(IPreferencesRepository preferencesRepository)
    {
        _preferencesRepository = preferencesRepository;
    }

    public ReportParameterMetaData ProvideValue(
        ReportParameterMetaData parameter,
        ReportMetaDataFromRtm reportMetaDataFromRtm)
    {
        var prefs = _preferencesRepository.GetPreferencesValue(
            new[] { "PREF_ADD_THEORETICAL_VALUE", "PREF_STRIP_BOND_GL1" }).Result;

        var addTheo = prefs.FirstOrDefault(p => p.Name == "PREF_ADD_THEORETICAL_VALUE")?.Value == "YES";
        var stripBond = prefs.FirstOrDefault(p => p.Name == "PREF_STRIP_BOND_GL1")?.Value == "YES";

        parameter.InitialValue = (addTheo && !stripBond) ? "1" : "0";
        return parameter;
    }
}
```

**2. Enregistrement (PreParamEntryValueProviderFunctionsExecuter.cs):**
```csharp
implementationsDictionary["InitGainLossCostDisplayed"] =
    () => new InitGainLossCostDisplayedParameter(preferencesRepository);
```

**3. Configuration (Parameters.cs):**
```csharp
this.AddParameter(new ParameterJoinEntity(...PARAM_GainLossCost)
{
    ValueProviderFunction = "InitGainLossCostDisplayed"
});
```

**Métriques:** 3 fichiers | 30min-4h | 1 classe | Tests requis (mocks)

**Voir:** Référence `.claude/conventions/reference/implementation-guide.md` pour patterns 1-9 détaillés

---

## Arbre de Décision

```
Pour fonction C++ à migrer:

1. Dans *ParametersImplementation.cs (Default)?
   OUI → NIVEAU 1: ValidationFunction=""
   NON → Continuer

2. SetValue("constante") seulement?
   OUI → NIVEAU 2: InitialValue="constante"
   NON → Continuer

3. Lit préférence avec mapping simple?
   OUI → NIVEAU 3: InitialValueFromPref="PREF_XXX"
   NON → Continuer

4. Date système SANS calcul?
   OUI → NIVEAU 4: InitialValueDateType="DateType"
   NON → Continuer

5. Logique/calculs/conditions?
   OUI → NIVEAU 6: Créer classe Parameter custom
```

**>90% se résolvent aux niveaux 1-4 (AUCUNE classe).**

---

## Checklist de Vérification

Avant créer classe Parameter:

- [ ] **1. ValidationFunction vide?** → Chercher dans *ParametersImplementation.cs
  ```bash
  grep -r "FunctionName" repos/ReportFoundations/.../SpecificTypes/*.cs
  ```

- [ ] **2. Constante simple?** → C++ fait `SetValue("constante")` seulement
  - OUI → `InitialValue = "constante"`

- [ ] **3. Préférence simple?** → C++ lit `PREF_XXX` mapping simple
  - OUI → `InitialValueFromPref = "PREF_XXX"`

- [ ] **4. Date système?** → C++ `sys_date_fin` sans calcul
  - OUI → `InitialValueDateType = "LastProcessedDate"`

- [ ] **5. Logique complexe?** → Calculs, conditions, dépendances multiples
  - OUI → Créer classe Parameter custom

**Si doute:** Skill `estimate-complexity` pour classifier

---

## Erreurs Courantes

**Erreur 1: Classe pour constante**
```csharp
// ❌ 30min perdues
public class MaturitySubReportFieldParameter : IValueProvidedParameter { ... }

// ✅ 2min
InitialValue = "SEC_V_Desc"
```

**Erreur 2: Helper Parameter vs InitialValue**
```csharp
// ❌ Déprécié (5-10min)
implementationsDictionary["Period1"] = () => new StringParameter("3");

// ✅ Moderne (2min)
InitialValue = "3"
```

**Erreur 3: Classe pour Default function**
```csharp
// ❌
public class CheckTrueParameter : IValueProvidedParameter { ... }

// ✅
ValidationFunction = ""  // Géré par HiddenParametersImplementation
```

**Erreur 4: Ne pas vérifier avant créer**

>90% n'ont PAS besoin de classe. Vérifier niveaux 1-4 AVANT créer classe.

---

## Exemples Réels

**Maturity (RPT-17874) - 96% déclaratif:**
- InitialValue: 6
- InitialValueDateType: 1
- InitialValueFromPref: 4 (commentés)
- ValidationFunction="": 13
- Custom: 1 (LastProcessingDatePlusOneMonth - calcul date)

Ratio: 24/25 = 96% déclaratif

**DistributionByMaturity/Report - Pattern mixte:**
```csharp
// NIVEAU 2
this.AddParameter(new ParameterJoinEntity(...PARAM_AssetMixRepartType)
{
    InitialValue = "Allocation - Maturity"
});

// NIVEAU 3
this.AddParameter(new ParameterJoinEntity(...PARAM_CIBCGainLossCalcul)
{
    ValidationFunction = "GetBoolFromPref(PREF_STRIP_BOND_GL1)",
    InitialValueFromPref = "PREF_STRIP_BOND_GL1"
});

// NIVEAU 1
this.AddParameter(new ParameterJoinEntity(...PARAM_DisplayCheckDigit)
{
    ValidationFunction = ""
});

// NIVEAU 2
this.AddParameter(new ParameterJoinEntity(...PARAM_MutFundBreakDown)
{
    ValidationFunction = "CheckFalse",
    InitialValue = "0"
});
```

---

## Fonctions Génériques - Hidden Parameters (POST)

**Localisation:** `repos/ReportFoundations/.../Parameters/SpecificTypes/HiddenParametersImplementation.cs`

Widget 8, Entry POST:

| Fonction | Retour | Utilisation |
|----------|--------|-------------|
| CheckTrue | "1" | ValidationFunction="" |
| CheckFalse | "0" | ValidationFunction="" |
| PureValueZero | "0" | ValidationFunction="" |
| PureValueMinusOne | "-1" | ValidationFunction="" |
| GetBoolFromPref(PREF_XXX) | "1"/"0" | InitialValueFromPref |
| GetDisplayDate | Date | ValidationFunction="" |
| GetDisplayUnmaskedId | "0"/"1" | ValidationFunction="" |
| GetFirmCurrency | Devise | ValidationFunction="" |

**Temps:** 10s | **Classe:** ❌

---

## Fonctions Génériques - Autres Widgets

**Checkbox (PRE) - CheckBoxParametersImplementation.cs:**
- InitCheckTrue / CheckTrue → ValidationFunction=""
- InitCheckFalse / CheckFalse → ValidationFunction=""

**Combobox - ComboBoxParametersImplementation.cs:**
- AsOfDate, AsOfDateNoFuture, IndCodeCombo, AssetMixRepartitionCombo

**Radio - RadioParametersImplementation.cs:**
- CostCalculation, PaginationVisible

**Date - DateParametersImplementation.cs:**
- GetStartDate, GetEndDate

**Tous:** ValidationFunction="" (NIVEAU 1)

---

## Références

**Framework Implementation Files (vérifier en priorité):**
- `repos/ReportFoundations/.../SpecificTypes/HiddenParametersImplementation.cs`
- `repos/ReportFoundations/.../SpecificTypes/CheckBoxParametersImplementation.cs`
- `repos/ReportFoundations/.../SpecificTypes/ComboBoxParametersImplementation.cs`
- `repos/ReportFoundations/.../SpecificTypes/RadioParametersImplementation.cs`
- `repos/ReportFoundations/.../SpecificTypes/DateParametersImplementation.cs`

**Executers (classes custom seulement):**
- `ReportManagerAPI.Infrastructure/.../PreParamEntryValueProviderFunctionsExecuter.cs`
- `ReportManagerAPI.Infrastructure/.../PostParamEntryValueProviderFunctionsExecuter.cs`

**Skills:**
- `estimate-complexity` - Classifier fonction C++ (niveaux 0-5)
- `.claude/conventions/reference/implementation-guide.md` - Patterns 1-9 pour classes custom
- `classify-functions` - Classification Default/Specific, PRE/POST
- `analyze-cpp-function` - Analyser dépendances et logique

**Documentation:**
- CLAUDE.md - Section "Hiérarchie d'Implémentation des Paramètres"

---

## Résumé: Quand Créer une Classe?

| Scénario | Classe? | Pattern | Temps |
|----------|---------|---------|-------|
| Default function | ❌ | ValidationFunction="" | 10s |
| Constante | ❌ | InitialValue="valeur" | 2min |
| Préférence simple | ❌ | InitialValueFromPref="PREF_XXX" | 2min |
| Date système | ❌ | InitialValueDateType="DateType" | 2min |
| Logique complexe | ✅ | Classe Parameter | 30min-4h |

**Règle finale:** SEULEMENT >10% nécessitent une classe.

Vérifier TOUJOURS niveaux 1-4 (déclaratifs) AVANT créer classe (niveau 6).
