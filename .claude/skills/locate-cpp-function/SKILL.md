---
name: locate-cpp-function
description: Localise le code source C++ d'une fonction de rapport dans CroesusServer en utilisant stratégies Plans A-E. Utiliser quand on a identifié une fonction à migrer et qu'on doit trouver son implémentation C++ dans les fichiers validation_*.c.
---

# Skill: Locate C++ Function

Expert en recherche de code C++ pour migration rapports Croesus.

## Objectif

Localiser le code source C++ d'une fonction de rapport dans les fichiers de validation de CroesusServer.

## Input

- **Nom fonction** (ex: `InitGainLossCostDisplayed`)
- **Widget Type** (optionnel, aide à cibler)
- **Entry Type** (PRE/POST, optionnel)

## Fichiers de Validation C++

**IMPORTANT:** Chercher dans `.c` et `.h` (PAS `.cpp`)

**Localisation:** `repos/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/`

### Mapping Widget → Fichier

| Widget | Description | Fichier C | Entry |
|--------|-------------|-----------|-------|
| 1 | Combobox | validation_combo.c | PRE |
| 2 | Radio | validation_radio.c | PRE |
| 3 | Checkbox | validation_check.c | PRE |
| 4 | List | validation_list.c | PRE |
| 5 | Date | validation_date.c | PRE |
| 7 | String/File | validation_file.c | PRE |
| 8 | Hidden | validation_hided.c | POST |
| 9 | MultiLangTextBox | validation_multilang_textbox.c | PRE |

**Orchestration:** `ctr_param.c/.h`

## Stratégies (Plans A-E)

**Suivre l'ordre. Si échec, passer au suivant.**

### Plan A: Recherche Directe (70% succès)

```bash
cd repos/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam

# Si Widget Type connu
grep -n "InitGainLossCost" validation_check.c

# Si inconnu, chercher dans tous
grep -n "FunctionName" validation_*.c
```

### Plan B: Recherche par Fragments (20% succès)

Si Plan A échoue, décomposer nom (PascalCase) et chercher fragments 4+ caractères.

**Exemple:** `PerfAccSummGetSubReportField` → chercher `AccSumm`, `SubReportField`, `GetSubReport`

```bash
grep -n "AccSumm" validation_hided.c
grep -n "SubReportField" validation_hided.c
```

### Plan C: Recherche par Paramètre (15% succès)

Chercher nom paramètre SQL (`PARAM_XXX`), lire contexte ±20 lignes.

```bash
grep -n -C 20 "PARAM_RPTSubId" validation_hided.c
```

### Plan D: Recherche par Pattern (10% succès)

Chercher fonctions similaires pour déduire naming pattern.

```bash
# Pattern Init*
grep -n "void.*Init.*(" validation_check.c

# Pattern Perf*
grep -n "^void.*Perf" validation_hided.c

# Pattern Get*
grep -n "void.*Get.*(" validation_hided.c

# Pattern Set*RptView
grep -n "^void.*Set.*RptView" validation_hided.c

# Pattern *DataEntryPoint
grep -n "DataEntryPoint" validation_hided.c
```

### Plan E: Recherche Globale (5% succès - dernier recours)

```bash
# Dans toute ReportApi
cd repos/CroesusServer/Src/ReportApi
grep -rn "FunctionName" .

# Dans tout Src/
cd repos/CroesusServer/Src
grep -r "FunctionName" . --include="*.c" --include="*.h"

# Dans headers
grep -n "FunctionName" validation_*.h
grep -n "FunctionName" ctr_param.h
```

### Dernière Option

Si introuvable après A-E:
1. Examiner implémentations C# similaires
2. Déduire logique du nom/contexte/widget type
3. Consulter développeur C++ senior
4. Historique Git: `git log -S "FunctionName"`

## Extraction Code

Une fois trouvée (ex: ligne 1234):

```bash
# Méthode 1: grep avec contexte
grep -A 50 "void.*FunctionName" validation_check.c

# Méthode 2: sed avec lignes
sed -n '1234,1300p' validation_check.c

# Méthode 3: Read tool
Read repos/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_check.c
```

## Analyse Code Extrait

### Signature Typique

```c
void FunctionName(REPORT_CTR_PARAM *pParam, int iParamIndex, HWND hDlg)
```

