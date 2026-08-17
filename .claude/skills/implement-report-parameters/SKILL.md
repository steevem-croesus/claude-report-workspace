---
name: implement-report-parameters
description: Implémente tous les paramètres d'un rapport en 2 phases - Configuration Parameters.cs (déclaratifs >90%) puis classes custom (>10%). Workflow complet avec templates et validation.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Skill: Implement Report Parameters

Implémentation complète des paramètres d'un rapport C# en distinguant patterns déclaratifs (>90%) vs custom (>10%).

**Utilisé par:** /report-developer/migrate-report

---

## Objectif

Transformer la spec d'implémentation en code C# fonctionnel en 2 phases:
1. **PHASE A (Prioritaire):** Configuration Parameters.cs pour TOUS les paramètres
2. **PHASE B (Si nécessaire):** Classes Parameter custom seulement

**Règle critique:** Ne JAMAIS sauter Phase A. >90% du travail se fait en configuration seule.

---

## Input Requis

**Depuis manage-state:**
- `state.analysis.files.spec` - Spec complète d'implémentation
- `state.analysis.functionsToAnalyze[]` - Liste fonctions avec patterns
- `state.reportId` - ID du rapport
- `state.reportName` - Nom du rapport

**Format fonction attendu:**
```json
{
  "name": "MaturitySubReportField",
  "implementationPattern": "declarative:InitialValue",
  "initialValue": "SEC_V_Desc",
  "entryType": "POST",
  "widgetType": 8
}
```

---

## PHASE A: Configuration Parameters.cs (OBLIGATOIRE)

### Étape 1: Localiser ou Créer Fichier

**Chercher fichier existant:**
```bash
find ../monolith/CFF/Products/ReportManagerApi -name "*Parameters.cs" -type f | \
  grep -v Test | \
  xargs grep -l "RPT.*{reportId}" 2>/dev/null
```

**Si inexistant, chercher pattern similaire:**
```bash
# Chercher autres rapports pour voir structure
find ../monolith/CFF/Products/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories -name "*Parameters.cs" -type f | head -5
```

**Créer nouveau fichier si aucun existant:**

Emplacement suggéré:
```
../monolith/CFF/Products/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ReportParameters/{ReportName}Parameters.cs
```

**Template fichier Parameters.cs:**
```csharp
using Croesus.Reports.Parameters.Model;
using System.Collections.Generic;

namespace ReportManagerAPI.Infrastructure.Repositories.ReportParameters
{
    public class {ReportName}Parameters
    {
        public List<ParameterJoinEntity> GetParameters()
        {
            var parameters = new List<ParameterJoinEntity>();

            // PRE Parameters (widgetType < 8)
            // ... configurations ci-dessous ...

            // POST Parameters (widgetType >= 8)
            // ... configurations ci-dessous ...

            return parameters;
        }

        private void AddParameter(ParameterJoinEntity parameter)
        {
            parameters.Add(parameter);
        }
    }
}
```

---

### Étape 2: Configurer TOUS les Paramètres

**Lire spec:** `.work/{slug}/spec.md` → Section 3

**Pour chaque fonction dans `state.analysis.functionsToAnalyze`:**

Identifier pattern via `implementationPattern`:

---

#### Pattern A: declarative:ValidationFunction (47% des cas)

**Indicateur:** `"implementationPattern": "declarative:ValidationFunction"`

**Fonction gérée par *ParametersImplementation.cs (Default functions)**

**Code:**
```csharp
this.AddParameter(new ParameterJoinEntity(
    reportMetaDataFromRtm,
    "PARAM_{XXX}",
    ParameterType.{Type},
    {widgetType})
{
    ValidationFunction = ""  // Vide = géré par framework
});
```

**Exemples réels:**
- CostCalculation (widget 2) → RadioParametersImplementation
- InitDisplayCheckDigit (widget 3) → CheckBoxParametersImplementation
- ReportTitle (widget 8) → HiddenParametersImplementation

**Mapping ParameterType:**
- widgetType 2 → ParameterType.Radio
- widgetType 3 → ParameterType.CheckBox
- widgetType 5 → ParameterType.Date
- widgetType 8 → ParameterType.Hidden

**Temps:** 10s par paramètre

---

#### Pattern B: declarative:InitialValue (21% des cas)

