---
name: implementation-guide
description: Guide complet des 9 patterns d'implémentation C++ vers C# pour ValueProviderParameters avec exemples de code. Utiliser pendant l'implémentation pour choisir le bon pattern et éviter les erreurs courantes.
allowed-tools: Read
---

# Skill: Implementation Guide

Guide complet de transformation C++ → C# pour ValueProviderParameters - Patterns 1-9.

**Utilisé par:** report-developer (implémentation de code C#)

---

## Structure Standard

**Template de base:**
```csharp
// Parameters/{Category}/{FunctionName}Parameter.cs
public class {FunctionName}Parameter : IValueProvidedParameter {
    private readonly {IDependency} _dependency;

    public {FunctionName}Parameter({IDependency} dependency) {
        _dependency = dependency;
    }

    public ReportParameterMetaData ProvideValue(
        ReportParameterMetaData parameter,
        ReportMetaDataFromRtm reportMetaDataFromRtm) {
        parameter.InitialValue = /* calcul */;
        return parameter;
    }
}
```

**Template tests:**
```csharp
public class {FunctionName}ParameterTests {
    [Theory]
    [InlineData(input1, expected1)]
    [InlineData(input2, expected2)]
    public void GivenInputs_WhenProvideValue_ThenReturnsExpected(input, expected) {
        var parameter = new {FunctionName}Parameter(dependency);
        var result = parameter.ProvideValue(new ReportParameterMetaData(), new ReportMetaDataFromRtm());
        result.InitialValue.Should().Be(expected);
    }
}
```

---

## Patterns d'Implémentation (1-9)

### Pattern 1: Préférence Simple

**C++:** `CF_STRING pref = GetCresusConfig()->get("PREF_XXX");`
**C# Injection:** `IPreferencesRepository`

```csharp
var pref = _preferencesRepository.GetPreference("PREF_XXX");
if (pref == null) throw new Exception("Preference PREF_XXX not found");
parameter.InitialValue = pref.Value?.ToUpper() == "YES" ? "1" : "0";
```

**Enregistrement:**
```csharp
implementationsDictionary["FunctionName"] = () => new FunctionNameParameter(preferencesRepository);
```

---

### Pattern 2: Préférences Multiples

**C++:** `CF_STRING pref1 = GetCresusConfig()->get("PREF_A"); CF_STRING pref2 = ...;`
**C# Injection:** `IPreferencesRepository`

```csharp
// Si < 3 préférences: GetPreference() séparément
var pref1 = _preferencesRepository.GetPreference("PREF_A");
var pref2 = _preferencesRepository.GetPreference("PREF_B");
parameter.InitialValue = (pref1?.Value == "YES" && pref2?.Value == "NO") ? "1" : "0";

// Si >= 3 préférences: GetPreferencesValue()
var prefs = _preferencesRepository.GetPreferencesValue(new[] { "PREF_A", "PREF_B", "PREF_C" }).Result;
```

---

### Pattern 3: Source Type (GetPad)

**C++:** `eReportPad pad = pReportApi->GetPad();`
**C# Injection:** `SourceTypes requestSourceType` (constructor param)

```csharp
parameter.InitialValue = _requestSourceType == SourceTypes.Client ? "1" : "0";
```

**Mapping:**
| C++ | C# |
|-----|-----|
| `REPORT_CLIENT` | `SourceTypes.Client` |
| `REPORT_ACCOUNT` | `SourceTypes.Account` |
| `REPORT_PORTEF` | `SourceTypes.Portfolio` |
| `REPORT_SECURITY` | `SourceTypes.Security` |

---

### Pattern 4: Accès Paramètre Rapport

**C++:** `CF_STRING param = GetParam(pParam, PARAM_XXX);`
**C# Injection:** `IReportCommandAndQueryContextRepository`

```csharp
var paramValue = _contextRepository.GetParameter("PARAM_XXX");
// Méthodes: GetParameter(name), GetParameterAsInt(name), IsParameterChecked(name)
```

---

### Pattern 5: Valeur avec Visibilité/Activation

**C++:** `pGroup->SetHideWidgetFlag(true); pGroup->Enable(false);`
**C# Propriétés UI:**

```csharp
parameter.VisibleOnUi = false;  // Afficher/cacher
parameter.EnabledOnUi = false;  // Activer/désactiver (grisé)
parameter.IsReadOnly = true;    // Lecture seule
```

---

### Pattern 6: GetBoolFromPref (Template Réutilisable)

**SQL:** `GetBoolFromPref(PREF_XXX)`

```csharp
private const string PreferenceKey = "PREF_XXX";

public ReportParameterMetaData ProvideValue(...) {
    var pref = _preferencesRepository.GetPreference(PreferenceKey);
    parameter.InitialValue = pref?.Value?.ToUpper() == "YES" ? "1" : "0";
    return parameter;
}
```

**Naming:** `GetBoolFromPref{PreferenceName}Parameter`
Exemple: `GetBoolFromPrefReportHideCurrencyParameter` pour `PREF_REPORT_HIDE_CURRENCY`

---

## Patterns Avancés (7-9)

**Utilisés pour:** Combobox/Radio avec choix dynamiques, paramètres conditionnels, composition de comportements.

### Propriétés ReportParameterMetaData

| Propriété | Type | Description | Mapping C++ |
|-----------|------|-------------|-------------|
| `InitialValue` | string | Valeur par défaut | `pAtt->SetValue("1")` |
| `VisibleOnUi` | bool | Afficher/cacher (existe toujours) | `pGroup->SetHideWidgetFlag(!visible)` |
| `EnabledOnUi` | bool | Activer/désactiver (grisé) | `pGroup->Enable(false)` |
| `IsReadOnly` | bool | Lecture seule (actif mais non modifiable) | - |
| `PossibleDisplayValues` | IEnumerable | Choix Combobox/Radio | `SetInit`, `SetValue` |
| **`return null`** | - | **Supprime le paramètre complètement** | - (nouveau) |

**Distinctions importantes:**
- `VisibleOnUi=false` : caché mais existe | `return null` : supprimé du modèle
- `EnabledOnUi=false` : grisé | `IsReadOnly=true` : actif mais non modifiable

**Structure PossibleDisplayValues:**
```csharp
parameter.PossibleDisplayValues = new List<PossibleDisplayValue>
{
    new PossibleDisplayValue
    {
        Value = "1",
        DisplayValue = new TranslatedDescription
        {
            Key = "Option 1",
            Values = new List<LocalizedDescription>
            {
                new LocalizedDescription { Culture = CultureValue.EnCa, Description = "Option 1 (EN)" },
                new LocalizedDescription { Culture = CultureValue.FrCa, Description = "Option 1 (FR)" }
            }
        }
    }
};
```

---

### Pattern 7: PossibleDisplayValues (Manipulation Choix Combobox/Radio)

**Essentiel pour Combobox (WIDGET_TYPE=1) et Radio (WIDGET_TYPE=2)**

**Indices C++:**
- `SetInit()` / `SetValue()` / `SetGetValue()` → Manipulation de choix
- `pCombo->AddItem()` / `RemoveItem()` → Construction dynamique
- Boucles sur données → Remplissage liste
- WIDGET_TYPE = 1 ou 2

**Exemple C++ typique:**
```c
m_pParam->SetInit(InitAssetMixWrapper);
m_pParam->SetValue(C_VALIDATION_RADIO::SetAssetMix);
// Ces callbacks ajoutent/enlèvent items dynamiquement
```

#### A. Filtrage Dynamique

Retirer certains choix selon conditions.

**C++ → C#:**
```c
// C++
if (!FirmRepartitionExists())
    pCombo->RemoveItem("MultiLevelFirmAssetMix");
```

```csharp
// C#
if (!repartitionRepository.FirmRepartitionExist())
{
    parameter.PossibleDisplayValues = parameter.PossibleDisplayValues
        .Where(x => !x.Value.Contains("MultiLevelFirmAssetMix"))
        .ToList();

    // CRITIQUE: Ajuster InitialValue si choix supprimé
    if (parameter.InitialValue == "MultiLevelFirmAssetMix")
        parameter.InitialValue = "MultiLevelBasicAssetMix";
}
return parameter;
```

**Réf:** `AssetMixSleevesRadioButtonParameter.cs:29-57`

#### B. Construction avec Traductions

Construire choix depuis BD/repository.

**C++ → C#:**
```c
// C++
vector<IndustryCode> codes = GetIndustryCodeList();
for (int i = 0; i < codes.size(); i++)
    pCombo->AddItem(codes[i].id, codes[i].descriptionFr, codes[i].descriptionEn);
```

```csharp
// C#
var industryCodes = industryCodeRepository.GetIndustryCodes();
parameter.PossibleDisplayValues = industryCodes.Select(x =>
    new PossibleDisplayValue
    {
        Value = x.IndustryCodeSetId.ToString(),
        DisplayValue = new TranslatedDescription
        {
            Key = x.DescriptionEn,
            Values = new List<LocalizedDescription>
            {
                new LocalizedDescription { Culture = CultureValue.EnCa, Description = x.DescriptionEn },
                new LocalizedDescription { Culture = CultureValue.FrCa, Description = x.DescriptionFr }
            }
        }
    }).ToList();

if (industryCodes.Any())
    parameter.InitialValue = industryCodes.First().IndustryCodeSetId.ToString();
```

**Réf:** `IndCodeComboParameter.cs:44-65`

**Mapping C++ → C#:**
- `SetInit()` → Initialise `PossibleDisplayValues`
- `SetValue()` → Modifie `PossibleDisplayValues`
- `AddItem()` → Ajout à liste
- `RemoveItem()` → `.Where(x => !x.Value.Contains(...))`
- `Select()` → `parameter.InitialValue = "value"`

**Exemples réels:**
- `AssetMixSleevesRadioButtonParameter.cs:29-57` - Filtrage dynamique
- `IndCodeComboParameter.cs:28-65` - Construction + return null
- `AssetMixRepartitionIDParameter.cs` - Choix custom
- `PreviousCurrentYearParameter.cs` - Construction d'années

---

### Pattern 8: Suppression Conditionnelle (return null)

**Nouveau pattern C#** - Le paramètre est complètement supprimé du modèle.

**vs `VisibleOnUi=false`:** caché mais existe toujours

```csharp
public ReportParameterMetaData ProvideValue(...) {
    var industryCodes = industryCodeRepository.GetIndustryCodes();
    if (industryCodes.Count == 0)
    {
        Logger.Debug("Removing parameter {ParameterName} - no industry codes", parameter.Name);
        return null;  // Paramètre supprimé
    }
    parameter.InitialValue = industryCodes.First().Id.ToString();
    return parameter;
}
```

**Utiliser `return null` si:**
- Aucune donnée disponible (combobox vide)
- Feature désactivée globalement
- Contexte incompatible (ex: paramètre Account-only sur rapport Client)

**Ne pas utiliser si:** paramètre caché temporairement ou révélable plus tard

**C++:** Pas d'équivalent direct (toujours présent mais caché/désactivé)

**Réf:** `IndCodeComboParameter.cs:28-34`

---

### Pattern 9: Composition (MultipleValueProvidedParameters)

Appliquer plusieurs transformations en chaîne sur un paramètre.

```csharp
implementationsDictionary["FunctionName"] =
    () => new MultipleValueProvidedParameters(
        new FirstParameter(...),   // S'exécute en premier
        new SecondParameter(...)   // Modifie le résultat
    );
```

**Exemple:**
```csharp
implementationsDictionary["SimpleAssetMixRadioButton_RemovedForSleeveContext"] =
    () => new MultipleValueProvidedParameters(
        new SimpleAssetMixRadioButtonParameter(repartitionsRepository),  // Définit choix
        new RemovedForSleeveContext(requestSourceType)  // Supprime si Sleeve
    );
```

**Utiliser si:**
- Logique réutilisable (ex: "Supprimer pour Sleeve") s'applique à plusieurs paramètres
- Éviter duplication de code
- Composition de comportements

**Ne pas utiliser si:** logique unique à un seul paramètre

**Pattern modificateur réutilisable:**
```csharp
// 1. Parameter de base
public class MyBaseParameter : IValueProvidedParameter
{
    public ReportParameterMetaData ProvideValue(...)
    {
        parameter.InitialValue = "value";
        return parameter;
    }
}

// 2. Modificateur réutilisable
public class RemovedForSleeveContext : IValueProvidedParameter
{
    public ReportParameterMetaData ProvideValue(...)
    {
        if (_requestSourceType == SourceTypes.Sleeve)
            return null;
        return parameter;
    }
}

// 3. Composition
implementationsDictionary["MyFunction"] = () => new MultipleValueProvidedParameters(
    new MyBaseParameter(...),
    new RemovedForSleeveContext(...)
);
```

**Avantages:** Réutilisabilité (ex: `RemovedForSleeveContext` utilisé 3×), séparation responsabilités, testabilité

**Réf:** `PreParamEntryValueProviderFunctionsExecuter.cs:62-63, 132-135`

---

### Checklist Patterns Avancés

**Combobox/Radio (WIDGET_TYPE 1 ou 2):**
- C++ utilise `SetInit()`/`SetValue()`/`SetGetValue()` → Pattern 7 requis
- C++ fait boucles sur données → Pattern 7 (Construction)
- C++ supprime items (`RemoveItem`) → Pattern 7 (Filtrage)
- Paramètre conditionnel (certains contextes) → Pattern 8 (return null)
- Logique réutilisable → Pattern 9 (Composition)

**Autres widgets:** Caché/désactivé → `VisibleOnUi`/`EnabledOnUi`

---

## Helper Parameters (Valeurs Statiques)

Pas de logique conditionnelle, valeur hardcodée.

| Helper | Usage | C++ Équivalent |
|--------|-------|----------------|
| `StringParameter("value")` | Valeur fixe | `pAtt->SetValue("value")` |
| `TrueParameter()` | Checkbox cochée | `pGroup->Select(true)` |
| `FalseParameter()` | Checkbox décochée | `pGroup->Select(false)` |
| `EmptyParameter()` | Valeur vide | `pAtt->SetValue("")` |
| `VoidParameter()` | Pas de valeur | Return sans SetValue |

**Enregistrement:**
```csharp
implementationsDictionary["Period1"] = () => new StringParameter("3");
implementationsDictionary["CheckTrue"] = () => new TrueParameter();
```

---

## Mapping Repositories C++ → C#

| Pattern C++ | Repository C# |
|-------------|---------------|
| `GetCresusConfig()->get("PREF_")` | `IPreferencesRepository` |
| `GetParam("PARAM_")` | `IReportCommandAndQueryContextRepository` |
| `pReportApi->GetPad()` | `SourceTypes` (constructor param) |
| Date operations | `IParameterDateValueService` |
| Repartitions | `IRepartitionRepository` |
| Industry codes | `IIndustryCodeRepository` |
| Indexes | `IIndexesRepository` |
| Transactions | `ITransactionsRepository` |

---

## Erreurs Courantes

**1. Oublier d'ajuster InitialValue après filtrage (Pattern 7)**
```csharp
// ❌ INCORRECT
parameter.PossibleDisplayValues = parameter.PossibleDisplayValues.Where(...);
return parameter;  // InitialValue peut être invalide!

// ✅ CORRECT
var removed = "OptionA";
parameter.PossibleDisplayValues = parameter.PossibleDisplayValues.Where(x => !x.Value.Contains(removed));
if (parameter.InitialValue == removed)
    parameter.InitialValue = parameter.PossibleDisplayValues.First().Value;
```

**2. Confondre VisibleOnUi=false et return null (Pattern 8)**
```csharp
// ❌ Si vraiment inutile, supprimer complètement
if (noDataAvailable)
    parameter.VisibleOnUi = false;  // Existe encore!

// ✅ CORRECT
if (noDataAvailable)
    return null;  // Supprimé
```

**3. Ne pas logger les suppressions (Pattern 8)**
```csharp
// ✅ Toujours logger les décisions importantes
Logger.Debug("Removing parameter {ParameterName} - reason", parameter.Name);
return null;
```

**4. GetPreferencesValue() pour 1 seule préférence (Pattern 1)**
```csharp
// ❌ INCORRECT
var pref = repo.GetPreferencesValue(new[]{"PREF_XXX"}).Result.FirstOrDefault();

// ✅ CORRECT
var pref = repo.GetPreference("PREF_XXX");
```

**5. Absence validation null (Pattern 1)**
```csharp
// ❌ INCORRECT
parameter.InitialValue = pref.Value; // Crash si null!

// ✅ CORRECT
if (pref == null) throw new Exception(...);
parameter.InitialValue = pref.Value;
```

---

## Références

**Code snippets:** `MyCustomSnippets.code-snippets` - `ivalueProvidedParameter`

**Exemples réels (Patterns avancés):**
- `AssetMixSleevesRadioButtonParameter.cs:29-57` - Pattern 7 (Filtrage)
- `IndCodeComboParameter.cs:28-65` - Pattern 7 (Construction) + Pattern 8 (return null)
- `PreParamEntryValueProviderFunctionsExecuter.cs:62-63,132-135` - Pattern 9 (Composition)

**Skills connexes:** `migration-examples`, `analyze-cpp-function`, `best-practices-analyst`, `generic-functions-reference`

**Documentation:** CLAUDE.md - Section "Adding a ValueProviderParameter"
