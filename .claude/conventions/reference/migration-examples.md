# Skill: Migration Examples

Guide pratique avec 4 migrations complètes C++ → C# du début à la fin.

## Objectif

Fournir des exemples concrets end-to-end pour guider l'analyse et estimer le temps de migration.

**Utilisé par:** report-analyst pour référencer des cas réels et estimer le temps

---

## Vue d'Ensemble

4 migrations complètes couvrant tous les niveaux de complexité.

| Exemple | Niveau | Estimé | Réel | Leçon Clé |
|---------|--------|--------|------|-----------|
| SinceInception | Niveau 1 | 10min | 5min | UnimplementedParameter ≠ Complexe |
| InitDefaultIndex | Niveau 2 | 1h | 52min | Condition simple = IValueProvidedParameter |
| Period1-5 | Niveau 2-3 | 2-3h | 30min | Simplifier logique UI complexe |
| GetBoolFromPref | Niveau 2 | 45min/fn | 44min | Pattern SQL spécial + template réutilisable |

**Conclusion:** Avec la bonne approche, migration **beaucoup plus rapide** que prévu!

---

## Exemple 1: Trivial - SinceInception (5 min)

**SQL:**
```
PARAM_PerfSinceInception, Default_Function: SinceInception, PRE, Checkbox
```

**Code C++ (validation_check.c:644):**
```c
void C_VALIDATION_CHECK::InitSinceInceptionCheck(C_WINDOW_PARAM_GROUP *in_pGroup) {
    C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_WINDOW_PARAM_GROUP_CHECK *) in_pGroup;  // IGNORER
    C_ATTRIBUTE *pAtt = pGroup->GetValue();  // IGNORER
    if (pAtt == NULL) { return; }            // IGNORER

    pGroup->Select(true);  // ← SEULE LIGNE IMPORTANTE!
}
```

**Analyse:**
- 1 Select(true), 0 prefs, 0 if → **Niveau 1**
- Équivalent: `parameter.InitialValue = "1"`

**Migration C#:**
```csharp
// PreParamEntryValueProviderFunctionsExecuter.cs:
implementationsDictionary["SinceInception"] = () => new TrueParameter();
```

**Temps réel:** Localisation 2min + Analyse 1min + Implémentation 2min = **5min** ✅

---

## Exemple 2: Simple - InitDefaultIndex (52 min)

**SQL:**
```
PARAM_DefaultIndices, Default_Function: InitDefaultIndex, PRE, Checkbox
```

**Code C++ (validation_check.c:789):**
```c
void C_VALIDATION_CHECK::InitDefaultIndexCheckTrue(C_WINDOW_PARAM_GROUP *in_pGroup) {
    C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_WINDOW_PARAM_GROUP_CHECK *)in_pGroup;  // IGNORER
    if (pGroup != NULL) {                                                           // IGNORER
        C_ATTRIBUTE *pAtt = pGroup->GetValue();                                     // IGNORER
        const C_REPORT_API *pReportApi = pGroup->GetReportApi();                    // LIRE

        if (pReportApi != NULL && pReportApi->GetPad() == REPORT_PORTEF) {         // LIRE
            pGroup->Select(false); pGroup->Enable(false);  // UI - IGNORER
            pAtt->SetValue("0");                           // LIRE: Valeur "0"
        } else {
            pGroup->Select(true);                          // UI - IGNORER
            pAtt->SetValue("1");                           // LIRE: Valeur "1"
        }
    }
}
```

**Analyse:**
- 1 GetPad, 2 SetValue, 1 if → **Niveau 2**
- Logique: SI Portfolio ALORS "0" ET désactivé, SINON "1"
- Dépendance: SourceTypes

