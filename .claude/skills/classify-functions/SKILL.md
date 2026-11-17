---
name: classify-functions
description: Classifie les fonctions de rapport extraites (Default/Specific, PRE/POST), détecte patterns déclaratifs (>90% sans classe), et détermine leur statut d'implémentation C#. Utiliser après extract-parameters pour identifier l'approche optimale (déclarative vs custom) et prioriser les analyses C++.
---

# Skill: Classify Functions

> **⚠️ NOTE SYMLINKS:** Les répertoires `ReportFoundations`, `ReportManagerApi` et `CroesusServer` sont des **liens symboliques**. L'outil `Glob` et la commande `find` (sans option) ne suivent PAS les symlinks.
> - **Solution:** Utiliser `find -L` pour suivre les symlinks
> - **Alternative:** L'outil `Grep` fonctionne si on lui donne un chemin explicite

## Objectif

Classifier TOUTES les fonctions extraites du CSV en traitant **Default ET Specific SÉPARÉMENT**.

**RÈGLE CRITIQUE #1:** >90% des fonctions sont déclaratives (pas de classe custom).
**RÈGLE CRITIQUE #2:** Default et Specific sont des contextes DIFFÉRENTS - analyser les DEUX!

## Input

- **Option 1:** Report ID (ex: `RPT-17858`) → lire `.work/{slug}/analysis-extraction.md`
- **Option 2:** Fichier CSV directement

## Processus

### 1. Charger et créer liste de fonctions À ANALYSER

**⚠️ IMPORTANT: Créer UNE ENTRÉE PAR FONCTION, pas par paramètre!**

Pour chaque ligne du CSV:
1. Extraire `Default_Function` → ajouter à la liste avec contexte "Default (Batch)"
2. Extraire `Specific_Function` → ajouter à la liste avec contexte "Specific (Individuel)"
3. Normaliser préfixes spéciaux:

| Préfixe | Signification | Action |
|---------|---------------|--------|
| `*Hided*PARAM_XXX` | Version hidden | Stripper → `PARAM_XXX` |
| `*H*PARAM_XXX` | Alias hidden | Stripper → `PARAM_XXX` |
| `*EndDate*PARAM_XXX` | Transformation date fin | Stripper → `PARAM_XXX`, noter transformation |
| `*PlusOneYear*PARAM_XXX` | Date + 1 an | Stripper → `PARAM_XXX`, noter transformation |

**Résultat:** Liste où un même paramètre peut avoir 2 entrées si Default ≠ Specific.

```
Exemple PARAM_UseGICSBreakDown:
├─ Entrée 1: IsBatchUseGicsBreakdown (Default/Batch)
└─ Entrée 2: IsReportUseGicsBreakdown (Specific/Individuel)
→ Les DEUX doivent être analysées indépendamment!
```

### 1.5. Identifier paramètres déjà configurés dans hiérarchie de classes

**CRITIQUE:** Paramètres peuvent être configurés dans classe parente. Ne pas lister comme "à faire" si déjà dans parent.

#### Processus

1. **Trouver classe du rapport:**
```bash
# Chercher classe correspondant au report code (ex: PERF_ACC_SUMM)
find -L ReportFoundations -name "*AccountSummary*.cs" -path "*/Reports/Main/*"
# Lire pour identifier: public partial class RPT_XXX : RPT_YYY
```

2. **Remonter hiérarchie:**
```bash
# Extraire nom parent (après ":")
grep "public.*class RPT_" <FILE> | grep -oE ": RPT_[A-Za-z0-9_]+"
# Chercher Parameters.cs du parent
find -L ReportFoundations -name "Parameters.cs" -path "*/<PARENT_DIR>/*"
# Répéter jusqu'à RPT_ReportBase ou absence de parent
```

3. **Extraire paramètres des parents:**
```bash
# Pour chaque Parameters.cs trouvé
grep "Params\.PARAM_" <FILE> | grep -oE "PARAM_[A-Za-z0-9_]+"
```