**Indicateur:** `"implementationPattern": "declarative:InitialValue"`

**Valeur constante définie dans l'état:** `fonction.initialValue`

**Code:**
```csharp
this.AddParameter(new ParameterJoinEntity(
    reportMetaDataFromRtm,
    "PARAM_{XXX}",
    ParameterType.Hidden,
    8)
{
    ValidationFunction = "{FunctionName}",
    InitialValue = "{fonction.initialValue}"  // Pas de classe Parameter!
});
```

**Exemples réels:**
```csharp
// Constante simple
InitialValue = "1"

// Constante complexe
InitialValue = "SEC_V_Desc:SECURITY,SEC_V_Desc:POSITION,SEC_V_Desc:ACCOUNT"

// Texte
InitialValue = "Allocation - Maturity"
```

**Temps:** 2min par paramètre

---

#### Pattern C: declarative:InitialValueFromPref (4% des cas)

**Indicateur:** `"implementationPattern": "declarative:InitialValueFromPref"`

**Préférence définie dans l'état:** `fonction.preference`

**Code:**
```csharp
this.AddParameter(new ParameterJoinEntity(
    reportMetaDataFromRtm,
    "PARAM_{XXX}",
    ParameterType.Hidden,
    8)
{
    ValidationFunction = "GetBoolFromPref({PREF_NAME})",
    InitialValueFromPref = "{fonction.preference}"  // Ex: "PREF_REPORT_BVMV_IND"
});
```

**Temps:** 2min par paramètre

---

#### Pattern D: declarative:InitialValueDateType (<1% des cas)

**Indicateur:** `"implementationPattern": "declarative:InitialValueDateType"`

**Date système sans calcul**

**Code:**
```csharp
this.AddParameter(new ParameterJoinEntity(
    reportMetaDataFromRtm,
    "PARAM_{XXX}",
    ParameterType.Date,
    5)
{
    ValidationFunction = "{FunctionName}",
    InitialValueDateType = "LastProcessedDate"  // DateType enum
});
```

**DateType disponibles:**
- LastProcessedDate
- FirmStartDate
- CurrentDate
- AsOfDate

**Temps:** 2min par paramètre

---

#### Pattern E: custom:ValueProviderFunction (>10% des cas)

**Indicateur:** `"implementationPattern": "custom:ValueProviderFunction"`

**Classe Parameter sera créée en Phase B**

**Code (dans Parameters.cs):**
```csharp
this.AddParameter(new ParameterJoinEntity(
    reportMetaDataFromRtm,
    "PARAM_{XXX}",
    ParameterType.{Type},
    {widgetType})
{
    ValueProviderFunction = "{FunctionName}"  // Classe créée Phase B
});
```

**Note:** La classe Parameter correspondante sera implémentée en Phase B.

**Temps:** 1min configuration (classe créée séparément)

---

### Étape 3: Organiser Paramètres

**Ordre recommandé dans le fichier:**

1. **Section PRE** (widgetType < 8) - Paramètres pré-entrée
   - Widget 2 (Radio)
   - Widget 3 (CheckBox)
   - Widget 5 (Date)

2. **Section POST** (widgetType >= 8) - Paramètres post-entrée
   - Widget 8 (Hidden)

**Ajouter commentaires:**
```csharp
// ========== PRE PARAMETERS ==========

// Radio (Widget 2)
this.AddParameter(new ParameterJoinEntity(...) { ... });

// CheckBox (Widget 3)
this.AddParameter(new ParameterJoinEntity(...) { ... });

// Date (Widget 5)
this.AddParameter(new ParameterJoinEntity(...) { ... });

// ========== POST PARAMETERS ==========

// Hidden (Widget 8)
this.AddParameter(new ParameterJoinEntity(...) { ... });
```

---

### Étape 4: Valider Build

```bash
cd ../monolith/CFF/Products/ReportManagerApi
dotnet build ReportManagerAPI.sln
```

**Si erreurs de compilation:**
- Vérifier using statements
- Vérifier noms de paramètres (PARAM_{XXX})
- Vérifier types (ParameterType enum)

---

### Étape 5: Update État

**Pour chaque paramètre déclaratif configuré:**

