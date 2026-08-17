---
name: register-ignore-id-masking
description: Ajoute un rapport dans GetDisplayUnmaskedIdParameter (ReportsWithInitialValueZero) et son InlineData de test. Utiliser quand un rapport migré possède le paramètre PARAM_IgnoreIdMasking.
allowed-tools: Read, Edit, Grep, Glob, Bash
---

# Skill: Register Ignore Id Masking

Ajoute un rapport dans `GetDisplayUnmaskedIdParameter.ReportsWithInitialValueZero` et dans le test associé.

**Utilisé par:** report-developer (pendant la migration d'un rapport qui possède `PARAM_IgnoreIdMasking`)

---

## Quand utiliser ce skill

**Condition:** Le rapport en cours de migration possède le paramètre `PARAM_IgnoreIdMasking`.

Si le rapport n'a pas ce paramètre, ne pas utiliser ce skill.

---

## Input

L'utilisateur fournit:
- **Nom interne du rapport**: Ex: `FOREIGN_PROPERTY` (le nom utilisé dans le système, pas le nom de classe C#)

Si non fourni, déduire du rapport en cours de migration.

---

## Fichiers à modifier

| Fichier | Chemin |
|---------|--------|
| Classe | `repos/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/Hidden/GetDisplayUnmaskedIdParameter.cs` |
| Tests | `repos/ReportManagerApi/ReportManagerAPI.Infrastructure.SmallTests/Repositories/ValueProviderFunctions/Parameters/Hidden/GetDisplayUnmaskedIdParameterTests.cs` |

---

## Étape 0: Vérifier que le rapport possède PARAM_IgnoreIdMasking

**IMPORTANT:** Les paramètres peuvent être définis dans une classe **Base** partagée (ex: `Base/Parameters.cs`), pas seulement dans le `Parameters.cs` du rapport spécifique. Chercher dans **tout le dossier** du rapport.

```bash
find -L ReportFoundations -path "*NomRapport*" -name "Parameters.cs" -exec grep -l "PARAM_IgnoreIdMasking" {} \;
```

Si `PARAM_IgnoreIdMasking` n'est trouvé dans aucun `Parameters.cs` du rapport (ni Standard, ni Base), **ne pas procéder** et informer l'utilisateur.

---

## Étape 1: Vérifier que le rapport n'est pas déjà enregistré

```bash
grep "NOM_INTERNE" repos/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/Hidden/GetDisplayUnmaskedIdParameter.cs
```

Si déjà présent, informer l'utilisateur et ne rien faire.

---

## Étape 2: Ajouter dans ReportsWithInitialValueZero

Dans `GetDisplayUnmaskedIdParameter.cs`, localiser le `HashSet<string> ReportsWithInitialValueZero` et insérer le nom interne du rapport en **ordre alphabétique**.

**Format:**
```csharp
            "NOM_INTERNE",
```

**Exemple:** Pour `FOREIGN_PROPERTY`, insérer entre `DOCUMENT_SUMMARY` et `GAIN_PERTE`:
```csharp
            "DOCUMENT_SUMMARY",
            "FOREIGN_PROPERTY",
            "GAIN_PERTE",
```

**Important:**
- Respecter l'indentation existante (12 espaces)
- Terminer par une virgule
- Ordre alphabétique strict

---

## Étape 3: Ajouter InlineData dans le test

Dans `GetDisplayUnmaskedIdParameterTests.cs`, localiser la liste des `[InlineData]` de la méthode `ProvideValue_ShouldSetInitialValueBasedOnReportName`.

Ajouter un `InlineData` pour le nouveau rapport **au début de la liste** (juste après le `[Theory]`), avec la valeur attendue `"0"`:

```csharp
        [InlineData("NOM_INTERNE", "0")]
```

**Exemple:**
```csharp
        [Theory]
        [InlineData("FOREIGN_PROPERTY", "0")]
        [InlineData("ASSET_MIX", "0")]
        ...
```

**Important:**
- Valeur attendue toujours `"0"` (le rapport est dans le set)
- Insérer au début de la liste d'InlineData, juste après `[Theory]`

---

## Étape 4: Vérification

### Checklist finale

- [ ] Rapport pas déjà dans `ReportsWithInitialValueZero`
- [ ] Nom interne ajouté en ordre alphabétique dans le HashSet
- [ ] `[InlineData("NOM_INTERNE", "0")]` ajouté au début du test
- [ ] Indentation cohérente avec les entrées existantes

---

## Rapport de fin

Fournir:
1. **Rapport ajouté:** Nom interne
2. **Position dans HashSet:** Entre quelles entrées il a été inséré
3. **InlineData ajouté:** Confirmation
4. **Fichiers modifiés:** Liste des 2 fichiers

---

## Référence

**Implémentation de référence:** `ASSETS_UNDER_MGT` ajouté dans RPT-18494 (commit `58cd1e8860`)

**Fichiers:**
- `repos/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/Hidden/GetDisplayUnmaskedIdParameter.cs`
- `repos/ReportManagerApi/ReportManagerAPI.Infrastructure.SmallTests/Repositories/ValueProviderFunctions/Parameters/Hidden/GetDisplayUnmaskedIdParameterTests.cs`
