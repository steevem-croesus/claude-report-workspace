---
name: register-parameter
description: Enregistre automatiquement un IValueProviderParameter dans l'executer approprié (Pre/Post) en respectant l'ordre alphabétique. Utiliser après avoir implémenté une nouvelle classe Parameter pour la rendre accessible dans le système.
allowed-tools: Read, Edit, Grep, Bash
---

# Skill: Register Parameter

> **⚠️ NOTE SYMLINKS:** `ReportFoundations` et `ReportManagerApi` sont des **liens symboliques**. Utiliser `find -L` pour suivre les symlinks.

Enregistre automatiquement un paramètre ValueProvider dans l'executer et le configure dans Parameters.cs.

## Mission

Enregistrer de manière autonome un paramètre dans le système de génération de rapports (deux étapes critiques).

## Input

L'utilisateur fournit:
- **Nom de fonction**: Ex: `InitGainLossCost`
- **Type d'entrée**: `PRE` ou `POST`
- **ID du rapport** (optionnel): Pour mise à jour de Parameters.cs

Exemples: `Enregistre InitGainLossCost en PRE` | `Enregistre GetBoolFromPref en POST pour GP_NON_REALISE`

## Étape 1: Enregistrement dans l'executer

### 1.1 Déterminer fichier cible

| Type | Fichier | Chemin |
|------|---------|--------|
| `PRE` | `PreParamEntryValueProviderFunctionsExecuter.cs` | `ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/` |
| `POST` | `PostParamEntryValueProviderFunctionsExecuter.cs` | `ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/` |

**Rappel:**
- **PRE**: Paramètres initialisés AVANT affichage formulaire (valeurs par défaut)
- **POST**: Paramètres calculés APRÈS saisie utilisateur (dépendent d'autres paramètres)

### 1.2 Analyser paramètre existant

**AVANT d'enregistrer:**

1. Localiser `{NomFonction}Parameter.cs` dans `ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/`
2. Examiner constructeur pour identifier dépendances:
   ```csharp
   public InitGainLossCostParameter(IPreferencesRepository preferencesRepository)
   ```
3. Vérifier disponibilité dans l'executer:
   - `preferencesRepository`
   - `reportCommandAndQueryContextRepository`
   - `requestSourceType`
   - `dateTimeService`
   - `repartitionsRepository`
   - `industryCodeRepository`
   - `indexesRepository`

**Si dépendance manquante:** Demander à l'utilisateur comment l'injecter. NE PAS modifier le constructeur sans confirmation.

### 1.3 Ajouter enregistrement (ORDRE ALPHABÉTIQUE STRICT)

**CRITIQUE: Respecter ordre alphabétique!**

1. Lire fichier executer complet
2. Localiser `InitializeValueProviderFunctionImplementations`
3. Trouver position alphabétique correcte
4. Insérer enregistrement avec dépendances appropriées

**Exemples:**

```csharp
// Avec préférences
implementationsDictionary["InitGainLossCost"] =
    () => new InitGainLossCostParameter(preferencesRepository);

// Avec SourceTypes
implementationsDictionary["InitDefaultIndex"] =
    () => new InitDefaultIndexParameter(requestSourceType);

// Plusieurs dépendances
implementationsDictionary["ComplexParameter"] =
    () => new ComplexParameter(preferencesRepository, requestSourceType, dateTimeService);

// Sans dépendances (helper)
implementationsDictionary["Period1"] = () => new StringParameter("3");
```

**Vérifications:**
- Nom clé = nom classe (sans "Parameter")
- Ordre alphabétique respecté
- Dépendances correspondent au constructeur
- Commentaires de groupe (// A, // B) préservés

## Étape 2: Configuration dans Parameters.cs

### 2.1 Localiser fichier

Si ID rapport fourni (avec -L pour suivre symlinks):
```bash
find -L ReportFoundations -name "Parameters.cs" -path "*{REPORT_ID}*" 2>/dev/null
```

Structure: `repos/ReportFoundations/ReportImplementations/Implementations/Reports/[Catégorie]/[Nom]/Parameters.cs`

### 2.2 Identifier paramètre et ajouter ValueProviderFunction

Chercher le paramètre par nom technique (ex: `PARAM_GainLossCostDisplayed`):

```csharp
this.AddParameter(new ParameterJoinEntity(
    this.GlobalProviders.Parameters.GetEntity(Params.PARAM_GainLossCostDisplayed))
{
    WindowOrder = 3,
    Position = 2,
    PositionH = 1,
    ValidationFunction = "",
    ValueProviderFunction = "InitGainLossCostDisplayed"  // AJOUTER ICI
});
```

**IMPORTANT:** Nom doit correspondre EXACTEMENT à la clé dans `implementationsDictionary` (casse respectée).

### 2.3 Décision ValidationFunction vs ValueProviderFunction

**Si `ValidationFunction` + `InitialValue` déjà présents:**

Demander à l'utilisateur:
- Remplacer par `ValueProviderFunction`?
- Ou garder les deux?

**Arbre de décision:**
- Valeur **statique** → `ValidationFunction` + `InitialValue` suffit
- Valeur **dynamique** (préférences, contexte, DB) → `ValueProviderFunction` nécessaire
- Valeur **par défaut + override** → Les deux propriétés

## Étape 3: Vérification et build

### Build et tests

```bash
cd /home/lab/projects/reports/../monolith/CFF/Products/ReportManagerApi

# Build
dotnet build ReportManagerAPI.sln

# Tests (si applicable)
dotnet test --filter "FullyQualifiedName~{NomFonction}ParameterTests"
```

### Troubleshooting

**"Type or namespace 'X' not found":**
→ Ajouter using manquant:
```csharp
using ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters;
using ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters.Date;
```

**"No parameterless constructor":**
→ Re-examiner constructeur et corriger dépendances dans l'enregistrement

**Duplicate key:**
→ Chercher doublons, informer utilisateur

## Checklist finale

- [ ] Nom dans `implementationsDictionary` = nom classe (sans "Parameter")
- [ ] Ordre alphabétique respecté
- [ ] Dépendances correctement injectées
- [ ] `ValueProviderFunction` dans Parameters.cs (si applicable)
- [ ] Nom dans `ValueProviderFunction` = clé dictionnaire
- [ ] Build réussi
- [ ] Tests passent

## Rapport de fin

Fournir:
1. **Résumé**: Fichier(s) modifié(s), ligne(s) ajoutée(s)
2. **Statut build**: ✅ Réussi / ❌ Échoué (détails)
3. **Prochaines étapes**: Tester manuellement, créer/exécuter tests unitaires

## Références

- Guide migration: `/home/lab/projects/reports/MIGRATION_PROCEDURE_HUMAN.md` (Étape 6)
- CLAUDE.md: Section "Adding a ValueProviderParameter"
- Skills: `implement-parameter`, `analyze-cpp-function`