4. **Marquer comme hérités:**
- Créer map: `inheritedParams[PARAM_XXX] = {configuredIn: "RPT_ParentClass", file: "path"}`
- Pour chaque fonction À ANALYSER: si `fonction.parametre in inheritedParams` → skip (déjà configuré)

#### Output ajouté

```markdown
## Hiérarchie

**Classe:** RPT_XXX
**Parents:** RPT_YYY (N params) → RPT_ZZZ (M params)
**Total hérité:** X params
**Spécifiques à configurer:** Y params

IMPORTANT: Seuls Y params nécessitent du travail. X params déjà dans parents.
```

### 2. Pour CHAQUE fonction de la liste, déterminer le pattern

**⚠️ Traiter chaque fonction INDÉPENDAMMENT (Default et Specific séparément).**

#### Étape 2a: Chercher dans *ParametersImplementation.cs

**⚠️ SYMLINKS:** `ReportFoundations` est un lien symbolique. Utiliser `grep -r` ou `find -L`:

```bash
# Option 1: grep -r (suit les symlinks automatiquement)
grep -r "Params.PARAM_XXX" repos/ReportFoundations/ReportImplementations/Implementations/Parameters/SpecificTypes/

# Option 2: Utiliser l'outil Grep avec chemin explicite
Grep(pattern="Params.PARAM_XXX", path="repos/ReportFoundations/ReportImplementations/Implementations/Parameters/SpecificTypes")
```

