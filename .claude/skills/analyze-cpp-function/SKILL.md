---
name: analyze-cpp-function
description: Analyse en profondeur une fonction C++ de rapport pour identifier patterns, dépendances et logique métier. Utiliser après locate-cpp-function pour créer une spec détaillée d'implémentation C# avec pseudo-code et mapping des repositories.
---

# Skill: Analyze C++ Function

Analyser fonction C++ de rapport pour identifier patterns, dépendances et logique métier.

**Input requis:**
- Nom fonction (ex: `InitGainLossCostDisplayed`)
- Code source C++ (via `locate-cpp-function` ou direct)
- Context: Widget Type, Entry Type, Paramètre (PARAM_XXX)

**Note:** Templates d'implémentation → `implementation-guide`

## Mode d'Utilisation

**Mode 1: Analyse Rapide de Complexité** (pour classify-functions)
- Input: Code source C++ d'une fonction
- Output: SIMPLE vs COMPLEXE + raison
- Temps: < 30 secondes

**Mode 2: Analyse Complète** (pour spec détaillée)
- Input: Code source C++ + contexte
- Output: Spec markdown complète
- Temps: 5-10 minutes

## Mode 1: Détection Rapide de Complexité ⚡

**OBJECTIF:** Déterminer si une fonction C++ peut être gérée par framework (SIMPLE) ou nécessite une classe Parameter custom (COMPLEXE).

**Utiliser ce mode quand:** classify-functions trouve une ValidationFunction dans *ParametersImplementation.cs et doit vérifier si elle est vraiment simple.

### Critères de Classification

**SIMPLE** → Pattern déclaratif (InitialValue, InitialValueFromPref, framework)
```c
// Exemples de fonctions SIMPLES:
void CheckTrue(REPORT_CTR_PARAM *pParam, ...) {
    pParam->SetValue("1");  // Une seule ligne, une seule valeur
}

void GetBoolFromPref(REPORT_CTR_PARAM *pParam, ...) {
    char* pref = GetPreference("PREF_XXX");
    pParam->SetValue(pref == "YES" ? "1" : "0");  // 1 préférence, mapping simple
}
```

**Caractéristiques SIMPLES:**
- ✅ 0-1 dépendance (PARAM_ OU PREF_, pas les deux)
- ✅ 0-1 instruction `if` (simple ternaire OK)
- ✅ 1 seul `SetValue()` ou return direct
- ✅ Pas de lecture d'autres paramètres du contexte
- ✅ Pas de calculs ou boucles

**COMPLEXE** → Pattern custom (nécessite classe Parameter)
```c
// Exemple de fonction COMPLEXE:
void IsBatchUseGicsBreakdown(REPORT_CTR_PARAM *pParam, ...) {
    pParam->SetValue("0");  // Défaut

    // Dépendance 1: PREF
    if (GetPreference("PREF_ENABLE_GICS") != "YES") return;

    // Dépendance 2-3: Lecture autres PARAM_
    char* indCodeCombo = GetParam(pParam, PARAM_IndCodeCombo);
    char* indCodeCheck = GetParam(pParam, PARAM_IndCodeCheck);

    if (indCodeCheck != "1") return;

    // Dépendance 4: Repository
    IndustryCodeSet* codeSet = GetIndustryCodeSet(atoi(indCodeCombo));
    if (codeSet && codeSet->id == GICS_SET_ID) {
        pParam->SetValue("1");
    }
}
```

**Caractéristiques COMPLEXES:**
- ❌ 2+ dépendances (PREF_ + PARAM_ + Repository)
- ❌ 2+ instructions `if` (logique conditionnelle complexe)
- ❌ Lecture d'autres paramètres du contexte (GetParam sur autre PARAM_)
- ❌ Appels à des repositories/services (GetIndustryCodeSet, GetRepartition, etc.)
- ❌ Calculs, boucles, transformations
- ❌ 2+ `SetValue()` (valeurs multiples selon conditions)