**Paramètres:** `pParam` (structure paramètres), `iParamIndex` (index), `hDlg` (UI, non pertinent C#)

### Patterns à Identifier

**Accès Paramètres (PARAM_):**
```c
GetParam(pParam, PARAM_XXX)
GetParamInt/String(pParam, PARAM_YYY)
IsParamChecked(pParam, PARAM_AAA)
```
→ **C# mapping:** `IReportCommandAndQueryContextRepository`

**Accès Préférences (PREF_):**
```c
GetPreference/GetBoolFromPref/GetIntFromPref(PREF_XXX)
```
→ **C# mapping:** `IPreferencesRepository`

**Opérations Date:**
```c
GetSelectedYearMonth(), GetStartDate(), GetEndDate(), DateToString()
```
→ **C# mapping:** `IParameterDateValueService`

**Requêtes BD/Logique Métier:**
```c
GetRepartitionList(), GetTransactionData(), QueryDatabase()
```
→ **C# mapping:** `IRepartitionRepository`, `ITransactionsRepository`, `IIndustryCodeRepository`, `IIndexesRepository`

**Logique Conditionnelle:** Noter toutes conditions `if/else`

## Format Sortie

```markdown
# Localisation: {FunctionName}

## Résultat

**✅ Trouvée** | **❌ Non trouvée**

**Fichier:** `validation_xxx.c` | **Ligne:** {line} | **Widget:** {type} | **Entry:** PRE/POST

## Signature C++

```c
void FunctionName(REPORT_CTR_PARAM *pParam, int iParamIndex, HWND hDlg)
```

## Code Source

```c
{Code complet}
```

## Analyse Initiale

**Dépendances:**
- **PARAM_:** XXX, YYY → `IReportCommandAndQueryContextRepository`
- **PREF_:** AAA, BBB → `IPreferencesRepository`
- **Date ops:** GetSelectedYearMonth() → `IParameterDateValueService`
- **Autres:** {Description} → `I{Repository}`

**Logique Principale:**
{Pseudo-code description}

**Cas Particuliers:**
- [ ] Gestion NULL, [ ] Validation, [ ] Défauts, [ ] Conditions spécifiques

## Prochaines Étapes

1. Analyser en profondeur (skill `analyze-cpp-code`)
2. Créer spec C# avec mappings
3. Implémenter Parameter C#
```

## Cas Particuliers

### Non Trouvée

```markdown
# ❌ Non Trouvée: {FunctionName}

**Stratégies tentées:** [x] Directe, [x] Fragments, [x] Paramètre, [x] Pattern, [x] Globale

**Hypothèses:**
1. Nom différent en C++ (mapping DB?)
2. Fonction inline/macro (`#define FunctionName`)
3. Logique dans `ctr_param.c`
4. Fonction générique paramétrée

**Actions:**
- [ ] Développeur C++ senior
- [ ] Git: `git log -S "FunctionName"`
- [ ] Vérifier côté client
- [ ] Documentation legacy
```

### Fonction Alias

Si deux noms → même code:

```markdown
**Alias:** `IndexListWhithIndexPerso` = `IndexListWhithIndexPersoSymb`
**Code:** IDENTIQUE (validation_combo.c:456)

**C# Recommandation:**
UNE classe Parameter, DEUX enregistrements dans executer:
```csharp
implementationsDictionary["IndexListWhithIndexPerso"] = () => new IndexListWhithIndexPersoParameter(deps);
implementationsDictionary["IndexListWhithIndexPersoSymb"] = () => new IndexListWhithIndexPersoParameter(deps);
```
```

### Fonction Complexe (>100 lignes)

```markdown
**Lignes:** {count} | **Complexité:** {high/medium/low}

**Recommandation:**
1. Décomposer en méthodes helper privées
2. Extraire logique métier dans service Domain
3. Plusieurs Parameter classes si logique très différente
4. Documenter avec commentaires XML

**Besoin:** Service `I{FunctionName}Service.cs`, Tests exhaustifs, Revue approfondie
```

## Optimisation

**Cache résultats** dans `docs/cpp-locations.json`:
```json
{
  "functions": {
    "InitGainLossCost": {"file": "validation_check.c", "line": 1234, "widgetType": 3, "found": true}
  }
}
```

**Recherche batch:**
```bash
for func in Func1 Func2 Func3; do
  echo "Searching: $func"
  grep -n "$func" validation_*.c
done
```

## Résumé Console

```
Recherche: {FunctionName}

Status: ✅ Trouvée | ❌ Non trouvée
Fichier: validation_xxx.c:{line}
Stratégie: {stratégie}

Dépendances: PARAM_: {x} | PREF_: {x} | Date: {x} | Autres: {x}
Code: {lines} lignes | Complexité: {Low|Medium|High}

Prochaine: analyze-cpp-code
```

## Références

- Localisation: `repos/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/`
- Skill suivant: `analyze-cpp-code`