```bash
manage-state → update {REPORT-ID}:
- completedParameters += {
    "name": "{FunctionName}",
    "type": "declarative",
    "file": "Parameters.cs ligne {X}",
    "pattern": "{implementationPattern}",
    "testsFile": null,
    "testsStatus": "not_required",
    "registered": "n/a",  // Déclaratifs ne nécessitent pas d'enregistrement
    "completedAt": "{timestamp}"
  }
- pendingParameters -= "{FunctionName}"
```

**Update step:**
```bash
manage-state → update {REPORT-ID}:
- development.currentStep: "parameters_declarative_completed"
```

**Temps total Phase A:** 5-20min selon nombre de paramètres

---

## PHASE B: Classes Parameter Custom (Si Nécessaire)

**Condition:** SEULEMENT si `state.analysis.functionsToAnalyze` contient des fonctions avec `implementationPattern: "custom:ValueProviderFunction"`

---

### Étape 1: Filtrer Fonctions Custom

```javascript
const customFunctions = state.analysis.functionsToAnalyze.filter(
  f => f.implementationPattern && f.implementationPattern.includes("custom:")
);

if (customFunctions.length === 0) {
  // Aucune classe à créer, passer directement Phase 3 (Enregistrement)
  return;
}
```

---

### Étape 2: Pour Chaque Fonction Custom

**Sous-étape 2.1: Vérifier si déjà implémentée**

→ **Skill:** `check-implementation`

**Résultats possibles:**
- `implemented` → Passer à suivante (déjà fait)
- `alias_available` → Vérifier alias, enregistrer si nécessaire
- `missing` ou `TODO` → Continuer implémentation

---

**Sous-étape 2.2: Créer Classe Parameter**

→ **Skill:** `implementation-guide` (Patterns 1-9)

**Emplacement:**
```
../monolith/CFF/Products/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/{Category}/{FunctionName}Parameter.cs
```

**Catégories courantes:**
- `Date/` - Fonctions de date
- `Preference/` - Fonctions de préférences
- `Hidden/` - Fonctions hidden spécifiques
- `Calculation/` - Calculs complexes

**Template de base:**
```csharp
using Croesus.Reports.Parameters.Model;
using Croesus.Reports.Parameters.Services;
using ReportManagerAPI.Domain.Services;

namespace ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters.{Category}
{
    public class {FunctionName}Parameter : IValueProvidedParameter
    {
        private readonly {IDependency} _dependency;

        public {FunctionName}Parameter({IDependency} dependency)
        {
            _dependency = dependency;
        }

        public ReportParameterMetaData ProvideValue(
            ReportParameterMetaData parameter,
            ReportMetaDataFromRtm reportMetaDataFromRtm)
        {
            // Logique depuis analyse C++
            parameter.InitialValue = /* calcul */;
            return parameter;
        }
    }
}
```

**Injection dépendances courantes:**
- `IPreferencesRepository` - Lecture préférences
- `IReportCommandAndQueryContextRepository` - Contexte rapport/paramètres
- `IParameterDateValueService` - Services de dates
- `IDateTimeService` - Transformations dates
- `SourceTypes requestSourceType` - Type de source (Client/Account/Portfolio)

---

**Sous-étape 2.3: Créer Tests**

→ **Skill:** `implementation-guide` (Section Tests)

**Emplacement:**
```
../monolith/CFF/Products/ReportManagerApi/ReportManagerAPI.Infrastructure.SmallTests/Repositories/ValueProviderFunctions/Parameters/{Category}/{FunctionName}ParameterTests.cs
```

**Template tests minimaux:**
```csharp
using FluentAssertions;
using Moq;
using Xunit;

namespace ReportManagerAPI.Infrastructure.SmallTests.Repositories.ValueProviderFunctions.Parameters.{Category}
{
    public class {FunctionName}ParameterTests
    {
        [Fact]
        public void GivenValidInput_WhenProvideValue_ThenReturnsExpected()
        {
            // Arrange
            var mockDependency = new Mock<{IDependency}>();
            mockDependency.Setup(x => x.Method(...)).Returns(...);

            var parameter = new {FunctionName}Parameter(mockDependency.Object);
            var reportParam = new ReportParameterMetaData();
            var reportMeta = new ReportMetaDataFromRtm();

            // Act
            var result = parameter.ProvideValue(reportParam, reportMeta);

            // Assert
            result.InitialValue.Should().Be("expected");
        }
    }
}
```