### Processus de Détection Rapide

**Input:** Code source C++ de la fonction + **ReportCode/ValidationName du rapport** (ex: "UnrealizedGainLoss" pour GP_NON_REALISES)

**Étapes:**

0. **⚠️ CRITIQUE: Vérifier contexte rapport spécifique AVANT analyse générique**

   Si la fonction contient des branches par ValidationName/ReportCode:
   ```cpp
   if (sValidationName == "UnrealizedGainLoss") { ... }
   else if (sValidationName == "AlarmsDataEntryPoint") { ... }
   ```

   a. Chercher la branche pour CE rapport: `grep -A 5 "ValidationName.*{ReportCode}\|sReportCode.*{ReportCode}"`
   b. Analyser UNIQUEMENT cette branche:
      - Si retourne une constante unique → **SIMPLE** (InitialValue = "{constante}")
      - Si contient logique dynamique → Continuer analyse
   c. **IGNORER les autres branches** - elles ne s'appliquent pas à ce rapport!

   **Exemple:**
   ```cpp
   // Pour GP_NON_REALISES (ValidationName = "UnrealizedGainLoss"):
   if (sValidationName == "UnrealizedGainLoss") {
       return "RAM_V_Level1Name|PAP_V_Value|ACC_Key";  // ← CONSTANTE!
   }
   // Les 15 autres branches sont IGNORÉES pour ce rapport
   ```
   → Verdict: **SIMPLE** | InitialValue = "RAM_V_Level1Name|PAP_V_Value|ACC_Key"

1. **Compter dépendances:**
   - `PREF_`: `grep -c "PREF_" | grep -c "GetPreference"`
   - `PARAM_`: `grep -c "PARAM_" | grep -c "GetParam"` (EXCLURE le paramètre courant)
   - Repositories: `grep -c "Get.*Set\|Get.*List\|Get.*Data\|Query"`

2. **Compter branches:**
   - `if` statements: `grep -c "^\s*if\s*("` (pas de ternaires)
   - `else` statements: `grep -c "^\s*else"`

3. **Compter SetValue:**
   - `grep -c "SetValue"`

4. **Détecter patterns complexes:**
   - Boucles: `grep "for\s*(\|while\s*("`
   - Calculs: `grep "\*\s\|/\s\|+\s[0-9]\|-\s[0-9]"`
   - Lecture autres params: `grep "GetParam.*PARAM_" | grep -v "{CurrentParam}"`

**Décision:**
```
# ÉTAPE 0 D'ABORD - Contexte rapport-spécifique
SI fonction contient branches par ValidationName/ReportCode:
    SI branche pour CE rapport retourne constante unique:
        → SIMPLE (InitialValue = "{constante}")
        → FIN (ne pas continuer l'analyse générique)
    SINON:
        → Continuer avec analyse générique sur la branche spécifique

# ANALYSE GÉNÉRIQUE (si étape 0 n'a pas conclu)
SI (dépendances >= 2) OU (if count > 1) OU (SetValue > 1) OU (lecture autres params > 0) OU (repositories > 0) OU (boucles > 0):
    → COMPLEXE
SINON:
    → SIMPLE
```

### Output Mode 1 (Rapide)

```markdown
# Complexité: {FunctionName}

**Verdict:** ✅ SIMPLE | ❌ COMPLEXE

**Contexte Rapport-Spécifique:** {oui/non}
- Si oui: Branche pour {ReportCode} retourne: "{valeur_constante}"

**Métriques:**
- Dépendances: {count} (PREF_: {x}, PARAM_: {y}, Repositories: {z})
- Branches if/else: {count}
- SetValue calls: {count}
- Lecture autres params: {yes/no}
- Boucles/calculs: {yes/no}

**Raison:** {Explication 1 ligne}

**Recommandation:**
- SIMPLE (contexte rapport) → InitialValue="{valeur_constante}" (extraite de la branche spécifique)
- SIMPLE (générique) → Pattern déclaratif (InitialValue="{value}" ou InitialValueFromPref="PREF_XXX")
- COMPLEXE → Pattern custom (créer classe {FunctionName}Parameter)

**Estimated Time:**
- SIMPLE → 0-2min (config only)
- COMPLEXE → 30min-4h (class + tests)
```