**Migration C#:**
```csharp
// Infrastructure/.../Parameters/InitDefaultIndexParameter.cs
public class InitDefaultIndexParameter : IValueProvidedParameter {
    private readonly SourceTypes _requestSourceType;

    public InitDefaultIndexParameter(SourceTypes requestSourceType) {
        _requestSourceType = requestSourceType;
    }

    public ReportParameterMetaData ProvideValue(
        ReportParameterMetaData parameter,
        ReportMetaDataFromRtm reportMetaDataFromRtm)
    {
        if (_requestSourceType == SourceTypes.Portfolio) {
            parameter.InitialValue = "0";
            parameter.EnabledOnUi = false;
        } else {
            parameter.InitialValue = "1";
        }
        return parameter;
    }
}

// Enregistrement:
implementationsDictionary["InitDefaultIndex"] =
    () => new InitDefaultIndexParameter(requestSourceType);
```

**Tests:**
```csharp
[Theory]
[InlineData(SourceTypes.Client, "1", true)]
[InlineData(SourceTypes.Portfolio, "0", false)]
public void GivenSourceType_WhenProvideValue_ThenReturnsCorrect(
    SourceTypes sourceType, string expectedValue, bool expectedEnabled) {
    var parameter = new InitDefaultIndexParameter(sourceType);
    var result = parameter.ProvideValue(
        new ReportParameterMetaData(), new ReportMetaDataFromRtm());

    result.InitialValue.Should().Be(expectedValue);
    result.EnabledOnUi.Should().Be(expectedEnabled);
}
```

**Temps réel:** Localisation 8min + Analyse 12min + Implémentation 18min + Tests 14min = **52min** ✅

**Leçon:** Condition simple → Pattern standard, pas de service domaine nécessaire

---

## Exemple 3: Patterns Simplifiés - Period1-5 (30 min total)

**SQL:**
```
PARAM_Period1, Specific_Function: InitPeriod1, PRE, Checkbox
PARAM_Period2, Specific_Function: InitPeriod2, PRE, Checkbox
... (Period3, 4, 5)
```

**Code C++ (validation_check.c:1456-1520):**
```c
// 5 fonctions identiques sauf numéro
void C_VALIDATION_CHECK::InitPeriod1(C_WINDOW_PARAM_GROUP *in_pGroup) {
    InitPeriod(in_pGroup, GetPeriodNotFixed("3"), 0);  // Helper avec valeur "3"
}

void C_VALIDATION_CHECK::InitPeriod2(C_WINDOW_PARAM_GROUP *in_pGroup) {
    InitPeriod(in_pGroup, GetPeriodNotFixed("36"), 0);  // Valeur "36"
}
// ... Period3 ("60"), Period4 ("120"), Period5 ("0")

void C_VALIDATION_CHECK::InitPeriod(
    C_WINDOW_PARAM_GROUP *in_pGroup,
    const CF_STRING &in_sValue,
    int in_nLevel) {
    // 50 lignes de logique UI complexe - IGNORER
    pAtt->SetValue(in_sValue);  // SEULE LIGNE IMPORTANTE!
}
```

**Analyse:**
- 5 fonctions → 1 helper appelé avec valeur différente
- Complexité **apparente**: Niveau 3 (50+ lignes code)
- Complexité **réelle**: Niveau 0 (valeur hardcodée)

**Migration C# (naïve - INCORRECT):**
```csharp
// NE PAS FAIRE: Créer 5 classes
public class InitPeriod1Parameter : IValueProvidedParameter { ... }
public class InitPeriod2Parameter : IValueProvidedParameter { ... }
// ... × 5 = 250 lignes + 5 tests
```

**Migration C# (optimale):**
```csharp
// Helper Parameter directement
implementationsDictionary["InitPeriod1"] = () => new StringParameter("3");
implementationsDictionary["InitPeriod2"] = () => new StringParameter("36");
implementationsDictionary["InitPeriod3"] = () => new StringParameter("60");
implementationsDictionary["InitPeriod4"] = () => new StringParameter("120");
implementationsDictionary["InitPeriod5"] = () => new StringParameter("0");
```

**Temps réel:** Localisation 5min + Analyse 10min + Implémentation 5min (5 lignes!) + Validation 10min = **30min** ✅

**Leçon:** IGNORER logique UI complexe → Focus sur SetValue() uniquement. 5 classes évitées!

