---
name: check-implementation
description: Vérifie si une fonction ValueProviderParameter est déjà implémentée en C#, son statut (implémenté/TODO/inexistant), et localise le code. Utiliser avant de commencer une nouvelle implémentation pour éviter la duplication.
---

# Skill: Check Implementation

> **⚠️ NOTE SYMLINKS:** `ReportManagerApi` est un **lien symbolique**. Utiliser `find -L` pour suivre les symlinks, ou utiliser l'outil `Grep` avec un chemin explicite.

Vérifie rapidement si une fonction spécifique est déjà implémentée en C#.

## Objectif

Analyser le statut d'implémentation d'une fonction C# ValueProviderParameter et fournir des détails complets sur son état actuel.

## Input Attendu

- **Nom de fonction** (ex: `AsOfDate`, `InitGainLossCostDisplayed`)
- Optionnel: Type attendu (PRE ou POST) pour validation de cohérence

## Processus

### 1. Recherche dans les Executers

**Chercher dans PRE executer:**
```bash
grep -n "\"$FunctionName\"" \
  ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/PreParamEntryValueProviderFunctionsExecuter.cs
```

**Chercher dans POST executer:**
```bash
grep -n "$FunctionName" \
  ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/PostParamEntryValueProviderFunctionsExecuter.cs
```

### 2. Déterminer le Statut

| Pattern Trouvé | Statut | Symbole |
|----------------|--------|---------|
| `new FunctionNameParameter(dependencies)` | ✅ Implémenté | ✅ |
| `new UnimplementedParameter() // TODO` | ⚠️ TODO | ⚠️ |
| Non trouvé | 🔴 Inexistant | 🔴 |

### 3. Localiser le Fichier Parameter (si implémenté)

**Pattern de recherche (avec -L pour suivre symlinks):**
```bash
find -L repos/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters \
  -name "${FunctionName}Parameter.cs" -o -name "*${FunctionName}*.cs" 2>/dev/null
```

### 4. Extraire les Détails (si trouvé)

**Lire le fichier Parameter:**
```bash
Read ReportManagerAPI.Infrastructure/.../Parameters/.../${FunctionName}Parameter.cs
```

**Extraire:**
- Dépendances injectées (constructor parameters)
- Repositories utilisés (I*Repository)
- Services utilisés (I*Service)
- Logique dans `ProvideValue()`

### 5. Vérifier les Tests

**Chercher le fichier de tests (avec -L pour suivre symlinks):**
```bash
find -L repos/ReportManagerApi/ReportManagerAPI.Infrastructure.SmallTests \
  -name "${FunctionName}ParameterTests.cs" 2>/dev/null
```

**Statut tests:**
- ✅ Fichier existe
- ❌ Fichier manquant

### 6. Vérifications de Cohérence

#### Cas Particulier 1: Fonction dans Mauvais Executer

Si fonction PRE trouvée dans POST executer (ou vice-versa):

```
⚠️ ATTENTION: Incohérence détectée!
- Trouvé dans: PostParamEntryValueProviderFunctionsExecuter.cs
- Attendu: PreParamEntryValueProviderFunctionsExecuter.cs (basé sur WIDGET_TYPE)

Action: Déplacer vers le bon executer
```

#### Cas Particulier 2: Fonction avec Alias

Si la fonction a plusieurs noms (ex: `IndexListWhithIndexPerso` et `IndexListWhithIndexPersoSymb`):
- Chercher tous les alias
- Indiquer s'ils pointent vers la même implémentation

#### Cas Particulier 3: Default vs Specific

Si fonction Default vérifiée alors qu'une Specific existe:

```
ℹ️ INFO: Fonction Default ignorée
- Default: CheckFalse
- Specific: PerfDoGraphAssetMix (priorité)

Recommandation: Vérifier 'PerfDoGraphAssetMix' à la place
```

## Output Attendu

**Format de rapport:**

```markdown
# Status: {FunctionName}

## Résultat

**Statut:** ✅ Implémenté | ⚠️ TODO | 🔴 Inexistant

**Localisation:**
- Executer: {Pre|Post}ParamEntryValueProviderFunctionsExecuter.cs:{ligne}
- Fichier Parameter: Parameters/{Category}/{FunctionName}Parameter.cs
- Tests: {✅ Existe | ❌ Manquant}

## Détails de l'Implémentation

{Si ✅ Implémenté:}

**Dépendances injectées:**
- `IParameterDateValueService`
- `IReportCommandAndQueryContextRepository`
- [autres dépendances]

**Code (extrait):**
```csharp
public class {FunctionName}Parameter : IValueProviderParameter
{
    // Constructor avec dépendances

    public string ProvideValue(string[] parameters)
    {
        // Logique...
    }
}
```

**Tests:**
- Fichier: `{FunctionName}ParameterTests.cs` ✅
- Localisation: `ReportManagerAPI.Infrastructure.SmallTests/.../`

{Si ⚠️ TODO:}

**Enregistrement:**
- Enregistré avec `UnimplementedParameter()`
- Localisation: {executer}:{ligne}

**Actions requises:**
1. Localiser code C++ source → skill: `locate-cpp-function`
2. Analyser dépendances → skill: `analyze-cpp-function`
3. Implémenter la logique
4. Écrire les tests

{Si 🔴 Inexistant:}

**Aucune trace trouvée dans:**
- PreParamEntryValueProviderFunctionsExecuter.cs ❌
- PostParamEntryValueProviderFunctionsExecuter.cs ❌

**Actions requises:**
1. Déterminer ENTRY_TYPE (PRE ou POST) basé sur WIDGET_TYPE
2. Localiser code C++ → skill: `locate-cpp-function`
3. Créer classe Parameter
4. Enregistrer dans executer approprié
5. Écrire tests

## Prochaines Étapes Recommandées

{Si ✅ Implémenté:}
✅ Aucune action - fonction opérationnelle

{Si ⚠️ TODO:}
→ Utiliser skill `implementation-guide` pour patterns
→ Utiliser skill `locate-cpp-function` pour trouver le code source

{Si 🔴 Inexistant:}
→ Utiliser skill `classify-functions` pour contexte global
→ Utiliser skill `locate-cpp-function` pour localiser le C++
→ Utiliser skill `analyze-cpp-function` pour analyser la logique
```

## Résumé Visuel Console

```
🔍 Check: {FunctionName}

Status: {✅|⚠️|🔴} {Implémenté|TODO|Inexistant}
Location: {fichier}:{ligne}
Parameter: {FunctionNameParameter.cs}
Tests: {✅ Existe | ❌ Manquant}

{Action recommandée si applicable}
```

## Utilisation dans les Commandes

Ce skill peut être appelé par:
- `analyze-report` (pendant la phase de classification)
- Invocation directe via agent pour vérification ponctuelle
- `classify-functions` pour détails sur une fonction spécifique

## Références

**Fichiers clés:**
- Executer PRE: `ReportManagerAPI.Infrastructure/.../PreParamEntryValueProviderFunctionsExecuter.cs`
- Executer POST: `ReportManagerAPI.Infrastructure/.../PostParamEntryValueProviderFunctionsExecuter.cs`
- Parameters: `ReportManagerAPI.Infrastructure/.../Parameters/`

**Skills complémentaires:**
- `locate-cpp-function` - Trouver le code C++ source
- `analyze-cpp-function` - Analyser la logique C++
- `classify-functions` - Vue d'ensemble de toutes les fonctions
- `generic-functions-reference` - Vérifier si fonction devrait être générique
- `best-practices-analyst` - Valider la qualité de l'implémentation
- `implementation-guide` - Patterns d'implémentation