**Tests minimaux requis:**
- 1 test nominal (cas standard)
- 1 test edge case (fin de mois, null, etc.)
- 1 test error handling si applicable

---

**Sous-étape 2.4: Build & Tests**

```bash
# Build
cd ../monolith/CFF/Products/ReportManagerApi
dotnet build ReportManagerAPI.sln

# Tests spécifiques
dotnet test --filter "FullyQualifiedName~{FunctionName}ParameterTests"
```

---

**Sous-étape 2.5: Update État**

```bash
manage-state → update {REPORT-ID}:
- completedParameters += {
    "name": "{FunctionName}",
    "type": "implemented",
    "file": "Parameters/{Category}/{FunctionName}Parameter.cs",
    "testsFile": "Parameters/{Category}/{FunctionName}ParameterTests.cs",
    "testsStatus": "passing",
    "registered": false,  // Sera enregistré Phase 3
    "completedAt": "{timestamp}"
  }
- pendingParameters -= "{FunctionName}"
```

---

**Sous-étape 2.6: Informer Progression**

```
✅ {FunctionName} complété ({X}/{total} custom)
   Fichier: Parameters/{Category}/{FunctionName}Parameter.cs
   Tests: 3 tests passent
   Temps: {elapsed}
```

---

### Étape 3: Récapitulatif Phase B

**Temps estimé:** Variable selon complexité
- Pattern simple (1 préférence): 30min-1h
- Pattern moyen (calculs dates): 1h-2h
- Pattern complexe (multiples dépendances): 2h-4h

---

## Output Final

**Fichiers créés/modifiés:**

**Phase A (Obligatoire):**
- ✅ `{ReportName}Parameters.cs` - Configuration complète des 19 paramètres

**Phase B (Si custom functions):**
- ✅ `Parameters/{Category}/{Function}Parameter.cs` - Classe(s) custom
- ✅ `Parameters/{Category}/{Function}ParameterTests.cs` - Tests unitaires

**État mis à jour:**
- ✅ `completedParameters[]` - Tous paramètres trackés
- ✅ `pendingParameters[]` - Vide
- ✅ `development.currentStep` - "parameters_completed"

---

## Validation Finale

**Checklist avant passer à Phase 3 (Enregistrement):**

- [ ] Fichier Parameters.cs existe et compile
- [ ] TOUS les paramètres configurés (déclaratifs + custom)
- [ ] Build réussit sans erreurs
- [ ] Tests classes custom passent (si applicables)
- [ ] État mis à jour correctement
- [ ] Aucun `pendingParameters` restant

---

## Erreurs Courantes

**Erreur 1: Sauter Phase A**
```
❌ Créer classes custom avant Parameters.cs
✅ TOUJOURS créer Parameters.cs en premier
```

**Erreur 2: Créer classe pour déclaratif**
```
❌ Créer classe pour InitialValue="constante"
✅ Utiliser InitialValue dans Parameters.cs
```

**Erreur 3: Mauvais ParameterType**
```
❌ ParameterType.Hidden pour widget 3
✅ ParameterType.CheckBox pour widget 3
```

**Erreur 4: Oublier using statements**
```csharp
using Croesus.Reports.Parameters.Model;
using System.Collections.Generic;
```

---

## Références

**Skills complémentaires:**
- `implementation-guide` - Patterns 1-9 classes custom
- `check-implementation` - Vérifier si déjà implémenté
- `register-parameter` - Enregistrement Phase 3
- `manage-state` - Gestion état persistant
- `generic-functions-reference` - Hiérarchie décision

**Documentation:**
- Spec: `.work/{slug}/spec.md`
- Classification: `.work/{slug}/analysis-classification.md`
- État: `.work/{slug}/state.json`

---

## Temps Total Estimé

**Rapport moyen (19 paramètres, 17 déclaratifs + 2 custom):**
- Phase A: 17min (configuration déclarative)
- Phase B: 1-2h (2 classes custom)
- **Total: 1.5-2.5h**

**Ratio temps:**
- >90% des paramètres (déclaratifs) = 15% du temps
- >10% des paramètres (custom) = 85% du temps

**💰 C'est pourquoi Phase A ne doit JAMAIS être sautée!**