**Si trouvé**, extraire:
- `ValidationFunction` (nom de la fonction C++)
- `valueProviderFunction` (nom de la classe C# si présent)
- `initialValue` (valeur par défaut si présente)

#### Étape 2b: Arbre de décision avec Quick C++ Scan

**Si valueProviderFunction dans *ParametersImplementation.cs:**
1. Chercher dans executers → `new XxxParameter()` trouvé?
   - OUI + classe existe → ✅ Preconfigured
   - OUI + classe absente → 🔴 Custom (référencée mais manquante)
   - UnimplementedParameter → ⚠️ Custom:TODO
   - Absent → 🔴 Custom:Inexistant

**Sinon → Vérifier si ValidationFunction est un PATTERN DÉCLARATIF CONNU:**

### Liste EXHAUSTIVE des Patterns Déclaratifs (FERMÉE)

**⚠️ RÈGLE CRITIQUE:** Si la ValidationFunction n'est **PAS** dans cette liste exacte → **Quick C++ Scan OBLIGATOIRE**

| Pattern | Description | Action C# |
|---------|-------------|-----------|
| `CheckTrue` | Valeur fixe "1" | `initialValue: "1"` |
| `CheckFalse` | Valeur fixe "0" | `initialValue: "0"` |
| `CheckFalseInvisible` | Valeur "0" + invisible | `initialValue: "0"` |
| `CheckFalseVisibleForRelOnly` | Valeur "0" + visible relation | `initialValue: "0"` + valueProviderFunction |
| `CheckTrueInvisible` | Valeur "1" + invisible | `initialValue: "1"` |
| `PureValueZero` | Valeur fixe "0" | `initialValue: "0"` |
| `PureValueMinusOne` | Valeur fixe "-1" | `initialValue: "-1"` |
| `PureValueGlobal` | Valeur fixe "GLOBAL" | `initialValue: "GLOBAL"` |
| `WhiteSpace` | Valeur fixe " " | `initialValue: " "` |
| `GetBoolFromPref(PREF_XXX)` | Lecture préférence boolean | `initialValueFromPref: "PREF_XXX"` |
| `GetBoolFromPrefUserAccess(PREF_XXX)` | Lecture préférence + accès | `valueProviderFunction` requis |
| `GetIntFromPref(PREF_XXX)` | Lecture préférence int | `initialValueFromPref: "PREF_XXX"` |
| `GetCheckValue(PARAM_XXX)` | Copie valeur autre param | `initialValueFromParam: "PARAM_XXX"` |
| `ReportTitle` | Titre rapport | Preconfigured dans executer |
| `GetPad` | Pad du rapport | Preconfigured dans executer |
| `GetDisplayDate` | Date affichage | Preconfigured dans executer |
| `GetFirmCurrency` | Devise firme | Preconfigured dans executer |
| `AsOfDate` | Date "As Of" | Preconfigured dans executer |
| `MustDoRequest` | Valeur fixe "1" | `initialValue: "1"` |
| `FieldsForEntity` | Valeur fixe "Y" | `initialValue: "Y"` |
| `UnmaskedAccIdNumbers` | Lecture préférence | `initialValueFromPref` |
| `(vide/empty)` | Aucune validation | Framework gère |

**⚠️ TOUTE fonction NON LISTÉE ci-dessus → Quick C++ Scan OBLIGATOIRE**

### Quick C++ Scan (si fonction NON dans liste ci-dessus)

Localiser C++ puis compter en 10s:

| SetValue | GetCresusConfig | if/else | GetParam* | → Classification |
|----------|-----------------|---------|-----------|------------------|
| 1 | 0 | 0 | 0 | ✅ InitialValue |
| 1 | 1 | 0-1 | 0 | ✅ InitialValueFromPref |
| 1 | 0 | 1 (source type) | 0 | ✅ ValidSourceType existant |
| 2+ | * | * | * | 🔴 Custom |
| * | 2+ | * | * | 🔴 Custom |
| * | * | 3+ | * | 🔴 Custom |
| * | * | * | 1+ | 🔴 Custom (lecture autres params) |

**Patterns déclaratifs (noter la valeur pour Parameters.cs):**
```c
pAtt->SetValue("constante");              // → InitialValue="constante"
pAtt->SetValue(pref ? pref : fallback);   // → InitialValueFromPref + InitialValue
```

**⚠️ Si 2 SetValue dans if/else avec même pref → InitialValueFromPref (pas custom)**

**🔴 Signaux d'alerte CUSTOM obligatoire:**
- `GetParamValueForAllSelectedReport()` → Lecture paramètres autres rapports
- `GetParam()`, `GetParamInt()`, `GetParamString()` → Lecture autres paramètres
- `pCtrParam->` → Accès controller
- Boucles `for`, `while` → Logique itérative
- `std::vector`, `std::map` → Collections

Voir `.claude/conventions/reference/read-cpp-patterns.md` pour: ignorer boilerplate, technique scanning, exemples annotés.

#### Étape 2c: Marquer CHAQUE entrée

Pour chaque fonction analysée, enregistrer:
- `fonction`: nom (ex: IsBatchUseGicsBreakdown)
- `contexte`: "Default (Batch)" ou "Specific (Individuel)"
- `parametre`: PARAM_XXX associé
- `pattern`: declarative:* ou custom:*
- `needsClass`: true/false
- `statut`: ✅ Implémenté | ⚠️ TODO | 🔴 Inexistant

**Statistiques attendues:** >90% déclaratif, ~10% custom
**⚠️ Si >20% custom: REVOIR - probablement sur-classification**

### 3. Vérifier statut d'implémentation (needsClass=true seulement)

**⚠️ SYMLINKS:** `ReportManagerApi` est un lien symbolique. Utiliser `find -L`:

```bash
# Localiser les executers (find -L pour suivre symlinks)
find -L ReportManagerApi -name "PreParamEntryValueProviderFunctionsExecuter.cs" 2>/dev/null
find -L ReportManagerApi -name "PostParamEntryValueProviderFunctionsExecuter.cs" 2>/dev/null

# Chercher chaque fonction custom
grep -n 'implementationsDictionary\["FunctionName"\]' <CHEMIN_EXECUTER>
```

**Statuts:**
- ✅ Implémenté: `new XxxParameter(...)` où Xxx est une vraie classe (ex: `IsCliRootManagementParameter`)
- ⚠️ TODO: `new UnimplementedParameter()` - placeholder à remplacer
- 📝 Déclaratif: `new StringParameter("...")` - constante simple
- 🔴 Inexistant: Non trouvé dans l'executer

**⚠️ VÉRIFICATION OBLIGATOIRE du contenu:**
Après le grep, LIRE la ligne complète trouvée. Ne pas assumer "Implémenté" si l'entry existe:
```bash
# Exemple: grep retourne une ligne
grep -n 'implementationsDictionary\["IsReportUseGicsBreakdown"\]' PostExecuter.cs
# → 45: implementationsDictionary["IsReportUseGicsBreakdown"] = () => new UnimplementedParameter();
#                                                                      ^^^^^^^^^^^^^^^^^^^^^^
# → C'est UnimplementedParameter! Statut = ⚠️ TODO, PAS ✅ Implémenté
```

### 4. Classifier par PARAMETER_ENTRY_TYPE

Séparer:
- **PRE:** `PreParamEntryValueProviderFunctionsExecuter.cs`
- **POST:** `PostParamEntryValueProviderFunctionsExecuter.cs`

## Format de Sortie

```markdown
# Classification - {REPORT-ID}

**Date:** {date} | **Source:** .work/{slug}/analysis-extraction.md

## Résumé

📊 **Patterns d'implémentation:**

| Pattern | Count | % | Classe Requise | Temps Estimé |
|---------|-------|---|----------------|--------------|
| Preconfigured | X | XX% | ❌ | XXs |
| ValidationFunction="" | X | XX% | ❌ | XXs |
| InitialValue | X | XX% | ❌ | XXmin |
| InitialValueFromPref | X | XX% | ❌ | XXmin |
| InitialValueDateType | X | XX% | ❌ | XXmin |
| **Sous-total Déclaratif** | **X** | **>90%** | **❌** | **XXmin** |
| ValueProviderFunction | X | XX% | ✅ | XXh |
| **TOTAL** | **X** | **100%** | - | **XXh** |

⚠️ {Si custom > 20%: "ATTENTION: Ratio custom élevé - vérifier analyse"}

🔍 **Statut implémentation (custom seulement):**

| Statut | PRE | POST | Total |
|--------|-----|------|-------|
| ✅ Implémenté | X | X | X |
| ⚠️ TODO | X | X | X |
| 🔴 Inexistant | X | X | X |
| **TOTAL** | **X** | **X** | **X** |

## Patterns Déclaratifs (0 classe requise)

### Preconfigured ({count})
| ValidationFunction | Paramètre | ValueProviderFunction | Défini dans | Implémentation |
|-------------------|-----------|----------------------|-------------|----------------|
| AssetMixRadioButton | PARAM_AssetMixRepartType | AssetMixRepartType | RadioParametersImplementation.cs | AssetMixRepartTypeParameter.cs ✅ |
| CostCalculation | PARAM_AvgCostCalculMethod | CostCalculation | RadioParametersImplementation.cs | CostCalculationParameter.cs ✅ |

### ValidationFunction="" ({count})
| Fonction | Paramètre | Widget | Géré par | Vérification C++ |
|----------|-----------|--------|----------|------------------|
| CheckTrue | PARAM_DisplayCheckDigit | 8 | HiddenParametersImplementation.cs | ✅ SIMPLE (framework) |

**⚠️ Note:** Toutes les fonctions listées ici ont été vérifiées avec analyze-cpp-function Mode 1. Les fonctions ValidationFunction COMPLEXES sont reclassifiées dans "Fonctions Custom" ci-dessous.

### InitialValue ({count})
| Fonction | Paramètre | Valeur | Widget |
|----------|-----------|--------|--------|
| MaturitySubReportField | PARAM_RPTSubId | "SEC_V_Desc" | 8 |

### InitialValueFromPref ({count})
| Fonction | Paramètre | Préférence | Widget |
|----------|-----------|------------|--------|
| GetBoolFromPref | PARAM_CIBCGainLossCalcul | PREF_STRIP_BOND_GL1 | 8 |

### InitialValueDateType ({count})
| Fonction | Paramètre | DateType | Widget |
|----------|-----------|----------|--------|
| LastProcessingDate | PARAM_StartDate | LastProcessedDate | 5 |

---

## Fonctions Reclassifiées (ValidationFunction → Custom)

**Fonctions initialement trouvées dans *ParametersImplementation.cs mais reclassifiées comme COMPLEXES après analyse C++:**

| ValidationFunction | Paramètre | Widget | Géré par | Verdict C++ | Raison | Action |
|--------------------|-----------|--------|----------|-------------|--------|--------|
| IsBatchUseGicsBreakdown | PARAM_UseGICSBreakDown | 8 | HiddenParametersImplementation.cs | ❌ COMPLEXE | 3 repositories + 4 if + lecture autres params | Créer IsReportUseGicsBreakdownParameter |

**⚠️ Ces fonctions nécessitent une classe Parameter custom malgré leur présence dans *ParametersImplementation.cs!**

---

## Fonctions Custom (classe requise)

### PRE - ✅ Implémentées ({count})
| Fonction | Utilisée par | Parameter.cs | Ligne |
|----------|--------------|--------------|-------|
| AsOfDate | PARAM_AsOfDate | AsOfDateParameter.cs | 45 |

### PRE - ⚠️ TODO ({count})
| Fonction | Utilisée par | Widget | C++ File |
|----------|--------------|--------|----------|
| InitGainLossCost | PARAM_GainLoss | 3 | validation_check.c |

### PRE - 🔴 Inexistantes ({count})
| Fonction | Utilisée par | Widget | C++ File | Priorité |
|----------|--------------|--------|----------|----------|
| EvalSimpleEntry | PARAM_Eval | 1 | validation_combo.c | CRITIQUE |

### POST - ✅ Implémentées / ⚠️ TODO / 🔴 Inexistantes

[Même structure que PRE]

## ⚠️ Vue Default vs Specific (CRITIQUE)

**Paramètres avec DEUX fonctions distinctes - les DEUX ont été analysées:**

| Paramètre | Default (Batch) | Pattern | Statut | Specific (Individuel) | Pattern | Statut |
|-----------|-----------------|---------|--------|----------------------|---------|--------|
| PARAM_UseGICSBreakDown | IsBatchUseGicsBreakdown | custom | 🔴 Inexistant | IsReportUseGicsBreakdown | Preconfigured | ✅ Implémenté |
| PARAM_DoGraphAssetMix | CheckFalse | declarative | ✅ Framework | PerfDoGraphAssetMix | custom | ⚠️ TODO |

**⚠️ ACTIONS REQUISES pour fonctions avec statut 🔴 ou ⚠️:**
- `IsBatchUseGicsBreakdown`: Créer classe (même si Specific existe!)

## Plan d'Action

**Patterns Déclaratifs (>90%) - Configuration Parameters.cs seulement:**
- [ ] ValidationFunction="": {count} × 10s = {time}min
- [ ] InitialValue: {count} × 2min = {time}min
- [ ] InitialValueFromPref: {count} × 2min = {time}min
- [ ] InitialValueDateType: {count} × 2min = {time}min
- **Sous-total:** {count} fonctions, {time}h

**Fonctions Custom (~>10%) - Classes à créer/compléter:**

**Priorité Critique - 🔴 Inexistantes ({count}):**
- [ ] PRE: `Function1` (Combo) - PARAM_XXX - {Xh}
- [ ] POST: `Function2` (Hidden) - PARAM_YYY - {Xh}

**Priorité Haute - ⚠️ TODO ({count}):**
- [ ] PRE: `Function3` - Remplacer UnimplementedParameter - {Xh}
- [ ] POST: `Function4` - Remplacer UnimplementedParameter - {Xh}
- **Sous-total:** {count} fonctions custom, {time}h

**TOTAL ESTIMÉ:** {totalTime}h

## Prochaines Étapes

**Pour patterns déclaratifs (>90%):**
1. ✅ Configurer directement dans Parameters.cs
2. ✅ Pas d'analyse C++ approfondie nécessaire
3. ✅ Tests déjà couverts par framework

**Pour fonctions custom (>10%):**
1. Localiser code C++ (skill: `locate-cpp-function`)
2. Analyser dépendances (skill: `analyze-cpp-function`)
3. Estimer complexité (skill: `estimate-complexity`)
4. Créer spec détaillée: `.work/{slug}/spec.md`

**⚠️ Temps économisé vs approche systématique:** ~{savedTime}h grâce aux patterns déclaratifs
```

### Sauvegarder

Créer fichier séparé: `.work/{slug}/analysis-classification.md`

### Résumé Console

```
✅ Classification terminée: {REPORT-ID}

📊 Patterns détectés:
├─ Déclaratifs (0 classe): {declarativeCount} ({declarativePct}%)
│  ├─ ValidationFunction="": {vfCount}
│  ├─ InitialValue: {ivCount}
│  ├─ InitialValueFromPref: {ivpCount}
│  └─ InitialValueDateType: {ivdtCount}
└─ Custom (classe requise): {customCount} ({customPct}%)

{customPct > 20 ? "⚠️ ATTENTION: Ratio custom élevé - vérifier analyse" : "✅ Ratio normal"}

🔍 Fonctions custom à traiter:
├─ ✅ Déjà implémentées: {implementedCount} (0h)
├─ ⚠️ TODO: {todoCount} (~{todoTime}h)
└─ 🔴 Inexistantes: {missingCount} (~{missingTime}h)

Temps estimé total: {totalTime}h
Temps économisé (déclaratif): {savedTime}h

Prochaines étapes:
1. Configurer patterns déclaratifs dans Parameters.cs ({declarativeCount} × 2min)
2. Analyser fonctions custom ({customCount} fonctions) - skill 'locate-cpp-function'
```

## Référence: Fichiers C++ par Widget

| Widget | C++ File | Entry Type |
|--------|----------|------------|
| 1 | validation_combo.c | PRE |
| 2 | validation_radio.c | PRE |
| 3 | validation_check.c | PRE |
| 4 | validation_list.c | PRE |
| 5 | validation_date.c | PRE |
| 7 | validation_file.c | PRE |
| 8 | validation_hided.c | POST |
| 9 | validation_multilang_textbox.c | PRE |

## Fichiers Executer

⚠️ **Chemins variables** - Toujours localiser dynamiquement.

**IMPORTANT - Gestion des symlinks:**
Les répertoires `ReportFoundations` et `ReportManagerApi` sont des **liens symboliques**. L'outil `Glob` et `find` (sans option) ne suivent PAS les symlinks.

**Solution: Utiliser `find -L` pour suivre les symlinks:**

```bash
# Localiser les executers (suivre symlinks avec -L)
find -L ReportManagerApi -name "PreParamEntryValueProviderFunctionsExecuter.cs" 2>/dev/null
find -L ReportManagerApi -name "PostParamEntryValueProviderFunctionsExecuter.cs" 2>/dev/null

# Chercher dans ParametersImplementation.cs
find -L ReportFoundations -name "*ParametersImplementation.cs" 2>/dev/null
```

**Alternative: Utiliser Grep avec chemin explicite:**
```bash
# Grep suit les symlinks automatiquement si on lui donne un chemin
grep -r "Params.PARAM_XXX" repos/ReportFoundations/
```

**Chemins typiques (pour référence seulement):**
- PRE: `repos/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/PreParamEntryValueProviderFunctionsExecuter.cs`
- POST: `repos/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/PostParamEntryValueProviderFunctionsExecuter.cs`
- Parameters: `repos/ReportFoundations/ReportImplementations/Implementations/Parameters/SpecificTypes/*ParametersImplementation.cs`