---

## Mode 2: Analyse Structurée Complète

**Utiliser ce mode quand:** Fonction confirmée COMPLEXE et besoin de spec détaillée pour implémentation.

### 1. Analyse des Dépendances

**1.1 Paramètres Rapport (PARAM_)**

Patterns C++: `GetParam()`, `GetParamInt()`, `IsParamChecked()`, etc.

Lister tous PARAM_, type d'accès et type de données.

**→ C#:** `IReportCommandAndQueryContextRepository`
```csharp
var value = contextRepository.GetParameter("PARAM_XXX");
var intValue = contextRepository.GetParameterAsInt("PARAM_YYY");
```

**1.2 Préférences (PREF_)**

Patterns C++: `GetPreference()`, `GetBoolFromPref()`, `SetPreference()`

Lister toutes PREF_, type de données, lecture/écriture.

**→ C#:** `IPreferencesRepository`
```csharp
var value = preferencesRepository.GetPreference("PREF_XXX");
```

**1.3 Dates**

Patterns: `GetSelectedYearMonth()`, `GetStartDate()`, `AddMonths()`, etc.

Identifier opérations, formats, calculs.

**→ C#:** `IParameterDateValueService` ou `IDateTimeService`
```csharp
var startYear = dateService.GetStartYearFromSelectedYM(parameters);
```

Si nouvelles méthodes → Ajouter dans `IParameterDateValueService` + implémenter

**1.4 BD et Logique Métier**

- Repartitions → `IRepartitionRepository`
- Transactions → `ITransactionsRepository`
- Industry Codes → `IIndustryCodeRepository`
- Indexes → `IIndexesRepository`

Identifier type données, mapper repository, noter filtres/paramètres.

**1.5 Mapping C++ → C#**

| Pattern C++ | Repository C# |
|-------------|---------------|
| `PREF_*`, `GetCresusConfig()->get()` | `IPreferencesRepository` |
| `PARAM_*`, `GetParam()` | `IReportCommandAndQueryContextRepository` |
| `pReportApi->GetPad()` | `SourceTypes` (constructor) |
| Date operations, `DATE_FIN` | `IParameterDateValueService` / `IDateTimeService` |
| Repartition logic | `IRepartitionRepository` |
| Industry codes | `IIndustryCodeRepository` |
| Indexes | `IIndexesRepository` |
| Transactions | `ITransactionsRepository` |

**Transformations courantes:**
```c
// C++ → C#
GetPreference("PREF_XXX")               → preferencesRepository.GetPreference("PREF_XXX")
GetParam("PARAM_XXX")                   → contextRepository.GetParameter("PARAM_XXX")
pReportApi->GetPad() == REPORT_CLIENT   → requestSourceType == SourceTypes.Client
sPref.CompareCaseInsensitive("YES")     → pref?.Value?.ToUpper() == "YES"
```

**Notes:** Valider `!= null`, logger erreurs, utiliser null-safe operators (`?.`)

**1.6 Logique UI (Ignorer)**

Patterns à ignorer: `SetDlgItemText()`, `EnableWindow()`, `ShowWindow()`, `SendMessage()`, `HWND`

Ne pas migrer logique UI → Focus sur logique métier/calculs

### 2. Analyse Logique

**2.1 Flux Principal** - Décrire en pseudo-code numéroté

**2.2 Conditions** - Lister tous `if/else`, documenter conditions, edge cases, valeurs par défaut

