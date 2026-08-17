---
name: best-practices-analyst
description: Best practices pour créer des specs de migration de haute qualité. Éviter les anti-patterns courants et documenter correctement les ambiguïtés et edge cases. Utiliser pendant la phase d'analyse.
---

# Skill: Best Practices for Analyst

Éviter anti-patterns et créer specs migration de qualité.

**Audience:** report-analyst (specs uniquement, pas d'implémentation)

---

## Anti-Patterns à Documenter

**1. GetPreferencesValue pour 1 Préférence**

Pour UNE préférence: Utiliser `GetPreference()`, PAS `GetPreferencesValue()`
```markdown
## Dépendances
- IPreferencesRepository - Utiliser GetPreference("PREF_XXX")
⚠️ GetPreferencesValue() réservé pour batch multiple
```

**2. Absence Validation Null**

Toujours valider null avant utilisation.
```markdown
## Gestion Erreurs
Si PREF_XXX null:
- Logger erreur: "Preference {PreferenceName} not found"
- Lancer exception
- Valider preference != null avant utilisation
```

**3. Valeurs Hardcodées**

Utiliser constantes documentées.
```markdown
## Constantes
```csharp
private const string PreferenceKey = "PREF_DISPLAY_CHECK_DIGIT";
```

## Logique
- pref.Value == "YES" (case-insensitive) → "1"
- Sinon → "0"
- Utiliser ToUpper() pour comparaisons
```

---

## Documentation Ambiguïtés

**Principe:** Identifier et documenter zones d'ombre, pas les résoudre.

**Format Questions:**
```markdown
## ❓ Questions
1. **Valeurs NULL** - Context: C++ `if (sPref.IsEmpty())` - Q: Traiter "" vs null?
   Options: A) Identique → "0" B) Différencier
   Recommandation: A (simplicité)

2. **Format Date** - Context: `DATE_FIN` - Q: Format InitialValue?
   Options: A) yyyy-MM-dd B) dd/MM/yyyy C) yyyyMMdd
   Action: Vérifier exemples

3. **Liste Vide** - Context: `GetIndustryCodes()` vide - Q: Retourner?
   Recommandation: `return null` (pattern standard)
```

**Format Edge Cases:**
```markdown
## ⚠️ Edge Cases
1. **Valeur Inattendue** - PREF_XXX = "MAYBE" (ni YES ni NO)
   C++: Toute valeur != "YES" → "0"
   C#: Identique + logger warning si inattendu

2. **Source Type Non Géré** - pad != CLIENT/ACCOUNT/SECURITY
   C++: Default → "0"
   C#: Implémenter default + logger warning

3. **Param Avant Init** - POST dépend de PARAM_YearMonth (PRE)
   Si manquant: Logger erreur + valeur défaut sécuritaire
```

---

**Template Spec Complet:**
```markdown
# Spec: [FunctionName]

## Info
- C++: `FunctionName` (`validation_xxx.c:123`)
- Type: Default/Specific | Phase: PRE/POST | Complexité: Niveau X

## Code C++
```c
[Code avec numéros ligne]
```
Logique: 1) Étape 1  2) Étape 2

## Dépendances
- IPreferencesRepository (PREF_XXX ligne 45)
- IReportCommandAndQueryContextRepository (PARAM_YYY ligne 89)
- SourceType: pad == REPORT_CLIENT (ligne 34)

## Implémentation
- Type: ☐ ValidationFunction ☑ ValueProviderFunction
- Nom: `[Name]Parameter.cs`
- Pseudo-code: 1) Récupérer PREF 2) Valider null 3) Calculer
- Constantes: `private const string PreferenceKey = "PREF_XXX";`

## Erreurs
- Pref manquante: Logger "Preference {Name} not found" + exception
- Valeur inattendue: Logger warning + défaut

## Enregistrement
- Fichier: `[Pre|Post]ParamEntryValueProviderFunctionsExecuter.cs`
- Position: Entre [Avant] et [Après]
- Code: `implementationsDictionary["FunctionName"] = () => new FunctionNameParameter(...);`

## ❓ Questions / ⚠️ Edge Cases / 📝 Notes
[Si applicable]
```

---

## Guidelines Logging

**Toujours logger:**
1. **Erreurs** - Error: "Preference {Name} not found"
2. **Décisions importantes** - Debug: "Removing parameter {Name} - no data"
3. **Logique complexe** - Debug: "Processing parameter {Name}" (optionnel)

**Ne pas logger:**
- Paramètres triviaux (StringParameter, TrueParameter)
- Chaque ligne de code simple
- Valeurs retournées simples

**Template specs:**
```markdown
## Logging
- Erreur critique: `Logger.Error("Preference {PreferenceName} not found", key)`
- Décision: `Logger.Debug("Removing parameter {Name} - reason", param.Name)`
```

**Exemples:** `InitDisplayCheckDigitParameter.cs:18,32-34`, `IndCodeComboParameter.cs:30-32`

---

## Bonnes Pratiques

1. **Exhaustif mais Concis** - Lister dépendances précises (IPreferencesRepository pour PREF_XXX), pas vague
2. **Numéros Ligne C++** - Toujours inclure (`validation_hided.c:1234-1256`) pour retrouver code
3. **Cas Normaux ET Exceptionnels** - Documenter comportement nominal + erreurs/edge cases
4. **Exemples Concrets** - Format entrée: "202401" → sortie: "2024-01-01"
5. **Liens Skills** - Référencer `migration-examples.md`, `implementation-guide.md`, etc.

---

## Checklist Validation

**Analyse C++:** Code lu, lignes documentées, logique décomposée, conditions identifiées
**Dépendances:** Repositories listés, PREF_/PARAM_ documentés (noms exacts), SourceType vérifié
**Implémentation:** Type choisi, nom C# spécifié, pseudo-code fourni, constantes identifiées
**Erreurs:** Cas identifiés, logging spécifié, exceptions documentées, edge cases listés
**Documentation:** Questions/ambiguïtés notées, exemples fournis, liens skills
**Enregistrement:** Fichier executer (Pre/Post), position alphabétique, code fourni
**Qualité:** Pas jargon non défini, pas suppositions, clair, actionnable

**Règle d'or:** Spec qualité = Zéro aller-retour analyste-développeur. Specs autonomes et complètes.

## Ressources

**Skills:** `migration-examples`, `read-cpp-patterns`, `analyze-cpp-function`, `implementation-guide`, `generic-functions-reference`

**Docs:** `MyCustomSnippets.code-snippets`, `README.BusinessBrowserWebApi.md`, `CONTRIBUTING.md`

## Aide-Mémoire

**Anti-patterns:** GetPreferencesValue() pour 1 pref, pas validation null, valeurs hardcodées
**Toujours:** Questions structurées, edge cases, erreurs complètes, logging points critiques
**Structure minimale:** Info générale, code C++ (lignes), dépendances, implémentation, erreurs, enregistrement