---

## Exemple 4: Pattern SQL - GetBoolFromPref (44 min pour template + instances)

**SQL (pattern répété):**
```
PARAM_ReportHideCurrency, Default_Function: GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY), POST
PARAM_DisplayCheckDigit, Default_Function: GetBoolFromPref(PREF_DISPLAY_CHECK_DIGIT), POST
... (7 autres paramètres identiques, seulement PREF_XXX change)
```

**Code C++ (validation_hided.c:234):**
```c
// Implémentation générique dans HiddenParametersImplementation.cs
CF_STRING sPref = GetCresusConfig()->get("PREF_XXX");
pAtt->SetValue(sPref == "YES" ? "1" : "0");
```

**Analyse:**
- Pattern répété 9 fois dans différents rapports
- Logique identique, seulement nom préférence change
- Niveau 2 (1 pref, 1 if)

**Migration C# (naïve - INCORRECT):**
```csharp
// Copier-coller 9 fois = 450 lignes
public class GetBoolFromPrefReportHideCurrencyParameter : IValueProvidedParameter { ... }
public class GetBoolFromPrefDisplayCheckDigitParameter : IValueProvidedParameter { ... }
// ... × 9
```

**Migration C# (avec template):**
```csharp
// 1. Template réutilisable (base)
public abstract class GetBoolFromPrefBaseParameter : IValueProvidedParameter {
    private readonly IPreferencesRepository _preferencesRepository;
    protected abstract string PreferenceKey { get; }

    protected GetBoolFromPrefBaseParameter(IPreferencesRepository preferencesRepository) {
        _preferencesRepository = preferencesRepository;
    }

    public ReportParameterMetaData ProvideValue(
        ReportParameterMetaData parameter,
        ReportMetaDataFromRtm reportMetaDataFromRtm) {
        var pref = _preferencesRepository.GetPreference(PreferenceKey);
        if (pref == null)
            throw new Exception($"Preference {PreferenceKey} not found");

        parameter.InitialValue = pref.Value?.ToUpper() == "YES" ? "1" : "0";
        return parameter;
    }
}

// 2. Instances (5 lignes chacune)
public class GetBoolFromPrefReportHideCurrencyParameter : GetBoolFromPrefBaseParameter {
    protected override string PreferenceKey => "PREF_REPORT_HIDE_CURRENCY";
    public GetBoolFromPrefReportHideCurrencyParameter(IPreferencesRepository repo) : base(repo) {}
}

// ... × 9 instances = 45 lignes total vs 450!
```

**Enregistrement:**
```csharp
implementationsDictionary["GetBoolFromPrefReportHideCurrency"] =
    () => new GetBoolFromPrefReportHideCurrencyParameter(preferencesRepository);
// ... × 9
```

**Temps réel:**
- Template (première fois): 25min
- Instances suivantes (8×): 2min chacune = 16min
- Tests template: 3min
- **Total: 44min** vs 6-9h si copier-coller ✅

**Leçon:** Pattern répété → Template. Économie massive de temps et maintenance simplifiée.

---

## Résumé des Leçons

1. **UnimplementedParameter ≠ Complexe** - SinceInception marqué TODO mais trivial (5min)
2. **Lire SEULEMENT SetValue/GetPad/GetConfig** - Ignorer 90% du code C++
3. **Helper Parameters FTW** - Valeurs hardcodées = 1 ligne
4. **Templates pour Patterns** - Pattern répété = Template réutilisable
5. **Tests simples suffisent** - Theory + InlineData couvre la majorité

## Références

**Code exemples réels:**
- `TrueParameter.cs` - Helper
- `InitDefaultIndexParameter.cs:15-35` - Condition simple
- `PreParamEntryValueProviderFunctionsExecuter.cs:180-184` - Period1-5
- `GetBoolFromPrefBase.cs` - Template pattern

**Skills:** `estimate-complexity`, `.claude/conventions/reference/implementation-guide.md`, `.claude/conventions/reference/read-cpp-patterns.md`