**2.3 Boucles** - Objectif itération, collections parcourues, transformations

**2.4 Calculs** - Identifier calculs mathématiques, conversions, manipulations strings, agrégations

### 3. Cas Particuliers

**3.1 Erreurs** - Noter cas d'erreur, comportement attendu, validations C#

**3.2 Valeurs par Défaut** - Lister toutes, documenter quand utilisées

**3.3 Dépendances Paramètres** - Documenter dépendances inter-paramètres, ordre d'exécution

### 4. Transformations C++ → C#

**Types:** `char*`→`string`, `BOOL`→`bool`, `NULL`→`null`

**Strings:**
- `strcpy(dest, src)` → `dest = src`
- `strcat()` → `+=`
- `sprintf()` → `.ToString()`
- `strcmp()` → `.Equals()`

**Conversions:**
- `atoi()` → `int.Parse()` / `int.TryParse()`
- `atof()` → `double.Parse()`
- `itoa()` → `.ToString()`

**Accès structures:**
- `pParam->value` → `contextRepository.GetParameter(name)` ou `parameters[index]`

### 5. Template Spec C#

```markdown
# Spec: {FunctionName}Parameter

## Contexte
**Fonction C++:** `{FunctionName}` (`validation_xxx.c:{line}`)
**Widget Type:** {type} | **Entry Type:** PRE/POST | **Paramètre:** PARAM_XXX

## Logique Métier

**Description:** {Description fonction}

**Pseudo-code:**
1. Étape 1
2. Étape 2
3. Retourner résultat

**Flux Détaillé:**
- Input: `string[] parameters` (parameters[0] = {desc})
- Traitement: Valider, récupérer PARAM_/PREF_, calculer, formater
- Output: `string` (Format: {desc}, Exemple: "2024-01-01")

## Implémentation

**Pattern:** {1-6} ou Helper (voir `implementation-guide`)

**Approche:** ☐ ValidationFunction ☐ ValueProviderFunction ☐ Mixte

**Dépendances:**
- `IReportCommandAndQueryContextRepository` - PARAM_XXX
- `IPreferencesRepository` - PREF_YYY
- `IParameterDateValueService` - Dates
- `SourceTypes` - Context

**Chemin:** `Parameters/{Category}/{FunctionName}Parameter.cs`
Catégories: Date/, Hidden/, Preference/, General/

**Services nouveaux (si requis):**
- `IParameterDateValueService` → Ajouter `{MethodName}()`

**Tests:** Nominal, null/vide, limites, erreurs (voir `implementation-guide`)

## Complexité

**Cyclomatique:** {Low|Med|High} (Lignes: {X}, Conditions: {Y}, Boucles: {Z}, Deps: {W})
**Risque:** {Low|Med|High}

**Risques:**
1. {Risque} - Impact: {H/M/L} - Mitigation: {Action}

**Points d'attention:**
- {Point 1}

## Questions
- [ ] {Question}

**Ambiguïtés:** {Liste}

## Estimation
- Parameter: {X}h | Service: {Y}h | Tests: {Z}h | **Total: {Total}h**
- **Effort:** {Trivial|Small|Med|Large}

## Références
- Source: `validation_xxx.c:{lines}`
- Similaire: `{Example}Parameter.cs` (PR #{num})
- Skills: `implementation-guide`, `estimate-complexity`
```

## Format Sortie

Générer:

1. **Spec markdown** (template ci-dessus)
2. **Résumé visuel:**
```
📊 {FunctionName}
Complexité: {L/M/H} | Lignes: {X} | Deps: {Y}
PARAM_: {X} | PREF_: {Y} | Dates: {Z}
Nouveaux services: {Y/N} | Tests: {N}
Estimation: {X}h | Risque: {L/M/H}
```

3. **Sauvegarde:** `.work/{slug}/spec.md`

**Références:** `locate-cpp-function` (précédent) → Implementation (suivant)
